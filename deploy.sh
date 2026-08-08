#!/usr/bin/env bash
#
# Coloré OS — backend deploy.
#
# Updates the repository, rebuilds the backend image, restarts the backend
# container, then runs the system doctor. Any failing step stops the deploy
# immediately.
#
# It also restarts the host-side Growth AI Telegram bot, whose code ships in
# this repository. Without that, a deploy leaves the bot running the previous
# commit — the same stale-code failure the doctor exists to catch for the
# container. Skipped silently when the service is not installed.
#
# This script never repairs anything on its own. It does not run migrations,
# does not run tests, does not touch .env, does not prune Docker, and does not
# rebuild any service other than backend.
#
# Usage:  ./deploy.sh

set -euo pipefail

REPO="${REPO:-/root/colore-os}"
DOCKER_DIR="${DOCKER_DIR:-/opt/colore-os/docker}"
DOCTOR="$REPO/scripts/doctor.sh"
SERVICE="backend"
BASE_URL="${BASE_URL:-http://localhost:8000}"
READY_TIMEOUT="${READY_TIMEOUT:-60}"

fail() {
  echo
  echo "================================"
  echo "❌ DEPLOY FAILED"
  echo
  echo "Deployment stopped."
  echo "See the error above."
  echo "================================"
  exit 1
}

trap fail ERR

echo "================================"
echo "Coloré OS — backend deploy"
echo "================================"
echo "  repository: $REPO"
echo "  compose:    $DOCKER_DIR"
echo "  service:    $SERVICE"
echo

echo "[1/6] Entering the compose directory ..."
cd "$DOCKER_DIR"

echo "[2/6] Updating the repository ..."
git -C "$REPO" pull

# Recorded in the image so the running container can report which commit it
# was built from. See app/core/startup.py and scripts/doctor.sh.
GIT_COMMIT="$(git -C "$REPO" rev-parse --short HEAD)"
export GIT_COMMIT
echo "      commit: $GIT_COMMIT"

echo "[3/6] Building the $SERVICE image ..."
docker compose build "$SERVICE"

echo "[4/6] Restarting the $SERVICE container ..."
docker compose up -d "$SERVICE"

# The container reports Started before uvicorn has bound the port. Without this
# wait the doctor runs against a socket that is not listening yet and every HTTP
# check fails. Nothing is repaired here — if the app never answers, the doctor
# reports it and the deploy fails.
echo "      waiting for $BASE_URL to answer ..."
for _ in $(seq 1 "$READY_TIMEOUT"); do
  if curl -s -o /dev/null --max-time 2 "$BASE_URL/" 2>/dev/null; then
    echo "      ready"
    break
  fi
  sleep 1
done

echo "[5/6] Restarting the host services ..."
for unit in colore-growth-bot colore-scheduler; do
  if systemctl list-unit-files "$unit.service" >/dev/null 2>&1 \
     && systemctl is-enabled --quiet "$unit" 2>/dev/null; then
    systemctl restart "$unit"
    echo "      $unit: $(systemctl is-active "$unit")"
  else
    echo "      $unit is not installed — skipped"
  fi
done

echo "[6/6] Running the system doctor ..."
if [ ! -x "$DOCTOR" ]; then
  echo "doctor not found or not executable: $DOCTOR" >&2
  fail
fi
"$DOCTOR"

echo
echo "================================"
echo "✅ DEPLOY SUCCESS"
echo
echo "Backend updated successfully."
echo "================================"
exit 0
