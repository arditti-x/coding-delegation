import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

import support
from model_routing.adapters import ClaudeAdapter, unknown_usage
from model_routing.catalog import load_catalog
from model_routing.choose import choose
from model_routing.fallback import plan_fallback
from model_routing.settings import load_yaml, merge_layers, normalize

CLAUDE = ClaudeAdapter()


def settings_with(**routing):
    base = load_yaml(support.ROOT / "data" / "prefs-defaults.yaml")
    return normalize(merge_layers(base, {"routing": routing}))


def reports():
    usage = CLAUDE.parse_usage(
        (support.FIXTURES / "claude" / "usage_partial.SYNTHETIC.result.json").read_text(encoding="utf-8")
    )
    return {
        "claude": {"usage": usage},
        "claude_api": {"usage": unknown_usage("API credit balance is not queried")},
        "cursor": {"usage": unknown_usage()},
    }


def write_fake_claude(directory: Path) -> None:
    path = directory / "claude"
    path.write_text(
        "#!/bin/sh\n"
        "if [ \"${1:-}\" = auth ] && [ \"${2:-}\" = status ]; then\n"
        "  printf '%s\\n' '{\"loggedIn\":true}'\n"
        "  exit 0\n"
        "fi\n"
        "exit 0\n",
        encoding="utf-8",
    )
    path.chmod(0o755)


class ClaudePoolTest(unittest.TestCase):
    def test_subscription_pool_strips_api_key(self):
        settings = settings_with(
            first_tool="claude_subscription",
            tools={"claude": {"enabled": True, "plan": "included"}},
        )
        result = choose(
            {"difficulty": "normal", "bytes_in_scope": 0, "roundtrip_tokens": 0},
            settings,
            reports(),
            load_catalog(),
        )
        self.assertEqual(result["tool"], "claude")
        self.assertEqual(result["billing_pool"], "claude_subscription")
        self.assertEqual(result["launch"]["auth"], "claude_subscription")
        self.assertEqual(result["launch"]["unset_env"], ["ANTHROPIC_API_KEY"])
        self.assertNotIn("require_env", result["launch"])

    def test_api_pool_requires_key_but_never_contains_it(self):
        settings = settings_with(
            first_tool="claude_api",
            extra_spend="per_job",
            tools={
                "claude": {"enabled": False},
                "claude_api": {"enabled": True, "plan": "extra"},
            },
        )
        result = choose(
            {
                "difficulty": "normal",
                "bytes_in_scope": 0,
                "roundtrip_tokens": 0,
                "allow_extra_spend": True,
            },
            settings,
            reports(),
            load_catalog(),
        )
        self.assertEqual(result["tool"], "claude_api")
        self.assertEqual(result["billing_pool"], "claude_api")
        self.assertEqual(result["launch"]["auth"], "anthropic_api_key")
        self.assertEqual(result["launch"]["require_env"], ["ANTHROPIC_API_KEY"])
        self.assertNotIn("unset_env", result["launch"])
        self.assertNotIn("sk-ant", str(result))

    def test_api_pool_is_extra_spend_gated_by_default(self):
        settings = settings_with(
            first_tool="claude_api",
            tools={
                "claude": {"enabled": False},
                "claude_api": {"enabled": True},
            },
        )
        result = choose(
            {"difficulty": "normal", "bytes_in_scope": 0, "roundtrip_tokens": 0},
            settings,
            reports(),
            load_catalog(),
        )
        self.assertEqual(result["action"], "stop")
        self.assertTrue(
            any(row["tool"] == "claude_api" and "extra spend" in row["reason"] for row in result["skipped"])
        )

    def test_subscription_alias_normalizes_to_existing_claude_id(self):
        settings = settings_with(first_tool="claude_subscription")
        self.assertEqual(settings["routing"]["first_tool"], "claude")

    def test_api_alias_normalizes_to_api_pool(self):
        settings = settings_with(first_tool="claude_api_key")
        self.assertEqual(settings["routing"]["first_tool"], "claude_api")

    @unittest.skipIf(os.name == "nt", "auth-check.sh requires a POSIX shell")
    def test_api_preflight_fails_closed_when_key_is_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            write_fake_claude(tmp_path)
            env = dict(os.environ)
            env.pop("ANTHROPIC_API_KEY", None)
            env["PATH"] = f"{tmp}{os.pathsep}/usr/bin{os.pathsep}/bin"
            completed = subprocess.run(
                ["bash", str(support.ROOT / "scripts" / "auth-check.sh"), "--only", "claude-api"],
                capture_output=True,
                text=True,
                env=env,
                check=False,
            )
        self.assertEqual(completed.returncode, 1, completed.stdout + completed.stderr)
        self.assertIn("missing env", completed.stdout)
        self.assertIn("ANTHROPIC_API_KEY", completed.stdout)

    @unittest.skipIf(os.name == "nt", "auth-check.sh requires a POSIX shell")
    def test_api_preflight_accepts_key_without_printing_secret(self):
        secret = "not-a-real-secret-value"
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            write_fake_claude(tmp_path)
            env = dict(os.environ)
            env["ANTHROPIC_API_KEY"] = secret
            env["PATH"] = f"{tmp}{os.pathsep}/usr/bin{os.pathsep}/bin"
            completed = subprocess.run(
                ["bash", str(support.ROOT / "scripts" / "auth-check.sh"), "--only", "claude-api"],
                capture_output=True,
                text=True,
                env=env,
                check=False,
            )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        self.assertIn("ok", completed.stdout)
        self.assertNotIn(secret, completed.stdout + completed.stderr)

    @unittest.skipIf(os.name == "nt", "auth-check.sh requires a POSIX shell")
    def test_subscription_preflight_flags_that_inherited_api_key_must_be_stripped(self):
        secret = "not-a-real-secret-value"
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            write_fake_claude(tmp_path)
            env = dict(os.environ)
            env["ANTHROPIC_API_KEY"] = secret
            env["CODING_DELEGATION_USAGE_FILE"] = str(tmp_path / "no-usage-limits")
            env["PATH"] = f"{tmp}{os.pathsep}/usr/bin{os.pathsep}/bin"
            completed = subprocess.run(
                ["bash", str(support.ROOT / "scripts" / "auth-check.sh"), "--only", "claude-subscription"],
                capture_output=True,
                text=True,
                env=env,
                check=False,
            )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        self.assertIn("must be stripped", completed.stdout)
        self.assertNotIn(secret, completed.stdout + completed.stderr)

    @unittest.skipIf(os.name == "nt", "route-model CLI test uses POSIX PATH conventions")
    def test_route_model_cli_builds_real_claude_api_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            user = tmp_path / "prefs.yaml"
            user.write_text(
                "routing:\n"
                "  first_tool: claude_api\n"
                "  extra_spend: per_job\n"
                "  tools:\n"
                "    claude:\n"
                "      enabled: false\n"
                "    claude_api:\n"
                "      enabled: true\n"
                "      plan: extra\n",
                encoding="utf-8",
            )
            completed = subprocess.run(
                [
                    "python3",
                    str(support.ROOT / "scripts" / "route-model.py"),
                    "choose",
                    "--difficulty",
                    "normal",
                    "--bytes",
                    "0",
                    "--roundtrip",
                    "0",
                    "--allow-extra",
                    "--fixtures",
                    str(support.FIXTURES),
                    "--user",
                    str(user),
                    "--repo",
                    tmp,
                    "--log",
                    str(tmp_path / "log.jsonl"),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["tool"], "claude_api")
        self.assertEqual(payload["billing_pool"], "claude_api")
        self.assertFalse(payload["usage"]["known"])
        self.assertIn("not queried", payload["usage"]["note"])

    def test_fallback_skips_api_pool_without_extra_spend_consent(self):
        settings = settings_with(
            on_limit_or_stall="handoff",
            extra_spend="deny",
            tools={
                "claude": {"enabled": True, "plan": "included"},
                "claude_api": {"enabled": True, "plan": "extra"},
                "codex": {"enabled": True, "plan": "included"},
            },
        )
        result = plan_fallback(
            current_tool="claude",
            tier="strong",
            reason="limit",
            eligible_tools=["claude", "claude_api", "codex"],
            settings=settings,
        )
        self.assertEqual(result["action"], "handoff")
        self.assertEqual(result["tool"], "codex")

    def test_fallback_can_use_api_pool_after_explicit_extra_spend_consent(self):
        settings = settings_with(
            on_limit_or_stall="handoff",
            extra_spend="per_job",
            tools={
                "claude": {"enabled": True, "plan": "included"},
                "claude_api": {"enabled": True, "plan": "extra"},
            },
        )
        result = plan_fallback(
            current_tool="claude",
            tier="strong",
            reason="limit",
            eligible_tools=["claude", "claude_api"],
            settings=settings,
            allow_extra_spend=True,
        )
        self.assertEqual(result["action"], "handoff")
        self.assertEqual(result["tool"], "claude_api")


if __name__ == "__main__":
    unittest.main()
