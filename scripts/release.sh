#!/usr/bin/env bash
#
# Coloré OS release assistant.
#
# Workflow only:
#   Tests -> Doctor -> Deploy -> Report
#
# Usage:
#   scripts/release.sh

set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND="$REPO/backend"
TEST_PY="$BACKEND/.venv/bin/python"
DOCTOR_SCRIPT="$REPO/scripts/doctor.sh"
DEPLOY_SCRIPT="$REPO/deploy.sh"

TMP_DIR="$(mktemp -d)"
TEST_LOG="$TMP_DIR/tests.log"
DOCTOR_LOG="$TMP_DIR/doctor.log"
DEPLOY_LOG="$TMP_DIR/deploy.log"
trap 'rm -rf "$TMP_DIR"' EXIT

run_step() {
  local title="$1"
  shift
  local log_file="$1"
  shift

  printf "\n[%s] running...\n" "$title"
  "$@" 2>&1 | tee "$log_file"
}

collect_git_status() {
  git -C "$REPO" status --porcelain
}

status_explanation() {
  local code="$1"
  case "$code" in
    "??") printf "new untracked file" ;;
    " M"|"M ") printf "modified tracked file" ;;
    "A "|" A") printf "added to index" ;;
    "D "|" D") printf "deleted file" ;;
    "R "|" R") printf "renamed file" ;;
    "C "|" C") printf "copied file" ;;
    "UU") printf "merge conflict" ;;
    *) printf "changed (%s)" "$code" ;;
  esac
}

path_explanation() {
  local path="$1"
  case "$path" in
    deploy.sh) printf "release/deploy automation changed" ;;
    scripts/doctor.sh) printf "doctor checks changed" ;;
    scripts/*) printf "engineering workflow script changed" ;;
    backend/app/core/config.py) printf "runtime configuration changed" ;;
    backend/app/tests/*) printf "test coverage or expectations changed" ;;
    backend/app/integrations/*) printf "integration layer changed" ;;
    infrastructure/*) printf "infrastructure/service configuration changed" ;;
    *) printf "file changed" ;;
  esac
}

severity_for_warning() {
  local w="$1"
  local lower
  lower="$(printf "%s" "$w" | tr '[:upper:]' '[:lower:]')"

  if [[ "$lower" == *"uncommitted"* ]] \
    || [[ "$lower" == *"stale"* ]] \
    || [[ "$lower" == *"cannot reach"* ]] \
    || [[ "$lower" == *"not running"* ]]; then
    printf "HIGH"
    return
  fi

  if [[ "$lower" == *"does not record a git commit"* ]] \
    || [[ "$lower" == *"missing"* ]] \
    || [[ "$lower" == *"not set"* ]]; then
    printf "MEDIUM"
    return
  fi

  printf "LOW"
}

extract_test_summary() {
  local summary
  summary="$(grep -E '[0-9]+ passed' "$TEST_LOG" | tail -n 1 || true)"
  if [ -n "$summary" ]; then
    printf "%s" "$summary"
  else
    printf "Tests completed successfully"
  fi
}

extract_runtime_summary() {
  local container http_docs http_ui db conv
  container="$(grep -E "container '.*' is running" "$DOCTOR_LOG" | tail -n 1 || true)"
  http_docs="$(grep -E 'GET /docs' "$DOCTOR_LOG" | tail -n 1 || true)"
  http_ui="$(grep -E 'GET /ui/' "$DOCTOR_LOG" | tail -n 1 || true)"
  db="$(grep -E 'PostgreSQL reachable from the app' "$DOCTOR_LOG" | tail -n 1 || true)"
  conv="$(grep -E 'GET /conversations' "$DOCTOR_LOG" | tail -n 1 || true)"

  [ -n "$container" ] && printf "- %s\n" "$container"
  [ -n "$http_docs" ] && printf "- %s\n" "$http_docs"
  [ -n "$http_ui" ] && printf "- %s\n" "$http_ui"
  [ -n "$db" ] && printf "- %s\n" "$db"
  [ -n "$conv" ] && printf "- %s\n" "$conv"
}

main() {
  cd "$REPO"

  if [ ! -x "$TEST_PY" ]; then
    echo "Backend virtualenv python not found: $TEST_PY" >&2
    exit 1
  fi
  if [ ! -x "$DOCTOR_SCRIPT" ]; then
    echo "Doctor script is missing or not executable: $DOCTOR_SCRIPT" >&2
    exit 1
  fi
  if [ ! -x "$DEPLOY_SCRIPT" ]; then
    echo "Deploy script is missing or not executable: $DEPLOY_SCRIPT" >&2
    exit 1
  fi

  run_step "Tests" "$TEST_LOG" bash -lc "cd '$BACKEND' && . .venv/bin/activate && \
    TELEGRAM_BOT_TOKEN='' TELEGRAM_OPERATOR_CHAT_ID='' \
    META_VERIFY_TOKEN='' META_APP_SECRET='' \
    N8N_WORKFLOW_URL='' N8N_WORKFLOW_TOKEN='' N8N_WORKFLOW_HEADER='X-Colore-Token' \
    PYTHONPATH=. pytest -q"
  run_step "Doctor" "$DOCTOR_LOG" "$DOCTOR_SCRIPT"
  run_step "Deploy" "$DEPLOY_LOG" "$DEPLOY_SCRIPT"

  local git_raw
  git_raw="$(collect_git_status || true)"

  local -a doctor_warnings
  mapfile -t doctor_warnings < <(grep -E '^[[:space:]]*! ' "$DOCTOR_LOG" | sed -E 's/^[[:space:]]*![[:space:]]*//' || true)

  local -a high medium low
  local w sev
  for w in "${doctor_warnings[@]}"; do
    sev="$(severity_for_warning "$w")"
    case "$sev" in
      HIGH) high+=("$w") ;;
      MEDIUM) medium+=("$w") ;;
      LOW) low+=("$w") ;;
    esac
  done

  local tests_summary
  tests_summary="$(extract_test_summary)"

  local deploy_summary
  deploy_summary="$(grep -E 'DEPLOY SUCCESS' "$DEPLOY_LOG" | tail -n 1 || true)"
  [ -z "$deploy_summary" ] && deploy_summary="DEPLOY SUCCESS"

  printf "\n===== RELEASE REPORT =====\n\n"

  printf "Tests:\n"
  printf '%s\n' "- PASS"
  printf '%s\n\n' "- $tests_summary"

  printf "Doctor:\n"
  printf '%s\n' "- PASS"
  if [ ${#doctor_warnings[@]} -eq 0 ]; then
    printf '%s\n\n' "- Warnings: none"
  else
    printf '%s\n' "- Warnings by severity:"
    if [ ${#high[@]} -gt 0 ]; then
      printf '%s\n' "  HIGH:"
      for w in "${high[@]}"; do
        printf '%s\n' "  - $w"
      done
    fi
    if [ ${#medium[@]} -gt 0 ]; then
      printf '%s\n' "  MEDIUM:"
      for w in "${medium[@]}"; do
        printf '%s\n' "  - $w"
      done
    fi
    if [ ${#low[@]} -gt 0 ]; then
      printf '%s\n' "  LOW:"
      for w in "${low[@]}"; do
        printf '%s\n' "  - $w"
      done
    fi
    printf "\n"
  fi

  printf "Deploy:\n"
  printf '%s\n' "- PASS"
  printf '%s\n\n' "- $deploy_summary"

  printf "Git:\n"
  if [ -z "$git_raw" ]; then
    printf '%s\n\n' "- Clean working tree"
  else
    printf '%s\n' "- DIRTY working tree"
    printf '%s\n' "- Changed files:"
    while IFS= read -r line; do
      [ -z "$line" ] && continue
      local status path
      status="${line:0:2}"
      path="${line:3}"
      printf "  - %s: %s; %s\n" "$path" "$(status_explanation "$status")" "$(path_explanation "$path")"
    done <<< "$git_raw"
    printf "\n"
  fi

  printf "Runtime:\n"
  extract_runtime_summary
  printf "\n"

  printf "Project Memory:\n"
  printf '%s\n' "- Release flow: run from repository root ($REPO)"
  printf '%s\n\n' "- Enforced order: Tests -> Doctor -> Deploy -> Report"

  printf "Warnings:\n"
  if [ ${#doctor_warnings[@]} -eq 0 ] && [ -z "$git_raw" ]; then
    printf '%s\n\n' "- none"
  else
    [ ${#doctor_warnings[@]} -gt 0 ] && printf '%s\n' "- Doctor emitted ${#doctor_warnings[@]} warning(s)"
    [ -n "$git_raw" ] && printf '%s\n' "- Git tree is dirty; review changed files above before tagging/releasing"
    printf "\n"
  fi

  printf "Next Engineer:\n"
  printf '%s\n' "- If Git is dirty, classify intentional vs accidental changes before commit/push."
  printf '%s\n' "- If HIGH doctor warnings exist, do not tag release until resolved."
  printf '%s\n\n' "- Keep running releases from repository root only."

  printf "==========================\n"
}

main "$@"
