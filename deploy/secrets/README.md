# Branch 23 Secret Handling Policy

RAGForge Branch 23 uses a server-owned secret boundary:

- GitHub Actions stores only deployment connection secrets.
- Application runtime secrets stay on the server.
- Production `.env` files are never committed.
- Server env files must be owned by the deployment user and readable only by that user.

Suggested server paths:

```text
/opt/ragforge/app/docker/env/.env.app
/opt/ragforge/app/docker/env/.env.mongodb
/opt/ragforge/app/docker/env/.env.postgres
/opt/ragforge/app/docker/env/.env.grafana
/opt/ragforge/app/docker/env/.env.postgres-exporter
/opt/ragforge/app/docker/env/.env.mongodb-exporter
```

Suggested permissions:

```bash
chmod 600 /opt/ragforge/app/docker/env/.env.*
chown ragforge_deploy:ragforge_deploy /opt/ragforge/app/docker/env/.env.*
```

Future hardening path:

```text
Docker Compose file-based secrets
Vault / Doppler / Infisical / cloud secret manager
short-lived deployment credentials
machine identity instead of long-lived SSH keys
```
