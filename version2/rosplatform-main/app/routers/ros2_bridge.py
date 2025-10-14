from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import datetime
import uuid
from ..kafkaservice import get_kafka_api

from ..schemas import (
    Bridge, BridgeCreate, BridgeSearchParams,
    NodeInfo, ServiceInfo, TopicInfo, ActionInfo,
    PublisherInfo, SubscriberInfo, MessageTypeInfo,
    SystemStatus, BridgeConnection, BridgeConnectionCreate,
    BridgeConnectionUpdate, ConnectionSearchParams,
    SuccessResponse, ErrorResponse, BridgeConnectionCreate2, BridgeConnectionDelete
)
from ..database import MongoDB
from ..auth import get_current_active_user
from ..kafkaservice import get_ros_info

router = APIRouter(
    prefix="/bridges",
    tags=["ros2-bridge"],
    dependencies=[Depends(get_current_active_user)]
)

# Bridge Management
@router.get("", response_model=SuccessResponse)
async def list_bridges(
    search_params: BridgeSearchParams = Depends(),
    skip: int = 0,
    limit: int = 100
):
    query = {}
    if search_params.name:
        query['name'] = {'$regex': search_params.name, '$options': 'i'}
    if search_params.status:
        query['status'] = search_params.status
    
    bridges = await MongoDB.get_all('bridges', query, skip, limit)
    return SuccessResponse(
        data={"bridges": bridges},
        message="Bridges retrieved successfully"
    )


@router.get("/ros_info")
async def _get_ros_info(
    current_user: dict = Depends(get_current_active_user)
):
    return get_ros_info()



# Bridge Connection Management
@router.get("/connections")
async def list_connections(
    current_user: dict = Depends(get_current_active_user)
):
    
    connections = await MongoDB.get_all('connections', {})

    connections_list = []

    for connection in connections:
        connection.pop('_id')
        connections_list.append(connection)

    return connections_list

@router.post("/connections", response_model=SuccessResponse)
async def create_connection(
    connection: BridgeConnectionCreate2,
    current_user: dict = Depends(get_current_active_user)
):

    connection_data = connection.dict()
    new_connections = []
    
    for data in connection_data['datas']:
        r = {
            'from_bridge': connection_data['from_bridge'],
            'to_bridge': connection_data['to_bridge'],
            'type': data['type'],
            'types': data['types'],
            'name': data['name'],
            'from_zeromq': connection_data['from_zeromq'],
            'to_zeromq': connection_data['to_zeromq']
        }

        connection_exist = await MongoDB.get('connections', r)
        if connection_exist:
            continue

        new_connection = BridgeConnection(
            id=str(uuid.uuid4()),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            **r
        )
        await MongoDB.set('connections', new_connection.dict())

        new_connections.append(new_connection)


        kafka_api = get_kafka_api()

        for new_connection in new_connections:
            kafka_api.send('connect_bridge', {
                'no': new_connection.id, 
                'from_bridge': new_connection.from_bridge, 
                'to_bridge': new_connection.to_bridge, 
                'type': new_connection.type, 
                'name': new_connection.name, 
                'types': new_connection.types, 
                'from_zeromq': new_connection.from_zeromq, 
                'to_zeromq': new_connection.to_zeromq})

    return SuccessResponse(
        data={"connection": new_connections},
        message="Connection created successfully"
    )

@router.delete("/connections", response_model=SuccessResponse)
async def delete_all_connection(
    connection_ids: BridgeConnectionDelete,
    current_user: dict = Depends(get_current_active_user)):


    delete_connections = await MongoDB.get_all('connections', {'id': {'$in': connection_ids.connection_ids}})


    await MongoDB.delete_all('connections', {'id': {'$in': connection_ids.connection_ids}})

    for delete_connection in delete_connections:
        kafka_api = get_kafka_api()
        kafka_api.send('disconnect_bridge', {'no': delete_connection['id'], 'from_bridge': delete_connection['from_bridge'], 'to_bridge': delete_connection['to_bridge'], 'type': delete_connection['type'], 'name': delete_connection['name'], 'types': delete_connection['types'], 'from_zeromq': delete_connection['from_zeromq'], 'to_zeromq': delete_connection['to_zeromq']})

    
    return SuccessResponse(
        message="Connection deleted successfully"
    )

@router.get("/connections/{connection_id}", response_model=SuccessResponse)
async def get_connection(connection_id: str, current_user: dict = Depends(get_current_active_user)):
    connection = await MongoDB.get('connections', {'id': connection_id})
    if not connection:
        raise HTTPException(status_code=404, detail="Connection not found")
    return SuccessResponse(
        data={"connection": connection},
        message="Connection retrieved successfully"
    )

@router.patch("/connections/{connection_id}", response_model=SuccessResponse)
async def update_connection(
    connection_id: str,
    connection_update: BridgeConnectionUpdate,
    current_user: dict = Depends(get_current_active_user)
):
    connection = await MongoDB.get('connections', {'id': connection_id})
    if not connection:
        raise HTTPException(status_code=404, detail="Connection not found")
    
    # Update connection fields
    for key, value in connection_update.dict(exclude_unset=True).items():
        connection[key] = value
    
    connection["updated_at"] = datetime.utcnow().isoformat()
    
    await MongoDB.update('connections', {'id': connection_id}, connection)
    
    return SuccessResponse(
        data={"connection": connection},
        message="Connection updated successfully"
    )

@router.delete("/connections/{connection_id}", response_model=SuccessResponse)
async def delete_connection(connection_id: str, current_user: dict = Depends(get_current_active_user)):
    connection = await MongoDB.get('connections', {'id': connection_id})
    if not connection:
        raise HTTPException(status_code=404, detail="Connection not found")
    
    await MongoDB.delete_all('connections', {'id': connection_id})
    
    return SuccessResponse(
        message="Connection deleted successfully"
    )

@router.get("/{bridge_id}", response_model=SuccessResponse)
async def get_bridge(bridge_id: str):
    bridge = await MongoDB.get('bridges', {'id': bridge_id})
    if not bridge:
        raise HTTPException(status_code=404, detail="Bridge not found")
    return SuccessResponse(
        data={"bridge": bridge},
        message="Bridge retrieved successfully"
    )

@router.get("/{bridge_id}/status", response_model=SuccessResponse)
async def get_bridge_status(bridge_id: str):
    bridge = await MongoDB.get('bridges', {'id': bridge_id})
    if not bridge:
        raise HTTPException(status_code=404, detail="Bridge not found")
    return SuccessResponse(
        data={"status": bridge.get('status')},
        message="Bridge status retrieved successfully"
    )

# Node Management
@router.get("/{bridge_id}/ros2/nodes", response_model=SuccessResponse)
async def list_nodes(bridge_id: str):
    nodes = await MongoDB.get_all('nodes', {'bridge_id': bridge_id})
    return SuccessResponse(
        data={"nodes": nodes},
        message="Nodes retrieved successfully"
    )

@router.get("/{bridge_id}/ros2/nodes/{node_name}", response_model=SuccessResponse)
async def get_node(bridge_id: str, node_name: str):
    node = await MongoDB.get('nodes', {'bridge_id': bridge_id, 'name': node_name})
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    return SuccessResponse(
        data={"node": node},
        message="Node retrieved successfully"
    )

# Service Management
@router.get("/{bridge_id}/ros2/services", response_model=SuccessResponse)
async def list_services(bridge_id: str):
    services = await MongoDB.get_all('services', {'bridge_id': bridge_id})
    return SuccessResponse(
        data={"services": services},
        message="Services retrieved successfully"
    )

@router.get("/{bridge_id}/ros2/services/{service_name}", response_model=SuccessResponse)
async def get_service(bridge_id: str, service_name: str):
    service = await MongoDB.get('services', {'bridge_id': bridge_id, 'name': service_name})
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return SuccessResponse(
        data={"service": service},
        message="Service retrieved successfully"
    )

# Topic Management
@router.get("/{bridge_id}/ros2/topics", response_model=SuccessResponse)
async def list_topics(bridge_id: str):
    topics = await MongoDB.get_all('topics', {'bridge_id': bridge_id})
    return SuccessResponse(
        data={"topics": topics},
        message="Topics retrieved successfully"
    )

@router.get("/{bridge_id}/ros2/topics/{topic_name}", response_model=SuccessResponse)
async def get_topic(bridge_id: str, topic_name: str):
    topic = await MongoDB.get('topics', {'bridge_id': bridge_id, 'name': topic_name})
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    return SuccessResponse(
        data={"topic": topic},
        message="Topic retrieved successfully"
    )

# Action Management
@router.get("/{bridge_id}/ros2/actions", response_model=SuccessResponse)
async def list_actions(bridge_id: str):
    actions = await MongoDB.get_all('actions', {'bridge_id': bridge_id})
    return SuccessResponse(
        data={"actions": actions},
        message="Actions retrieved successfully"
    )

@router.get("/{bridge_id}/ros2/actions/{action_name}", response_model=SuccessResponse)
async def get_action(bridge_id: str, action_name: str):
    action = await MongoDB.get('actions', {'bridge_id': bridge_id, 'name': action_name})
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")
    return SuccessResponse(
        data={"action": action},
        message="Action retrieved successfully"
    )

# Publisher Management
@router.get("/{bridge_id}/ros2/publishers", response_model=SuccessResponse)
async def list_publishers(bridge_id: str):
    publishers = await MongoDB.get_all('publishers', {'bridge_id': bridge_id})
    return SuccessResponse(
        data={"publishers": publishers},
        message="Publishers retrieved successfully"
    )

@router.get("/{bridge_id}/ros2/publishers/{publisher_id}", response_model=SuccessResponse)
async def get_publisher(bridge_id: str, publisher_id: str):
    publisher = await MongoDB.get('publishers', {'bridge_id': bridge_id, 'id': publisher_id})
    if not publisher:
        raise HTTPException(status_code=404, detail="Publisher not found")
    return SuccessResponse(
        data={"publisher": publisher},
        message="Publisher retrieved successfully"
    )

# Subscriber Management
@router.get("/{bridge_id}/ros2/subscribers", response_model=SuccessResponse)
async def list_subscribers(bridge_id: str):
    subscribers = await MongoDB.get_all('subscribers', {'bridge_id': bridge_id})
    return SuccessResponse(
        data={"subscribers": subscribers},
        message="Subscribers retrieved successfully"
    )

@router.get("/{bridge_id}/ros2/subscribers/{subscriber_id}", response_model=SuccessResponse)
async def get_subscriber(bridge_id: str, subscriber_id: str):
    subscriber = await MongoDB.get('subscribers', {'bridge_id': bridge_id, 'id': subscriber_id})
    if not subscriber:
        raise HTTPException(status_code=404, detail="Subscriber not found")
    return SuccessResponse(
        data={"subscriber": subscriber},
        message="Subscriber retrieved successfully"
    )

# System Status
@router.get("/{bridge_id}/ros2/status", response_model=SuccessResponse)
async def get_system_status(bridge_id: str):
    bridge = await MongoDB.get('bridges', {'id': bridge_id})
    if not bridge:
        raise HTTPException(status_code=404, detail="Bridge not found")
    return SuccessResponse(
        data={"system_status": bridge.get('system_status', {})},
        message="System status retrieved successfully"
    )
