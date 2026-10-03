# Cursor CLI

## What it is

Local terminal agent. Official binary name is `agent`, not `cursor`. Cursor CLI is Cursor's terminal coding agent for understanding, planning, building, debugging, and reviewing code.

## Install

macOS, Linux, and Windows (WSL):

```bash
curl https://cursor.com/install -fsS | bash
```

Windows (native) PowerShell:

```powershell
irm 'https://cursor.com/install?win32=true' | iex
```

Verify: `agent --version`. The install docs say to put `~/.local/bin` on `PATH` if the shell cannot find `agent`. Update: `agent update` (auto-update is the default).

**Warning (checked 2026-10-03 on Linux):** The xAI/Grok installer may take over `~/.local/bin/agent`; Cursor CLI's binary is also named `agent`. If both are needed, install Grok first, then re-run the Cursor CLI installer so `agent` is Cursor again. Invoke Grok as `grok`, not `agent`. This warning was checked by actually running both installers.

## Login

- Browser (recommended): `agent login`. Check: `agent status` (`whoami` is the same command). Sign out: `agent logout`.
- If the browser does not open: `NO_OPEN_BROWSER=1 agent login` and open the printed URL.
- API key: create one in Cursor Dashboard → API Keys, then `export CURSOR_API_KEY=...` or `agent --api-key ...`.

## Commands and skills

**Unknown.** The current official CLI pages do not publish a distinctive slash-command or named skill-invocation list.

## Ongoing session and answering questions

- **How it asks:** Before a terminal command, the CLI asks you to approve or reject it. Plan mode asks clarifying questions; the page does not say how those are shown.
- **How to answer:** `y` approves that terminal command. `n` rejects it. How to answer a Plan-mode clarifying question: unknown.
- **Blocks:** That terminal command does not run until you approve or reject it. Whether a Plan-mode question blocks the turn: unknown.

## Observed behavior

Observed 2026-10-03 (live sessions, Linux):

- `agent status` already logged in. `agent --trust "<prompt>"` in a worktree started with no new login. It asked a filename question. The answer `alpha.txt` was typed in that same session. It wrote `alpha.txt`.

## Quirks

**Warning (checked 2026-10-03 on Linux):** The xAI/Grok installer may take over `~/.local/bin/agent`; Cursor CLI's binary is also named `agent`. If both are needed, install Grok first, then re-run the Cursor CLI installer so `agent` is Cursor again. Invoke Grok as `grok`, not `agent`. This warning was checked by actually running both installers.

## Checked

2026-10-03

## Updated instructions

- Install: https://cursor.com/docs/cli/installation
- Login: https://cursor.com/docs/cli/reference/authentication
- Commands: https://docs.cursor.com/cli/overview
- Session questions: https://cursor.com/docs/cli/using
