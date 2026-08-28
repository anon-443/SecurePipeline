# SecurePipeline Ubuntu VMware Setup

Run these commands inside the Ubuntu VM terminal. Do not run them in Kali or in the Manus sandbox. First, check the system and existing tools:

```bash
cat /etc/os-release
uname -m
free -h
df -h /
command -v git && git --version || echo "Git is missing"
command -v docker && docker --version || echo "Docker is missing"
command -v kubectl && kubectl version --client || echo "kubectl is missing"
command -v minikube && minikube version || echo "Minikube is missing"
command -v helm && helm version --short || echo "Helm is missing"
```

The VM should ideally have at least 4 CPU cores, 8 GB RAM, and 40 GB free disk space. If VMware allows it, enable virtualization support. These checks are only for information and do not change the system.

## Install Basic Tools

```bash
sudo apt update
sudo apt upgrade -y
sudo apt install -y ca-certificates curl git unzip jq python3 python3-venv
```

## Install Docker Engine

```bash
sudo apt remove -y docker.io docker-doc docker-compose podman-docker containerd runc 2>/dev/null || true
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
printf 'Types: deb\nURIs: https://download.docker.com/linux/ubuntu\nSuites: %s\nComponents: stable\nArchitectures: amd64\nSigned-By: /etc/apt/keyrings/docker.asc\n' "$(. /etc/os-release && echo "$VERSION_CODENAME")" | sudo tee /etc/apt/sources.list.d/docker.sources >/dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo systemctl enable --now docker
sudo usermod -aG docker "$USER"
```

Log out of Ubuntu and log in again so the Docker group change takes effect. Then verify Docker:

```bash
docker run --rm hello-world
docker compose version
```

If Docker gives a permission error before logging out again, use `newgrp docker` once for the current terminal.

## Install kubectl

```bash
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.34/deb/Release.key | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg
sudo chmod 644 /etc/apt/keyrings/kubernetes-apt-keyring.gpg
printf 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.34/deb/ /\n' | sudo tee /etc/apt/sources.list.d/kubernetes.list >/dev/null
sudo apt update
sudo apt install -y kubectl
kubectl version --client
```

## Install Minikube

```bash
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube
rm minikube-linux-amd64
minikube version
```

## Start the Local Kubernetes Cluster

```bash
minikube start --driver=docker --cpus=3 --memory=4096
kubectl get nodes
kubectl get pods -A
```

The expected node status is `Ready`. If the VM has less memory, use `--memory=3072`, but monitoring tools may need more memory.

## Clone SecurePipeline

```bash
cd "$HOME"
git clone https://github.com/anon-443/SecurePipeline.git
cd SecurePipeline
git status
```

## Run the Application Directly

```bash
cd application
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
pytest -q
ruff check .
python app.py
```

Open another terminal and test the running application:

```bash
curl http://127.0.0.1:8080/health
curl http://127.0.0.1:8080/ready
curl http://127.0.0.1:8080/metrics | head
```

Stop the development server with `Ctrl+C`.

## Build and Run the Container

From the repository root:

```bash
cd "$HOME/SecurePipeline"
docker build -f docker/Dockerfile -t securepipeline:0.1.0 .
docker run --rm -d --name securepipeline -p 8080:8080 securepipeline:0.1.0
curl http://127.0.0.1:8080/health
docker exec securepipeline id
docker stop securepipeline
```

The `docker exec` output should show the non-root `appuser` rather than root.

## Load the Image into Minikube

```bash
cd "$HOME/SecurePipeline"
minikube image load securepipeline:0.1.0
sed -i "s#DOCKERHUB_USERNAME/securepipeline:0.1.0#securepipeline:0.1.0#" kubernetes/deployment.yaml
kubectl apply -k kubernetes/
kubectl -n securepipeline rollout status deployment/securepipeline
kubectl -n securepipeline get pods,service
kubectl -n securepipeline port-forward service/securepipeline 8080:80
```

In another terminal, test the Kubernetes service:

```bash
curl http://127.0.0.1:8080/health
```

When finished with port forwarding, press `Ctrl+C`. To stop the cluster without deleting it, use `minikube stop`.
