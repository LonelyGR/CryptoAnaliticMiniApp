#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "[deploy] pulling git changes (if repo has remote)..."
git rev-parse --is-inside-work-tree >/dev/null 2>&1 && git pull --ff-only || true

echo "[deploy] starting prod stack..."
docker compose -f docker-compose.prod.yml up -d --build

echo "[deploy] quick checks..."
DOMAIN="${DOMAIN:-}"
if [[ -n "$DOMAIN" ]]; then
  curl -fsSI "https://${DOMAIN}/" >/dev/null
  curl -fsSI "https://${DOMAIN}/api/" >/dev/null || true
fi

echo "[deploy] done"

