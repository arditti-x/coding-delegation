#!/usr/bin/env python3
"""SessionStart hook for Cursor, Codex, and Claude Code.

Prints additional context when model-routing prefs are missing. Does not run
a CLI and does not use the network. Exit 0 either way.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from model_routing.session_check import session_message  # noqa: E402


def main() -> int:
    raw = sys.stdin.read() if not sys.stdin.isatty() else ""
    payload = {}
    if raw.strip():
        try:
            loaded = json.loads(raw)
            if isinstance(loaded, dict):
                payload = loaded
        except json.JSONDecodeError:
            payload = {}
    repo = _repo_root(payload)
    user_config = payload.get("userConfig") if isinstance(payload.get("userConfig"), dict) else None
    message = session_message(repo_root=repo, user_config=user_config)
    if not message:
        json.dump({}, sys.stdout)
        sys.stdout.write("\n")
        return 0
    json.dump(
        {
            "additional_context": message,
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": message,
            },
        },
        sys.stdout,
    )
    sys.stdout.write("\n")
    return 0


def _repo_root(payload: dict) -> Path | None:
    for key in ("workspace_roots", "cwd", "workspaceRoot"):
        value = payload.get(key)
        if isinstance(value, str) and value:
            return Path(value)
        if isinstance(value, list) and value and isinstance(value[0], str):
            return Path(value[0])
    cwd = Path.cwd()
    for parent in [cwd, *cwd.parents]:
        if (parent / ".git").exists():
            return parent
    return cwd


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception:
        # A setup hint must not block the session.
        json.dump({}, sys.stdout)
        sys.stdout.write("\n")
        raise SystemExit(0)
