---
name: agent-comms
description: >-
  Use this when messaging a builder or another agent about a build, a question, or
  a reply, including how to get a response back, how to answer their questions,
  and how to answer a question from a running coding-agent session.
---

# Agent communication

## 1. Start the handoff or question

For a build, the file brief is the spec: repo, goal, constraints, done-when, and
do-nots. The file brief still comes from **build-handoff-brief**. A direct message
with the brief path and the one-line ask is required to wake the builder; a file
drop alone does not reach them. A short question with no build can be a message
only.

## 2. Read the response

The builder messages you back. It arrives as your later turn, not a reply inside
yours. Read that message. If they need you to act, they mark it so it wakes you.
Status/FYI waits until your next turn. Do not poll their chat and do not sit in
your turn waiting.

## 3. Answer the builder

Answer with a new message to them. Put the decision in the message. If you
changed the brief, say what changed and the path. If they were blocked on you,
mark the reply so it wakes them.

## 4. Do not waste messages

Never send ack-only pings ("got it", "thanks", "on it"); wait in the same turn
for their reply; re-send the same ask while one is in flight; assume they re-read
a file you edited unless you message them; wake them for an FYI; or fan the same
job out to several agents.

## Questions from the coding agent

This is the session you launched, not the builder seat in sections 1–4. The source of truth for each peer is [docs/agents/_template.md](../../docs/agents/_template.md) and the matching [docs/agents/<name>.md](../../docs/agents/); answer in that same session and do not invent a command or a key.
