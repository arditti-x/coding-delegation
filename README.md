# Coding Delegation

Marketplace-ready Cursor plugin that teaches **any** orchestrator or domain bot how to hand coding work to Cursor Cloud Agents, Herdr-style TTY cloud CLIs, or git worktrees — **without replacing a builder agent seat**.

## What this is

Portable skills for:

- Choosing the right coding surface (Cloud Agents → TTY cloud → worktrees)
- Preflighting remotes and auth before launch
- Writing a complete build handoff brief as a file

## What this is not

- **Not** a replacement for a standing builder agent
- **Not** an MCP server, rule pack, or agent personality
- **Not** fleet-specific: no personal or org-only names in the skills

Domain bots own product intent and MCP day-to-day usage. The builder seat owns code and merges when CI is green.

## Install (Cursor IDE)

From a local checkout of this plugin:

```bash
# Symlink or copy into Cursor’s local plugins path (IDE)
mkdir -p ~/.cursor/plugins
ln -sfn /absolute/path/to/coding-delegation ~/.cursor/plugins/coding-delegation
```

Then enable **Coding Delegation** in Cursor Settings → Plugins (or reload the window).

Or install from the Cursor Marketplace once published (search for **Coding Delegation** / `coding-delegation`).

## Install (Grok Bot / dashboard)

Grok Bot loads marketplace plugins from the **dashboard / marketplace**, not from `~/.cursor/plugins/local`.

Once this plugin is published to the marketplace, enable it in the Grok Bot dashboard plugin list. Do **not** expect a local filesystem symlink to load for Grok Bot.

Suggested (after publish — do not publish from this repo unless intentional):

```text
Dashboard → Marketplace → Coding Delegation → Enable
```

## Usage

1. When routing repo/PR work, invoke skill **delegate-coding**.
2. Before launch, run **coding-preflight** (abort if remotes/auth fail).
3. Write the brief with **build-handoff-brief**; pass the file path to the builder / Cloud Agent.
4. Prefer Cloud Agents; else Herdr-style TTY only; else git worktrees — never the main checkout.
5. Monitor only on idle, blocker, or PR ready. Builder merges when CI is green.

## Skills

| Skill | When to use |
|-------|-------------|
| `delegate-coding` | Launch or route coding from an orchestrator / domain bot |
| `coding-preflight` | Checklist before Cloud Agent / TTY / worktree launch |
| `build-handoff-brief` | Required brief fields + template for handoff |

## Layout

```
coding-delegation/
├── .cursor-plugin/plugin.json
├── plugin.json
├── README.md
├── LICENSE
├── PROOF.md
└── skills/
    ├── delegate-coding/SKILL.md
    ├── coding-preflight/SKILL.md
    └── build-handoff-brief/SKILL.md
```

## License

MIT — see [LICENSE](./LICENSE).
