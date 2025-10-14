# FaaS Serverless API

## 1. 시스템 개요

### 1.1 목적
- FaaS 기반 서버리스 함수 관리
- 환경, 함수, 패키지, 트리거의 CRUD 작업 지원
- 서버리스 함수의 실행 및 모니터링

### 1.2 주요 기능
- 환경(Environment) 관리
- 함수(Function) 관리
- 패키지(Package) 관리
- 트리거(Trigger) 관리
- 함수 실행 및 모니터링

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

## 3. 리소스별 API

### 3.1 환경 (Environment)

#### 조회 (Read)
- **GET** `/environments`
  - 환경 목록 조회
- **GET** `/environments/{env_name}`
  - 특정 환경 상세 정보 조회
- **GET** `/environments/{env_name}/status`
  - 환경 상태 조회

#### 생성 (Create)
- **POST** `/environments`
```json
{
    "name": "string",
    "image": "string",
    "builder_image": "string",
    "poolsize": 3,
    "resources": {
        "requests": {
            "cpu": "100m",
            "memory": "128Mi"
        },
        "limits": {
            "cpu": "200m",
            "memory": "256Mi"
        }
    },
    "runtime_version": "string",
    "keep_archive": false
}
```

#### 수정 (Update)
- **PUT** `/environments/{env_name}`
  - 환경 전체 수정
- **PATCH** `/environments/{env_name}`
  - 환경 부분 수정

#### 삭제 (Delete)
- **DELETE** `/environments/{env_name}`
  - 환경 삭제

### 3.2 함수 (Function)

#### 조회 (Read)
- **GET** `/functions`
  - 함수 목록 조회
- **GET** `/functions/{function_name}`
  - 특정 함수 상세 정보 조회
- **GET** `/functions/{function_name}/logs`
  - 함수 실행 로그 조회
- **GET** `/functions/{function_name}/metrics`
  - 함수 실행 메트릭 조회

#### 생성 (Create)
- **POST** `/functions`
```json
{
    "name": "string",
    "environment": "string",
    "package": "string",
    "entrypoint": "string",
    "secrets": ["string"],
    "configmaps": ["string"],
    "resources": {
        "requests": {
            "cpu": "100m",
            "memory": "128Mi"
        },
        "limits": {
            "cpu": "200m",
            "memory": "256Mi"
        }
    },
    "invoke_strategy": {
        "execution_strategy": "poolmgr|newdeploy",
        "min_scale": 0,
        "max_scale": 1,
        "target_cpu_percent": 80
    }
}
```

#### 수정 (Update)
- **PUT** `/functions/{function_name}`
  - 함수 전체 수정
- **PATCH** `/functions/{function_name}`
  - 함수 부분 수정

#### 삭제 (Delete)
- **DELETE** `/functions/{function_name}`
  - 함수 삭제

#### 실행 (Invoke)
- **POST** `/functions/{function_name}/invoke`
  - 함수 직접 실행
```json
{
    "body": "string",
    "headers": {},
    "query": {}
}
```

### 3.3 패키지 (Package)

#### 조회 (Read)
- **GET** `/packages`
  - 패키지 목록 조회
- **GET** `/packages/{package_name}`
  - 특정 패키지 상세 정보 조회
- **GET** `/packages/{package_name}/download`
  - 패키지 다운로드

#### 생성 (Create)
- **POST** `/packages`
  - 패키지 생성 (multipart/form-data)
  - 파일 업로드 지원

#### 수정 (Update)
- **PUT** `/packages/{package_name}`
  - 패키지 전체 수정
- **PATCH** `/packages/{package_name}`
  - 패키지 부분 수정

#### 삭제 (Delete)
- **DELETE** `/packages/{package_name}`
  - 패키지 삭제

### 3.4 트리거 (Trigger)

#### 조회 (Read)
- **GET** `/triggers`
  - 트리거 목록 조회
- **GET** `/triggers/{trigger_name}`
  - 특정 트리거 상세 정보 조회
- **GET** `/triggers/{trigger_name}/status`
  - 트리거 상태 조회

#### 생성 (Create)
- **POST** `/triggers`
```json
{
    "name": "string",
    "type": "http|messagequeue|time|kafka",
    "function": "string",
    "config": {
        "method": "GET|POST|PUT|DELETE",
        "path": "/path",
        "host": "example.com",
        "cron": "*/5 * * * *",
        "topic": "my-topic",
        "bootstrap_servers": ["kafka:9092"]
    }
}
```

#### 수정 (Update)
- **PUT** `/triggers/{trigger_name}`
  - 트리거 전체 수정
- **PATCH** `/triggers/{trigger_name}`
  - 트리거 부분 수정

#### 삭제 (Delete)
- **DELETE** `/triggers/{trigger_name}`
  - 트리거 삭제

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
