"""Tool adapters for Claude Code, Codex CLI, and Cursor.

Each adapter describes how to launch, set the model, list models, confirm the
model that actually ran, read remaining usage, and recognize limit and
bad-model errors. Parsers accept fixture text. They do not run CLIs.

Codex processes are always started with stdin from /dev/null. `codex exec`
hangs otherwise (it prints "Reading additional input from stdin...").
The usage read is `account/rateLimits/read` on `codex app-server`. This module
never builds `account/rateLimitResetCredit/consume`.

Cursor has no public per-user usage API. Usage stays unknown. This module
does not call Cursor's dashboard.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any, Iterable

# Named so a review can see the credit-consuming method is refused, not called.
DENIED_CODEX_METHODS = frozenset({"account/rateLimitResetCredit/consume"})
CODEX_USAGE_METHOD = "account/rateLimits/read"

USAGE_SKIP_PERCENT = 90.0

_PCT_LINE = re.compile(
    r"^(?P<name>.+?):\s*(?P<pct>\d+(?:\.\d+)?)\s*%\s*used"
    r"(?:\s*[·•|\-]+\s*resets\s+(?P<resets>.+))?$",
    re.IGNORECASE,
)
_BAD_MODEL = re.compile(
    r"unrecognized_model|not supported|not found|may not exist|unknown model|invalid model",
    re.IGNORECASE,
)
_LIMIT = re.compile(
    r"usage_limit_reached|usage limit|rate limit|rate_limit|hit your .*limit",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class Command:
    argv: tuple[str, ...]
    stdin: str = "devnull"
    rpc_method: str | None = None

    def __post_init__(self) -> None:
        if self.rpc_method in DENIED_CODEX_METHODS:
            raise ValueError(f"refusing Codex method {self.rpc_method}")
        joined = " ".join(self.argv)
        if "rateLimitResetCredit" in joined or "cursor.com" in joined or "api2.cursor.sh" in joined:
            raise ValueError("refusing forbidden endpoint in command")


@dataclass
class UsageWindow:
    name: str
    used_percent: float | None = None
    resets_at: Any = None
    window_minutes: int | None = None


@dataclass
class Usage:
    known: bool
    windows: list[UsageWindow] = field(default_factory=list)
    blocked: bool = False
    spend_capped: bool = False
    ordinary_usage_allowed: bool | None = None
    rate_limit_reached_type: str | None = None
    note: str = ""

    def over_threshold(self, threshold: float = USAGE_SKIP_PERCENT) -> bool:
        if self.blocked or self.spend_capped:
            return True
        return any(
            window.used_percent is not None and window.used_percent >= threshold
            for window in self.windows
        )

    def max_used_percent(self) -> float | None:
        values = [window.used_percent for window in self.windows if window.used_percent is not None]
        if not values:
            return None
        return max(values)

    def remaining_percent(self) -> float | None:
        used = self.max_used_percent()
        if used is None:
            return None
        return 100.0 - used

    def as_dict(self) -> dict[str, Any]:
        return {
            "known": self.known,
            "blocked": self.blocked,
            "spend_capped": self.spend_capped,
            "ordinary_usage_allowed": self.ordinary_usage_allowed,
            "rate_limit_reached_type": self.rate_limit_reached_type,
            "max_used_percent": self.max_used_percent(),
            "windows": [
                {
                    "name": window.name,
                    "used_percent": window.used_percent,
                    "resets_at": window.resets_at,
                }
                for window in self.windows
            ],
            "note": self.note,
        }


def unknown_usage(note: str = "usage unknown") -> Usage:
    return Usage(known=False, note=note)


class ClaudeAdapter:
    tool_id = "claude"

    def launch(self, model: str, prompt: str) -> Command:
        # --fallback-model does not trip on usage limits, so it is not used.
        return Command(
            argv=("claude", "-p", prompt, "--model", model, "--output-format", "stream-json"),
            stdin="devnull",
        )

    def list_models(self) -> Command | None:
        return None

    def usage(self) -> Command:
        # Unofficial in -p. Free, plain text inside JSON, works at a limit.
        return Command(
            argv=("claude", "-p", "/usage", "--output-format", "json"),
            stdin="devnull",
        )

    def parse_models(self, stdout: str) -> list[dict[str, Any]]:
        return []

    def parse_usage(self, stdout: str) -> Usage:
        text = stdout or ""
        result_text = text
        blocked = False
        for value in iter_json_values(text):
            if not isinstance(value, dict):
                continue
            if isinstance(value.get("result"), str):
                result_text = value["result"]
            if value.get("api_error") == "usage_limit_reached" or value.get("api_error_status") == 429:
                blocked = True
            info = value.get("rate_limit_info")
            if isinstance(info, dict) and str(info.get("status") or "").lower() == "rejected":
                blocked = True
        windows = _percent_windows(result_text)
        if not windows and blocked:
            windows = [UsageWindow(name="limit", used_percent=100.0)]
        known = bool(windows) or blocked
        return Usage(
            known=known,
            windows=windows,
            blocked=blocked or any((w.used_percent or 0) >= 100 for w in windows),
            note="parsed /usage result" if known else "no usage percentages in output",
        )

    def parse_actual_model(self, stdout: str) -> str | None:
        for value in iter_json_values(stdout):
            if not isinstance(value, dict):
                continue
            if value.get("type") == "system" and value.get("subtype") == "init":
                model = value.get("model")
                if isinstance(model, str) and model:
                    return model
        return None

    def classify_error(self, *, exit_code: int, stdout: str, stderr: str) -> str:
        blob = f"{stdout}\n{stderr}"
        statuses = []
        api_errors = []
        for value in iter_json_values(stdout):
            _collect_error_fields(value, statuses, api_errors)
        if _BAD_MODEL.search(blob) or 404 in statuses:
            return "bad_model"
        if exit_code == 1 and (429 in statuses or "usage_limit_reached" in api_errors or _LIMIT.search(blob)):
            return "limit"
        if any(code == 429 for code in statuses) or "usage_limit_reached" in api_errors:
            return "limit"
        if exit_code not in (0, None):
            return "error"
        return "none"

    def usable_window(self, *_args: Any, **_kwargs: Any) -> int | None:
        # Claude's usage and init events in the fixtures do not report a window.
        return None


class CodexAdapter:
    tool_id = "codex"

    def launch(self, model: str, prompt: str) -> Command:
        return Command(
            argv=("codex", "exec", "--json", "-m", model, "--", prompt),
            stdin="devnull",
        )

    def list_models(self) -> Command:
        return Command(argv=("codex", "debug", "models"), stdin="devnull")

    def usage(self, socket_path: str = "") -> Command:
        """Read-only rate limits.

        `codex app-server` is started with stdin from /dev/null. The JSON-RPC
        request goes to the unix socket (`--listen unix://PATH`), and the only
        method is `account/rateLimits/read`.
        """
        listen = f"unix://{socket_path}" if socket_path else "unix://"
        return Command(
            argv=("codex", "app-server", "--listen", listen),
            stdin="devnull",
            rpc_method=CODEX_USAGE_METHOD,
        )

    def parse_models(self, stdout: str) -> Any:
        values = list(iter_json_values(stdout))
        if not values:
            return {"models": []}
        return values[0]

    def parse_usage(self, stdout: str) -> Usage:
        values = [value for value in iter_json_values(stdout) if isinstance(value, dict)]
        if not values:
            return unknown_usage("codex rate-limit output was not JSON")
        payload = _unwrap_rate_limits(values[-1])
        limits = payload.get("rateLimits") or payload.get("rate_limits") or {}
        windows: list[UsageWindow] = []
        if isinstance(limits, dict):
            windows.extend(_codex_windows(limits))
            by_id = limits.get("rateLimitsByLimitId") or payload.get("rateLimitsByLimitId")
            if isinstance(by_id, dict):
                for name, block in by_id.items():
                    if isinstance(block, dict):
                        windows.extend(_codex_windows(block, prefix=str(name)))
        if isinstance(payload.get("rateLimitsByLimitId"), dict) and not any(
            window.name.startswith("id:") for window in windows
        ):
            for name, block in payload["rateLimitsByLimitId"].items():
                if isinstance(block, dict):
                    windows.extend(_codex_windows(block, prefix=str(name)))
        ordinary = _optional_bool(payload.get("ordinaryUsageAllowed", payload.get("ordinary_usage_allowed")))
        reached = payload.get("rateLimitReachedType", payload.get("rate_limit_reached_type"))
        if reached in ("", "null"):
            reached = None
        reached_text = str(reached) if reached else None
        spend_capped = bool(reached_text and "spend" in reached_text.lower())
        blocked = ordinary is False or reached_text is not None or spend_capped
        return Usage(
            known=True,
            windows=windows,
            blocked=blocked,
            spend_capped=spend_capped,
            ordinary_usage_allowed=ordinary,
            rate_limit_reached_type=reached_text,
            note="account/rateLimits/read",
        )

    def parse_actual_model(self, stdout: str) -> str | None:
        """Session-log `turn_context.model`. Exec jsonl does not carry the model."""
        for value in iter_json_values(stdout):
            if not isinstance(value, dict):
                continue
            kind = str(value.get("type") or value.get("event") or "")
            if kind.replace(".", "_") not in {"turn_context", "session_turn_context"}:
                continue
            payload = value.get("payload") if isinstance(value.get("payload"), dict) else value
            model = payload.get("model")
            if isinstance(model, str) and model:
                return model
        return None

    def classify_error(self, *, exit_code: int, stdout: str, stderr: str) -> str:
        blob = f"{stdout}\n{stderr}"
        failed = False
        for value in iter_json_values(stdout):
            if isinstance(value, dict) and value.get("type") in {"turn.failed", "turn_failed"}:
                failed = True
        bad = bool(_BAD_MODEL.search(blob))
        if bad and (exit_code == 1 or failed):
            return "bad_model"
        # Brief: a Codex limit error is exit 1 plus turn.failed.
        if exit_code == 1 and failed:
            return "limit"
        if failed and _LIMIT.search(blob):
            return "limit"
        if exit_code not in (0, None):
            return "error"
        return "none"

    def usable_window(self, catalog: dict[str, Any], models_payload: Any, model: str) -> int | None:
        from model_routing.catalog import codex_usable_window

        return codex_usable_window(catalog, models_payload, model)


class CursorAdapter:
    tool_id = "cursor"

    def launch(self, model: str, prompt: str) -> Command:
        # `agent --trust` is the documented non-interactive start. `--model` selects the catalog default.
        return Command(argv=("agent", "--model", model, "--trust", prompt), stdin="devnull")

    def list_models(self) -> Command | None:
        return None

    def usage(self) -> None:
        # No public per-user usage API. Do not call the dashboard.
        return None

    def parse_models(self, stdout: str) -> list[dict[str, Any]]:
        return []

    def parse_usage(self, stdout: str = "") -> Usage:
        return unknown_usage("Cursor has no public per-user usage API")

    def parse_actual_model(self, stdout: str) -> str | None:
        for value in iter_json_values(stdout):
            if isinstance(value, dict) and isinstance(value.get("model"), str):
                return value["model"]
        return None

    def classify_error(self, *, exit_code: int, stdout: str, stderr: str) -> str:
        blob = f"{stdout}\n{stderr}"
        if _BAD_MODEL.search(blob):
            return "bad_model"
        if exit_code not in (0, None) and _LIMIT.search(blob):
            return "limit"
        if exit_code not in (0, None):
            return "error"
        return "none"

    def usable_window(self, *_args: Any, **_kwargs: Any) -> int | None:
        return None


ADAPTERS = {
    "claude": ClaudeAdapter(),
    "codex": CodexAdapter(),
    "cursor": CursorAdapter(),
}


def iter_json_values(text: str) -> Iterable[Any]:
    raw = (text or "").strip()
    if not raw:
        return
    try:
        yield json.loads(raw)
        return
    except json.JSONDecodeError:
        pass
    decoder = json.JSONDecoder()
    for line in raw.splitlines():
        chunk = line.strip()
        if not chunk:
            continue
        try:
            yield json.loads(chunk)
            continue
        except json.JSONDecodeError:
            pass
        pos = 0
        while pos < len(chunk):
            while pos < len(chunk) and chunk[pos].isspace():
                pos += 1
            if pos >= len(chunk):
                break
            try:
                value, end = decoder.raw_decode(chunk, pos)
            except json.JSONDecodeError:
                break
            yield value
            pos = end


def _percent_windows(text: str) -> list[UsageWindow]:
    windows: list[UsageWindow] = []
    for line in (text or "").splitlines():
        match = _PCT_LINE.match(line.strip())
        if not match:
            continue
        resets = match.group("resets")
        windows.append(
            UsageWindow(
                name=match.group("name").strip(),
                used_percent=float(match.group("pct")),
                resets_at=resets.strip() if resets else None,
            )
        )
    return windows


def _unwrap_rate_limits(value: dict[str, Any]) -> dict[str, Any]:
    current = value
    # Tolerate a JSON-RPC envelope, a bare result, or result nested twice.
    for _ in range(3):
        if "rateLimits" in current or "rate_limits" in current or "ordinaryUsageAllowed" in current:
            return current
        inner = current.get("result")
        if isinstance(inner, dict):
            current = inner
            continue
        break
    return current


def _codex_windows(block: dict[str, Any], prefix: str = "") -> list[UsageWindow]:
    windows: list[UsageWindow] = []
    for name in ("primary", "secondary"):
        window = block.get(name)
        if not isinstance(window, dict):
            continue
        percent = window.get("usedPercent", window.get("used_percent"))
        if percent is None:
            continue
        try:
            percent_value = float(percent)
        except (TypeError, ValueError):
            continue
        label = f"{prefix}.{name}" if prefix else name
        minutes = window.get("windowDurationMins", window.get("window_duration_mins"))
        windows.append(
            UsageWindow(
                name=label,
                used_percent=percent_value,
                resets_at=window.get("resetsAt", window.get("resets_at")),
                window_minutes=int(minutes) if isinstance(minutes, (int, float)) else None,
            )
        )
    return windows


def _optional_bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if value is None:
        return None
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"true", "yes"}:
            return True
        if lowered in {"false", "no"}:
            return False
    return None


def _collect_error_fields(value: Any, statuses: list[int], api_errors: list[str]) -> None:
    if isinstance(value, dict):
        status = value.get("api_error_status")
        if isinstance(status, int):
            statuses.append(status)
        err = value.get("api_error")
        if isinstance(err, str):
            api_errors.append(err)
        for child in value.values():
            if isinstance(child, (dict, list)):
                _collect_error_fields(child, statuses, api_errors)
    elif isinstance(value, list):
        for child in value:
            _collect_error_fields(child, statuses, api_errors)
