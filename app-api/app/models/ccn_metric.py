import uuid

from sqlalchemy import Column, String, Float, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base


class CcnMetric(Base):
    __tablename__ = 'ccn_metric'

    id: Mapped[UUID] = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    asn: Mapped[Integer] = Column(Integer, nullable=True)
    url: Mapped[String] = Column(String, nullable=True)
    as_name: Mapped[String] = Column(String, nullable=True)
    version: Mapped[String] = Column(String, nullable=True)
    txs_total: Mapped[int] = Column(Integer, nullable=True)
    measured_at: Mapped[Float] = Column(Float, nullable=True)
    measured_at_formatted: Mapped[str] = Column(Float, nullable=True)
    base_latency: Mapped[Float] = Column(Float, nullable=True)
    metrics_latency: Mapped[float] = Column(Float, nullable=True)
    pending_messages: Mapped[int] = Column(Integer, nullable=True)
    aggregate_latency: Mapped[float] = Column(Float, nullable=True)
    base_latency_ipv4: Mapped[Float] = Column(Float, nullable=True)
    eth_height_remaining: Mapped[int] = Column(Integer, nullable=True)
    file_download_latency: Mapped[float] = Column(Float, nullable=True)
    status: Mapped[bool] = Column(Boolean)

    message_id: Mapped[UUID] = Column(UUID(as_uuid=True), ForeignKey('message.id'))
    node_id: Mapped[UUID] = Column(ForeignKey("node.id"))
    """
        node: Mapped["Node"] = relationship(
        "Node", 
        back_populates="ccn_metrics"
    )
    """
