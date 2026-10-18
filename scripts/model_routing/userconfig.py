"""Map Claude Code plugin userConfig into the same prefs file the setup skill writes."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from model_routing.settings import deep_merge, load_yaml, write_prefs

_BOOL_TRUE = {"1", "true", "yes", "on"}
_BOOL_FALSE = {"0", "false", "no", "off"}


def user_config_from_env(environ: dict[str, str] | None = None) -> dict[str, str]:
    source = environ if environ is not None else os.environ
    prefix = "CLAUDE_PLUGIN_OPTION_"
    found: dict[str, str] = {}
    for key, value in source.items():
        if key.startswith(prefix):
            found[key[len(prefix):]] = value
    return found


def user_config_to_prefs(config: dict[str, Any]) -> dict[str, Any]:
    def raw(name: str, default: Any = None) -> Any:
        if name in config:
            return config[name]
        return default

    def flag(name: str) -> bool:
        value = raw(name, False)
        if isinstance(value, bool):
            return value
        return str(value).strip().lower() in _BOOL_TRUE

    def text(name: str, default: str = "") -> str:
        value = raw(name, default)
        if value is None:
            return default
        return str(value).strip()

    tools = {}
    for tool_id, key in (("claude", "tool_claude"), ("codex", "tool_codex"), ("cursor", "tool_cursor")):
        plan = text(f"plan_{tool_id}", "included").lower() or "included"
        tools[tool_id] = {"enabled": flag(key), "plan": plan}

    pins: dict[str, str] = {}
    for part in text("pins").split():
        if "=" not in part:
            continue
        family, model = part.split("=", 1)
        if family and model:
            pins[family] = model

    first = text("first_tool", "no preference")
    return {
        "models": {"policy": text("versions", "newest") or "newest", "pins": pins},
        "routing": {
            "frontier": text("frontier", "never") or "never",
            "extra_spend": text("extra_spend", "deny") or "deny",
            "extra_spend_cap": _number(raw("extra_spend_cap", 0)),
            "reviewer": text("reviewer", "none") or "none",
            "on_limit_or_stall": text("on_limit_or_stall", "ask first") or "ask first",
            "stall_timeout_min": text("stall_timeout", "30") or "30",
            "first_tool": first,
            "setup_complete": True,
            "tools": tools,
        },
    }


def apply_user_config(user_path: Path, config: dict[str, Any]) -> bool:
    """Write routing prefs once. Do not overwrite a routing section the user already has."""
    if not config:
        return False
    existing = load_yaml(user_path)
    routing = existing.get("routing")
    if isinstance(routing, dict) and routing.get("setup_complete") is True:
        return False
    overlay = user_config_to_prefs(config)
    # Keep license answers already stored in the user file.
    merged = deep_merge(existing, overlay)
    write_prefs(user_path, merged)
    return True


def _number(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0
