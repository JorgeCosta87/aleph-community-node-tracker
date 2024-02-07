import uuid

from pydantic import BaseModel
from app.schemas.crn_metrics import CrnMetricSchema

class BaseMessage(BaseModel):
    item_hash: str
    item_type: str
    time: float
    message_type: str

class MessageCreate(BaseMessage):
    pass

class MessageSchema(BaseMessage):
    id: uuid.UUID