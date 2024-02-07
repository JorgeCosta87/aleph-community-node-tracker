import uuid

from pydantic import BaseModel
from app.schemas.crn_metrics import CrnMetricSchema
from app.utils.constants import SubscribeType
from app.schemas.user_session import UserSessionSchema


class BaseSubscription(BaseModel):
    node_id: uuid.UUID
    subscriber_id: uuid.UUID

class SubscriptionCreate(BaseSubscription):
    pass

class SubscriptionUpdate(BaseSubscription):
    pass

class SubscriptionSchema(BaseSubscription):
    id: uuid.UUID
