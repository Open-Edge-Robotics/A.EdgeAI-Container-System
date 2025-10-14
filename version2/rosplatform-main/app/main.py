from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from typing import List
import uvicorn
import uuid
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from .kafkamessage import SimpleMessage
from . import schemas, auth
from .database import MongoDB, SERVICE_KEY, SERVICE_LIST_KEY, init_db
from .routers import workspaces, projects, clusters, users, platform_services, kubernetes, ros2_bridge, faas
import json
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from .auth import get_current_admin_user, get_current_active_user
from .kafkaservice import start_module, stop_module
from .scheduler import request_kube_api
import yaml
from .kuberesource import create_deployment_yaml, create_service_yaml, create_pod_yaml

yaml.Dumper.ignore_aliases = lambda *args : True
# FastAPI 애플리케이션 설정
app = FastAPI(
    title="Robot Platform API",           # API 제목
    description="Robot Platform API Documentation",  # API 설명
    version="1.0.0"                       # API 버전
)

@app.on_event("startup")
async def startup_event():
    await init_db()

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],                  # 모든 출처 허용
    allow_credentials=True,               # 인증 정보 허용
    allow_methods=["*"],                  # 모든 HTTP 메서드 허용
    allow_headers=["*"],                  # 모든 헤더 허용
)

# 라우터 등록
app.include_router(users.router)          # 사용자 관리 라우터
app.include_router(workspaces.router)     # 작업공간 관리 라우터
app.include_router(projects.router)       # 프로젝트 관리 라우터
app.include_router(clusters.router)       # 클러스터 관리 라우터
app.include_router(platform_services.router)  # 플랫폼 서비스 라우터
app.include_router(kubernetes.router)     # 쿠버네티스 API 라우터
app.include_router(ros2_bridge.router)    # ROS2 브릿지 라우터
app.include_router(faas.router)           # FaaS 라우터

# 인증 엔드포인트
@app.post("/token", response_model=schemas.ResToken)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends()  # 폼 데이터 의존성
):
    """액세스 토큰 발급 API"""
    # 사용자 인증
    await init_admin()

    user = await MongoDB.get('users', {'username': form_data.username})
    if not user or not auth.verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 토큰 생성
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )


    res =  {"access_token": access_token, "token_type": "bearer", "user_id": user["id"], "user_type": user["user_type"]}
    #print(res)

    return res


async def has_user(username: str):
    user = await MongoDB.get('users', {'username': username})
    return user is not None

# Create initial admin user on startup
async def init_admin():

    #await MongoDB.delete_all('users', {})

    if not await has_user("admin"):
    
        user_data = {
            "id": 'admin',
            "email": 'admin@etri.dev',
            "username": 'admin',
            "hashed_password": auth.get_password_hash('1234'),
            "is_active": True,
            "user_type": "admin",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at":  datetime.utcnow().isoformat()
        }

        _user = schemas.User(**user_data)

        user_data = json.loads(_user.model_dump_json())

        await MongoDB.set('users', user_data)

 


# 템플릿 설정
templates = Jinja2Templates(directory="templates")

# 정적 파일 설정 (CSS, JS, 이미지 등)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/webfonts", StaticFiles(directory="webfonts"), name="webfonts")



# 기본 라우트
@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("login.html", {
        "request": request,
        "title": "FastAPI 웹서버",
        "version": "1.0.0"
    })


@app.get("/platform_page")
async def platform(request: Request):

    return templates.TemplateResponse("index.html", {
        "request": request,
        "title": "Admin"
    })


@app.get("/dashboard")
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "title": "Dashboard"
    })

@app.get("/cluster")
async def cluster(request: Request):
    return templates.TemplateResponse("cluster.html", {
        "request": request,
        "title": "Cluster"
    })

@app.get("/node")
async def node(request: Request):
    return templates.TemplateResponse("node.html", {
        "request": request,
        "title": "Node"
    })

@app.get("/pod")
async def pod(request: Request):
    return templates.TemplateResponse("pod.html", {
        "request": request,
        "title": "Pod"
    })

@app.get("/monitoring")
async def monitoring(request: Request):
    return templates.TemplateResponse("monitoring.html", {
        "request": request,
        "title": "Monitoring"
    })


@app.get("/platformservice")
async def platformservice(request: Request):
    return templates.TemplateResponse("platformservice.html", {
        "request": request,
        "title": "Platformservice"
    })

@app.get("/user_page")
async def user_page(request: Request):
    return templates.TemplateResponse("user.html", {
        "request": request,
        "title": "User"
    })

@app.get("/workspace")
async def workspace(request: Request):
    return templates.TemplateResponse("workspace.html", {
        "request": request,
        "title": "Workspace"
    })

@app.get("/project")
async def project(request: Request):
    return templates.TemplateResponse("project.html", {
        "request": request,
        "title": "Project"
    })

@app.get("/robot")
async def robot(request: Request):
    return templates.TemplateResponse("robot.html", {
        "request": request,
        "title": "Robot"
    })

@app.get("/topic")
async def topic(request: Request):
    return templates.TemplateResponse("topic.html", {
        "request": request,
        "title": "Topic"
    })



# project
@app.get("/project_page")
async def project_index(request: Request):
    return templates.TemplateResponse("project/index.html", {
        "request": request,
        "title": "Project"
    })

@app.get("/project/info")
async def project_info(request: Request):
    return templates.TemplateResponse("project/userinfo.html", {
        "request": request,
        "title": "Project Info"
    })

@app.get("/project/userinfo")
async def project_userinfo(request: Request):
    return templates.TemplateResponse("project/userinfo.html", {
        "request": request,
        "title": "Project User Info"
    })

@app.get("/project/project")
async def project_project(request: Request):
    return templates.TemplateResponse("project/project.html", {
        "request": request,
        "title": "Project Project"
    })

@app.get("/project/cluster")
async def project_cluster(request: Request):
    return templates.TemplateResponse("project/cluster.html", {
        "request": request,
        "title": "Project Cluster"
    })

@app.get("/project/node")
async def project_node(request: Request):
    return templates.TemplateResponse("project/node.html", {
        "request": request,
        "title": "Project Node"
    })

@app.get("/project/deployment")
async def project_deployment(request: Request):
    return templates.TemplateResponse("project/deployment.html", {
        "request": request,
        "title": "Project Deployment"
    })

@app.get("/project/pod")
async def project_pod(request: Request):
    return templates.TemplateResponse("project/pod.html", {
        "request": request,
        "title": "Project Pod"
    })

@app.get("/project/service")
async def project_service(request: Request):
    return templates.TemplateResponse("project/service.html", {
        "request": request,
        "title": "Project Service"
    })

@app.get("/project/volume")
async def project_volume(request: Request):
    return templates.TemplateResponse("project/volume.html", {
        "request": request,
        "title": "Project Volume"
    })

@app.get("/project/yamls")
async def project_yamls(request: Request):
    return templates.TemplateResponse("project/yamls.html", {
        "request": request,
        "title": "Project Yamls"
    })

@app.get("/project/robot")
async def project_robot(request: Request):
    return templates.TemplateResponse("project/robot.html", {
        "request": request,
        "title": "Project Robot"
    })

@app.get("/project/topic")
async def project_topic(request: Request):
    return templates.TemplateResponse("project/topic.html", {
        "request": request,
        "title": "Project Topic"
    })

@app.get("/project/serviceaction")
async def project_serviceaction(request: Request):
    return templates.TemplateResponse("project/serviceaction.html", {
        "request": request,
        "title": "Project Service Action"
    })

@app.get("/project/map")
async def project_map(request: Request):
    return templates.TemplateResponse("project/map.html", {
        "request": request,
        "title": "Project Map"
    })



@app.get("/login")
async def login(request: Request):
    return templates.TemplateResponse("login.html", {
        "request": request,
        "title": "Login"
    })


@app.get("/signup")
async def signup(request: Request):
    return templates.TemplateResponse("signup.html", {
        "request": request,
        "title": "Signup"
    })


@app.post("/login")
async def login_post(request: Request):
    return templates.TemplateResponse("login.html", {
        "request": request,
        "title": "Login"
    })



@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "서버가 정상적으로 작동 중입니다."}


@app.post("/requst_kube_api")
async def requst_kube_api(request: Request
             #, current_user: dict = Depends(get_current_active_user)
             ):
    request_data = await request.json()

    #print(request_data)
    if request_data.get("type") == "deployment" or request_data.get("type") == "pod":

        if request_data.get("type") == "deployment":
            resource_yaml = create_deployment_yaml(request_data)
        else:
            resource_yaml = create_pod_yaml(request_data)

        if request_data.get("service_name") != "":
            service_yaml = create_service_yaml(request_data)
            send_data = {"resource": request_data.get("type"), "data": resource_yaml, "service": service_yaml}
        else:
            send_data = {"resource": request_data.get("type"), "data": resource_yaml}

        send_data['priority'] = request_data['priority']
        send_data['target_cluster'] = request_data['target_cluster']
        send_data['present_clusters'] = request_data['present_clusters']

        if 'username' in request_data:
            send_data['username'] = request_data['username']

        if 'workspace' in request_data:
            send_data['workspace'] = request_data['workspace']

        if 'project' in request_data:
            send_data['project'] = request_data['project']
        
        res = await request_kube_api(send_data)

        return res
    
    elif request_data.get("type") == "service":
        resource_yaml = create_service_yaml(request_data)
        send_data = {"resource": request_data.get("type"), "data": resource_yaml}
        send_data['priority'] = 'simple'
        send_data['pod_name'] = request_data['select_pod']
        send_data['method'] = 'create'
        send_data['namespace'] = request_data['username']
        send_data['target_cluster'] = request_data['select_cluster']

        if 'username' in request_data:
            send_data['username'] = request_data['username']

        if 'workspace' in request_data:
            send_data['workspace'] = request_data['workspace']

        if 'project' in request_data:
            send_data['project'] = request_data['project']

        res = await request_kube_api(send_data)
        return res
    elif request_data.get("type") == "yaml":
        yaml_data = request_data.get("yaml")
        send_data = {
            "resource": "yaml",
            "data": yaml_data,
            "priority": request_data.get("priority", "simple"),
            "target_cluster": request_data.get("target_cluster"),
            "source_cluster": request_data.get("source_cluster"),
            "source_node": request_data.get("source_node"),
            "present_clusters": request_data.get("present_clusters"),
            "namespace": request_data.get("username"),
            "method": "create"
        }

        if 'username' in request_data:
            send_data['username'] = request_data['username']

        if 'workspace' in request_data:
            send_data['workspace'] = request_data['workspace']

        if 'project' in request_data:
            send_data['project'] = request_data['project']

        res = await request_kube_api(request_data)
        return res
    else:
        return {"status": "error", "message": "Invalid request type"}


@app.post("/request_simple")
async def request_simple(request: Request
            # , current_user: dict = Depends(get_current_active_user)
            ):

    request_data = await request.json()
    message = SimpleMessage.model_validate(request_data).model_dump()
    message['priority'] = 'simple'
    res = await request_kube_api(message)
    return res


start_module()

# 서버 실행
if __name__ == "__main__":
   uvicorn.run(app, host="0.0.0.0", port=8000, workers=5)
   #uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)