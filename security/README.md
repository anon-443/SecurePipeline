# Security Gates

SecurePipeline treats security checks as release gates rather than optional checks. Pull requests and pushes to `main` run three controls: Bandit scans Python source code for common security problems, OWASP Dependency-Check reviews declared dependencies, and Trivy scans the built container image for high and critical vulnerabilities.

## GitHub Configuration

The repository should contain the following Actions secrets before image publishing is enabled:

| Secret | Purpose |
|---|---|
| `DOCKERHUB_USERNAME` | Docker Hub account name |
| `DOCKERHUB_TOKEN` | A Docker Hub access token, not the account password |

Secrets must be configured in GitHub repository settings and must never be committed to YAML files, source code, or `.env` files.

## Release Policy

A release should be created only after the quality workflow and security workflow succeed. The publish workflow accepts semantic version tags such as `v1.0.0` and publishes both an immutable commit-SHA tag and a release tag. The `latest` tag is updated only for version-tagged releases.

## Scan Policy

The dependency workflow fails for vulnerabilities with a CVSS score of 7 or higher. Trivy checks `HIGH` and `CRITICAL` vulnerabilities and ignores unfixed findings to reduce false release blockers. Any exception should be documented, reviewed, and added through an explicit suppression process rather than silently ignored.
