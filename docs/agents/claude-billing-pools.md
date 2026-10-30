# Claude billing pools

The router treats Claude subscription usage and Anthropic API-key usage as two separate pools.

## Tool IDs and aliases

- `claude` — Claude Code authenticated with the Claude subscription (`claude auth login --claudeai`). This is the existing tool ID and remains backwards-compatible.
- `claude_subscription` — accepted alias for `claude` in preference/order fields.
- `claude_api` — Claude Code launched with `ANTHROPIC_API_KEY` present. This is a separate, opt-in pool.
- `claude_api_key` — accepted alias for `claude_api` in preference/order fields.

The normalized routing IDs remain `claude` and `claude_api`.

## Billing safety

Subscription launches return launch metadata with:

```yaml
auth: claude_subscription
unset_env:
  - ANTHROPIC_API_KEY
```

The launch runner must actually remove `ANTHROPIC_API_KEY` from the child process environment. Leaving it inherited can cause a job intended for subscription capacity to use API-key billing instead.

API launches return:

```yaml
auth: anthropic_api_key
require_env:
  - ANTHROPIC_API_KEY
```

The key itself is never copied into routing output or logs. The launch runner must fail closed if a required variable is absent.

`delegate-coding` defines the runner contract: `unset_env` and `require_env` are mandatory execution metadata, not advisory fields. `coding-preflight` also performs an explicit pool check before spawn:

```bash
bash scripts/auth-check.sh --only claude-subscription
bash scripts/auth-check.sh --only claude-api
```

The API check verifies only that the Claude binary exists and that `ANTHROPIC_API_KEY` is non-empty. It does not validate whether the key is current, well-formed, or authorized; a revoked or malformed key can pass preflight and then fail when Claude actually launches. In other words, preflight verifies configuration presence, not credential validity. The check never prints the key and does not make a billable API request.

## Default policy

`claude_api` is disabled by default and its default plan is `extra`. That means simply having an API key in the environment cannot make the router spend against the API pool. A user must explicitly enable the tool and also allow extra spend according to the existing routing policy.

Treat `plan: included` for `claude_api` as an advanced override. It disables the router's normal extra-spend consent gate for that pool. **Do not use it merely because the account currently has promotional or monthly API credits.** The router cannot verify remaining API credits or whether billing will continue after credits are exhausted. Use `included` only when an external billing control independently guarantees that the resulting spend behavior is acceptable.

Example:

```yaml
preferences:
  order:
    - claude_subscription
    - claude_api
    - codex
routing:
  extra_spend: per_job
  tools:
    claude:
      enabled: true
      plan: included
    claude_api:
      enabled: true
      plan: extra
```

This expresses the intended order: subscription capacity first, then the separately authorized API pool, then other tools.

## Fallback

Fallback does not bypass billing consent. If `claude_api` is configured as `plan: extra`, a subscription limit or stall may hand off to that pool only when the current job has the same extra-spend authorization that would have been required for an initial API launch. Otherwise the API pool is skipped and fallback continues to another eligible included tool, or stops and asks the user.

## Usage reporting

The router can read Claude subscription usage from Claude Code's `/usage` output. It does not query an Anthropic API-credit balance because this project has no non-billable balance query for that pool. Production routing therefore includes `claude_api` explicitly with unknown usage rather than inventing a balance.

## Logs

Routing logs include `billing_pool` (`claude_subscription` or `claude_api`) so a later audit can distinguish which Claude capacity was selected without storing credentials.
