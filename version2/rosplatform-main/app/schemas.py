from pydantic import BaseModel, EmailStr, constr, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from typing import Optional, Dict, Any, List
from datetime import datetime

# User schemas
class UserBase(BaseModel):
    username: constr(pattern=r"^[a-zA-Z0-9_-]{3,20}$")
    user_type: str
    email: EmailStr
    phone: Optional[str] = None

class UserCreate(UserBase):
    password: str
    workspaces: List[str]

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[constr(pattern=r"^[a-zA-Z0-9_-]{3,20}$")] = None
    is_active: Optional[bool] = None
    user_type: Optional[str] = None
    password: Optional[str] = None
    workspaces: Optional[List[str]] = None


class PasswordChange(BaseModel):
    current_password: str
    new_password: str

class User(UserBase):
    id: str
    is_active: bool
    user_type: str
    hashed_password: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class UserWithWorkspace(User):
    workspaces: Optional[List[str]] = None
    clusters: Optional[List[str]] = None

# Workspace schemas
class WorkspaceBase(BaseModel):
    name: constr(pattern=r"^[a-zA-Z0-9_-]{3,50}$")
    clusters: List[str]
    description: Optional[str] = None

class WorkspaceCreate(WorkspaceBase):
    pass

class Workspace(WorkspaceBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    users: Optional[List[str]] = None

    class Config:
        from_attributes = True

# Project schemas
class ProjectBase(BaseModel):
    name: constr(pattern=r"^[a-zA-Z0-9_-]{3,50}$")
    workspace_name: str
    status: str
    
class ProjectCreate(ProjectBase):
    description: Optional[str] = None
    clusters: List[str]

class ProjectUpdate(BaseModel):
    status: str

class Project(ProjectCreate):
    username: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Cluster schemas
class ClusterBase(BaseModel):
    name: constr(pattern=r"^[a-zA-Z0-9_-]{3,50}$")
    description: Optional[str] = None

class ClusterCreate(ClusterBase):
    project_name: str

class Cluster(ClusterBase):
    id: str
    project_name: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Platform Service schemas
class PlatformServiceBase(BaseModel):
    name: constr(pattern=r"^[a-zA-Z0-9_-]{3,50}$")
    ip: constr(pattern=r"^(\d{1,3}\.){3}\d{1,3}$")
    port: int
    description: Optional[str] = None
    status: constr(pattern=r"^(active|inactive|maintenance)$")
    metadata: Optional[Dict[str, Any]] = None

class PlatformServiceCreate(PlatformServiceBase):
    pass

class PlatformServiceUpdate(BaseModel):
    ip: Optional[constr(pattern=r"^(\d{1,3}\.){3}\d{1,3}$")] = None
    port: Optional[int] = None
    description: Optional[str] = None
    status: Optional[constr(pattern=r"^(active|inactive|maintenance)$")] = None
    metadata: Optional[Dict[str, Any]] = None

class PlatformService(PlatformServiceBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class ResToken(BaseModel):
    access_token: str
    token_type: str
    user_id: str
    user_type: str

class TokenData(BaseModel):
    username: Optional[str] = None 


class ServiceMetadata(BaseModel):
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    updated_by: Optional[str] = None
    tags: Optional[List[str]] = Field(default_factory=list)

class PlatformServiceBase(BaseModel):
    name: str = Field(..., pattern=r"^[a-zA-Z0-9_-]{3,50}$")
    ip: str = Field(..., pattern=r"^(\d{1,3}\.){3}\d{1,3}$")
    port: int = Field(..., ge=1, le=65535)
    description: Optional[str] = None
    status: str = Field(..., pattern=r"^(active|inactive)$")
    metadata: Optional[ServiceMetadata] = None

class PlatformServiceCreate(PlatformServiceBase):
    pass

class PlatformServiceUpdate(BaseModel):
    ip: Optional[str] = Field(None, pattern=r"^(\d{1,3}\.){3}\d{1,3}$")
    port: Optional[int] = Field(None, ge=1, le=65535)
    description: Optional[str] = None
    status: Optional[str] = Field(None, pattern=r"^(active|inactive)$")
    metadata: Optional[ServiceMetadata] = None

class PlatformService(PlatformServiceBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ServiceSearchParams(BaseModel):
    name: Optional[str] = None
    ip: Optional[str] = None
    port: Optional[int] = None
    status: Optional[str] = Field(None, pattern=r"^(active|inactive)$") 


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None

class ErrorResponse(BaseModel):
    status: str = "error"
    error: ErrorDetail
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class SuccessResponse(BaseModel):
    status: str = "success"
    data: Optional[Any] = None
    message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# Kubernetes schemas
class ContainerPort(BaseModel):
    containerPort: int
    protocol: str = Field(..., pattern=r"^(TCP|UDP)$")

class ResourceRequirements(BaseModel):
    requests: Optional[Dict[str, str]] = None
    limits: Optional[Dict[str, str]] = None

class Container(BaseModel):
    name: str
    image: str
    ports: Optional[List[ContainerPort]] = None
    resources: Optional[ResourceRequirements] = None

class PodSpec(BaseModel):
    containers: List[Container]
    volumes: Optional[List[Dict[str, Any]]] = None
    restartPolicy: str = Field(..., pattern=r"^(Always|OnFailure|Never)$")

class PodCreate(BaseModel):
    name: str
    containers: List[Container]
    volumes: Optional[List[Dict[str, Any]]] = None
    restartPolicy: str = Field(..., pattern=r"^(Always|OnFailure|Never)$")

class DeploymentTemplate(BaseModel):
    containers: List[Container]

class DeploymentCreate(BaseModel):
    name: str
    replicas: int
    template: DeploymentTemplate

class ServicePort(BaseModel):
    port: int
    targetPort: int
    protocol: str = Field(..., pattern=r"^(TCP|UDP)$")

class ServiceCreate(BaseModel):
    name: str
    type: str = Field(..., pattern=r"^(ClusterIP|NodePort|LoadBalancer)$")
    ports: List[ServicePort]
    selector: Dict[str, str]

class PersistentVolumeCreate(BaseModel):
    name: str
    capacity: Dict[str, str]
    accessModes: List[str]
    persistentVolumeReclaimPolicy: str = Field(..., pattern=r"^(Retain|Recycle|Delete)$")
    storageClassName: str
    hostPath: Dict[str, str]

class PersistentVolumeClaimCreate(BaseModel):
    name: str
    accessModes: List[str]
    resources: Dict[str, Dict[str, str]]
    storageClassName: str 


class ScheduleCreate(BaseModel):
    policy_type: str
    yaml: str

# Example schemas showing different field definitions
class ExampleSchema(BaseModel):
    # Required fields
    required_field1: str = ...  # Method 1: Using ellipsis
    required_field2: str = Field(...)  # Method 2: Using Field
    
    # Optional fields
    optional_field1: Optional[str] = None  # Method 1: Using Optional
    optional_field2: str = Field(None)  # Method 2: Using Field with None
    
    # Fields with validation
    validated_field: str = Field(..., min_length=3, max_length=50)
    
    # Fields with default values
    default_field: str = Field("default_value")
    
    class Config:
        exclude_unset = True  # Method 3: Exclude unset fields in updates

# ROS2 Bridge schemas
class BridgeBase(BaseModel):
    name: str = Field(..., pattern=r"^[a-zA-Z0-9_-]{3,50}$")
    host_name: str
    description: Optional[str] = None

class BridgeCreate(BridgeBase):
    pass

class Bridge(BridgeBase):
    id: str
    status: str = Field(..., pattern=r"^(active|inactive)$")
    ip: str
    zeromq: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class NodeInfo(BaseModel):
    name: str
    namespace: str
    status: str
    pid: int
    parameters: Dict[str, Any]

class ServiceInfo(BaseModel):
    name: str
    type: str
    nodes: List[str]
    status: str

class TopicInfo(BaseModel):
    name: str
    type: str
    publishers: List[str]
    subscribers: List[str]
    message_count: int
    frequency: float

class ActionInfo(BaseModel):
    name: str
    type: str
    clients: List[str]
    servers: List[str]
    status: str
    goal_count: int
    result_count: int
    feedback_count: int

class PublisherInfo(BaseModel):
    id: str
    node_name: str
    topics: List[TopicInfo]
    message_count: int
    publish_rate: float
    status: str

class SubscriberInfo(BaseModel):
    id: str
    node_name: str
    topics: List[TopicInfo]
    message_count: int
    receive_rate: float
    status: str

class MessageTypeInfo(BaseModel):
    name: str
    package: str
    definition: Dict[str, Any]

class SystemStatus(BaseModel):
    ros_version: str
    active_nodes: int
    active_topics: int
    active_services: int
    network: Dict[str, Any]
    resources: Dict[str, Any]

class BridgeConnectionBase(BaseModel):
    from_bridge: str
    to_bridge: str
    type: str = Field(..., pattern=r"^(topic|service|action)$")
    types: str
    name: str
    from_zeromq: str
    to_zeromq: str

class BridgeConnectionCreate(BridgeConnectionBase):
    pass

class ConnectionData(BaseModel):
    name: str
    type: str = Field(..., pattern=r"^(topic|service|action)$")
    types: str

class BridgeConnectionBase2(BaseModel):
    from_bridge: str
    to_bridge: str
    datas: List[ConnectionData]
    from_zeromq: str
    to_zeromq: str

class BridgeConnectionCreate2(BridgeConnectionBase2):
    pass

class BridgeConnection(BridgeConnectionBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class BridgeConnectionDelete(BaseModel):
    connection_ids: List[str]


class BridgeConnectionUpdate(BaseModel):
    qos_profile: Optional[str] = Field(None, pattern=r"^(reliable|best_effort)$")
    direction: Optional[str] = Field(None, pattern=r"^(bidirectional|source_to_target|target_to_source)$")
    filters: Optional[Dict[str, Any]] = None
    transform: Optional[Dict[str, Any]] = None
    status: Optional[str] = Field(None, pattern=r"^(active|inactive)$")

class BridgeSearchParams(BaseModel):
    name: Optional[str] = None
    host_name: Optional[str] = None
    status: Optional[str] = Field(None, pattern=r"^(active|inactive)$")

class ConnectionSearchParams(BaseModel):
    connection_type: Optional[str] = Field(None, pattern=r"^(topic|service|action)$")
    source_bridge_id: Optional[str] = None
    target_bridge_id: Optional[str] = None
    status: Optional[str] = Field(None, pattern=r"^(active|inactive)$")

# FaaS schemas
class ResourceRequirements(BaseModel):
    """리소스 요구사항 모델"""
    requests: Optional[Dict[str, str]] = None  # 요청 리소스 (CPU, 메모리 등)
    limits: Optional[Dict[str, str]] = None    # 제한 리소스 (CPU, 메모리 등)

class EnvironmentBase(BaseModel):
    """환경 기본 모델"""
    name: str = Field(..., pattern=r"^[a-zA-Z0-9_-]{3,50}$")  # 환경 이름
    image: str                                                # 컨테이너 이미지
    builder_image: Optional[str] = None                       # 빌더 이미지
    poolsize: int = Field(..., ge=1)                         # 풀 크기
    resources: Optional[ResourceRequirements] = None          # 리소스 요구사항
    runtime_version: Optional[str] = None                     # 런타임 버전
    keep_archive: bool = False                               # 아카이브 보관 여부

class EnvironmentCreate(EnvironmentBase):
    """환경 생성 모델"""
    pass

class Environment(EnvironmentBase):
    """환경 모델"""
    id: str                                                  # 환경 ID
    status: str = Field(..., pattern=r"^(active|inactive|maintenance)$")  # 상태
    created_at: datetime                                     # 생성 시간
    updated_at: Optional[datetime] = None                    # 수정 시간

    class Config:
        from_attributes = True

class FunctionBase(BaseModel):
    """함수 기본 모델"""
    name: str = Field(..., pattern=r"^[a-zA-Z0-9_-]{3,50}$")  # 함수 이름
    environment: str                                          # 실행 환경
    package: str                                             # 패키지
    entrypoint: str                                          # 진입점
    secrets: Optional[List[str]] = None                      # 시크릿 목록
    configmaps: Optional[List[str]] = None                   # 설정 맵 목록
    resources: Optional[ResourceRequirements] = None          # 리소스 요구사항
    invoke_strategy: Optional[Dict[str, Any]] = None         # 호출 전략

class FunctionCreate(FunctionBase):
    """함수 생성 모델"""
    pass

class Function(FunctionBase):
    """함수 모델"""
    id: str                                                  # 함수 ID
    status: str = Field(..., pattern=r"^(active|inactive|maintenance)$")  # 상태
    created_at: datetime                                     # 생성 시간
    updated_at: Optional[datetime] = None                    # 수정 시간

    class Config:
        from_attributes = True

class PackageBase(BaseModel):
    """패키지 기본 모델"""
    name: str = Field(..., pattern=r"^[a-zA-Z0-9_-]{3,50}$")  # 패키지 이름
    environment: str                                          # 실행 환경
    source: Optional[str] = None                             # 소스 코드
    build_command: Optional[str] = None                      # 빌드 명령어

class PackageCreate(PackageBase):
    """패키지 생성 모델"""
    pass

class Package(PackageBase):
    """패키지 모델"""
    id: str                                                  # 패키지 ID
    status: str = Field(..., pattern=r"^(active|inactive|maintenance)$")  # 상태
    created_at: datetime                                     # 생성 시간
    updated_at: Optional[datetime] = None                    # 수정 시간

    class Config:
        from_attributes = True

class TriggerBase(BaseModel):
    """트리거 기본 모델"""
    name: str = Field(..., pattern=r"^[a-zA-Z0-9_-]{3,50}$")  # 트리거 이름
    type: str = Field(..., pattern=r"^(http|messagequeue|time|kafka)$")  # 트리거 타입
    function: str                                            # 연결된 함수
    config: Dict[str, Any]                                   # 트리거 설정

class TriggerCreate(TriggerBase):
    """트리거 생성 모델"""
    pass

class Trigger(TriggerBase):
    """트리거 모델"""
    id: str                                                  # 트리거 ID
    status: str = Field(..., pattern=r"^(active|inactive|maintenance)$")  # 상태
    created_at: datetime                                     # 생성 시간
    updated_at: Optional[datetime] = None                    # 수정 시간

    class Config:
        from_attributes = True

class FunctionInvoke(BaseModel):
    """함수 호출 모델"""
    body: Optional[str] = None                               # 요청 본문
    headers: Optional[Dict[str, str]] = None                 # HTTP 헤더
    query: Optional[Dict[str, str]] = None                   # 쿼리 파라미터

class EnvironmentSearchParams(BaseModel):
    """환경 검색 파라미터"""
    name: Optional[str] = None                               # 환경 이름
    status: Optional[str] = Field(None, pattern=r"^(active|inactive|maintenance)$")  # 상태

class FunctionSearchParams(BaseModel):
    """함수 검색 파라미터"""
    name: Optional[str] = None                               # 함수 이름
    environment: Optional[str] = None                        # 실행 환경
    status: Optional[str] = Field(None, pattern=r"^(active|inactive|maintenance)$")  # 상태

class PackageSearchParams(BaseModel):
    """패키지 검색 파라미터"""
    name: Optional[str] = None                               # 패키지 이름
    environment: Optional[str] = None                        # 실행 환경
    status: Optional[str] = Field(None, pattern=r"^(active|inactive|maintenance)$")  # 상태

class TriggerSearchParams(BaseModel):
    """트리거 검색 파라미터"""
    name: Optional[str] = None                               # 트리거 이름
    type: Optional[str] = Field(None, pattern=r"^(http|messagequeue|time|kafka)$")  # 트리거 타입
    function: Optional[str] = None                           # 연결된 함수
    status: Optional[str] = Field(None, pattern=r"^(active|inactive|maintenance)$")  # 상태