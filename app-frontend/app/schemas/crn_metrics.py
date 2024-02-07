from datetime import datetime
from typing import Optional
import uuid

from pydantic import BaseModel, validator


class BaseCrnMetric(BaseModel):
    asn: Optional[int] = None
    url: Optional[str] = None
    as_name: Optional[str] = None
    version: Optional[str] = None
    measured_at: Optional[float] = None
    measured_at_formatted: Optional[str] = None
    base_latency: Optional[float] = None
    base_latency_ipv4: Optional[float] = None
    full_check_latency: Optional[float] = None
    diagnostic_vm_latency: Optional[float] = None

class CrnMetricCreate(BaseCrnMetric):
    message_id: uuid.UUID
    node_id: uuid.UUID
    status: bool


class CrnMetricSchema(BaseCrnMetric):
    id: uuid.UUID
    node_id: uuid.UUID
    status: bool

    class config:
        orm_mode = True


class CrnMetricsResponseSchema(BaseModel):
    id: uuid.UUID
    asn: Optional[int] = None
    url: Optional[str] = None
    as_name: Optional[str] = None
    version: Optional[str] = None
    measured_at: Optional[float] = None
    measured_at_formatted: Optional[str] = None
    base_latency: Optional[float] = None
    base_latency_ipv4: Optional[float] = None
    full_check_latency: Optional[float] = None
    diagnostic_vm_latency: Optional[float] = None
    status: bool


    @validator('measured_at_formatted', always=True, pre=True)
    def format_measured_at(cls, v, values):
        measured_at = values.get('measured_at')
        if measured_at is not None:
            dt_object = datetime.fromtimestamp(measured_at)
            return dt_object.strftime("%d-%m-%Y %H:%M:%S")
        return None




