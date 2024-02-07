from typing import Optional, List
import uuid
from pydantic import BaseModel

class BaseCnnMetric(BaseModel):
    asn: Optional[int] = None
    url: Optional[str] = None
    as_name: Optional[str] = None
    node_id: Optional[str] = None
    version: Optional[str] = None
    txs_total: Optional[int] = None
    measured_at: Optional[float] = None
    base_latency: Optional[float] = None
    metrics_latency: Optional[float] = None
    pending_messages: Optional[int] = None
    aggregate_latency: Optional[float] = None
    base_latency_ipv4: Optional[float] = None
    eth_height_remaining: Optional[int] = None
    file_download_latency: Optional[float] = None

class BaseCrnMetric(BaseModel):
    asn: Optional[int] = None
    url: Optional[str] = None
    as_name: Optional[str] = None
    node_id: Optional[str] = None
    version: Optional[str] = None
    measured_at: Optional[float] = None
    base_latency: Optional[float] = None
    base_latency_ipv4: Optional[float] = None
    full_check_latency: Optional[float] = None
    diagnostic_vm_latency: Optional[float] = None

class Metrics(BaseModel):
    ccn: List[BaseCnnMetric]
    crn: List[BaseCrnMetric]
    server: str
    server_asn: int
    server_as_name: str

class ContentDetails(BaseModel):
    tags: List[str]
    metrics: Metrics
    version: str

class Content(BaseModel):
    time: float
    type: str
    address: str
    content: ContentDetails

class MessageNetworkMetrics(BaseModel):
    item_hash: str
    type: str
    chain: str
    sender: str
    signature: str
    item_type: str
    item_content: Optional[str]
    content: Content
    time: float
    channel: str
    size: int
    confirmations: List[dict]
    confirmed: bool


