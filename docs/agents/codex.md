# Codex

## What it is

Local coding agent from OpenAI. Binary `codex`. Codex cloud is separate: it requires a ChatGPT sign-in and a published cloud environment. An API key is not enough for Codex cloud. Codex is OpenAI's coding agent available through the CLI, IDE extension, and app.

## Install

From the Codex CLI page.

macOS/Linux:

```bash
curl -fsSL https://chatgpt.com/codex/install.sh | sh
```

The same page also documents npm (`npm install -g @openai/codex`) and Homebrew (`brew install --cask codex`). The GitHub README documents a Windows installer:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://chatgpt.com/codex/install.ps1 | iex"
```

## Login

Local CLI:

- Run `codex` in a project directory and choose **Sign in with ChatGPT**, or run `codex login` and finish the browser flow.
- API key (local workflows only; usage-based): `printenv OPENAI_API_KEY | codex login --with-api-key`
- Enterprise automation (ChatGPT Enterprise, admin must grant the access token permission): `printenv CODEX_ACCESS_TOKEN | codex login --with-access-token`
- Check: `codex login status` (exits 0 when logged in). Sign out: `codex logout`.
- Headless or remote, when the browser callback cannot reach the CLI: choose **Sign in with Device Code** in the login UI or run `codex login --device-auth` (beta; device-code login must be enabled in ChatGPT security settings or workspace permissions). Docs also describe copying `~/.codex/auth.json` or forwarding `localhost:1455`. Treat that file like a password.

Codex cloud (no separate CLI install):

- Open ChatGPT on the web, mobile, or desktop app and sign in with a ChatGPT account. API-key sign-in does not enable Codex cloud.
- If you log in with email and password, the auth docs require MFA before Codex cloud. Social login and SSO have their own MFA rules on that page.
- On the web or desktop app: **Work in > Cloud**, then select or create an environment (connect GitHub if prompted, review setup, **Publish**). On mobile, open Codex.
- From the CLI, after the same ChatGPT login: `codex cloud` opens a picker; `codex cloud exec` submits a task; `codex cloud list` lists recent cloud chats. `codex apply` applies the latest cloud diff locally.

## Commands and skills

| Command or skill | Use it for |
|---|---|
| `/skills` | Browse and apply local skills. |
| `$skill-name` | Explicitly invoke a named skill. |
| `codex exec` | Run a non-interactive prompt for scripts, CI, or automation. |
| `/init` | Scaffold an `AGENTS.md` starter file. |
| `/review` | Review code changes. |
| `/goal` | Set, edit, pause, resume, view, or clear a persistent task goal. |

## Ongoing session and answering questions

- **How it asks:** With an interactive approval policy, Codex stops and asks before an action that policy requires, such as leaving the sandbox, using the network, a side-effecting app or MCP tool, or a `request_permissions` prompt.
- **How to answer:** Unknown. The official pages do not name the key that accepts or declines that prompt. `/permissions` changes the approval preset. `/approve` retries one recent auto-review denial.
- **Blocks:** Yes while approvals are interactive (`on-request`, or a granular policy that still surfaces that prompt). `--ask-for-approval never` does not ask. `approval_policy = "untrusted"` is retired and can stop Codex from starting; remove it from config. Codex may also start read-only until you trust the working directory through an onboarding prompt or `/permissions`.

## Observed behavior

Observed 2026-10-03 (live sessions, Linux):

- `codex login status` said logged in using ChatGPT. `codex "<prompt>"` still blocked on “Trust this folder?” for the worktree root before any model question. That prompt needs a keypress in the same terminal. It could not be answered from a non-interactive driver. Session killed. No file written.

## Quirks

`whoami` or login-status passing does not mean the next session starts. Codex adds a folder-trust prompt.

## Checked

2026-10-05

## Updated instructions

- CLI install: https://learn.chatgpt.com/docs/codex/cli
- Auth: https://learn.chatgpt.com/docs/auth
- Cloud: https://learn.chatgpt.com/docs/cloud
- CLI commands, flags, and slash commands: https://learn.chatgpt.com/docs/developer-commands?surface=cli
- Windows installer also stated in https://github.com/openai/codex
- Session questions: https://learn.chatgpt.com/docs/agent-approvals-security

The old developers.openai.com/codex pages redirect to these as of 2026-10-05.
