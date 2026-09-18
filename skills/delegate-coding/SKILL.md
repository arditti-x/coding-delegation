---
name: delegate-coding
description: >-
  Use when an orchestrator or domain bot needs to launch or route repo/PR coding
  work. Chooses Cloud Agents, Herdr-style TTY cloud CLIs, or git worktrees;
  enforces seat split and token rules. Does not replace a builder agent seat.
---

# Delegate coding

Hand coding work to the right execution surface. This skill teaches routing and
handoff. It does **not** turn the calling bot into a builder.

## Preference order

1. **Cursor Cloud Agents** — default for repo changes, branches, and pull requests.
2. **Herdr-style TTY cloud-first CLIs** — only when Cloud Agents are unavailable or unfit; always use a TTY session (never bare non-TTY cloud CLIs).
3. **Local git worktrees** — last resort; create an isolated worktree. Never code on the main checkout.

## Decision table

| Situation | Route |
|-----------|--------|
| Need a PR or remote branch from a repo | Cloud Agent |
| Cloud Agents blocked; need interactive cloud shell | Herdr-style TTY cloud CLI |
| Must stay local; need isolated checkout | Git worktree (not main) |
| Product / MCP day-to-day usage | Domain bot (not builder) |
| Merge when CI is green | Standing builder seat |

## Seat split

- **Standing builder seat** — owns code, branches, PRs, and merges when CI is green. Code-only.
- **Domain / orchestrator bots** — own product intent, MCP usage, and brief writing. They do not replace the builder.
- **Cloud Agent / TTY session** — executes the brief; reports blockers and PR links.

## Token rules

- No ack-only pings. Do not message “got it” or “working” without new status.
- Do not burn orchestrator tokens on long builds; launch once, then monitor sparingly.
- Monitor pings only on idle timeout, blocker, or PR ready.

## Launch sequence

1. Run **coding-preflight** — abort if remotes/auth/pushability fail.
2. Write the brief with **build-handoff-brief** (file on disk, not chat paste).
3. Push a durable `fix/…` (or equivalent) branch before any cloud teleport when local work exists.
4. Launch Cloud Agent (preferred) or Herdr-style TTY / worktree per the table.
5. Monitor only for idle, blocker, or PR; notify per the brief’s merge policy.
6. Builder merges when CI is green; domain bot stays on product/MCP.

## Sibling skills

- `coding-preflight` — checklist before launch.
- `build-handoff-brief` — required brief fields and template.
