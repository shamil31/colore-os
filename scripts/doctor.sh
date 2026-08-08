#!/usr/bin/env bash
#
# Coloré OS system doctor.
#
# Diagnostic only: this script never writes, fixes, rebuilds or restarts
# anything. It reports what is wrong and exits non-zero so it can be used
# as a gate before a demo.
#
# Usage:  scripts/doctor.sh

set -uo pipefail

REPO="${REPO:-/root/colore-os}"
BACKEND="$REPO/backend"
COMPOSE_FILE="${COMPOSE_FILE:-/opt/colore-os/docker/docker-compose.yml}"
CONTAINER="${CONTAINER:-colore-backend}"
BASE_URL="${BASE_URL:-http://localhost:8000}"
EXPECTED_CONTEXT="$BACKEND"
PY="$BACKEND/.venv/bin/python"

PROBLEMS=()

if [ -t 1 ]; then
  G=$'\033[32m'; R=$'\033[31m'; Y=$'\033[33m'; B=$'\033[1m'; N=$'\033[0m'
else
  G=''; R=''; Y=''; B=''; N=''
fi

ok()   { printf "  %s✓%s %s\n" "$G" "$N" "$1"; }
bad()  { printf "  %s✗%s %s\n" "$R" "$N" "$1"; PROBLEMS+=("$1"); }
warn() { printf "  %s!%s %s\n" "$Y" "$N" "$1"; }
note() { printf "      %s\n" "$1"; }
head_() { printf "\n%s%s%s\n" "$B" "$1" "$N"; }

http_code() {
  local code
  code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 10 "$1" 2>/dev/null)
  printf '%s' "${code:-000}"
}

# ---------------------------------------------------------------- deployment

head_ "Deployment"

if [ ! -f "$COMPOSE_FILE" ]; then
  bad "compose file not found: $COMPOSE_FILE"
  CONFIGURED_CONTEXT=""
else
  CONFIGURED_CONTEXT=$(grep -A12 '^  backend:' "$COMPOSE_FILE" \
    | grep -E '^\s*context:' | head -1 | sed 's/.*context:[[:space:]]*//')
  if [ "$CONFIGURED_CONTEXT" = "$EXPECTED_CONTEXT" ]; then
    ok "build context in compose: $CONFIGURED_CONTEXT"
  else
    bad "build context in compose is '$CONFIGURED_CONTEXT', expected '$EXPECTED_CONTEXT'"
    note "the archived clone at /opt/colore-os/app/backend must never be built"
  fi
fi

STRAY=$(grep -rln "/opt/colore-os/app/backend" "$REPO" \
          --include="*.yml" --include="*.yaml" --include="*.py" 2>/dev/null \
        | xargs -r grep -l "context:.*opt/colore-os/app/backend" 2>/dev/null)
if [ -z "$STRAY" ]; then
  ok "no compose file in the repository builds from the archived clone"
else
  bad "these files still build from the archived clone: $(echo "$STRAY" | tr '\n' ' ')"
fi

# ---------------------------------------------------------------- container

head_ "Container and image"

if ! command -v docker >/dev/null 2>&1; then
  bad "docker is not available on PATH"
  CONTAINER_UP=""
elif ! docker ps --format '{{.Names}}' 2>/dev/null | grep -qx "$CONTAINER"; then
  bad "container '$CONTAINER' is not running"
  CONTAINER_UP=""
else
  CONTAINER_UP=1
  ok "container '$CONTAINER' is running ($(docker ps --filter "name=^${CONTAINER}$" --format '{{.Status}}'))"
fi

if [ -n "$CONTAINER_UP" ]; then
  IMAGE_ID=$(docker inspect "$CONTAINER" --format '{{.Image}}' 2>/dev/null | cut -c8-19)
  IMAGE_NAME=$(docker inspect "$CONTAINER" --format '{{.Config.Image}}' 2>/dev/null)
  IMAGE_CREATED=$(docker image inspect "$IMAGE_NAME" --format '{{.Created}}' 2>/dev/null | cut -c1-19)
  LATEST_ID=$(docker image inspect "$IMAGE_NAME" --format '{{.Id}}' 2>/dev/null | cut -c8-19)
  ok "image $IMAGE_NAME built $IMAGE_CREATED"
  if [ -n "$LATEST_ID" ] && [ "$IMAGE_ID" != "$LATEST_ID" ]; then
    bad "container runs image $IMAGE_ID but $IMAGE_NAME is now $LATEST_ID — container is stale"
    note "rebuild picked up but 'docker compose up -d backend' was not run"
  else
    ok "container runs the current $IMAGE_NAME image ($IMAGE_ID)"
  fi

  RUNTIME_CONTEXT=$(docker exec "$CONTAINER" printenv BUILD_CONTEXT 2>/dev/null)
  if [ "$RUNTIME_CONTEXT" = "$EXPECTED_CONTEXT" ]; then
    ok "image reports build context: $RUNTIME_CONTEXT"
  elif [ -z "$RUNTIME_CONTEXT" ]; then
    bad "image does not report BUILD_CONTEXT — built before hardening, or built elsewhere"
  else
    bad "image reports build context '$RUNTIME_CONTEXT', expected '$EXPECTED_CONTEXT'"
  fi
fi

# ---------------------------------------------------------------- git commit

head_ "Code version"

REPO_COMMIT=$(git -C "$REPO" rev-parse --short HEAD 2>/dev/null || echo "")
if [ -n "$REPO_COMMIT" ]; then
  ok "repository HEAD: $REPO_COMMIT ($(git -C "$REPO" log -1 --format=%s | cut -c1-50))"
  DIRTY=$(git -C "$REPO" status --porcelain 2>/dev/null | grep -c . || true)
  [ "$DIRTY" -gt 0 ] && warn "$DIRTY uncommitted file(s) in the repository"
else
  bad "cannot read git HEAD in $REPO"
fi

if [ -n "$CONTAINER_UP" ]; then
  IMAGE_COMMIT=$(docker exec "$CONTAINER" printenv GIT_COMMIT 2>/dev/null)
  if [ -z "$IMAGE_COMMIT" ] || [ "$IMAGE_COMMIT" = "unknown" ]; then
    warn "image does not record a git commit (build without GIT_COMMIT arg)"
  elif [ "$IMAGE_COMMIT" = "$REPO_COMMIT" ]; then
    ok "image commit matches repository HEAD: $IMAGE_COMMIT"
  else
    bad "image was built from $IMAGE_COMMIT but repository HEAD is $REPO_COMMIT"
    note "the running container does not contain the current code"
  fi
fi

# ---------------------------------------------------------------- config

head_ "Configuration"

if [ -n "$CONTAINER_UP" ]; then
  # Presence only. The key value is never read or printed.
  if docker exec "$CONTAINER" sh -c '[ -n "$OPENAI_API_KEY" ]' 2>/dev/null; then
    ok "OPENAI_API_KEY: YES"
  else
    bad "OPENAI_API_KEY: NO — /ai and /process endpoints will return 503"
  fi

  ALTEGIO=$(docker exec "$CONTAINER" printenv ALTEGIO_BASE_URL 2>/dev/null)
  if [ -n "$ALTEGIO" ]; then
    ok "ALTEGIO_BASE_URL: $ALTEGIO"
  else
    bad "ALTEGIO_BASE_URL is not set — startup validation will stop the app"
  fi

  MODEL=$(docker exec "$CONTAINER" printenv OPENAI_MODEL 2>/dev/null)
  [ -n "$MODEL" ] && ok "OPENAI_MODEL: $MODEL"
fi

# ---------------------------------------------------------------- http

head_ "HTTP endpoints"

for path in /docs /ui/; do
  code=$(http_code "${BASE_URL}${path}")
  if [ "$code" = "200" ]; then
    ok "GET $path → 200"
  else
    bad "GET $path → $code (expected 200)"
    [ "$path" = "/ui/" ] && note "UI missing usually means app/static/ did not reach the image"
  fi
done

# ---------------------------------------------------------------- database

head_ "Database"

DB_CODE=$(http_code "${BASE_URL}/db")
if [ "$DB_CODE" = "200" ]; then
  PGVER=$(curl -s --max-time 10 "${BASE_URL}/db" 2>/dev/null | sed -n 's/.*"postgres":"\([^"]*\).*/\1/p' | cut -c1-40)
  ok "PostgreSQL reachable from the app (${PGVER:-connected})"
else
  bad "GET /db → $DB_CODE — the app cannot reach PostgreSQL"
fi

# ---------------------------------------------------------------- endpoints

head_ "Conversation endpoint"

# Read-only on purpose: the doctor must not create demo data.
CONV_CODE=$(http_code "${BASE_URL}/conversations")
if [ "$CONV_CODE" = "200" ]; then
  COUNT=$(curl -s --max-time 10 "${BASE_URL}/conversations" 2>/dev/null | grep -o '"id"' | grep -c . || echo 0)
  ok "GET /conversations → 200 ($COUNT conversation(s))"
else
  bad "GET /conversations → $CONV_CODE (expected 200)"
fi

if [ -f "$REPO/backend/app/api/conversations.py" ]; then
  MISSING=""
  for route in '"/{conversation_id}/messages"' '"/{conversation_id}/process"' '"/{conversation_id}/reply"'; do
    grep -q "$route" "$REPO/backend/app/api/conversations.py" || MISSING="$MISSING $route"
  done
  [ -z "$MISSING" ] && ok "conversation routes present in source" \
                    || bad "routes missing from source:$MISSING"
fi

# ---------------------------------------------------------------- tests

head_ "pytest database isolation"

if [ ! -x "$PY" ]; then
  bad "virtualenv python not found at $PY — cannot verify test isolation"
else
  ISO=$(cd "$BACKEND" && "$PY" - <<'PY' 2>/dev/null
try:
    from app.core.config import settings
    from app.tests.testdb import TEST_DATABASE_URL
except Exception as exc:  # noqa: BLE001
    print("ERROR", exc)
else:
    working = settings.DATABASE_URL
    if TEST_DATABASE_URL == working:
        print("SAME")
    elif TEST_DATABASE_URL.startswith("sqlite"):
        print("OK sqlite fallback")
    else:
        print("OK", TEST_DATABASE_URL.rsplit("/", 1)[-1])
PY
)
  case "$ISO" in
    "OK sqlite fallback") ok "tests use a temporary SQLite database (TEST_DATABASE_URL unset)" ;;
    OK*)                  ok "tests use a separate database: ${ISO#OK }" ;;
    SAME)                 bad "tests would run against the WORKING database and drop its tables" ;;
    ERROR*)               bad "cannot resolve the test database: ${ISO#ERROR }" ;;
    *)                    bad "test database isolation could not be determined" ;;
  esac

  if [ -f "$BACKEND/app/tests/testdb.py" ]; then
    grep -q "must not point at the working database" "$BACKEND/app/tests/testdb.py" \
      && ok "guard against TEST_DATABASE_URL == DATABASE_URL is in place" \
      || bad "guard against TEST_DATABASE_URL == DATABASE_URL is missing"
  fi
fi

# --------------------------------------------------------------- salon

head_ "Salon configuration"

if [ ! -x "$PY" ]; then
  bad "virtualenv python not found at $PY — cannot read the salon profile"
else
  SALON_FILE=$(mktemp)
  (cd "$BACKEND" && "$PY" -c "
import json
from app.core.salon import salon_profile
from app.core.config import settings
p = salon_profile()
print(json.dumps({**p.describe(), 'missing': list(p.missing()),
                  'dataset': settings.META_DATASET_ID,
                  'has_token': bool(settings.META_ACCESS_TOKEN)}, ensure_ascii=False))
" >"$SALON_FILE" 2>/dev/null)

  if [ ! -s "$SALON_FILE" ]; then
    bad "salon profile could not be read"
  else
    SALON_NAME=$("$PY" -c "import json,sys;print(json.load(open(sys.argv[1])).get('name') or '')" "$SALON_FILE")
    SALON_COUNTRY=$("$PY" -c "import json,sys;print(json.load(open(sys.argv[1])).get('country') or '')" "$SALON_FILE")
    SALON_TZ=$("$PY" -c "import json,sys;print(json.load(open(sys.argv[1])).get('timezone') or '')" "$SALON_FILE")
    SALON_CUR=$("$PY" -c "import json,sys;print(json.load(open(sys.argv[1])).get('currency') or '')" "$SALON_FILE")
    SALON_MISSING=$("$PY" -c "import json,sys;print(', '.join(json.load(open(sys.argv[1])).get('missing') or []))" "$SALON_FILE")

    [ -n "$SALON_NAME" ]    && ok "Salon: $SALON_NAME"          || bad "Salon: not configured"
    [ -n "$SALON_COUNTRY" ] && ok "Country: $SALON_COUNTRY"     || bad "Country: not configured"
    [ -n "$SALON_TZ" ]      && ok "Timezone: $SALON_TZ"         || bad "Timezone: not configured"
    if [ -n "$SALON_CUR" ]; then
      ok "Currency: $SALON_CUR"
    else
      bad "Currency: not configured — conversion events would carry no value"
    fi
    [ -n "$SALON_MISSING" ] && note "missing: $SALON_MISSING"
  fi
  rm -f "$SALON_FILE"
fi

# ------------------------------------------------------------- meta dataset

head_ "Meta dataset"

if [ ! -x "$PY" ]; then
  warn "cannot verify the dataset: virtualenv python not found"
else
  DS_FILE=$(mktemp)
  # Read-only: fetches the dataset's own id and name. The token is taken from
  # settings and never printed.
  (cd "$BACKEND" && "$PY" -c "
import json
import requests
from app.core.config import settings

dataset = (settings.META_DATASET_ID or '').strip()
token = (settings.META_ACCESS_TOKEN or '').strip()
out = {'dataset': dataset, 'configured': bool(dataset), 'has_token': bool(token)}

if dataset and token:
    try:
        r = requests.get(
            f'https://graph.facebook.com/{settings.META_API_VERSION}/{dataset}',
            params={'fields': 'id,name'},
            headers={'Authorization': f'Bearer {token}'},
            timeout=15,
        )
        body = r.json()
        out['status_code'] = r.status_code
        if 'error' in body:
            out['error'] = body['error'].get('message', '')[:160]
        else:
            out['name'] = body.get('name', '')
            out['reachable'] = True
    except Exception as exc:
        out['error'] = f'{type(exc).__name__}: {exc}'[:160]

print(json.dumps(out, ensure_ascii=False))
" >"$DS_FILE" 2>/dev/null)

  if [ ! -s "$DS_FILE" ]; then
    bad "Meta dataset check could not run"
  else
    DS_ID=$("$PY" -c "import json,sys;print(json.load(open(sys.argv[1])).get('dataset') or '')" "$DS_FILE")
    DS_OK=$("$PY" -c "import json,sys;print('1' if json.load(open(sys.argv[1])).get('reachable') else '')" "$DS_FILE")
    DS_NAME=$("$PY" -c "import json,sys;print(json.load(open(sys.argv[1])).get('name') or '')" "$DS_FILE")
    DS_ERR=$("$PY" -c "import json,sys;print(json.load(open(sys.argv[1])).get('error') or '')" "$DS_FILE")
    DS_TOK=$("$PY" -c "import json,sys;print('1' if json.load(open(sys.argv[1])).get('has_token') else '')" "$DS_FILE")

    if [ -z "$DS_ID" ]; then
      bad "META_DATASET_ID is not configured — nothing can be sent"
    elif [ -z "$DS_TOK" ]; then
      bad "dataset $DS_ID configured but META_ACCESS_TOKEN is absent"
    elif [ -n "$DS_OK" ]; then
      ok "dataset $DS_ID reachable (${DS_NAME:-unnamed})"
    else
      bad "dataset $DS_ID is NOT reachable: ${DS_ERR:-unknown error}"
    fi
  fi
  rm -f "$DS_FILE"
fi

# ---------------------------------------------------------------- scheduler

head_ "Integration scheduler"

if ! systemctl list-unit-files colore-scheduler.service >/dev/null 2>&1 \
   || ! systemctl cat colore-scheduler >/dev/null 2>&1; then
  warn "colore-scheduler is not installed — no integration job will ever run"
elif [ "$(systemctl is-active colore-scheduler 2>/dev/null)" = "active" ]; then
  ok "scheduler running ($(systemctl show -p ActiveEnterTimestamp --value colore-scheduler | cut -c1-19))"
else
  bad "colore-scheduler is not running — queued events will never be sent"
fi

if [ ! -x "$PY" ]; then
  warn "cannot read job status: virtualenv python not found"
else
  SCHED_FILE=$(mktemp)
  # The status JSON goes through a file, not a pipe: the reader below is a
  # heredoc, and a heredoc already owns stdin.
  (cd "$BACKEND" && "$PY" -m app.scheduler.runner --status >"$SCHED_FILE" 2>/dev/null)
  if [ ! -s "$SCHED_FILE" ]; then
    bad "scheduler status could not be read"
    rm -f "$SCHED_FILE"
  else
    "$PY" - "$SCHED_FILE" <<'PY'
import json, sys

try:
    with open(sys.argv[1], encoding="utf-8") as handle:
        data = json.load(handle)
except Exception as exc:  # noqa: BLE001
    print(f"  \033[31m✗\033[0m scheduler status is not readable: {exc}")
    raise SystemExit(1)

jobs = data.get("jobs", [])
failing = data.get("failing", [])

if not jobs:
    print("  \033[31m✗\033[0m no integration jobs are registered")
    raise SystemExit(1)

print(f"  \033[32m✓\033[0m registered jobs: {len(jobs)}")
for job in jobs:
    name = job["name"]
    last = job.get("last_run_at") or "never"
    nxt = job.get("next_run_at") or "not scheduled"
    status = job.get("last_status") or "-"
    mark = "\033[32m✓\033[0m" if status in ("success", "skipped", "-") else "\033[31m✗\033[0m"
    print(f"  {mark} {name}: last {last[:19]} ({status}), next {nxt[:19]}")
    if not job.get("available", True):
        print(f"      unavailable: {job.get('unavailable_reason','')}")
    if job.get("last_error"):
        print(f"      last error: {job['last_error'][:90]}")

if failing:
    print(f"  \033[31m✗\033[0m failed jobs: {', '.join(failing)}")
    raise SystemExit(1)

print("  \033[32m✓\033[0m failed jobs: none")
PY
    SCHED_RC=$?
    rm -f "$SCHED_FILE"
    [ "$SCHED_RC" -ne 0 ] && PROBLEMS+=("integration scheduler reports a problem")
  fi
fi

# ---------------------------------------------------------------- verdict

printf "\n"
if [ ${#PROBLEMS[@]} -eq 0 ]; then
  printf "%s✅ SYSTEM HEALTHY%s\n" "$G" "$N"
  exit 0
fi

printf "%s❌ %d PROBLEM(S)%s\n" "$R" "${#PROBLEMS[@]}" "$N"
for p in "${PROBLEMS[@]}"; do
  printf "   - %s\n" "$p"
done
exit 1
