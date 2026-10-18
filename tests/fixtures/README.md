# Sanitized fixtures for model-routing tests
Derived from real CLI runs; ids, session/thread ids, paths, dates, timezones, plan/usage details and per-machine breakdowns were replaced with placeholders.
Files with SYNTHETIC in the name were not captured verbatim: their shape follows the field names documented in BRIEF.md (verify against the real CLI where possible) and values are invented.
- claude/limit_error.result.json: `claude -p ... --output-format json` at a usage limit (exit 1, api_error_status 429, api_error usage_limit_reached).
- claude/bad_model.*: unknown --model (exit 1, api_error_status 404, stderr unrecognized_model).
- claude/usage_at_limit.result.json / usage_partial.SYNTHETIC: `claude -p "/usage" --output-format json </dev/null`; parse the `result` text.
- claude/stream_limit.jsonl: stream-json; system/init `model` = model that ran.
- codex/exec_ok.<model>.jsonl, exec_bad_model.jsonl: `codex exec --json -m <model> ... </dev/null` (bad model: exit 1 + turn.failed).
- codex/debug_models.json: reduced `codex debug models` (keep visibility=="list", match ^gpt-(ver)-(family)$, highest version). Expected: astra->gpt-6-astra, sol->gpt-6.1-sol, terra->gpt-5.6-terra (lags newest generation 6 -> warn), luna->gpt-6-luna.
- codex/rate_limits_*.SYNTHETIC.json: app-server `account/rateLimits/read`. NEVER call account/rateLimitResetCredit/consume.
