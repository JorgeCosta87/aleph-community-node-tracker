from __future__ import annotations
import uuid

from pydantic import BaseModel

from schemas.constants import SubscribeType

class BaseUserSession(BaseModel):
    session_id: uuid.UUID
    verification_token: str
    is_verified: bool

class UserSessionCreate(BaseUserSession):
    subscriber_id: uuid.UUID

class UserSessionUpdate(BaseModel):
    session_id: uuid.UUID | None
    is_verified: bool | None

class UserSessionSchema(BaseUserSession):
    id: uuid.UUID
    subscriber_id: uuid.UUID

class UserSessionBodyResponse(BaseModel):
    subscriber_id: uuid.UUID
    session_id: uuid.UUID
    type: SubscribeType
    value: str
