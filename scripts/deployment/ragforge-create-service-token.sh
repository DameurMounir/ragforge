
#!/usr/bin/env bash
set -Eeuo pipefail
set +H
umask 077

TOKEN_PATH="${RAGFORGE_SERVICE_AUTH_TOKEN_SOURCE:-/etc/ragforge/secrets/service-token}"
OWNER_UID="${RAGFORGE_SERVICE_AUTH_OWNER_UID:-10001}"
OWNER_GID="${RAGFORGE_SERVICE_AUTH_OWNER_GID:-10001}"

[[ "$TOKEN_PATH" = /* ]] || { echo 'absolute token path required' >&2; exit 2; }
[[ "$OWNER_UID" =~ ^[0-9]+$ ]] || { echo 'numeric owner UID required' >&2; exit 2; }
[[ "$OWNER_GID" =~ ^[0-9]+$ ]] || { echo 'numeric owner GID required' >&2; exit 2; }

if [[ "$(id -u)" -ne 0 ]]; then
  echo 'run as root so ownership can be set safely' >&2
  exit 3
fi

if [[ -L "$TOKEN_PATH" ]]; then
  echo 'refusing symlink token path' >&2
  exit 4
fi

if [[ -e "$TOKEN_PATH" ]]; then
  [[ -f "$TOKEN_PATH" ]] || { echo 'token path is not a regular file' >&2; exit 5; }
  [[ "$(stat -c '%u' "$TOKEN_PATH")" = "$OWNER_UID" ]] || { echo 'token owner UID mismatch' >&2; exit 6; }
  [[ "$(stat -c '%g' "$TOKEN_PATH")" = "$OWNER_GID" ]] || { echo 'token owner GID mismatch' >&2; exit 7; }
  [[ "$(stat -c '%a' "$TOKEN_PATH")" = '400' ]] || { echo 'token mode must be 0400' >&2; exit 8; }
  echo 'RAGFORGE_SERVICE_TOKEN_ALREADY_PRESENT'
  exit 0
fi

install -d -m 0700 -o root -g root "$(dirname "$TOKEN_PATH")"
tmp="$(mktemp "$(dirname "$TOKEN_PATH")/.service-token.XXXXXX")"
trap 'rm -f -- "$tmp"' EXIT
python3 - <<'PY' >"$tmp"
import secrets
print(secrets.token_urlsafe(48), end='')
PY
[[ "$(wc -c <"$tmp")" -ge 32 ]] || { echo 'generated token is too short' >&2; exit 9; }
chown "$OWNER_UID:$OWNER_GID" "$tmp"
chmod 0400 "$tmp"
mv -T -- "$tmp" "$TOKEN_PATH"
trap - EXIT
sync -f "$TOKEN_PATH" 2>/dev/null || true
echo 'RAGFORGE_SERVICE_TOKEN_CREATED'
echo "TOKEN_PATH=$TOKEN_PATH"
