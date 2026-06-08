from __future__ import annotations

import argparse
import sys
import urllib.error
import urllib.request
from pathlib import Path


REQUIRED_FILES = [
    'docker/docker-compose.production.yml',
    'docker/ragforge/Dockerfile',
    'docker/ragforge/entrypoint.sh',
    'docker/nginx/default.conf',
    'docker/prometheus/prometheus.yml',
    'docker/grafana/provisioning/datasources/prometheus.yml',
    'docker/env/.env.app.example',
    'docker/env/.env.mongodb.example',
    'docker/env/.env.postgres.example',
    'docker/env/.env.grafana.example',
    'docker/env/.env.postgres-exporter.example',
    'src/ragforge/observability/__init__.py',
    'src/ragforge/observability/metrics.py',
    'tests/branch_22_observability/test_metrics_middleware.py',
    'docs/setup/production-docker-runtime.md',
    'docs/milestones/milestone-06-production-deployment-workers/branches/branch-22-production-docker-observability.md',
]

REQUIRED_SERVICES = [
    'ragforge-migrations:',
    'ragforge-api:',
    'nginx:',
    'mongodb:',
    'postgres:',
    'qdrant:',
    'prometheus:',
    'grafana:',
    'postgres-exporter:',
    'node-exporter:',
]

REQUIRED_PROMETHEUS_JOBS = [
    "job_name: 'ragforge-api'",
    "job_name: 'postgres'",
    "job_name: 'qdrant'",
    "job_name: 'node-exporter'",
    "job_name: 'prometheus'",
]


def fail(message: str) -> None:
    raise RuntimeError(message)


def assert_file_exists(repo_root: Path, relative_path: str) -> None:
    path = repo_root / relative_path
    if not path.exists():
        fail(f'Missing required file: {relative_path}')


def assert_text_contains(path: Path, patterns: list[str]) -> None:
    text = path.read_text(encoding='utf-8')
    for pattern in patterns:
        if pattern not in text:
            fail(f'{path} does not contain required pattern: {pattern}')


def http_get(url: str, timeout: float = 5.0) -> tuple[int, str]:
    request = urllib.request.Request(url=url, method='GET')
    with urllib.request.urlopen(request, timeout=timeout) as response:
        body = response.read().decode('utf-8', errors='replace')
        return int(response.status), body


def validate_static_files(repo_root: Path) -> None:
    for relative_path in REQUIRED_FILES:
        assert_file_exists(repo_root, relative_path)

    compose_file = repo_root / 'docker/docker-compose.production.yml'
    assert_text_contains(compose_file, REQUIRED_SERVICES)
    assert_text_contains(
        compose_file,
        [
            'condition: service_healthy',
            'condition: service_completed_successfully',
            'name: ragforge-production',
            'ragforge-backend:',
            'platform: linux/amd64',
            'nginx:1.30.2-alpine-slim',
            'prom/prometheus:v3.12.0',
            'prometheuscommunity/postgres-exporter:v0.19.1',
            'prom/node-exporter:v1.11.0',
            'ragforge_postgres_data:',
            'ragforge_mongodb_data:',
        ],
    )

    prometheus_file = repo_root / 'docker/prometheus/prometheus.yml'
    assert_text_contains(prometheus_file, REQUIRED_PROMETHEUS_JOBS)
    assert_text_contains(prometheus_file, ["metrics_path: '/metrics'", "targets: ['ragforge-api:8000']"])

    nginx_file = repo_root / 'docker/nginx/default.conf'
    assert_text_contains(nginx_file, ['proxy_pass http://ragforge_api;', 'location = /metrics', 'return 404;'])

    metrics_file = repo_root / 'src/ragforge/observability/metrics.py'
    assert_text_contains(
        metrics_file,
        [
            'ragforge_http_requests_total',
            'ragforge_http_request_duration_seconds',
            'ragforge_http_requests_in_progress',
            '_build_metrics_registry',
            'MultiProcessCollector',
            '_route_template',
            'Match.FULL',
        ],
    )

    config_file = repo_root / 'src/ragforge/core/config.py'
    assert_text_contains(
        config_file,
        [
            'METRICS_ENABLED',
            'METRICS_PATH',
            'METRICS_INCLUDE_IN_SCHEMA',
            'METRICS_SKIP_PATHS',
        ],
    )

    main_file = repo_root / 'src/ragforge/main.py'
    assert_text_contains(main_file, ['setup_metrics', 'src.ragforge.observability.metrics'])


def validate_runtime(base_url: str) -> None:
    health_url = f'{base_url.rstrip("/")}/api/v1/health/'
    metrics_url = f'{base_url.rstrip("/")}/metrics'

    status, body = http_get(health_url)
    if status != 200 or 'app_healthy' not in body:
        fail(f'Health check did not return app_healthy from {health_url}')
    print('RAGForge health endpoint succeeded.')

    status, body = http_get(metrics_url)
    if status != 200 or 'ragforge_http_requests_total' not in body:
        fail(f'Metrics endpoint did not expose expected Prometheus metrics from {metrics_url}')
    print('RAGForge metrics endpoint succeeded.')


def main() -> int:
    parser = argparse.ArgumentParser(description='Validate Branch 22 production runtime files.')
    parser.add_argument('--runtime', action='store_true', help='Also validate a running API and metrics endpoint.')
    parser.add_argument('--base-url', default='http://127.0.0.1:8000', help='Base URL used when --runtime is enabled.')
    args = parser.parse_args()

    repo_root = Path.cwd()

    try:
        validate_static_files(repo_root=repo_root)
        print('Branch 22 static production runtime file validation passed.')

        if args.runtime:
            validate_runtime(base_url=args.base_url)
            print('Branch 22 runtime validation passed.')

        print('Branch 22 production Docker observability validation passed.')
        return 0
    except (RuntimeError, urllib.error.URLError, TimeoutError) as error:
        print(f'Branch 22 validation failed: {error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
