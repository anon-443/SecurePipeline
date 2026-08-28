# SecurePipeline Demo Runbook

## Demo Objective

Demonstrate that a code change can pass quality and security gates, become a hardened Docker image, run as a Kubernetes workload, and expose operational telemetry.

## Suggested Demonstration Sequence

1. Open the GitHub repository and show the repository layout, README, and green GitHub Actions workflows.
2. Show `application/app.py` and point out `/health`, `/ready`, and `/metrics`.
3. In Ubuntu, run the tests and linting:

```bash
cd ~/SecurePipeline/application
source .venv/bin/activate
pytest -q
ruff check .
```

4. Build and run the container:

```bash
cd ~/SecurePipeline
docker build -f docker/Dockerfile -t securepipeline:0.1.0 .
docker run --rm -d --name securepipeline -p 8080:8080 securepipeline:0.1.0
curl http://127.0.0.1:8080/health
docker exec securepipeline id
docker stop securepipeline
```

5. Load and deploy to Minikube:

```bash
minikube image load securepipeline:0.1.0
sed -i "s#DOCKERHUB_USERNAME/securepipeline:0.1.0#securepipeline:0.1.0#" kubernetes/deployment.yaml
kubectl apply -k kubernetes/
kubectl -n securepipeline rollout status deployment/securepipeline
kubectl -n securepipeline get pods,service,networkpolicy,pdb
```

6. Demonstrate application reachability:

```bash
kubectl -n securepipeline port-forward service/securepipeline 8080:80
```

In a second terminal:

```bash
curl http://127.0.0.1:8080/health
curl http://127.0.0.1:8080/ready
curl http://127.0.0.1:8080/metrics | grep securepipeline_http_requests_total
```

7. Show the Kubernetes security context and probes:

```bash
kubectl -n securepipeline describe deployment securepipeline
kubectl -n securepipeline get networkpolicy -o yaml
```

8. Open the Grafana dashboard after the monitoring stack is installed. Generate several requests through `/health`, then capture request rate, response status, ready pod count, CPU, memory, and logs.

## Evidence Checklist

Capture screenshots of the green CI workflow, green security workflow, passing local tests, non-root container identity, Docker health response, Ready Minikube node, successful rollout, ready pods, service health response, NetworkPolicy, and Grafana dashboard. Avoid showing tokens, private keys, or personal credentials.
