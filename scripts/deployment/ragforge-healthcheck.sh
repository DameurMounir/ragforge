#!/usr/bin/env bash
set -Eeuo pipefail

APP_URL="${RAGFORGE_HEALTH_URL:-http://127.0.0.1:8088/api/v1/health/}"
METRICS_URL="${RAGFORGE_METRICS_URL:-http://127.0.0.1:8000/metrics}"
PROMETHEUS_URL="${RAGFORGE_PROMETHEUS_URL:-http://127.0.0.1:9090/-/healthy}"
GRAFANA_URL="${RAGFORGE_GRAFANA_URL:-http://127.0.0.1:3000/api/health}"
MAX_ATTEMPTS="${RAGFORGE_HEALTH_ATTEMPTS:-30}"
SLEEP_SECONDS="${RAGFORGE_HEALTH_SLEEP_SECONDS:-3}"

wait_for_url() {
  local name="$1"
  local url="$2"
  local expected="${3:-}"

  for attempt in $(seq 1 "$MAX_ATTEMPTS"); do
    if body=$(curl -fsS --max-time 5 "$url" 2>/dev/null); then
      if [[ -z "$expected" || "$body" == *"$expected"* ]]; then
        echo "OK: $name is healthy."
        return 0
      fi
    fi
    echo "Waiting for $name... $attempt/$MAX_ATTEMPTS"
    sleep "$SLEEP_SECONDS"
  done

  echo "ERROR: $name did not become healthy at $url" >&2
  return 1
}

wait_for_url 'RAGForge API via Nginx' "$APP_URL" 'healthy'
wait_for_url 'RAGForge metrics' "$METRICS_URL" 'ragforge'
wait_for_url 'Prometheus' "$PROMETHEUS_URL" 'Prometheus'
wait_for_url 'Grafana' "$GRAFANA_URL" 'database'

echo 'Branch 23 deployment healthcheck passed.'
