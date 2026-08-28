# SecurePipeline — Detailed AI Handoff Document

## Purpose of This Document

This document is a complete handoff for any AI assistant that continues working on the SecurePipeline internship project. The next AI should read this document before making changes. It records what the project is, what has already been implemented, what was tested, what remains unfinished, the user’s Ubuntu environment, known issues, and the safest exact continuation path.

> Do not assume that the full internship has been completed. The repository foundation is strong and the automated CI/security workflows are green, but the actual application deployment and monitoring evidence still need to be completed on the user’s Ubuntu VMware VM.

## User and Internship Context

The user is **Adeen Shahzad**, intern ID **TSH/4515CF1B**, participating in the TechSkillHub **DevOps Engineer Virtual Internship**. The internship is one month long, from **05 August 2026 to 05 September 2026**, and is conducted remotely. The task assignment is titled **SecurePipeline — Enterprise DevSecOps Deployment Platform**.

The assignment requires a production-oriented web application delivery platform that automates source management, build and testing, security scanning, Docker image creation, Kubernetes deployment, monitoring, logging, and security validation before release. The required technology areas are Ubuntu Linux, Git, GitHub Actions, Docker, Kubernetes, Trivy, OWASP Dependency-Check, Prometheus, Grafana, Loki, and Promtail.

The expected final deliverables are the GitHub repository, application source code, Dockerfiles, Kubernetes YAML files, CI/CD workflows, security scan reports, monitoring dashboard screenshots, architecture diagrams, deployment guide, engineering report, presentation, demo video, and README documentation.

## Repository and Ownership

The repository is private and is located at:

`https://github.com/anon-443/SecurePipeline`

The local development copy used by the previous AI is:

`/home/ubuntu/SecurePipeline`

The previous AI created and pushed the repository using GitHub CLI. Do not create another repository. Continue using the existing `main` branch unless the user requests a branching strategy or pull-request workflow.

The most recent repository commit at the time of this handoff is:

`2c057bd docs: add GitHub Pages dashboard and final project materials`

The repository was clean after that commit. A ZIP archive was created at:

`/home/ubuntu/SecurePipeline-complete.zip`

The ZIP was tested with `unzip -t` and returned `No errors detected in compressed data`.

## Current Repository Structure

```text
SecurePipeline/
├── .dockerignore
├── .gitignore
├── .github/
│   └── workflows/
│       ├── ci.yml
│       ├── pages.yml
│       ├── publish.yml
│       └── security.yml
├── README.md
├── UBUNTU_SETUP.md
├── application/
│   ├── app.py
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   └── tests/
│       └── test_app.py
├── docker/
│   ├── .dockerignore
│   └── Dockerfile
├── docs/
│   ├── .nojekyll
│   ├── README.md
│   ├── index.html
│   └── styles.css
├── documentation/
│   ├── architecture.mmd
│   ├── architecture.png
│   ├── demo-runbook.md
│   ├── deployment-guide.md
│   ├── engineering-report.md
│   └── presentation-outline.md
├── kubernetes/
│   ├── README.md
│   ├── deployment.yaml
│   ├── kustomization.yaml
│   ├── namespace-config.yaml
│   ├── networking.yaml
│   └── security-policies.yaml
├── monitoring/
│   ├── README.md
│   ├── grafana-dashboard.json
│   └── prometheus.yml
└── security/
    └── README.md
```

## What Has Been Implemented

### Application

`application/app.py` contains a Flask service called SecurePipeline. The service supports the following endpoints:

| Endpoint | Purpose |
|---|---|
| `/` | Returns service name, version, environment, and a running message |
| `/health` | Liveness-style health response with HTTP 200 |
| `/ready` | Readiness response with an UTC timestamp |
| `/metrics` | Prometheus-compatible request counter output |
| Unknown paths | JSON 404 response |

The application uses environment variables for `APP_VERSION`, `APP_ENVIRONMENT`, `APP_BIND_HOST`, and `PORT`. Local execution defaults to `127.0.0.1`; the Docker image sets `APP_BIND_HOST=0.0.0.0` for container networking. The request counter is named `securepipeline_http_requests_total` and is labelled by endpoint, method, and status.

### Automated Tests and Linting

`application/tests/test_app.py` contains five tests covering the root endpoint, health endpoint, readiness endpoint, metrics endpoint, and JSON 404 handling. The development requirements include pytest and Ruff. Local validation in the previous sandbox passed:

```text
5 passed
All checks passed!
```

The normal commands are:

```bash
cd ~/SecurePipeline/application
source .venv/bin/activate
pytest -q
ruff check .
```

### Docker

`docker/Dockerfile` uses a Python 3.12 slim multi-stage build. The builder creates a virtual environment and installs the application dependencies. The runtime stage creates an `appuser`, runs as that non-root user, exposes port 8080, uses Gunicorn with two workers and four threads, and defines a Docker health check against `/health`.

The runtime security controls include a non-root user, a small runtime layer, current Debian package updates, removal of unused packaging artifacts, environment-configurable bind host, and no development test dependencies in the runtime image.

The standard commands are:

```bash
cd ~/SecurePipeline
docker build -f docker/Dockerfile -t securepipeline:0.1.0 .
docker run --rm -d --name securepipeline -p 8080:8080 securepipeline:0.1.0
curl http://127.0.0.1:8080/health
docker exec securepipeline id
docker stop securepipeline
```

The expected container identity should show `appuser` and not root.

### CI Workflow

`.github/workflows/ci.yml` runs on pushes and pull requests targeting `main`. It performs the following stages:

1. Checks out source code.
2. Installs Python 3.12.
3. Installs development dependencies.
4. Runs Ruff.
5. Runs pytest.
6. Builds the Docker image after quality checks pass.
7. Inspects image user and exposed port metadata.

The latest verified CI workflow for commit `2c057bd` passed successfully. GitHub Actions run ID: `33137981183`.

### Security Workflow

`.github/workflows/security.yml` runs three security controls:

| Security control | Implementation |
|---|---|
| SAST | Bandit scans `application/app.py` and stores JSON report artifact |
| Dependency analysis | OWASP Dependency-Check scans the declared Python requirements and stores HTML report artifact |
| Image scanning | Trivy scans the built image for HIGH and CRITICAL vulnerabilities and stores SARIF artifact |

The Trivy action was updated to the verified `aquasecurity/trivy-action@v0.36.0` release. The Code Scanning SARIF upload step was removed because the repository token returned a 403 due to missing checks permission; the Trivy SARIF report is still preserved as a workflow artifact and the Trivy scan itself remains blocking.

The latest verified security workflow for commit `2c057bd` passed successfully. GitHub Actions run ID: `33137981172`.

Earlier security failures were fixed rather than hidden. Bandit initially reported pytest assertions, so the production scan was scoped to `app.py`. Bandit then correctly found binding to all interfaces in the local entry point, which was fixed by making the bind host configurable. Trivy found base-image and Python packaging vulnerabilities; the Dockerfile and dependencies were hardened, and the final Trivy run passed.

### Docker Hub Publishing Workflow

`.github/workflows/publish.yml` publishes the image on semantic version tags such as `v1.0.0` or by manual dispatch. It uses the GitHub Actions secrets `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN`, creates SHA and version tags, and only enables the `latest` tag for version-tagged releases.

These Docker Hub secrets have **not** been configured or tested. Never ask the user to paste a Docker Hub token into chat. The user should add it privately in GitHub repository settings if Docker Hub publishing is needed.

### Kubernetes Manifests

The `kubernetes/` directory contains a Kustomize bundle with:

| Manifest capability | Implementation |
|---|---|
| Namespace | Dedicated `securepipeline` namespace |
| Pod Security Admission | Restricted labels on the namespace |
| Deployment | Two replicas and a rolling update strategy |
| Container probes | Startup, readiness, and liveness probes |
| Resources | CPU and memory requests and limits |
| Runtime security | Non-root, RuntimeDefault seccomp, dropped capabilities, no privilege escalation, read-only filesystem |
| Service | Internal ClusterIP service on port 80 to container port 8080 |
| Ingress | NGINX Ingress with HTTPS/TLS placeholder configuration |
| RBAC | Service account, Role, and RoleBinding with minimal ConfigMap read permission |
| Network policy | Default deny with explicit ingress and DNS egress exceptions |
| Disruption safety | PodDisruptionBudget requiring one available replica |
| Packaging | `kustomization.yaml` entry point |

The deployment image currently contains a placeholder:

`DOCKERHUB_USERNAME/securepipeline:0.1.0`

For a local Minikube demonstration, it must be changed to:

`securepipeline:0.1.0`

The local deployment process is:

```bash
cd ~/SecurePipeline
minikube image load securepipeline:0.1.0
sed -i "s#DOCKERHUB_USERNAME/securepipeline:0.1.0#securepipeline:0.1.0#" kubernetes/deployment.yaml
kubectl apply -k kubernetes/
kubectl -n securepipeline rollout status deployment/securepipeline
kubectl -n securepipeline get pods,service,networkpolicy,pdb
```

The TLS secret in the Ingress is intentionally not created in the repository. For local testing, use port forwarding instead of Ingress:

```bash
kubectl -n securepipeline port-forward service/securepipeline 8080:80
```

Then, from another terminal:

```bash
curl http://127.0.0.1:8080/health
curl http://127.0.0.1:8080/ready
curl http://127.0.0.1:8080/metrics
```

### Monitoring and Logging

`monitoring/prometheus.yml` configures Kubernetes endpoint discovery for the `securepipeline` namespace and scrapes the application’s `/metrics` endpoint. `monitoring/grafana-dashboard.json` defines panels for request rate, response status, ready pod count, CPU usage, and memory usage.

The repository documents Loki and Promtail as the centralized logging layer, but they have **not yet been installed or verified** in the user’s Minikube cluster. Monitoring screenshots have also not yet been captured. The user’s VM has only two CPU cores, so the monitoring stack should be installed selectively and only after the application is stable.

### GitHub Pages Dashboard

The `docs/` directory contains a static, dependency-free HTML/CSS dashboard. It presents the project architecture, pipeline stages, operational controls, security posture, and links to the repository and deployment guide. It is designed for GitHub Pages.

`.github/workflows/pages.yml` uploads the `docs/` directory and deploys it through GitHub Pages. The latest Pages run for commit `2c057bd` failed at `actions/configure-pages@v5` because the repository Pages site was not enabled/configured:

```text
Get Pages site failed. Please verify that the repository has Pages enabled and configured to build using GitHub Actions
```

GitHub Actions run ID: `33137981143`.

This is a repository settings issue, not an HTML/CSS failure. The user must open **GitHub repository → Settings → Pages**, set the source to **GitHub Actions**, and rerun the Pages workflow. The expected URL is:

`https://anon-443.github.io/SecurePipeline/`

GitHub Pages hosts the dashboard only. It cannot run Flask, Docker, Kubernetes, Prometheus, Grafana, Loki, or Promtail.

### Documentation and Evidence Materials

The repository includes:

- `documentation/architecture.mmd`: Mermaid architecture source.
- `documentation/architecture.png`: rendered architecture diagram.
- `documentation/engineering-report.md`: engineering report draft.
- `documentation/deployment-guide.md`: deployment and troubleshooting guide.
- `documentation/demo-runbook.md`: demonstration sequence and evidence checklist.
- `documentation/presentation-outline.md`: twelve-slide presentation outline.
- `UBUNTU_SETUP.md`: beginner-friendly Ubuntu VMware setup instructions.
- `security/README.md`: security policy and required GitHub secrets.
- `kubernetes/README.md`: Kubernetes deployment instructions.
- `monitoring/README.md`: monitoring and logging plan.

## User’s Ubuntu VMware Environment

The user’s environment is Ubuntu running inside VMware Workstation. The key facts are:

| Item | Current state |
|---|---|
| OS | Ubuntu 24.04.4 LTS |
| Architecture | x86_64 |
| CPU | 2 virtual CPUs |
| Memory | Approximately 8.3 GB |
| Root disk | 59 GB total |
| Free space after cleanup | Approximately 33 GB |
| Docker | Docker 29.7.2, active and working |
| Compose | Docker Compose v5.5.0 |
| kubectl | Client v1.34.11 |
| Minikube | v1.38.1 |
| Kubernetes cluster | Minikube node Ready, Kubernetes v1.35.1 |
| Minikube profile | Docker driver, 2 CPUs, 3072 MB memory, 20 GB disk |

The disk originally had only about 814 MB free. Safe cleanup removed the unused Nessus installation from `/opt/nessus`, which used approximately 9.9 GB, and an old Linux kernel build directory at `~/build/kernel`, which used approximately 22 GB. The user now has enough space for the application and local Kubernetes cluster.

The user’s successful Minikube command was:

```bash
minikube start --driver=docker --cpus=2 --memory=3072 --disk-size=20g
```

The Minikube output confirmed:

```text
minikube   Ready   control-plane   v1.35.1
host: Running
kubelet: Running
apiserver: Running
```

The user’s normal system is resource-constrained. Do not request three CPUs; Minikube previously failed because the VM only has two CPUs. Use two CPUs and approximately 3 GB Minikube memory. Do not install the full observability stack until the core application is deployed and the VM’s remaining disk and memory are checked.

## Current Blocker

The user attempted to clone the private repository from the Ubuntu VM over HTTPS. GitHub requested a username and password. The user does not remember the GitHub password, and a browser/device login attempt later showed a 404. The normal GitHub password must not be used for Git HTTPS operations.

The repository is private, so the Ubuntu VM needs an authenticated GitHub session. The safest continuation is GitHub CLI browser authentication:

```bash
sudo apt update
sudo apt install -y gh
gh auth logout -h github.com
gh auth login -h github.com -p https -w
```

The user should select GitHub.com, HTTPS, authenticate Git, and “Login with a web browser.” They should open the exact one-time URL and enter the one-time code locally. They must not send the code, password, or token to an AI assistant.

Then verify access:

```bash
gh auth status
gh repo view anon-443/SecurePipeline
```

If `gh repo view` returns 404, the Ubuntu VM is authenticated to a different GitHub account or that account does not have access to the private repository. The user must complete login with the GitHub account that owns or can access `anon-443/SecurePipeline`. Do not create another repository and do not expose the repository publicly just to bypass login.

After access works, clone:

```bash
cd "$HOME"
rm -rf -- "$HOME/SecurePipeline"  # only if this is the incomplete failed clone

gh repo clone anon-443/SecurePipeline "$HOME/SecurePipeline"
cd "$HOME/SecurePipeline"
git status
```

If the user has a valid complete local clone already, do not delete it; use `git pull` instead.

## Exact Next Steps for a Continuing AI

The next AI should proceed in this order:

### Step 1: Resolve private repository access

Help the user complete `gh auth login` and verify `gh repo view anon-443/SecurePipeline`. Do not request credentials in chat.

### Step 2: Clone and run local tests

```bash
cd "$HOME/SecurePipeline/application"
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
pytest -q
ruff check .
```

Expected result: five tests pass and Ruff has no errors.

### Step 3: Build and test the Docker image

```bash
cd "$HOME/SecurePipeline"
docker build -f docker/Dockerfile -t securepipeline:0.1.0 .
docker run --rm -d --name securepipeline -p 8080:8080 securepipeline:0.1.0
curl http://127.0.0.1:8080/health
docker exec securepipeline id
docker stop securepipeline
```

Expected result: health JSON returns a healthy status and `docker exec ... id` shows the non-root application user.

### Step 4: Deploy to Minikube

```bash
cd "$HOME/SecurePipeline"
minikube status
minikube image load securepipeline:0.1.0
sed -i "s#DOCKERHUB_USERNAME/securepipeline:0.1.0#securepipeline:0.1.0#" kubernetes/deployment.yaml
kubectl apply -k kubernetes/
kubectl -n securepipeline rollout status deployment/securepipeline
kubectl -n securepipeline get pods,service,networkpolicy,pdb
```

If Kubernetes reports an image pull problem, inspect:

```bash
kubectl -n securepipeline describe pod
kubectl -n securepipeline get events --sort-by=.lastTimestamp
```

### Step 5: Test Kubernetes service reachability

Use one terminal for port forwarding:

```bash
kubectl -n securepipeline port-forward service/securepipeline 8080:80
```

Use a second terminal for testing:

```bash
curl http://127.0.0.1:8080/health
curl http://127.0.0.1:8080/ready
curl http://127.0.0.1:8080/metrics | grep securepipeline_http_requests_total
```

### Step 6: Verify security posture

```bash
kubectl -n securepipeline get deployment securepipeline -o yaml
kubectl -n securepipeline get networkpolicy -o yaml
kubectl -n securepipeline get pods -o wide
```

Look for two ready replicas, non-root settings, probes, resource requests/limits, and the default-deny NetworkPolicy.

### Step 7: Configure observability selectively

Only after the application is stable, install a resource-appropriate Prometheus/Grafana stack. Loki and Promtail may need to be installed separately or omitted from the constrained VM if resources are insufficient. Capture screenshots of dashboards showing real requests generated through `/health` and `/ready`.

### Step 8: Enable GitHub Pages

The user must enable GitHub Pages using GitHub Actions in repository settings. Then rerun the `Deploy SecurePipeline Dashboard` workflow. Verify the expected dashboard URL and capture a screenshot.

### Step 9: Complete evidence and final submission

Collect screenshots or logs for passing local tests, Docker health, non-root image identity, Ready Minikube node, successful rollout, ready pods, service health response, security context, NetworkPolicy, security reports, and Grafana dashboard panels. Update the engineering report with actual observed results rather than claiming unverified deployment. Prepare the presentation from `documentation/presentation-outline.md` and record a five-to-ten-minute demo using `documentation/demo-runbook.md`.

## Do Not Do These Things

Do not use Kali Linux as the documented primary environment because the internship assignment specifies Ubuntu Linux. Do not delete the Ubuntu VM; it has already been cleaned and configured. Do not delete `/usr`, `/var`, `/opt`, `/lib`, `/bin`, or swap files blindly. Do not force-delete GitHub credentials, Docker Hub tokens, TLS keys, or Kubernetes secrets. Do not commit secrets to GitHub. Do not claim that GitHub Pages runs the backend. Do not claim that Kubernetes or monitoring has been verified until the user runs the commands in the Ubuntu VM.

Do not overwrite the existing repository with a new scaffold. Continue from the existing files and commits. Do not add heavy tools such as Nessus; Trivy and OWASP Dependency-Check satisfy the assignment’s security requirements.

## Definition of Done

The project is fully ready for internship submission when the repository is clean and pushed, GitHub CI and security workflows are green, the user’s Ubuntu VM can clone the repository, local tests and linting pass, the Docker image builds and runs as a non-root service, Minikube shows a Ready node, the Kubernetes deployment rolls out with two ready replicas, port forwarding reaches the health endpoint, Prometheus receives the request counter, Grafana displays real metrics, centralized logging is demonstrated if resources allow, GitHub Pages serves the static dashboard, and the report, presentation, and demo evidence are updated with real screenshots and logs.

## Handoff Summary

The previous AI completed the repository foundation, hardened the Docker and security workflows through iterative fixes, created the Kubernetes and monitoring configuration, built a professional GitHub Pages dashboard, rendered the architecture diagram, wrote the deployment/report/demo materials, pushed everything to GitHub, and created a valid ZIP archive. The user completed Ubuntu cleanup, Docker installation, kubectl installation, and Minikube startup. The remaining critical work is authenticating the Ubuntu VM to the private repository, running the code locally, deploying to Minikube, installing or selectively configuring observability, enabling GitHub Pages, and collecting final evidence.
