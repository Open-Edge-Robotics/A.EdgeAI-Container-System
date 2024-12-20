# 호스트 이름 변경
```shell
hostnamectl set-hostname gedge-master
```

# 포트 확인
```shell
netstat -tulpn | grep "6443\|2379\|2380\|10250\|10259\|10257"
netstat -tulpn | grep "10250"
```

# 방화벽 off
```shell
ufw disable
```

# 패키지 업그레이드
```shell
apt update
apt -y full-upgrade
```

# 시간 동기화

```shell
apt install systemd-timesyncd
timedatectl set-ntp true
timedatectl status
```

# 메모리 스왑 off

```shell
swapoff -a
sed -i.bak -r 's/(.+ swap .+)/#\1/' /etc/fstab
```

# 모듈 추가
```shell
vi /etc/modules-load.d/k8s.conf
overlay
br_netfilter

modprobe overlay
modprobe br_netfilter
```

# 커널 매개변수 설정
```shell
vi /etc/sysctl.d/k8s.conf

net.bridge.bridge-nf-call-ip6tables = 1
net.bridge.bridge-nf-call-iptables = 1
net.ipv4.ip_forward = 1
sysctl --system
```

# Kubernetes v1.28 설치
```shell
apt-get install -y apt-transport-https ca-certificates curl gpg gnupg2 software-properties-common

curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.28/deb/Release.key | \
  sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg

echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.28/deb/ /' | \
  sudo tee /etc/apt/sources.list.d/kubernetes.list


apt update
apt-get install -y kubelet kubeadm kubectl
apt-mark hold kubelet kubeadm kubectl
```


# 도커 설치
```shell
for pkg in docker.io docker-doc docker-compose docker-compose-v2 podman-docker containerd runc; do sudo apt-get remove $pkg; done

sudo apt-get update
sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc


echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update


sudo apt-get -y install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

# containerd 설정
```shell
sudo mkdir -p /etc/containerd

sudo containerd config default|sudo tee /etc/containerd/config.toml


vi  /etc/containerd/config.toml
```
```ini
[plugins."io.containerd.grpc.v1.cri".containerd.runtimes.runc]
  runtime_type = "io.containerd.runc.v2"  # <- note this, this line might have been missed
  [plugins."io.containerd.grpc.v1.cri".containerd.runtimes.runc.options]
    SystemdCgroup = true # <- note this, this could be set as false in the default configuration, please make it true
```
```shell
sudo systemctl restart containerd
sudo systemctl enable containerd
systemctl status containerd
```

# crictl 설정

```shell
crictl ps
apt install cri-tools

vi /etc/crictl.yaml
```
```ini
runtime-endpoint: unix:///run/containerd/containerd.sock
image-endpoint: unix:///run/containerd/containerd.sock
timeout: 2
debug: true # <- if you don't want to see debug info you can set this to false
pull-image-on-create: false
```
```shell
crictl ps
```

# Kubnernetes Image pull
```shell
systemctl enable kubelet
kubeadm config images pull --cri-socket unix:///var/run/containerd/containerd.sock

crictl images
```

# Kubnernetes 마스터 설치
```shell
sudo kubeadm init \
  --pod-network-cidr=10.244.0.0/16 \
  --cri-socket unix:///var/run/containerd/containerd.sock \
  --v=5

mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config
```


# Weavnet 설치
```shell
kubectl apply -f https://github.com/weaveworks/weave/releases/download/v2.8.1/weave-daemonset-k8s.yaml

crictl ps
```


# Kubnernetes 슬레이브 설치
```shell
kubeadm join 192.168.241.133:6443 --token lduq5i.5dq9sluuicnci02y --discovery-token-ca-cert-hash sha256:4d3f6c4a3abd7c2f8aba79eaa45c8b7e158252ed54a5ba8c37abceafca089bb5 --cri-socket unix:///var/run/containerd/containerd.sock
```

# token 생성(추후)
```shell
kubeadm token create --print-join-command
```