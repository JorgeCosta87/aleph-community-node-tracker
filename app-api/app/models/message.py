import uuid
from sqlalchemy import Column, String, Float
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base

class Message(Base):
    __tablename__ = 'message'

    id: Mapped[UUID] = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    item_hash = Column(String, unique=True)
    item_type = Column(String)
    time = Column(Float)
    message_type = Column(String)
