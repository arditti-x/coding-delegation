# Claude Code

## What it is

One CLI, binary `claude`. Local sessions and cloud sessions (`claude --cloud`) share that install. Cloud sessions are a product surface on top of the same login, not a second installer. Claude Code is Anthropic's terminal coding agent with built-in commands and bundled skills.

## Install

From the quickstart; native install is the recommended path.

macOS, Linux, WSL:

```bash
curl -fsSL https://claude.ai/install.sh | bash
```

Windows PowerShell:

```powershell
irm https://claude.ai/install.ps1 | iex
```

Windows CMD:

```batch
curl -fsSL https://claude.ai/install.cmd -o install.cmd && install.cmd && del install.cmd
```

Also documented: `brew install --cask claude-code`, `winget install Anthropic.ClaudeCode`, and apt/dnf/apk. Confirm with `claude --version`.

## Login

- Run `claude`. On first launch it opens a browser. Account types in the quickstart: Claude Pro, Max, Team, or Enterprise; Claude Console (API credits); Amazon Bedrock, Google Cloud’s Agent Platform, or Microsoft Foundry; or a self-hosted Claude apps gateway.
- If `ANTHROPIC_API_KEY` is set, the quickstart says Claude Code skips the browser login and asks you to approve the key.
- Re-authenticate inside a session with `/login`. CLI form from the CLI reference: `claude auth login` (optional `--email`, `--sso`, `--console`). Status: `claude auth status`. Logout: `claude auth logout` or `/logout`.
- Cloud sessions need the same claude.ai account (`claude auth login`). They are not available when Claude Code is configured only for a third-party provider such as Bedrock. Start a new cloud session with `claude --cloud "task"`. The cloud VM clones the current directory’s GitHub remote at the current branch, so push local commits first. Pull a cloud session back with `claude --teleport`.
- GitHub for cloud sessions: authorize the Claude GitHub App during web onboarding, or run `/web-setup` in the terminal to send the local `gh` CLI token to the Claude account (Teams/Enterprise may hide `/web-setup` until an Owner enables Quick web setup).

## Commands and skills

| Command or skill | Use it for |
|---|---|
| `/loop` | Re-run a prompt on a time interval. |
| `/goal` | Keep working toward a stated completion condition and stop when it is met, impossible, or needs an error fixed. |
| `/verify` | Build and run the app to confirm a change against the running app. |
| `/code-review` | Run Claude's bundled code-review skill. |

## Ongoing session and answering questions

- **How it asks:** `AskUserQuestion` opens a multiple-choice dialog in the same session. Separate permission prompts, including plan approval, also appear in that session.
- **How to answer:** Pick an option, or type your own text through the Other row or the notes field. In a confirmation dialog, Enter confirms and Escape declines. A dialog that shows `y` and `n` reads those letters itself.
- **Blocks:** Yes. `AskUserQuestion` stays open until you answer it, unless `askUserQuestionTimeout` is set. Permission prompts, including plan approval, never auto-resolve on idle.

## Observed behavior

Observed 2026-10-03 (live sessions, Linux):

- In an earlier install pass, not this Q&A round, `claude auth status` was logged out. Needs `claude` or `claude auth login` in a real terminal. Do not put an API key in chat.

## Quirks

unknown

## Checked

2026-10-03

## Updated instructions

- Install and first login: https://code.claude.com/docs/en/quickstart
- Auth commands: https://code.claude.com/docs/en/cli
- Cloud sessions: https://code.claude.com/docs/en/claude-code-on-the-web
- Commands: https://code.claude.com/docs/en/commands
- Session questions: https://code.claude.com/docs/en/tools and https://code.claude.com/docs/en/keybindings
