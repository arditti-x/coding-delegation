---
name: build-handoff-brief
description: >-
  Use when preparing a file-based build brief for a standing builder seat, Cursor
  Cloud Agent, or Herdr-style TTY session. Defines required fields, a markdown
  template, and what must never be included.
---

# Build handoff brief

Write the brief as a **file** (durable path in the repo or shared workspace). Do
not rely on chat paste alone. Domain/orchestrator bots write the brief; the
builder or Cloud Agent executes it.

## Required fields

| Field | Purpose |
|-------|---------|
| **Goal** | One concrete outcome the change must achieve. |
| **Repo** | Remote URL or org/name plus default branch. |
| **Constraints** | Languages, style, deps, APIs, deadlines, branch naming. |
| **Success criteria** | Testable checks (tests pass, PR open, CI green, etc.). |
| **Out of scope** | Explicit non-goals so the builder does not expand the job. |
| **Merge policy** | Who merges, when (e.g. builder merges when CI green), and PR target. |
| **Who to notify** | Channels or agents to ping on idle, blocker, or PR ready. |

## Template

```markdown
# Build brief

## Goal
<!-- One concrete outcome -->

## Repo
- Remote:
- Default branch:
- Working branch (suggested): fix/…

## Constraints
-

## Success criteria
- [ ]
- [ ]

## Out of scope
-

## Merge policy
- PR target:
- Merger: standing builder seat when CI is green
- Do not merge if:

## Who to notify
- On idle:
- On blocker:
- On PR ready:

## Notes for executor
- Prefer Cursor Cloud Agent; else Herdr-style TTY; else git worktree (never main checkout).
- Push durable fix/… before cloud teleport if local work exists.
- Monitor pings only on idle / blocker / PR — no ack-only chatter.
```

## What NOT to put in the brief

- Secrets, tokens, passwords, private keys, or session cookies.
- Ack-only chatter (“please confirm”, “say when started”) that burns tokens.
- Open-ended “improve everything” goals without success criteria.
- Instructions that replace the builder seat with the domain bot for merges.
- Product/MCP day-to-day tasks that belong to the domain bot, not the code seat.

## After writing

1. Save the file; pass its path into the launch command or Cloud Agent prompt.
2. Run `coding-preflight`.
3. Launch via `delegate-coding`.
