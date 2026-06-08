from __future__ import annotations

import os
import time
from collections.abc import Iterable
from typing import Any

from fastapi import FastAPI, Request, Response
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    REGISTRY,
    CollectorRegistry,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
    multiprocess,
)
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.routing import Match

from src.ragforge.core.config import get_settings


HTTP_REQUESTS_TOTAL = Counter(
    'ragforge_http_requests_total',
    'Total HTTP requests processed by RAGForge.',
    ['method', 'endpoint', 'status_code'],
)

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    'ragforge_http_request_duration_seconds',
    'HTTP request latency in seconds for RAGForge.',
    ['method', 'endpoint'],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
)

HTTP_REQUESTS_IN_PROGRESS = Gauge(
    'ragforge_http_requests_in_progress',
    'In-progress HTTP requests currently handled by RAGForge.',
    ['method', 'endpoint'],
    multiprocess_mode='livesum',
)

HTTP_REQUEST_EXCEPTIONS_TOTAL = Counter(
    'ragforge_http_request_exceptions_total',
    'Unhandled HTTP request exceptions raised by RAGForge.',
    ['method', 'endpoint', 'exception_type'],
)


def _normalize_path(path: str) -> str:
    normalized = path.strip() or '/metrics'
    if not normalized.startswith('/'):
        normalized = f'/{normalized}'
    return normalized


def _normalize_skip_paths(paths: Iterable[str] | None, metrics_path: str) -> set[str]:
    default_paths = {
        metrics_path,
        '/docs',
        '/redoc',
        '/openapi.json',
        '/favicon.ico',
    }
    if paths is None:
        return default_paths
    return default_paths | {_normalize_path(path) for path in paths}


def _route_template(request: Request) -> str:
    """Return the FastAPI/Starlette route template, not the raw path.

    BaseHTTPMiddleware runs before routing, so ``request.scope['route']`` is
    usually empty at the beginning of dispatch. To avoid high-cardinality
    Prometheus labels, this function proactively matches the current request
    scope against registered Starlette/FastAPI routes and returns the route
    template when possible.
    """

    route = request.scope.get('route')
    template = getattr(route, 'path', None)
    if template:
        return str(template)

    app = request.app
    for candidate_route in getattr(app, 'routes', []):
        try:
            match, _ = candidate_route.matches(request.scope)
        except Exception:
            continue
        if match == Match.FULL:
            candidate_template = getattr(candidate_route, 'path', None)
            if candidate_template:
                return str(candidate_template)

    return request.url.path


def _build_metrics_registry() -> CollectorRegistry:
    """Return the correct registry for single-process or multiprocess mode.

    prometheus_client needs a dedicated CollectorRegistry with
    MultiProcessCollector when the app is deployed with multiple worker
    processes. The entrypoint wipes PROMETHEUS_MULTIPROC_DIR on container
    startup, as recommended by the prometheus_client multiprocess mode docs.
    """

    multiproc_dir = os.getenv('PROMETHEUS_MULTIPROC_DIR')
    if multiproc_dir:
        registry = CollectorRegistry()
        multiprocess.MultiProcessCollector(registry)
        return registry
    return REGISTRY


class PrometheusMetricsMiddleware(BaseHTTPMiddleware):
    """Collect low-cardinality Prometheus metrics for FastAPI requests."""

    def __init__(
        self,
        app: Any,
        *,
        metrics_path: str,
        skip_paths: Iterable[str] | None = None,
    ) -> None:
        super().__init__(app)
        self.metrics_path = _normalize_path(metrics_path)
        self.skip_paths = _normalize_skip_paths(skip_paths, self.metrics_path)

    async def dispatch(self, request: Request, call_next: Any) -> Response:
        path = request.url.path
        if path in self.skip_paths:
            return await call_next(request)

        method = request.method
        endpoint = _route_template(request)
        started_at = time.perf_counter()
        response: Response | None = None

        HTTP_REQUESTS_IN_PROGRESS.labels(method=method, endpoint=endpoint).inc()
        try:
            response = await call_next(request)
            return response
        except Exception as error:
            HTTP_REQUEST_EXCEPTIONS_TOTAL.labels(
                method=method,
                endpoint=endpoint,
                exception_type=error.__class__.__name__,
            ).inc()
            raise
        finally:
            duration = time.perf_counter() - started_at
            status_code = str(response.status_code) if response is not None else '500'
            HTTP_REQUEST_DURATION_SECONDS.labels(
                method=method,
                endpoint=endpoint,
            ).observe(duration)
            HTTP_REQUESTS_TOTAL.labels(
                method=method,
                endpoint=endpoint,
                status_code=status_code,
            ).inc()
            HTTP_REQUESTS_IN_PROGRESS.labels(method=method, endpoint=endpoint).dec()


def setup_metrics(app: FastAPI, settings: Any | None = None) -> None:
    """Attach Prometheus middleware and a metrics endpoint to a FastAPI app.

    Metrics are configurable through Settings:
    - METRICS_ENABLED
    - METRICS_PATH
    - METRICS_INCLUDE_IN_SCHEMA
    - METRICS_SKIP_PATHS
    """

    settings = settings or get_settings()
    metrics_enabled = bool(getattr(settings, 'METRICS_ENABLED', True))
    if not metrics_enabled:
        return

    metrics_path = _normalize_path(getattr(settings, 'METRICS_PATH', '/metrics'))
    include_in_schema = bool(getattr(settings, 'METRICS_INCLUDE_IN_SCHEMA', False))
    skip_paths = getattr(settings, 'METRICS_SKIP_PATHS', None)

    app.add_middleware(
        PrometheusMetricsMiddleware,
        metrics_path=metrics_path,
        skip_paths=skip_paths,
    )

    async def metrics_endpoint() -> Response:
        registry = _build_metrics_registry()
        return Response(generate_latest(registry), media_type=CONTENT_TYPE_LATEST)

    app.add_api_route(
        metrics_path,
        metrics_endpoint,
        methods=['GET'],
        include_in_schema=include_in_schema,
        name='metrics',
    )
