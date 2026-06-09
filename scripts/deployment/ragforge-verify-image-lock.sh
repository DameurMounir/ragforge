#!/usr/bin/env bash
set -Eeuo pipefail

APP_DIR="${RAGFORGE_APP_DIR:-/opt/ragforge/app}"
LOCK_FILE="${RAGFORGE_IMAGE_LOCK_FILE:-deploy/state/image-digests.lock}"
COMPOSE_FILES="${RAGFORGE_COMPOSE_FILES:--f docker/docker-compose.production.yml -f docker/docker-compose.production.hardened.yml}"

cd "$APP_DIR"
if [ ! -s "$LOCK_FILE" ]; then
  echo "ERROR: image lock file not found: $LOCK_FILE" >&2
  echo "Run scripts/deployment/ragforge-image-lock.sh after approving image versions." >&2
  exit 1
fi

missing=0
while read -r locked_image; do
  [ -n "$locked_image" ] || continue
  if ! docker pull "$locked_image" >/dev/null 2>&1; then
    echo "ERROR: locked image cannot be pulled: $locked_image" >&2
    missing=1
  fi
done < "$LOCK_FILE"

if [ "$missing" -ne 0 ]; then
  exit 1
fi

echo 'Image lock verification passed.'
