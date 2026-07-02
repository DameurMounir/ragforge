#!/usr/bin/env python3
from __future__ import annotations

import ast
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROTECTED_ROUTES = {
    "src/ragforge/routes/documents.py",
    "src/ragforge/routes/indexing.py",
    "src/ragforge/routes/search.py",
    "src/ragforge/routes/answers.py",
    "src/ragforge/routes/llm.py",
}
REQUIRED_MODELS = {
    "HealthResponse",
    "UploadDocumentResponse",
    "ProcessDocumentResponse",
    "IndexingResponse",
    "SemanticSearchResponse",
    "RAGAnswerResponse",
}


def fail(message: str) -> None:
    raise SystemExit(f"RAGFORGE_AUTH_SCHEMA_VALIDATION_FAILED: {message}")


for relative in sorted(PROTECTED_ROUTES):
    text = (ROOT / relative).read_text(encoding="utf-8")
    if "Security(require_service_identity)" not in text:
        fail(f"protected route lacks service authentication: {relative}")

security = (ROOT / "src/ragforge/security/service_auth.py").read_text(encoding="utf-8")
for token in (
    "HTTPBearer(",
    "auto_error=False",
    "hmac.compare_digest",
    "O_NOFOLLOW",
    "st_nlink",
):
    if token not in security:
        fail(f"security control missing: {token}")

classes: set[str] = set()
for path in (ROOT / "src/ragforge/schemas").glob("*.py"):
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    classes.update(
        node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)
    )
missing = sorted(REQUIRED_MODELS - classes)
if missing:
    fail(f"missing response models: {missing}")

compose = (ROOT / "docker/docker-compose.production.yml").read_text(encoding="utf-8")
if "RAGFORGE_SERVICE_AUTH_TOKEN_SOURCE" not in compose or ":ro" not in compose:
    fail("production compose lacks read-only service-token mount")
env = (ROOT / "docker/env/.env.app.example").read_text(encoding="utf-8")
if "SERVICE_AUTH_ENABLED=true" not in env or "SERVICE_AUTH_TOKEN_FILE=" not in env:
    fail("production application environment lacks service-auth settings")
for rel in ("docker/nginx/default.conf", "docker/nginx/default.https.conf"):
    if (
        "proxy_set_header Authorization $http_authorization;"
        not in (ROOT / rel).read_text()
    ):
        fail(f"Authorization forwarding missing: {rel}")

print(
    json.dumps(
        {"status": "valid", "protected_route_files": len(PROTECTED_ROUTES)},
        sort_keys=True,
    )
)
print("RAGFORGE_AUTH_SCHEMA_VALIDATION=PASS")
