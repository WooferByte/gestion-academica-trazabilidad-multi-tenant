#!/bin/bash
set -e

echo "================================================"
echo "  activia-trace — API Entrypoint"
echo "================================================"

# ── Wait for PostgreSQL ──────────────────────────────
echo "[1/4] Waiting for postgres..."
for i in $(seq 1 30); do
  if pg_isready -h postgres -U postgres -d trace > /dev/null 2>&1; then
    echo "      ✓ Postgres is ready! (attempt $i)"
    break
  fi
  if [ "$i" -eq 30 ]; then
    echo "      ⚠ Could not verify postgres readiness after 30s, trying migrations anyway..."
  fi
  sleep 1
done

# ── Run Alembic migrations ───────────────────────────
echo "[2/4] Running database migrations..."
if alembic upgrade head; then
  echo "      ✓ Migrations applied successfully"
else
  echo "      ✗ Migration failed!"
  echo "      Retrying once after 5s..."
  sleep 5
  alembic upgrade head
  echo "      ✓ Migrations applied on retry"
fi

# ── Seed data (dev only) ─────────────────────────────
if [ "$RUN_SEED" = "true" ]; then
  echo "[3/4] Running seed data..."
  if python seed.py; then
    echo "      ✓ Seed data loaded"
  else
    echo "      ⚠ Seed data may have partially failed (some records may already exist)"
  fi
else
  echo "[3/4] Skipping seed data (RUN_SEED != true)"
fi

# ── Start uvicorn ────────────────────────────────────
echo "[4/4] Starting API server..."
echo "================================================"
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
