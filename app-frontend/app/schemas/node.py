import uuid
from pydantic import BaseModel, validator

from schemas.constants import NodeType
from schemas.crn_metrics import CrnMetricsResponseSchema
from schemas.ccn_metrics import CcnMetricsResponseSchema


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

    @validator('last_metric', pre=True)
    def set_metric_type(cls, value, values):
        if 'node_type' in values:
            if values['node_type'] == NodeType.CRN:
                return CrnMetricsResponseSchema(**value)
            elif values['node_type'] == NodeType.CCN:
                return CcnMetricsResponseSchema(**value)
        raise ValueError("Invalid node_type for determining metrics schema")

class NodesMetrics(BaseModel):
    updated_at: str
    message_hash: str
    metrics: list[NodeMetricsSubscribedBody]
