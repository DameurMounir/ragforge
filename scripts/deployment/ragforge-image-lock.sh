#!/usr/bin/env bash
set -Eeuo pipefail

APP_DIR="${RAGFORGE_APP_DIR:-/opt/ragforge/app}"
LOCK_FILE="${RAGFORGE_IMAGE_LOCK_FILE:-deploy/state/image-digests.lock}"
COMPOSE_FILES="${RAGFORGE_COMPOSE_FILES:--f docker/docker-compose.production.yml -f docker/docker-compose.production.hardened.yml}"

cd "$APP_DIR"
mkdir -p "$(dirname "$LOCK_FILE")"
: > "$LOCK_FILE"

docker compose $COMPOSE_FILES config --images | sort -u | while read -r image; do
  [ -n "$image" ] || continue
  docker pull "$image" >/dev/null
  digest="$(docker image inspect --format='{{index .RepoDigests 0}}' "$image" 2>/dev/null || true)"
  if [ -z "$digest" ]; then
    echo "WARN: no repo digest found for $image" >&2
    echo "$image" >> "$LOCK_FILE"
  else
    echo "$digest" >> "$LOCK_FILE"
  fi
done

echo "Image lock written to $LOCK_FILE"
