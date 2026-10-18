"""Context-skip math.

need = bytes_in_scope/3 + 40_000 + 2 * roundtrip_tokens + output_reserve

output_reserve is 16_000 to 32_000 tokens (default 32_000).
Skip when need > 0.6 * usable window. An unknown window does not skip.
"""

from __future__ import annotations

OUTPUT_RESERVE_MIN = 16_000
OUTPUT_RESERVE_MAX = 32_000
DEFAULT_OUTPUT_RESERVE = OUTPUT_RESERVE_MAX
FIXED_OVERHEAD = 40_000
USABLE_FRACTION = 0.6


def context_need(
    bytes_in_scope: float,
    roundtrip_tokens: float,
    output_reserve: int = DEFAULT_OUTPUT_RESERVE,
) -> float:
    if output_reserve < OUTPUT_RESERVE_MIN or output_reserve > OUTPUT_RESERVE_MAX:
        raise ValueError(
            f"output reserve must be {OUTPUT_RESERVE_MIN}-{OUTPUT_RESERVE_MAX} tokens, got {output_reserve}"
        )
    if bytes_in_scope < 0 or roundtrip_tokens < 0:
        raise ValueError("bytes_in_scope and roundtrip_tokens must be >= 0")
    return (bytes_in_scope / 3.0) + FIXED_OVERHEAD + (2.0 * roundtrip_tokens) + output_reserve


def skips_for_context(need: float, usable_window: int | None) -> bool:
    if usable_window is None:
        return False
    if usable_window <= 0:
        return True
    return need > USABLE_FRACTION * usable_window
