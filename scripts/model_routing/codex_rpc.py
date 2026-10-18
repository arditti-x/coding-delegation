"""Read Codex rate limits without spending a reset credit.

`codex exec` and `codex debug models` are started with stdin from /dev/null.
`codex app-server` is also started with stdin from /dev/null; its JSON-RPC
transport for this read is the unix socket (`--listen unix://PATH`).

The only method sent is `account/rateLimits/read`.
`account/rateLimitResetCredit/consume` is refused before any socket write.
"""

from __future__ import annotations

import base64
import json
import os
import socket
from typing import Any
from urllib.parse import unquote

from model_routing.adapters import DENIED_CODEX_METHODS, CODEX_USAGE_METHOD

ALLOWED_RPC_METHODS = frozenset({"initialize", "initialized", CODEX_USAGE_METHOD})


def build_usage_rpc_messages() -> list[dict[str, Any]]:
    messages = [
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {"clientInfo": {"name": "coding-delegation", "version": "0.4.0"}},
        },
        {"jsonrpc": "2.0", "method": "initialized", "params": {}},
        {"jsonrpc": "2.0", "id": 2, "method": CODEX_USAGE_METHOD, "params": {}},
    ]
    for message in messages:
        _reject_method(str(message.get("method")))
    return messages


def rpc_over_unix(socket_path: str, messages: list[dict[str, Any]] | None = None, timeout: float = 10.0) -> dict[str, Any]:
    """Speak the app-server websocket on a unix socket and return the usage response."""
    outgoing = messages if messages is not None else build_usage_rpc_messages()
    for message in outgoing:
        _reject_method(str(message.get("method")))
    path = _socket_path(socket_path)
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
        sock.settimeout(timeout)
        sock.connect(path)
        _upgrade(sock)
        pending = {message["id"]: None for message in outgoing if "id" in message}
        for message in outgoing:
            _send_text(sock, json.dumps(message))
            if "id" not in message:
                continue
            pending[message["id"]] = _read_until_id(sock, message["id"])
    response = pending.get(2)
    if not isinstance(response, dict):
        raise RuntimeError("codex rate-limit response missing")
    return response


def _reject_method(method: str) -> None:
    if method in DENIED_CODEX_METHODS or method not in ALLOWED_RPC_METHODS:
        raise ValueError(f"refusing Codex RPC method {method}")


def _socket_path(listen: str) -> str:
    if listen.startswith("unix://"):
        return unquote(listen[len("unix://"):])
    return listen


def _upgrade(sock: socket.socket) -> None:
    key = base64.b64encode(os.urandom(16)).decode("ascii")
    request = (
        "GET / HTTP/1.1\r\n"
        "Host: localhost\r\n"
        "Upgrade: websocket\r\n"
        "Connection: Upgrade\r\n"
        f"Sec-WebSocket-Key: {key}\r\n"
        "Sec-WebSocket-Version: 13\r\n"
        "\r\n"
    )
    sock.sendall(request.encode("ascii"))
    data = b""
    while b"\r\n\r\n" not in data:
        chunk = sock.recv(4096)
        if not chunk:
            raise RuntimeError("codex app-server closed before the websocket upgrade")
        data += chunk
    head = data.split(b"\r\n", 1)[0].decode("ascii", "replace")
    if " 101 " not in head:
        raise RuntimeError(f"codex app-server did not upgrade the socket ({head})")


def _send_text(sock: socket.socket, text: str) -> None:
    payload = text.encode("utf-8")
    mask = os.urandom(4)
    header = bytearray([0x81])
    length = len(payload)
    if length < 126:
        header.append(0x80 | length)
    elif length < 65536:
        header.append(0x80 | 126)
        header.extend(length.to_bytes(2, "big"))
    else:
        header.append(0x80 | 127)
        header.extend(length.to_bytes(8, "big"))
    header.extend(mask)
    masked = bytes(byte ^ mask[index % 4] for index, byte in enumerate(payload))
    sock.sendall(bytes(header) + masked)


def _read_until_id(sock: socket.socket, expected: int) -> dict[str, Any]:
    while True:
        text = _recv_text(sock)
        if not text:
            continue
        try:
            value = json.loads(text)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict) and value.get("id") == expected:
            return value


def _recv_text(sock: socket.socket) -> str:
    first = _recv_exact(sock, 2)
    if not first:
        raise RuntimeError("empty websocket frame")
    length = first[1] & 0x7F
    if length == 126:
        length = int.from_bytes(_recv_exact(sock, 2), "big")
    elif length == 127:
        length = int.from_bytes(_recv_exact(sock, 8), "big")
    mask = b""
    if first[1] & 0x80:
        mask = _recv_exact(sock, 4)
    payload = _recv_exact(sock, length)
    if mask:
        payload = bytes(byte ^ mask[index % 4] for index, byte in enumerate(payload))
    opcode = first[0] & 0x0F
    if opcode == 0x8:
        raise RuntimeError("codex app-server closed the socket")
    if opcode == 0x1:
        return payload.decode("utf-8", "replace")
    return ""


def _recv_exact(sock: socket.socket, size: int) -> bytes:
    chunks = bytearray()
    while len(chunks) < size:
        part = sock.recv(size - len(chunks))
        if not part:
            raise RuntimeError("socket closed")
        chunks.extend(part)
    return bytes(chunks)
