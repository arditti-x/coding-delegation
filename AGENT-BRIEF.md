# Brief: document the Mac laptop + Claude Code remote-control pattern

Repo: arditti-x/coding-delegation. Branch: `docs/mac-claude-remote-control` (stay on it, push to it, open a PR to main). Do NOT force-push. No secrets, no hostnames beyond what's below. Delete this AGENT-BRIEF.md in your final commit.

## Goal
Add a concise, generic section (repo's existing style: short headings, bullets, imperative) documenting a verified (2026-10-15) pattern for running Claude Code on the user's own Mac laptop. Keep it generic: "the user's Mac laptop (a registered machine)", not personal names/IDs.

Best fit: a new section in `skills/delegate-coding/SKILL.md` (e.g. "## Mac laptop surface (Claude Code remote control)"), plus a short row/note in the Surface-specific table of `skills/coding-preflight/SKILL.md`. Bump plugin.json patch version and add a CHANGELOG/README line only if the repo already has that convention.

## Facts to document (exactly these; don't invent more)
- Use: Mac-only work (Xcode builds, iOS simulator checks). The Mac has Claude Code, Xcode, an iOS simulator, and tmux. Each machine-targeted Shell call needs the user's approval, and the Mac must be awake (it is not always on) — use it per task, not as an always-on session.
- Always start Claude with remote control so the session shows in the user's Claude app. In the project folder:
  `tmux new-session -d -s <name> -x 200 -y 50 "claude --remote-control <name>"`
- Folder-trust prompt: answer with `tmux send-keys -t <name> Down` then `tmux send-keys -t <name> Enter`, only for folders we created or own.
- Send prompts: `tmux send-keys -t <name> -l '<prompt>'`, then a separate `tmux send-keys -t <name> Enter`.
- Read output: `tmux capture-pane -p -J -t <name> -S -N` (N = lines of scrollback), filtering blank lines (e.g. `| grep -v '^\s*$'`).
- Frugal-usage rule: drive the session through the terminal on the Mac (tmux over the machine shell), never through claude.ai/code in the agent's browser — screenshots cost far more usage. Do not use `claude remote-control --session-id` / `--continue` or teleport from the agent box; those move the session off the Mac.
- Never use plain `claude -p` on the Mac; always remote control.
- If the Mac reports "OAuth access token has expired", alert the user to run `claude auth login` on the Mac (ties into the existing Login and usage limits rules: stop and alert, no silent fallback).

## Acceptance
- Only skills/ (and version/changelog if conventional) changed. Markdown concise (~25-40 lines added total).
- Open PR; reply with the PR URL.
