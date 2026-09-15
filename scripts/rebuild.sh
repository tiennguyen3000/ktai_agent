#!/usr/bin/env bash
# KTAI rebuild — reproduce the whole distribution from the upstream core, in order.
#
# Steps 1–4 are idempotent and destructive only inside ~/KTAI (never ~/.hermes).
# Step 5 (seed) is additive: it keeps an existing ~/.ktai/config.yaml, .env and skills
# unless you pass --force-seed.
#
#   bash scripts/rebuild.sh                 # full rebuild
#   bash scripts/rebuild.sh --no-clone      # keep core/ (re-apply brand + venv + seed)
set -euo pipefail

KTAI_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PY_BOOT="${KTAI_BOOTSTRAP_PYTHON:-$HOME/.hermes/hermes-agent/venv/bin/python3}"
SEED_ARGS=()

for arg in "$@"; do
  case "$arg" in
    --no-clone) SKIP_CLONE=1 ;;
    --force-seed) SEED_ARGS+=(--force) ;;
    *) echo "unknown flag: $arg" >&2; exit 2 ;;
  esac
done

if [[ ! -x "$PY_BOOT" ]]; then
  echo "bootstrap python not found: $PY_BOOT" >&2
  echo "set KTAI_BOOTSTRAP_PYTHON to any python3 with pyyaml, or create the bootstrap venv first" >&2
  exit 1
fi

if [[ -z "${SKIP_CLONE:-}" ]]; then
  echo "── 1/5 clone core (KTAI/core <- upstream core)"
  bash "$KTAI_ROOT/scripts/clone_core.sh"
else
  echo "── 1/5 clone core: skipped"
fi

echo "── 2/5 apply the KTAI identity layer"
"$PY_BOOT" "$KTAI_ROOT/scripts/rebrand_core.py"

echo "── 3/5 build KTAI's own venv (repointed off ~/.hermes)"
"$PY_BOOT" "$KTAI_ROOT/scripts/setup_venv.py"

echo "── 4/5 seed the KTAI home (~/.ktai)"
if [[ ${#SEED_ARGS[@]} -gt 0 ]]; then
  "$PY_BOOT" "$KTAI_ROOT/scripts/seed_home.py" "${SEED_ARGS[@]}"
else
  "$PY_BOOT" "$KTAI_ROOT/scripts/seed_home.py"
fi

echo "── 5/5 verify"
bash "$KTAI_ROOT/scripts/verify.sh" "$@"

echo
echo "KTAI is ready.  Chat:   ktai        Delegate: ktai team code \"<task>\""
