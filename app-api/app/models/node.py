from typing import TYPE_CHECKING
import uuid

from sqlalchemy import Column, String, Float, Integer, Enum
from sqlalchemy.orm import declarative_base, relationship, Mapped
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base
from app.utils.constants import NodeType


class Node(Base):
    __tablename__ = 'node'

    id: Mapped[UUID] = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    aleph_node_id: Mapped[str] = Column(String, index=True, unique=True, nullable=False)
    type : Mapped[NodeType] = Column(Enum(NodeType))

    subscriptions: Mapped[list["Subscription"]] = relationship(
        "Subscription", 
        back_populates="node",
        cascade="all, delete"
    )
"""
    crn_metrics: Mapped[list["CrnMetric"]] = relationship(
        "CrnMetric", 
        back_populates="node",
        cascade="all, delete"
    )

    ccn_metrics: Mapped[list["CcnMetric"]] = relationship(
        "CcnMetric", 
        back_populates="node",
        cascade="all, delete"
    )

"""
