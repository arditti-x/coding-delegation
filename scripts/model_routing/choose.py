"""Pre-job tool and model choice.

Hard jobs are big: the eligible tool with the most usage left.
Small jobs use the cheapest eligible tool.
Normal jobs follow the user's order.
Unknown-usage tools sort last.
Ties with no user ranking ask the user instead of picking a vendor.
"""

from __future__ import annotations

from typing import Any

from model_routing.adapters import ADAPTERS, USAGE_SKIP_PERCENT, Usage
from model_routing.catalog import (
    load_catalog,
    resolve_claude,
    resolve_codex_tier,
    resolve_cursor,
    select_tier,
)
from model_routing.context import context_need, skips_for_context
from model_routing.settings import TOOL_IDS, preference_order

USAGE_CACHE_SECONDS = 300


def cache_is_fresh(cached_at: float, now: float, *, big: bool, ttl: int = USAGE_CACHE_SECONDS) -> bool:
    """Usage cache lasts about five minutes. Big jobs always re-read."""
    if big:
        return False
    return (now - cached_at) < ttl


def choose(
    job: dict[str, Any],
    settings: dict[str, Any],
    reports: dict[str, dict[str, Any]] | None = None,
    catalog: dict[str, Any] | None = None,
) -> dict[str, Any]:
    catalog = catalog or load_catalog()
    reports = reports or {}
    routing = settings.get("routing") or {}
    difficulty = str(job.get("difficulty") or "normal")
    tier = select_tier(
        catalog,
        difficulty,
        str(routing.get("frontier") or "never"),
        bool(job.get("frontier")),
    )
    need = context_need(
        float(job.get("bytes_in_scope") or job.get("bytes") or 0),
        float(job.get("roundtrip_tokens") or job.get("roundtrip") or 0),
        int(job.get("output_reserve") or 32_000),
    )
    pins = _pins(settings, job)
    policy = (settings.get("models") or {}).get("policy") or "newest"
    eligible: list[dict[str, Any]] = []
    skipped: list[dict[str, str]] = []

    for tool_id in TOOL_IDS:
        report = reports.get(tool_id) or {}
        usage = report.get("usage")
        if not isinstance(usage, Usage):
            usage = ADAPTERS[tool_id].parse_usage(report.get("usage_text") or "")
        job_model = job.get("model") if job.get("tool") == tool_id else None
        decision = _evaluate_tool(
            tool_id,
            tier=tier,
            settings=settings,
            job=job,
            usage=usage,
            models_payload=report.get("models"),
            catalog=catalog,
            need=need,
            pins=pins if policy == "pin" else {},
            job_model=job_model,
        )
        if decision.get("skip"):
            skipped.append({"tool": tool_id, "reason": decision["skip"]})
        else:
            eligible.append(decision)

    forced = job.get("tool")
    if forced:
        eligible = [row for row in eligible if row["tool"] == forced]
        if not eligible:
            skipped.append({"tool": str(forced), "reason": "per-job tool is not eligible"})

    action, chosen, ask = _pick(eligible, settings, difficulty)
    reviewer = None
    if chosen and action == "launch":
        reviewer = _reviewer(chosen, eligible, settings, tier)

    result = {
        "action": action,
        "tool": chosen["tool"] if chosen else None,
        "model": chosen["model"] if chosen else None,
        "tier": tier,
        "family": chosen.get("family") if chosen else None,
        "warnings": list(chosen.get("warnings") or []) if chosen else [],
        "usage": chosen["usage"].as_dict() if chosen else None,
        "context_need": need,
        "skipped": skipped,
        "candidates": [row["tool"] for row in eligible],
        "ask": ask,
        "stall_timeout_min": int(routing.get("stall_timeout_min") or 30),
        "launch": None,
        "reviewer": reviewer,
        "big": difficulty == "hard",
    }
    if chosen and action == "launch":
        prompt = str(job.get("prompt") or "")
        command = ADAPTERS[chosen["tool"]].launch(chosen["model"], prompt)
        result["launch"] = {"argv": list(command.argv), "stdin": command.stdin}
    return result


def _evaluate_tool(
    tool_id: str,
    *,
    tier: str,
    settings: dict[str, Any],
    job: dict[str, Any],
    usage: Usage,
    models_payload: Any,
    catalog: dict[str, Any],
    need: float,
    pins: dict[str, str],
    job_model: Any = None,
) -> dict[str, Any]:
    routing = settings.get("routing") or {}
    tool_cfg = (routing.get("tools") or {}).get(tool_id) or {}
    if not tool_cfg.get("enabled"):
        return {"skip": "tool is not enabled in prefs"}
    if usage.over_threshold(USAGE_SKIP_PERCENT):
        return {"skip": f"usage >= {int(USAGE_SKIP_PERCENT)}% or blocked"}
    bills_extra = tool_cfg.get("plan") == "extra"
    if bills_extra and not _extra_allowed(routing, job):
        return {"skip": "plan bills extra and extra spend is not allowed"}
    resolution = _resolve(tool_id, tier, catalog, models_payload, pins, job_model)
    if not resolution.model:
        return {"skip": "; ".join(resolution.warnings) or "no model resolved"}
    window = None
    if tool_id == "codex":
        window = ADAPTERS["codex"].usable_window(catalog, models_payload, resolution.model)
    if skips_for_context(need, window):
        return {"skip": "context need exceeds 0.6 of the usable window"}
    return {
        "tool": tool_id,
        "model": resolution.model,
        "family": resolution.family,
        "warnings": list(resolution.warnings),
        "usage": usage,
        "bills_extra": bills_extra,
        "window": window,
    }


def _resolve(tool_id: str, tier: str, catalog: dict[str, Any], models_payload: Any, pins: dict[str, str], job_model: Any):
    pin = str(job_model) if job_model and isinstance(job_model, str) else None
    if tool_id == "claude":
        family_pin = pin or _family_pin(catalog, tier, pins, "claude")
        return resolve_claude(catalog, tier, family_pin)
    if tool_id == "cursor":
        return resolve_cursor(catalog, pin or pins.get("cursor"))
    family_pin = None if pin is None else pin
    # A job-level model pin replaces family resolution for this run.
    if family_pin:
        from model_routing.catalog import Resolution

        return Resolution(tool="codex", family=None, model=family_pin)
    return resolve_codex_tier(catalog, models_payload, tier, pins)


def _family_pin(catalog: dict[str, Any], tier: str, pins: dict[str, str], tool_id: str) -> str | None:
    if tool_id != "claude":
        return None
    from model_routing.catalog import tier_families

    for family in tier_families(catalog, tier):
        if family in pins:
            return pins[family]
    return None


def _pins(settings: dict[str, Any], job: dict[str, Any]) -> dict[str, str]:
    pins = dict((settings.get("models") or {}).get("pins") or {})
    job_pins = job.get("pins")
    if isinstance(job_pins, dict):
        pins.update({str(key): str(value) for key, value in job_pins.items()})
    return {str(key): str(value) for key, value in pins.items()}


def _extra_allowed(routing: dict[str, Any], job: dict[str, Any]) -> bool:
    policy = routing.get("extra_spend") or "deny"
    if policy == "deny":
        return False
    if policy == "per_job":
        return bool(job.get("allow_extra_spend"))
    if policy == "capped":
        if float(routing.get("extra_spend_cap") or 0) <= 0:
            return False
        return bool(job.get("allow_extra_spend"))
    return False


def _pick(eligible: list[dict[str, Any]], settings: dict[str, Any], difficulty: str):
    if not eligible:
        return "stop", None, ["no eligible tool; ask the user"]
    order = preference_order(settings)
    cost_order = list((settings.get("routing") or {}).get("cost_order") or [])

    def key(row: dict[str, Any]) -> tuple:
        usage: Usage = row["usage"]
        unknown = 0 if usage.known else 1
        remaining = usage.remaining_percent() if usage.known else 0.0
        user_rank = order.index(row["tool"]) if row["tool"] in order else None
        ranked = 0 if user_rank is not None else 1
        user_index = user_rank if user_rank is not None else 0
        if difficulty == "hard":
            # Most usage left. Unknown usage last. User order breaks ties.
            return (unknown, -(remaining or 0.0), ranked, user_index)
        if difficulty == "small":
            # Cheapest: included before extra, then the user's cost order.
            # Tools the user did not put in cost_order tie with each other.
            if row["tool"] in cost_order:
                cost_rank, cost_known = cost_order.index(row["tool"]), 0
            else:
                cost_rank, cost_known = 0, 1 if cost_order else 0
            extra = 1 if row["bills_extra"] else 0
            return (extra, unknown, cost_known, cost_rank, ranked, user_index)
        # Normal: user order, then most usage left. Unknown usage last.
        return (unknown, ranked, user_index, -(remaining or 0.0))

    decorated = [(key(row), row) for row in eligible]
    best_key = min(item[0] for item in decorated)
    top = [row for item_key, row in decorated if item_key == best_key]
    if len(top) == 1:
        return "launch", top[0], []
    names = [row["tool"] for row in top]
    return "ask", None, [f"tie among {', '.join(names)}; ask which tool to use"]


def _reviewer(chosen: dict[str, Any], eligible: list[dict[str, Any]], settings: dict[str, Any], tier: str):
    mode = (settings.get("routing") or {}).get("reviewer") or "none"
    if mode == "none":
        return None
    if mode == "same":
        return {"tool": chosen["tool"], "model": chosen["model"], "tier": tier}
    for row in eligible:
        if row["tool"] != chosen["tool"]:
            return {"tool": row["tool"], "model": row["model"], "tier": tier}
    return None
