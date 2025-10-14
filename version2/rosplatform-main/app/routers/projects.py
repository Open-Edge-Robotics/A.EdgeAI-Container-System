from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from datetime import datetime
import uuid

from .. import schemas
from ..database import MongoDB
from .users import get_current_active_user

router = APIRouter(
    prefix="/projects",
    tags=["projects"]
)

@router.post("/", response_model=schemas.Project)
async def create_project(
    project: schemas.ProjectCreate,
    current_user: dict = Depends(get_current_active_user)
):
    # Check if workspace exists
    workspace = await MongoDB.get('workspaces', {'name': project.workspace_name})
    if workspace is None:
        raise HTTPException(status_code=404, detail="Workspace not found")


    project_exists = await MongoDB.get('projects', {'name': project.name, 'username': current_user['username'], 'workspace_name': project.workspace_name})
    if project_exists is not None:
        raise HTTPException(status_code=400, detail="Project already exists")

    project_data = {
        "name": project.name,
        "username": current_user['username'],
        "workspace_name": project.workspace_name,
        "workspace_id": workspace['id'],
        **project.dict(),
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }
    
    await MongoDB.set('projects', project_data)
    project_data.pop('_id')
    return project_data

@router.get("/", response_model=List[schemas.Project])
async def list_projects(
    skip: int = 0,
    limit: int = 100,
    workspace_name: str = None,
    user_name: str = None,
    current_user: dict = Depends(get_current_active_user)
):
    query = {}

    if workspace_name:
        query['workspace_name'] = workspace_name

    if user_name:
        query['username'] = user_name

    
    projects = await MongoDB.get_all('projects', query, skip, limit)

    _projects = []

    for project in projects:
        project.pop('_id')
        _project = schemas.Project(**project)
        _projects.append(_project)

    return _projects

@router.get("/{project_name}", response_model=schemas.Project)
async def get_project(
    project_name: str,
    current_user: dict = Depends(get_current_active_user)
):
    project = await MongoDB.get('projects', {'name': project_name})
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.put("/{project_name}", response_model=schemas.Project)
async def update_project(
    project_name: str,
    workspace_name: str,
    project_update: schemas.ProjectUpdate,
    current_user: dict = Depends(get_current_active_user)
):
    project = await MongoDB.get('projects', {'name': project_name, 'username': current_user['username'], 'workspace_name': workspace_name})
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check if new workspace exists
    if workspace_name != project["workspace_name"]:
        workspace = await MongoDB.get('workspaces', {'name': workspace_name})
        if workspace is None:
            raise HTTPException(status_code=404, detail="Workspace not found")
    
    # Update project fields
    for key, value in project_update.dict().items():
        project[key] = value
    
    project["updated_at"] = datetime.utcnow().isoformat()
    
    # Update project data
    await MongoDB.update('projects', {'name': project_name, 'username': current_user['username'], 'workspace_name': workspace_name}, project)
    project.pop('_id')
    return project

@router.delete("/{project_name}")
async def delete_project(
    project_name: str,
    workspace_name: str,
    current_user: dict = Depends(get_current_active_user)
):
    project = await MongoDB.get('projects', {'name': project_name, 'username': current_user['username'], 'workspace_name': workspace_name})
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Delete project data
    await MongoDB.delete_all('projects', {'name': project_name, 'username': current_user['username'], 'workspace_name': workspace_name})
    
    return {"message": "Project deleted successfully"} 