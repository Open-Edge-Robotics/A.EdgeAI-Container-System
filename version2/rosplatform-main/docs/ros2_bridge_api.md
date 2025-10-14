# ROS2 Bridge API

## 1. 시스템 개요

### 1.1 목적
- ROS2 환경의 노드, 서비스, 토픽, 메시지 타입 등의 정보를 조회
- 클러스터별 ROS2 시스템 상태 모니터링
- ROS2와 외부 시스템 간의 브릿지 역할

### 1.2 주요 기능
- ROS2 노드 정보 조회
- ROS2 서비스 정보 조회
- ROS2 토픽 정보 조회
- ROS2 메시지 타입 정보 조회
- ROS2 시스템 상태 모니터링

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

### 3.1 브릿지 (Bridge)

#### 조회 (Read)
- **GET** `/bridges`
  - 브릿지 목록 조회
- **GET** `/bridges/{bridge_id}`
  - 특정 브릿지 상세 정보 조회
- **GET** `/bridges/{bridge_id}/status`
  - 브릿지 상태 조회
- **GET** `/bridges/{bridge_id}/config`
  - 브릿지 설정 조회


#### 응답 예시
```json
{
    "status": "success",
    "data": {
        "bridges": [
            {
                "id": "bridge-001",
                "name": "main-bridge",
                "description": "Main ROS2 bridge for cluster-001",
                "host_name": "cluster-001",
                "status": "active",
                "ip": "active",
                "zeromq": "active",
                "created_at": "2024-03-20T10:00:00Z",
                "updated_at": "2024-03-20T10:00:00Z"
            }
        ]
    }
}
```

### 3.2 노드 (Node)

#### 조회 (Read)
- **GET** `/bridges/{bridge_id}/ros2/nodes`
  - ROS2 노드 목록 조회
- **GET** `/bridges/{bridge_id}/ros2/nodes/{node_name}`
  - 특정 노드 상세 정보 조회
- **GET** `/bridges/{bridge_id}/ros2/nodes/{node_name}/parameters`
  - 노드 파라미터 조회

#### 응답 예시
```json
{
    "status": "success",
    "data": {
        "nodes": [
            {
                "name": "talker",
                "namespace": "/",
                "status": "active",
                "pid": 1234,
                "parameters": {
                    "param1": "value1",
                    "param2": "value2"
                }
            }
        ]
    }
}
```

### 3.3 서비스 (Service)

#### 조회 (Read)
- **GET** `/bridges/{bridge_id}/ros2/services`
  - ROS2 서비스 목록 조회
- **GET** `/bridges/{bridge_id}/ros2/services/{service_name}`
  - 특정 서비스 상세 정보 조회
- **GET** `/bridges/{bridge_id}/ros2/services/{service_name}/type`
  - 서비스 타입 정보 조회

#### 응답 예시
```json
{
    "status": "success",
    "data": {
        "services": [
            {
                "name": "/add_two_ints",
                "type": "example_interfaces/srv/AddTwoInts",
                "nodes": ["server", "client"],
                "status": "active"
            }
        ]
    }
}
```

### 3.4 토픽 (Topic)

#### 조회 (Read)
- **GET** `/bridges/{bridge_id}/ros2/topics`
  - ROS2 토픽 목록 조회
- **GET** `/bridges/{bridge_id}/ros2/topics/{topic_name}`
  - 특정 토픽 상세 정보 조회
- **GET** `/bridges/{bridge_id}/ros2/topics/{topic_name}/type`
  - 토픽 메시지 타입 조회
- **GET** `/bridges/{bridge_id}/ros2/topics/{topic_name}/publishers`
  - 토픽 발행자 목록 조회
- **GET** `/bridges/{bridge_id}/ros2/topics/{topic_name}/subscribers`
  - 토픽 구독자 목록 조회

#### 응답 예시
```json
{
    "status": "success",
    "data": {
        "topics": [
            {
                "name": "/chatter",
                "type": "std_msgs/msg/String",
                "publishers": ["talker"],
                "subscribers": ["listener"],
                "message_count": 100,
                "frequency": 10.0
            }
        ]
    }
}
```

### 3.5 액션 (Action)

#### 조회 (Read)
- **GET** `/bridges/{bridge_id}/ros2/actions`
  - ROS2 액션 목록 조회
- **GET** `/bridges/{bridge_id}/ros2/actions/{action_name}`
  - 특정 액션 상세 정보 조회
- **GET** `/bridges/{bridge_id}/ros2/actions/{action_name}/type`
  - 액션 타입 정보 조회
- **GET** `/bridges/{bridge_id}/ros2/actions/{action_name}/clients`
  - 액션 클라이언트 목록 조회
- **GET** `/bridges/{bridge_id}/ros2/actions/{action_name}/servers`
  - 액션 서버 목록 조회

#### 응답 예시
```json
{
    "status": "success",
    "data": {
        "actions": [
            {
                "name": "/fibonacci",
                "type": "example_interfaces/action/Fibonacci",
                "clients": ["action_client"],
                "servers": ["action_server"],
                "status": "active",
                "goal_count": 5,
                "result_count": 3,
                "feedback_count": 15
            }
        ]
    }
}
```

### 3.6 퍼블리셔 (Publisher)

#### 조회 (Read)
- **GET** `/bridges/{bridge_id}/ros2/publishers`
  - ROS2 퍼블리셔 목록 조회
- **GET** `/bridges/{bridge_id}/ros2/publishers/{publisher_id}`
  - 특정 퍼블리셔 상세 정보 조회
- **GET** `/bridges/{bridge_id}/ros2/publishers/{publisher_id}/topics`
  - 퍼블리셔가 발행하는 토픽 목록 조회
- **GET** `/bridges/{bridge_id}/ros2/publishers/{publisher_id}/qos`
  - 퍼블리셔 QoS 설정 조회

#### 응답 예시
```json
{
    "status": "success",
    "data": {
        "publishers": [
            {
                "id": "pub-001",
                "node_name": "talker",
                "topics": [
                    {
                        "name": "/chatter",
                        "type": "std_msgs/msg/String",
                        "qos_profile": "reliable"
                    }
                ],
                "message_count": 1000,
                "publish_rate": 10.0,
                "status": "active"
            }
        ]
    }
}
```

### 3.7 서브스크라이버 (Subscriber)

#### 조회 (Read)
- **GET** `/bridges/{bridge_id}/ros2/subscribers`
  - ROS2 서브스크라이버 목록 조회
- **GET** `/bridges/{bridge_id}/ros2/subscribers/{subscriber_id}`
  - 특정 서브스크라이버 상세 정보 조회
- **GET** `/bridges/{bridge_id}/ros2/subscribers/{subscriber_id}/topics`
  - 서브스크라이버가 구독하는 토픽 목록 조회
- **GET** `/bridges/{bridge_id}/ros2/subscribers/{subscriber_id}/qos`
  - 서브스크라이버 QoS 설정 조회

#### 응답 예시
```json
{
    "status": "success",
    "data": {
        "subscribers": [
            {
                "id": "sub-001",
                "node_name": "listener",
                "topics": [
                    {
                        "name": "/chatter",
                        "type": "std_msgs/msg/String",
                        "qos_profile": "reliable"
                    }
                ],
                "message_count": 950,
                "receive_rate": 9.8,
                "status": "active"
            }
        ]
    }
}
```

### 3.8 메시지 타입 (Message Type)

#### 조회 (Read)
- **GET** `/bridges/{bridge_id}/ros2/message-types`
  - ROS2 메시지 타입 목록 조회
- **GET** `/bridges/{bridge_id}/ros2/message-types/{type_name}`
  - 특정 메시지 타입 상세 정보 조회
- **GET** `/bridges/{bridge_id}/ros2/message-types/{type_name}/definition`
  - 메시지 타입 정의 조회

#### 응답 예시
```json
{
    "status": "success",
    "data": {
        "message_types": [
            {
                "name": "std_msgs/msg/String",
                "package": "std_msgs",
                "definition": {
                    "fields": [
                        {
                            "name": "data",
                            "type": "string"
                        }
                    ]
                }
            }
        ]
    }
}
```

### 3.9 시스템 상태 (System Status)

#### 조회 (Read)
- **GET** `/bridges/{bridge_id}/ros2/status`
  - ROS2 시스템 상태 조회
- **GET** `/bridges/{bridge_id}/ros2/status/network`
  - ROS2 네트워크 상태 조회
- **GET** `/bridges/{bridge_id}/ros2/status/resources`
  - ROS2 리소스 사용량 조회

#### 응답 예시
```json
{
    "status": "success",
    "data": {
        "system_status": {
            "ros_version": "2.0.0",
            "active_nodes": 5,
            "active_topics": 10,
            "active_services": 3,
            "network": {
                "connections": 15,
                "bandwidth": "1.2 MB/s"
            },
            "resources": {
                "cpu_usage": "25%",
                "memory_usage": "512MB",
                "disk_usage": "1.2GB"
            }
        }
    }
}
```

### 3.10 브릿지 연결 (Bridge Connection)

#### 조회 (Read)
- **GET** `/bridges/{bridge_id}/connections`
  - 브릿지의 모든 연결 목록 조회
- **GET** `/bridges/{bridge_id}/connections/{connection_id}`
  - 특정 연결 상세 정보 조회
- **GET** `/bridges/{bridge_id}/connections/status`
  - 모든 연결의 상태 조회

#### 생성 (Create)
- **POST** `/bridges/{bridge_id}/connections`
```json
{
    "target_bridge_id": "string",
    "connection_type": "topic|service|action",
    "source": {
        "name": "string",
        "type": "string"
    },
    "target": {
        "name": "string",
        "type": "string"
    },
    "qos_profile": "reliable|best_effort",
    "direction": "bidirectional|source_to_target|target_to_source",
    "filters": {
        "enabled": false,
        "include_patterns": ["string"],
        "exclude_patterns": ["string"]
    },
    "transform": {
        "enabled": false,
        "type": "none|rename|remap",
        "config": {}
    }
}
```

#### 수정 (Update)
- **PUT** `/bridges/{bridge_id}/connections/{connection_id}`
  - 연결 전체 수정
- **PATCH** `/bridges/{bridge_id}/connections/{connection_id}`
  - 연결 부분 수정
- **PATCH** `/bridges/{bridge_id}/connections/{connection_id}/status`
  - 연결 상태 수정 (활성화/비활성화)

#### 삭제 (Delete)
- **DELETE** `/bridges/{bridge_id}/connections/{connection_id}`
  - 연결 삭제

#### 응답 예시
```json
{
    "status": "success",
    "data": {
        "connections": [
            {
                "id": "conn-001",
                "source_bridge_id": "bridge-001",
                "target_bridge_id": "bridge-002",
                "connection_type": "topic",
                "source": {
                    "name": "/chatter",
                    "type": "std_msgs/msg/String"
                },
                "target": {
                    "name": "/chatter_remote",
                    "type": "std_msgs/msg/String"
                },
                "qos_profile": "reliable",
                "direction": "bidirectional",
                "status": "active",
                "stats": {
                    "messages_sent": 1000,
                    "messages_received": 950,
                    "bytes_sent": "1.2MB",
                    "bytes_received": "1.1MB",
                    "latency_ms": 5.2
                },
                "filters": {
                    "enabled": true,
                    "include_patterns": ["/chatter/*"],
                    "exclude_patterns": ["/chatter/debug"]
                },
                "transform": {
                    "enabled": true,
                    "type": "remap",
                    "config": {
                        "field_mappings": {
                            "data": "message"
                        }
                    }
                },
                "created_at": "2024-03-20T10:00:00Z",
                "updated_at": "2024-03-20T10:00:00Z"
            }
        ]
    }
}
```
