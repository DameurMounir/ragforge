from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_deploy_workflow_uses_quality_gates_before_deploy() -> None:
    workflow = (ROOT / '.github/workflows/deploy-production.yml').read_text()
    assert 'needs: quality-gates' in workflow
    assert 'pytest -q' in workflow
    assert 'environment: production' in workflow
    assert 'permissions:' in workflow
    assert 'contents: read' in workflow


def test_remote_deploy_script_is_idempotent_and_health_checked() -> None:
    script = (ROOT / 'scripts/deployment/ragforge-deploy.sh').read_text()
    assert 'git fetch --prune origin' in script
    assert 'docker compose $COMPOSE_FILES config' in script
    assert 'docker compose $COMPOSE_FILES build ragforge-api' in script
    assert 'docker compose $COMPOSE_FILES up -d --remove-orphans' in script
    assert 'ragforge-healthcheck.sh' in script


def test_hardened_compose_adds_exporters_and_limits() -> None:
    compose = (ROOT / 'docker/docker-compose.production.hardened.yml').read_text()
    assert 'mongodb-exporter:' in compose
    assert 'qdrant-healthcheck:' in compose
    assert 'mem_limit:' in compose
    assert 'cpus:' in compose
    assert 'no-new-privileges:true' in compose
    assert './grafana/dashboards:/etc/grafana/dashboards:ro' in compose


def test_https_config_hides_metrics_publicly() -> None:
    nginx = (ROOT / 'docker/nginx/default.https.conf').read_text()
    assert 'listen 443 ssl http2;' in nginx
    assert 'location = /metrics' in nginx
    assert 'return 404;' in nginx


def test_grafana_dashboards_are_valid_json() -> None:
    for path in [
        ROOT / 'docker/grafana/dashboards/ragforge-http-overview.json',
        ROOT / 'docker/grafana/dashboards/ragforge-runtime-overview.json',
    ]:
        data = json.loads(path.read_text())
        assert data['uid']
        assert data['panels']


def test_branch23_requires_branch22_v3_baseline() -> None:
    validator = (ROOT / 'scripts/validation/validate_branch_23_deployment_package.py').read_text()
    assert 'validate_branch22_v3_baseline' in validator
    assert 'docker/docker-compose.production.yml' in validator
    assert 'PROMETHEUS_MULTIPROC_DIR' in validator
    assert 'Match.FULL' in validator


def test_mongodb_exporter_user_script_exists() -> None:
    script = ROOT / 'scripts/deployment/ragforge-create-mongodb-exporter-user.sh'
    assert script.exists()
    text = script.read_text()
    assert 'clusterMonitor' in text
    assert 'MONGO_EXPORTER_PASSWORD' in text
