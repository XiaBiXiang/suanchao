#!/usr/bin/env sh
set -eu

echo "[backend] booting container..."

if [ "${SKIP_MIGRATIONS:-0}" != "1" ]; then
  max_attempts="${MIGRATION_MAX_ATTEMPTS:-30}"
  attempt=1

  echo "[backend] applying alembic migrations..."
  until alembic upgrade head; do
    if [ "$attempt" -ge "$max_attempts" ]; then
      echo "[backend] migration failed after ${max_attempts} attempts"
      exit 1
    fi

    echo "[backend] database not ready yet, retry ${attempt}/${max_attempts} in 2s..."
    attempt=$((attempt + 1))
    sleep 2
  done
fi

port="${PORT:-8000}"
workers="${UVICORN_WORKERS:-1}"

echo "[backend] starting uvicorn at 0.0.0.0:${port} (workers=${workers})"
exec uvicorn app.main:app --host 0.0.0.0 --port "${port}" --workers "${workers}"
