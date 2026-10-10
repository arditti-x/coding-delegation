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
- Re-authenticate inside a session with `/login`. CLI form from the CLI reference: `claude auth login` (optional `--claudeai` (Claude subscription, the default), `--email`, `--sso`, `--console`; per `claude auth login --help`, checked 2026-10-09). Status: `claude auth status`. Logout: `claude auth logout` or `/logout`.
- Cloud sessions need the same claude.ai account (`claude auth login`). They are not available when Claude Code is configured only for a third-party provider such as Bedrock. Start a new cloud session with `claude --cloud "task"`. The cloud VM clones the current directory’s GitHub remote at the current branch, so push local commits first. Pull a cloud session back with `claude --teleport`.
- GitHub for cloud sessions: authorize the Claude GitHub App during web onboarding, or run `/web-setup` in the terminal to send the local `gh` CLI token to the Claude account (Teams/Enterprise may hide `/web-setup` until an Owner enables Quick web setup).

### Headless box login (verified 2026-10-09, Linux)

Use this when Claude Code runs on a remote or headless box and a browser on that same box is already signed in to claude.ai. A human is needed only if Claude asks for a password, passkey, or SSO step.

1. In tmux (a real TTY is required), run `claude auth login --claudeai`. It prints an authorize URL at `https://claude.com/cai/oauth/authorize?...` and waits at `Paste code here if prompted >`.
2. Open that exact URL in the box browser that is signed in to claude.ai and click **Authorize**. A picture captcha may appear; solve it or hand it to the human.
3. The browser lands on `https://platform.claude.com/oauth/code/callback?code=<CODE>&state=<STATE>`. Read `code` and `state` from the address bar and form `<CODE>#<STATE>`. Do not rely on the clipboard: when a human copies the code from a remote-desktop viewer, it lands on their own clipboard, not the box's. That failed on 2026-10-09.
4. Paste it literally into the waiting prompt, then press Enter:

   ```bash
   tmux send-keys -t <session> -l '<CODE>#<STATE>'
   tmux send-keys -t <session> Enter
   ```

5. Verify with `claude auth status` (`loggedIn: true`).
6. Restarting `claude auth login` changes the PKCE challenge and invalidates any earlier code. Always use the code from the current session's URL. If the browser still shows an old callback page, start over from step 1.

Keep real codes, state values, authorize URLs with real challenge values, and the account email out of chat, briefs, logs, and git.

## Auth status check

- Command: `claude auth status` (JSON by default; `--json` or `--text`). Logged in when `loggedIn` is `true`. Verified live on 2026-10-09 (Linux): returns JSON with `loggedIn`; the output also contains the account email, so never paste it raw.
- Logged-out output was not observed live; the script treats `"loggedIn": false` as logged out and anything else as unknown.
- Usage limits: no non-interactive usage command found in the CLI help (`claude --help`, `claude auth status --help`, checked 2026-10-09). When a session reports a limit, record it in the local usage-limits file (see `coding-preflight`).

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

Observed 2026-10-09 (Linux): the login had expired without any alert, and work quietly moved to other surfaces. A pasted code of 34 characters with a space was rejected; the real `code#state` is about 100 characters with one `#`. The Headless box login flow above then succeeded and `claude auth status` showed `loggedIn: true`.

Observed 2026-10-03 (live sessions, Linux):

- In an earlier install pass, not this Q&A round, `claude auth status` was logged out. Needs `claude` or `claude auth login` in a real terminal. Do not put an API key in chat.

## Quirks

- `claude --cloud` (Claude Code cloud) and plain `claude` (local) are different surfaces in prefs (`claude_code_cloud` vs a local CLI entry). Do not substitute one for the other; see `delegate-coding`.
- A login code copied by a remote viewer does not reach the box clipboard; read it from the callback URL instead (Headless box login, step 3).

## Checked

2026-10-09

## Updated instructions

- Install and first login: https://code.claude.com/docs/en/quickstart
- Auth commands: https://code.claude.com/docs/en/cli
- Cloud sessions: https://code.claude.com/docs/en/claude-code-on-the-web
- Commands: https://code.claude.com/docs/en/commands
- Session questions: https://code.claude.com/docs/en/tools and https://code.claude.com/docs/en/keybindings
