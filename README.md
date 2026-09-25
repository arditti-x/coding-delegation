# Coding Delegation

Marketplace-ready Cursor plugin that teaches **any** orchestrator or domain bot
how to hand coding work to licensed coding surfaces — Cursor Cloud Agents,
Claude Code cloud, Codex cloud, Cursor CLI, Grok Build, other TTY cloud CLIs, or git
worktrees — **without replacing a builder agent seat**.

Surfaces are **agent-agnostic peers**. On first use (or when prefs are missing),
the plugin asks which licenses exist and when to prefer each surface. There is
no built-in ranking.

## What this is

Portable skills for:

- Collecting licenses and user-defined routing prefs (`setup-coding-delegation`)
- Choosing a coding surface from those prefs only (peers; no default winner)
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

Suggested paths (first existing wins for read):

- `coding-delegation.prefs.yaml` in the repository root
- `~/.config/coding-delegation/prefs.yaml`

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
```

## Grok Build peer

Grok Build is a TTY cloud CLI peer selected only through user prefs. If it is not installed, the documented install hint is:

```bash
curl -fsSL https://x.ai/cli/install.sh | bash
```

Do not infer a binary name or flags from this hint; use the Grok Build / xAI CLI documentation.

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
   Confirm licenses, rank preferred order, and optionally note when to use each
   surface. Persist prefs; set `setup_complete: true`.
2. When routing repo/PR work, invoke **delegate-coding** (it re-runs setup if
   needed).
3. Before launch, run **coding-preflight** (abort if remotes/auth fail).
4. Write the brief with **build-handoff-brief**; pass the file path to the
   builder or chosen surface.
5. Route per prefs only — never the main checkout; TTY for cloud CLIs, including Grok Build, when
   required.
6. Monitor only on idle, blocker, or PR ready. Builder merges when CI is green.

## Skills

| Skill | When to use |
|-------|-------------|
| `setup-coding-delegation` | First install, missing prefs, or “configure coding delegation” |
| `delegate-coding` | Launch or route coding from an orchestrator / domain bot |
| `coding-preflight` | Checklist before any prefs-selected surface launch |
| `build-handoff-brief` | Required brief fields + template for handoff |

## Layout

```
coding-delegation/
├── .cursor-plugin/plugin.json
├── plugin.json
├── README.md
├── LICENSE
├── PROOF.md
├── assets/
│   └── logo.png
└── skills/
    ├── setup-coding-delegation/SKILL.md
    ├── delegate-coding/SKILL.md
    ├── coding-preflight/SKILL.md
    └── build-handoff-brief/SKILL.md
```

## License

MIT — see [LICENSE](./LICENSE).
