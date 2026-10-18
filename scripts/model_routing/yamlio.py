"""A small YAML subset reader and writer.

Covers the prefs and catalog files: nested maps, lists, scalars, comments,
and empty `[]` / `{}`. Not a general YAML library.
"""

from __future__ import annotations

from typing import Any


def loads(text: str) -> Any:
    lines: list[tuple[int, str]] = []
    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        text = _strip_inline_comment(raw.strip())
        if not text:
            continue
        lines.append((indent, text))
    if not lines:
        return {}
    value, index = _parse_block(lines, 0, lines[0][0])
    if index != len(lines):
        raise ValueError(f"yaml: leftover content at line {index + 1}")
    return value


def dumps(value: Any) -> str:
    return _dump(value, 0).rstrip("\n") + "\n"


def _parse_block(lines: list[tuple[int, str]], index: int, indent: int) -> tuple[Any, int]:
    if index >= len(lines):
        return {}, index
    if lines[index][0] != indent:
        return {}, index
    if lines[index][1].startswith("- "):
        return _parse_list(lines, index, indent)
    return _parse_map(lines, index, indent)


def _parse_map(lines: list[tuple[int, str]], index: int, indent: int) -> tuple[dict[str, Any], int]:
    result: dict[str, Any] = {}
    while index < len(lines):
        level, text = lines[index]
        if level < indent:
            break
        if level > indent:
            raise ValueError(f"yaml: unexpected indent in '{text}'")
        if text.startswith("- "):
            break
        key, sep, rest = text.partition(":")
        if not sep:
            raise ValueError(f"yaml: expected key: value, got '{text}'")
        key = key.strip()
        rest = rest.strip()
        index += 1
        if rest == "" or rest == "|" or rest == ">":
            if index < len(lines) and lines[index][0] > indent:
                child_indent = lines[index][0]
                child, index = _parse_block(lines, index, child_indent)
                result[key] = child
            else:
                result[key] = {} if rest == "" else rest
        else:
            result[key] = _scalar(rest)
    return result, index


def _parse_list(lines: list[tuple[int, str]], index: int, indent: int) -> tuple[list[Any], int]:
    result: list[Any] = []
    while index < len(lines):
        level, text = lines[index]
        if level < indent:
            break
        if level > indent:
            raise ValueError(f"yaml: unexpected indent in '{text}'")
        if not text.startswith("- "):
            break
        item = text[2:].strip()
        index += 1
        if item == "":
            if index < len(lines) and lines[index][0] > indent:
                child_indent = lines[index][0]
                child, index = _parse_block(lines, index, child_indent)
                result.append(child)
            else:
                result.append(None)
        elif item.endswith(":") and not _looks_like_scalar(item[:-1]):
            # "- key:" followed by a nested block, stored as a one-key map.
            key = item[:-1].strip()
            if index < len(lines) and lines[index][0] > indent:
                child_indent = lines[index][0]
                child, index = _parse_block(lines, index, child_indent)
                result.append({key: child})
            else:
                result.append({key: None})
        else:
            result.append(_scalar(item))
    return result, index


def _looks_like_scalar(text: str) -> bool:
    return text[:1] in ("'", '"') or text in {"true", "false", "null", "~"} or _is_number(text)


def _scalar(text: str) -> Any:
    if text.startswith("[") and text.endswith("]"):
        inner = text[1:-1].strip()
        if not inner:
            return []
        return [_scalar(part.strip()) for part in _split_flow(inner)]
    if text in {"[]"}:
        return []
    if text in {"{}"}:
        return {}
    if len(text) >= 2 and text[0] == text[-1] and text[0] in ("'", '"'):
        body = text[1:-1]
        if text[0] == '"':
            body = body.replace(r"\"", '"').replace(r"\\", "\\").replace(r"\n", "\n")
        return body
    lowered = text.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if lowered in {"null", "~"}:
        return None
    if _is_number(text):
        if any(ch in text for ch in ".eE"):
            return float(text)
        return int(text)
    return text


def _strip_inline_comment(text: str) -> str:
    quote = ""
    for index, char in enumerate(text):
        if quote:
            if char == quote:
                quote = ""
            continue
        if char in ("'", '"'):
            quote = char
            continue
        if char == "#" and (index == 0 or text[index - 1].isspace()):
            return text[:index].rstrip()
    return text


def _split_flow(text: str) -> list[str]:
    parts: list[str] = []
    current: list[str] = []
    quote = ""
    for char in text:
        if quote:
            current.append(char)
            if char == quote:
                quote = ""
            continue
        if char in ("'", '"'):
            quote = char
            current.append(char)
            continue
        if char == ",":
            parts.append("".join(current))
            current = []
            continue
        current.append(char)
    parts.append("".join(current))
    return parts


def _is_number(text: str) -> bool:
    if not text:
        return False
    try:
        float(text)
    except ValueError:
        return False
    return True


def _dump(value: Any, indent: int) -> str:
    pad = " " * indent
    if isinstance(value, dict):
        if not value:
            return "{}"
        lines: list[str] = []
        for key, child in value.items():
            if isinstance(child, (dict, list)) and child:
                lines.append(f"{pad}{key}:\n{_dump(child, indent + 2)}")
            else:
                lines.append(f"{pad}{key}: {_format_scalar(child)}\n")
        return "".join(lines)
    if isinstance(value, list):
        if not value:
            return "[]"
        lines = []
        for child in value:
            if isinstance(child, (dict, list)) and child:
                dumped = _dump(child, indent + 2)
                first, _, rest = dumped.partition("\n")
                lines.append(f"{pad}- {first.lstrip()}\n{rest}")
            else:
                lines.append(f"{pad}- {_format_scalar(child)}\n")
        return "".join(lines)
    return _format_scalar(value)


def _format_scalar(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int) and not isinstance(value, bool):
        return str(value)
    if isinstance(value, float):
        return repr(value)
    if isinstance(value, str):
        if value == "" or value.lower() in {"true", "false", "null", "~"} or _is_number(value):
            return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'
        if any(ch in value for ch in ":#{}[]&*!|>%@`'\"\n"):
            return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'
        return value
    if isinstance(value, dict) and not value:
        return "{}"
    if isinstance(value, list) and not value:
        return "[]"
    raise TypeError(f"cannot write {type(value).__name__}")
