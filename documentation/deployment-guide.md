# SecurePipeline Deployment Guide

## Environment

The project is designed for Ubuntu 24.04 on a VMware Workstation guest with Docker Engine, kubectl, and Minikube. The tested local cluster uses the Docker driver, two CPU cores, 3 GB memory, and a 20 GB Minikube disk allocation. This profile is appropriate for the application demonstration; the full observability stack may require additional memory or selective installation.

## Repository Setup

Clone the repository with GitHub CLI authentication because the repository is private:

```bash
gh auth login
gh repo clone anon-443/SecurePipeline "$HOME/SecurePipeline"
cd "$HOME/SecurePipeline"
```

Never place a GitHub password, personal access token, Docker Hub token, TLS private key, or `.env` file in the repository.

## Local Application

```bash
cd "$HOME/SecurePipeline/application"
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
pytest -q
ruff check .
python app.py
```

In another terminal, verify the service:

```bash
curl http://127.0.0.1:8080/health
curl http://127.0.0.1:8080/ready
curl http://127.0.0.1:8080/metrics
```

## Docker

```bash
cd "$HOME/SecurePipeline"
docker build -f docker/Dockerfile -t securepipeline:0.1.0 .
docker run --rm -d --name securepipeline -p 8080:8080 securepipeline:0.1.0
curl http://127.0.0.1:8080/health
docker exec securepipeline id
docker stop securepipeline
```

The container should run as `appuser`. The Dockerfile uses a multi-stage build, a read-only runtime filesystem, a health check, Gunicorn, and configurable environment variables.

## Minikube Deployment

Start Minikube using the resource profile appropriate for the VMware guest:

```bash
minikube start --driver=docker --cpus=2 --memory=3072 --disk-size=20g
kubectl get nodes
```

Load the local image and adjust the image reference for the local demonstration:

```bash
cd "$HOME/SecurePipeline"
minikube image load securepipeline:0.1.0
sed -i "s#DOCKERHUB_USERNAME/securepipeline:0.1.0#securepipeline:0.1.0#" kubernetes/deployment.yaml
kubectl apply -k kubernetes/
kubectl -n securepipeline rollout status deployment/securepipeline
kubectl -n securepipeline get pods,service,ingress,networkpolicy,pdb
```

Access the service locally:

```bash
kubectl -n securepipeline port-forward service/securepipeline 8080:80
```

From a second terminal:

```bash
curl http://127.0.0.1:8080/health
curl http://127.0.0.1:8080/ready
```

## Monitoring

Prometheus should scrape the application’s `/metrics` endpoint using `monitoring/prometheus.yml`. Grafana can import `monitoring/grafana-dashboard.json`. Loki and Promtail are the centralized log collection path. Install these components through pinned, organization-approved Helm charts and keep the values files under version control after reviewing them for secrets.

## Troubleshooting

If `kubectl` reports that `localhost:8080` was refused, Minikube is not running or the current context is wrong. Run `minikube status`, `minikube start`, and `kubectl config current-context`. If the deployment remains pending, inspect `kubectl -n securepipeline describe pod` and verify that the image was loaded into Minikube. If a port is already in use, stop the old port-forward or choose another local port such as `8081:80`. If the VM becomes low on disk, remove unused images with `docker image prune` only after reviewing the list, and stop Minikube with `minikube stop` when it is not needed.
