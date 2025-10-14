from pydantic import BaseModel

class KafkaMessage(BaseModel):
    type: str

class KafkaStatus(KafkaMessage):
    status: str
    timestamp: float

class ClusterStatusMessage(KafkaStatus):
    cluster_name: str
    

class WebserverStatus(KafkaMessage):
    cluster_name: str
    status: str
    timestamp: float


class SimpleMessage(BaseModel):
    target_cluster: str
    resource: str
    method: str
    namespace: str
    data: str | None = None