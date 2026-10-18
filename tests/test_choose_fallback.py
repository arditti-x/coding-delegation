import json
import unittest
from pathlib import Path

import support
from model_routing.adapters import CodexAdapter, ClaudeAdapter, unknown_usage
from model_routing.catalog import load_catalog
from model_routing.choose import cache_is_fresh, choose
from model_routing.fallback import plan_fallback
from model_routing.prejob import prejob
from model_routing.settings import load_yaml, merge_layers, normalize

MODELS = json.loads((support.FIXTURES / "codex" / "debug_models.json").read_text(encoding="utf-8"))
CLAUDE = ClaudeAdapter()
CODEX = CodexAdapter()


def settings_with(**routing):
    base = load_yaml(support.ROOT / "data" / "prefs-defaults.yaml")
    return normalize(merge_layers(base, {"routing": routing}))


def reports(claude_file="usage_partial.SYNTHETIC.result.json", codex_file="rate_limits_ok.SYNTHETIC.json"):
    return {
        "claude": {"usage": CLAUDE.parse_usage((support.FIXTURES / "claude" / claude_file).read_text(encoding="utf-8"))},
        "codex": {
            "usage": CODEX.parse_usage((support.FIXTURES / "codex" / codex_file).read_text(encoding="utf-8")),
            "models": MODELS,
        },
        "cursor": {"usage": unknown_usage()},
    }


class ChooseTest(unittest.TestCase):
    def test_frontier_stays_off_by_default(self):
        settings = settings_with(tools={"claude": {"enabled": True}, "codex": {"enabled": True}}, first_tool="claude")
        result = choose({"difficulty": "hard", "bytes_in_scope": 0, "roundtrip_tokens": 0}, settings, reports(), load_catalog())
        self.assertEqual(result["tier"], "strong")
        self.assertEqual(result["model"], "opus")
        self.assertNotEqual(result["tier"], "frontier")

    def test_flagged_frontier_requires_the_user_policy(self):
        settings = settings_with(frontier="never", tools={"claude": {"enabled": True}}, first_tool="claude")
        job = {"difficulty": "normal", "frontier": True, "bytes_in_scope": 0, "roundtrip_tokens": 0}
        self.assertEqual(choose(job, settings, reports(), load_catalog())["tier"], "standard")
        settings["routing"]["frontier"] = "flagged"
        result = choose(job, settings, reports(), load_catalog())
        self.assertEqual(result["tier"], "frontier")
        self.assertEqual(result["model"], "fable")

    def test_big_job_picks_most_usage_left_and_unknown_usage_is_last(self):
        settings = settings_with(
            first_tool="cursor",
            tools={
                "claude": {"enabled": True, "plan": "included"},
                "codex": {"enabled": True, "plan": "included"},
                "cursor": {"enabled": True, "plan": "included"},
            },
        )
        result = choose({"difficulty": "hard", "bytes_in_scope": 0, "roundtrip_tokens": 0}, settings, reports(), load_catalog())
        self.assertEqual(result["action"], "launch")
        # Claude week is 41% used, Codex max is 48%, Cursor usage is unknown.
        self.assertEqual(result["tool"], "claude")
        self.assertEqual(result["model"], "opus")

    def test_small_job_skips_extra_spend_and_prefers_the_users_cost_order(self):
        settings = settings_with(
            extra_spend="deny",
            cost_order=["codex", "claude"],
            tools={
                "claude": {"enabled": True, "plan": "included"},
                "codex": {"enabled": True, "plan": "extra"},
            },
        )
        result = choose({"difficulty": "small", "bytes_in_scope": 0, "roundtrip_tokens": 0}, settings, reports(), load_catalog())
        self.assertEqual(result["tool"], "claude")
        self.assertEqual(result["model"], "haiku")
        self.assertTrue(any(row["tool"] == "codex" and "bills extra" in row["reason"] for row in result["skipped"]))

    def test_context_skip_removes_codex_when_the_window_is_too_small(self):
        settings = settings_with(tools={"codex": {"enabled": True}}, first_tool="codex")
        result = choose(
            {"difficulty": "normal", "bytes_in_scope": 3_000_000, "roundtrip_tokens": 0},
            settings,
            reports(),
            load_catalog(),
        )
        self.assertEqual(result["action"], "stop")
        self.assertTrue(any("usable window" in row["reason"] for row in result["skipped"]))

    def test_at_limit_tool_is_skipped(self):
        settings = settings_with(
            tools={"claude": {"enabled": True}, "codex": {"enabled": True}},
            first_tool="claude",
        )
        result = choose(
            {"difficulty": "normal", "bytes_in_scope": 0, "roundtrip_tokens": 0},
            settings,
            reports(claude_file="usage_at_limit.result.json"),
            load_catalog(),
        )
        self.assertEqual(result["tool"], "codex")
        self.assertEqual(result["model"], "gpt-5.6-terra")
        self.assertTrue(any("lags newest generation" in warning for warning in result["warnings"]))

    def test_tie_without_a_user_order_asks(self):
        settings = settings_with(tools={"claude": {"enabled": True}, "cursor": {"enabled": True}})
        # Give both unknown usage so remaining cannot pick a winner.
        same = {
            "claude": {"usage": unknown_usage()},
            "cursor": {"usage": unknown_usage()},
            "codex": {"usage": unknown_usage(), "models": MODELS},
        }
        result = choose({"difficulty": "normal", "bytes_in_scope": 0, "roundtrip_tokens": 0}, settings, same, load_catalog())
        self.assertEqual(result["action"], "ask")
        self.assertIsNone(result["tool"])

    def test_nothing_enabled_does_not_launch(self):
        result = choose({"difficulty": "small", "bytes_in_scope": 0, "roundtrip_tokens": 0}, settings_with(), reports(), load_catalog())
        self.assertEqual(result["action"], "stop")
        self.assertIsNone(result["tool"])

    def test_cursor_default_model_when_it_is_the_only_enabled_tool(self):
        settings = settings_with(tools={"cursor": {"enabled": True}}, first_tool="cursor")
        result = choose({"difficulty": "fast" if False else "small", "bytes_in_scope": 0, "roundtrip_tokens": 0}, settings, reports(), load_catalog())
        self.assertEqual(result["tool"], "cursor")
        self.assertEqual(result["model"], "grok-4.7")
        self.assertEqual(result["launch"]["stdin"], "devnull")
        self.assertNotIn("--fallback-model", result["launch"]["argv"])

    def test_cache_rereads_before_big_jobs(self):
        self.assertTrue(cache_is_fresh(0, 100, big=False))
        self.assertFalse(cache_is_fresh(0, 100, big=True))
        self.assertFalse(cache_is_fresh(0, 301, big=False))

    def test_prejob_logs_tool_model_and_usage(self):
        import tempfile

        settings = settings_with(tools={"codex": {"enabled": True}}, first_tool="codex")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "routing-log.jsonl"
            result = prejob(
                {"difficulty": "small", "bytes_in_scope": 0, "roundtrip_tokens": 0},
                settings,
                reports(),
                catalog=load_catalog(),
                log_to=path,
            )
            line = json.loads(path.read_text(encoding="utf-8").strip())
        self.assertEqual(line["tool"], result["tool"])
        self.assertEqual(line["model"], "gpt-6-luna")
        self.assertIn("usage", line)
        self.assertNotIn("email", json.dumps(line).lower())


class FallbackTest(unittest.TestCase):
    def test_default_asks_before_handoff_and_keeps_the_tier(self):
        settings = settings_with()
        decision = plan_fallback(
            current_tool="claude",
            tier="strong",
            reason="limit",
            eligible_tools=["claude", "codex"],
            settings=settings,
        )
        self.assertEqual(decision["action"], "ask")
        self.assertEqual(decision["tool"], "codex")
        self.assertEqual(decision["tier"], "strong")

    def test_handoff_tells_the_user(self):
        settings = settings_with(on_limit_or_stall="hand off and tell me")
        decision = plan_fallback(
            current_tool="claude",
            tier="fast",
            reason="stall",
            eligible_tools=["claude", "cursor"],
            settings=settings,
        )
        self.assertEqual(decision["action"], "handoff")
        self.assertTrue(decision["tell_user"])
        self.assertEqual(decision["tier"], "fast")

    def test_none_left_stops(self):
        decision = plan_fallback(
            current_tool="codex",
            tier="standard",
            reason="error",
            eligible_tools=["codex"],
            settings=settings_with(on_limit_or_stall="handoff"),
        )
        self.assertEqual(decision["action"], "stop")
        self.assertTrue(decision["ask_user"])
        self.assertIsNone(decision["tool"])


if __name__ == "__main__":
    unittest.main()
