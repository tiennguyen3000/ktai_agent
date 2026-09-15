"""KTAI brain — identity, role catalogue, and team-prompt composition.

Two sources of truth, in priority order:
  1. the live home (~/.ktai/...) — what the running agent actually reads;
  2. the shipped identity layer (~/KTAI/identity/...) — used before seeding, and
     as the fallback/mirror that keeps the home recoverable.
"""

from __future__ import annotations

import sys
from pathlib import Path

from . import IDENTITY, KTAI_EXPANSION, KTAI_NAME, KTAI_OWNER, CORE, ROOT, ktai_home

ROLES = ("code", "debug", "review", "test", "research", "devops")


def _parse_frontmatter(text: str) -> tuple[dict, str]:
    """Split YAML frontmatter from body. Falls back to an empty meta on any issue."""
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    raw, body = text[3:end], text[end + 4:].lstrip("\n")
    try:
        import yaml
        meta = yaml.safe_load(raw) or {}
    except Exception as exc:  # noqa: BLE001
        # Never fail silently: an unparsed charter would render as an agent with an
        # empty mission, which looks like it works and is worse than a loud error.
        print(f"warning: bad frontmatter in role file ({exc}); treating header as plain text",
              file=sys.stderr)
        meta = {}
    return (meta if isinstance(meta, dict) else {}), body


def agents_dir() -> Path:
    """Directory holding the engineering-agent definitions (home first)."""
    home_agents = ktai_home() / "agents"
    return home_agents if home_agents.is_dir() else IDENTITY / "agents"


def list_roles() -> list[dict]:
    """Catalogue of the KTAI engineering agents, sorted by canonical order."""
    found: dict[str, dict] = {}
    for path in sorted(agents_dir().glob("*.md")):
        meta, body = _parse_frontmatter(path.read_text(encoding="utf-8"))
        name = str(meta.get("name") or path.stem)
        found[name] = {
            "name": name,
            "title": str(meta.get("title") or f"KTAI {name.title()} Agent"),
            "mission": str(meta.get("mission") or ""),
            "output": str(meta.get("output") or ""),
            "path": path,
            "body": body,
        }
    ordered = [found.pop(r) for r in ROLES if r in found]
    return ordered + [found[k] for k in sorted(found)]


def load_role(name: str) -> dict | None:
    """One role by name (case-insensitive)."""
    name = (name or "").strip().lower()
    for role in list_roles():
        if role["name"].lower() == name:
            return role
    return None


def build_team_prompt(role: dict, task: str) -> str:
    """Compose the delegated brief: role charter + the assigned task."""
    return (
        f"{role['body'].strip()}\n\n"
        f"---\n\n## NHIỆM VỤ ĐƯỢC GIAO\n\n{task.strip()}\n\n"
        f"Bám đúng hợp đồng đầu ra ở trên. Trả lời bằng tiếng Việt, ngắn gọn, "
        f"chỉ nêu việc đã làm và bằng chứng thật đã thu được."
    )


def identity_card() -> str:
    """Human-readable identity block for `ktai identity`."""
    from ktai_branding import KTAI_CORE, version_label  # lives in core/

    home = ktai_home()
    soul = home / "SOUL.md"
    lines = [
        "╭─ KTAI ─────────────────────────────────────────────",
        f"│ Name        : {KTAI_NAME} ({KTAI_EXPANSION})",
        f"│ Role        : Personal AI Engineering Agent",
        f"│ Owner       : {KTAI_OWNER}",
        f"│ Core        : {KTAI_CORE}",
        f"│ Version     : {version_label(_core_version(), _core_release())}",
        "├─ Runtime ──────────────────────────────────────────",
        f"│ Home        : {home}",
        f"│ SOUL        : {soul}{'' if soul.is_file() else '  (missing — run scripts/seed_home.py)'}",
        f"│ Source      : {CORE}",
        f"│ Distribution: {ROOT}",
        "├─ Team ─────────────────────────────────────────────",
    ]
    for role in list_roles():
        lines.append(f"│ {role['name']:9s}: {role['mission'][:70]}")
    lines.append("╰────────────────────────────────────────────────────")
    return "\n".join(lines)


def _core_version() -> str:
    try:
        import hermes_cli
        return str(getattr(hermes_cli, "__version__", ""))
    except Exception:
        return ""


def _core_release() -> str:
    try:
        import hermes_cli
        return str(getattr(hermes_cli, "__release_date__", ""))
    except Exception:
        return ""
