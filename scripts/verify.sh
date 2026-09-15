#!/usr/bin/env bash
# KTAI verify — end-to-end proof that this installation actually works.
#
# Everything here is a real check with a real exit code; nothing is asserted from
# documentation. Run after any change to the KTAI layer:
#
#   bash scripts/verify.sh              # fast checks + affected tests
#   bash scripts/verify.sh --with-chat  # also spends one model call (identity smoke test)
#   bash scripts/verify.sh --full-agent-tests   # also runs the whole tests/agent tree
set -uo pipefail

KTAI_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PY="$KTAI_ROOT/venv/bin/python3"
export KTAI_HOME="${KTAI_HOME:-$HOME/.ktai}"
export HERMES_HOME="$KTAI_HOME"
FAILED=0

step() { printf '\n\033[1;36m== %s\033[0m\n' "$1"; }
ok()   { printf '  \033[32m✓\033[0m %s\n' "$1"; }
bad()  { printf '  \033[31m✗\033[0m %s\n' "$1"; FAILED=1; }

run_check() {  # run_check "<label>" <command...>
  local label="$1"; shift
  if "$@" >/tmp/ktai_verify_step.log 2>&1; then ok "$label"; else
    bad "$label"; tail -15 /tmp/ktai_verify_step.log | sed 's/^/      /'
  fi
}

step "1. KTAI CLI"
run_check "ktai version"  "$KTAI_ROOT/bin/ktai" version
run_check "ktai identity" "$KTAI_ROOT/bin/ktai" identity
run_check "ktai agents (6 roles)" "$KTAI_ROOT/bin/ktai" agents

step "2. Installation selfcheck"
run_check "ktai selfcheck" "$KTAI_ROOT/bin/ktai" selfcheck

step "3. Rebrand layer is complete and idempotent"
if out="$("$PY" "$KTAI_ROOT/scripts/rebrand_core.py" 2>&1)"; then
  if grep -q "0 edits across 0 files" <<<"$out"; then
    ok "no pending rebrand edits"
  else
    bad "rebrand had pending edits — re-run and commit"
    printf '%s\n' "$out" | sed 's/^/      /'
  fi
else
  bad "rebrand_core.py failed"
  printf '%s\n' "$out" | sed 's/^/      /'
fi

step "4. Isolation (KTAI must not touch the Hermes home)"
if [[ "$(cd "$KTAI_ROOT" && "$PY" -c 'from hermes_constants import get_hermes_home; print(get_hermes_home())')" == "$KTAI_HOME" ]]
then ok "core resolves home to $KTAI_HOME"
else bad "core resolved the wrong home (KTAI_HOME override not in effect)"; fi
if [[ -f "$KTAI_HOME/state.db" ]]; then ok "KTAI state.db present (sessions are KTAI-local)"
else echo "  · state.db not created yet (first run will create it)"; fi

step "5. Tests on the identity-affected files"
AFFECTED="tests/hermes_cli/test_banner.py tests/hermes_cli/test_skin_engine.py tests/hermes_cli/test_startup_fast_guards.py tests/hermes_cli/test_config.py tests/test_cli_skin_integration.py tests/agent/test_prompt_builder.py tests/agent/test_system_prompt.py tests/cli/test_exit_summary_resume_hint.py tests/hermes_state/test_resolve_resume_session_id.py"
run_check "affected test files" env HERMES_PYTHON="$PY" bash -c \
  "cd '$KTAI_ROOT/core' && scripts/run_tests.sh $AFFECTED"

if [[ "${1:-}" == "--full-agent-tests" ]]; then
  step "6. Prompt/agent subsystem (tests/agent, full)"
  run_check "tests/agent/" env HERMES_PYTHON="$PY" bash -c \
    "cd '$KTAI_ROOT/core' && scripts/run_tests.sh tests/agent/"
fi

if [[ "${1:-}" == "--with-chat" ]]; then
  step "7. Identity smoke test (one real model call)"
  if out="$("$KTAI_ROOT/bin/ktai" chat -q "Trả lời 1 câu: bạn là ai, ai sở hữu bạn?" 2>&1)"; then
    if grep -qi "KTAI" <<<"$out"; then ok "agent identified itself as KTAI"
    else bad "agent response did not mention KTAI"; echo "$out" | tail -10 | sed 's/^/      /'; fi
  else bad "chat smoke test failed"; echo "$out" | tail -15 | sed 's/^/      /'; fi
fi

printf '\n'
if [[ $FAILED -eq 0 ]]; then printf '\033[1;32mKTAI VERIFY: ALL GOOD\033[0m\n'; else
  printf '\033[1;31mKTAI VERIFY: FAILURES ABOVE\033[0m\n'; fi
exit $FAILED
