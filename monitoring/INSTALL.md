# Monitoring Installation Guide

This guide installs the monitoring stack on the local Minikube cluster. The application is already exposing `/metrics`; this guide adds Prometheus collection, Grafana dashboards, and optional Loki log aggregation.

## Prerequisites

The Ubuntu VM should have at least 10 GB free, Docker running, Minikube running, and Helm installed. Verify the cluster first:

```bash
minikube status
kubectl get nodes
```

Install Helm if it is missing:

```bash
command -v helm || {
  curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
}
helm version --short
```

## Install Prometheus and Grafana

Add the Prometheus Community chart repository and update it:

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
kubectl create namespace monitoring --dry-run=client -o yaml | kubectl apply -f -
```

Install a resource-conscious kube-prometheus-stack. The release name must remain `kube-prometheus-stack` because the ServiceMonitor in this repository uses that release label:

```bash
helm upgrade --install kube-prometheus-stack prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --set prometheus.prometheusSpec.retention=24h \
  --set prometheus.prometheusSpec.resources.requests.cpu=100m \
  --set prometheus.prometheusSpec.resources.requests.memory=512Mi \
  --set prometheus.prometheusSpec.resources.limits.cpu=500m \
  --set prometheus.prometheusSpec.resources.limits.memory=1Gi \
  --set grafana.resources.requests.cpu=50m \
  --set grafana.resources.requests.memory=128Mi \
  --set grafana.resources.limits.cpu=300m \
  --set grafana.resources.limits.memory=512Mi
```

Apply the application ServiceMonitor:

```bash
kubectl apply -f monitoring/servicemonitor.yaml
kubectl -n monitoring get pods
kubectl -n monitoring get servicemonitor
```

Verify that Prometheus and Grafana become Ready. On a two-CPU VM this may take several minutes. If the VM runs out of memory, stop optional workloads and retry with only Prometheus and Grafana enabled.

## Open Prometheus and Grafana

Use separate terminals for port forwards:

```bash
kubectl -n monitoring port-forward svc/kube-prometheus-stack-prometheus 9090:9090
```

```bash
kubectl -n monitoring port-forward svc/kube-prometheus-stack-grafana 3000:80
```

Open `http://127.0.0.1:9090` for Prometheus and `http://127.0.0.1:3000` for Grafana. Retrieve the generated Grafana administrator password with:

```bash
kubectl -n monitoring get secret kube-prometheus-stack-grafana \
  -o jsonpath='{.data.admin-password}' | base64 -d; echo
```

In Prometheus, query:

```text
securepipeline_http_requests_total
```

In Grafana, import `monitoring/grafana-dashboard.json` or use the dashboards that ship with kube-prometheus-stack. Capture screenshots only after generating traffic through `/health` and `/ready`.

## Optional Loki and Promtail Logging

The Loki chart is maintained in the Grafana Community Helm Charts repository. Install the small monolithic Loki deployment and Promtail only if Minikube has enough memory:

```bash
helm repo add grafana-community https://grafana-community.github.io/helm-charts
helm repo update
helm upgrade --install loki grafana-community/loki \
  --namespace monitoring \
  --set deploymentMode=SingleBinary \
  --set singleBinary.replicas=1 \
  --set loki.auth_enabled=false \
  --set loki.commonConfig.replication_factor=1 \
  --set loki.storage.type=filesystem
helm upgrade --install promtail grafana-community/promtail \
  --namespace monitoring \
  --set config.clients[0].url=http://loki-gateway.monitoring.svc.cluster.local/loki/api/v1/push
```

Check logging workloads:

```bash
kubectl -n monitoring get pods
kubectl -n monitoring logs daemonset/promtail --tail=20
```

Add Loki to Grafana as a data source using the URL `http://loki-gateway.monitoring.svc.cluster.local` if the chart creates the gateway service. If that service is not present, inspect services with `kubectl -n monitoring get svc` and use the Loki service name shown there.

## Cleanup

To stop the monitoring stack while preserving the application:

```bash
helm uninstall promtail -n monitoring 2>/dev/null || true
helm uninstall loki -n monitoring 2>/dev/null || true
helm uninstall kube-prometheus-stack -n monitoring 2>/dev/null || true
```

The official Prometheus Operator documentation recommends kube-prometheus-stack as a practical installation route for Prometheus Operator components [1]. Grafana’s Loki documentation recommends the Loki Helm chart and describes monolithic mode as appropriate for a small monitoring stack [2].

## References

[1]: https://prometheus-operator.dev/docs/getting-started/installation/ "Prometheus Operator: Installing Prometheus Operator"
[2]: https://grafana.com/docs/loki/latest/setup/install/helm/ "Grafana Loki: Install using Helm"
