# Cursor Cloud Agents

## What it is

Cloud agents that run in Cursor-managed VMs. This peer is not a local CLI. Do not install a binary for it. The Cursor CLI (`agent`) is a different peer. Cursor Cloud Agents run coding agents in Cursor's hosted environment.

## Install

No local install.

## Login

- Sign in to a Cursor account. Cloud Agents require a paid Cursor plan.
- Before anyone can start an agent from a repository, a Cursor account admin connects source control: GitHub (Cloud and Enterprise Server), GitLab (Cloud and Self-Hosted), Bitbucket Cloud, or Azure DevOps. You need read-write access to the repo.
- Start agents from [cursor.com/agents](https://cursor.com/agents), from Cursor Desktop (Cloud in the agent-input dropdown), or from the other surfaces listed in the docs (iOS, Slack, GitHub or Bitbucket `@cursor`, Linear, API).
- If a run does not start, the docs say to confirm you are logged in, source control is connected, repository permissions are sufficient, and the account is on a paid plan.

## Auth status check

unknown, manual check. No local CLI or status command for this surface; confirm login, source control, and plan at https://cursor.com/agents. Source: https://cursor.com/docs/cloud-agent (checked 2026-10-09).

## Commands and skills

**Unknown.** The current official Cloud Agents launch documentation does not publish a slash-command or skill-invocation list for this surface.

## Ongoing session and answering questions

- **How it asks:** Unknown. The Cloud Agents pages do not describe an in-run question prompt.
- **How to answer:** Stay on the same agent. `POST /v1/agents/{id}/runs` with `prompt.text` continues that agent's conversation and workspace. If another run is `CREATING` or `RUNNING`, the API returns `409 agent_busy`; wait for that run to end or cancel it. Follow-ups are accepted when the agent is `IDLE`. A follow-up can also be sent from [cursor.com/agents](https://cursor.com/agents). Team follow-ups require the team setting. Commenting `@cursor` on a GitHub PR or issue, or on a Bitbucket PR, starts an agent; those pages do not say the comment answers a question inside an existing run.
- **Blocks:** Unknown.

## Observed behavior

unknown

## Quirks

unknown

## Checked

2026-10-03

## Updated instructions

- https://cursor.com/docs/cloud-agent
- https://docs.cursor.com/en/background-agent/api/launch-an-agent
- https://cursor.com/docs/cloud-agent/api/endpoints
