"""Run the pre-job checks: usage, context, choose, log."""

from __future__ import annotations

from typing import Any

from model_routing.choose import choose
from model_routing.log import append_log


def prejob(
    job: dict[str, Any],
    settings: dict[str, Any],
    reports: dict[str, dict[str, Any]] | None = None,
    *,
    catalog: dict[str, Any] | None = None,
    log_to: Any = None,
) -> dict[str, Any]:
    result = choose(job, settings, reports, catalog)
    append_log(result, log_to)
    return result
