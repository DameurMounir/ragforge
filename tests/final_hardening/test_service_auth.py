from __future__ import annotations

import os
from pathlib import Path

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from src.ragforge.core.config import Settings, get_settings
from src.ragforge.security.service_auth import ServiceIdentity, require_service_identity


def _settings(
    token_file: Path, *, enabled: bool = True, environment: str = "test"
) -> Settings:
    return Settings(
        APP_ENV=environment,
        SERVICE_AUTH_ENABLED=enabled,
        SERVICE_AUTH_TOKEN_FILE=str(token_file),
        SERVICE_AUTH_TOKEN_EXPECTED_OWNER_UID=os.getuid(),
    )


def _client(settings: Settings) -> TestClient:
    app = FastAPI()
    app.dependency_overrides[get_settings] = lambda: settings

    @app.get("/protected")
    async def protected(
        identity: ServiceIdentity = Depends(require_service_identity),
    ) -> dict[str, str]:
        return {"authentication_type": identity.authentication_type}

    return TestClient(app)


def _token_file(tmp_path: Path, token: str = "a" * 48) -> Path:
    path = tmp_path / "service-token"
    path.write_text(token, encoding="utf-8")
    path.chmod(0o400)
    return path


def test_missing_wrong_and_correct_bearer_credentials(tmp_path: Path) -> None:
    token = "a" * 48
    client = _client(_settings(_token_file(tmp_path, token)))
    missing = client.get("/protected")
    wrong = client.get("/protected", headers={"Authorization": "Bearer " + ("b" * 48)})
    correct = client.get("/protected", headers={"Authorization": "Bearer " + token})
    assert missing.status_code == 401
    assert wrong.status_code == 401
    assert correct.status_code == 200
    assert correct.json() == {"authentication_type": "service_bearer"}
    assert token not in missing.text + wrong.text


def test_unsafe_secret_file_is_fail_closed(tmp_path: Path) -> None:
    path = _token_file(tmp_path)
    path.chmod(0o644)
    response = _client(_settings(path)).get(
        "/protected", headers={"Authorization": "Bearer " + ("a" * 48)}
    )
    assert response.status_code == 503
    assert "permissions" not in response.text.lower()


def test_non_ascii_secret_file_is_fail_closed(tmp_path: Path) -> None:
    path = _token_file(tmp_path, "é" * 48)
    response = _client(_settings(path)).get(
        "/protected", headers={"Authorization": "Bearer " + ("a" * 48)}
    )
    assert response.status_code == 503


def test_symlink_and_hardlink_secret_sources_are_rejected(tmp_path: Path) -> None:
    original = _token_file(tmp_path)
    symlink = tmp_path / "service-token-symlink"
    symlink.symlink_to(original)
    hardlink = tmp_path / "service-token-hardlink"
    hardlink.hardlink_to(original)

    for unsafe_path in (symlink, hardlink):
        response = _client(_settings(unsafe_path)).get(
            "/protected", headers={"Authorization": "Bearer " + ("a" * 48)}
        )
        assert response.status_code == 503


def test_nonproduction_can_explicitly_disable_auth(tmp_path: Path) -> None:
    response = _client(_settings(_token_file(tmp_path), enabled=False)).get(
        "/protected"
    )
    assert response.status_code == 200
    assert response.json()["authentication_type"] == "disabled_nonproduction"


def test_production_cannot_disable_auth(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="Production requires"):
        _settings(_token_file(tmp_path), enabled=False, environment="production-docker")
