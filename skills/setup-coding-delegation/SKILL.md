---
name: setup-coding-delegation
description: >-
  Use on first install, when coding-delegation prefs are missing or incomplete,
  or when the user says "configure coding delegation" or wants to change
  licenses or routing preferences. Collects which surfaces are licensed,
  how to prefer them, and the model-routing answers. Does not invent licenses
  or a tool order.
---

# Setup coding delegation

The source of truth for each peer is [docs/agents/_template.md](../../docs/agents/_template.md) and the matching [docs/agents/<name>.md](../../docs/agents/); do not invent installer, login, or agent commands.

Run this skill before any coding handoff when preferences are missing or the
user asks to reconfigure. Persist the result so later routing uses **only**
what the user declared. Do not invent licenses the user did not confirm.

## Prefs file

Agents should load preferences by deep-merging, highest precedence first:
per-job flag, then the repo file, then the user file, then plugin defaults in
`data/prefs-defaults.yaml`. This replaces "first file wins" (a repo file used
to hide the user file). A key left out of a higher file keeps the lower value.
For a first-time write, prefer the repo copy if the agent is in a git checkout,
otherwise the home config path:

- `coding-delegation.prefs.yaml` in the current repository root
- `~/.config/coding-delegation/prefs.yaml`

Documented data shape:

```yaml
# coding-delegation.prefs.yaml
licenses:
  cursor_cloud_agents: false
  claude_code_cloud: false
  codex_cloud: false
  cursor_cli: false
  agy_cloud: false          # Antigravity `agy` (Google AI Pro) via TTY
  kiro_cloud: false         # Kiro cloud via TTY
  grok_build: false         # Grok Build / xAI CLI via TTY
  other_tty_cloud_clis: []  # freeform names the user names
  local_worktrees: true     # usually available unless the user disables it
preferences:
  # Ordered preference is USER-DEFINED only — empty until setup finishes
  order: []  # e.g. [codex_cloud, agy_cloud, kiro_cloud, grok_build, local_worktrees]
  when:
    cursor_cloud_agents: ""
    claude_code_cloud: ""
    codex_cloud: ""
    cursor_cli: ""
    agy_cloud: ""
    kiro_cloud: ""
    grok_build: ""
    # one free-text entry per licensed surface
  defaults:
    never_main_checkout: true
    require_tty_for_cloud_clis: true
    preflight_before_launch: true
setup_complete: false
models:
  policy: newest
  pins: {}
routing:
  frontier: never
  extra_spend: deny
  extra_spend_cap: 0
  reviewer: none
  on_limit_or_stall: ask_first
  stall_timeout_min: 30
  first_tool: null
  cost_order: []
  setup_complete: false
  tools:
    claude:
      enabled: false
      plan: included
    codex:
      enabled: false
      plan: included
    cursor:
      enabled: false
      plan: included
```

Agents may also store the same fields in durable agent memory if a local file
cannot be written; the skill name for that store is still
`coding-delegation.prefs`. The file (or memory) is the source of truth.

## Questions to ask

Ask in this order. Use a multi-select style prompt for licenses, then ranking
and optional free text. Complete sentences; do not pre-check surfaces the user
did not claim.

### a) Which coding surfaces are licensed or available?

Present these as peers (no implied winner). Allow multi-select:

- Cursor Cloud Agents (`cursor_cloud_agents`)
- Claude Code cloud (`claude_code_cloud`)
- Codex cloud (`codex_cloud`)
- Cursor CLI (`cursor_cli`)
- Antigravity / AGY cloud (`agy_cloud`) — Google AI Pro via `agy` on a TTY
- Kiro cloud (`kiro_cloud`) — Kiro on a TTY
- Grok Build (`grok_build`) — Grok Build / xAI CLI on a TTY; install hint: `curl -fsSL https://x.ai/cli/install.sh | bash`
- Other TTY cloud CLIs (`other_tty_cloud_clis`) — if chosen, ask for freeform names
- Local git worktrees (`local_worktrees`) — default available unless the user turns it off

Only mark a license `true` when the user says they have it. Leave unknown
surfaces `false`. Do not assume any surface is licensed.

### b) Preferred order among the licensed surfaces

Ask the user to rank **only** the surfaces they licensed. The ordered list
becomes `preferences.order`. Do not invent a ranking. If they
skip ranking, leave `order` empty and ask again before the first
`delegate-coding` launch. Model choice still uses the opt-in tier catalog;
frontier stays off unless they allow it below.

### c) Optional when-to-use notes

For each licensed surface, offer an optional free-text `preferences.when.<key>`
(for example, “long PR work”, “interactive debugging”, “offline / air-gapped”).
Empty strings are fine.

Confirm `defaults` (or keep the documented defaults unless the user changes
them): never edit the main checkout; require a TTY for cloud CLIs; run
preflight before launch.

## Model routing questions

Ask these only with the choices below. Do not add a vendor ranking, a person's
name, an account id, or a plan date. Claude Code already asked them at install
via `.claude-plugin/plugin.json` `userConfig`; if that config is present, map
it into this file and skip questions the user already answered. On Codex, call
`request_user_input` with **at most 3 questions per call**, one batch at a
time. Cursor asks the same batches in the session.

Write the answers into `models` and `routing`, then set
`routing.setup_complete: true`.

### Batch 1 — tools you pay for

One yes/no each:

- Claude Code (`routing.tools.claude.enabled`)
- Codex CLI (`routing.tools.codex.enabled`)
- Cursor (`routing.tools.cursor.enabled`)

### Batch 2 — plan for each enabled tool

`included` or `extra`. `extra` means the tool bills beyond the subscription.
Those tools are not routed unless extra spend is allowed below. Leave disabled
tools at `included`.

### Batch 3 — order, frontier, extra spend

- Preferred first tool: `no preference`, `claude`, `codex`, or `cursor` (only tools they enabled). Store `routing.first_tool`. This is their order, not a default.
- Frontier: `never`, `when I flag a job`, or `automatically`. Default `never`. Store `routing.frontier` as `never`, `flagged`, or `auto`.
- Extra spend: `deny`, `per job`, or `capped`. Default `deny`. If capped, ask the cap as a number and store `routing.extra_spend_cap`. Zero means no extra spend.

### Batch 4 — reviewer, limits, stall

- Reviewer: `other vendor`, `same`, or `none`.
- When a job hits a limit, an error, or a stall: `hand off and tell me`, or `ask first`. Default `ask first`.
- Stall timeout: `15`, `30`, or `60` minutes. Default `30`.

### Batch 5 — versions

- `newest` or `pin`. If they pin, ask for `family=model` pairs (for example `sol=gpt-6-sol`) and store them under `models.pins`. Claude aliases stay the alias (`opus`, `sonnet`, `haiku`, `fable`) unless pinned.

The tier catalog itself is not a question. Frontier is fable / astra, strong is opus / sol, standard is sonnet / terra, fast is haiku / luna, and Cursor's default model is `grok-4.7`.

## Persist and finish

1. Write the YAML (or equivalent memory) with only confirmed licenses.
2. Set `setup_complete: true` and `routing.setup_complete: true`.
3. Tell the user where prefs were saved and that they can re-run this skill to
   change licenses or order later.
4. Do not launch coding work from this skill; hand off to `delegate-coding`
   after setup when the user still wants a handoff.

## Sibling skills

- `delegate-coding` — routes using these prefs only.
- `coding-preflight` — checklist before launch.
- `build-handoff-brief` — file-based brief template.
