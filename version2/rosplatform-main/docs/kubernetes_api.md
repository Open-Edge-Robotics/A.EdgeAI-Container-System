# 쿠버네티스 리소스 관리 API

## 1. 시스템 개요

### 1.1 목적
- FastAPI를 통한 여러 쿠버네티스 리소스 접근 제어
- 사용자별 권한 관리 및 모니터링
- RESTful API를 통한 쿠버네티스 리소스 관리

### 1.2 주요 기능
- 여러 쿠버네티스 리소스들에 대한 수정, 삭제, 조회 기능

## 2. API 기본 정보

### 2.1 기본 URL
- Base URL: `http://api.example.com/v1`
- 인증: Bearer Token
- 응답 형식: JSON

### 2.2 공통 응답 형식
```json
{
    "status": "success|error",
    "data": {},
    "message": "응답 메시지",
    "timestamp": "2024-03-20T10:00:00Z"
}
```

## 3. 리소스별 CRUD API

### 3.1 플랫폼 서비스 (Platform Service)

#### 조회 (Read)
- **GET** `/platform/services`
  - 플랫폼 서비스 목록 조회
- **GET** `/platform/services/{name}`
  - 특정 플랫폼 서비스 상세 정보 조회
- **GET** `/platform/services/search`
  - 플랫폼 서비스 검색 (쿼리 파라미터: name, ip, port)

#### 생성 (Create)
- **POST** `/platform/services`
```json
{
    "name": "string",
    "ip": "string",
    "port": 0,
    "description": "string",
    "status": "active|inactive",
    "metadata": {
        "created_by": "string",
        "tags": []
    }
}
```

#### 수정 (Update)
- **PUT** `/platform/services/{name}`
  - 플랫폼 서비스 전체 수정
```json
{
    "ip": "string",
    "port": 0,
    "description": "string",
    "status": "active|inactive",
    "metadata": {
        "updated_by": "string",
        "tags": []
    }
}
```
- **PATCH** `/platform/services/{name}`
  - 플랫폼 서비스 부분 수정
```json
{
    "ip": "string",
    "port": 0,
    "status": "active|inactive"
}
```

#### 삭제 (Delete)
- **DELETE** `/platform/services/{name}`
  - 플랫폼 서비스 삭제

#### 응답 예시
```json
{
    "status": "success",
    "data": {
        "name": "example-service",
        "ip": "192.168.1.100",
        "port": 8080,
        "description": "Example platform service",
        "status": "active",
        "metadata": {
            "created_by": "admin",
            "created_at": "2024-03-20T10:00:00Z",
            "updated_at": "2024-03-20T10:00:00Z",
            "tags": ["web", "api"]
        }
    }
}
```

### 3.2 파드 (Pod)

#### 조회 (Read)
- **GET** `/clusters/{cluster_id}/namespaces/{namespace}/pods`
  - 파드 목록 조회
- **GET** `/clusters/{cluster_id}/namespaces/{namespace}/pods/{name}`
  - 특정 파드 상세 정보 조회
- **GET** `/clusters/{cluster_id}/namespaces/{namespace}/pods/{name}/logs`
  - 파드 로그 조회

#### 생성 (Create)
- **POST** `/clusters/{cluster_id}/namespaces/{namespace}/pods`
```json
{
    "name": "string",
    "containers": [
        {
            "name": "string",
            "image": "string",
            "ports": [
                {
                    "containerPort": 0,
                    "protocol": "TCP|UDP"
                }
            ],
            "resources": {
                "requests": {
                    "cpu": "string",
                    "memory": "string"
                },
                "limits": {
                    "cpu": "string",
                    "memory": "string"
                }
            }
        }
    ],
    "volumes": [],
    "restartPolicy": "Always|OnFailure|Never"
}
```

#### 수정 (Update)
- **PUT** `/clusters/{cluster_id}/namespaces/{namespace}/pods/{name}`
  - 파드 전체 수정
- **PATCH** `/clusters/{cluster_id}/namespaces/{namespace}/pods/{name}`
  - 파드 부분 수정

#### 삭제 (Delete)
- **DELETE** `/clusters/{cluster_id}/namespaces/{namespace}/pods/{name}`
  - 파드 삭제

### 3.3 디플로이먼트 (Deployment)

#### 조회 (Read)
- **GET** `/clusters/{cluster_id}/namespaces/{namespace}/deployments`
  - 디플로이먼트 목록 조회
- **GET** `/clusters/{cluster_id}/namespaces/{namespace}/deployments/{name}`
  - 특정 디플로이먼트 상세 정보 조회

#### 생성 (Create)
- **POST** `/clusters/{cluster_id}/namespaces/{namespace}/deployments`
```json
{
    "name": "string",
    "replicas": 0,
    "template": {
        "containers": [
            {
                "name": "string",
                "image": "string",
                "ports": [],
                "resources": {}
            }
        ]
    }
}
```

#### 수정 (Update)
- **PUT** `/clusters/{cluster_id}/namespaces/{namespace}/deployments/{name}`
  - 디플로이먼트 전체 수정
- **PATCH** `/clusters/{cluster_id}/namespaces/{namespace}/deployments/{name}`
  - 디플로이먼트 부분 수정

#### 삭제 (Delete)
- **DELETE** `/clusters/{cluster_id}/namespaces/{namespace}/deployments/{name}`
  - 디플로이먼트 삭제

### 3.4 서비스 (Service)

#### 조회 (Read)
- **GET** `/clusters/{cluster_id}/namespaces/{namespace}/services`
  - 서비스 목록 조회
- **GET** `/clusters/{cluster_id}/namespaces/{namespace}/services/{name}`
  - 특정 서비스 상세 정보 조회

#### 생성 (Create)
- **POST** `/clusters/{cluster_id}/namespaces/{namespace}/services`
```json
{
    "name": "string",
    "type": "ClusterIP|NodePort|LoadBalancer",
    "ports": [
        {
            "port": 0,
            "target_port": 0,
            "protocol": "TCP|UDP"
        }
    ],
    "selector": {}
}
```

#### 수정 (Update)
- **PUT** `/clusters/{cluster_id}/namespaces/{namespace}/services/{name}`
  - 서비스 전체 수정
- **PATCH** `/clusters/{cluster_id}/namespaces/{namespace}/services/{name}`
  - 서비스 부분 수정

#### 삭제 (Delete)
- **DELETE** `/clusters/{cluster_id}/namespaces/{namespace}/services/{name}`
  - 서비스 삭제

### 3.5 퍼시스턴트볼륨 (PersistentVolume)

#### 조회 (Read)
- **GET** `/clusters/{cluster_id}/persistentvolumes`
  - PV 목록 조회
- **GET** `/clusters/{cluster_id}/persistentvolumes/{name}`
  - 특정 PV 상세 정보 조회

#### 생성 (Create)
- **POST** `/clusters/{cluster_id}/persistentvolumes`
```json
{
    "name": "string",
    "capacity": {
        "storage": "string"
    },
    "accessModes": ["ReadWriteOnce", "ReadOnlyMany", "ReadWriteMany"],
    "persistentVolumeReclaimPolicy": "Retain|Recycle|Delete",
    "storageClassName": "string",
    "hostPath": {
        "path": "string"
    }
}
```

#### 수정 (Update)
- **PUT** `/clusters/{cluster_id}/persistentvolumes/{name}`
  - PV 전체 수정
- **PATCH** `/clusters/{cluster_id}/persistentvolumes/{name}`
  - PV 부분 수정

#### 삭제 (Delete)
- **DELETE** `/clusters/{cluster_id}/persistentvolumes/{name}`
  - PV 삭제

### 3.6 퍼시스턴트볼륨클레임 (PersistentVolumeClaim)

#### 조회 (Read)
- **GET** `/clusters/{cluster_id}/namespaces/{namespace}/persistentvolumeclaims`
  - PVC 목록 조회
- **GET** `/clusters/{cluster_id}/namespaces/{namespace}/persistentvolumeclaims/{name}`
  - 특정 PVC 상세 정보 조회

#### 생성 (Create)
- **POST** `/clusters/{cluster_id}/namespaces/{namespace}/persistentvolumeclaims`
```json
{
    "name": "string",
    "accessModes": ["ReadWriteOnce", "ReadOnlyMany", "ReadWriteMany"],
    "resources": {
        "requests": {
            "storage": "string"
        }
    },
    "storageClassName": "string"
}
```

#### 수정 (Update)
- **PUT** `/clusters/{cluster_id}/namespaces/{namespace}/persistentvolumeclaims/{name}`
  - PVC 전체 수정
- **PATCH** `/clusters/{cluster_id}/namespaces/{namespace}/persistentvolumeclaims/{name}`
  - PVC 부분 수정

#### 삭제 (Delete)
- **DELETE** `/clusters/{cluster_id}/namespaces/{namespace}/persistentvolumeclaims/{name}`
  - PVC 삭제

## 4. 에러 처리

### 4.1 공통 에러 코드
| 코드 | 설명 |
|------|------|
| 400 | 잘못된 요청 |
| 401 | 인증 실패 |
| 403 | 권한 없음 |
| 404 | 리소스 없음 |
| 409 | 리소스 충돌 |
| 500 | 서버 내부 오류 |

### 4.2 에러 응답 예시
```json
{
    "status": "error",
    "error": {
        "code": "string",
        "message": "string",
        "details": {}
    }
}
```

## 5. 보안

### 5.1 인증
- 모든 API 요청은 Bearer 토큰을 포함해야 함
- 토큰은 Authorization 헤더에 포함: `Authorization: Bearer <token>`

### 5.2 권한
- 클러스터 관리자: 모든 API 접근 가능
- 네임스페이스 관리자: 해당 네임스페이스의 리소스만 관리 가능
- 일반 사용자: 조회 권한만 있음

## 6. 변경 이력

| 버전 | 날짜 | 변경 내용 |
|------|------|-----------|
| 1.0.0 | 2024-03-20 | 최초 작성 |