#!/usr/bin/env python3
"""KTAI venv setup — gives KTAI its own isolated runtime.

Two ways to populate ~/KTAI/venv:

  --mode clone   (same machine as a Hermes install — fast, no downloads)
      Copies the Hermes venv (308 MB of already-installed dependencies: litellm,
      openai, fastapi, discord.py, ...) into <KTAI_ROOT>/venv and repoints every
      absolute path from the Hermes install to the KTAI core. That avoids
      re-downloading/re-resolving the whole dependency tree while keeping KTAI's
      runtime fully independent: after this step nothing in KTAI reads or writes
      ~/.hermes/hermes-agent.

  --mode fresh   (new machine — no Hermes install present)
      Creates a brand-new venv with a supported CPython (>=3.11,<3.14 — the core's
      requires-python), installs the core's dependencies (uv + uv.lock when uv is
      available, otherwise pip -e), then applies the same finalisation below.

  --mode auto    (default) clone when the Hermes venv exists, else fresh.

Both modes end in finalize(): the editable mapping that makes `import cli`,
`import hermes_cli`, `import tools` resolve to the KTAI core, plus the `ktai`
console script that boots KTAI with KTAI_HOME set.

Why repointing works (clone mode): the venv's editable install is a
`__editable__*.pth` + finder module whose MAPPING/NAMESPACES tables hold absolute
source paths. Rewriting that table (and the console-script shebangs) is enough to
move the install root.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

KTAI_ROOT = Path(__file__).resolve().parent.parent
CORE = KTAI_ROOT / "core"
DST_VENV = KTAI_ROOT / "venv"
SRC_ROOT = Path.home() / ".hermes" / "hermes-agent"
SRC_VENV = SRC_ROOT / "venv"
OLD_ROOT = str(SRC_ROOT.resolve())
NEW_ROOT = str(CORE.resolve())

# CPython candidates for a fresh venv, best first. The core's requires-python is
# ">=3.11,<3.14" — 3.14 is excluded because Rust-backed transitives (pydantic-core)
# have no cp314 wheel yet and would fall back to a source build.
PY_CANDIDATES = ("python3.13", "python3.12", "python3.11")
MIN_PY, MAX_PY = (3, 11), (3, 14)


def step(msg: str) -> None:
    print(f"== {msg}", flush=True)


def run(cmd: list[str], **kw) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, check=True, **kw)


def python_version(path: str) -> tuple[int, int] | None:
    try:
        out = subprocess.run(
            [path, "-c", "import sys;print('%d.%d' % sys.version_info[:2])"],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
        major, minor = out.split(".")
        return int(major), int(minor)
    except Exception:
        return None


def find_python() -> str | None:
    explicit = os.environ.get("KTAI_PYTHON", "").strip()
    for cand in ([explicit] if explicit else []) + list(PY_CANDIDATES):
        path = shutil.which(cand) or (cand if Path(cand).is_file() else None)
        if not path:
            continue
        ver = python_version(path)
        if ver and MIN_PY <= ver < MAX_PY:
            step(f"python for the fresh venv: {path} ({ver[0]}.{ver[1]})")
            return path
    return None


def clone_mode() -> None:
    if not SRC_VENV.is_dir():
        raise SystemExit(f"source venv not found: {SRC_VENV} — use --mode fresh")

    if DST_VENV.exists():
        step(f"removing previous venv at {DST_VENV}")
        shutil.rmtree(DST_VENV)

    step(f"cloning venv {SRC_VENV} -> {DST_VENV} (308 MB, preserves symlinks)")
    run(["cp", "-a", str(SRC_VENV), str(DST_VENV)])

    step("repointing absolute paths (editable finder, shebangs, activate scripts)")
    rewritten, scanned = 0, 0
    for path in DST_VENV.rglob("*"):
        if not path.is_file() or path.is_symlink():
            continue
        try:
            if path.stat().st_size > 3_000_000:
                continue
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue  # binary payloads (.so, .dylib) — never touch
        scanned += 1
        # `OLD_ROOT/venv` must be rewritten first: console-script shebangs
        # (`#!/…/hermes-agent/venv/bin/python3`) point at the venv, not the source
        # tree, so a plain OLD_ROOT→NEW_ROOT swap would leave them dangling.
        new_text = text.replace(f"{OLD_ROOT}/venv", str(DST_VENV))
        if OLD_ROOT in new_text:
            new_text = new_text.replace(OLD_ROOT, NEW_ROOT)
        if new_text != text:
            path.write_text(new_text, encoding="utf-8")
            rewritten += 1
    step(f"text files scanned: {scanned}, repointed: {rewritten}")


def fresh_mode(allow_uv: bool = True) -> None:
    py = find_python()
    if not py:
        raise SystemExit(
            "no CPython 3.11–3.13 found (core requires >=3.11,<3.14).\n"
            "  install one, e.g.:  brew install python@3.12\n"
            "  or point KTAI_PYTHON at an interpreter:  KTAI_PYTHON=/path/to/python3.12 "
            "python3 scripts/setup_venv.py --mode fresh"
        )

    if DST_VENV.exists():
        step(f"removing previous venv at {DST_VENV}")
        shutil.rmtree(DST_VENV)

    step(f"creating venv: {py} -m venv {DST_VENV}")
    run([py, "-m", "venv", str(DST_VENV)])
    vpy = DST_VENV / "bin" / "python3"

    uv = shutil.which("uv") if allow_uv else None
    installed = False
    if uv and (CORE / "uv.lock").is_file():
        step("installing core dependencies with uv (uv.lock, frozen)")
        try:
            run([uv, "sync", "--frozen", "--no-dev"], cwd=str(CORE),
                env={**os.environ, "UV_PROJECT_ENVIRONMENT": str(DST_VENV)})
            installed = True
        except subprocess.CalledProcessError:
            step("uv sync failed — falling back to pip")

    if not installed:
        step("installing core dependencies with pip (editable install of core/)")
        run([str(vpy), "-m", "pip", "install", "--upgrade", "pip", "wheel", "setuptools==83.0.0"])
        run([str(vpy), "-m", "pip", "install", "-e", str(CORE)])

    step("dependency install done")


def finalize() -> int:
    site = next(DST_VENV.glob("lib/python3*/site-packages"))
    for junk in list(site.glob("__editable__*")):
        junk.unlink()
    (site / "ktai_core.pth").write_text(f"{NEW_ROOT}\n{KTAI_ROOT}\n", encoding="utf-8")
    step(f"editable mapping written: {site / 'ktai_core.pth'}")

    # Console scripts: keep the passthrough faithful (argv[0] still reads 'ktai'
    # because the launcher execs with that name).
    binp = DST_VENV / "bin"
    ktai_script = binp / "ktai"
    ktai_script.write_text(
        f"""#!/bin/sh
# KTAI entry point (generated by scripts/setup_venv.py)
KTAI_HOME="${{KTAI_HOME:-$HOME/.ktai}}"
export KTAI_HOME
export HERMES_HOME="$KTAI_HOME"
unset PYTHONPATH PYTHONHOME
exec "{binp}/python3" "{KTAI_ROOT}/bin/ktai_entry.py" "$@"
""", encoding="utf-8")
    ktai_script.chmod(0o755)

    # Verification: imports must resolve inside the KTAI core, not the Hermes one.
    step("verifying import resolution")
    probe = subprocess.run(
        [str(binp / "python3"), "-c",
         "import cli, ktai_branding, hermes_constants, agent.prompt_builder as p, tools;"
         "print('cli      ->', cli.__file__);"
         "print('branding ->', ktai_branding.__file__);"
         "print('identity ->', 'You are KTAI' in p.DEFAULT_AGENT_IDENTITY)"],
        cwd=str(CORE), capture_output=True, text=True,
    )
    print(probe.stdout.strip() or probe.stderr.strip())
    if probe.returncode != 0:
        return 1
    if NEW_ROOT not in probe.stdout:
        print("FAIL: modules resolved outside the KTAI core")
        return 1
    step("venv ready")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=("auto", "clone", "fresh"), default="auto")
    ap.add_argument("--no-uv", action="store_true", help="fresh mode: never use uv, always pip")
    args = ap.parse_args()

    if not (CORE / "hermes_cli").is_dir():
        print(f"core not found at {CORE} — run scripts/clone_core.sh first")
        return 1

    mode = args.mode
    if mode == "auto":
        mode = "clone" if SRC_VENV.is_dir() else "fresh"
        step(f"mode auto-detected: {mode}")

    if mode == "clone":
        clone_mode()
    else:
        fresh_mode(allow_uv=not args.no_uv)

    return finalize()


if __name__ == "__main__":
    sys.exit(main())
