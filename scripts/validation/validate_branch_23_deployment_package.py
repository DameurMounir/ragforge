from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

BRANCH22_V3_REQUIRED_FILES = [
    'docker/docker-compose.production.yml',
    'docker/ragforge/Dockerfile',
    'docker/ragforge/entrypoint.sh',
    'docker/nginx/default.conf',
    'docker/prometheus/prometheus.yml',
    'docker/grafana/provisioning/datasources/prometheus.yml',
    'docker/env/.env.app.example',
    'docker/env/.env.postgres.example',
    'docker/env/.env.mongodb.example',
    'docker/env/.env.grafana.example',
    'docker/env/.env.postgres-exporter.example',
    'src/ragforge/observability/metrics.py',
    'scripts/validation/validate_branch_22_production_runtime.py',
    'docs/setup/production-docker-runtime.md',
]

REQUIRED_FILES = [
    '.github/workflows/deploy-production.yml',
    'docker/docker-compose.production.hardened.yml',
    'docker/docker-compose.https.yml',
    'docker/nginx/default.https.conf',
    'docker/prometheus/prometheus.production.yml',
    'docker/env/.env.mongodb-exporter.example',
    'docker/grafana/provisioning/dashboards/dashboards.yml',
    'docker/grafana/dashboards/ragforge-http-overview.json',
    'docker/grafana/dashboards/ragforge-runtime-overview.json',
    'scripts/deployment/ragforge-deploy.sh',
    'scripts/deployment/ragforge-healthcheck.sh',
    'scripts/deployment/ragforge-backup.sh',
    'scripts/deployment/ragforge-image-lock.sh',
    'scripts/deployment/ragforge-verify-image-lock.sh',
    'scripts/deployment/ragforge-rollback.sh',
    'scripts/deployment/ragforge-tls-init.sh',
    'scripts/deployment/ragforge-bootstrap-server.sh',
    'scripts/deployment/ragforge-create-mongodb-exporter-user.sh',
    'deploy/systemd/ragforge-production.service',
    'deploy/systemd/ragforge-healthcheck.service',
    'deploy/systemd/ragforge-healthcheck.timer',
    'deploy/server/ufw-ragforge.sh',
    'deploy/server/sudoers-ragforge-deploy',
    'deploy/secrets/README.md',
    'docs/setup/server-deployment-github-actions.md',
    'docs/milestones/milestone-06-production-deployment-workers/branches/branch-23-server-deployment-github-actions.md',
]

SHELL_SCRIPTS = [
    'scripts/deployment/ragforge-deploy.sh',
    'scripts/deployment/ragforge-healthcheck.sh',
    'scripts/deployment/ragforge-backup.sh',
    'scripts/deployment/ragforge-image-lock.sh',
    'scripts/deployment/ragforge-verify-image-lock.sh',
    'scripts/deployment/ragforge-rollback.sh',
    'scripts/deployment/ragforge-tls-init.sh',
    'scripts/deployment/ragforge-bootstrap-server.sh',
    'scripts/deployment/ragforge-create-mongodb-exporter-user.sh',
    'deploy/server/ufw-ragforge.sh',
    'scripts/deployment/ragforge-create-mongodb-exporter-user.sh',
]

FORBIDDEN_PATTERNS = [
    r'BEGIN OPENSSH PRIVATE KEY',
    r'sk-[A-Za-z0-9_-]{20,}',
    r'OPENAI_API_KEY\s*=\s*[A-Za-z0-9_-]{20,}',
    r'password\s*=\s*admin123',
]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding='utf-8')



def validate_branch22_v3_baseline() -> None:
    missing = [path for path in BRANCH22_V3_REQUIRED_FILES if not (ROOT / path).exists()]
    if missing:
        raise AssertionError(
            'Branch 23 requires Branch 22 v3 baseline files before applying this package. '
            f'Missing: {missing}'
        )

    compose = read('docker/docker-compose.production.yml')
    required_compose_fragments = [
        'name: ragforge-production',
        'ragforge-migrations:',
        'ragforge-api:',
        'postgres-exporter:',
        'node-exporter:',
        'grafana/provisioning',
    ]
    for fragment in required_compose_fragments:
        if fragment not in compose:
            raise AssertionError(f'Branch 22 v3 compose baseline is missing: {fragment}')

    dockerfile = read('docker/ragforge/Dockerfile')
    if 'PROMETHEUS_MULTIPROC_DIR' not in dockerfile or 'USER ragforge' not in dockerfile:
        raise AssertionError('Branch 22 v3 Dockerfile baseline must include multiprocess metrics support and non-root runtime user.')

    metrics = read('src/ragforge/observability/metrics.py')
    if 'MultiProcessCollector' not in metrics or 'Match.FULL' not in metrics:
        raise AssertionError('Branch 22 v3 metrics baseline must include multiprocess support and route-template matching.')

def validate_required_files() -> None:
    missing = [path for path in REQUIRED_FILES if not (ROOT / path).exists()]
    if missing:
        raise AssertionError(f'Missing Branch 23 files: {missing}')


def validate_no_secret_leaks() -> None:
    for path in REQUIRED_FILES:
        if not (ROOT / path).is_file():
            continue
        text = read(path)
        for pattern in FORBIDDEN_PATTERNS:
            if re.search(pattern, text, flags=re.IGNORECASE):
                raise AssertionError(f'Forbidden secret-like pattern in {path}: {pattern}')


def validate_workflow_security() -> None:
    workflow = read('.github/workflows/deploy-production.yml')
    required_fragments = [
        'permissions:',
        'contents: read',
        'environment: production',
        'concurrency:',
        'StrictHostKeyChecking=yes',
        'ssh-keyscan',
        'scripts/validation/validate_branch_23_deployment_package.py',
        'pytest -q',
    ]
    for fragment in required_fragments:
        if fragment not in workflow:
            raise AssertionError(f'Workflow is missing required fragment: {fragment}')


def validate_compose_hardening() -> None:
    compose = read('docker/docker-compose.production.hardened.yml')
    required_fragments = [
        'qdrant-healthcheck:',
        'mongodb-exporter:',
        'mem_limit:',
        'cpus:',
        'pids_limit:',
        'no-new-privileges:true',
        'prometheus.production.yml',
        './grafana/dashboards:/etc/grafana/dashboards:ro',
        'service_completed_successfully',
    ]
    for fragment in required_fragments:
        if fragment not in compose:
            raise AssertionError(f'Hardened compose is missing: {fragment}')


def validate_https_config() -> None:
    nginx = read('docker/nginx/default.https.conf')
    required_fragments = [
        'listen 443 ssl http2;',
        'Strict-Transport-Security',
        'location = /metrics',
        'return 404;',
        'proxy_pass http://ragforge-api:8000;',
    ]
    for fragment in required_fragments:
        if fragment not in nginx:
            raise AssertionError(f'HTTPS Nginx config is missing: {fragment}')


def validate_grafana_dashboards() -> None:
    for path in [
        'docker/grafana/dashboards/ragforge-http-overview.json',
        'docker/grafana/dashboards/ragforge-runtime-overview.json',
    ]:
        data = json.loads(read(path))
        if not data.get('uid') or not data.get('panels'):
            raise AssertionError(f'Invalid Grafana dashboard: {path}')


def validate_scripts_are_executable() -> None:
    for path in SHELL_SCRIPTS:
        mode = (ROOT / path).stat().st_mode
        if not mode & 0o111:
            raise AssertionError(f'Script is not executable: {path}')


def main() -> None:
    validate_branch22_v3_baseline()
    validate_required_files()
    validate_no_secret_leaks()
    validate_workflow_security()
    validate_compose_hardening()
    validate_https_config()
    validate_grafana_dashboards()
    validate_scripts_are_executable()
    print('Branch 23 deployment package validation passed.')


if __name__ == '__main__':
    main()
