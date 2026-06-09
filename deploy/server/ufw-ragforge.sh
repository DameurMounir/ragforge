#!/usr/bin/env bash
set -Eeuo pipefail

SSH_PORT="${RAGFORGE_SSH_PORT:-22}"
ALLOW_GRAFANA_PUBLIC="${RAGFORGE_ALLOW_GRAFANA_PUBLIC:-false}"
ALLOW_PROMETHEUS_PUBLIC="${RAGFORGE_ALLOW_PROMETHEUS_PUBLIC:-false}"

ufw default deny incoming
ufw default allow outgoing
ufw allow "$SSH_PORT"/tcp
ufw allow 80/tcp
ufw allow 443/tcp

if [ "$ALLOW_GRAFANA_PUBLIC" = "true" ]; then
  ufw allow 3000/tcp
fi

if [ "$ALLOW_PROMETHEUS_PUBLIC" = "true" ]; then
  ufw allow 9090/tcp
fi

ufw --force enable
ufw status verbose
