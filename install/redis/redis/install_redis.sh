RELEASE_NAME="gros-redis"
VALUES_YAML="redis_values.yaml"
NAMESPACE="redis"

# Kubernetes 네임스페이스 생성
echo "Kubernetes 네임스페이스 생성 중..."
kubectl create namespace $NAMESPACE || echo "네임스페이스가 이미 존재합니다."

# Helm 리포지토리 for redis 추가
echo "Helm 리포지토리 for redis 추가 중"
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

# redis 설치
echo "redis 설치 중..."
helm install $RELEASE_NAME bitnami/redis -n $NAMESPACE -f $VALUES_YAML