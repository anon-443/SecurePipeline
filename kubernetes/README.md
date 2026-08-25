# Kubernetes Deployment

The manifests in this directory deploy SecurePipeline into a dedicated namespace with two replicas, rolling updates, health probes, resource limits, a non-root runtime, a read-only filesystem, dropped Linux capabilities, least-privilege RBAC, a default-deny network policy, and a PodDisruptionBudget.

## Before Applying

Replace `DOCKERHUB_USERNAME` in `deployment.yaml` with the Docker Hub account that owns the published `securepipeline` image. Create the TLS secret required by the Ingress using a cluster-specific certificate process such as cert-manager, or create it manually:

```bash
kubectl -n securepipeline create secret tls securepipeline-tls \
  --cert=path/to/tls.crt \
  --key=path/to/tls.key
```

The TLS files must not be committed to GitHub. For a local-only demo without an Ingress controller, the Service can be accessed with port forwarding:

```bash
kubectl -n securepipeline port-forward service/securepipeline 8080:80
```

## Apply and Validate

```bash
kubectl apply -k kubernetes/
kubectl -n securepipeline rollout status deployment/securepipeline
kubectl -n securepipeline get pods,service,ingress,networkpolicy,pdb
kubectl -n securepipeline describe deployment securepipeline
```

The deployment is intentionally configured with `imagePullPolicy: IfNotPresent` for repeatable local demonstrations. In a production registry workflow, images should be immutable and referenced by digest or a release-specific tag.
