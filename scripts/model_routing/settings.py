"""Prefs merge.

Order, highest precedence last in the overlay sense — a higher layer wins per key:

    per-job flag  >  repo file  >  user file  >  plugin defaults

Replaces "first file wins" (the first existing file used to hide the other).
Maps merge recursively. Lists and scalars are replaced when the higher layer
sets that key. A missing key falls through.

Migration: a repo `coding-delegation.prefs.yaml` used to hide
`~/.config/coding-delegation/prefs.yaml` entirely. Now a key you leave out of
the repo file keeps the user-file value. To keep the old "repo replaces
everything" result, put every key you care about in the repo file.
"""

from __future__ import annotations

import copy
import os
from pathlib import Path
from typing import Any

from model_routing.yamlio import dumps, loads

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULTS_PATH = REPO_ROOT / "data" / "prefs-defaults.yaml"
REPO_PREFS_NAME = "coding-delegation.prefs.yaml"

FRONTIER_VALUES = {
    "never": "never",
    "flagged": "flagged",
    "when i flag a job": "flagged",
    "auto": "auto",
    "automatically": "auto",
}
EXTRA_VALUES = {
    "deny": "deny",
    "none": "deny",
    "per job": "per_job",
    "per_job": "per_job",
    "per-job": "per_job",
    "capped": "capped",
}
REVIEWER_VALUES = {
    "none": "none",
    "same": "same",
    "other_vendor": "other_vendor",
    "other vendor": "other_vendor",
}
LIMIT_VALUES = {
    "ask_first": "ask_first",
    "ask first": "ask_first",
    "handoff": "handoff",
    "hand off and tell me": "handoff",
}
POLICY_VALUES = {"newest": "newest", "pin": "pin"}
STALL_CHOICES = (15, 30, 60)
TOOL_IDS = ("claude", "codex", "cursor")

# Surface keys from the existing prefs shape, mapped only so a user's order
# can name either the surface or the routing tool. Not a ranking.
SURFACE_TO_TOOL = {
    "claude_code_cloud": "claude",
    "claude": "claude",
    "codex_cloud": "codex",
    "codex": "codex",
    "cursor_cli": "cursor",
    "cursor_cloud_agents": "cursor",
    "cursor": "cursor",
}


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    value = loads(path.read_text(encoding="utf-8"))
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValueError(f"{path} must be a YAML map")
    return value


def user_prefs_path(home: Path | None = None) -> Path:
    override = os.environ.get("CODING_DELEGATION_USER_PREFS")
    if override:
        return Path(override)
    root = home if home is not None else Path(os.environ.get("HOME", "~")).expanduser()
    return root / ".config" / "coding-delegation" / "prefs.yaml"


def repo_prefs_path(repo_root: Path) -> Path:
    return repo_root / REPO_PREFS_NAME


def deep_merge(base: Any, overlay: Any) -> Any:
    if isinstance(base, dict) and isinstance(overlay, dict):
        merged = copy.deepcopy(base)
        for key, value in overlay.items():
            if key in merged:
                merged[key] = deep_merge(merged[key], value)
            else:
                merged[key] = copy.deepcopy(value)
        return merged
    return copy.deepcopy(overlay)


def merge_layers(*layers: dict[str, Any] | None) -> dict[str, Any]:
    merged: dict[str, Any] = {}
    for layer in layers:
        if layer:
            merged = deep_merge(merged, layer)
    return merged


def load_merged(
    *,
    repo_root: Path | None = None,
    user_path: Path | None = None,
    job: dict[str, Any] | None = None,
    defaults_path: Path | None = None,
    home: Path | None = None,
) -> dict[str, Any]:
    defaults = load_yaml(defaults_path or DEFAULTS_PATH)
    user = load_yaml(user_path or user_prefs_path(home))
    repo: dict[str, Any] = {}
    if repo_root is not None:
        repo = load_yaml(repo_prefs_path(repo_root))
    return normalize(merge_layers(defaults, user, repo, job))


def normalize(settings: dict[str, Any]) -> dict[str, Any]:
    data = copy.deepcopy(settings)
    routing = data.setdefault("routing", {})
    models = data.setdefault("models", {})
    routing["frontier"] = _map(routing.get("frontier"), FRONTIER_VALUES, "never")
    routing["extra_spend"] = _map(routing.get("extra_spend"), EXTRA_VALUES, "deny")
    routing["reviewer"] = _map(routing.get("reviewer"), REVIEWER_VALUES, "none")
    routing["on_limit_or_stall"] = _map(routing.get("on_limit_or_stall"), LIMIT_VALUES, "ask_first")
    models["policy"] = _map(models.get("policy"), POLICY_VALUES, "newest")
    routing["stall_timeout_min"] = _stall(routing.get("stall_timeout_min"))
    try:
        routing["extra_spend_cap"] = float(routing.get("extra_spend_cap") or 0)
    except (TypeError, ValueError):
        routing["extra_spend_cap"] = 0.0
    tools = routing.setdefault("tools", {})
    for tool_id in TOOL_IDS:
        tool = tools.get(tool_id)
        if not isinstance(tool, dict):
            tool = {}
        tool["enabled"] = bool(tool.get("enabled"))
        plan = str(tool.get("plan") or "included").strip().lower()
        tool["plan"] = "extra" if plan in {"extra", "bills_extra", "bills extra"} else "included"
        tools[tool_id] = tool
    first = routing.get("first_tool")
    if first in (None, "", "no preference", "no_preference", "none"):
        routing["first_tool"] = None
    elif str(first) in SURFACE_TO_TOOL:
        routing["first_tool"] = SURFACE_TO_TOOL[str(first)]
    else:
        routing["first_tool"] = None
    if not isinstance(routing.get("cost_order"), list):
        routing["cost_order"] = []
    routing["cost_order"] = [_tool_name(item) for item in routing["cost_order"] if _tool_name(item)]
    if not isinstance(models.get("pins"), dict):
        models["pins"] = {}
    routing["setup_complete"] = bool(routing.get("setup_complete"))
    return data


def preference_order(settings: dict[str, Any]) -> list[str]:
    """User-declared tool order. Empty when the user has not ranked tools."""
    routing = settings.get("routing") or {}
    order: list[str] = []
    first = routing.get("first_tool")
    if first in TOOL_IDS and first not in order:
        order.append(first)
    for item in (settings.get("preferences") or {}).get("order") or []:
        tool = _tool_name(item)
        if tool and tool not in order:
            order.append(tool)
    return order


def write_prefs(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dumps(data), encoding="utf-8")


def _map(value: Any, table: dict[str, str], default: str) -> str:
    if value is None:
        return default
    key = str(value).strip().lower()
    return table.get(key, default)


def _stall(value: Any) -> int:
    try:
        number = int(str(value).strip().split()[0])
    except (TypeError, ValueError, IndexError):
        return 30
    if number in STALL_CHOICES:
        return number
    return 30


def _tool_name(value: Any) -> str | None:
    if value is None:
        return None
    return SURFACE_TO_TOOL.get(str(value))
