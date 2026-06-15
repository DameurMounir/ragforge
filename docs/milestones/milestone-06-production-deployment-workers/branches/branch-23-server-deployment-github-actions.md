# Branch 23 — Server Deployment & GitHub Actions CD

Git branch:

```text
feature/23-server-deployment-github-actions
```

Milestone:

```text
Milestone 6 — Production Deployment & Workers
```

## Goal

Turn the Branch 22 production Docker runtime into a server-deployable system with controlled GitHub Actions deployment, systemd supervision, server-side health checks, optional HTTPS, and deployment hardening.

## Why this branch exists

Branch 22 created the production-like Docker runtime and observability foundation.

Branch 23 adds the deployment boundary:

```text
GitHub push / manual dispatch
  ↓
GitHub Actions quality gates
  ↓
SSH to production server
  ↓
remote deploy script
  ↓
git fetch + reset to target release
  ↓
compose config validation
  ↓
app image build
  ↓
compose up -d
  ↓
health checks
  ↓
release state update
```

## Main changes

- Add GitHub Actions production deployment workflow.
- Add server-side deployment script.
- Add server-side healthcheck script.
- Add lightweight backup and rollback scripts.
- Add systemd service and healthcheck timer.
- Add firewall baseline script.
- Add HTTPS Nginx config and Certbot compose override.
- Add hardened Compose override with resource limits.
- Add Qdrant healthcheck sidecar.
- Add MongoDB exporter service.
- Add Prometheus production scrape config.
- Add Grafana dashboard provisioning.
- Add image lock generation and verification scripts.
- Add validation script and artifact tests.

## Deliberate non-goals

- No Celery worker runtime yet.
- No Redis runtime yet.
- No Kubernetes.
- No GitHub Actions deployment without quality gates.
- No production application secrets stored in GitHub Actions.

## Definition of done

- Workflow runs quality gates before deployment.
- Remote deployment uses SSH with known-host verification.
- Server keeps production runtime secrets locally.
- systemd can start the Docker Compose runtime after reboot.
- Deployment script can update the server idempotently.
- Healthcheck validates API, metrics, Prometheus, and Grafana.
- Qdrant healthcheck sidecar passes before API readiness is accepted.
- MongoDB exporter is scrapeable by Prometheus.
- Grafana dashboards are provisioned from JSON files.
- Optional HTTPS stack is documented and ready for real domain use.
- Branch 23 validation script passes.
- Branch 23 tests pass.

## Validation

```bash
python -m compileall src/ragforge scripts/validation tests
python scripts/validation/validate_branch_23_deployment_package.py
pytest tests/branch_23_deployment -q
pytest -q
```

## Architecture rule

Branch 23 must not modify the RAG Core behavior. It only adds deployment automation, operational hardening, and production server readiness around the existing Branch 22 runtime.


## Branch 22 v3 dependency

Branch 23 must be applied after Branch 22 v3. The validation script checks for the Branch 22 v3 Docker Compose baseline, non-root API Dockerfile, multiprocess Prometheus support, and route-template metric labels.

## MongoDB exporter user

After MongoDB is healthy, create the exporter user with:

```bash
export MONGO_INITDB_ROOT_USERNAME='admin'
export MONGO_INITDB_ROOT_PASSWORD='CHANGE_ME'
export MONGO_EXPORTER_PASSWORD='CHANGE_ME_STRONG'
bash scripts/deployment/ragforge-create-mongodb-exporter-user.sh
```

Then store the same exporter credentials in `docker/env/.env.mongodb-exporter`.

---

## Verified production rollout recap

Branch 23 was activated on the real Sherizon production server and connected to GitHub Actions deployment.

Final verified flow:

    push to main
    GitHub Actions quality gates
    SSH to production server
    git pull origin main
    Docker image build
    Docker Compose production restart
    deployment healthcheck
    production endpoint healthy

Problems discovered during activation:

    Docker env example files were missing from Git.
    CI tests failed because required settings were missing in GitHub Actions.
    GitHub repository deployment secrets were not configured.
    The deployment script defaulted to /opt/ragforge/app.
    The backup script defaulted to /opt/ragforge, which was not writable.
    The hardened compose overlay had a pids_limit conflict.

Fixes applied:

    Added Docker env example files required by Branch 23 validation.
    Added deterministic pytest settings defaults in tests/conftest.py.
    Configured GitHub Actions deployment secrets and variables.
    Overrode deployment paths with RAGFORGE_APP_DIR, RAGFORGE_BACKUP_DIR, and RAGFORGE_RELEASE_STATE_DIR.
    Temporarily selected only docker/docker-compose.production.yml for the verified deployment.

Final acceptance:

    https://ragforge.sherizon.com/docs returned 200 OK
    /api/v1/health/ returned app_healthy
    environment was production-docker
    deployed SHA was ffd00d636f951adc16e44c76081b3d82b407b615

Follow-up hardening branch:

    fix/23-deployment-hardening-alignment
