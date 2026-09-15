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

## Repo GitHub

`~/KTAI` là git repo, remote `origin` = `https://github.com/tiennguyen3000/ktai_agent` (**private**, nhánh `main`).
Chi tiết cần nhớ khi push:

- Repo giờ có **2 nhánh**: `main` = lớp KTAI (29 file: `identity/`, `ktai/`, `bin/`, `scripts/`,
  `patches/`, `docs/`), `core` = runtime Hermes core đã áp bản sắc (push từ `git -C core push
  <repo> main:core`, root commit riêng, 69MB pack). `.gitignore` loại trừ `core/` và `venv/` —
  `core/` có git repo riêng (remote `upstream` = NousResearch/hermes-agent).
- **Cài trên máy mới**: `git clone --single-branch --branch main <repo> ~/KTAI && bash ~/KTAI/scripts/install.sh`
  (6 bước, tự lấy nhánh `core`). Cờ hay dùng: `--from-hermes` (copy core+venv từ `~/.hermes`),
  `--mode git|local|auto` (nguồn core), `--venv-mode auto|clone|fresh` (nguồn venv),
  `--extras`/`--with-dev`, `--no-link`, `--skip-verify`. Chi tiết: `docs/INSTALL.md`.
- **Test lại đường cài mà không phá máy thật**: clone repo vào `/tmp/ktai-fresh`, chạy
  `KTAI_HOME=/tmp/ktai-home-test bash /tmp/ktai-fresh/scripts/install.sh --dir /tmp/ktai-fresh --mode git --venv-mode fresh --no-link`
  (nhớ `KTAI_HOME` + `--no-link` để không ghi vào `~/.ktai` và không đổi symlink `~/.local/bin/ktai`).
- Auth: token trong macOS keychain (user `tiennguyen3000`, quyền admin/push) — `git push`
  chạy trực tiếp, không cần `gh auth login`.

## Bản anh em (cùng thiết kế, khác chủ sở hữu)

KTAI là **template**: `scripts/new_distribution.py` sinh bản khác từ chính layer này
(sao chép CLI + identity + scripts + manifest, đổi token KTAI→tên mới, đổi tên path).

- Đã sinh: **Linh** — owner `Linh Nguyen`, lệnh `linh`, `~/Linh`, home `~/.linh`, env `LINH_HOME`,
  repo `tiennguyen3000/linh_agent` (nhánh `main` + `core`). Lệnh: `python3 scripts/new_distribution.py
  --name Linh --owner "Linh Nguyen" --slug linh --dir ~/Linh --home ~/.linh --repo <url>`.
- Bản mới lấy core từ **tree Hermes nguyên bản** (`~/.hermes/hermes-agent`), KHÔNG copy
  `core/` của KTAI: core KTAI đã áp bản sắc nên anchor `old` của manifest đã mất → rebrand fail.
- Sau khi sinh phải sửa tay 2 chỗ (không phải token): art wordmark ASCII (vẽ chữ, không phải text)
  và câu giải thích expansion trong README/docs nếu bản mới không có expansion.

## Commands

- `ktai` — interactive session; `ktai chat -q "<question>"` for one-shot.
- `ktai identity` — identity card + home + team roster.
- `ktai agents [role]` — list charters, or print one.
- `ktai team <role> "<task>"` — delegate a task to code|debug|review|test|research|devops.
- `ktai selfcheck` — end-to-end install verification.
- `bash scripts/sync_home.sh [--apply] [--overwrite] [--only skills|memories|plugins] [--show-extra]`
  — kéo skill/memory/plugin **mới** từ `~/.hermes` sang `~/.ktai` (seed chỉ copy 1 lần lúc cài;
  sau đó 2 home tách rời). Mặc định dry-run, không đè, không xoá, không đụng `skills/ktai`.
  Phân loại NEW/DIFF bằng 1 pass dry-run rồi mới copy — cần vì rsync của macOS là openrsync
  (không có `+` trong itemize code, và nếu copy trước khi phân loại thì file mới thành DIFF).
- Everything else (`gateway`, `cron`, `config`, `tools`, `doctor`, …) passes
  straight through to the core CLI; capability is not reduced.

## Pitfalls (đã trả giá)

- **`ktai_branding.py` không có trong tree Hermes gốc** → rebuild từ `~/.hermes` (hoặc clone
  nhánh `core` cũ) chết ở gate `branding import`. Bản canonical nằm ở `patches/ktai_branding.py`,
  `rebrand_core.py` tự tạo/refresh vào core. Thêm identity mới thì copy ngược lại vào `patches/`.
- **Seed kế thừa `config.yaml` từ `~/.hermes` → `display.skin: default`**, mất skin KTAI và
  `ktai selfcheck` fail. `seed_home.py` giờ luôn chạy `ktai config set display.skin ktai` sau khi
  seed (idempotent).

- **`KTAI_HOME` trong terminal của KTAI thắng `HERMES_HOME`.** Runtime KTAI export `KTAI_HOME`,
  và patch trong `hermes_constants.get_hermes_home()` cho `KTAI_HOME` ưu tiên cao hơn
  `HERMES_HOME`. Hệ quả: mọi lệnh chạy qua terminal tool thừa hưởng `KTAI_HOME=$HOME/.ktai`;
  `HERMES_HOME=/tmp/x python3 -c "...save_config()"` vẫn ghi vào home THẬT. Muốn cô lập để thử
  nghiệm thì set cả hai (`KTAI_HOME=/tmp/probe HERMES_HOME=/tmp/probe`), hoặc `unset KTAI_HOME`.
- **Không bao giờ chạy code ghi config của core trên home thật để "probe".** Đã từng ghi đè
  `~/.ktai/config.yaml` bằng `save_config(DEFAULT_CONFIG)` → mất `model`, telegram prompts,
  plugins, `display.skin` (skin check fail). Khôi phục: `cp ~/.hermes/config.yaml ~/.ktai/config.yaml`
  rồi `ktai config set display.skin ktai` (vì bản KTAI khác bản Hermes đúng ở key này).
- **Tool `patch` từ chối sửa file config** (`Refusing to write to Hermes config file`) — sửa
  config bằng `ktai config set <key> <value>`, không sửa tay.
- Bootstrap python của `rebuild.sh`/`install.sh` đã bỏ hard-code `~/.hermes/.../venv/bin/python3`:
  giờ tự dò `python3.12|3.11|3.13|python3` (>=3.8). Venv mới cần CPython 3.11–3.13
  (core `requires-python = ">=3.11,<3.14"`; macOS mặc định 3.9.6, Homebrew có 3.12/3.14).

## Rules that matter here

- `core/` is the live runtime: never hand-edit it. Add the edit to
  `scripts/rebrand_core.py`'s manifest (idempotent, fails loudly on a stale anchor),
  re-run it, then run `scripts/verify.sh`.
- After merging upstream core changes, re-run `scripts/rebrand_core.py` to re-apply
  the identity layer; `patches/rebrand.patch` shows exactly what is KTAI-specific.
- Internal module names (`hermes_cli`, `hermes_state`) and `HERMES_*` env vars stay
  as-is on purpose: they are the runtime API. Only the identity surface is renamed.
- Prefer adding capability in `~/KTAI/ktai` (CLI/skill/plugin) over touching core.
