---
name: build-handoff-brief
description: >-
  Use when preparing a file-based build brief for a standing builder seat or any
  coding surface selected via coding-delegation prefs. Defines required fields,
  a markdown template, and what must never be included. Required fields include
  Assumptions, Who runs it, and Deliverables (builder ships / requester runs).
  A brief missing those must not be sent; check it with check_brief.py first.
---

# Build handoff brief

Write the brief as a **file** (durable path in the repo or shared workspace). Do
not rely on chat paste alone. Domain/orchestrator bots write the brief; the
builder or the prefs-selected coding surface executes it.

## Required fields

| Field | Purpose |
|-------|---------|
| **Goal** | One concrete outcome the change must achieve. |
| **Repo** | Remote URL or org/name plus default branch. |
| **Constraints** | Languages, style, deps, APIs, deadlines, branch naming. |
| **Assumptions** | What the requester takes as given (e.g. connectors already work, auth is out of scope). |
| **Who runs it** | Who or what runs the result, and how (an agent run, a person, cron, CI). |
| **Deliverables** | Split in two: **Builder ships** (code, PR, script, notes) and **Requester runs** (what the requester runs or does afterward). |
| **Success criteria** | Testable checks (tests pass, PR open, CI green, etc.). |
| **Out of scope** | Explicit non-goals so the builder does not expand the job. |
| **Merge policy** | Who merges, when (e.g. builder merges when CI green), and PR target. |
| **Who to notify** | Channels or agents to ping on idle, blocker, or PR ready. |

**Do not send a brief that is missing Assumptions, Who runs it, or
Deliverables with both Builder ships and Requester runs filled in.** The
requester fills these; the builder does not invent them. A heading with only
an HTML comment, a bare `-`, or an empty `- [ ]` counts as missing. Without
them the builder guesses which side owns what and over-scopes (auth flows,
scheduling, refresh jobs nobody asked for).

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

## Assumptions
<!-- What you take as given, e.g. connectors already work, auth is out of scope -->
-

## Who runs it
<!-- Who or what runs the result, and how: agent run, person, cron, CI -->
-

## Deliverables

### Builder ships
<!-- Code, PR, script, notes -->
-

### Requester runs
<!-- What you run or do after the builder is done -->
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
- Route per coding-delegation prefs. Tool order comes from the user. The model comes from the opt-in tier catalog (frontier off unless allowed).
- Never edit the main checkout; use a worktree or cloud session branch.
- Push durable fix/… before cloud teleport if local work exists.
- Require a TTY for cloud CLIs when prefs say so.
- Monitor pings only on idle / blocker / PR — no ack-only chatter.
```

## What NOT to put in the brief

- Secrets, tokens, passwords, private keys, or session cookies.
- Ack-only chatter (“please confirm”, “say when started”) that burns tokens.
- Open-ended “improve everything” goals without success criteria.
- Instructions that replace the builder seat with the domain bot for merges.
- Product/MCP day-to-day tasks that belong to the domain bot, not the code seat.
- A hard-coded “always use Cloud Agents first” (or any other forced ranking). Routing belongs in coding-delegation prefs.

## After writing

1. Run `python3 skills/build-handoff-brief/check_brief.py <brief.md>`. If it prints `FAIL`, fill the named section; do not send the brief.
2. Save the file; saving the file does not notify anyone; send a message with the path and the one-line ask. Then pass its path into the launch command or chosen surface prompt.
3. Run `coding-preflight`.
4. Launch via `delegate-coding` (which uses user prefs only).
