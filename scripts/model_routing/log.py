"""Append one routing record per run. Local file, never a git commit."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


def log_path(home: Path | None = None) -> Path:
    override = os.environ.get("CODING_DELEGATION_ROUTING_LOG")
    if override:
        return Path(override)
    root = home if home is not None else Path(os.environ.get("HOME", "~")).expanduser()
    return root / ".config" / "coding-delegation" / "routing-log.jsonl"


def append_log(record: dict[str, Any], path: Path | None = None) -> Path:
    target = path or log_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(_public_record(record), sort_keys=True)
    with target.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")
    return target


def _public_record(record: dict[str, Any]) -> dict[str, Any]:
    """Keep tool, model, and usage. Drop anything that looks like an account id."""
    usage = record.get("usage")
    return {
        "tool": record.get("tool"),
        "model": record.get("model"),
        "tier": record.get("tier"),
        "action": record.get("action"),
        "usage": usage,
        "warnings": list(record.get("warnings") or []),
        "skipped": list(record.get("skipped") or []),
    }
