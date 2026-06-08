#!/usr/bin/env sh
set -eu

if [ -n "${PROMETHEUS_MULTIPROC_DIR:-}" ]; then
  mkdir -p "${PROMETHEUS_MULTIPROC_DIR}"
  rm -f "${PROMETHEUS_MULTIPROC_DIR}"/*.db 2>/dev/null || true
fi

echo "Starting RAGForge command: $*"
exec "$@"
