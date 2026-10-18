import json
import socket
import tempfile
import threading
import unittest
from pathlib import Path

import support
from model_routing.adapters import CODEX_USAGE_METHOD, DENIED_CODEX_METHODS, ADAPTERS
from model_routing.codex_rpc import _recv_text, build_usage_rpc_messages, rpc_over_unix
from model_routing.session_check import session_message
from model_routing.userconfig import user_config_to_prefs


class SafetyTest(unittest.TestCase):
    def test_commands_are_devnull_and_do_not_spend_credits(self):
        codex = ADAPTERS["codex"]
        for command in (
            codex.launch("gpt-6-luna", "hello"),
            codex.list_models(),
            codex.usage("/tmp/coding-delegation-rate-limits.sock"),
        ):
            self.assertEqual(command.stdin, "devnull")
            joined = " ".join(command.argv)
            self.assertNotIn("rateLimitResetCredit", joined)
            self.assertNotIn("consume", joined)
        usage = codex.usage("/tmp/coding-delegation-rate-limits.sock")
        self.assertIn("app-server", usage.argv)
        self.assertTrue(any(arg.startswith("unix://") for arg in usage.argv))
        self.assertEqual(usage.rpc_method, CODEX_USAGE_METHOD)
        claude = ADAPTERS["claude"].launch("sonnet", "hello")
        self.assertNotIn("--fallback-model", claude.argv)
        self.assertEqual(claude.stdin, "devnull")
        self.assertIsNone(ADAPTERS["cursor"].usage())

    def test_rpc_messages_are_only_the_read(self):
        messages = build_usage_rpc_messages()
        methods = [message["method"] for message in messages]
        self.assertEqual(methods, ["initialize", "initialized", "account/rateLimits/read"])
        self.assertNotIn("account/rateLimitResetCredit/consume", methods)
        self.assertIn("account/rateLimitResetCredit/consume", DENIED_CODEX_METHODS)
        with self.assertRaises(ValueError):
            from model_routing.codex_rpc import _reject_method

            _reject_method("account/rateLimitResetCredit/consume")

    def test_source_does_not_reference_the_cursor_dashboard(self):
        blob = []
        for path in (support.ROOT / "scripts").rglob("*.py"):
            blob.append(path.read_text(encoding="utf-8"))
        text = "\n".join(blob)
        for host in ("cursor.com/dashboard", "api2.cursor.sh", "api2.cursor.com"):
            self.assertNotIn("https://" + host, text)
            self.assertNotIn("http://" + host, text)

    def test_unix_socket_client_against_a_fake_server(self):
        fixture = json.loads((support.FIXTURES / "codex" / "rate_limits_ok.SYNTHETIC.json").read_text(encoding="utf-8"))
        seen = []

        def send_text(conn, text):
            payload = text.encode("utf-8")
            header = bytearray([0x81])
            size = len(payload)
            if size < 126:
                header.append(size)
            elif size < 65536:
                header.append(126)
                header.extend(size.to_bytes(2, "big"))
            else:
                header.append(127)
                header.extend(size.to_bytes(8, "big"))
            conn.sendall(bytes(header) + payload)

        def serve(path, ready):
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as server:
                server.bind(path)
                server.listen(1)
                ready.set()
                conn, _addr = server.accept()
                with conn:
                    conn.settimeout(5)
                    data = b""
                    while b"\r\n\r\n" not in data:
                        data += conn.recv(4096)
                    conn.sendall(b"HTTP/1.1 101 Switching Protocols\r\nUpgrade: websocket\r\nConnection: Upgrade\r\n\r\n")
                    while True:
                        message = json.loads(_recv_text(conn))
                        seen.append(message.get("method"))
                        if "id" not in message:
                            continue
                        if message.get("method") == CODEX_USAGE_METHOD:
                            body = dict(fixture)
                            body["id"] = message["id"]
                        else:
                            body = {"jsonrpc": "2.0", "id": message["id"], "result": {}}
                        send_text(conn, json.dumps(body))
                        if message.get("method") == CODEX_USAGE_METHOD:
                            return

        with tempfile.TemporaryDirectory() as tmp:
            path = str(Path(tmp) / "app.sock")
            ready = threading.Event()
            thread = threading.Thread(target=serve, args=(path, ready))
            thread.start()
            self.assertTrue(ready.wait(2))
            response = rpc_over_unix(path, timeout=5)
            thread.join(5)
        self.assertEqual(response["result"]["rateLimits"]["primary"]["usedPercent"], 23)
        self.assertNotIn("account/rateLimitResetCredit/consume", seen)

    def test_user_config_maps_into_generic_prefs(self):
        prefs = user_config_to_prefs(
            {
                "tool_claude": "true",
                "tool_codex": "false",
                "tool_cursor": "false",
                "plan_claude": "included",
                "first_tool": "claude",
                "frontier": "never",
                "extra_spend": "deny",
                "reviewer": "other vendor",
                "on_limit_or_stall": "ask first",
                "stall_timeout": "15",
                "versions": "pin",
                "pins": "sol=gpt-6-sol",
            }
        )
        self.assertTrue(prefs["routing"]["tools"]["claude"]["enabled"])
        self.assertFalse(prefs["routing"]["tools"]["codex"]["enabled"])
        self.assertEqual(prefs["routing"]["frontier"], "never")
        self.assertEqual(prefs["models"]["pins"]["sol"], "gpt-6-sol")
        self.assertEqual(prefs["routing"]["stall_timeout_min"], "15")

    def test_route_model_cli_reads_fixtures_only(self):
        import os
        import subprocess

        with tempfile.TemporaryDirectory() as tmp:
            user = Path(tmp) / "prefs.yaml"
            user.write_text(
                "routing:\n  first_tool: codex\n  tools:\n    codex:\n      enabled: true\n      plan: included\n",
                encoding="utf-8",
            )
            env = dict(os.environ)
            env["PATH"] = "/usr/bin:/bin"
            completed = subprocess.run(
                [
                    "python3",
                    str(support.ROOT / "scripts" / "route-model.py"),
                    "choose",
                    "--difficulty",
                    "small",
                    "--bytes",
                    "0",
                    "--roundtrip",
                    "0",
                    "--fixtures",
                    str(support.FIXTURES),
                    "--user",
                    str(user),
                    "--repo",
                    tmp,
                    "--log",
                    str(Path(tmp) / "log.jsonl"),
                ],
                capture_output=True,
                text=True,
                env=env,
                check=False,
            )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["model"], "gpt-6-luna")
        self.assertEqual(payload["launch"]["stdin"], "devnull")

    def test_session_hook_asks_until_routing_setup_is_done(self):
        import os
        import subprocess

        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            env = dict(os.environ)
            env["HOME"] = str(home)
            env["CODING_DELEGATION_USER_PREFS"] = str(home / "prefs.yaml")
            message = session_message(repo_root=Path(tmp), user_path=home / "prefs.yaml", home=home, user_config={})
            self.assertIn("setup-coding-delegation", message)
            self.assertIn("request_user_input", message)
            self.assertIn("3 questions", message)
            completed = subprocess.run(
                ["python3", str(support.ROOT / "hooks" / "session-start.py")],
                input="{}",
                text=True,
                capture_output=True,
                env=env,
                check=False,
            )
            self.assertEqual(completed.returncode, 0)
            payload = json.loads(completed.stdout)
            self.assertIn("additional_context", payload)
            self.assertIn("additionalContext", payload["hookSpecificOutput"])
            # A finished routing section stays quiet.
            (home / "prefs.yaml").write_text(
                "routing:\n  setup_complete: true\n  frontier: never\n",
                encoding="utf-8",
            )
            quiet = subprocess.run(
                ["python3", str(support.ROOT / "hooks" / "session-start.py")],
                input="{}",
                text=True,
                capture_output=True,
                env=env,
                check=False,
            )
            self.assertEqual(json.loads(quiet.stdout), {})


if __name__ == "__main__":
    unittest.main()
