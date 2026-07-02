from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_production_compose_mounts_secret_read_only() -> None:
    compose = (ROOT / "docker/docker-compose.production.yml").read_text(
        encoding="utf-8"
    )
    assert "RAGFORGE_SERVICE_AUTH_TOKEN_SOURCE" in compose
    assert "/run/ragforge-secrets/service-token:ro" in compose


def test_production_environment_enables_service_auth() -> None:
    env = (ROOT / "docker/env/.env.app.example").read_text(encoding="utf-8")
    assert "SERVICE_AUTH_ENABLED=true" in env
    assert "SERVICE_AUTH_TOKEN_EXPECTED_OWNER_UID=10001" in env


def test_nginx_explicitly_forwards_authorization() -> None:
    for name in ("default.conf", "default.https.conf"):
        text = (ROOT / "docker/nginx" / name).read_text(encoding="utf-8")
        assert "proxy_set_header Authorization $http_authorization;" in text


def test_token_generator_never_prints_token() -> None:
    text = (ROOT / "scripts/deployment/ragforge-create-service-token.sh").read_text(
        encoding="utf-8"
    )
    assert "token_urlsafe" in text
    assert 'cat "$TOKEN_PATH"' not in text
    assert "chmod 0400" in text
