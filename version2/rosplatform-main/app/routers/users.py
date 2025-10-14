from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from datetime import datetime
import uuid
import json

from .. import schemas, auth
from ..database import MongoDB, USER_KEY, USER_EMAIL_KEY, USER_USERNAME_KEY, USER_LIST_KEY

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

async def get_current_user(token: str = Depends(auth.oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = auth.jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        user = await MongoDB.get('users', {'username': username})
        if user is None:
            raise credentials_exception
        return user
    except auth.JWTError:
        raise credentials_exception

async def get_current_active_user(current_user: dict = Depends(get_current_user)):
    if not current_user.get("is_active", False):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def get_current_admin_user(current_user: dict = Depends(get_current_user)):
    if not current_user.get("user_type") == "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return current_user

@router.post("/", response_model=schemas.User)
async def create_user(
    user: schemas.UserCreate,
    current_user: dict = Depends(get_current_admin_user)
):
    # Check if email already exists
    if await MongoDB.exists('users', {'email': user.email}):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Check if username already exists
    if  await MongoDB.exists('users', {'username': user.username}):
        raise HTTPException(status_code=400, detail="Username already taken")

    _user = schemas.User(**user.model_dump(), 
                         id = str(uuid.uuid4()), 
                         created_at = datetime.utcnow().isoformat(), 
                         updated_at = datetime.utcnow().isoformat(), 
                         hashed_password = auth.get_password_hash(user.password),
                         is_active = True)

    '''
    for workspace in user.workspaces:
        _workspace = schemas.Workspace(
            id = str(uuid.uuid4()),
            name = workspace,
            username = user.username,
            clusters = [],
            created_at = datetime.utcnow().isoformat(),
            updated_at = datetime.utcnow().isoformat()
        )
        await MongoDB.set('workspaces', _workspace.model_dump())

    
    _workspace = schemas.Workspace(
        id = str(uuid.uuid4()),
        name = user.workspace,
        username = user.username,
        clusters = user.clusters,
        created_at = datetime.utcnow().isoformat(),
        updated_at = datetime.utcnow().isoformat()
    )
    '''

    if user.workspaces is not None:
        for workspace in user.workspaces:
            _workspace = await MongoDB.get('workspaces', {'name': workspace})
            if _workspace is None:
                raise HTTPException(status_code=404, detail="Workspace not found")

            if await MongoDB.exists('workspaces_as_user', {'username': user.username, 'workspace': workspace}):
                continue
            else:
                await MongoDB.set('workspaces_as_user', {'username': user.username, 'workspace': workspace})

    user_data = json.loads(_user.model_dump_json())

    await MongoDB.set('users', user_data)

    #await MongoDB.delete('workspaces', {'username': user.username})
    #await MongoDB.set('workspaces', _workspace.model_dump())

    return _user

@router.put("/", response_model=schemas.UserUpdate)
async def update_user(
    user_update: schemas.UserUpdate,
    current_user: dict = Depends(get_current_admin_user)
):
    _user = await MongoDB.get('users', {'username': user_update.username})
    if _user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    for key, value in user_update.dict(exclude_unset=True).items():
        if key == "password":
            continue
        _user[key] = value
    
    _user["updated_at"] = datetime.utcnow().isoformat()

    if user_update.password is not None and user_update.password != "":
        _user["hashed_password"] = auth.get_password_hash(user_update.password)

    if user_update.workspaces is not None:
        for workspace in user_update.workspaces:
            _workspace = await MongoDB.get('workspaces', {'name': workspace})
            if _workspace is None:
                raise HTTPException(status_code=404, detail="Workspace not found")

            if await MongoDB.exists('workspaces_as_user', {'username': user_update.username, 'workspace': workspace}):
                continue
            else:
                await MongoDB.set('workspaces_as_user', {'username': user_update.username, 'workspace': workspace})

    await MongoDB.update('users', {'username': user_update.username}, _user)

    return _user

@router.get("/", response_model=List[schemas.UserWithWorkspace])
async def list_users(
    current_user: dict = Depends(get_current_admin_user)
):
    #await MongoDB.delete_all('users', {})
    user_list = await MongoDB.get_all('users', {}) or []
    users = []
    for _user in user_list:
        _workspaces = await MongoDB.get_all('workspaces_as_user', {'username': _user['username']})

        workspaces = []

        if _workspaces is not None:

            for _workspace in _workspaces:
                _workspace.pop('_id')
                workspaces.append(_workspace['workspace'])


        workspaces_ = await MongoDB.get_all('workspaces', {'name': {'$in': workspaces}})

        clusters = []

        for workspace in workspaces_:
            clusters.extend(workspace['clusters'])

        clusters = [cluster for cluster in clusters if clusters.count(cluster) == 1]

        clusters = list(set(clusters))

        _user.pop('_id')
        _user['workspaces'] = workspaces
        _user['clusters'] = clusters
        user = schemas.UserWithWorkspace(**_user)
        
        if user:
            users.append(user)
    return users


async def get_user_info(user):
    
    _workspaces = await MongoDB.get_all('workspaces_as_user', {'username': user['username']})

    workspaces = []

    if _workspaces is not None:

        for _workspace in _workspaces:
            _workspace.pop('_id')
            workspaces.append(_workspace['workspace'])


    workspaces_ = await MongoDB.get_all('workspaces', {'name': {'$in': workspaces}})

    clusters = []

    for workspace in workspaces_:
        clusters.extend([cluster for cluster in workspace['clusters'] if cluster not in clusters])

    

    clusters = list(set(clusters))

    user.pop('_id')
    user['workspaces'] = workspaces
    user['clusters'] = clusters
    user = schemas.UserWithWorkspace(**user)
    return user


@router.get("/me", response_model=schemas.UserWithWorkspace)
async def read_users_me(current_user: dict = Depends(get_current_active_user)):
    return await get_user_info(current_user)

@router.put("/me", response_model=schemas.User)
async def update_user_me(
    user_update: schemas.UserUpdate,
    current_user: dict = Depends(get_current_active_user)
):
    # Update user fields
    for key, value in user_update.dict(exclude_unset=True).items():
        current_user[key] = value
    
    current_user["updated_at"] = datetime.utcnow().isoformat()
    
    # Update user data

    await MongoDB.update('users', {'id': current_user['id']}, current_user)
    
    return current_user

@router.put("/me/password", response_model=schemas.User)
async def change_password(
    password_change: schemas.PasswordChange,
    current_user: dict = Depends(get_current_active_user)
):
    # Verify current password
    if not auth.verify_password(password_change.current_password, current_user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )
    
    # Update password
    current_user["hashed_password"] = auth.get_password_hash(password_change.new_password)
    current_user["updated_at"] = datetime.utcnow().isoformat()
    
    # Update user data
    #await MongoDB.set(USER_KEY.format(current_user["id"]), current_user)

    await MongoDB.update('users', {'id': current_user['id']}, current_user)
    
    return current_user


@router.get("/{user_id}", response_model=schemas.User)
async def get_user(
    user_id: str,
    current_user: dict = Depends(get_current_admin_user)
):
    user = await MongoDB.get('users', {'username': user_id})
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    current_user: dict = Depends(get_current_admin_user)
):
    db_user = await MongoDB.get('users', {'username': user_id})

    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Prevent self-deletion
    if db_user["username"] == current_user["username"]:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")
    
    # Delete user data
    await MongoDB.delete_all('users', {'username': user_id})
    await MongoDB.delete_all('users', {'email': db_user["email"]})
    
    return {"message": "User deleted successfully"} 