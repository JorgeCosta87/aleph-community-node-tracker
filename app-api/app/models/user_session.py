
from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, String, Boolean, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped

import uuid

from app.db.base import Base


class UserSession(Base):
    __tablename__ = 'session'

    id: Mapped[UUID] = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    session_id: Mapped[UUID]  = Column(UUID)
    subscriber_id: Mapped[UUID] = Column(UUID(as_uuid=True), ForeignKey('subscriber.id'))
    verification_token: Mapped[String] = Column(String)
    is_verified: Mapped[bool] = Column(Boolean)
    verified_at: Mapped[datetime] = Column(DateTime, server_default=func.now())

    subscriber: Mapped["Subscriber"] = relationship(
        "Subscriber", 
        back_populates="user_session"
    )