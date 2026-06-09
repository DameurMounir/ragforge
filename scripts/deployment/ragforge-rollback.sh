#!/usr/bin/env bash
set -Eeuo pipefail

APP_DIR="${RAGFORGE_APP_DIR:-/opt/ragforge/app}"
COMPOSE_FILES="${RAGFORGE_COMPOSE_FILES:--f docker/docker-compose.production.yml -f docker/docker-compose.production.hardened.yml}"
STATE_DIR="${RAGFORGE_RELEASE_STATE_DIR:-deploy/state}"
PREVIOUS_SHA_FILE="$APP_DIR/$STATE_DIR/previous-sha.txt"

cd "$APP_DIR"

if [ ! -s "$PREVIOUS_SHA_FILE" ]; then
  echo "ERROR: no previous SHA stored at $PREVIOUS_SHA_FILE" >&2
  exit 1
fi

previous_sha="$(cat "$PREVIOUS_SHA_FILE")"
echo "Rolling back to $previous_sha"

git fetch --all --prune
git reset --hard "$previous_sha"

docker compose $COMPOSE_FILES build ragforge-api
docker compose $COMPOSE_FILES up -d --remove-orphans
scripts/deployment/ragforge-healthcheck.sh

echo "Rollback completed: $previous_sha"
