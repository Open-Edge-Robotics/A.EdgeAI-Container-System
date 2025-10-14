from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from datetime import datetime
import uuid

from .. import schemas
from ..database import MongoDB
from .users import get_current_active_user

from ..kafkaservice import get_clusters_info, get_ros_info

router = APIRouter(
    prefix="/clusters",
    tags=["clusters"]
)

@router.post("/", response_model=schemas.Cluster)
async def create_cluster(
    cluster: schemas.ClusterCreate,
    current_user: dict = Depends(get_current_active_user)
):
    # Check if project exists
    project = await MongoDB.get('projects', {'id': cluster.project_id})
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    
    cluster_id = str(uuid.uuid4())
    cluster_data = {
        "id": cluster_id,
        **cluster.dict(),
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": None
    }
    
    await MongoDB.set('clusters', cluster_data)
    return cluster_data

@router.get("/", response_model=List[schemas.Cluster])
async def list_clusters(
    skip: int = 0,
    limit: int = 100,
    project_id: str = None,
    current_user: dict = Depends(get_current_active_user)
):
    query = {}
    if project_id:
        query['project_id'] = project_id
    
    clusters = await MongoDB.get_all('clusters', query, skip, limit)
    return clusters



@router.get("/info")
async def get_clusters_in(
    current_user: dict = Depends(get_current_active_user)
):
    return get_clusters_info()


@router.get("/{cluster_id}", response_model=schemas.Cluster)
async def get_cluster(
    cluster_id: str,
    current_user: dict = Depends(get_current_active_user)
):
    cluster = await MongoDB.get('clusters', {'id': cluster_id})
    if cluster is None:
        raise HTTPException(status_code=404, detail="Cluster not found")
    return cluster

@router.put("/{cluster_id}", response_model=schemas.Cluster)
async def update_cluster(
    cluster_id: str,
    cluster_update: schemas.ClusterCreate,
    current_user: dict = Depends(get_current_active_user)
):
    cluster = await MongoDB.get('clusters', {'id': cluster_id})
    if cluster is None:
        raise HTTPException(status_code=404, detail="Cluster not found")
    
    # Check if new project exists
    if cluster_update.project_id != cluster["project_id"]:
        project = await MongoDB.get('projects', {'id': cluster_update.project_id})
        if project is None:
            raise HTTPException(status_code=404, detail="Project not found")
    
    # Update cluster fields
    for key, value in cluster_update.dict().items():
        cluster[key] = value
    
    cluster["updated_at"] = datetime.utcnow().isoformat()
    
    # Update cluster data
    await MongoDB.update('clusters', {'id': cluster_id}, cluster)
    
    return cluster

@router.delete("/{cluster_id}")
async def delete_cluster(
    cluster_id: str,
    current_user: dict = Depends(get_current_active_user)
):
    cluster = await MongoDB.get('clusters', {'id': cluster_id})
    if cluster is None:
        raise HTTPException(status_code=404, detail="Cluster not found")
    
    # Delete cluster data
    await MongoDB.delete_all('clusters', {'id': cluster_id})
    
    return {"message": "Cluster deleted successfully"} 
