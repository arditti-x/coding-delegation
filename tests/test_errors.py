import unittest

import support
from model_routing.adapters import ClaudeAdapter, CodexAdapter

CLAUDE = support.FIXTURES / "claude"
CODEX = support.FIXTURES / "codex"


class ClaudeErrorTest(unittest.TestCase):
    def setUp(self):
        self.adapter = ClaudeAdapter()

    def test_limit_error(self):
        stdout = (CLAUDE / "limit_error.result.json").read_text(encoding="utf-8")
        self.assertEqual(self.adapter.classify_error(exit_code=1, stdout=stdout, stderr=""), "limit")

    def test_stream_limit_includes_the_model_that_ran(self):
        stdout = (CLAUDE / "stream_limit.jsonl").read_text(encoding="utf-8")
        self.assertEqual(self.adapter.classify_error(exit_code=1, stdout=stdout, stderr=""), "limit")
        self.assertEqual(self.adapter.parse_actual_model(stdout), "claude-opus-5-5")

    def test_bad_model(self):
        stdout = (CLAUDE / "bad_model.result.json").read_text(encoding="utf-8")
        stderr = (CLAUDE / "bad_model.stderr.txt").read_text(encoding="utf-8")
        self.assertEqual(self.adapter.classify_error(exit_code=1, stdout=stdout, stderr=stderr), "bad_model")
        self.assertIn("unrecognized_model", stderr)


class CodexErrorTest(unittest.TestCase):
    def setUp(self):
        self.adapter = CodexAdapter()

    def test_bad_model_is_turn_failed(self):
        stdout = (CODEX / "exec_bad_model.jsonl").read_text(encoding="utf-8")
        self.assertEqual(self.adapter.classify_error(exit_code=1, stdout=stdout, stderr=""), "bad_model")

    def test_limit_is_exit_1_and_turn_failed(self):
        # No captured Codex limit fixture was attached. The brief defines the
        # shape as exit 1 plus turn.failed, distinct from a bad-model message.
        stdout = '\n'.join(
            [
                '{"type":"turn.started"}',
                '{"type":"turn.failed","error":{"message":"usage limit reached"}}',
            ]
        )
        self.assertEqual(self.adapter.classify_error(exit_code=1, stdout=stdout, stderr=""), "limit")

    def test_successful_exec_is_not_an_error_and_has_no_model(self):
        stdout = (CODEX / "exec_ok.gpt-6.1-sol.jsonl").read_text(encoding="utf-8")
        self.assertEqual(self.adapter.classify_error(exit_code=0, stdout=stdout, stderr=""), "none")
        self.assertIsNone(self.adapter.parse_actual_model(stdout))

    def test_actual_model_comes_from_session_turn_context(self):
        stdout = (CODEX / "session_turn_context.SYNTHETIC.jsonl").read_text(encoding="utf-8")
        self.assertEqual(self.adapter.parse_actual_model(stdout), "gpt-6.1-sol")


if __name__ == "__main__":
    unittest.main()
