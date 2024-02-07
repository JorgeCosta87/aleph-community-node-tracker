import logging
import uuid
from sqlalchemy.orm import Session

from app.models.node import Node
from app.models.message import Message
from app.schemas.message import MessageCreate, MessageSchema

logger = logging.getLogger(__name__) 

class MessageRepository():
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def get_last_message(self) -> MessageSchema | None:
        model = self.db_session.query(Message) \
            .order_by(Message.time.desc()).first()

        if model is None:
            return None

        return MessageSchema.model_validate(model, from_attributes=True)
    
    def get_message_by_hash(self, hash: str) -> MessageSchema | None:
        model = self.db_session.query(Message).filter_by(item_hash=hash).first()

        if model is None:
            return None
        
        return MessageSchema.model_validate(model, from_attributes=True)
    
    def save(self, message_create: MessageCreate) -> MessageSchema:
        model = Message(
            item_hash=message_create.item_hash,
            item_type=message_create.item_type,
            time=message_create.time,
            message_type=message_create.message_type
        )

        self.db_session.add(model)
        self.db_session.commit()
        self.db_session.refresh(model)

        return MessageSchema.model_validate(model, from_attributes=True)