#!/usr/bin/env python3
"""KTAI home seeder — builds ~/.ktai so KTAI starts capable, not empty.

Copies the capability surface (config, credentials, skills, memories, plugins)
from the Hermes home, then installs the KTAI identity layer on top:
SOUL.md / AGENTS.md / agents/ / skins/ / skills/ktai.

Deliberately NOT copied: state.db, session transcripts, kanban board, history and
caches — KTAI starts with its own clean session history. The source home is only
ever read.

Re-runnable: identity files are overwritten (they are generated from the repo),
config/credentials/skills are only copied when absent unless --force.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IDENTITY = ROOT / "identity"
SRC_HOME = Path.home() / ".hermes"
DST_HOME = Path.home() / ".ktai"

# Files the user chose to inherit: without these KTAI cannot run at all.
INHERIT_FILES = ("config.yaml", ".env", "auth.json", "google_token.json", "google_client_secret.json")
INHERIT_DIRS = ("skills", "memories", "plugins")
# Fresh empty dirs so first-run logging/session writes never race a missing parent.
FRESH_DIRS = ("logs", "sessions", "cron", "cache", "pastes", "plans", "sandboxes", "workspace")

# Identity artefacts: (destination relative to home, source)
IDENTITY_FILES = (
    ("SOUL.md", IDENTITY / "SOUL.md"),
    ("AGENTS.md", IDENTITY / "AGENTS.md"),
)


def step(msg: str) -> None:
    print(f"== {msg}")


def copy_file(src: Path, dst: Path, force: bool) -> str:
    if not src.is_file():
        return f"skip (source missing): {src}"
    if dst.exists() and not force:
        return f"keep existing: {dst}"
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return f"copied: {dst}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true", help="overwrite inherited config/skills in the home")
    args = ap.parse_args()

    if not SRC_HOME.is_dir():
        print(f"source home not found: {SRC_HOME}")
        return 1

    step(f"seeding KTAI home: {DST_HOME}")
    DST_HOME.mkdir(parents=True, exist_ok=True)
    DST_HOME.chmod(0o700)

    for name in FRESH_DIRS:
        (DST_HOME / name).mkdir(parents=True, exist_ok=True)
    step(f"fresh dirs: {', '.join(FRESH_DIRS)}")

    for name in INHERIT_FILES:
        print("   ", copy_file(SRC_HOME / name, DST_HOME / name, args.force))

    for name in INHERIT_DIRS:
        src, dst = SRC_HOME / name, DST_HOME / name
        if not src.is_dir():
            print(f"    skip (source missing): {src}")
            continue
        if dst.exists() and not args.force:
            print(f"    keep existing: {dst}")
            continue
        shutil.copytree(src, dst, dirs_exist_ok=True)
        print(f"    copied tree: {dst}")

    step("installing KTAI identity layer")
    for rel, src in IDENTITY_FILES:
        print("   ", copy_file(src, DST_HOME / rel, True))  # identity is generated: always refresh
    for rel_dir, src_dir in (("agents", IDENTITY / "agents"), ("skins", IDENTITY / "skins")):
        shutil.copytree(src_dir, DST_HOME / rel_dir, dirs_exist_ok=True)
        print(f"    installed: {DST_HOME / rel_dir}  ({len(list(src_dir.glob('*')))} files)")

    skill_src = IDENTITY / "skills" / "ktai"
    if skill_src.is_dir():
        shutil.copytree(skill_src, DST_HOME / "skills" / "ktai", dirs_exist_ok=True)
        print(f"    installed: {DST_HOME / 'skills/ktai'}")

    # A KTAI home must never be a Hermes home.
    assert DST_HOME.resolve() != SRC_HOME.resolve(), "refusing to seed onto the Hermes home"
    step("done")
    return 0


if __name__ == "__main__":
    sys.exit(main())
