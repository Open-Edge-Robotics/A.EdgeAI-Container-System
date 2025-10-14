from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from datetime import datetime
import uuid

from .. import schemas
from ..database import MongoDB
from .users import get_current_active_user, get_current_admin_user

router = APIRouter(
    prefix="/platform/services",
    tags=["platform-services"]
)

@router.get("/", response_model=schemas.SuccessResponse)
async def list_services(
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(get_current_active_user)
):
    services = await MongoDB.get_all('services', {}, skip, limit)
    return schemas.SuccessResponse(
        data={"services": services}
    )

@router.get("/search", response_model=schemas.SuccessResponse)
async def search_services(
    params: schemas.ServiceSearchParams = Depends(),
    current_user: dict = Depends(get_current_active_user)
):
    query = {}
    if params.name:
        query['name'] = {'$regex': params.name, '$options': 'i'}
    if params.ip:
        query['ip'] = params.ip
    if params.port:
        query['port'] = params.port
    if params.status:
        query['status'] = params.status
    
    services = await MongoDB.get_all('services', query)
    return schemas.SuccessResponse(
        data={"services": services}
    )

@router.get("/{name}", response_model=schemas.SuccessResponse)
async def get_service(
    name: str,
    current_user: dict = Depends(get_current_active_user)
):
    service = await MongoDB.get('services', {'name': name})
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )
    return schemas.SuccessResponse(data=service)

@router.post("/", response_model=schemas.SuccessResponse)
async def create_service(
    service: schemas.PlatformServiceCreate,
    current_user: dict = Depends(get_current_admin_user)
):
    # Check if service name already exists
    existing_service = await MongoDB.get('services', {'name': service.name})
    if existing_service:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Service name already exists"
        )
    
    service_id = str(uuid.uuid4())
    service_data = {
        "id": service_id,
        **service.dict(),
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": None
    }
    
    # Add metadata
    if not service_data["metadata"]:
        service_data["metadata"] = {}
    service_data["metadata"]["created_by"] = current_user["username"]
    service_data["metadata"]["created_at"] = service_data["created_at"]
    
    await MongoDB.set('services', service_data)
    
    return schemas.SuccessResponse(
        data=service_data,
        message="Service created successfully"
    )

@router.put("/{name}", response_model=schemas.SuccessResponse)
async def update_service(
    name: str,
    service_update: schemas.PlatformServiceUpdate,
    current_user: dict = Depends(get_current_admin_user)
):
    service = await MongoDB.get('services', {'name': name})
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )
    
    # Update service fields
    for key, value in service_update.dict(exclude_unset=True).items():
        service[key] = value
    
    service["updated_at"] = datetime.utcnow().isoformat()
    
    # Update metadata
    if not service["metadata"]:
        service["metadata"] = {}
    service["metadata"]["updated_by"] = current_user["username"]
    service["metadata"]["updated_at"] = service["updated_at"]
    
    await MongoDB.update('services', {'name': name}, service)
    
    return schemas.SuccessResponse(
        data=service,
        message="Service updated successfully"
    )

@router.patch("/{name}", response_model=schemas.SuccessResponse)
async def partial_update_service(
    name: str,
    service_update: schemas.PlatformServiceUpdate,
    current_user: dict = Depends(get_current_admin_user)
):
    return await update_service(name, service_update, current_user)

@router.delete("/{name}", response_model=schemas.SuccessResponse)
async def delete_service(
    name: str,
    current_user: dict = Depends(get_current_admin_user)
):
    service = await MongoDB.get('services', {'name': name})
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )
    
    await MongoDB.delete_all('services', {'name': name})
    
    return schemas.SuccessResponse(
        data={"name": name},
        message="Service deleted successfully"
    ) 