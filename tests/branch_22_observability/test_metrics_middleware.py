from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.ragforge.observability.metrics import setup_metrics


class MetricsSettings:
    METRICS_ENABLED = True
    METRICS_PATH = '/metrics'
    METRICS_INCLUDE_IN_SCHEMA = False
    METRICS_SKIP_PATHS = ['/metrics', '/docs', '/redoc', '/openapi.json']


def test_metrics_endpoint_exposes_prometheus_format():
    app = FastAPI()
    setup_metrics(app=app, settings=MetricsSettings())

    @app.get('/health-test')
    async def health_test():
        return {'status': 'ok'}

    client = TestClient(app)

    response = client.get('/health-test')
    assert response.status_code == 200

    metrics_response = client.get('/metrics')
    assert metrics_response.status_code == 200
    assert 'text/plain' in metrics_response.headers['content-type']
    assert 'ragforge_http_requests_total' in metrics_response.text
    assert 'ragforge_http_request_duration_seconds' in metrics_response.text


def test_metrics_use_route_templates_to_avoid_high_cardinality_labels():
    app = FastAPI()
    setup_metrics(app=app, settings=MetricsSettings())

    @app.get('/projects/{project_id}/assets/{asset_id}')
    async def read_asset(project_id: str, asset_id: str):
        return {'project_id': project_id, 'asset_id': asset_id}

    client = TestClient(app)

    assert client.get('/projects/project-a/assets/asset-1').status_code == 200
    assert client.get('/projects/project-b/assets/asset-2').status_code == 200

    metrics_response = client.get('/metrics')
    assert metrics_response.status_code == 200
    assert '/projects/{project_id}/assets/{asset_id}' in metrics_response.text
    assert '/projects/project-a/assets/asset-1' not in metrics_response.text
    assert '/projects/project-b/assets/asset-2' not in metrics_response.text
