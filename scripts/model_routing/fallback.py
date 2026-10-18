"""Mid-job fallback.

On a limit error, another error, or a stall past the user's timeout, move to
the next eligible tool at the same tier. When none remain, stop and ask.
`ask_first` (the default) does not launch the next tool. `handoff` does, and
still tells the user.
"""

from __future__ import annotations

from typing import Any


def plan_fallback(
    *,
    current_tool: str,
    tier: str,
    reason: str,
    eligible_tools: list[str],
    settings: dict[str, Any],
) -> dict[str, Any]:
    if reason not in {"limit", "error", "stall"}:
        raise ValueError(f"unsupported fallback reason {reason!r}")
    mode = (settings.get("routing") or {}).get("on_limit_or_stall") or "ask_first"
    rest = [tool for tool in eligible_tools if tool != current_tool]
    if not rest:
        return {
            "action": "stop",
            "tier": tier,
            "reason": reason,
            "tool": None,
            "ask_user": True,
            "tell_user": True,
            "message": "No eligible tool left at this tier. Stop and ask the user.",
        }
    nxt = rest[0]
    if mode == "handoff":
        return {
            "action": "handoff",
            "tier": tier,
            "reason": reason,
            "tool": nxt,
            "ask_user": False,
            "tell_user": True,
            "message": f"Hand off to {nxt} at tier {tier} and tell the user.",
        }
    return {
        "action": "ask",
        "tier": tier,
        "reason": reason,
        "tool": nxt,
        "ask_user": True,
        "tell_user": True,
        "message": f"Ask before handing off to {nxt} at tier {tier}.",
    }
