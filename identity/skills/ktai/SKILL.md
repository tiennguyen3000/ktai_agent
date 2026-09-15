---
name: ktai
description: "Use when operating, extending, or troubleshooting KTAI — the user's own agent. Commands, home layout, engineering agents, rebrand layer."
version: 1.0.0
author: Nguyễn Khánh Tiển
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [ktai, identity, agents, rebrand, cli, team, engineering]
---

# KTAI — Personal AI Engineering Agent

KTAI (Khánh Tiển AI) is the personal AI engineering agent of Nguyễn Khánh Tiển.
It runs on the Hermes core architecture (Nous Research) but is an independent
distribution: own command, own home, own identity, own team of engineering agents.

## Layout

```
~/KTAI/                 # the distribution
├── core/               # forked core source (runtime) — patched via scripts/rebrand_core.py
├── ktai/               # the `ktai` CLI package (dispatch + passthrough)
├── identity/           # SOUL.md, AGENTS.md, agents/*.md, skins/, skills/
├── bin/ktai            # launcher
├── scripts/            # clone → rebrand → venv → seed → verify (re-runnable)
├── patches/            # diff + manifest of every core edit
├── venv/               # KTAI's own runtime (independent of ~/.hermes)
└── docs/               # ARCHITECTURE, KTAI-IDENTITY, REBRAND, AGENT-ROLES

~/.ktai/                # data home (KTAI_HOME)
├── config.yaml .env    # settings / secrets (inherited from the Hermes home at seed time)
├── SOUL.md AGENTS.md   # persona + repo rules
├── agents/*.md         # the 6 engineering-agent charters
├── skins/ktai.yaml     # KTAI branding (active skin)
├── skills/ memory/     # capability + memory
└── state.db logs/ sessions/
```

## Commands

- `ktai` — interactive session; `ktai chat -q "<question>"` for one-shot.
- `ktai identity` — identity card + home + team roster.
- `ktai agents [role]` — list charters, or print one.
- `ktai team <role> "<task>"` — delegate a task to code|debug|review|test|research|devops.
- `ktai selfcheck` — end-to-end install verification.
- Everything else (`gateway`, `cron`, `config`, `tools`, `doctor`, …) passes
  straight through to the core CLI; capability is not reduced.

## Rules that matter here

- `core/` is the live runtime: never hand-edit it. Add the edit to
  `scripts/rebrand_core.py`'s manifest (idempotent, fails loudly on a stale anchor),
  re-run it, then run `scripts/verify.sh`.
- After merging upstream core changes, re-run `scripts/rebrand_core.py` to re-apply
  the identity layer; `patches/rebrand.patch` shows exactly what is KTAI-specific.
- Internal module names (`hermes_cli`, `hermes_state`) and `HERMES_*` env vars stay
  as-is on purpose: they are the runtime API. Only the identity surface is renamed.
- Prefer adding capability in `~/KTAI/ktai` (CLI/skill/plugin) over touching core.
