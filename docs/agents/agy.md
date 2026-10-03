# Antigravity CLI (AGY)

## What it is

Google’s terminal agent. Binary `agy` (installed to `~/.local/bin/agy` on macOS/Linux). AGY is the Antigravity terminal agent with slash commands and Agent Skills.

## Install

macOS, Linux, and Googlebook:

```bash
curl -fsSL https://antigravity.google/cli/install.sh | bash
```

Windows PowerShell:

```powershell
irm https://antigravity.google/cli/install.ps1 | iex
```

Windows CMD:

```batch
curl -fsSL https://antigravity.google/cli/install.cmd -o install.cmd && install.cmd && del install.cmd
```

## Login

- Run `agy`. If the OS keyring already has a token, sign-in is silent. Otherwise the CLI opens a browser; sign in with the approved Google account.
- Over SSH the CLI prints an authorization URL. Open it locally, then paste the code the browser shows back into the SSH session.
- Sign out inside the CLI with `/logout` (clears keyring profiles).
- Optional, instead of an account session: set `"modelProvider": "gemini"` in `~/.gemini/antigravity-cli/settings.json` and `export GEMINI_API_KEY=...`. A key alone, without `modelProvider`, does nothing. Create the key in Google AI Studio.

## Commands and skills

| Command or skill | Use it for |
|---|---|
| `/skills` | Browse loaded local and global Agent Skills. |
| `/plugin` | Open the Plugins Manager or run plugin actions such as `list`, `install`, `enable`, and `disable`. |
| `agy plugin list` | List active plugins and their bundled skills. |
| `agy plugin install <path>` | Install a local plugin containing skills. |

Skills become slash commands in the interactive CLI; a skill named `deploy-staging` is invoked as `/deploy-staging`.

## Ongoing session and answering questions

- **How it asks:** In Ask mode, an interactive prompt card appears in the TUI and the agent pauses for approval.
- **How to answer:** `y` authorizes the proposed tool, command, or artifact. `n` rejects it. `Ctrl+K` approves the pending subagent action in the status alert. `Alt+J` moves to the next subagent waiting for confirmation.
- **Blocks:** Yes in the interactive TUI. Headless mode has no prompt: an Ask action is soft-denied, the run continues, and it exits 0.

## Observed behavior

Observed 2026-10-03 (live sessions, Linux):

- Not opened this round. `agy` starts a browser login if the OS keyring has no token.

## Quirks

unknown

## Checked

2026-10-03

## Updated instructions

- Install and login: https://antigravity.google/docs/cli/install/
- Commands: https://antigravity.google/docs/cli/reference/
- Session questions: https://antigravity.google/docs/cli/permissions/ and https://antigravity.google/docs/cli/headless/
