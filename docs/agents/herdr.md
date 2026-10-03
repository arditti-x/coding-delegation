# Herdr

## What it is

Terminal multiplexer for running coding agents in real panes. It is the launcher, not a coding model. Each agent still uses that agent’s own install and login. Herdr is the terminal workspace and agent-orchestration surface. Its reusable agent skill teaches an agent to control Herdr from inside a Herdr-managed pane.

## Install

Linux or macOS:

```bash
curl -fsSL https://herdr.dev/install.sh | sh
```

Windows PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -c "irm https://herdr.dev/install.ps1 | iex"
```

If that fileless command is blocked, Command Prompt:

```batch
curl.exe -fsSLo install.cmd https://herdr.dev/install.cmd && install.cmd && del install.cmd
```

Also documented: `brew install herdr`, `mise use -g herdr`, a Nix flake, and GitHub release binaries. Verify by running `herdr`. Update a direct install with `herdr update`.

## Login

No Herdr account and no `herdr login` command are documented. Saved SSH machine profiles do not store passwords or keys. Remote machines use your existing OpenSSH auth (`ssh workbox` must already work). Add one with `herdr machine add workbox` in an interactive terminal. If a saved machine needs a key passphrase, `ssh-add` before Herdr’s background connections. Git or SSH signing inside remote panes needs `ForwardAgent yes` in your SSH config; Herdr does not turn that on for you.

## Commands and skills

| Command or skill | Use it for |
|---|---|
| `herdr --skill` | Print the release-matched Herdr agent skill. |
| `herdr pane run <pane_id> "<command>"` | Run and submit a command in a pane. |
| `herdr pane wait-output <pane_id> --regex "<pattern>"` | Wait for matching pane output. |
| `herdr agent prompt <target> "<text>" --wait` | Send a prompt to an agent and wait for a settled state. |
| `herdr agent wait --until <status>` | Wait for an agent status. |
| `herdr --remote <machine>` | Attach through SSH to a named remote session. |
| `npx skills add herdrdev/herdr --skill herdr -g` | Install Herdr's reusable agent skill globally. |

How it launches CLIs:

- Quick start: open `herdr`, then run the agent binary in a pane (`claude`, `codex`, or another supported agent). Herdr detects it.
- Automation: `herdr agent start` needs an existing shell pane at a prompt. It does not create the pane. Example from the agent-automation docs: `herdr agent start reviewer --kind codex --pane "$review_pane" -- -m gpt-5.4`. Arguments after `--` go to that agent’s executable. Documented `--kind` values include `claude`, `codex`, `cursor`, `agy`, `kiro`, and `grok`.
- Supported-agent table (screen detection / integrations) uses integration ids such as `claude`, `codex`, `cursor`, `grok`, `antigravity-cli`. Kiro CLI is listed as recognized without a Herdr integration install. Other agents still run as plain terminals.

Fleet note (not Herdr’s installer): Some Grok Bot fleets only start cloud CLIs inside Herdr panes, on a git worktree, and require the agent’s own login to already be done in that environment. That is local policy. Follow the matching agent file for install and login, then Herdr’s own docs for pane and `agent start` syntax. Do not copy org repo names or tokens into this file.

## Ongoing session and answering questions

- **How it asks:** Herdr sets the agent to `blocked` when it recognizes an approval or question UI in the pane.
- **How to answer:** Do not use `herdr agent prompt` while the agent is `blocked`. That returns `agent_blocked` and sends nothing. Read the pane with `herdr agent read`, then answer with `herdr agent send-keys` (`enter`, `up`, `esc`, or `ctrl+c`). Which key the dialog wants is the inner agent's UI, not a Herdr command.
- **Blocks:** Yes. The agent stays `blocked` until that dialog is handled. `herdr agent wait --until blocked` waits for that state.

## Observed behavior

Observed 2026-10-03 (live sessions, Linux):

- No login command. `herdr` exits “cannot attach without a usable terminal: Not a tty”.

## Quirks

unknown

## Checked

2026-10-03

## Updated instructions

- Install: https://herdr.dev/docs/install/
- First session: https://herdr.dev/docs/quick-start/
- SSH machines: https://herdr.dev/docs/connecting-machines/
- Which agents Herdr recognizes: https://herdr.dev/docs/agents/
- `herdr agent start`: https://herdr.dev/docs/agent-automation/
- Commands: https://herdr.dev/docs/cli-reference/
- Agent skill: https://herdr.dev/docs/agent-skill/
