#!/usr/bin/env bash
# KTAI rebuild — reproduce the whole distribution, in order, on this machine.
#
# Steps 1–4 are idempotent and destructive only inside ~/KTAI (never ~/.hermes).
# Step 5 (seed) is additive: it keeps an existing ~/.ktai/config.yaml, .env and skills
# unless you pass --force-seed.
#
#   bash scripts/rebuild.sh                 # full rebuild (core from the repo branch)
#   bash scripts/rebuild.sh --from-hermes   # core + venv from ~/.hermes/hermes-agent
#   bash scripts/rebuild.sh --no-clone      # keep core/ (re-apply brand + venv + seed)
#
# For a machine that has nothing installed yet, use scripts/install.sh instead.
set -euo pipefail

KTAI_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CORE_MODE="auto"
SEED_ARGS=()
VERIFY_ARGS=()
SKIP_CLONE=""

for arg in "$@"; do
  case "$arg" in
    --no-clone) SKIP_CLONE=1 ;;
    --force-seed) SEED_ARGS+=(--force) ;;
    --from-hermes) CORE_MODE=local ;;
    --from-git) CORE_MODE=git ;;
    --with-chat) VERIFY_ARGS+=(--with-chat) ;;
    *) echo "unknown flag: $arg" >&2; exit 2 ;;
  esac
done

# Bootstrap python for the KTAI-layer scripts (stdlib-only: rebrand/seed/setup).
BOOT_PY="${KTAI_BOOTSTRAP_PYTHON:-}"
if [[ -z "$BOOT_PY" ]]; then
  for cand in python3.12 python3.11 python3.13 python3; do
    if command -v "$cand" >/dev/null 2>&1 && \
       "$cand" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 8) else 1)' 2>/dev/null; then
      BOOT_PY="$(command -v "$cand")"; break
    fi
  done
fi
if [[ -z "$BOOT_PY" || ! -x "$BOOT_PY" ]]; then
  echo "no python3 (>=3.8) found; set KTAI_BOOTSTRAP_PYTHON to one" >&2
  exit 1
fi

export KTAI_HOME="${KTAI_HOME:-$HOME/.ktai}"
export HERMES_HOME="$KTAI_HOME"
unset PYTHONPATH PYTHONHOME || true

if [[ -z "${SKIP_CLONE:-}" ]]; then
  echo "── 1/5 core (mode=$CORE_MODE)"
  bash "$KTAI_ROOT/scripts/clone_core.sh" --mode "$CORE_MODE" --dst "$KTAI_ROOT/core"
else
  echo "── 1/5 core: skipped"
fi

echo "── 2/5 apply the KTAI identity layer"
"$BOOT_PY" "$KTAI_ROOT/scripts/rebrand_core.py"

echo "── 3/5 build KTAI's own venv"
"$BOOT_PY" "$KTAI_ROOT/scripts/setup_venv.py" --mode auto

echo "── 4/5 seed the KTAI home ($KTAI_HOME)"
if [[ ${#SEED_ARGS[@]} -gt 0 ]]; then
  "$BOOT_PY" "$KTAI_ROOT/scripts/seed_home.py" "${SEED_ARGS[@]}"
else
  "$BOOT_PY" "$KTAI_ROOT/scripts/seed_home.py"
fi

echo "── 5/5 verify"
bash "$KTAI_ROOT/scripts/verify.sh" "${VERIFY_ARGS[@]+"${VERIFY_ARGS[@]}"}"

echo
echo "KTAI is ready.  Chat:   ktai        Delegate: ktai team code \"<task>\""
