#!/usr/bin/env bash
set -Eeuo pipefail

APP_DIR="${RAGFORGE_APP_DIR:-/opt/ragforge/app}"
DEPLOY_BRANCH="${RAGFORGE_DEPLOY_BRANCH:-main}"
COMPOSE_FILES="${RAGFORGE_COMPOSE_FILES:--f docker/docker-compose.production.yml -f docker/docker-compose.production.hardened.yml}"
HEALTHCHECK_SCRIPT="${RAGFORGE_HEALTHCHECK_SCRIPT:-scripts/deployment/ragforge-healthcheck.sh}"
BACKUP_SCRIPT="${RAGFORGE_BACKUP_SCRIPT:-scripts/deployment/ragforge-backup.sh}"
RELEASE_STATE_DIR="${RAGFORGE_RELEASE_STATE_DIR:-deploy/state}"
ENABLE_IMAGE_LOCK_VERIFY="${RAGFORGE_ENABLE_IMAGE_LOCK_VERIFY:-false}"

cd "$APP_DIR"
mkdir -p "$RELEASE_STATE_DIR"

current_sha="$(git rev-parse HEAD 2>/dev/null || true)"
echo "Current SHA: ${current_sha:-none}"

echo 'Fetching latest release candidate...'
git fetch --prune origin "$DEPLOY_BRANCH"
target_sha="$(git rev-parse "origin/$DEPLOY_BRANCH")"
echo "Target SHA: $target_sha"

if [ -n "$current_sha" ]; then
  echo "$current_sha" > "$RELEASE_STATE_DIR/previous-sha.txt"
fi

git checkout "$DEPLOY_BRANCH"
git reset --hard "$target_sha"

chmod +x scripts/deployment/*.sh || true

if [ -x "$BACKUP_SCRIPT" ]; then
  "$BACKUP_SCRIPT" || echo 'WARN: backup script failed; continuing deployment.' >&2
fi

if [ "$ENABLE_IMAGE_LOCK_VERIFY" = "true" ]; then
  scripts/deployment/ragforge-verify-image-lock.sh
fi

echo 'Validating compose configuration...'
docker compose $COMPOSE_FILES config >/tmp/ragforge-compose.config.yml

echo 'Building application image...'
docker compose $COMPOSE_FILES build ragforge-api

echo 'Starting production runtime...'
docker compose $COMPOSE_FILES up -d --remove-orphans

echo 'Waiting for deployment health...'
"$HEALTHCHECK_SCRIPT"

echo "$target_sha" > "$RELEASE_STATE_DIR/current-sha.txt"
date -u +%Y-%m-%dT%H:%M:%SZ > "$RELEASE_STATE_DIR/deployed-at.txt"

echo "RAGForge deployment completed: $target_sha"
