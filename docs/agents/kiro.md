# Kiro CLI

## What it is

Terminal agent. Binary `kiro-cli`. The plugin peer is this TTY CLI. Kiro also has IDE, web, and mobile surfaces that share the same identity providers; those are not a second install command in the CLI docs. Kiro CLI is an interactive coding agent with slash commands and portable Agent Skills.

## Install

From the CLI docs index:

```bash
curl -fsSL https://cli.kiro.dev/install | bash
```

Start: `cd my-project` then `kiro-cli`.

## Login

- Providers documented for the CLI: GitHub, Google, AWS Builder ID, AWS IAM Identity Center (Start URL and Region from your admin), or an external identity provider (“Your organization” plus work email). Sign-in finishes in the browser.
- On a remote machine (SSH, SSM, containers): `kiro-cli login`, pick the provider, then open the printed URL and enter the one-time code. External IdP login is not supported on that device flow.
- Check which method is active: `kiro-cli whoami`. Re-auth after a failure: `kiro-cli login`.
- CI/headless (paid plans; an admin may have to enable it): create a key at [app.kiro.dev](https://app.kiro.dev) under API Keys, then `export KIRO_API_KEY=...` and `kiro-cli chat --no-interactive "..."`. Browser session from `kiro-cli login` takes precedence over `KIRO_API_KEY`.

## Auth status check

- Command: `kiro-cli whoami`. Logged in: exit 0 and `Logged in with <method>`. Verified live on 2026-10-09 (Linux). The output contains the account email; never paste it raw.
- `kiro-cli whoami --format json` hung past 20s on 2026-10-09; use the plain form.
- Logged-out output was not observed live; the script treats anything other than a logged-in result as unknown (needs attention).
- Usage limits: unknown; no usage command in `kiro-cli --help-all` (checked 2026-10-09).

## Commands and skills

| Command or skill | Use it for |
|---|---|
| `/help` | Get Kiro CLI help or ask the Help Agent a question. |
| `/context show` | Show context rules and matched files. |
| `/agent swap <name>` | Switch to another agent configuration. |
| `/spawn <task>` | Start a parallel agent session. |
| `/plan` | Switch to the Plan agent. |
| `/goal` | Run iterative work toward an objective and verify completion. |
| `/pr-review` | Invoke a skill named `pr-review` when that skill is installed. |

## Ongoing session and answering questions

- **How it asks:** A tool that needs permission shows a notification bar with Yes, Trust, and No. The busy timer also pauses for an answer to a question. The CLI page does not name a separate question command.
- **How to answer:** Choose Yes, Trust, or No. Tab drills into the approval so you can give feedback instead of yes or no. How to answer a question that is not a tool approval: unknown, except a paused workflow step, where `s` in the workflow monitor sends a text reply.
- **Blocks:** Yes. The busy timer pauses while the turn waits for an approval or an answer, then resumes after you respond.

## Observed behavior

Observed 2026-10-03 (live sessions, Linux):

- `kiro-cli whoami` was logged in. `kiro-cli chat "<prompt>"` accepted the task and the answer `alpha.txt`, then blocked on “write requires approval” with choices Yes (single permission), Trust (always allow in this session), No. That is a permission prompt, not login. File was not written.

## Quirks

`whoami` or login-status passing does not mean the next session starts. Kiro adds a write-approval prompt.

## Checked

2026-10-03

## Updated instructions

- Install and launch: https://kiro.dev/docs/cli/ (page itself says “Page updated: August 4, 2026”; re-check that page if the command fails)
- Auth and remote/device flow: https://kiro.dev/docs/getting-started/authentication/
- First-run notes: https://kiro.dev/docs/cli/setup/
- Commands: https://kiro.dev/docs/reference/slash-commands/
- Session questions: https://kiro.dev/docs/cli/terminal-ui/
