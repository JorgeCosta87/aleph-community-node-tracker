import uuid

from sqlalchemy import Column, String, Float, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base


class CrnMetric(Base):
    __tablename__ = 'crn_metric'

    id: Mapped[UUID] = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    asn: Mapped[Integer] = Column(Integer, nullable=True)
    url: Mapped[String] = Column(String, nullable=True)
    as_name: Mapped[String] = Column(String, nullable=True)
    version: Mapped[String] = Column(String, nullable=True)
    measured_at: Mapped[Float] = Column(Float, nullable=True)
    base_latency: Mapped[Float] = Column(Float, nullable=True)
    base_latency_ipv4: Mapped[Float] = Column(Float, nullable=True)
    full_check_latency: Mapped[Float] = Column(Float, nullable=True)
    diagnostic_vm_latency: Mapped[Float] = Column(Float, nullable=True)
    status: Mapped[bool] = Column(Boolean, nullable=False)

    message_id: Mapped[UUID] = Column(UUID(as_uuid=True), ForeignKey('message.id'))
    node_id: Mapped[UUID] = Column(ForeignKey("node.id"))
    """
        node: Mapped["Node"] = relationship(
        "Node", 
        back_populates="crn_metrics"
    )
    """
