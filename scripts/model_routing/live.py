"""Live usage reads. Tests and CI must not import this module's runners.

Codex is started with stdin from /dev/null. The only JSON-RPC method is
account/rateLimits/read. Cursor is not queried.
"""

from __future__ import annotations

import json
import subprocess
import tempfile
import time
from pathlib import Path

from model_routing.adapters import CodexAdapter, unknown_usage, Usage
from model_routing.codex_rpc import rpc_over_unix


def read_codex_rate_limits(timeout: float = 20.0) -> Usage:
    adapter = CodexAdapter()
    with tempfile.TemporaryDirectory(prefix="coding-delegation-") as tmp:
        socket_path = str(Path(tmp) / "app.sock")
        command = adapter.usage(socket_path)
        process = subprocess.Popen(
            list(command.argv),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )
        try:
            deadline = time.monotonic() + timeout
            last_error: Exception | None = None
            while time.monotonic() < deadline:
                if process.poll() is not None:
                    break
                try:
                    payload = rpc_over_unix(socket_path, timeout=2.0)
                    return adapter.parse_usage(json.dumps(payload))
                except (FileNotFoundError, ConnectionRefusedError, OSError, RuntimeError) as exc:
                    last_error = exc
                    time.sleep(0.1)
            note = "codex rate-limit read failed"
            if last_error is not None:
                note = f"{note}: {last_error}"
            return unknown_usage(note)
        finally:
            if process.poll() is None:
                process.kill()
            process.wait(timeout=5)
