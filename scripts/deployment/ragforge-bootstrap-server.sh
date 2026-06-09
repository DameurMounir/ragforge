#!/usr/bin/env bash
set -Eeuo pipefail

DEPLOY_USER="${RAGFORGE_DEPLOY_USER:-ragforge_deploy}"
APP_ROOT="${RAGFORGE_APP_ROOT:-/opt/ragforge}"
APP_DIR="$APP_ROOT/app"
REPO_SSH_URL="${RAGFORGE_REPO_SSH_URL:-git@github.com:DameurMounir/ragforge.git}"
BRANCH="${RAGFORGE_DEPLOY_BRANCH:-main}"

if [ "$(id -u)" -ne 0 ]; then
  echo 'Run this script as root or with sudo.' >&2
  exit 1
fi

apt-get update
apt-get install -y ca-certificates curl gnupg git ufw

if ! command -v docker >/dev/null 2>&1; then
  install -m 0755 -d /etc/apt/keyrings
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
  chmod a+r /etc/apt/keyrings/docker.asc
  . /etc/os-release
  echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $VERSION_CODENAME stable" > /etc/apt/sources.list.d/docker.list
  apt-get update
  apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
fi

id "$DEPLOY_USER" >/dev/null 2>&1 || adduser --disabled-password --gecos '' "$DEPLOY_USER"
usermod -aG docker "$DEPLOY_USER"

mkdir -p "$APP_ROOT" /opt/ragforge/backups
chown -R "$DEPLOY_USER:$DEPLOY_USER" "$APP_ROOT" /opt/ragforge/backups

if [ ! -d "$APP_DIR/.git" ]; then
  sudo -u "$DEPLOY_USER" git clone --branch "$BRANCH" "$REPO_SSH_URL" "$APP_DIR"
fi

install -m 0644 "$APP_DIR/deploy/systemd/ragforge-production.service" /etc/systemd/system/ragforge-production.service
systemctl daemon-reload
systemctl enable ragforge-production.service

echo 'Server bootstrap completed. Configure docker/env files before starting the service.'
