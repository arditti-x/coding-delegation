# Other coding CLIs and agents

## What it is

Use this when the tool is not one of the named peers. Do not invent its install or login from a similar vendor.

## Install

1. Open the vendor’s current install page (their docs or their GitHub README). Copy the install command from that page only.
2. Install it yourself. This plugin does not run the installer.
3. Confirm the binary with the command their docs use (`which <binary>`, `<binary> --version`, or whatever they document).

## Login

Log in with the command their docs name (`login`, `auth login`, a browser on first launch, or an env var). Confirm with their documented status or whoami command.

Write down, next to your coding-delegation prefs or in a local note:

- official docs URL
- the date you checked it (YYYY-MM-DD)
- binary name
- the login command you actually used

In `coding-delegation.prefs.yaml`, set the surface up as a peer: add the name to `licenses.other_tty_cloud_clis` and, if you want it ranked, to `preferences.order`. Re-run `setup-coding-delegation` instead of editing those fields by guesswork.

If Herdr should track it, check https://herdr.dev/docs/agents/ for whether that agent is already recognized. If it is not, it can still run in a pane as a normal terminal.

## Commands and skills

When using a coding CLI or agent not named above, find that vendor's current official skills and commands index, record its URL and the date checked, and use only commands documented there. Do not invent commands, slash commands, skills, or flags.

## Ongoing session and answering questions

- **How it asks:** Unknown until that vendor's current official page says so.
- **How to answer:** Unknown. Record the page URL and the date checked. Do not invent a command or a key.
- **Blocks:** Unknown until that page says whether the session waits.

## Observed behavior

unknown

## Quirks

unknown

## Checked

2026-10-03

## Updated instructions

Start from the vendor’s own docs index. Herdr’s agent list: https://herdr.dev/docs/agents/
