from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from typing import Optional, Any, List, Dict
from datetime import datetime

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "robotplatform")
MONGODB_USER = os.getenv("MONGODB_USER", "")
MONGODB_PASSWORD = os.getenv("MONGODB_PASSWORD", "")

client = None
db = None

async def init_db():
    global client, db
    if MONGODB_USER and MONGODB_PASSWORD:
        client = AsyncIOMotorClient(MONGODB_URL, username=MONGODB_USER, password=MONGODB_PASSWORD)
    else:
        client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]


    # Ensure indexes
    
    #await db.users.create_index("username", unique=True)
    #await db.users.create_index("email", unique=True)

class MongoDB:
    @staticmethod
    async def get(collection: str, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return await db[collection].find_one(query)

    @staticmethod
    async def set(collection: str, data: Dict[str, Any]) -> None:
        await db[collection].insert_one(data)

    @staticmethod
    async def update(collection: str, query: Dict[str, Any], data: Dict[str, Any]) -> None:
        await db[collection].update_one(query, {"$set": data})

    @staticmethod
    async def delete(collection: str, query: Dict[str, Any]) -> None:
        await db[collection].delete_one(query)

    @staticmethod
    async def delete_all(collection: str, query: Dict[str, Any]) -> None:
        await db[collection].delete_many(query)

    @staticmethod
    async def exists(collection: str, query: Dict[str, Any]) -> bool:
        return await db[collection].count_documents(query) > 0

    @staticmethod
    async def get_all(collection: str, query: Dict[str, Any] = None, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        cursor = db[collection].find(query or {})
        #cursor.skip(skip).limit(limit)
        return await cursor.to_list(length=limit)

    # Bridge Management
    @staticmethod
    async def get_bridges(search_params: Dict[str, Any], skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """브릿지 목록 조회"""
        query = {}
        if search_params:
            if "status" in search_params:
                query["status"] = search_params["status"]
            if "name" in search_params:
                query["name"] = {"$regex": search_params["name"], "$options": "i"}
        return await MongoDB.get_all("bridges", query, skip, limit)

    @staticmethod
    async def get_bridge(bridge_id: str) -> Optional[Dict[str, Any]]:
        """특정 브릿지 조회"""
        return await MongoDB.get("bridges", {"id": bridge_id})

    @staticmethod
    async def get_bridge_status(bridge_id: str) -> Optional[Dict[str, Any]]:
        """브릿지 상태 조회"""
        return await MongoDB.get("bridge_status", {"bridge_id": bridge_id})

    # Publisher Management
    @staticmethod
    async def get_publishers(bridge_id: str) -> List[Dict[str, Any]]:
        """퍼블리셔 목록 조회"""
        return await MongoDB.get_all("publishers", {"bridge_id": bridge_id})

    @staticmethod
    async def get_publisher(bridge_id: str, publisher_id: str) -> Optional[Dict[str, Any]]:
        """특정 퍼블리셔 조회"""
        return await MongoDB.get("publishers", {"bridge_id": bridge_id, "id": publisher_id})

    # Subscriber Management
    @staticmethod
    async def get_subscribers(bridge_id: str) -> List[Dict[str, Any]]:
        """서브스크라이버 목록 조회"""
        return await MongoDB.get_all("subscribers", {"bridge_id": bridge_id})

    @staticmethod
    async def get_subscriber(bridge_id: str, subscriber_id: str) -> Optional[Dict[str, Any]]:
        """특정 서브스크라이버 조회"""
        return await MongoDB.get("subscribers", {"bridge_id": bridge_id, "id": subscriber_id})

    # System Status
    @staticmethod
    async def get_system_status(bridge_id: str) -> Optional[Dict[str, Any]]:
        """시스템 상태 조회"""
        return await MongoDB.get("system_status", {"bridge_id": bridge_id})

    # Bridge Connection Management
    @staticmethod
    async def get_connections(
        bridge_id: str,
        search_params: Dict[str, Any],
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """연결 목록 조회"""
        query = {"bridge_id": bridge_id}
        if search_params:
            if "status" in search_params:
                query["status"] = search_params["status"]
            if "connection_type" in search_params:
                query["connection_type"] = search_params["connection_type"]
        return await MongoDB.get_all("connections", query, skip, limit)

    @staticmethod
    async def get_connection(bridge_id: str, connection_id: str) -> Optional[Dict[str, Any]]:
        """특정 연결 조회"""
        return await MongoDB.get("connections", {"bridge_id": bridge_id, "id": connection_id})

    @staticmethod
    async def create_connection(connection: Dict[str, Any]) -> None:
        """연결 생성"""
        await MongoDB.set("connections", connection)

    @staticmethod
    async def update_connection(
        bridge_id: str,
        connection_id: str,
        connection_update: Dict[str, Any]
    ) -> Dict[str, Any]:
        """연결 수정"""
        await MongoDB.update(
            "connections",
            {"bridge_id": bridge_id, "id": connection_id},
            connection_update
        )
        return await MongoDB.get_connection(bridge_id, connection_id)

    @staticmethod
    async def delete_connection(bridge_id: str, connection_id: str) -> None:
        """연결 삭제"""
        await MongoDB.delete("connections", {"bridge_id": bridge_id, "id": connection_id})

# Collection names
USERS_COLLECTION = "users"
WORKSPACES_COLLECTION = "workspaces"
PROJECTS_COLLECTION = "projects"
CLUSTERS_COLLECTION = "clusters"
SERVICES_COLLECTION = "services"
BRIDGES_COLLECTION = "bridges"
PUBLISHERS_COLLECTION = "publishers"
SUBSCRIBERS_COLLECTION = "subscribers"
CONNECTIONS_COLLECTION = "connections"

# Key patterns
USER_KEY = "user:{}"
USER_ID_KEY = "id:{}"
USER_EMAIL_KEY = "email:{}"
USER_USERNAME_KEY = "username:{}"
USER_LIST_KEY = "users"
WORKSPACE_KEY = "workspace:{}"
WORKSPACE_LIST_KEY = "workspaces"
PROJECT_KEY = "project:{}"
PROJECT_LIST_KEY = "projects"
CLUSTER_KEY = "cluster:{}"
CLUSTER_LIST_KEY = "clusters"
SERVICE_KEY = "service:{}"
SERVICE_LIST_KEY = "services"

# FaaS Key patterns
ENVIRONMENT_KEY = "faas:environment:{}"
ENVIRONMENT_LIST_KEY = "faas:environments"
FUNCTION_KEY = "faas:function:{}"
FUNCTION_LIST_KEY = "faas:functions"
PACKAGE_KEY = "faas:package:{}"
PACKAGE_LIST_KEY = "faas:packages"
TRIGGER_KEY = "faas:trigger:{}"
TRIGGER_LIST_KEY = "faas:triggers"

class MongoDB2:
    # Environment Management
    @staticmethod
    async def get_environments(search_params: Dict[str, Any], skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """환경 목록 조회"""
        # MongoDB에서 환경 목록 조회 로직 구현
        pass

    @staticmethod
    async def get_environment(env_name: str) -> Optional[Dict[str, Any]]:
        """특정 환경 조회"""
        # MongoDB에서 특정 환경 조회 로직 구현
        pass

    @staticmethod
    async def create_environment(environment: Dict[str, Any]) -> None:
        """환경 생성"""
        # MongoDB에 환경 생성 로직 구현
        pass

    @staticmethod
    async def get_environment_status(env_name: str) -> Optional[Dict[str, Any]]:
        """환경 상태 조회"""
        # MongoDB에서 환경 상태 조회 로직 구현
        pass

    # Function Management
    @staticmethod
    async def get_functions(search_params: Dict[str, Any], skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """함수 목록 조회"""
        # MongoDB에서 함수 목록 조회 로직 구현
        pass

    @staticmethod
    async def get_function(function_name: str) -> Optional[Dict[str, Any]]:
        """특정 함수 조회"""
        # MongoDB에서 특정 함수 조회 로직 구현
        pass

    @staticmethod
    async def create_function(function: Dict[str, Any]) -> None:
        """함수 생성"""
        # MongoDB에 함수 생성 로직 구현
        pass

    @staticmethod
    async def invoke_function(function_name: str, invoke_data: Dict[str, Any]) -> Dict[str, Any]:
        """함수 실행"""
        # MongoDB에서 함수 실행 로직 구현
        pass

    # Package Management
    @staticmethod
    async def get_packages(search_params: Dict[str, Any], skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """패키지 목록 조회"""
        # MongoDB에서 패키지 목록 조회 로직 구현
        pass

    @staticmethod
    async def get_package(package_name: str) -> Optional[Dict[str, Any]]:
        """특정 패키지 조회"""
        # MongoDB에서 특정 패키지 조회 로직 구현
        pass

    @staticmethod
    async def create_package(package: Dict[str, Any], file: Optional[Any] = None) -> None:
        """패키지 생성"""
        # MongoDB에 패키지 생성 로직 구현
        pass

    # Trigger Management
    @staticmethod
    async def get_triggers(search_params: Dict[str, Any], skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """트리거 목록 조회"""
        # MongoDB에서 트리거 목록 조회 로직 구현
        pass

    @staticmethod
    async def get_trigger(trigger_name: str) -> Optional[Dict[str, Any]]:
        """특정 트리거 조회"""
        # MongoDB에서 특정 트리거 조회 로직 구현
        pass

    @staticmethod
    async def create_trigger(trigger: Dict[str, Any]) -> None:
        """트리거 생성"""
        # MongoDB에 트리거 생성 로직 구현
        pass

    @staticmethod
    async def get_trigger_status(trigger_name: str) -> Optional[Dict[str, Any]]:
        """트리거 상태 조회"""
        # MongoDB에서 트리거 상태 조회 로직 구현
        pass 