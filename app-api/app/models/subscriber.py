
from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship, Mapped

import uuid

from app.db.base import Base

class Subscription(Base):
    __tablename__ = 'subscription'

    id: Mapped[UUID] = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    node_id: Mapped[UUID] = Column(ForeignKey("node.id"))  
    subscriber_id: Mapped[UUID] = Column(ForeignKey('subscriber.id'))

    node: Mapped["Node"] = relationship(
        "Node", 
        back_populates="subscriptions"
    )
    subscriber: Mapped["Subscriber"] = relationship(
        "Subscriber", 
        back_populates="subscriptions"
    )
    notifications: Mapped[list["Notification"]] = relationship(
        "Notification", 
        back_populates="subscription", 
        cascade="all, delete"
    )


class Subscriber(Base):
    __tablename__ = 'subscriber'
    id: Mapped[UUID] = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    type: Mapped[str] = Column(String(50))
    value: Mapped[str] = Column(String(255))

    subscriptions: Mapped[list["Subscription"]] = relationship(
        "Subscription", 
        back_populates="subscriber", 
        cascade="all, delete"
    )

    user_session: Mapped["UserSession"] = relationship(
        "UserSession", 
        back_populates="subscriber", 
        uselist=False,
        cascade="all, delete-orphan"
    )

