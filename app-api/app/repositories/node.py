import logging
import uuid
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.schemas.node import NodeCreate, NodeSchema
from app.models.node import Node
from app.models.crn_metric import CrnMetric
from app.schemas.crn_metrics import CrnMetricCreate, CrnMetricSchema
from app.models.message import Message
from app.models.subscriber import Subscriber, Subscription
from app.models.user_session import UserSession


logger = logging.getLogger(__name__) 

class NodeRepository():
    def __init__(self, db_session: Session):
        self.db_session = db_session

    
    def get_crn_node_by_node_id(self, node_id: int) -> NodeSchema:
        model = self.db_session.query(Node).filter_by(node_id=node_id).first()

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

    
    def save_crn_node(self, crn_node_create: NodeCreate) -> NodeSchema:
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