"""Tier catalog. Families, not versions. No tool ranking."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from model_routing.yamlio import loads

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CATALOG = REPO_ROOT / "data" / "tiers.yaml"

DIFFICULTY_TIER = {"hard": "strong", "normal": "standard", "small": "fast"}


@dataclass
class Resolution:
    tool: str
    family: str | None
    model: str | None
    warnings: list[str] = field(default_factory=list)


def load_catalog(path: Path | None = None) -> dict[str, Any]:
    return loads((path or DEFAULT_CATALOG).read_text(encoding="utf-8"))


def tier_families(catalog: dict[str, Any], tier: str) -> list[str]:
    block = (catalog.get("tiers") or {}).get(tier) or {}
    families = block.get("families") or []
    return [str(item) for item in families]


def tier_for_difficulty(catalog: dict[str, Any], difficulty: str) -> str:
    table = catalog.get("difficulty_tier") or DIFFICULTY_TIER
    if difficulty not in table:
        raise ValueError(f"unknown difficulty {difficulty!r}")
    return str(table[difficulty])


def select_tier(catalog: dict[str, Any], difficulty: str, frontier_policy: str, job_flagged: bool) -> str:
    """Frontier only when the user's policy allows it.

    `never` ignores a per-job frontier flag. `flagged` uses frontier only when
    this job is flagged. `auto` always uses frontier. Passing a new policy in
    the per-job settings layer is a separate, explicit override.
    """
    policy = (frontier_policy or "never").strip().lower()
    if policy in {"auto", "automatically"}:
        return "frontier"
    if policy in {"flagged", "when i flag a job"} and job_flagged:
        return "frontier"
    return tier_for_difficulty(catalog, difficulty)


def resolve_claude(catalog: dict[str, Any], tier: str, pin: str | None = None) -> Resolution:
    if pin:
        return Resolution(tool="claude", family=None, model=pin)
    aliases = catalog.get("claude_aliases") or {}
    for family in tier_families(catalog, tier):
        alias = aliases.get(family)
        if alias:
            return Resolution(tool="claude", family=family, model=str(alias))
    return Resolution(tool="claude", family=None, model=None, warnings=[f"no Claude alias for tier {tier}"])


def resolve_cursor(catalog: dict[str, Any], pin: str | None = None) -> Resolution:
    model = pin or str((catalog.get("cursor") or {}).get("default_model") or "")
    if not model:
        return Resolution(tool="cursor", family=None, model=None, warnings=["cursor default model is unset"])
    return Resolution(tool="cursor", family=None, model=model)


def resolve_codex_family(
    catalog: dict[str, Any],
    models_payload: Any,
    family: str,
    pin: str | None = None,
) -> Resolution:
    """Pick the newest visible `gpt-<ver>-<family>` slug.

    Hidden models are ignored. Warn when the family's newest listed generation
    lags the newest generation present in the visible catalog.
    """
    if pin:
        return Resolution(tool="codex", family=family, model=pin)
    spec = catalog.get("codex") or {}
    pattern = re.compile(spec.get("slug_pattern") or r"^gpt-(\d+(?:\.\d+)*)-([a-z]+)$")
    visible = str(spec.get("visible_value") or "list")
    listed = _model_rows(models_payload)

    best: dict[str, tuple[tuple[int, ...], str]] = {}
    newest_gen = 0
    for row in listed:
        if str(row.get("visibility") or "") != visible:
            continue
        slug = str(row.get("slug") or row.get("id") or "")
        match = pattern.match(slug)
        if not match:
            continue
        version = tuple(int(part) for part in match.group(1).split("."))
        fam = match.group(2)
        newest_gen = max(newest_gen, version[0])
        current = best.get(fam)
        if current is None or version > current[0]:
            best[fam] = (version, slug)

    chosen = best.get(family)
    if chosen is None:
        return Resolution(
            tool="codex",
            family=family,
            model=None,
            warnings=[f"no visible Codex model for family {family}"],
        )
    version, slug = chosen
    warnings: list[str] = []
    if newest_gen and version[0] < newest_gen:
        warnings.append(
            f"{family} resolved to {slug} lags newest generation {newest_gen} "
            f"(this family's generation is {version[0]})"
        )
    return Resolution(tool="codex", family=family, model=slug, warnings=warnings)


def resolve_codex_tier(
    catalog: dict[str, Any],
    models_payload: Any,
    tier: str,
    pins: dict[str, str] | None = None,
) -> Resolution:
    pins = pins or {}
    families = (catalog.get("codex") or {}).get("families") or []
    wanted = [family for family in tier_families(catalog, tier) if family in families or family in pins]
    if not wanted:
        # A pin may name the tier directly.
        if tier in pins:
            return Resolution(tool="codex", family=tier, model=pins[tier])
        return Resolution(tool="codex", family=None, model=None, warnings=[f"no Codex family for tier {tier}"])
    family = wanted[0]
    return resolve_codex_family(catalog, models_payload, family, pin=pins.get(family))


def codex_usable_window(catalog: dict[str, Any], models_payload: Any, model: str) -> int | None:
    """Usable tokens = context_window * effective_context_window_percent / 100."""
    default_pct = (catalog.get("codex") or {}).get("effective_context_window_percent") or 95
    for row in _model_rows(models_payload):
        slug = str(row.get("slug") or row.get("id") or "")
        if slug != model:
            continue
        window = row.get("context_window")
        if window is None:
            return None
        pct = row.get("effective_context_window_percent", default_pct)
        try:
            return int(float(window) * float(pct) / 100.0)
        except (TypeError, ValueError):
            return None
    return None


def _model_rows(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, dict):
        rows = payload.get("models", payload.get("data", []))
    else:
        rows = payload
    if not isinstance(rows, list):
        return []
    return [row for row in rows if isinstance(row, dict)]
