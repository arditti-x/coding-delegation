import unittest

import support
from model_routing.adapters import ClaudeAdapter, CodexAdapter, CursorAdapter

CLAUDE = support.FIXTURES / "claude"
CODEX = support.FIXTURES / "codex"


class ClaudeUsageTest(unittest.TestCase):
    def setUp(self):
        self.adapter = ClaudeAdapter()

    def test_partial_usage(self):
        usage = self.adapter.parse_usage((CLAUDE / "usage_partial.SYNTHETIC.result.json").read_text(encoding="utf-8"))
        by_name = {window.name: window.used_percent for window in usage.windows}
        self.assertEqual(by_name["Current session"], 12)
        self.assertEqual(by_name["Current week (all models)"], 41)
        self.assertFalse(usage.over_threshold())
        self.assertTrue(usage.known)

    def test_at_limit_usage(self):
        usage = self.adapter.parse_usage((CLAUDE / "usage_at_limit.result.json").read_text(encoding="utf-8"))
        by_name = {window.name: window.used_percent for window in usage.windows}
        self.assertEqual(by_name["Current session"], 0)
        self.assertEqual(by_name["Current week (all models)"], 100)
        self.assertTrue(usage.over_threshold())
        self.assertTrue(usage.blocked)

    def test_plain_text_result_is_accepted(self):
        usage = self.adapter.parse_usage("Current session: 95% used\n")
        self.assertEqual(usage.windows[0].used_percent, 95)
        self.assertTrue(usage.over_threshold())


class CodexUsageTest(unittest.TestCase):
    def setUp(self):
        self.adapter = CodexAdapter()

    def test_ok(self):
        usage = self.adapter.parse_usage((CODEX / "rate_limits_ok.SYNTHETIC.json").read_text(encoding="utf-8"))
        by_name = {window.name: window.used_percent for window in usage.windows}
        self.assertEqual(by_name["primary"], 23)
        self.assertEqual(by_name["secondary"], 48)
        self.assertTrue(usage.ordinary_usage_allowed)
        self.assertFalse(usage.blocked)
        self.assertFalse(usage.over_threshold())
        self.assertEqual(usage.note, "account/rateLimits/read")

    def test_at_limit(self):
        usage = self.adapter.parse_usage((CODEX / "rate_limits_at_limit.SYNTHETIC.json").read_text(encoding="utf-8"))
        by_name = {window.name: window.used_percent for window in usage.windows}
        self.assertEqual(by_name["primary"], 100)
        self.assertEqual(by_name["secondary"], 91)
        self.assertFalse(usage.ordinary_usage_allowed)
        self.assertEqual(usage.rate_limit_reached_type, "primary")
        self.assertTrue(usage.blocked)
        self.assertTrue(usage.over_threshold())

    def test_bare_result_without_jsonrpc_envelope(self):
        usage = self.adapter.parse_usage(
            '{"rateLimits": {"primary": {"usedPercent": 10}}, "ordinaryUsageAllowed": true}'
        )
        self.assertEqual(usage.windows[0].used_percent, 10)
        self.assertFalse(usage.blocked)

    def test_null_secondary_is_skipped(self):
        usage = self.adapter.parse_usage(
            '{"result": {"rateLimits": {"primary": {"usedPercent": 5}, "secondary": null}, "ordinaryUsageAllowed": true}}'
        )
        self.assertEqual([window.name for window in usage.windows], ["primary"])


class CursorUsageTest(unittest.TestCase):
    def test_usage_is_unknown_and_there_is_no_command(self):
        adapter = CursorAdapter()
        self.assertIsNone(adapter.usage())
        usage = adapter.parse_usage("")
        self.assertFalse(usage.known)
        self.assertFalse(usage.over_threshold())


if __name__ == "__main__":
    unittest.main()
