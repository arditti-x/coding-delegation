#!/usr/bin/env bash
# auth-check.sh — one line per coding surface: ok, logged out, usage exhausted,
# not installed, or unknown. Runs only each tool's OWN documented status command.
# Never prints tokens, emails, or raw command output.
#
# Exit codes:
#   0  every checked surface is ok (or has no status command and is "unknown, manual check")
#   1  at least one surface needs attention (logged out, usage exhausted, or its
#      status command failed / timed out / returned something unexpected)
#   2  bad arguments
#
# Options:
#   --strict          also exit 1 for "not installed" and "unknown, manual check"
#   --only a,b        check only these surfaces (claude-code,cursor-cli,codex,agy,kiro,grok-build,cursor-cloud-agents)
#   --timeout SECS    per-command timeout (default 60; env AUTH_CHECK_TIMEOUT)
#
# Usage limits: no surface here exposes a non-interactive usage/quota command, so
# usage limits come from a local record the skills write when a limit is hit:
#   ${CODING_DELEGATION_USAGE_FILE:-~/.config/coding-delegation/usage-limits}
# One line per limit:  <surface> <reset YYYY-MM-DD or unknown> [note]
# A line stops counting once its reset date has passed. Keep this file out of git.

set -u

STRICT=0
ONLY=""
TIMEOUT="${AUTH_CHECK_TIMEOUT:-60}"
USAGE_FILE="${CODING_DELEGATION_USAGE_FILE:-$HOME/.config/coding-delegation/usage-limits}"
ALL_SURFACES="claude-code cursor-cli codex agy kiro grok-build cursor-cloud-agents"

while [ $# -gt 0 ]; do
  case "$1" in
    --strict) STRICT=1 ;;
    --only) shift; ONLY="${1:-}" ;;
    --only=*) ONLY="${1#--only=}" ;;
    --timeout) shift; TIMEOUT="${1:-60}" ;;
    --timeout=*) TIMEOUT="${1#--timeout=}" ;;
    -h|--help) sed -n '2,23p' "$0"; exit 0 ;;
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
login_ok() { # surface detail
  local reset
  if reset="$(usage_limit "$1")"; then
    line "$1" "usage exhausted" "resets $reset (from $USAGE_FILE)"
  else
    line "$1" "ok" "$2"
  fi
}

failed() { # surface command
  if [ "$RC" = 124 ]; then line "$1" "unknown" "\`$2\` timed out after ${TIMEOUT}s"
  else line "$1" "unknown" "\`$2\` exited $RC with unexpected output"; fi
}

check() {
  case "$1" in
    claude-code)
      command -v claude >/dev/null || { line "$1" "not installed" "binary claude not on PATH"; return; }
      run claude auth status --json
      if echo "$OUT" | grep -Eq '"loggedIn"[[:space:]]*:[[:space:]]*true'; then login_ok "$1" "claude auth status: loggedIn true"
      elif echo "$OUT" | grep -Eq '"loggedIn"[[:space:]]*:[[:space:]]*false'; then line "$1" "logged out" "run the Claude login flow in docs/agents/claude-code.md"
      else failed "$1" "claude auth status --json"; fi ;;
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
    *) echo "unknown surface: $1 (known: $ALL_SURFACES)" >&2; exit 2 ;;
  esac
}

for s in $SURFACES; do check "$s"; done
exit "$ATTENTION"
