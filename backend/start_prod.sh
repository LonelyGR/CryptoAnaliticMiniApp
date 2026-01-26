#!/usr/bin/env bash
set -euo pipefail

# Production start (without docker)
# Requires: pip install -r requirements.txt && pip install gunicorn

export HOST="${HOST:-0.0.0.0}"
export PORT="${PORT:-8000}"
export WORKERS="${WORKERS:-2}"

exec gunicorn -k uvicorn.workers.UvicornWorker "app.main:app" \
  --bind "${HOST}:${PORT}" \
  --workers "${WORKERS}" \
  --timeout 60

