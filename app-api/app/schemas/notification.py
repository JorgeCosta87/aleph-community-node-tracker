from datetime import datetime
import uuid
from pydantic import BaseModel

class BaseNotification(BaseModel):
    message: str
    metrics_failed: str
    node_status: bool

class Create(BaseNotification):
    pass

class Update(BaseNotification):
    pass


class NotificationSchema(BaseNotification):
    id: uuid.UUID
    created_at: datetime

    class config:
        from_attributes = True