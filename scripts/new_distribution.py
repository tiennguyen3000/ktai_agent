#!/usr/bin/env python3
"""New distribution — derive another branded agent from the KTAI layer.

KTAI is not hand-written per owner: it is a *layer* (CLI package, identity docs,
scripts, rebrand manifest) on top of a pristine Hermes core. This script copies
that layer, rewrites the identity tokens, and renames the paths — producing a
sibling distribution (own command, own home, own branding) from the same design.

What it does NOT do (deliberate — run those separately so each step is verifiable):

    scripts/clone_core.sh --mode local      # pristine core into <dir>/core
    scripts/rebrand_core.py                 # apply the new identity layer
    scripts/setup_venv.py --mode auto       # the new distribution's own venv
    scripts/seed_home.py                    # <home> for data
    scripts/verify.sh

Usage:

    python3 scripts/new_distribution.py \
        --name Linh --owner "Linh Nguyen" --slug linh \
        --dir ~/Linh --home ~/.linh \
        --repo https://github.com/tiennguyen3000/linh_agent.git

    --expansion ""      display expansion shown after the name (KTAI: "Khánh Tiển AI")
    --dry-run           list what would be written, touch nothing

Token order matters: longest / most specific first, generic last (see TOKEN_RULES).
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path

KTAI_ROOT = Path(__file__).resolve().parent.parent
SKIP_DIRS = {"core", "venv", ".git", "__pycache__", ".pytest_cache", ".mypy_cache"}
SKIP_FILES = {".DS_Store"}
TEXT_SUFFIXES = {".py", ".sh", ".md", ".yaml", ".yml", ".json", ".txt", ".cfg", ".toml", ".patch"}

# (label, old, new) — applied in order. `new` is filled from CLI args.
TOKEN_TEMPLATE = (
    # Doc filenames carry the uppercase name; rewrite the references before the generic pass.
    ("doc-ID", "{OLD}-IDENTITY", "{NEW_UPPER}-IDENTITY"),
    ("owner", "Nguyễn Khánh Tiển", "{OWNER}"),
    ("expansion", "Khánh Tiển AI", "{EXPANSION_OR_NAME}"),
    ("env-prefix", "KTAI_", "{NEW_UPPER}_"),
    ("branding-module", "ktai_branding", "{SLUG}_branding"),
    ("entry-module", "ktai_entry", "{SLUG}_entry"),
    ("repo-name", "ktai_agent", "{SLUG}_agent"),
    ("pth", "ktai_core.pth", "{SLUG}_core.pth"),
    ("name", "KTAI", "{NEW}"),
    ("slug", "ktai", "{SLUG}"),
)


def build_rules(name: str, owner: str, slug: str, expansion: str) -> list[tuple[str, str, str]]:
    mapping = {
        "OLD": "KTAI",
        "NEW": name,
        "NEW_UPPER": name.upper(),
        "OWNER": owner,
        "SLUG": slug,
        "EXPANSION_OR_NAME": expansion or name,
    }
    return [(label, old, new.format(**mapping)) for label, old, new in TOKEN_TEMPLATE]


def rewrite_text(text: str, rules: list[tuple[str, str, str]], counts: dict[str, int]) -> str:
    for label, old, new in rules:
        if old and old in text:
            counts[label] = counts.get(label, 0) + text.count(old)
            text = text.replace(old, new)
    return text


def target_path(rel: Path, rules: list[tuple[str, str, str]]) -> Path:
    """Rename the path itself with the same rules (ktai/ -> linh/, bin/ktai -> bin/linh)."""
    parts = []
    for part in rel.parts:
        for _, old, new in rules:
            part = part.replace(old, new)
        parts.append(part)
    return Path(*parts) if parts else rel


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", required=True, help="display name, e.g. Linh")
    ap.add_argument("--owner", required=True, help="owner full name, e.g. 'Linh Nguyen'")
    ap.add_argument("--slug", required=True, help="lowercase command/package name, e.g. linh")
    ap.add_argument("--expansion", default="", help="expansion shown after the name (KTAI: 'Khánh Tiển AI')")
    ap.add_argument("--dir", required=True, help="target distribution dir, e.g. ~/Linh")
    ap.add_argument("--home", required=True, help="target data home, e.g. ~/.linh")
    ap.add_argument("--repo", default="", help="target git remote (recorded in docs)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    dst_root = Path(args.dir).expanduser().resolve()
    home = Path(args.home).expanduser()
    rules = build_rules(args.name, args.owner, args.slug, args.expansion)

    if dst_root == KTAI_ROOT:
        print("target dir is the source distribution — pick another --dir")
        return 1
    if dst_root.exists() and any(dst_root.iterdir()):
        print(f"target dir exists and is not empty: {dst_root} (move it aside first)")
        return 1

    if not args.dry_run:
        dst_root.mkdir(parents=True, exist_ok=True)

    counts: dict[str, int] = {}
    written = renamed = skipped = 0

    for src in sorted(KTAI_ROOT.rglob("*")):
        rel = src.relative_to(KTAI_ROOT)
        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        if src.name in SKIP_FILES or src.name.endswith(".pyc"):
            continue

        dest_rel = target_path(rel, rules)
        dest = dst_root / dest_rel
        if dest_rel != rel:
            renamed += 1

        if src.is_dir():
            if not args.dry_run:
                dest.mkdir(parents=True, exist_ok=True)
            continue

        try:
            text = src.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            skipped += 1
            continue

        new_text = rewrite_text(text, rules, counts)
        if not args.dry_run:
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(new_text, encoding="utf-8")
            shutil.copymode(src, dest)
        written += 1

    print(f"{'[dry-run] ' if args.dry_run else ''}{args.name} distribution -> {dst_root}")
    print(f"  files written : {written}   paths renamed: {renamed}   binary/skipped: {skipped}")
    print(f"  home          : {home}")
    print(f"  command       : {args.slug}   env prefix: {args.name.upper()}_")
    if args.repo:
        print(f"  repo          : {args.repo}")
    print("  replacements  : " + ", ".join(f"{k}={v}" for k, v in sorted(counts.items())))

    print(f"""
next steps (each verifiable on its own):
  cd {dst_root}
  bash scripts/clone_core.sh --mode local          # pristine Hermes core -> core/
  python3 scripts/rebrand_core.py                  # apply the {args.name} identity layer
  python3 scripts/setup_venv.py --mode auto        # own venv (clone of ~/.hermes venv)
  python3 scripts/seed_home.py                     # create {home}
  ln -sfn {dst_root}/bin/{args.slug} ~/.local/bin/{args.slug}
  bash scripts/verify.sh""")
    return 0


if __name__ == "__main__":
    sys.exit(main())
