---
name: setup-coding-delegation
description: >-
  Use on first install, when coding-delegation prefs are missing or incomplete,
  or when the user says "configure coding delegation" or wants to change
  licenses or routing preferences. Collects which surfaces are licensed and
  how to prefer them; does not invent licenses.
---

# Setup coding delegation

Run this skill before any coding handoff when preferences are missing or the
user asks to reconfigure. Persist the result so later routing uses **only**
what the user declared. Do not invent licenses the user did not confirm.

## Prefs file

Agents should load and write preferences from one of these paths (first that
exists wins for read; for first-time write, prefer the repo copy if the agent
is in a git checkout, otherwise the home config path):

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
becomes `preferences.order`. There is no built-in default ranking. If they
skip ranking, leave `order` empty and ask again before the first
`delegate-coding` launch, or treat all licensed surfaces as equal peers and
ask which to use for that task.

### c) Optional when-to-use notes

For each licensed surface, offer an optional free-text `preferences.when.<key>`
(for example, “long PR work”, “interactive debugging”, “offline / air-gapped”).
Empty strings are fine.

Confirm `defaults` (or keep the documented defaults unless the user changes
them): never edit the main checkout; require a TTY for cloud CLIs; run
preflight before launch.

## Persist and finish

1. Write the YAML (or equivalent memory) with only confirmed licenses.
2. Set `setup_complete: true`.
3. Tell the user where prefs were saved and that they can re-run this skill to
   change licenses or order later.
4. Do not launch coding work from this skill; hand off to `delegate-coding`
   after setup when the user still wants a handoff.

## Sibling skills

- `delegate-coding` — routes using these prefs only.
- `coding-preflight` — checklist before launch.
- `build-handoff-brief` — file-based brief template.
