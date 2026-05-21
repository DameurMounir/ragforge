# Validation Scripts

This folder contains manual validation scripts used during RAGForge development.

These scripts are not production code and they are not unit tests. They are local development utilities used to validate MongoDB metadata behavior.

## Requirements

MongoDB must be running:

```bash
docker compose --env-file docker/.env -f docker/docker-compose.yml up -d
