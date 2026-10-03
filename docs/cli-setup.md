> **Superseded by [docs/agents/](./agents/).** Use [docs/agents/_template.md](./agents/_template.md) and the matching per-agent file. Install and login notes below are kept so old links do not 404. Do not treat this file as the source of truth.

# CLI and Herdr setup

Install and login notes for the named coding-delegation peers, plus Herdr and a generic path for any other coding CLI.

These commands are copied from vendor docs. They are documentation only. This plugin does not run installers. Vendor installers change often: use the **Updated instructions** URL if a command fails, and record a new checked date when you re-read that page.

Checked means the date this repo’s author fetched the linked page, not a vendor release date.

## Cursor Cloud Agents

Cloud agents that run in Cursor-managed VMs. This peer is not a local CLI. Do not install a binary for it. The Cursor CLI (`agent`) is a different peer, below.

**Install:** No local install.

**Login / access:**

- Sign in to a Cursor account. Cloud Agents require a paid Cursor plan.
- Before anyone can start an agent from a repository, a Cursor account admin connects source control: GitHub (Cloud and Enterprise Server), GitLab (Cloud and Self-Hosted), Bitbucket Cloud, or Azure DevOps. You need read-write access to the repo.
- Start agents from [cursor.com/agents](https://cursor.com/agents), from Cursor Desktop (Cloud in the agent-input dropdown), or from the other surfaces listed in the docs (iOS, Slack, GitHub or Bitbucket `@cursor`, Linear, API).
- If a run does not start, the docs say to confirm you are logged in, source control is connected, repository permissions are sufficient, and the account is on a paid plan.

**Checked:** 2026-10-03

**Updated instructions:** https://cursor.com/docs/cloud-agent

## Claude Code CLI and Claude Code cloud

One CLI, binary `claude`. Local sessions and cloud sessions (`claude --cloud`) share that install. Cloud sessions are a product surface on top of the same login, not a second installer.

**Install** (from the quickstart; native install is the recommended path):

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

**Login:**

- Run `claude`. On first launch it opens a browser. Account types in the quickstart: Claude Pro, Max, Team, or Enterprise; Claude Console (API credits); Amazon Bedrock, Google Cloud’s Agent Platform, or Microsoft Foundry; or a self-hosted Claude apps gateway.
- If `ANTHROPIC_API_KEY` is set, the quickstart says Claude Code skips the browser login and asks you to approve the key.
- Re-authenticate inside a session with `/login`. CLI form from the CLI reference: `claude auth login` (optional `--email`, `--sso`, `--console`). Status: `claude auth status`. Logout: `claude auth logout` or `/logout`.
- Cloud sessions need the same claude.ai account (`claude auth login`). They are not available when Claude Code is configured only for a third-party provider such as Bedrock. Start a new cloud session with `claude --cloud "task"`. The cloud VM clones the current directory’s GitHub remote at the current branch, so push local commits first. Pull a cloud session back with `claude --teleport`.
- GitHub for cloud sessions: authorize the Claude GitHub App during web onboarding, or run `/web-setup` in the terminal to send the local `gh` CLI token to the Claude account (Teams/Enterprise may hide `/web-setup` until an Owner enables Quick web setup).

**Checked:** 2026-10-03

**Updated instructions:**

- Install and first login: https://code.claude.com/docs/en/quickstart
- Auth commands: https://code.claude.com/docs/en/cli
- Cloud sessions: https://code.claude.com/docs/en/claude-code-on-the-web

## Codex CLI and Codex cloud

Local coding agent from OpenAI. Binary `codex`. Codex cloud is separate: it requires a ChatGPT sign-in and a published cloud environment. An API key is not enough for Codex cloud.

**Install** (from the Codex CLI page):

macOS/Linux:

```bash
curl -fsSL https://chatgpt.com/codex/install.sh | sh
```

The same page also documents npm (`npm install -g @openai/codex`) and Homebrew (`brew install --cask codex`). The GitHub README documents a Windows installer:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://chatgpt.com/codex/install.ps1 | iex"
```

**Login (local CLI):**

- Run `codex` in a project directory and choose **Sign in with ChatGPT**, or run `codex login` and finish the browser flow.
- API key (local workflows only; usage-based): `printenv OPENAI_API_KEY | codex login --with-api-key`
- Check: `codex login status`. Sign out: `codex logout`.
- Headless or remote, when the browser callback cannot reach the CLI: `codex login --device-auth` (device-code login must be enabled in ChatGPT security settings or workspace permissions). Docs also describe copying `~/.codex/auth.json` or forwarding `localhost:1455`. Treat that file like a password.

**Codex cloud (no separate CLI install):**

- Open ChatGPT on the web, mobile, or desktop app and sign in with a ChatGPT account. API-key sign-in does not enable Codex cloud.
- If you log in with email and password, the auth docs require MFA before Codex cloud. Social login and SSO have their own MFA rules on that page.
- On the web or desktop app: **Work in > Cloud**, then select or create an environment (connect GitHub if prompted, review setup, **Publish**). On mobile, open Codex.
- From the CLI, after the same ChatGPT login: `codex cloud` opens a picker; `codex cloud exec` submits a task; `codex cloud list` lists recent cloud chats. `codex apply` applies the latest cloud diff locally.

**Checked:** 2026-10-03

**Updated instructions:**

- CLI install: https://developers.openai.com/codex/cli
- Auth: https://developers.openai.com/codex/auth
- Cloud: https://developers.openai.com/codex/cloud
- CLI cloud subcommand: https://developers.openai.com/codex/cli/reference
- Windows installer also stated in https://github.com/openai/codex

## Cursor CLI

Local terminal agent. Official binary name is `agent`, not `cursor`.

**Install:**

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

**Login:**

- Browser (recommended): `agent login`. Check: `agent status` (`whoami` is the same command). Sign out: `agent logout`.
- If the browser does not open: `NO_OPEN_BROWSER=1 agent login` and open the printed URL.
- API key: create one in Cursor Dashboard → API Keys, then `export CURSOR_API_KEY=...` or `agent --api-key ...`.

**Checked:** 2026-10-03

**Updated instructions:**

- Install: https://cursor.com/docs/cli/installation
- Login: https://cursor.com/docs/cli/reference/authentication

## Antigravity CLI (AGY)

Google’s terminal agent. Binary `agy` (installed to `~/.local/bin/agy` on macOS/Linux).

**Install:**

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

**Login:**

- Run `agy`. If the OS keyring already has a token, sign-in is silent. Otherwise the CLI opens a browser; sign in with the approved Google account.
- Over SSH the CLI prints an authorization URL. Open it locally, then paste the code the browser shows back into the SSH session.
- Sign out inside the CLI with `/logout` (clears keyring profiles).
- Optional, instead of an account session: set `"modelProvider": "gemini"` in `~/.gemini/antigravity-cli/settings.json` and `export GEMINI_API_KEY=...`. A key alone, without `modelProvider`, does nothing. Create the key in Google AI Studio.

**Checked:** 2026-10-03

**Updated instructions:** https://antigravity.google/docs/cli/install/

## Kiro CLI

Terminal agent. Binary `kiro-cli`. The plugin peer is this TTY CLI. Kiro also has IDE, web, and mobile surfaces that share the same identity providers; those are not a second install command in the CLI docs.

**Install** (from the CLI docs index):

```bash
curl -fsSL https://cli.kiro.dev/install | bash
```

Start: `cd my-project` then `kiro-cli`.

**Login:**

- Providers documented for the CLI: GitHub, Google, AWS Builder ID, AWS IAM Identity Center (Start URL and Region from your admin), or an external identity provider (“Your organization” plus work email). Sign-in finishes in the browser.
- On a remote machine (SSH, SSM, containers): `kiro-cli login`, pick the provider, then open the printed URL and enter the one-time code. External IdP login is not supported on that device flow.
- Check which method is active: `kiro-cli whoami`. Re-auth after a failure: `kiro-cli login`.
- CI/headless (paid plans; an admin may have to enable it): create a key at [app.kiro.dev](https://app.kiro.dev) under API Keys, then `export KIRO_API_KEY=...` and `kiro-cli chat --no-interactive "..."`. Browser session from `kiro-cli login` takes precedence over `KIRO_API_KEY`.

**Checked:** 2026-10-03

**Updated instructions:**

- Install and launch: https://kiro.dev/docs/cli/ (page itself says “Page updated: August 4, 2026”; re-check that page if the command fails)
- Auth and remote/device flow: https://kiro.dev/docs/getting-started/authentication/
- First-run notes: https://kiro.dev/docs/cli/setup/

## Grok Build (xAI CLI)

Coding agent from xAI. Binary `grok`.

**Install** (from the Grok Build overview):

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

**Login:**

- On first launch, Grok opens a browser. Explicit sign-in: `grok login`. Sign out: `grok logout`.
- Headless or remote: `grok login --device-auth` (device-code auth).
- Non-browser environments can skip the account session with `export XAI_API_KEY="xai-..."` and then `grok`.

**Checked:** 2026-10-03

**Updated instructions:**

- Install and first-run auth: https://docs.x.ai/build/overview
- Subcommands including `grok login`: https://docs.x.ai/build/cli/reference

## Local git worktrees

Not a vendor coding CLI. No vendor account and no vendor login.

**Install:** None beyond Git, which you already use for the repo.

**Login:** Use whatever already authenticates you to `origin` (SSH key, `gh`, credential helper). This plugin does not add a second login. Preflight still has to confirm that helper can push the planned branch.

**Checked:** 2026-10-03

**Updated instructions:** https://git-scm.com/docs/git-worktree

## Herdr

Terminal multiplexer for running coding agents in real panes. It is the launcher, not a coding model. Each agent still uses that agent’s own install and login from the sections above.

**Install:**

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

**Login:** No Herdr account and no `herdr login` command are documented. Saved SSH machine profiles do not store passwords or keys. Remote machines use your existing OpenSSH auth (`ssh workbox` must already work). Add one with `herdr machine add workbox` in an interactive terminal. If a saved machine needs a key passphrase, `ssh-add` before Herdr’s background connections. Git or SSH signing inside remote panes needs `ForwardAgent yes` in your SSH config; Herdr does not turn that on for you.

**How it launches CLIs:**

- Quick start: open `herdr`, then run the agent binary in a pane (`claude`, `codex`, or another supported agent). Herdr detects it.
- Automation: `herdr agent start` needs an existing shell pane at a prompt. It does not create the pane. Example from the agent-automation docs: `herdr agent start reviewer --kind codex --pane "$review_pane" -- -m gpt-5.4`. Arguments after `--` go to that agent’s executable. Documented `--kind` values include `claude`, `codex`, `cursor`, `agy`, `kiro`, and `grok`.
- Supported-agent table (screen detection / integrations) uses integration ids such as `claude`, `codex`, `cursor`, `grok`, `antigravity-cli`. Kiro CLI is listed as recognized without a Herdr integration install. Other agents still run as plain terminals.

**Fleet note (not Herdr’s installer):** Some Grok Bot fleets only start cloud CLIs inside Herdr panes, on a git worktree, and require the agent’s own login to already be done in that environment. That is local policy. Follow the vendor section above for install and login, then Herdr’s own docs for pane and `agent start` syntax. Do not copy org repo names or tokens into this file.

**Checked:** 2026-10-03

**Updated instructions:**

- Install: https://herdr.dev/docs/install/
- First session: https://herdr.dev/docs/quick-start/
- SSH machines: https://herdr.dev/docs/connecting-machines/
- Which agents Herdr recognizes: https://herdr.dev/docs/agents/
- `herdr agent start`: https://herdr.dev/docs/agent-automation/

## Other coding CLIs and agents

Use this when the tool is not one of the named peers. Do not invent its install or login from a similar vendor.

1. Open the vendor’s current install page (their docs or their GitHub README). Copy the install command from that page only.
2. Install it yourself. This plugin does not run the installer.
3. Confirm the binary with the command their docs use (`which <binary>`, `<binary> --version`, or whatever they document).
4. Log in with the command their docs name (`login`, `auth login`, a browser on first launch, or an env var). Confirm with their documented status or whoami command.
5. Write down, next to your coding-delegation prefs or in a local note:
   - official docs URL
   - the date you checked it (YYYY-MM-DD)
   - binary name
   - the login command you actually used
6. In `coding-delegation.prefs.yaml`, set the surface up as a peer: add the name to `licenses.other_tty_cloud_clis` and, if you want it ranked, to `preferences.order`. Re-run `setup-coding-delegation` instead of editing those fields by guesswork.
7. If Herdr should track it, check https://herdr.dev/docs/agents/ for whether that agent is already recognized. If it is not, it can still run in a pane as a normal terminal.

**Checked:** 2026-10-03

**Updated instructions:** start from the vendor’s own docs index. Herdr’s agent list: https://herdr.dev/docs/agents/
