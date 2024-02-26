
from datetime import datetime
import uuid

from sqlalchemy import Boolean, Column, ForeignKey, String, DateTime, func, JSON
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base

class Notification(Base):
    __tablename__ = 'notification'
    
    id: Mapped[UUID] = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    message: Mapped[str] = Column(String(255))
    metrics_failed: Mapped[dict] = Column(JSON)
    node_status: Mapped[bool] = Column(Boolean)
    created_at: Mapped[datetime] = Column(DateTime, server_default=func.now())

    subscription_id: Mapped[UUID] = Column(ForeignKey('subscription.id'))
    subscription: Mapped["Subscription"] = relationship("Subscription", back_populates="notifications")
    
