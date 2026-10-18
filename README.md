# Coding Delegation

Marketplace-ready Cursor plugin that teaches **any** orchestrator or domain bot
how to hand coding work to licensed coding surfaces **without replacing a builder
agent seat**.

Surfaces are **agent-agnostic peers**. On first use (or when prefs are missing),
the plugin asks which licenses exist and when to prefer each surface. Model
choice uses an opt-in tier catalog: frontier stays off unless you allow it.
Tool order comes only from your answers.

Agent instructions follow [docs/agents/_template.md](./docs/agents/_template.md).
One file per agent:

- [Cursor Cloud Agents](./docs/agents/cursor-cloud-agents.md)
- [Cursor CLI](./docs/agents/cursor-cli.md)
- [Claude Code](./docs/agents/claude-code.md)
- [Codex](./docs/agents/codex.md)
- [AGY](./docs/agents/agy.md)
- [Kiro](./docs/agents/kiro.md)
- [Grok Build](./docs/agents/grok-build.md)
- [Herdr](./docs/agents/herdr.md)
- [Local git worktrees](./docs/agents/worktrees.md)
- [Other coding CLIs](./docs/agents/other.md)

Those files are the source of truth. Do not invent installer, login, or agent commands.

## What this is

Portable skills for:

- Collecting licenses and user-defined routing prefs (`setup-coding-delegation`)
- Choosing a coding surface from those prefs, then a model from the opt-in tier catalog
- Preflighting remotes and auth before launch
- Writing a complete build handoff brief as a file

## What this is not

- **Not** a replacement for a standing builder agent
- **Not** an MCP server, rule pack, or agent personality
- **Not** tied to a single org: no personal or org-only names in the skills
- **Not** a hard preference for Cursor Cloud Agents (or any other vendor)

Domain bots own product intent and MCP day-to-day usage. The builder seat owns
code and merges when CI is green.

## Preferences

Prefs are deep-merged. For each key, the first layer that sets it wins:

1. Per-job flag (a one-run overlay)
2. `coding-delegation.prefs.yaml` in the repository root
3. `~/.config/coding-delegation/prefs.yaml`
4. Plugin defaults in `data/prefs-defaults.yaml`

Maps merge. Lists and scalars are replaced when a higher layer sets that key.
A key you leave out falls through to the next layer.

**Migration from "first file wins".** Older versions used the first of those
files that existed and ignored the other. A repo file hid the user file
completely. Now a key absent from the repo file keeps the user-file value.
If you depended on the repo file replacing every user key, copy those keys
into the repo file.

`models:` and `routing:` are part of the same file. Defaults enable no tool,
leave `preferences.order` empty, and set frontier to `never`.

Shape (also documented in `setup-coding-delegation`):

```yaml
licenses:
  cursor_cloud_agents: false
  claude_code_cloud: false
  codex_cloud: false
  cursor_cli: false
  agy_cloud: false
  kiro_cloud: false
  grok_build: false
  other_tty_cloud_clis: []
  local_worktrees: true
preferences:
  order: []  # user-defined only
  when: {}
  defaults:
    never_main_checkout: true
    require_tty_for_cloud_clis: true
    preflight_before_launch: true
setup_complete: false
models:
  policy: newest   # newest | pin
  pins: {}         # family: exact model id, used when policy is pin
routing:
  frontier: never            # never | flagged | auto
  extra_spend: deny          # deny | per_job | capped
  extra_spend_cap: 0
  reviewer: none             # none | same | other_vendor
  on_limit_or_stall: ask_first  # ask_first | handoff
  stall_timeout_min: 30      # 15 | 30 | 60
  first_tool: null
  cost_order: []
  setup_complete: false
  tools:
    claude:
      enabled: false
      plan: included   # included | extra
    codex:
      enabled: false
      plan: included
    cursor:
      enabled: false
      plan: included
```

## Model routing

Before each coding job, `scripts/route-model.py` chooses a tool and a model
from the tools you enabled, the plan you declared, live usage, and the job
size. It does not rank vendors. With no enabled tool, or a tie you did not
break, it stops and asks.

The tier catalog is `data/tiers.yaml` (families, not versions):

| Tier | Families | When |
|------|----------|------|
| frontier | fable / astra | Only if you set frontier to `auto`, or to `flagged` and you flag that job |
| strong | opus / sol | Hard jobs |
| standard | sonnet / terra | Normal jobs |
| fast | haiku / luna | Small jobs |

Claude Code aliases are already the newest model in each family. Codex
resolves `gpt-<version>-<family>` from `codex debug models`, visible models
only, highest version, and warns when a family lags the newest generation.
Cursor's adapter default is `grok-4.7`. A pin replaces that resolution for
one family.

Pre-job checks, in order:

1. **Usage.** Claude: `claude -p "/usage" --output-format json </dev/null` (unofficial in `-p`; the `result` text is what gets parsed). Codex: app-server JSON-RPC `account/rateLimits/read` only. Cursor: usage stays unknown, because there is no public per-user usage API. Skip a tool at 90% or more of any window, or when it is blocked or spend-capped. Cache a reading for about five minutes, and re-read before a hard job. Unknown usage sorts last.
2. **Context.** `need = bytes_in_scope/3 + 40000 + 2 * roundtrip_tokens + output_reserve`, with the reserve between 16k and 32k tokens. Skip a model when `need` is greater than `0.6` times its usable window. Codex usable window is `context_window * effective_context_window_percent / 100` from the model list. An unknown window does not skip.
3. **Choose.** Hard jobs go to the eligible tool with the most usage left. Small jobs go to the cheapest eligible tool (your `cost_order`, and a plan that bills extra loses unless you allowed extra spend). Normal jobs follow your order. Frontier is off unless you allowed it.
4. **Log.** Every run appends tool, resolved model, and the usage snapshot to `~/.config/coding-delegation/routing-log.jsonl`.

Nothing that bills extra is routed unless `routing.extra_spend` is `per_job` or `capped` and this job is allowed. The default is `deny`.

Mid-job, a limit error, another error, or a stall past your timeout (15, 30, or 60 minutes) moves to the next eligible tool at the same tier. The default is to ask first. `handoff` switches and still tells you. If none remain, it stops and asks. Claude's `--fallback-model` is not used; it does not trip on usage limits.

Codex is always started with stdin from `/dev/null` (`codex exec` hangs otherwise, printing `Reading additional input from stdin...`). Rate limits use `codex app-server --listen unix://…` so that stdin stays `/dev/null`. This plugin never calls `account/rateLimitResetCredit/consume`. It never calls Cursor's dashboard for usage.

Setup writes the same prefs file from either host:

- Claude Code asks the fixed questions at install through `userConfig` in `.claude-plugin/plugin.json` (one boolean per tool, string options for the rest).
- Cursor and Codex run a SessionStart hook (`hooks/hooks-cursor.json` and `hooks/hooks.json`) that points at the setup skill when `routing.setup_complete` is not true. On Codex the skill calls `request_user_input` with at most three questions per call.

**Open item (not blocking).** It is untested whether `claude --cloud` honors `--model` or needs `ANTHROPIC_MODEL` on the cloud environment. Recheck after 2026-10-20.

## Install (Cursor IDE)

From a local checkout of this plugin:

```bash
# Symlink or copy into Cursor’s local plugins path (IDE)
mkdir -p ~/.cursor/plugins
ln -sfn /absolute/path/to/coding-delegation ~/.cursor/plugins/coding-delegation
```

Then enable **Coding Delegation** in Cursor Settings → Plugins (or reload the
window).

Or install from the Cursor Marketplace once published (search for
**Coding Delegation** / `coding-delegation`).

## Install (Grok Bot / dashboard)

Grok Bot loads marketplace plugins from the **dashboard / marketplace**, not
from `~/.cursor/plugins/local`.

Once this plugin is published to the marketplace, enable it in the Grok Bot
dashboard plugin list. Do **not** expect a local filesystem symlink to load for
Grok Bot.

Suggested (after publish — do not publish from this repo unless intentional):

```text
Dashboard → Marketplace → Coding Delegation → Enable
```

## Usage

1. On first use (or when prefs are missing), invoke **setup-coding-delegation**.
   Confirm licenses, your tool order, and the model-routing answers.
   Persist prefs; set `setup_complete: true` and `routing.setup_complete: true`.
2. When routing repo/PR work, invoke **delegate-coding** (it re-runs setup if
   needed, then the model-routing pre-job checks).
3. Before launch, run **coding-preflight** (abort if remotes/auth fail). It starts with `bash scripts/auth-check.sh`, which prints one line per surface (ok, logged out, usage exhausted, not installed, unknown) and exits non-zero when any needs attention, so a scheduled routine can alert. A logged-out or out-of-usage surface is reported to the user before any fallback.
4. Write the brief with **build-handoff-brief**; pass the file path to the
   builder or chosen surface.
5. For builder questions and replies, use **agent-comms**; message with the brief
   path and one-line ask because saving the file alone does not wake the builder.
6. Route per prefs only — never the main checkout; TTY for cloud CLIs when required. Use the matching file under `docs/agents/`.
7. Monitor only on idle, blocker, or PR ready. Builder merges when CI is green.

## Skills

| Skill | When to use |
|-------|-------------|
| `setup-coding-delegation` | First install, missing prefs, or “configure coding delegation” |
| `delegate-coding` | Launch or route coding from an orchestrator / domain bot |
| `coding-preflight` | Checklist before any prefs-selected surface launch |
| `build-handoff-brief` | Required brief fields + template for handoff |
| `agent-comms` | Message a builder or another agent about a build, question, or reply |
| `vendor-tools` | Use documented vendor commands and skills before launch |

## Layout

```
coding-delegation/
├── .claude-plugin/plugin.json
├── .codex-plugin/plugin.json
├── .cursor-plugin/plugin.json
├── .github/workflows/test.yml
├── plugin.json
├── README.md
├── docs/
│   ├── agents/
│   │   ├── _template.md
│   │   └── <agent>.md
│   ├── cli-setup.md
│   └── vendor-tools.md
├── LICENSE
├── PROOF.md
├── assets/
│   └── logo.png
├── data/
│   ├── tiers.yaml
│   └── prefs-defaults.yaml
├── hooks/
│   ├── hooks.json
│   ├── hooks-cursor.json
│   └── session-start
├── scripts/
│   ├── auth-check.sh
│   ├── route-model.py
│   └── model_routing/
├── tests/
│   └── fixtures/
└── skills/
    ├── setup-coding-delegation/SKILL.md
    ├── delegate-coding/SKILL.md
    ├── coding-preflight/SKILL.md
    ├── build-handoff-brief/SKILL.md
    ├── agent-comms/SKILL.md
    └── vendor-tools/SKILL.md
```

## License

MIT — see [LICENSE](./LICENSE).
