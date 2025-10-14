from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from datetime import datetime
import uuid
import json

from .. import schemas
from ..database import MongoDB
from .users import get_current_active_user

router = APIRouter(
    prefix="/workspaces",
    tags=["workspaces"]
)

@router.post("/", response_model=schemas.Workspace)
async def create_workspace(
    workspace: schemas.WorkspaceCreate,
    current_user: dict = Depends(get_current_active_user)
):
    # Check if workspace name already exists
    if await MongoDB.exists('workspaces', {'name': workspace.name}):
        raise HTTPException(status_code=400, detail="Workspace name already taken")

    _workspace = schemas.Workspace(
        **workspace.model_dump(),
        id=str(uuid.uuid4()),
        created_at=datetime.utcnow().isoformat(),
        updated_at=datetime.utcnow().isoformat()
    )

    workspace_data = json.loads(_workspace.model_dump_json())
    await MongoDB.set('workspaces', workspace_data)
    
    return _workspace

@router.get("/", response_model=List[schemas.Workspace])
async def list_workspaces(
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(get_current_active_user)
):

    workspaces = await MongoDB.get_all('workspaces', {})

    _workspaces = []

    for workspace in workspaces:
        workspace.pop('_id')
        _workspace = schemas.Workspace(**workspace)
        _workspaces.append(_workspace)

    return _workspaces

@router.get("/as_user/{username}", response_model=List[schemas.Workspace])
async def list_workspaces_as_user(
    username: str,
    current_user: dict = Depends(get_current_active_user)
):

    workspaces = await MongoDB.get_all('workspaces_as_user', {'username': username})

    _workspaces = []

    workspace_names = []

    for workspace in workspaces:
        workspace_names.append(workspace['workspace'])

    workspaces = await MongoDB.get_all('workspaces', {'name': {'$in': workspace_names}})

    for workspace in workspaces:
        workspace.pop('_id')
        _workspace = schemas.Workspace(**workspace)
        _workspaces.append(_workspace)

    return _workspaces

@router.get("/{workspace_name}", response_model=schemas.Workspace)
async def get_workspace(
    workspace_name: str,
    current_user: dict = Depends(get_current_active_user)
):
    workspace = await MongoDB.get('workspaces', {'name': workspace_name})
    if workspace is None:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return schemas.Workspace(**workspace)

@router.put("/{workspace_name}", response_model=schemas.Workspace)
async def update_workspace(
    workspace_name: str,
    workspace_update: schemas.WorkspaceCreate,
    current_user: dict = Depends(get_current_active_user)
):
    workspace = await MongoDB.get('workspaces', {'name': workspace_name})
    if workspace is None:
        raise HTTPException(status_code=404, detail="Workspace not found")
    
    # Check if new name conflicts with existing workspace
    if workspace_update.name != workspace['name']:
        if await MongoDB.exists('workspaces', {'name': workspace_update.name}):
            raise HTTPException(status_code=400, detail="Workspace name already taken")
    
    # Update workspace fields
    for key, value in workspace_update.model_dump().items():
        workspace[key] = value
    
    workspace["updated_at"] = datetime.utcnow().isoformat()
    
    # Update workspace data
    await MongoDB.update('workspaces', {'name': workspace_name}, workspace)
    
    return schemas.Workspace(**workspace)

@router.delete("/{workspace_id}")
async def delete_workspace(
    workspace_id: str,
    current_user: dict = Depends(get_current_active_user)
):
    workspace = await MongoDB.get('workspaces', {'id': workspace_id})
    if workspace is None:
        raise HTTPException(status_code=404, detail="Workspace not found")
    
    # Delete workspace data
    await MongoDB.delete('workspaces', {'id': workspace_id})
    
    return {"message": "Workspace deleted successfully"} 