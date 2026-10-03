---
name: agent-comms
description: >-
  Use this when messaging a builder or another agent about a build, a question, or
  a reply, including how to get a response back, how to answer their questions,
  and how to answer a question from a running coding-agent session.
---

# Agent communication

## 1. Start the handoff or question

For a build, the file brief is the spec: repo, goal, constraints, done-when, and
do-nots. The file brief still comes from **build-handoff-brief**. A direct message
with the brief path and the one-line ask is required to wake the builder; a file
drop alone does not reach them. A short question with no build can be a message
only.

## 2. Read the response

The builder messages you back. It arrives as your later turn, not a reply inside
yours. Read that message. If they need you to act, they mark it so it wakes you.
Status/FYI waits until your next turn. Do not poll their chat and do not sit in
your turn waiting.

## 3. Answer the builder

Answer with a new message to them. Put the decision in the message. If you
changed the brief, say what changed and the path. If they were blocked on you,
mark the reply so it wakes them.

## 4. Do not waste messages

Never send ack-only pings ("got it", "thanks", "on it"); wait in the same turn
for their reply; re-send the same ask while one is in flight; assume they re-read
a file you edited unless you message them; wake them for an FYI; or fan the same
job out to several agents.

## Questions from the coding agent

This is the session you launched (Claude Code, Codex, Cursor CLI, a Cursor Cloud
Agent, AGY, Kiro, Grok Build, or a Herdr pane). It is not the builder seat in
sections 1–4.

- Answer in the same session that asked. Do not start a second agent for the same question.
- Do not ack-only. Put the decision in the answer.
- If you cannot answer, say what is blocking and who must decide.

How that session asks, how to answer, and whether it blocks are in the Questions
note for that vendor in [docs/vendor-tools.md](../../docs/vendor-tools.md). If
the note says unknown, do not invent a command or a key. Checked 2026-10-03.

## Observed 2026-10-03 (live sessions, Linux)

These are observed session results, not a guessed protocol:

- **Cursor CLI:** `agent status` already logged in. `agent --trust "<prompt>"` in a worktree started with no new login. It asked a filename question. The answer `alpha.txt` was typed in that same session. It wrote `alpha.txt`.
- **Codex:** `codex login status` said logged in using ChatGPT. `codex "<prompt>"` still blocked on “Trust this folder?” for the worktree root before any model question. That prompt needs a keypress in the same terminal. It could not be answered from a non-interactive driver. Session killed. No file written.
- **Kiro:** `kiro-cli whoami` was logged in. `kiro-cli chat "<prompt>"` accepted the task and the answer `alpha.txt`, then blocked on “write requires approval” with choices Yes (single permission), Trust (always allow in this session), No. That is a permission prompt, not login. File was not written.
- **Grok:** A previous installer had used `~/.grok/auth.json`, but a new interactive `grok "<prompt>"` ignored that and demanded browser device auth. The session was killed while still “Waiting for approval” (about 308s). After that, `~/.grok/auth.json` was missing. Approving after the process died did not attach.
- **Claude Code:** In an earlier install pass, not this Q&A round, `claude auth status` was logged out. Needs `claude` or `claude auth login` in a real terminal. Do not put an API key in chat.
- **AGY:** Not opened this round. `agy` starts a browser login if the OS keyring has no token.
- **Herdr:** No login command. `herdr` exits “cannot attach without a usable terminal: Not a tty”.
- **Quirk:** `whoami` or login-status passing does not mean the next session starts. Codex adds a folder-trust prompt, Kiro adds a write-approval prompt, Grok can demand a fresh device login even when an auth file existed, and a device approval only counts if that process is still waiting.
