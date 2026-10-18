#!/usr/bin/env python3
"""Choose a tool and model from merged prefs and fixture or live reports.

With --fixtures, this reads only the files in that directory. It does not
spawn claude, codex, or agent, and it does not use the network.
Without --fixtures, live usage reads are a separate step: this CLI still
refuses to run unless --fixtures is set, so a test or CI job cannot call a
real CLI by accident.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from model_routing.adapters import CodexAdapter, ClaudeAdapter, unknown_usage  # noqa: E402
from model_routing.catalog import load_catalog  # noqa: E402
from model_routing.prejob import prejob  # noqa: E402
from model_routing.settings import load_merged  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="coding-delegation model routing")
    sub = parser.add_subparsers(dest="cmd", required=True)
    choose = sub.add_parser("choose")
    choose.add_argument("--difficulty", required=True, choices=("hard", "normal", "small"))
    choose.add_argument("--bytes", type=float, default=0)
    choose.add_argument("--roundtrip", type=float, default=0)
    choose.add_argument("--reserve", type=int, default=32000)
    choose.add_argument("--frontier", action="store_true")
    choose.add_argument("--allow-extra", action="store_true")
    choose.add_argument("--repo", type=Path, default=None)
    choose.add_argument("--user", type=Path, default=None)
    choose.add_argument("--fixtures", type=Path, default=None)
    choose.add_argument("--claude-usage", type=Path, default=None)
    choose.add_argument("--codex-rate-limits", type=Path, default=None)
    choose.add_argument("--codex-models", type=Path, default=None)
    choose.add_argument("--log", type=Path, default=None)
    choose.add_argument("--prompt", default="")
    args = parser.parse_args(argv)
    if args.cmd == "choose":
        if args.fixtures is None and not any((args.claude_usage, args.codex_rate_limits, args.codex_models)):
            parser.error("pass --fixtures or captured CLI files; this command never runs a CLI")
        reports = _reports(args)
        settings = load_merged(repo_root=args.repo, user_path=args.user)
        job = {
            "difficulty": args.difficulty,
            "bytes_in_scope": args.bytes,
            "roundtrip_tokens": args.roundtrip,
            "output_reserve": args.reserve,
            "frontier": args.frontier,
            "allow_extra_spend": args.allow_extra,
            "prompt": args.prompt,
        }
        result = prejob(job, settings, reports, catalog=load_catalog(), log_to=args.log)
        json.dump(result, sys.stdout, indent=2, default=_json_default)
        sys.stdout.write("\n")
        return 0
    return 2


def _reports(args) -> dict:
    directory = args.fixtures
    claude_path = args.claude_usage
    rate_path = args.codex_rate_limits
    models_path = args.codex_models
    if directory is not None:
        claude_path = claude_path or _first(
            directory / "claude" / "usage_partial.SYNTHETIC.result.json",
            directory / "claude" / "usage_at_limit.result.json",
        )
        rate_path = rate_path or _first(directory / "codex" / "rate_limits_ok.SYNTHETIC.json")
        models_path = models_path or _first(directory / "codex" / "debug_models.json")
    claude = ClaudeAdapter()
    codex = CodexAdapter()
    return {
        "claude": {"usage": claude.parse_usage(_read(claude_path))},
        "codex": {
            "usage": codex.parse_usage(_read(rate_path)) if rate_path else unknown_usage(),
            "models": json.loads(_read(models_path)) if models_path and _read(models_path).strip() else {"models": []},
        },
        "cursor": {"usage": unknown_usage("Cursor has no public per-user usage API")},
    }


def _first(*paths: Path) -> Path | None:
    for path in paths:
        if path.is_file():
            return path
    return None


def _read(path: Path | None) -> str:
    if path is None or not path.is_file():
        return ""
    return path.read_text(encoding="utf-8")


def _json_default(value):
    if hasattr(value, "as_dict"):
        return value.as_dict()
    raise TypeError(type(value).__name__)


if __name__ == "__main__":
    raise SystemExit(main())
