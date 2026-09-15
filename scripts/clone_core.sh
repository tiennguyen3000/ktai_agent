#!/usr/bin/env bash
# KTAI — Phase 3 clone step.
# Copies the Hermes source tree (the runtime core) into the KTAI distribution.
# Heavy/regenerable dirs are excluded; the KTAI patch layer is applied afterwards
# by scripts/rebrand_core.py. Re-runnable (idempotent) — safe to re-clone.
set -euo pipefail

SRC="${SRC:-$HOME/.hermes/hermes-agent}"
DST="${DST:-$HOME/KTAI/core}"

echo "== KTAI clone: $SRC -> $DST"
mkdir -p "$DST"

rsync -a \
  --exclude node_modules \
  --exclude .git \
  --exclude venv \
  --exclude __pycache__ \
  --exclude '*.pyc' \
  --exclude .pytest_cache \
  --exclude .ruff_cache \
  --exclude .mypy_cache \
  --exclude '*.egg-info' \
  --exclude .web_ui_build.lock \
  --exclude .ds_store \
  "$SRC"/ "$DST"/

echo "== copied. size:"
du -sh "$DST"
echo "== core import check:"
cd "$DST" && ls -d agent tools hermes_cli gateway cron plugins >/dev/null && echo "key packages present"
