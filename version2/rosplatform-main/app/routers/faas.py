from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from typing import List, Optional
from datetime import datetime
import uuid

from ..schemas import (
    Environment, EnvironmentCreate, EnvironmentSearchParams,
    Function, FunctionCreate, FunctionSearchParams, FunctionInvoke,
    Package, PackageCreate, PackageSearchParams,
    Trigger, TriggerCreate, TriggerSearchParams,
    SuccessResponse, ErrorResponse
)
from ..database import MongoDB
from ..auth import get_current_active_user

# FaaS API 라우터 설정
router = APIRouter(
    prefix="/faas",  # API 경로 접두사
    tags=["faas"],   # API 문서 태그
    dependencies=[Depends(get_current_active_user)]  # 인증 의존성
)

# 환경 관리 API
@router.get("/environments", response_model=SuccessResponse)
async def list_environments(
    search_params: EnvironmentSearchParams = Depends(),  # 검색 파라미터
    skip: int = 0,                                      # 건너뛸 항목 수
    limit: int = 100                                    # 반환할 최대 항목 수
):
    """환경 목록 조회 API"""
    query = {}
    if search_params.name:
        query['name'] = {'$regex': search_params.name, '$options': 'i'}
    if search_params.status:
        query['status'] = search_params.status
    
    environments = await MongoDB.get_all('environments', query, skip, limit)
    return SuccessResponse(
        data={"environments": environments},
        message="Environments retrieved successfully"
    )

@router.post("/environments", response_model=SuccessResponse)
async def create_environment(environment: EnvironmentCreate):
    """환경 생성 API"""
    environment_id = str(uuid.uuid4())  # 고유 ID 생성
    new_environment = Environment(
        id=environment_id,
        status="active",
        created_at=datetime.utcnow(),
        **environment.dict()
    )
    await MongoDB.set('environments', new_environment.dict())
    return SuccessResponse(
        data={"environment": new_environment},
        message="Environment created successfully"
    )

@router.get("/environments/{env_name}", response_model=SuccessResponse)
async def get_environment(env_name: str):
    """특정 환경 상세 정보 조회 API"""
    environment = await MongoDB.get('environments', {'name': env_name})
    if not environment:
        raise HTTPException(status_code=404, detail="Environment not found")
    return SuccessResponse(
        data={"environment": environment},
        message="Environment retrieved successfully"
    )

@router.get("/environments/{env_name}/status", response_model=SuccessResponse)
async def get_environment_status(env_name: str):
    """환경 상태 조회 API"""
    environment = await MongoDB.get('environments', {'name': env_name})
    if not environment:
        raise HTTPException(status_code=404, detail="Environment not found")
    return SuccessResponse(
        data={"status": environment.get('status')},
        message="Environment status retrieved successfully"
    )

# 함수 관리 API
@router.get("/functions", response_model=SuccessResponse)
async def list_functions(
    search_params: FunctionSearchParams = Depends(),  # 검색 파라미터
    skip: int = 0,                                   # 건너뛸 항목 수
    limit: int = 100                                 # 반환할 최대 항목 수
):
    """함수 목록 조회 API"""
    query = {}
    if search_params.name:
        query['name'] = {'$regex': search_params.name, '$options': 'i'}
    if search_params.environment:
        query['environment'] = search_params.environment
    if search_params.status:
        query['status'] = search_params.status
    
    functions = await MongoDB.get_all('functions', query, skip, limit)
    return SuccessResponse(
        data={"functions": functions},
        message="Functions retrieved successfully"
    )

@router.post("/functions", response_model=SuccessResponse)
async def create_function(function: FunctionCreate):
    """함수 생성 API"""
    function_id = str(uuid.uuid4())  # 고유 ID 생성
    new_function = Function(
        id=function_id,
        status="active",
        created_at=datetime.utcnow(),
        **function.dict()
    )
    await MongoDB.set('functions', new_function.dict())
    return SuccessResponse(
        data={"function": new_function},
        message="Function created successfully"
    )

@router.get("/functions/{function_name}", response_model=SuccessResponse)
async def get_function(function_name: str):
    """특정 함수 상세 정보 조회 API"""
    function = await MongoDB.get('functions', {'name': function_name})
    if not function:
        raise HTTPException(status_code=404, detail="Function not found")
    return SuccessResponse(
        data={"function": function},
        message="Function retrieved successfully"
    )

@router.post("/functions/{function_name}/invoke", response_model=SuccessResponse)
async def invoke_function(function_name: str, invoke_data: FunctionInvoke):
    """함수 실행 API"""
    function = await MongoDB.get('functions', {'name': function_name})
    if not function:
        raise HTTPException(status_code=404, detail="Function not found")
    
    # Add invocation record
    invocation_id = str(uuid.uuid4())
    invocation_data = {
        'id': invocation_id,
        'function_name': function_name,
        'input': invoke_data.input,
        'created_at': datetime.utcnow().isoformat(),
        'status': 'pending'
    }
    await MongoDB.set('function_invocations', invocation_data)
    
    return SuccessResponse(
        data={"invocation": invocation_data},
        message="Function invoked successfully"
    )

# 패키지 관리 API
@router.get("/packages", response_model=SuccessResponse)
async def list_packages(
    search_params: PackageSearchParams = Depends(),  # 검색 파라미터
    skip: int = 0,                                  # 건너뛸 항목 수
    limit: int = 100                                # 반환할 최대 항목 수
):
    """패키지 목록 조회 API"""
    query = {}
    if search_params.name:
        query['name'] = {'$regex': search_params.name, '$options': 'i'}
    if search_params.version:
        query['version'] = search_params.version
    if search_params.status:
        query['status'] = search_params.status
    
    packages = await MongoDB.get_all('packages', query, skip, limit)
    return SuccessResponse(
        data={"packages": packages},
        message="Packages retrieved successfully"
    )

@router.post("/packages", response_model=SuccessResponse)
async def create_package(
    package: PackageCreate,
    file: Optional[UploadFile] = File(None)  # 업로드된 파일
):
    """패키지 생성 API"""
    package_id = str(uuid.uuid4())  # 고유 ID 생성
    new_package = Package(
        id=package_id,
        status="active",
        created_at=datetime.utcnow(),
        **package.dict()
    )
    
    if file:
        # Handle file upload logic here
        file_content = await file.read()
        new_package.file_content = file_content
    
    await MongoDB.set('packages', new_package.dict())
    return SuccessResponse(
        data={"package": new_package},
        message="Package created successfully"
    )

@router.get("/packages/{package_name}", response_model=SuccessResponse)
async def get_package(package_name: str):
    """특정 패키지 상세 정보 조회 API"""
    package = await MongoDB.get('packages', {'name': package_name})
    if not package:
        raise HTTPException(status_code=404, detail="Package not found")
    return SuccessResponse(
        data={"package": package},
        message="Package retrieved successfully"
    )

# 트리거 관리 API
@router.get("/triggers", response_model=SuccessResponse)
async def list_triggers(
    search_params: TriggerSearchParams = Depends(),  # 검색 파라미터
    skip: int = 0,                                  # 건너뛸 항목 수
    limit: int = 100                                # 반환할 최대 항목 수
):
    """트리거 목록 조회 API"""
    query = {}
    if search_params.name:
        query['name'] = {'$regex': search_params.name, '$options': 'i'}
    if search_params.function:
        query['function'] = search_params.function
    if search_params.status:
        query['status'] = search_params.status
    
    triggers = await MongoDB.get_all('triggers', query, skip, limit)
    return SuccessResponse(
        data={"triggers": triggers},
        message="Triggers retrieved successfully"
    )

@router.post("/triggers", response_model=SuccessResponse)
async def create_trigger(trigger: TriggerCreate):
    """트리거 생성 API"""
    trigger_id = str(uuid.uuid4())  # 고유 ID 생성
    new_trigger = Trigger(
        id=trigger_id,
        status="active",
        created_at=datetime.utcnow(),
        **trigger.dict()
    )
    await MongoDB.set('triggers', new_trigger.dict())
    return SuccessResponse(
        data={"trigger": new_trigger},
        message="Trigger created successfully"
    )

@router.get("/triggers/{trigger_name}", response_model=SuccessResponse)
async def get_trigger(trigger_name: str):
    """특정 트리거 상세 정보 조회 API"""
    trigger = await MongoDB.get('triggers', {'name': trigger_name})
    if not trigger:
        raise HTTPException(status_code=404, detail="Trigger not found")
    return SuccessResponse(
        data={"trigger": trigger},
        message="Trigger retrieved successfully"
    )

@router.get("/triggers/{trigger_name}/status", response_model=SuccessResponse)
async def get_trigger_status(trigger_name: str):
    """트리거 상태 조회 API"""
    trigger = await MongoDB.get('triggers', {'name': trigger_name})
    if not trigger:
        raise HTTPException(status_code=404, detail="Trigger not found")
    return SuccessResponse(
        data={"status": trigger.get('status')},
        message="Trigger status retrieved successfully"
    ) 