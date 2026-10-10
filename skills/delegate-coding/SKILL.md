---
name: delegate-coding
description: >-
  Use when an orchestrator or domain bot needs to launch or route repo/PR coding
  work. Routes among licensed surfaces using user prefs only (Cloud Agents,
  Claude, Codex, Cursor CLI, AGY, Kiro, Grok Build, other TTY cloud CLIs, worktrees as
  peers). Enforces seat split and token rules. Does not replace a builder agent
  seat. Runs setup first when prefs are missing.
---

# Delegate coding

Hand coding work to the right execution surface. This skill teaches routing and
handoff. It does **not** turn the calling bot into a builder.

## Setup gate

Before routing:

1. Look for prefs at `coding-delegation.prefs.yaml` in the repo root, or at
   `~/.config/coding-delegation/prefs.yaml`, or in agent memory under
   `coding-delegation.prefs`.
2. If prefs are missing, unreadable, or `setup_complete` is not `true`, run
   **setup-coding-delegation** first. Do not invent licenses or invent an order.
3. Only proceed when `setup_complete` is true and at least one licensed surface
   remains available for the task.

## Surfaces (peers)

Treat every licensed surface as a peer. There is **no** built-in preference among
Cursor Cloud Agents, Claude Code cloud, Codex cloud, Cursor CLI, Antigravity
AGY, Kiro, Grok Build, other TTY cloud CLIs, or local worktrees. Ranking comes only from
`preferences.order` and the free-text `preferences.when` notes the user set.

Known surface keys (from setup):

| Key | Meaning |
|-----|---------|
| `cursor_cloud_agents` | Cursor Cloud Agents |
| `claude_code_cloud` | Claude Code cloud |
| `codex_cloud` | Codex cloud |
| `cursor_cli` | Cursor CLI |
| `agy_cloud` | Antigravity `agy` (Google AI Pro) on a TTY |
| `kiro_cloud` | Kiro cloud on a TTY |
| `grok_build` | Grok Build / xAI CLI on a TTY |
| `other_tty_cloud_clis` | User-named TTY cloud CLIs |
| `local_worktrees` | Isolated local git worktrees |

`grok_build` follows the same TTY cloud path as AGY and Kiro: run the
**coding-preflight** checks and launch only in a real TTY.

## Routing rules

1. Consider only surfaces with `licenses.<key>: true` (and named entries under
   `other_tty_cloud_clis`).
2. Walk `preferences.order` from first to last. Skip any entry that is not
   licensed or unfit for the task.
3. Use `preferences.when` notes to break ties or skip a surface that does not
   match the job (for example, interactive vs long PR vs offline).
4. If `order` is empty, ask the user which licensed peer to use for this task;
   do not silently pick a default winner.
5. Honor `defaults`: never code on the main checkout; require a TTY for cloud
   CLIs when `require_tty_for_cloud_clis` is true; run **coding-preflight** when
   `preflight_before_launch` is true.
6. A cloud key launches the cloud variant. `claude_code_cloud` is `claude --cloud "<task>"` in a real TTY via Herdr; `codex_cloud` is Codex cloud; other cloud keys use the cloud form in their `docs/agents/<agent>.md`. Running the local CLI of the same tool is a different surface and is allowed only if prefs list it.
7. Before using a surface, check its auth and usage (`coding-preflight`, `scripts/auth-check.sh`). See **Login and usage limits** below.

## Login and usage limits

- If the surface's login has expired or it hit a usage limit, **STOP and alert the user** before falling back. Name the surface and what is needed (for example "Claude Code login expired; run the headless login" or "Cursor CLI usage exhausted, resets 2026-11-06").
- Record the reset date when the tool shows one (see `coding-preflight`, step 3 of the auth gate).
- Never fall back silently. After alerting, move to the next licensed peer in `preferences.order` only, and say which surface you moved to and why.
- Any fallback from a cloud surface to a local CLI must be announced to the user with the reason, even when prefs allow that local surface.

## Decision guidance (prefs-driven)

| Situation | Route |
|-----------|--------|
| User prefs name a first-choice surface that is licensed and fit | That surface |
| First-choice unfit; next in `order` is fit | Next licensed peer in order |
| First-choice logged out or out of usage | Alert the user (surface, what is needed, reset date if known), then the next licensed peer in order |
| Prefs say `claude_code_cloud` | `claude --cloud` in a real TTY via Herdr, not local `claude` |
| Need interactive cloud shell; prefs allow a TTY cloud CLI | Named TTY cloud CLI (TTY required) |
| Must stay local; `local_worktrees` licensed | Git worktree (not main checkout) |
| Product / MCP day-to-day usage | Domain bot (not builder) |
| Merge when CI is green | Standing builder seat |

## Seat split

- **Standing builder seat** — owns code, branches, PRs, and merges when CI is green. Code-only.
- **Domain / orchestrator bots** — own product intent, MCP usage, and brief writing. They do not replace the builder.
- **Chosen coding surface** — executes the brief; reports blockers and PR links.

## Token rules

- No ack-only pings. Do not message “got it” or “working” without new status.
- Do not burn orchestrator tokens on long builds; launch once, then monitor sparingly.
- Monitor pings only on idle timeout, blocker, or PR ready.

## Launch sequence

1. Ensure setup is complete (see Setup gate).
2. Run **coding-preflight** when defaults require it — abort if remotes, auth, usage, or pushability fail, and alert the user on auth or usage failures.
3. Write the brief with **build-handoff-brief** (file on disk, not chat paste).
4. Push a durable `fix/…` (or equivalent) branch before any cloud teleport when local work exists.
5. Launch the surface selected from user prefs (peers only; no built-in ranking), in its cloud form when the key is a cloud surface.
6. Monitor only for idle, blocker, or PR; notify per the brief’s merge policy.
7. Builder merges when CI is green; domain bot stays on product/MCP.

The source of truth for each peer is [docs/agents/_template.md](../../docs/agents/_template.md) and the matching [docs/agents/<name>.md](../../docs/agents/); do not duplicate or invent those instructions here.

## Sibling skills

- `setup-coding-delegation` — licenses, order, and when-to-use prefs.
- `coding-preflight` — checklist before launch.
- `build-handoff-brief` — required brief fields and template.
- `agent-comms` — message a builder or another agent about a build, question, or reply.
