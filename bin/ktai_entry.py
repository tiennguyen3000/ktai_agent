#!/usr/bin/env python3
"""KTAI process entry point (invoked by bin/ktai on KTAI's venv)."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT / "core"), str(ROOT)]  # core runtime first, then the KTAI package

from ktai.cli import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
