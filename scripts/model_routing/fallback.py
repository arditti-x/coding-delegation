"""Mid-job fallback.

On a limit error, another error, or a stall past the user's timeout, move to
the next eligible tool at the same tier. When none remain, stop and ask.
`ask_first` (the default) does not launch the next tool. `handoff` does, and
still tells the user.

Fallback never bypasses the existing extra-spend policy. A caller may pass
`allow_extra_spend=True` only when that job already received per-job consent.
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
    allow_extra_spend: bool = False,
) -> dict[str, Any]:
    if reason not in {"limit", "error", "stall"}:
        raise ValueError(f"unsupported fallback reason {reason!r}")
    routing = settings.get("routing") or {}
    mode = routing.get("on_limit_or_stall") or "ask_first"
    rest = [
        tool
        for tool in eligible_tools
        if tool != current_tool and _fallback_spend_allowed(tool, routing, allow_extra_spend)
    ]
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


def _fallback_spend_allowed(tool: str, routing: dict[str, Any], allow_extra_spend: bool) -> bool:
    cfg = (routing.get("tools") or {}).get(tool) or {}
    default_plan = "extra" if tool == "claude_api" else "included"
    plan = str(cfg.get("plan") or default_plan).strip().lower()
    if plan not in {"extra", "bills_extra", "bills extra"}:
        return True

    policy = routing.get("extra_spend") or "deny"
    if policy == "deny":
        return False
    if policy == "per_job":
        return allow_extra_spend
    if policy == "capped":
        try:
            cap = float(routing.get("extra_spend_cap") or 0)
        except (TypeError, ValueError):
            cap = 0.0
        return cap > 0 and allow_extra_spend
    return False
