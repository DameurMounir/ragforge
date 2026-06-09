#!/usr/bin/env bash
set -Eeuo pipefail

DOMAIN="${RAGFORGE_DOMAIN:?Set RAGFORGE_DOMAIN before running TLS init.}"
EMAIL="${RAGFORGE_TLS_EMAIL:?Set RAGFORGE_TLS_EMAIL before running TLS init.}"
APP_DIR="${RAGFORGE_APP_DIR:-/opt/ragforge/app}"
COMPOSE_BASE="${RAGFORGE_COMPOSE_BASE:-docker/docker-compose.production.yml}"
COMPOSE_HARDENED="${RAGFORGE_COMPOSE_HARDENED:-docker/docker-compose.production.hardened.yml}"
COMPOSE_HTTPS="${RAGFORGE_COMPOSE_HTTPS:-docker/docker-compose.https.yml}"

cd "$APP_DIR/docker"
mkdir -p certbot/www certbot/conf

if grep -q 'example.com' nginx/default.https.conf; then
  echo "Replacing example.com with $DOMAIN in docker/nginx/default.https.conf"
  sed -i "s/example.com/$DOMAIN/g" nginx/default.https.conf
fi

cd "$APP_DIR"

echo 'Starting Nginx HTTP challenge endpoint...'
docker compose -f "$COMPOSE_BASE" -f "$COMPOSE_HARDENED" -f "$COMPOSE_HTTPS" up -d nginx

echo 'Requesting certificate...'
docker compose -f "$COMPOSE_BASE" -f "$COMPOSE_HARDENED" -f "$COMPOSE_HTTPS" run --rm certbot \
  certonly --webroot -w /var/www/certbot \
  --email "$EMAIL" --agree-tos --no-eff-email \
  -d "$DOMAIN"

echo 'Restarting HTTPS stack...'
docker compose -f "$COMPOSE_BASE" -f "$COMPOSE_HARDENED" -f "$COMPOSE_HTTPS" up -d --remove-orphans

echo 'TLS initialization completed.'
