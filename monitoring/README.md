# Monitoring and Logging

SecurePipeline exposes Prometheus metrics at `/metrics`. Prometheus should scrape the Kubernetes Service endpoints using `prometheus.yml`. Grafana will visualize request volume, response status, pod availability, CPU usage, and memory usage. Loki and Promtail will collect and search container logs so failures can be correlated with deployment and request activity.

## Suggested Stack Installation

For a local Kubernetes demonstration, install the Prometheus and Grafana stack with the organization-approved Helm chart, then configure the data source and import the dashboard stored in this directory. Install Loki and Promtail using the organization-approved Helm chart and connect Loki as a Grafana data source.

The exact chart versions should be pinned in the deployment environment so that the internship demo remains reproducible. Generated dashboards, screenshots, and exported reports belong in the final submission documentation rather than in runtime configuration directories.

## Dashboard Panels

| Panel | Purpose |
|---|---|
| Request rate | Shows application traffic over time |
| HTTP request status | Highlights error responses and availability problems |
| Pod count | Confirms replica availability during rollout |
| CPU and memory | Detects resource pressure and capacity trends |
| Container logs | Supports root-cause analysis for failed requests and crashes |

## Validation

After installing the stack, verify that Prometheus can query `securepipeline_http_requests_total`, Grafana can read the Prometheus and Loki data sources, and Promtail is forwarding logs from the application namespace. Capture screenshots only after the dashboard displays real application traffic generated through the health and readiness endpoints.
