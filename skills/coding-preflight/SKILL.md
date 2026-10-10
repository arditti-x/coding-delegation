---
name: coding-preflight
description: >-
  Use before launching any coding surface from coding-delegation prefs (Cloud
  Agents, Claude/Codex/CLI cloud CLIs, other TTY cloud CLIs, or local git
  worktrees). Verifies remotes, auth, and branch pushability so sessions never
  start unable to push or open a PR.
---

# Coding preflight

Run this checklist **before** any coding session launch. If the chosen surface is not installed or not logged in, follow `docs/cli-setup.md` for that surface instead of inventing install or login commands. Prefer aborting early
over starting a session that cannot push or open a PR. Prefer the surface
already chosen via `delegate-coding` and user prefs; this skill does not rank
surfaces.

## Auth and usage gate (run first)

1. Run `bash <plugin>/scripts/auth-check.sh` (or `--only <surface>` for the chosen one). It prints one line per surface: `ok`, `logged out`, `usage exhausted`, `not installed`, `unknown` (the status command failed or timed out), or `unknown, manual` (that tool has no non-interactive status command; check it by hand as its `docs/agents/<agent>.md` says). It exits non-zero when any surface needs attention.
2. If the chosen surface is logged out, out of usage, or `unknown`: **STOP and alert the user before doing anything else.** Name the surface and what is needed, for example "Claude Code is logged out; needs the headless login in docs/agents/claude-code.md" or "Codex usage is exhausted until 2026-10-25". Do not fall back to the next surface silently. Fall back only after the alert, and say which surface you are moving to and why.
3. When a session reports a usage limit, record it in `~/.config/coding-delegation/usage-limits` (override with `CODING_DELEGATION_USAGE_FILE`), one line per limit: `<surface> <reset YYYY-MM-DD or unknown> [note]`, using the script's surface names (`claude-code`, `cursor-cli`, `codex`, `agy`, `kiro`, `grok-build`, `cursor-cloud-agents`). Use the reset date the tool showed; write `unknown` if it showed none. The script reports `usage exhausted` until that date passes. This file is local; never commit it.
4. Never paste status output raw: several status commands print the account email. The script prints neither emails nor tokens.

## Cloud keys mean cloud launches

A prefs key that names a cloud surface must launch that cloud variant. The local CLI with the same binary is a different surface.

- `claude_code_cloud` means `claude --cloud "<task>"` in a real TTY via Herdr (see `docs/agents/claude-code.md` and `docs/agents/herdr.md`). Running plain local `claude` is not `claude_code_cloud`.
- `codex_cloud` means Codex cloud (for example `codex cloud exec` after a ChatGPT login; see `docs/agents/codex.md`). Running local `codex` is not `codex_cloud`.
- Any other cloud key launches the cloud form its `docs/agents/<agent>.md` file documents.

Run a local CLI only if prefs list that local surface. Any fallback from cloud to local must be announced to the user, with the reason, before launch.

## Signing Claude Code back in

If `claude auth status` shows `loggedIn: false` on a headless box, use the **Headless box login** steps in `docs/agents/claude-code.md` (tmux, `claude auth login --claudeai`, Authorize in the box browser, read `code#state` from the callback URL, `tmux send-keys -l`, then verify). Ask the human only for a password, passkey, captcha you cannot solve, or SSO step. Keep codes and URLs out of chat and git.

## Checklist

### Remotes

- [ ] Repository has a usable `origin` (or named remote) with a fetch URL.
- [ ] Remote accepts pushes to feature branches (or the brief names an allowed remote).
- [ ] Default branch is known (`main` / `master` / project default).

### Auth

- [ ] Git credentials or credential helper can authenticate to the remote.
- [ ] Host CLI / cloud coding identity for the **chosen** surface can create branches and open PRs.
- [ ] Required org SSO / 2FA / fine-grained token scopes are already satisfied.
- [ ] No secrets will be pasted into the agent chat or brief file.

### Branch pushability

- [ ] Intended branch name is free or intentionally reused (`fix/…` preferred for durable handoffs).
- [ ] Local commits (if any) are on a **worktree** or dedicated branch — never the main checkout.
- [ ] Durable `fix/…` (or equivalent) is pushed **before** cloud teleport when local work must travel.
- [ ] Protected-branch rules will not block the planned PR target.

### Surface-specific

| Surface | Extra checks |
|---------|----------------|
| Cursor Cloud Agents | Repo is linked; agent can clone and open PR; brief path reachable or content inlined once. |
| Claude / Codex / Cursor CLI / AGY / Kiro / Grok Build / other TTY cloud CLIs | Session is a real **TTY**; use cloud-first options as documented by that CLI; bare non-TTY cloud CLIs are disallowed. |
| Git worktree | Path is outside the main working tree; branch is checked out only in that worktree. |

## Abort conditions

Stop launch (do not start the session) if any of the following hold:

1. Remote missing, wrong, or push denied.
2. Auth expired, usage exhausted, insufficient scopes, or SSO not completed (alert the user first; see Auth and usage gate).
3. Cannot create or push the planned branch.
4. Only path available is editing the main checkout in place.
5. Only available cloud path is a non-TTY bare CLI while prefs require a TTY.
6. Brief lacks merge policy or success criteria (complete via `build-handoff-brief` first).
7. Prefs missing or `setup_complete` false (run `setup-coding-delegation` first).
8. The prefs key is a cloud surface but the only thing available is the local CLI, and prefs do not list that local surface (announce it to the user with the reason; do not launch local quietly).

## After a clean preflight

Proceed to launch per `delegate-coding`, using the brief from `build-handoff-brief`
and the surface chosen from coding-delegation prefs.
