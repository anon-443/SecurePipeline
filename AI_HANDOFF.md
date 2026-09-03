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


## Complete Ubuntu VMware Setup Procedure

This section is written for a beginner or another AI assisting the user from the beginning.

### 1. VMware and Ubuntu Requirements

Use Ubuntu because the internship assignment explicitly names Ubuntu Linux. Kali Linux is not the documented primary environment for this project. VMware Workstation is acceptable for the internship demonstration.

The user’s existing Ubuntu VM initially had a 59 GB root disk with only 814 MB free. It was safely cleaned without reinstalling the operating system. The cleanup removed an unused Nessus installation and an old Linux kernel build directory. The VM now has approximately 33 GB free.

If a fresh VM is ever required, use an Ubuntu 24.04 LTS 64-bit ISO, allocate at least 80 GB as a dynamically growing virtual disk, assign approximately 8 GB RAM, assign two to four CPUs depending on the host, and use NAT networking. The current user’s VM has two CPUs, so Kubernetes commands must use two CPUs.

### 2. Check the Ubuntu System

Open Terminal and run:

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

The expected architecture is `x86_64`. Before installing Docker or Kubernetes, keep at least 15–20 GB free. If disk space is low, inspect the largest directories with `Disk Usage Analyzer` or, from Terminal, use:

```bash
du -xhd1 "$HOME" 2>/dev/null | sort -h
sudo du -xhd1 /opt /var 2>/dev/null | sort -h
```

Never blindly delete `/usr`, `/bin`, `/lib`, `/boot`, `/var`, `/opt`, or swap files. Inspect their contents first.

### 3. Safe Disk Cleanup

The following commands remove package cache, old system journal entries, user cache, Trash contents, and unused packages:

```bash
sudo apt clean
sudo journalctl --vacuum-time=7d
rm -rf ~/.cache/*
gio trash --empty
sudo apt autoremove --purge -y
df -h /
```

For this VM, the largest unnecessary items were identified before deletion. Nessus was removed with:

```bash
sudo systemctl stop nessusd 2>/dev/null || true
sudo systemctl disable nessusd 2>/dev/null || true
sudo apt purge -y 'nessus*' 'nessusagent*' 'nessuscli*' 2>/dev/null || true
sudo rm -rf /opt/nessus
sudo rm -rf /etc/nessus /var/lib/nessus /var/log/nessus
df -h /
```

An old kernel build directory was removed only after confirming it contained generated build artifacts and was not an active kernel project:

```bash
rm -rf -- "$HOME/build/kernel"
df -h /
```

This recovered the VM from 99% full to approximately 43% used, with 33 GB available.

### 4. Repair the Package Manager and Install Basic Tools

If an earlier update was interrupted, repair it before installing anything else:

```bash
sudo dpkg --configure -a
sudo apt --fix-broken install -y
sudo apt update
sudo apt install -y ca-certificates curl git unzip jq python3 python3-venv gnupg
```

Verify:

```bash
git --version
python3 --version
df -h /
```

The user’s verified result was Git 2.43.0, Python 3.12.3, and 33 GB free.

If Ubuntu shows `unattended-upgrade in progress during shutdown`, do not immediately force power off. The shutdown service may take up to 30 minutes. Press Esc once to see progress and wait while the timer advances. If the system remains genuinely unchanged after approximately 45–60 minutes, try VMware **VM → Power → Restart Guest**. Use forced power-off only as a last resort. After reboot, repair with `sudo dpkg --configure -a` and `sudo apt --fix-broken install -y`.

### 5. Install Docker Engine

Use Docker’s official Ubuntu repository. Remove conflicting packages, add the repository key, install Docker Engine and Compose, and enable the service:

```bash
sudo dpkg --configure -a
sudo apt --fix-broken install -y
sudo apt update
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

Start a new shell group session and verify:

```bash
newgrp docker
docker --version
docker compose version
sudo systemctl is-active docker
docker run --rm hello-world
```

The user verified Docker 29.7.2, Docker Compose v5.5.0, an active Docker service, and the successful `Hello from Docker!` container.

### 6. Install kubectl

The user installed kubectl from the Kubernetes stable v1.34 repository:

```bash
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.34/deb/Release.key | sudo gpg --dearmor --yes -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg
sudo chmod 644 /etc/apt/keyrings/kubernetes-apt-keyring.gpg
printf 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.34/deb/ /\n' | sudo tee /etc/apt/sources.list.d/kubernetes.list >/dev/null
sudo apt update
sudo apt install -y kubectl
kubectl version --client
```

### 7. Install and Start Minikube

Install Minikube:

```bash
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube
rm minikube-linux-amd64
minikube version
```

The user’s VMware VM has two CPUs. Start Minikube with a resource profile that fits the VM:

```bash
minikube start --driver=docker --cpus=2 --memory=3072 --disk-size=20g
kubectl get nodes
kubectl get pods -A
minikube status
```

The verified result was a `minikube` control-plane node in `Ready` state, Kubernetes v1.35.1, and running kubelet and API server. Do not request three CPUs on this VM.

### 8. Authenticate and Clone the Private Repository

GitHub does not accept the normal account password for Git HTTPS authentication. Use GitHub CLI browser authentication:

```bash
sudo apt update
sudo apt install -y gh
gh auth logout -h github.com
gh auth login -h github.com -p https -w
```

Choose GitHub.com, HTTPS, authenticate Git, and login with a web browser. Open the exact one-time URL and use the displayed code locally. Never send the code, password, personal access token, or Docker Hub token to an AI assistant.

Verify access:

```bash
gh auth status
gh repo view anon-443/SecurePipeline
```

Then clone:

```bash
cd "$HOME"
gh repo clone anon-443/SecurePipeline "$HOME/SecurePipeline"
cd "$HOME/SecurePipeline"
git status
```

A 404 from `gh repo view` means that the logged-in GitHub account cannot see the private repository, usually because the wrong account is authenticated. Do not create a second repository or make the project public merely to bypass this issue. If a failed clone created an incomplete directory, inspect it before removing it; only delete it if it contains no important work.

## Complete Docker and Trivy Vulnerability-Analysis History

This section records the vulnerability investigation and remediation sequence that another AI must understand before changing the Dockerfile or security workflow.

### Initial Vulnerability Analysis

A Trivy scan of `securepipeline:latest` reported 19 HIGH-severity operating-system package vulnerabilities. Examples included `libexpat1`, `libssl3`, and `python3.11-minimal`. The investigation separated OS-level packages from Python application dependencies. The Python dependencies inside the virtual environment at `/app/application/.venv` were clean; the issue was isolated to the Debian base-image layer.

The correct interpretation was that application requirements were not the source of the reported vulnerabilities. The base image and its OS packages required remediation.

### First Remediation Attempt and Build Failure

The first remediation attempt added `apt-get update && apt-get upgrade -y` to the Dockerfile’s multi-stage build. The build then failed during image creation with:

```text
ERROR: failed to calculate checksum ... "/install/lib/python3.12/site-packages": not found
```

The root cause was an inconsistent builder layout. The pip installation step was missing or packages were being installed into the global Python path rather than the expected `/install` path. The later `COPY` instruction therefore referenced a directory that did not exist.

The correct principle is to create one explicit virtual environment in the builder, install dependencies into that environment, and copy that exact directory into the runtime image. The current implementation uses `/opt/venv` consistently between builder and runtime stages.

### Distroless Runtime Limitation

Distroless runtime images intentionally omit package managers and shell utilities. `apt-get` cannot be executed inside a Google Distroless runtime image because there is no package manager by design. OS-level patching must occur in the builder or by using a patched base image; it cannot be performed inside the final distroless runtime stage.

The final repository uses a Python slim runtime rather than pretending that a distroless image can run apt commands. The runtime is hardened through a multi-stage build, non-root execution, removal of unnecessary packaging artifacts, current package updates during image creation, and a small production dependency set.

### Virtual-Environment Refactoring

The Dockerfile was refactored so that the builder creates and populates `/opt/venv`, then the runtime copies the exact `/opt/venv` directory. This eliminated the missing `/install/lib/python3.12/site-packages` checksum error and made the dependency boundary explicit.

The runtime image includes only the application requirements and production server. Development test and lint dependencies remain outside the runtime image. The application is executed through Gunicorn as a non-root `appuser`.

### Docker Hub Network Timeout

A local build attempt using:

```bash
docker build --no-cache -t securepipeline:latest .
```

failed after approximately 100 seconds with:

```text
dial tcp: lookup registry-1.docker.io on 1.1.1.1:53: i/o timeout
```

This was not a Dockerfile or application defect. The failure occurred while Docker attempted to resolve or contact Docker Hub to pull `python:3.12-slim`. The root cause was local network or DNS resolution failure in the environment.

The correct troubleshooting order is:

```bash
ping -c 3 1.1.1.1
getent hosts registry-1.docker.io
curl -I https://registry-1.docker.io/v2/
docker pull python:3.12-slim
```

If DNS resolution fails, inspect VMware NAT connectivity, the Ubuntu DNS configuration, VPN or proxy settings, and the host firewall. Do not rewrite the Dockerfile or disable security scans to hide a registry network timeout. GitHub Actions later validated the image build and security workflow successfully.

### Final Remediation Result

The security workflow was corrected and the image was hardened iteratively. The remediation included:

1. Updating the Trivy GitHub Action to a verified maintained release.
2. Scanning production application code rather than test assertions for Bandit SAST.
3. Making the application bind host configurable to remove the Bandit B104 finding.
4. Applying current Debian security updates during image construction.
5. Upgrading vulnerable Python runtime dependencies.
6. Removing the unnecessary direct `msgpack` dependency.
7. Removing unused system-level packaging and build-only artifacts from the final runtime layer.
8. Preserving the Trivy SARIF report as a workflow artifact.
9. Removing the optional Code Scanning upload step because the repository token lacked the required checks permission; the blocking Trivy scan remained enabled.

The latest verified CI and security workflows for commit `2c057bd` both passed. The security workflow therefore represents a real remediation history rather than a bypassed or ignored vulnerability gate.

## Handoff Interpretation for Another AI

Another AI should treat this project as a partially completed but strong internship submission foundation. The repository and automation are implemented. The Ubuntu VM prerequisites are also installed and Minikube is running. The remaining work is operational execution: authenticate the VM to GitHub, clone the private repository, run the local tests, build the image despite any local registry DNS issues, deploy it to Minikube, verify health and security settings, install monitoring selectively, enable GitHub Pages, and collect screenshots and final evidence.

The next AI must preserve the existing secure design. It should not replace the Dockerfile with an insecure single-stage build, remove Trivy to make a workflow pass, add secrets to source control, delete the Ubuntu VM, or claim that GitHub Pages runs the backend. All unverified results must be recorded as pending until the user runs the commands in the Ubuntu VM.


## Latest Verified Ubuntu VM Evidence — 03 September 2026

The user successfully verified the project on the Ubuntu VMware VM. Ubuntu 24.04.4 LTS and x86_64 are confirmed. The VM has approximately 24 GB free disk space, Docker 29.7.2, Docker Compose v5.5.0, kubectl v1.34.11, and Minikube v1.38.1.

Docker is active and the `hello-world` container ran successfully. The application virtual environment passed all five tests and Ruff linting. The Docker image built successfully, the `/health` endpoint returned `{"service":"securepipeline","status":"healthy"}`, and the running container identity was `uid=999(appuser) gid=999(appgroup)`, confirming non-root execution.

Minikube was restarted with the two-CPU resource profile and its node reached `Ready`. The latest repository commit `5ce6b92` fixed the Kustomize labels schema, and the user confirmed `Kustomize validation passed`. The Kubernetes deployment rolled out successfully with two running pods, an internal ClusterIP service, a default-deny NetworkPolicy, and a PodDisruptionBudget.

The user then ran the Kubernetes port-forward successfully. Endpoint verification returned:

```text
{"service":"securepipeline","status":"healthy"}
{"status":"ready","timestamp":"2026-09-02T20:54:38.332571+00:00"}
# HELP securepipeline_http_requests_total Total HTTP requests handled by SecurePipeline
# TYPE securepipeline_http_requests_total counter
securepipeline_http_requests_total{endpoint="health",method="GET",status="200"} 12.0
securepipeline_http_requests_total{endpoint="ready",method="GET",status="200"} 19.0
```

Docker Hub connectivity was also verified. DNS resolved for `auth.docker.io` and `registry-1.docker.io`, and an HTTPS request to the Docker token endpoint returned HTTP 405 with an `Allow: GET`/`POST` response. This is an expected endpoint-method response and confirms that network/DNS connectivity is working. The earlier Docker build timeout was therefore transient or environment-specific, not a Dockerfile defect.

The only remaining operational work is to capture screenshots, install and verify the monitoring stack as VM resources allow, enable GitHub Pages in repository settings, and complete the final internship report, presentation, and demo evidence. The private GitHub CLI login is still not configured, but Git fetch access has already worked and the local checkout was successfully updated to `5ce6b92`.


## Final Local Validation Evidence — 03 September 2026

The user completed a clean local validation run on the Ubuntu VMware VM. The Docker Hub registry lookup continued to fail intermittently during the later rebuild attempt with a DNS timeout for `registry-1.docker.io`. This remains an environmental network issue, not an application or Kubernetes defect. The previously built `securepipeline:0.1.0` image remained available locally and was successfully tested.

The standalone Docker validation passed on host port 8081. The container returned `{"service":"securepipeline","status":"healthy"}` and ran as `uid=999(appuser) gid=999(appgroup) groups=999(appgroup)`. This confirms the image starts correctly and does not run as root.

Minikube was running with a Ready control-plane node. The Kubernetes manifests were applied successfully, the deployment rollout completed, and two application pods were Running and Ready. The Service, default-deny NetworkPolicy, and PodDisruptionBudget were present.

Because host port 8080 was already occupied by an earlier forward, the Kubernetes Service was forwarded on port 8082 instead. The user verified the following responses:

```text
{"service":"securepipeline","status":"healthy"}
{"status":"ready","timestamp":"2026-09-03T15:29:15.397759+00:00"}
# HELP securepipeline_http_requests_total Total HTTP requests handled by SecurePipeline
# TYPE securepipeline_http_requests_total counter
securepipeline_http_requests_total{endpoint="health",method="GET",status="200"} 122.0
securepipeline_http_requests_total{endpoint="ready",method="GET",status="200"} 262.0
```

This is the strongest local evidence currently available: application unit tests and linting pass, the Docker image runs as a non-root user, Kubernetes is healthy, port forwarding works, health and readiness probes return successful responses, and Prometheus metrics are emitted. A fresh image rebuild should be repeated later when Docker Hub DNS is stable, but the core deployment is verified.
