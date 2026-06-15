#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEFAULT_APP_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

APP_DIR="${RAGFORGE_APP_DIR:-$DEFAULT_APP_DIR}"
RAGFORGE_DEPLOY_ROOT="${RAGFORGE_DEPLOY_ROOT:-$HOME/deployment}"
BACKUP_DIR="${RAGFORGE_BACKUP_DIR:-$RAGFORGE_DEPLOY_ROOT/backups/ragforge}"
COMPOSE_FILES="${RAGFORGE_COMPOSE_FILES:--f docker/docker-compose.production.yml -f docker/docker-compose.production.hardened.yml}"
TIMESTAMP="$(date -u +%Y%m%dT%H%M%SZ)"
RELEASE_SHA="$(cd "$APP_DIR" && git rev-parse --short HEAD 2>/dev/null || echo unknown)"
TARGET_DIR="$BACKUP_DIR/$TIMESTAMP-$RELEASE_SHA"

mkdir -p "$TARGET_DIR"
cd "$APP_DIR"

echo "Creating lightweight deployment backup in $TARGET_DIR"
git rev-parse HEAD > "$TARGET_DIR/git-sha.txt" || true
docker compose $COMPOSE_FILES config > "$TARGET_DIR/docker-compose.config.yml"
docker compose $COMPOSE_FILES ps > "$TARGET_DIR/docker-compose.ps.txt" || true
cp -a docker/env "$TARGET_DIR/env.snapshot" 2>/dev/null || true

echo "$TARGET_DIR"
