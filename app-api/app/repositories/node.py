from collections import defaultdict
import logging
import uuid
from sqlalchemy import func
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.schemas.node import NodeCreate, NodeSchema
from app.models.node import Node
from app.models.crn_metric import CrnMetric
from app.models.ccn_metric import CcnMetric
from app.schemas.crn_metrics import CrnMetricCreate, CrnMetricSchema
from app.schemas.ccn_metrics import CcnMetricCreate, CcnMetricSchema
from app.models.message import Message
from app.models.subscriber import Subscriber, Subscription
from app.models.user_session import UserSession
from app.schemas.subscriber import SubscriberSchema
from app.schemas.user_session import UserSessionSchema


logger = logging.getLogger(__name__) 

class NodeRepository():
    def __init__(self, db_session: Session):
        self.db_session = db_session

    
    def get_node_by_aleph_node_id(self, aleph_node_id: str) -> NodeSchema:
        model = self.db_session.query(Node).filter_by(aleph_node_id=aleph_node_id).first()

        return NodeSchema.model_validate(model, from_attributes=True) 
 
    
    def get_all_nodes(self) -> list[NodeSchema]:
        models = self.db_session.query(Node).all()

        return [
            NodeSchema.model_validate(model, from_attributes=True) 
            for model in models
        ]
    
    def get_latest_crn_metrics(self) -> list[CrnMetricSchema]:
        latest_message_time = self.db_session.query(func.max(Message.time)).scalar()
        metrics = (self.db_session.query(CrnMetric)
                        .join(Message, CrnMetric.message_id == Message.id)
                        .filter(Message.time == latest_message_time)
                        .all())

        response_data = []
        for metric in metrics:
            response_data.append(
                CrnMetricSchema(
                    id=metric.id,
                    asn=metric.asn,
                    url=metric.url,
                    as_name=metric.as_name,
                    version=metric.version,
                    measured_at=metric.measured_at,
                    base_latency=metric.base_latency,
                    base_latency_ipv4=metric.base_latency_ipv4,
                    full_check_latency=metric.full_check_latency,
                    diagnostic_vm_latency=metric.diagnostic_vm_latency,
                    node_id=metric.node_id,
                    status=metric.status
                )
            )
        return response_data
    

    def get_latest_ccn_metrics(self) -> list[CcnMetricSchema]:
        latest_message_time = self.db_session.query(func.max(Message.time)).scalar()
        metrics = (
                        self.db_session.query(CcnMetric)
                        .join(Message, CcnMetric.message_id == Message.id)
                        .filter(Message.time == latest_message_time)
                        .all()
                )

        response_data = []
        for metric in metrics:
            response_data.append(
                CcnMetricSchema.model_validate(metric, from_attributes=True)
            )
        return response_data

    
    def save_node(self, crn_node_create: NodeCreate) -> NodeSchema:
        node = Node(**crn_node_create.__dict__)

        self.db_session.add(node)
        self.db_session.commit()

        self.db_session.refresh(node)

        return NodeSchema.model_validate(node, from_attributes=True)
    
    def bulk_save_crn_nodes_metrics(
            self,
            crn_nodes_metrics: list[CrnMetricCreate]
        ):
        metrics_to_save = []

        for metric in crn_nodes_metrics:
            new_metric = CrnMetric(
                asn=metric.asn,
                url=metric.url,
                as_name=metric.as_name,
                version=metric.version,
                measured_at=metric.measured_at,
                base_latency=metric.base_latency,
                base_latency_ipv4=metric.base_latency_ipv4,
                full_check_latency=metric.full_check_latency,
                diagnostic_vm_latency=metric.diagnostic_vm_latency,
                node_id=metric.node_id,
                message_id=metric.message_id,
                status=metric.status
            )
            metrics_to_save.append(new_metric)

        self.db_session.bulk_save_objects(metrics_to_save)
        self.db_session.commit()
        

    def bulk_save_ccn_nodes_metrics(
        self,
        ccn_nodes_metrics: list[CcnMetricCreate]
    ):
        metrics_to_save = []

        for metric in ccn_nodes_metrics:
            new_metric = CcnMetric(
                asn=metric.asn,
                url=metric.url,
                as_name=metric.as_name,
                version=metric.version,
                txs_total=metric.txs_total,
                measured_at=metric.measured_at,
                base_latency=metric.base_latency,
                metrics_latency=metric.metrics_latency,
                pending_messages=metric.pending_messages,
                aggregate_latency=metric.aggregate_latency,
                base_latency_ipv4=metric.base_latency_ipv4,
                eth_height_remaining=metric.eth_height_remaining,
                file_download_latency=metric.file_download_latency,
                status=metric.status,
                message_id=metric.message_id,
                node_id=metric.node_id,

            )
            metrics_to_save.append(new_metric)

        self.db_session.bulk_save_objects(metrics_to_save)
        self.db_session.commit()

    def get_last_metric(self) -> CrnMetricSchema | None:
        model = self.db_session.query(CrnMetric) \
        .order_by(CrnMetric.measured_at.desc()).first()

        if model is None:
            return None

        return CrnMetricSchema.model_validate(model, from_attributes=True)
    
    def get_crn_node_metrics_for_session(self, session_id: uuid.UUID):
        crn_metrics = self.db_session.query(CrnMetric)\
                            .join(Node, CrnMetric.crn_node_id == Node.id)\
                            .join(Subscription, Node.id == Subscription.node_id)\
                            .join(Subscriber, Subscription.subscriber_id == Subscriber.id)\
                            .join(UserSession, Subscriber.id == UserSession.subscriber_id)\
                            .filter(UserSession.id == session_id)\
                            .all()

        return crn_metrics
    
    def get_latest_crn_metric_for_subscriber_nodes(self, subscriber_id: uuid.UUID):
        latest_crn_metrics = self.db_session.query(CrnMetric)\
            .join(Node, Node.id == CrnMetric.node_id)\
            .join(Subscription, Subscription.id == Node.id)\
            .join(Subscriber, Subscriber.id == Subscription.subscriber_id)\
            .join(Message, Message.id == CrnMetric.message_id)\
            .filter(Subscriber.id == subscriber_id)\
            .order_by(Message.time.desc())\
            .first()

        return latest_crn_metrics
    
    def delete_old_crn_metrics(self, days_old: int) -> int:
        target_date = datetime.now() - timedelta(days=days_old)
        target_date_unix = target_date.timestamp()

        count = self.db_session.query(CrnMetric).filter(CrnMetric.measured_at < target_date_unix).delete()
        self.db_session.commit()

        return count

    def delete_old_ccn_metrics(self, days_old: int) -> int:
        target_date = datetime.now() - timedelta(days=days_old)
        target_date_unix = target_date.timestamp()

        count = self.db_session.query(CcnMetric).filter(CcnMetric.measured_at < target_date_unix).delete()
        self.db_session.commit()

        return count
    
    def get_subscribers_indexed_by_node_id(self) -> dict[uuid.UUID, list[SubscriberSchema]]:
            subscriptions = self.db_session.query(Subscription).all()

            subscribers_by_node_id = {}

            for subscription in subscriptions:
                node_id = subscription.node_id
                logger.info(subscription.subscriber)
                subscriber_schema = SubscriberSchema(
                    id=subscription.subscriber.id,
                    type=subscription.subscriber.type,
                    value=subscription.subscriber.value,
                    user_session=UserSessionSchema.model_validate(
                        subscription.subscriber.user_session, from_attributes=True
                        )
                )

                if node_id not in subscribers_by_node_id:
                    subscribers_by_node_id[node_id] = [subscriber_schema]
                else:
                    subscribers_by_node_id[node_id].append(subscriber_schema)

            return subscribers_by_node_id