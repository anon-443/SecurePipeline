# SecurePipeline

SecurePipeline is an enterprise-style DevSecOps deployment platform created for the TechSkillHub DevOps Engineer Internship. It demonstrates how source control, automated testing, security validation, containerization, Kubernetes deployment, monitoring, and centralized logging work together in a production-oriented delivery process.

## Current Status

The first milestone contains a small production-style Flask service with health checks, a readiness probe, Prometheus-compatible metrics, automated tests, and a secure multi-stage Docker build. CI/CD, security scanning, Kubernetes, monitoring, and logging will be added in the following milestones.

## Architecture Direction

```text
Developer
   |
   v
GitHub Pull Request --> GitHub Actions
                            |
              +-------------+-------------+
              |                           |
         Tests and linting          Security scans
              |                           |
              +-------------+-------------+
                            |
                    Docker image build
                            |
                        Docker Hub
                            |
                       Kubernetes
                    /       |        \
              Service    Ingress    Probes
                            |
                Prometheus / Grafana / Loki
```

## Repository Layout

| Directory | Purpose |
|---|---|
| `application/` | Flask service, dependencies, and automated tests |
| `docker/` | Optimized production Docker build files |
| `kubernetes/` | Deployment, Service, Ingress, security, and policy manifests |
| `security/` | Security scanner configuration and generated reports |
| `monitoring/` | Prometheus, Grafana, Loki, and Promtail configuration |
| `documentation/` | Architecture diagrams, deployment guide, and final report material |
| `.github/workflows/` | CI/CD workflow definitions |

## Run Locally

```bash
cd application
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
python app.py
```

The service is available at `http://localhost:8080`. Useful endpoints are `/`, `/health`, `/ready`, and `/metrics`.

## Run Tests

```bash
cd application
source .venv/bin/activate
pytest -q
ruff check .
```

## Build and Run with Docker

```bash
docker build -f docker/Dockerfile -t securepipeline:0.1.0 .
docker run --rm -p 8080:8080 securepipeline:0.1.0
```

## Delivery Roadmap

The project will be completed in stages: establish the repository and application baseline; add automated tests, linting, Docker publishing, and security gates; deploy the service to Kubernetes with least-privilege controls and network policies; add observability with Prometheus, Grafana, Loki, and Promtail; then finalize the deployment guide, architecture diagrams, engineering report, presentation, and demonstration video.

## Security Principles

The platform will keep secrets outside source control, use immutable image tags, run containers as non-root users, scan dependencies and images before release, apply Kubernetes least privilege, expose only required network paths, and provide health checks for safe rollout and rollback.
