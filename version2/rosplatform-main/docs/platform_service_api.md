# 플랫폼 서비스 API 문서

## 1. API 개요

### 1.1 기본 정보
- Base URL: `http://api.example.com/v1`
- 인증: Bearer Token
- 응답 형식: JSON

### 1.2 공통 응답 형식
```json
{
    "status": "success|error",
    "data": {},
    "message": "응답 메시지",
    "timestamp": "2024-03-20T10:00:00Z"
}
```

## 2. 플랫폼 서비스 API

### 2.1 서비스 조회

#### 전체 서비스 목록 조회
- **GET** `/platform/services`
- **설명**: 등록된 모든 플랫폼 서비스 목록을 조회합니다.
- **응답**:
```json
{
    "status": "success",
    "data": {
        "services": [
            {
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
        ]
    }
}
```

#### 특정 서비스 조회
- **GET** `/platform/services/{name}`
- **설명**: 특정 플랫폼 서비스의 상세 정보를 조회합니다.
- **응답**:
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

#### 서비스 검색
- **GET** `/platform/services/search`
- **설명**: 조건에 맞는 플랫폼 서비스를 검색합니다.
- **쿼리 파라미터**:
  - `name`: 서비스 이름 (부분 일치)
  - `ip`: IP 주소 (부분 일치)
  - `port`: 포트 번호 (정확히 일치)
  - `status`: 서비스 상태 (active/inactive)
- **응답**: 전체 서비스 목록 조회와 동일한 형식

### 2.2 서비스 생성

- **POST** `/platform/services`
- **설명**: 새로운 플랫폼 서비스를 생성합니다.
- **요청 본문**:
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
- **응답**: 특정 서비스 조회와 동일한 형식

### 2.3 서비스 수정

#### 전체 수정
- **PUT** `/platform/services/{name}`
- **설명**: 플랫폼 서비스의 모든 정보를 수정합니다.
- **요청 본문**:
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

#### 부분 수정
- **PATCH** `/platform/services/{name}`
- **설명**: 플랫폼 서비스의 일부 정보만 수정합니다.
- **요청 본문**:
```json
{
    "ip": "string",
    "port": 0,
    "status": "active|inactive"
}
```

### 2.4 서비스 삭제

- **DELETE** `/platform/services/{name}`
- **설명**: 플랫폼 서비스를 삭제합니다.
- **응답**:
```json
{
    "status": "success",
    "message": "Service deleted successfully",
    "data": {
        "name": "example-service"
    }
}
```

## 3. 에러 처리

### 3.1 에러 코드
| 코드 | 설명 |
|------|------|
| 400 | 잘못된 요청 (필수 필드 누락, 잘못된 형식 등) |
| 401 | 인증 실패 |
| 403 | 권한 없음 |
| 404 | 서비스 없음 |
| 409 | 서비스 이름 중복 |
| 500 | 서버 내부 오류 |

### 3.2 에러 응답 예시
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
