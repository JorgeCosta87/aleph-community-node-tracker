from datetime import datetime
import uuid
from pydantic import BaseModel
from app.utils.constants import NodeType
from app.schemas.crn_metrics import CrnMetricsResponseSchema
from app.schemas.ccn_metrics import CcnMetricsResponseSchema


class BaseNode(BaseModel):
    node_id: str
    type: NodeType

class NodeCreate(BaseNode):
    pass

class NodeSchema(BaseNode):
    id: uuid.UUID

    class config:
        from_attributes = True

class NodeMetricsSubscribedBody(BaseModel):
    subscribed: bool
    node_id: uuid.UUID
    aleph_node_id: str
    node_type: NodeType
    last_metric: CrnMetricsResponseSchema | CcnMetricsResponseSchema

class NodesMetrics(BaseModel):
    updated_at: str
    message_hash: str
    metrics: list[NodeMetricsSubscribedBody]
