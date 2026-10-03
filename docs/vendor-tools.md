# Vendor tools: documented commands and skills

Use the matching vendor section before launching a named peer. These are commands
and skills found in the vendors' current official documentation, checked on
**2026-10-03**. If a command is marked unknown, do not guess it; use the linked
official index for the current list.

## Cursor Cloud Agents

Cursor Cloud Agents run coding agents in Cursor's hosted environment.

- **Commands / skills:** **Unknown** — the current official Cloud Agents launch
  documentation does not publish a slash-command or skill-invocation list for
  this surface.
- **Updated official list:** [Launch a Cloud Agent](https://docs.cursor.com/en/background-agent/api/launch-an-agent)
- **Checked:** 2026-10-03

## Cursor CLI

Cursor CLI is Cursor's terminal coding agent for understanding, planning,
building, debugging, and reviewing code.

- **Commands / skills:** **Unknown** — the current official CLI pages do not
  publish a distinctive slash-command or named skill-invocation list.
- **Updated official list:** [Cursor CLI overview](https://docs.cursor.com/cli/overview)
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

## Another coding CLI or agent

When using a coding CLI or agent not named above, find that vendor's current
official skills and commands index, record its URL and the date checked, and use
only commands documented there. Do not invent commands, slash commands, skills,
or flags.
