# ROS2
## 기본 명령어
- 토픽 리스트

```sh
ros2 topic list
ros2 topic list -t
```

- 토픽 송신

```sh
ros2 topic pub <topic_name> <msg_type> '<args>'

ros2 topic pub /test std_msgs/String "data: test1234"

- 토픽 수신
```sh
ros2 topic echo <topic_name>

ros2 topic echo /test
```

- 토픽 정보

```sh
ros2 topic info /test

Type: std_msgs/msg/String
Publisher count: 0
Subscription count: 2
```

- 토픽 인터페이스 리스트
```sh
ros2 interface list
```

- 토픽 msg 리스트
```sh
ros2 interface list -m
```


- 메시지 타입 확인
```sh
ros2 interface show  std_msgs/msg/String

# This was originally provided as an example message.
# It is deprecated as of Foxy
# It is recommended to create your own semantically meaningful message.
# However if you would like to continue using this please use the equivalent in example_msgs.

string data
```

- 토픽 hz

```sh
ros2 topic hz /test
```
