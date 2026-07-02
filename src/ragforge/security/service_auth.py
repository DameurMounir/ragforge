"""Fail-closed service-to-service bearer authentication.

The token is loaded from a root-managed, read-only file.  It is never accepted
from a plaintext environment variable, command line, query string, or cookie.
"""

from __future__ import annotations

import hmac
import os
import stat
from dataclasses import dataclass
from pathlib import Path

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.ragforge.core.config import Settings, get_settings


_SERVICE_BEARER = HTTPBearer(
    auto_error=False,
    scheme_name="RAGForgeServiceBearer",
    description=(
        "Service-to-service bearer credential loaded from a protected file. "
        "The credential value must never be placed in OpenAPI, logs, URLs, or source."
    ),
)


@dataclass(frozen=True, slots=True)
class ServiceIdentity:
    """Authenticated calling-service identity."""

    authentication_type: str = "service_bearer"


def _unauthorized() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Service authentication required.",
        headers={"WWW-Authenticate": "Bearer"},
    )


def load_service_auth_token(settings: Settings) -> str:
    """Load and validate the configured token without following symlinks."""

    raw_path = settings.SERVICE_AUTH_TOKEN_FILE
    if not raw_path:
        raise RuntimeError("SERVICE_AUTH_TOKEN_FILE is not configured.")

    path = Path(raw_path)
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW

    try:
        descriptor = os.open(path, flags)
    except OSError as exc:
        raise RuntimeError("Service authentication token file is unavailable.") from exc

    try:
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode):
            raise RuntimeError("Service authentication token must be a regular file.")
        if before.st_nlink != 1:
            raise RuntimeError(
                "Service authentication token file must have one hard link."
            )
        expected_uid = settings.SERVICE_AUTH_TOKEN_EXPECTED_OWNER_UID
        if expected_uid is None or before.st_uid != expected_uid:
            raise RuntimeError("Service authentication token file owner is invalid.")
        if stat.S_IMODE(before.st_mode) & 0o177:
            raise RuntimeError(
                "Service authentication token file permissions are too broad."
            )
        if before.st_size < settings.SERVICE_AUTH_MIN_TOKEN_BYTES:
            raise RuntimeError("Service authentication token is too short.")
        if before.st_size > settings.SERVICE_AUTH_MAX_TOKEN_BYTES:
            raise RuntimeError("Service authentication token is too large.")

        data = os.read(descriptor, settings.SERVICE_AUTH_MAX_TOKEN_BYTES + 1)
        after = os.fstat(descriptor)
        immutable_identity = (
            before.st_dev,
            before.st_ino,
            before.st_size,
            before.st_mtime_ns,
        )
        if immutable_identity != (
            after.st_dev,
            after.st_ino,
            after.st_size,
            after.st_mtime_ns,
        ):
            raise RuntimeError("Service authentication token changed while being read.")
    finally:
        os.close(descriptor)

    if len(data) != before.st_size:
        raise RuntimeError("Service authentication token read was incomplete.")

    try:
        token = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise RuntimeError("Service authentication token is not valid UTF-8.") from exc

    if not token.isascii():
        raise RuntimeError(
            "Service authentication token must contain ASCII characters only."
        )
    if any(character.isspace() for character in token):
        raise RuntimeError("Service authentication token must not contain whitespace.")
    if len(data) < settings.SERVICE_AUTH_MIN_TOKEN_BYTES:
        raise RuntimeError("Service authentication token is too short.")
    return token


async def require_service_identity(
    credentials: HTTPAuthorizationCredentials | None = Security(_SERVICE_BEARER),
    settings: Settings = Depends(get_settings),
) -> ServiceIdentity:
    """Authenticate a trusted service; production always fails closed."""

    if not settings.SERVICE_AUTH_ENABLED:
        if settings.is_production_environment:
            raise RuntimeError("Production service authentication is disabled.")
        return ServiceIdentity(authentication_type="disabled_nonproduction")

    if credentials is None or credentials.scheme.lower() != "bearer":
        raise _unauthorized()

    try:
        expected = load_service_auth_token(settings)
    except RuntimeError:
        # A missing or unsafe secret source is a server configuration failure,
        # not an authentication oracle.  Never return file details to callers.
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service authentication is unavailable.",
        ) from None

    if not hmac.compare_digest(credentials.credentials, expected):
        raise _unauthorized()

    return ServiceIdentity()
