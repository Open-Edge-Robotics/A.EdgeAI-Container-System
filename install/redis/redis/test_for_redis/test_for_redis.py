import redis

# Redis 마스터 서비스에 연결 (Node IP와 NodePort 사용)
redis_host = "129.254.202.111"  # Node의 IP 주소
redis_port = 30079           # Redis NodePort
redis_password = "gr1324"  # Redis 비밀번호

# Redis 클라이언트 생성
client = redis.StrictRedis(host=redis_host, port=redis_port, password=redis_password, decode_responses=True)

# 데이터 쓰기
client.set("mykey", "Hello, Redis!")

# 데이터 읽기
value = client.get("mykey")
print(f"The value of 'mykey' is: {value}")
