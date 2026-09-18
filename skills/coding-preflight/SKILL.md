---
name: coding-preflight
description: >-
  Use before launching a Cloud Agent, Herdr-style TTY cloud CLI, or local git
  worktree. Verifies remotes, auth, and branch pushability so sessions never
  start unable to push or open a PR.
---

# Coding preflight

Run this checklist **before** any coding session launch. Prefer aborting early
over starting a session that cannot push or open a PR.

## Checklist

### Remotes

- [ ] Repository has a usable `origin` (or named remote) with a fetch URL.
- [ ] Remote accepts pushes to feature branches (or the brief names an allowed remote).
- [ ] Default branch is known (`main` / `master` / project default).

### Auth

- [ ] Git credentials or credential helper can authenticate to the remote.
- [ ] Host CLI / Cloud Agent identity can create branches and open PRs.
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
| Cloud Agent | Repo is linked; agent can clone and open PR; brief file path is reachable or content will be inlined once. |
| Herdr-style TTY | Session is **TTY**; cloud-first CLI; non-TTY bare cloud CLIs are disallowed. |
| Git worktree | Path is outside the main working tree; branch is checked out only in that worktree. |

## Abort conditions

Stop launch (do not start the session) if any of the following hold:

1. Remote missing, wrong, or push denied.
2. Auth expired, insufficient scopes, or SSO not completed.
3. Cannot create or push the planned branch.
4. Only path available is editing the main checkout in place.
5. Only available cloud path is a non-TTY bare CLI.
6. Brief lacks merge policy or success criteria (complete via `build-handoff-brief` first).

## After a clean preflight

Proceed to launch per `delegate-coding`, using the brief from `build-handoff-brief`.
