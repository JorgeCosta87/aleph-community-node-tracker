from datetime import datetime
from typing import Optional
import uuid

from pydantic import BaseModel, validator


class BaseCcnMetric(BaseModel):
    asn: Optional[int] = None
    url: Optional[str] = None
    as_name: Optional[str] = None
    version: Optional[str] = None
    txs_total: Optional[int] = None
    measured_at: Optional[float] = None
    measured_at_formatted: Optional[str] = None
    base_latency: Optional[float] = None
    metrics_latency: Optional[float] = None
    pending_messages: Optional[int] = None
    aggregate_latency: Optional[float] = None
    base_latency_ipv4: Optional[float] = None
    eth_height_remaining: Optional[int] = None
    file_download_latency: Optional[float] = None

class CcnMetricCreate(BaseCcnMetric):
    message_id: uuid.UUID
    node_id: uuid.UUID
    status: bool


class CcnMetricSchema(BaseCcnMetric):
    id: uuid.UUID
    node_id: uuid.UUID
    status: bool

    class config:
        orm_mode = True


class CcnMetricsResponseSchema(BaseModel):
    id: uuid.UUID
    asn: Optional[int] = None
    url: Optional[str] = None
    as_name: Optional[str] = None
    version: Optional[str] = None
    txs_total: Optional[int] = None
    measured_at: Optional[float] = None
    measured_at_formatted: Optional[str] = None
    base_latency: Optional[float] = None
    metrics_latency: Optional[float] = None
    pending_messages: Optional[int] = None
    aggregate_latency: Optional[float] = None
    base_latency_ipv4: Optional[float] = None
    eth_height_remaining: Optional[int] = None
    file_download_latency: Optional[float] = None
    status: bool


    @validator('measured_at_formatted', always=True, pre=True)
    def format_measured_at(cls, v, values):
        measured_at = values.get('measured_at')
        if measured_at is not None:
            dt_object = datetime.fromtimestamp(measured_at)
            return dt_object.strftime("%d-%m-%Y %H:%M:%S")
        return None




