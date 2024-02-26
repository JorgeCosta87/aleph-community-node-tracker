from collections import defaultdict
import logging
import time
import uuid
from fastapi import HTTPException
from pydantic import ValidationError
import requests

from app.schemas.message_metrics import BaseCnnMetric, BaseCrnMetric, MessageNetworkMetrics
from app.schemas.node import NodeCreate, NodeMetricsSubscribedBody, NodeSchema, NodesMetrics
from app.repositories.node import NodeRepository
from app.utils.utils import Utils
from app.repositories.message import MessageRepository
from app.schemas.message import MessageCreate
from app.schemas.crn_metrics import CrnMetricCreate, CrnMetricSchema, CrnMetricsResponseSchema
from app.schemas.ccn_metrics import CcnMetricCreate, CcnMetricSchema, CcnMetricsResponseSchema
from app.utils.constants import NodeType, SubscribeType
from app.repositories.subscribe import SubscribeRepository
from app.schemas.subscriber import SubscriberSchema

logger = logging.getLogger(__name__) 


class NodeMetricsService():

    def __init__(self, repository: NodeRepository):
        self.repository = repository

    def get_crn_metrics(self) -> list[CrnMetricsResponseSchema]:
        return self.repository.get_latest_crn_metrics()


    def update_nodes_and_notify_subscribers(self, messageRepository: MessageRepository):
        logger.info("Start thread to update nodes and notify subscribers")
       
        while True:
            message = self._fetch_and_extract_node_metrics()
            if message is None:
                continue

            update_time = message.content.time
            crn_metrics = message.content.content.metrics.crn
            ccn_metrics = message.content.content.metrics.ccn
            message_hash = message.item_hash

            logger.info(f"Fecthed {len(crn_metrics)} crn nodes at {Utils.convert_unix_to_datetime(update_time)}")

            last_message = messageRepository.get_message_by_hash(message_hash)

            #If the hash isn't on the db, a new message is added and the nodes are updated on the db
            if last_message is None:
                message_saved = messageRepository.save(
                    MessageCreate(
                        item_hash=message.item_hash,
                        item_type=message.item_type,
                        time=message.content.time,
                        message_type=message.content.type
                    )
                )
                logger.info(f"Saved new message with hash: {message_saved.item_hash}")
                self._update_node_metrics(crn_metrics, message_saved.id, NodeType.CRN)
                self._update_node_metrics(ccn_metrics, message_saved.id, NodeType.CCN)
                logger.info(f"Saved {len(crn_metrics)} Crn metrics and {len(ccn_metrics)} Ccn metrics")

            else:
                logger.info(f"No new message, last update at: {Utils.convert_unix_to_datetime(update_time)}")
            
            current_time = int(time.time()) 
            time_since_message = current_time - update_time
            time_betwwen_messages = 600
            
            if time_since_message < time_betwwen_messages:
                sleep_time = time_betwwen_messages - time_since_message
                logger.info(f"Sleeping for {round(sleep_time,1)}")
                time.sleep(sleep_time)
            else:
                time.sleep(30)

    def NofitySubscribers(self, nodes : list[CcnMetricCreate | CrnMetricCreate]) -> None:
        subscribers_by_node_id = self.repository.get_subscribers_indexed_by_node_id()

        nodes_to_notify = defaultdict(list)

        for node in nodes:
            if node.node_id in subscribers_by_node_id and not node.status:
                for subscriber in subscribers_by_node_id[node.node_id]:
                    if subscriber.type == SubscribeType.EMAIL:
                        nodes_to_notify[subscriber.value].append(node)

        for subscriber_email, nodes in nodes_to_notify.items():
            self.send_notification(subscriber_email, nodes)
                        
        
    def send_notification(
            self, subscriber_email: str, nodes: list[CcnMetricCreate | CrnMetricCreate]
            ) -> None:
        
        initial_message = "Alert: Some of the nodes you are subscribed have failed metrics.\n\n"

        message = initial_message
        for node in nodes:
            failed_metrics = self._identify_failed_metrics(node)
            message += f"Node: {node.url}\n"
            message += f"Time: {Utils.convert_unix_to_datetime(node.measured_at)}\n"
            message += f"Missing metrics:\n"
            for metric in failed_metrics:
                message += f"    - {metric}\n"
            message += "\n"

        # For testing
        if subscriber_email.lower() == "equilibrium.k21@gmail.com":
            Utils.send_email(
                subscriber_email,
                "Aleph node is offline",
                message
            )

        print(f"Sending email to {subscriber_email}:\n{message}")

    def _identify_failed_metrics(self, node) -> list[str]:
        if isinstance(node, CrnMetricCreate):
            metrics = ["base_latency", "base_latency_ipv4", "full_check_latency", "diagnostic_vm_latency"]
        elif isinstance(node, CcnMetricCreate):
            metrics = [
                "txs_total", "base_latency", "metrics_latency", "pending_messages",
                "aggregate_latency", "base_latency_ipv4", "eth_height_remaining",
                "file_download_latency"
            ]
        else:
            return []

        failed_metrics = [metric for metric in metrics if getattr(node, metric) is None]
        return failed_metrics
    
    def _update_node_metrics(
            self,
            node_metrics: list[BaseCnnMetric] | list[BaseCrnMetric],
            message_id: uuid.UUID, 
            node_type: NodeType
        ):
        nodes_db = self._get_nodes_indexed_by_aleph_node_id()
        
        node_metrics_to_update = []
        node_metric_down = []

        for node_metric in node_metrics:
            if node_metric.node_id not in nodes_db:
                node_db = self.repository.save_node(
                    NodeCreate(
                        aleph_node_id=node_metric.node_id,
                        type=node_type
                    )
                )
            else:
                node_db = self.repository.get_node_by_aleph_node_id(node_metric.node_id)

            if node_type == NodeType.CRN:
                node_status = self.all_metrics_present_crn(node_metric)
                metric_create = CrnMetricCreate(
                    asn=node_metric.asn,
                    url=node_metric.url,
                    as_name=node_metric.as_name,
                    version=node_metric.version,
                    measured_at=node_metric.measured_at,
                    base_latency=node_metric.base_latency,
                    base_latency_ipv4=node_metric.base_latency_ipv4,
                    full_check_latency=node_metric.full_check_latency,
                    diagnostic_vm_latency=node_metric.diagnostic_vm_latency,
                    node_id=node_db.id,
                    message_id=message_id,
                    status=node_status
                )
            elif node_type == NodeType.CCN:
                node_status = self.all_metrics_present_ccn(node_metric)
                metric_create = CcnMetricCreate(
                    asn=node_metric.asn,
                    url=node_metric.url,
                    as_name=node_metric.as_name,
                    version=node_metric.version,
                    txs_total=node_metric.txs_total,
                    measured_at=node_metric.measured_at,
                    base_latency=node_metric.base_latency,
                    metrics_latency=node_metric.metrics_latency,
                    pending_messages=node_metric.pending_messages,
                    aggregate_latency=node_metric.aggregate_latency,
                    base_latency_ipv4=node_metric.base_latency_ipv4,
                    eth_height_remaining=node_metric.eth_height_remaining,
                    file_download_latency=node_metric.file_download_latency,
                    node_id=node_db.id,
                    message_id=message_id,
                    status=node_status
                )

            if node_status is False:
                node_metric_down.append(metric_create)
            
            node_metrics_to_update.append(metric_create)

        if node_type == NodeType.CRN:
            self.repository.bulk_save_crn_nodes_metrics(node_metrics_to_update)
        elif node_type == NodeType.CCN:
            self.repository.bulk_save_ccn_nodes_metrics(node_metrics_to_update)

        self.NofitySubscribers(node_metric_down)
                            
        
    def _send_notification(self):
        pass

    def _get_nodes_indexed_by_aleph_node_id(self):
        nodes = self.repository.get_all_nodes()
        
        return {node.aleph_node_id: NodeSchema(**node.model_dump()) for node in nodes}
        
    def get_crn_from_subscriber(self, subcriber_id: uuid.UUID):
        self.repository.get_latest_crn_metric_for_subscriber_nodes(subcriber_id)

    def _get_last_crn_metrics_indexed_by_node_id(self) -> dict[uuid.UUID, CrnMetricSchema]:
        latest_crn_metrics = self.repository.get_latest_crn_metrics()

        return {crn_metric.node_id: CrnMetricSchema.model_validate(crn_metric) for crn_metric in latest_crn_metrics}
    
    def _get_last_ccn_metrics_indexed_by_node_id(self) -> dict[uuid.UUID, CrnMetricSchema]:
        latest_ccn_metrics = self.repository.get_latest_ccn_metrics()

        return {ccn_metric.node_id: CcnMetricSchema.model_validate(ccn_metric) for ccn_metric in latest_ccn_metrics}
    
    def _get_subscriber_indexed_by_node_id(
            self, subscriber_id: uuid.UUID,  subscriber_repository: SubscribeRepository
        ) -> dict:
        subscriptions = subscriber_repository.get_subscriptions_by_subscriber_id(subscriber_id)

        return {subscription.node_id : subscription for subscription in subscriptions}


    def fetch_all_nodes_and_subscribed(
            self,
            subscribed_id: uuid.UUID,
            subscriber_repository: SubscribeRepository,
            messageRepository: MessageRepository
        ) -> NodesMetrics:

        last_message = messageRepository.get_last_message()

        if last_message is None:
             raise HTTPException(status_code=404, detail="No aleph message found.")

        #TODO: improve queries.
        nodes = self.repository.get_all_nodes()
        last_crn_metrics = self._get_last_crn_metrics_indexed_by_node_id()
        last_ccn_metrics = self._get_last_ccn_metrics_indexed_by_node_id()
        subscriptions_by_node_id = self._get_subscriber_indexed_by_node_id(subscribed_id, subscriber_repository)

        node_metrics = []
        last_metric = None

        for node in nodes:
            if node.type == NodeType.CCN:
                if node.id in last_ccn_metrics:
                    last_metric = CcnMetricsResponseSchema(**last_ccn_metrics[node.id].__dict__)
                else:
                    logger.info(f"Last ccn metric do not have the aleph node id: {node.aleph_node_id}")
            elif node.type == NodeType.CRN:
                if node.id in last_crn_metrics:
                    last_metric = CrnMetricsResponseSchema(**last_crn_metrics[node.id].__dict__)
                else:
                    logger.info(f"Last crn metric do not have the aleph node id: {node.aleph_node_id}")

            if last_metric is None:
                continue

            node_metric_body = NodeMetricsSubscribedBody(
                subscribed=node.id in subscriptions_by_node_id,
                node_id=node.id,
                aleph_node_id=node.aleph_node_id,
                node_type=node.type,
                last_metric=last_metric
            )

            node_metrics.append(node_metric_body)

        nodes = NodesMetrics(
            updated_at=Utils.convert_unix_to_datetime(last_message.time),
            message_hash=last_message.item_hash,
            metrics=node_metrics
        )

        return nodes
    
    def scheduled_metrics_deletion(self, days_old):
        time.sleep(30)
        while True:
            logger.info("Starting the scheduled deletion of old metrics.")
            deleted_ccn_count = self.repository.delete_old_ccn_metrics(days_old)
            logger.info(f"Deleted {deleted_ccn_count} old CCN metrics.")

            deleted_crn_count = self.repository.delete_old_crn_metrics(days_old)
            logger.info(f"Deleted {deleted_crn_count} old CRN metrics.")
            logger.info("Scheduled deletion complete. Waiting 24 hours for the next deletion.")
            time.sleep(86400)
            
    @staticmethod
    def all_metrics_present_crn(crn_node_metric: BaseCrnMetric):
        metrics = ["base_latency", "base_latency_ipv4", "full_check_latency", "diagnostic_vm_latency"]
        return all(getattr(crn_node_metric, metric) is not None for metric in metrics)
    
    @staticmethod
    def all_metrics_present_ccn(crn_node_metric: BaseCrnMetric):
        metrics = [
                    "txs_total", "base_latency", "metrics_latency", "pending_messages",
                    "aggregate_latency", "base_latency_ipv4", "eth_height_remaining",
                    "file_download_latency"
                ]
        return all(getattr(crn_node_metric, metric) is not None for metric in metrics)


    @staticmethod
    def _fetch_and_extract_node_metrics() -> MessageNetworkMetrics:
        url = "https://api2.aleph.im/api/v0/messages.json?addresses=0x4D52380D3191274a04846c89c069E6C3F2Ed94e4&pagination=1&page=1"
        response = requests.get(url)

        if response.status_code != 200:
            return None

        try:
            data = response.json()
            message = None
            for item in data.get('messages', []):
                #TODO:Also fetch [aleph-scoring-scores]
                if item.get("content", {}).get("type") == "aleph-network-metrics":
                    message = MessageNetworkMetrics.parse_obj(item)

            return message

        except ValidationError as e:
            logger.error(f"ValidationError: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error: {str(e)}")
            return None
