import uuid

from pydantic import BaseModel

from schemas.constants import SubscribeType
from schemas.user_session import UserSessionSchema


class BaseSubscriber(BaseModel):
    type: SubscribeType
    value: str

class SubscriberCreate(BaseSubscriber):
    pass

class SubscriberUpdate(BaseSubscriber):
    pass

class SubscriberSchema(BaseSubscriber):
    id: uuid.UUID
    user_session: UserSessionSchema | None
