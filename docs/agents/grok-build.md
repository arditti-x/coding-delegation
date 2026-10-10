# Grok Build (xAI CLI)

## What it is

Coding agent from xAI. Binary `grok`. Grok Build is the xAI terminal agent with TUI commands, workflows, plugins, and user-invocable skills.

## Install

From the Grok Build overview.

macOS/Linux:

```bash
curl -fsSL https://x.ai/cli/install.sh | bash
```

Windows PowerShell:

```powershell
irm https://x.ai/cli/install.ps1 | iex
```

Start: `cd your-project` then `grok`. Version: `grok version`. Update: `grok update`.

**Warning (checked 2026-10-03 on Linux):** The xAI/Grok installer may take over `~/.local/bin/agent`; Cursor CLI's binary is also named `agent`. If both are needed, install Grok first, then re-run the Cursor CLI installer so `agent` is Cursor again. Invoke Grok as `grok`, not `agent`. This warning was checked by actually running both installers.

## Login

- On first launch, Grok opens a browser. Explicit sign-in: `grok login`. Sign out: `grok logout`.
- Headless or remote: `grok login --device-auth` (device-code auth).
- Non-browser environments can skip the account session with `export XAI_API_KEY="xai-..."` and then `grok`.

## Auth status check

unknown, manual check. `grok --help` and https://docs.x.ai/build/cli/reference (checked 2026-10-09) list `grok login` and `grok logout` but no status or whoami subcommand. `grok usage <SESSION_ID>` reports token and cost usage for one session, not account quota. Do not infer login from `~/.grok/auth.json`; see Observed behavior.

## Commands and skills

| Command or skill | Use it for |
|---|---|
| `/plan [description]` | Enter plan mode. |
| `/loop [interval] <prompt>` | Run a prompt on a recurring interval. |
| `/skills` | Open the Skills tab in the extensions modal. |
| `/workflow <name>` | Launch or control a saved workflow. |
| `/deep-research <prompt>` | Start the built-in research workflow. |
| `/local:commit` | Invoke a user skill with a qualified name when skill names collide. |
| `grok inspect` | Show discovered skills, plugins, hooks, and MCP servers. |

## Ongoing session and answering questions

- **How it asks:** Ask mode, the default, prompts before a tool call that is not already allowed.
- **How to answer:** On the Agent Dashboard (`Ctrl+\`, `/dashboard`, or `grok dashboard`), permission prompts and questions are answered inline with the number keys. Typing in the peek sends immediately if the agent is idle and queues the text if it is busy. Enter attaches to that session. The keyboard-shortcuts page does not name the keys for a prompt while you are attached to the session.
- **Blocks:** The tool call is not approved until the Ask-mode prompt is answered. Those sessions are grouped under Needs input. The permissions page does not say the attached session exits.

## Observed behavior

Observed 2026-10-03 (live sessions, Linux):

- A previous installer had used `~/.grok/auth.json`, but a new interactive `grok "<prompt>"` ignored that and demanded browser device auth. The session was killed while still “Waiting for approval” (about 308s). After that, `~/.grok/auth.json` was missing. Approving after the process died did not attach.

## Quirks

**Warning (checked 2026-10-03 on Linux):** The xAI/Grok installer may take over `~/.local/bin/agent`; Cursor CLI's binary is also named `agent`. If both are needed, install Grok first, then re-run the Cursor CLI installer so `agent` is Cursor again. Invoke Grok as `grok`, not `agent`. This warning was checked by actually running both installers.

`whoami` or login-status passing does not mean the next session starts. Grok can demand a fresh device login even when an auth file existed, and a device approval only counts if that process is still waiting.

## Checked

2026-10-03

## Updated instructions

- Install and first-run auth: https://docs.x.ai/build/overview
- Subcommands including `grok login`: https://docs.x.ai/build/cli/reference
- Commands: https://docs.x.ai/build/modes-and-commands
- Session questions: https://docs.x.ai/build/features/permissions and https://docs.x.ai/build/features/dashboard
