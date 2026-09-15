"""KTAI — Personal AI Engineering Agent (Khánh Tiển AI).

Owner: Nguyễn Khánh Tiển. Built on the Hermes core architecture (Nous Research).
The `ktai` command dispatches KTAI-native subcommands and passes everything else
through to the core CLI, so the full capability surface (gateway, cron, tools,
delegation, desktop/TUI) is preserved.
"""

import os
from pathlib import Path

KTAI_NAME = "KTAI"
KTAI_EXPANSION = "Khánh Tiển AI"
KTAI_OWNER = "Nguyễn Khánh Tiển"
KTAI_VERSION = "1.0.0"

ROOT = Path(__file__).resolve().parent.parent
CORE = ROOT / "core"
IDENTITY = ROOT / "identity"
VENV_BIN = ROOT / "venv" / "bin"


def ktai_home() -> Path:
    """KTAI data home (~/.ktai unless KTAI_HOME says otherwise)."""
    return Path(os.environ.get("KTAI_HOME") or (Path.home() / ".ktai")).expanduser()


def core_entry() -> Path:
    """The core CLI entry the passthrough execs (KTAI's own venv copy)."""
    return VENV_BIN / "hermes"
