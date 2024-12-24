#!/bin/bash

# 스크립트 실행 중 오류 발생 시 종료
set -e

# 매우 중요!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! 
# all node of k8s must be installed nfs provisioner 
# must be set up default storageclass all node of k8s with nfs provisioner 

# 기존 설치된 MongoDB 삭제
#echo "MongoDB 삭제 중..."
#helm uninstall $RELEASE_NAME -n $NAMESPACE

# 변수 설정
NAMESPACE="mongodb"
RELEASE_NAME="gros-mongodb"
CHART_VERSION="15.6.16"  # 사용하려는 MongoDB 차트 버전을 명시
VALUES_YAML="mongo_values.yaml"

# Kubernetes 네임스페이스 생성
echo "Kubernetes 네임스페이스 생성 중..."
kubectl create namespace $NAMESPACE || echo "네임스페이스가 이미 존재합니다."

# MongoDB Helm 리포지토리 추가
echo "MongoDB Helm 리포지토리 추가 중..."
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

# MongoDB 설치
echo "MongoDB 설치 중..."
helm install $RELEASE_NAME bitnami/mongodb --namespace $NAMESPACE --version $CHART_VERSION -f $VALUES_YAML
    
# 설치 완료 메시지
echo "MongoDB가 Helm을 사용하여 Kubernetes 클러스터에 성공적으로 설치되었습니다."
echo "네임스페이스: $NAMESPACE"
echo "릴리즈 이름: $RELEASE_NAME"

# MONGO_NODE_PORT 30017로 변경 
echo "MongoDB nodePort 30017로 변경 중 ..."
kubectl patch svc $RELEASE_NAME -n $NAMESPACE -p '{"spec": {"ports": [{"port": 27017, "nodePort": 30017, "protocol": "TCP"}]}}'
