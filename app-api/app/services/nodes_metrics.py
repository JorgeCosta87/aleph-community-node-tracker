import logging
import time
import uuid
from fastapi import HTTPException
from pydantic import ValidationError
import requests

from app.schemas.message_metrics import BaseCrnMetric, MessageNetworkMetrics
from app.schemas.node import NodeCreate, NodeMetricsSubscribedBody, NodeSchema, NodesMetrics
from app.repositories.node import NodeRepository
from app.utils.utils import Utils
from app.repositories.message import MessageRepository
from app.schemas.message import MessageCreate
from app.schemas.crn_metrics import CrnMetricCreate, CrnMetricsResponseSchema
from app.utils.constants import NodeType
from app.repositories.subscribe import SubscribeRepository

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

            #If the hash isn't on the db, we update the nodes
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
                self._update_crn_metrics(crn_metrics, message_saved.id)
                logger.info(f"{len(crn_metrics)} Crn metrics saved")

                current_time = int(time.time()) 
                time_since_message = current_time - update_time
                time_betwwen_messages = 540
                
                if time_since_message < time_betwwen_messages:
                    sleep_time = time_betwwen_messages - time_since_message
                    logger.info(f"Sleeping for {round(sleep_time,1)} seconds to make up for 9 minutes since message time.")
                    time.sleep(sleep_time)  

            else:
                logger.info(f"No new message last update at: {Utils.convert_unix_to_datetime(update_time)}")

            time.sleep(60)

    def _update_crn_metrics(self, crn_nodes_metrics: list[BaseCrnMetric], message_id: uuid.UUID):
        
        nodes_db = self._get_crn_nodes_indexed_by_node_id()
        
        crn_node_metrics_to_update = []
        for crn_node_metric in crn_nodes_metrics:
            if crn_node_metric.node_id not in nodes_db:
                crn_db = self.repository.save_crn_node(
                    NodeCreate(
                        node_id=crn_node_metric.node_id,
                        type=NodeType.CRN
                    )
                )
            else:
                crn_db = self.repository.get_crn_node_by_node_id(crn_node_metric.node_id)

            node_status = self.all_metrics_present(crn_node_metric)

            if node_status is False:
                self._send_notification()
            
            crn_node_metric_create = CrnMetricCreate(
                asn=crn_node_metric.asn,
                url=crn_node_metric.url,
                as_name=crn_node_metric.as_name,
                version=crn_node_metric.version,
                measured_at=crn_node_metric.measured_at,
                base_latency=crn_node_metric.base_latency,
                base_latency_ipv4=crn_node_metric.base_latency_ipv4,
                full_check_latency=crn_node_metric.full_check_latency,
                diagnostic_vm_latency=crn_node_metric.diagnostic_vm_latency,
                node_id=crn_db.id,
                message_id=message_id,
                status=self.all_metrics_present(crn_node_metric)
            )

            crn_node_metrics_to_update.append(crn_node_metric_create)

        self.repository.bulk_save_crn_nodes_metrics(crn_node_metrics_to_update)
                        
    
    def _send_notification(self):
        pass

    def _get_crn_nodes_indexed_by_node_id(self):
        crn_nodes = self.repository.get_all_nodes()
        return {node.node_id: NodeSchema(**node.__dict__) for node in crn_nodes}
        
    def get_crn_from_subscriber(self, subcriber_id: uuid.UUID):
        self.repository.get_latest_crn_metric_for_subscriber_nodes(subcriber_id)

    def _get_last_crn_metrics_indexed_by_node_id(self):
        latest_crn_metrics = self.repository.get_latest_crn_metrics()

        return {crn_metric.node_id: crn_metric for crn_metric in latest_crn_metrics}
    
    def _get_subscriber_indexed_by_node_id(
            self, subscriber_id: uuid.UUID,  subscriber_repository: SubscribeRepository
        ) -> dict:
        subscriptions = subscriber_repository.get_subscriptions_by_subscriber_id(subscriber_id)

        return {subscription.node_id : subscription for subscription in subscriptions}


    def fetch_all_nodes_check_is_subscribed(
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
        subscriptions_by_node_id = self._get_subscriber_indexed_by_node_id(subscribed_id, subscriber_repository)

        node_metrics = []

        for node in nodes:
            if node.type == NodeType.CCN:
                pass
            elif node.type == NodeType.CRN:
                last_metric = CrnMetricsResponseSchema(**last_crn_metrics[node.id].__dict__)
            

            node_metric_body = NodeMetricsSubscribedBody(
                subscribed=node.id in subscriptions_by_node_id,
                node_id=node.id,
                aleph_node_id=node.node_id,
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
            
            
    @staticmethod
    def all_metrics_present(crn_node_metric: BaseCrnMetric):
        metrics = ["base_latency", "base_latency_ipv4", "full_check_latency", "diagnostic_vm_latency"]
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
