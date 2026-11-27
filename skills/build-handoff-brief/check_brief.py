#!/usr/bin/env python3
"""Fail if a build brief lacks Assumptions, Who runs it, or split Deliverables.

Usage:
  check_brief.py BRIEF.md [...]      each section must have real content
  check_brief.py --template SKILL.md the template must carry the headings
"""
import re
import sys

REQUIRED = [
    ("##", "Assumptions"),
    ("##", "Who runs it"),
    ("###", "Builder ships"),
    ("###", "Requester runs"),
]
# Content that does not count: blank lines, bare dashes, empty checkboxes.
STUB = re.compile(r"^\s*(?:[-*]\s*(?:\[[ xX]?\]\s*)?)?$")


def sections(text):
    """Map (level, title) -> body lines, ending at the next heading of any level."""
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    found, key = {}, None
    for line in text.splitlines():
        m = re.match(r"^(#{2,3})\s+(.+?)\s*$", line)
        if m:
            key = (m.group(1), m.group(2).lower())
            found.setdefault(key, [])
        elif key:
            found[key].append(line)
    return found


def problems(path, template):
    found = sections(open(path, encoding="utf-8").read())
    out = []
    if ("##", "deliverables") not in found:
        out.append("missing section: ## Deliverables")
    for level, title in REQUIRED:
        body = found.get((level, title.lower()))
        if body is None:
            out.append(f"missing section: {level} {title}")
        elif not template and all(STUB.match(l) for l in body):
            out.append(f"empty section: {level} {title}")
    return out


def main(argv):
    template = argv[:1] == ["--template"]
    paths = argv[1:] if template else argv
    if not paths:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    failed = False
    for path in paths:
        errs = problems(path, template)
        for e in errs:
            print(f"FAIL {path}: {e}")
        if not errs:
            print(f"ok   {path}")
        failed |= bool(errs)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
