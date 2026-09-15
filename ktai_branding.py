"""KTAI branding — single source of truth for KTAI identity inside the core.

KTAI = Khánh Tiển AI: the personal AI engineering agent of Nguyễn Khánh Tiển,
running on the Hermes core architecture (Nous Research).

This module is part of the KTAI rebrand layer. Core logic is untouched: only the
display/identity surfaces import from here, so re-branding KTAI never requires
editing core behaviour again. See KTAI/docs/REBRAND.md.
"""

KTAI_NAME = "KTAI"
KTAI_EXPANSION = "Khánh Tiển AI"
KTAI_OWNER = "Nguyễn Khánh Tiển"
KTAI_TAGLINE = "Personal AI Engineering Agent"
KTAI_VERSION = "1.0.0"
KTAI_CORE = "Hermes core (Nous Research)"

# ANSI-Shadow wordmark "KTAI" (Rich markup; colours are the KTAI palette).
KTAI_LOGO = """[bold #38BDF8]██╗  ██╗████████╗ █████╗ ██╗[/]
[bold #38BDF8]██║ ██╔╝╚══██╔══╝██╔══██╗██║[/]
[#22D3EE]█████╔╝    ██║   ███████║██║[/]
[#22D3EE]██╔═██╗    ██║   ██╔══██║██║[/]
[#2563EB]██║  ██╗   ██║   ██║  ██║██║[/]
[#2563EB]╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚═╝[/]"""

# No hero art: KTAI renders the wordmark only (keeps the banner tight).
KTAI_HERO = ""

# Display branding consumed by hermes_cli/skin_engine.py and the CLI.
# Keys match the core's branding contract.
KTAI_BRANDING = {
    "agent_name": KTAI_NAME,
    "welcome": f"{KTAI_NAME} ready — {KTAI_TAGLINE} of {KTAI_OWNER}. Type your message or /help for commands.",
    "goodbye": "KTAI signing off ⚡",
    "response_label": " ⚡ KTAI ",
    "prompt_symbol": "❯",
    "help_header": "(⚡) Available Commands",
    "tiny_line": "⚡ KTAI",
}

# Spinner wings / verbs — engineering flavour, distinct from the Hermes gold persona.
KTAI_SPINNER = {
    "waiting_faces": ["(⚡)", "(⌬)", "(▚)", "(⚙)", "(<>)"],
    "thinking_faces": ["(⚡)", "(⚙)", "(⌬)", "(▞)", "(<>)"],
    "thinking_verbs": [
        "inspecting the repo", "tracing the call path", "reading the diff",
        "running the tests", "checking the premise", "profiling the hot path",
        "reviewing the invariants", "wiring the tools"],
}

KTAI_TOOL_PREFIX = "⚡"


def version_label(core_version: str = "", release_date: str = "") -> str:
    """Version label for banners: KTAI's own version first, core version second."""
    seat = f"{KTAI_NAME} v{KTAI_VERSION}"
    if core_version:
        seat += f" · core {core_version}"
        if release_date:
            seat += f" ({release_date})"
    return seat


def identity_lines() -> list:
    """Human-readable identity card (used by ``ktai identity``)."""
    return [
        f"Name        : {KTAI_NAME} ({KTAI_EXPANSION})",
        f"Role        : {KTAI_TAGLINE}",
        f"Owner       : {KTAI_OWNER}",
        f"Core        : {KTAI_CORE}",
        f"KTAI version: {KTAI_VERSION}",
    ]
