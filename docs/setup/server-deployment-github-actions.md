# RAGForge Server Deployment & GitHub Actions CD

Branch 23 turns the Branch 22 production Docker runtime into a server-deployable system.

## Scope

Branch 23 covers:

- Ubuntu server preparation.
- Dedicated deployment user.
- SSH-based deployment from GitHub Actions.
- Server-owned production env files.
- systemd service for the Docker Compose runtime.
- Firewall baseline.
- Optional HTTPS with Nginx and Certbot.
- Deployment health checks.
- Lightweight backup and rollback scripts.
- Image lock generation and verification.

Branch 23 does not introduce Celery workers. Redis/Celery monitoring belongs to the future worker branches.

## Server layout

```text
/opt/ragforge/
  app/        # git clone of RAGForge
  backups/    # lightweight deployment snapshots
```

## GitHub repository secrets

Create these in GitHub repository settings:

```text
RAGFORGE_PRODUCTION_HOST
RAGFORGE_PRODUCTION_USER
RAGFORGE_PRODUCTION_SSH_PRIVATE_KEY
```

Create this GitHub variable if the SSH port is not 22:

```text
RAGFORGE_PRODUCTION_SSH_PORT
```

Optional variable:

```text
RAGFORGE_REMOTE_DEPLOY_COMMAND=/opt/ragforge/app/scripts/deployment/ragforge-deploy.sh
```

## Bootstrap server

After adding a deploy key with read access to the repository, run:

```bash
sudo RAGFORGE_REPO_SSH_URL='git@github.com:DameurMounir/ragforge.git' \
  RAGFORGE_DEPLOY_USER='ragforge_deploy' \
  RAGFORGE_DEPLOY_BRANCH='main' \
  bash scripts/deployment/ragforge-bootstrap-server.sh
```

Then configure production env files under:

```text
/opt/ragforge/app/docker/env/
```

Never commit real `.env` files.

## Start service manually

```bash
sudo systemctl daemon-reload
sudo systemctl enable ragforge-production.service
sudo systemctl start ragforge-production.service
sudo systemctl status ragforge-production.service
```

## Deploy manually

```bash
cd /opt/ragforge/app
bash scripts/deployment/ragforge-deploy.sh
```

## Healthcheck

```bash
bash scripts/deployment/ragforge-healthcheck.sh
```

## Rollback

```bash
cd /opt/ragforge/app
bash scripts/deployment/ragforge-rollback.sh
```

## Optional HTTPS

Before enabling HTTPS, replace `example.com` in:

```text
docker/nginx/default.https.conf
```

Then run:

```bash
export RAGFORGE_DOMAIN='your-domain.com'
export RAGFORGE_TLS_EMAIL='you@example.com'
bash scripts/deployment/ragforge-tls-init.sh
```

Use the HTTPS compose stack:

```bash
export RAGFORGE_COMPOSE_FILES='-f docker/docker-compose.production.yml -f docker/docker-compose.production.hardened.yml -f docker/docker-compose.https.yml'
bash scripts/deployment/ragforge-deploy.sh
```

## SSH port forwarding for private dashboards

Grafana and Prometheus should stay private by default.

```bash
ssh -L 3000:127.0.0.1:3000 -L 9090:127.0.0.1:9090 ragforge_deploy@SERVER_IP
```

Then open locally:

```text
http://127.0.0.1:3000
http://127.0.0.1:9090
```

## Image lock

After approving image versions:

```bash
bash scripts/deployment/ragforge-image-lock.sh
```

To enforce locked image digests during deployment:

```bash
export RAGFORGE_ENABLE_IMAGE_LOCK_VERIFY=true
bash scripts/deployment/ragforge-deploy.sh
```

## Validation

```bash
python scripts/validation/validate_branch_23_deployment_package.py
pytest tests/branch_23_deployment -q
```
