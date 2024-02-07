import enum


class SubscribeType(str, enum.Enum):
    EMAIL = "EMAIL",
    TELEGRAM = "TELEGRAM"

class NodeType(str, enum.Enum):
    CRN ="COMPUTE_RESOURCE_NODE"
    CCN = "CORE_CHANNEL_NODE"
