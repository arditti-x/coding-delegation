"""Decide whether a SessionStart hook should ask the routing setup questions."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from model_routing.settings import load_merged, user_prefs_path
from model_routing.userconfig import apply_user_config, user_config_from_env

SETUP_MESSAGE = (
    "Coding-delegation model routing is not set up. "
    "Run the setup-coding-delegation skill and ask its model-routing questions. "
    "Do not invent licenses, a tool order, or a vendor rank. "
    "Frontier stays off unless the user allows it. "
    "On Codex, call request_user_input with at most 3 questions per call. "
    "Write the answers to the same prefs file the skill documents."
)


def needs_routing_setup(settings: dict[str, Any]) -> bool:
    routing = settings.get("routing") or {}
    return routing.get("setup_complete") is not True


def session_message(
    *,
    repo_root: Path | None,
    user_path: Path | None = None,
    home: Path | None = None,
    user_config: dict[str, Any] | None = None,
    environ: dict[str, str] | None = None,
) -> str | None:
    path = user_path or user_prefs_path(home)
    config = user_config if user_config is not None else user_config_from_env(environ)
    if config:
        apply_user_config(path, config)
    settings = load_merged(repo_root=repo_root, user_path=path, home=home)
    if needs_routing_setup(settings):
        return SETUP_MESSAGE
    return None
