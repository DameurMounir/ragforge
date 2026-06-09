#!/usr/bin/env bash
set -Eeuo pipefail

COMPOSE_FILES="${RAGFORGE_COMPOSE_FILES:--f docker/docker-compose.production.yml -f docker/docker-compose.production.hardened.yml}"
MONGO_ADMIN_USER="${MONGO_INITDB_ROOT_USERNAME:-admin}"
MONGO_ADMIN_PASSWORD="${MONGO_INITDB_ROOT_PASSWORD:-admin}"
MONGO_EXPORTER_USERNAME="${MONGO_EXPORTER_USERNAME:-ragforge_mongodb_exporter}"
MONGO_EXPORTER_PASSWORD="${MONGO_EXPORTER_PASSWORD:?Set MONGO_EXPORTER_PASSWORD before running this script.}"

# Run from repository root after the MongoDB service is healthy.
docker compose $COMPOSE_FILES exec -T mongodb mongosh \
  -u "$MONGO_ADMIN_USER" \
  -p "$MONGO_ADMIN_PASSWORD" \
  --authenticationDatabase admin \
  --eval "
    db = db.getSiblingDB('admin');
    if (!db.getUser('$MONGO_EXPORTER_USERNAME')) {
      db.createUser({
        user: '$MONGO_EXPORTER_USERNAME',
        pwd: '$MONGO_EXPORTER_PASSWORD',
        roles: [
          { role: 'clusterMonitor', db: 'admin' },
          { role: 'read', db: 'local' }
        ]
      });
      print('MongoDB exporter user created.');
    } else {
      print('MongoDB exporter user already exists.');
    }
  "
