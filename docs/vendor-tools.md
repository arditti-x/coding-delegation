# Vendor tools: documented commands and skills

Use the matching vendor section before launching a named peer. These are commands
and skills found in the vendors' current official documentation, checked on
**2026-10-03**. If a command is marked unknown, do not guess it; use the linked
official index for the current list. Each named peer also has a Questions note
for how that session asks and how to answer in the same session.

## Cursor Cloud Agents

Cursor Cloud Agents run coding agents in Cursor's hosted environment.

- **Commands / skills:** **Unknown** — the current official Cloud Agents launch
  documentation does not publish a slash-command or skill-invocation list for
  this surface.
- **Updated official list:** [Launch a Cloud Agent](https://docs.cursor.com/en/background-agent/api/launch-an-agent)
- **Checked:** 2026-10-03

### Questions

- **How it asks:** Unknown. The Cloud Agents pages do not describe an in-run question prompt.
- **How to answer:** Stay on the same agent. `POST /v1/agents/{id}/runs` with `prompt.text` continues that agent's conversation and workspace. If another run is `CREATING` or `RUNNING`, the API returns `409 agent_busy`; wait for that run to end or cancel it. Follow-ups are accepted when the agent is `IDLE`. A follow-up can also be sent from [cursor.com/agents](https://cursor.com/agents). Team follow-ups require the team setting. Commenting `@cursor` on a GitHub PR or issue, or on a Bitbucket PR, starts an agent; those pages do not say the comment answers a question inside an existing run.
- **Blocks:** Unknown.
- **Docs:** [Cloud Agents API](https://cursor.com/docs/cloud-agent/api/endpoints), [Cloud Agents](https://cursor.com/docs/cloud-agent)
- **Checked:** 2026-10-03

## Cursor CLI

Cursor CLI is Cursor's terminal coding agent for understanding, planning,
building, debugging, and reviewing code.

- **Commands / skills:** **Unknown** — the current official CLI pages do not
  publish a distinctive slash-command or named skill-invocation list.
- **Updated official list:** [Cursor CLI overview](https://docs.cursor.com/cli/overview)
- **Checked:** 2026-10-03

### Questions

- **How it asks:** Before a terminal command, the CLI asks you to approve or reject it. Plan mode asks clarifying questions; the page does not say how those are shown.
- **How to answer:** `y` approves that terminal command. `n` rejects it. How to answer a Plan-mode clarifying question: unknown.
- **Blocks:** That terminal command does not run until you approve or reject it. Whether a Plan-mode question blocks the turn: unknown.
- **Docs:** [Using Agent in CLI](https://cursor.com/docs/cli/using)
- **Checked:** 2026-10-03

## Claude Code

Claude Code is Anthropic's terminal coding agent with built-in commands and
bundled skills.

| Command or skill | Use it for |
|---|---|
| `/loop` | Re-run a prompt on a time interval. |
| `/goal` | Keep working toward a stated completion condition and stop when it is met, impossible, or needs an error fixed. |
| `/verify` | Build and run the app to confirm a change against the running app. |
| `/code-review` | Run Claude's bundled code-review skill. |

- **Updated official list:** [Claude Code commands](https://code.claude.com/docs/en/commands)
- **Checked:** 2026-10-03

### Questions

- **How it asks:** `AskUserQuestion` opens a multiple-choice dialog in the same session. Separate permission prompts, including plan approval, also appear in that session.
- **How to answer:** Pick an option, or type your own text through the Other row or the notes field. In a confirmation dialog, Enter confirms and Escape declines. A dialog that shows `y` and `n` reads those letters itself.
- **Blocks:** Yes. `AskUserQuestion` stays open until you answer it, unless `askUserQuestionTimeout` is set. Permission prompts, including plan approval, never auto-resolve on idle.
- **Docs:** [Tools reference](https://code.claude.com/docs/en/tools), [Keyboard shortcuts](https://code.claude.com/docs/en/keybindings)
- **Checked:** 2026-10-03

## Codex

Codex is OpenAI's coding agent available through the CLI, IDE extension, and
app.

| Command or skill | Use it for |
|---|---|
| `/skills` | Browse and apply local skills. |
| `$skill-name` | Explicitly invoke a named skill. |
| `codex exec` | Run a non-interactive prompt for scripts, CI, or automation. |
| `/init` | Scaffold an `AGENTS.md` starter file. |
| `/review` | Review code changes. |

- **Updated official list:** [Codex CLI slash commands](https://developers.openai.com/codex/cli/slash-commands)
- **Checked:** 2026-10-03

### Questions

- **How it asks:** With an interactive approval policy, Codex stops and asks before an action that policy requires, such as leaving the sandbox, using the network, a side-effecting app or MCP tool, or a `request_permissions` prompt.
- **How to answer:** Unknown. The official pages do not name the key that accepts or declines that prompt. `/permissions` changes the approval preset. `/approve` retries one recent auto-review denial.
- **Blocks:** Yes while approvals are interactive (`on-request`, or a granular policy that still surfaces that prompt). `--ask-for-approval never` does not ask.
- **Docs:** [Agent approvals and security](https://developers.openai.com/codex/agent-approvals-security), [Slash commands](https://developers.openai.com/codex/cli/slash-commands)
- **Checked:** 2026-10-03

## AGY (Antigravity CLI)

AGY is the Antigravity terminal agent with slash commands and Agent Skills.

| Command or skill | Use it for |
|---|---|
| `/skills` | Browse loaded local and global Agent Skills. |
| `/plugin` | Open the Plugins Manager or run plugin actions such as `list`, `install`, `enable`, and `disable`. |
| `agy plugin list` | List active plugins and their bundled skills. |
| `agy plugin install <path>` | Install a local plugin containing skills. |

Skills become slash commands in the interactive CLI; a skill named
`deploy-staging` is invoked as `/deploy-staging`.

- **Updated official list:** [Antigravity CLI reference](https://antigravity.google/docs/cli/reference/)
- **Checked:** 2026-10-03

### Questions

- **How it asks:** In Ask mode, an interactive prompt card appears in the TUI and the agent pauses for approval.
- **How to answer:** `y` authorizes the proposed tool, command, or artifact. `n` rejects it. `Ctrl+K` approves the pending subagent action in the status alert. `Alt+J` moves to the next subagent waiting for confirmation.
- **Blocks:** Yes in the interactive TUI. Headless mode has no prompt: an Ask action is soft-denied, the run continues, and it exits 0.
- **Docs:** [CLI reference](https://antigravity.google/docs/cli/reference/), [Permissions](https://antigravity.google/docs/cli/permissions/), [Headless mode](https://antigravity.google/docs/cli/headless/)
- **Checked:** 2026-10-03

## Kiro

Kiro CLI is an interactive coding agent with slash commands and portable Agent
Skills.

| Command or skill | Use it for |
|---|---|
| `/help` | Get Kiro CLI help or ask the Help Agent a question. |
| `/context show` | Show context rules and matched files. |
| `/agent swap <name>` | Switch to another agent configuration. |
| `/spawn <task>` | Start a parallel agent session. |
| `/plan` | Switch to the Plan agent. |
| `/goal` | Run iterative work toward an objective and verify completion. |
| `/pr-review` | Invoke a skill named `pr-review` when that skill is installed. |

- **Updated official list:** [Kiro slash commands](https://kiro.dev/docs/reference/slash-commands/)
- **Checked:** 2026-10-03

### Questions

- **How it asks:** A tool that needs permission shows a notification bar with Yes, Trust, and No. The busy timer also pauses for an answer to a question. The CLI page does not name a separate question command.
- **How to answer:** Choose Yes, Trust, or No. Tab drills into the approval so you can give feedback instead of yes or no. How to answer a question that is not a tool approval: unknown, except a paused workflow step, where `s` in the workflow monitor sends a text reply.
- **Blocks:** Yes. The busy timer pauses while the turn waits for an approval or an answer, then resumes after you respond.
- **Docs:** [Terminal UI](https://kiro.dev/docs/cli/terminal-ui/)
- **Checked:** 2026-10-03

## Grok Build / xAI CLI

Grok Build is the xAI terminal agent with TUI commands, workflows, plugins, and
user-invocable skills.

| Command or skill | Use it for |
|---|---|
| `/plan [description]` | Enter plan mode. |
| `/loop [interval] <prompt>` | Run a prompt on a recurring interval. |
| `/skills` | Open the Skills tab in the extensions modal. |
| `/workflow <name>` | Launch or control a saved workflow. |
| `/deep-research <prompt>` | Start the built-in research workflow. |
| `/local:commit` | Invoke a user skill with a qualified name when skill names collide. |
| `grok inspect` | Show discovered skills, plugins, hooks, and MCP servers. |

- **Updated official list:** [Grok Build modes and commands](https://docs.x.ai/build/modes-and-commands)
- **Checked:** 2026-10-03

### Questions

- **How it asks:** Ask mode, the default, prompts before a tool call that is not already allowed.
- **How to answer:** On the Agent Dashboard (`Ctrl+\`, `/dashboard`, or `grok dashboard`), permission prompts and questions are answered inline with the number keys. Typing in the peek sends immediately if the agent is idle and queues the text if it is busy. Enter attaches to that session. The keyboard-shortcuts page does not name the keys for a prompt while you are attached to the session.
- **Blocks:** The tool call is not approved until the Ask-mode prompt is answered. Those sessions are grouped under Needs input. The permissions page does not say the attached session exits.
- **Docs:** [Permissions](https://docs.x.ai/build/features/permissions), [Agent Dashboard](https://docs.x.ai/build/features/dashboard)
- **Checked:** 2026-10-03

## Herdr

Herdr is the terminal workspace and agent-orchestration surface. Its reusable
agent skill teaches an agent to control Herdr from inside a Herdr-managed pane.

| Command or skill | Use it for |
|---|---|
| `herdr --skill` | Print the release-matched Herdr agent skill. |
| `herdr pane run <pane_id> "<command>"` | Run and submit a command in a pane. |
| `herdr pane wait-output <pane_id> --regex "<pattern>"` | Wait for matching pane output. |
| `herdr agent prompt <target> "<text>" --wait` | Send a prompt to an agent and wait for a settled state. |
| `herdr agent wait --until <status>` | Wait for an agent status. |
| `herdr --remote <machine>` | Attach through SSH to a named remote session. |
| `npx skills add herdrdev/herdr --skill herdr -g` | Install Herdr's reusable agent skill globally. |

- **Updated official list:** [Herdr CLI reference](https://herdr.dev/docs/cli-reference/)
- **Agent skill:** [Herdr agent skill](https://herdr.dev/docs/agent-skill/)
- **Checked:** 2026-10-03

### Questions

- **How it asks:** Herdr sets the agent to `blocked` when it recognizes an approval or question UI in the pane.
- **How to answer:** Do not use `herdr agent prompt` while the agent is `blocked`. That returns `agent_blocked` and sends nothing. Read the pane with `herdr agent read`, then answer with `herdr agent send-keys` (`enter`, `up`, `esc`, or `ctrl+c`). Which key the dialog wants is the inner agent's UI, not a Herdr command.
- **Blocks:** Yes. The agent stays `blocked` until that dialog is handled. `herdr agent wait --until blocked` waits for that state.
- **Docs:** [Agent automation](https://herdr.dev/docs/agent-automation/)
- **Checked:** 2026-10-03

## Another coding CLI or agent

When using a coding CLI or agent not named above, find that vendor's current
official skills and commands index, record its URL and the date checked, and use
only commands documented there. Do not invent commands, slash commands, skills,
or flags.

### Questions

- **How it asks:** Unknown until that vendor's current official page says so.
- **How to answer:** Unknown. Record the page URL and the date checked. Do not invent a command or a key.
- **Blocks:** Unknown until that page says whether the session waits.
- **Checked:** 2026-10-03
