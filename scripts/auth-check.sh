#!/usr/bin/env bash
# auth-check.sh — one line per coding surface: ok, logged out, usage exhausted,
# not installed, or unknown. Runs only each tool's OWN documented status command.
# Never prints tokens, emails, or raw command output.
#
# Exit codes:
#   0  every checked surface is ok (or has no status command and is "unknown, manual check")
#   1  at least one surface needs attention (logged out, usage exhausted, missing env,
#      or its status command failed / timed out / returned something unexpected)
#   2  bad arguments
#
# Options:
#   --strict          also exit 1 for "not installed" and "unknown, manual check"
#   --only a,b        check only these surfaces. In addition to the normal surface
#                     names, claude-subscription and claude-api are accepted for
#                     explicit billing-pool preflight checks.
#   --timeout SECS    per-command timeout (default 60; env AUTH_CHECK_TIMEOUT)
#
# Usage limits recorded by a session still come from a local file. Live remaining
# usage for model routing is separate: Claude `/usage`, Codex
# account/rateLimits/read (never rateLimitResetCredit/consume), Cursor unknown.
#   ${CODING_DELEGATION_USAGE_FILE:-~/.config/coding-delegation/usage-limits}
# One line per limit:  <surface> <reset YYYY-MM-DD or unknown> [note]
# A line stops counting once its reset date has passed. Keep this file out of git.

set -u

STRICT=0
ONLY=""
TIMEOUT="${AUTH_CHECK_TIMEOUT:-60}"
USAGE_FILE="${CODING_DELEGATION_USAGE_FILE:-$HOME/.config/coding-delegation/usage-limits}"
# Keep claude-api out of the default sweep: users who did not enable the API
# pool should not fail preflight merely because they do not have an API key.
ALL_SURFACES="claude-code cursor-cli codex agy kiro grok-build cursor-cloud-agents"

while [ $# -gt 0 ]; do
  case "$1" in
    --strict) STRICT=1 ;;
    --only) shift; ONLY="${1:-}" ;;
    --only=*) ONLY="${1#--only=}" ;;
    --timeout) shift; TIMEOUT="${1:-60}" ;;
    --timeout=*) TIMEOUT="${1#--timeout=}" ;;
    -h|--help) sed -n '2,26p' "$0"; exit 0 ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
  shift
done

SURFACES="$ALL_SURFACES"
[ -n "$ONLY" ] && SURFACES="$(echo "$ONLY" | tr ',' ' ')"

TODAY="$(date +%F)"
ATTENTION=0

line() { # surface status detail
  printf '%-20s %-17s %s\n' "$1" "$2" "$3"
  case "$2" in
    ok) ;;
    "not installed"|"unknown, manual") [ "$STRICT" = 1 ] && ATTENTION=1 ;;
    *) ATTENTION=1 ;;
  esac
}

# run a status command with a timeout and no stdin; capture output in $OUT, exit in $RC
run() {
  OUT="$(timeout "$TIMEOUT" "$@" </dev/null 2>&1)"
  RC=$?
}

usage_limit() { # prints "reset-date note" if an active limit is recorded for $1
  [ -f "$USAGE_FILE" ] || return 1
  local s d rest
  while read -r s d rest; do
    case "$s" in ''|\#*) continue ;; esac
    [ "$s" = "$1" ] || continue
    if [ "$d" = "unknown" ] || [[ "$d" > "$TODAY" ]] || [ "$d" = "$TODAY" ]; then
      echo "$d"; return 0
    fi
  done < "$USAGE_FILE"
  return 1
}

# after a login check passes, downgrade to "usage exhausted" if a limit is recorded
login_ok() { # surface detail [usage-surface]
  local surface="$1" detail="$2" usage_surface="${3:-$1}" reset
  if reset="$(usage_limit "$usage_surface")"; then
    line "$surface" "usage exhausted" "resets $reset (from $USAGE_FILE)"
  else
    line "$surface" "ok" "$detail"
  fi
}

failed() { # surface command
  if [ "$RC" = 124 ]; then line "$1" "unknown" "\`$2\` timed out after ${TIMEOUT}s"
  else line "$1" "unknown" "\`$2\` exited $RC with unexpected output"; fi
}

check_claude_subscription() { # displayed-surface
  local surface="$1" detail key_present=0
  command -v claude >/dev/null || { line "$surface" "not installed" "binary claude not on PATH"; return; }
  [ -n "${ANTHROPIC_API_KEY:-}" ] && key_present=1
  # Verify the subscription/OAuth login with the API-key override removed.
  # Otherwise a stray key could affect the very status check meant to validate
  # the subscription path.
  OUT="$( (unset ANTHROPIC_API_KEY; timeout "$TIMEOUT" claude auth status --json </dev/null) 2>&1 )"
  RC=$?
  if echo "$OUT" | grep -Eq '"loggedIn"[[:space:]]*:[[:space:]]*true'; then
    detail="claude auth status: loggedIn true (checked with ANTHROPIC_API_KEY unset)"
    if [ "$key_present" = 1 ]; then
      detail="$detail; ANTHROPIC_API_KEY present in parent and must be stripped by launch contract"
    fi
    login_ok "$surface" "$detail" "claude-code"
  elif echo "$OUT" | grep -Eq '"loggedIn"[[:space:]]*:[[:space:]]*false'; then
    line "$surface" "logged out" "run the Claude login flow in docs/agents/claude-code.md"
  else
    failed "$surface" "claude auth status --json (API key unset)"
  fi
}

check_claude_api() { # displayed-surface
  local surface="$1"
  command -v claude >/dev/null || { line "$surface" "not installed" "binary claude not on PATH"; return; }
  if [ -n "${ANTHROPIC_API_KEY:-}" ]; then
    line "$surface" "ok" "ANTHROPIC_API_KEY present (value not printed)"
  else
    line "$surface" "missing env" "ANTHROPIC_API_KEY is required for the Claude API pool"
  fi
}

check() {
  case "$1" in
    claude-code|claude-subscription)
      check_claude_subscription "$1" ;;
    claude-api)
      check_claude_api "$1" ;;
    cursor-cli)
      command -v agent >/dev/null || { line "$1" "not installed" "binary agent not on PATH"; return; }
      run agent status --format json
      if echo "$OUT" | grep -Eq '"isAuthenticated"[[:space:]]*:[[:space:]]*true'; then login_ok "$1" "agent status: isAuthenticated true"
      elif echo "$OUT" | grep -Eq '"isAuthenticated"[[:space:]]*:[[:space:]]*false'; then line "$1" "logged out" "needs \`agent login\` (see docs/agents/cursor-cli.md)"
      else failed "$1" "agent status --format json"; fi ;;
    codex)
      command -v codex >/dev/null || { line "$1" "not installed" "binary codex not on PATH"; return; }
      run codex login status
      if [ "$RC" = 0 ] && echo "$OUT" | grep -q 'Logged in'; then login_ok "$1" "codex login status: logged in"
      elif [ "$RC" = 1 ] && echo "$OUT" | grep -q 'Not logged in'; then line "$1" "logged out" "needs \`codex login\` (see docs/agents/codex.md)"
      else failed "$1" "codex login status"; fi ;;
    kiro)
      command -v kiro-cli >/dev/null || { line "$1" "not installed" "binary kiro-cli not on PATH"; return; }
      run kiro-cli whoami
      if [ "$RC" = 0 ] && echo "$OUT" | grep -q 'Logged in'; then login_ok "$1" "kiro-cli whoami: logged in"
      else failed "$1" "kiro-cli whoami"; fi ;;
    agy)
      command -v agy >/dev/null || { line "$1" "not installed" "binary agy not on PATH"; return; }
      if reset="$(usage_limit "$1")"; then line "$1" "usage exhausted" "resets $reset (from $USAGE_FILE)"
      else line "$1" "unknown, manual" "no non-interactive status command; /usage in the TUI (https://antigravity.google/docs/cli/reference/, checked 2026-10-09)"; fi ;;
    grok-build)
      command -v grok >/dev/null || { line "$1" "not installed" "binary grok not on PATH"; return; }
      if reset="$(usage_limit "$1")"; then line "$1" "usage exhausted" "resets $reset (from $USAGE_FILE)"
      else line "$1" "unknown, manual" "no status subcommand (https://docs.x.ai/build/cli/reference, checked 2026-10-09)"; fi ;;
    cursor-cloud-agents)
      if reset="$(usage_limit "$1")"; then line "$1" "usage exhausted" "resets $reset (from $USAGE_FILE)"
      else line "$1" "unknown, manual" "no CLI; check cursor.com/agents (https://cursor.com/docs/cloud-agent, checked 2026-10-09)"; fi ;;
    *) echo "unknown surface: $1 (known defaults: $ALL_SURFACES; also claude-subscription, claude-api)" >&2; exit 2 ;;
  esac
}

for s in $SURFACES; do check "$s"; done
exit "$ATTENTION"
