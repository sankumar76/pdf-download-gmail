#!/usr/bin/env bash
# -----------------------------------------------------------------------------
# guard-merge.sh — PreToolUse guard for mcp__github__merge_pull_request.
# Enforces MERGE_POLICY from CLAUDE.md: unless it is "all-auto", agents may only
# merge PRs whose changed files are all under docs/. Code PRs wait for a human.
# Fails CLOSED when the PR's files cannot be listed.
#
# Requires: gh (authenticated) and jq or python3.
# -----------------------------------------------------------------------------
set -u
INPUT="$(cat)"
PROJECT_ROOT="${CLAUDE_PROJECT_DIR:-$(pwd)}"

deny() { echo "Merge guard: $1" >&2; exit 2; }

if grep -qE '^\|[[:space:]]*`MERGE_POLICY`[[:space:]]*\|[^|]*all-auto' "$PROJECT_ROOT/CLAUDE.md" 2>/dev/null; then
  exit 0
fi

if command -v jq >/dev/null 2>&1; then
  read -r OWNER REPO PR < <(printf '%s' "$INPUT" | jq -r '.tool_input | "\(.owner // "") \(.repo // "") \(.pullNumber // .pull_number // "")"')
elif command -v python3 >/dev/null 2>&1; then
  read -r OWNER REPO PR < <(printf '%s' "$INPUT" | python3 -c 'import sys,json; t=json.load(sys.stdin).get("tool_input",{}); print(t.get("owner",""), t.get("repo",""), t.get("pullNumber") or t.get("pull_number") or "")' | tr -d '\r')
else
  deny "neither jq nor python3 is installed, so the PR cannot be checked."
fi

[ -n "${OWNER:-}" ] && [ -n "${REPO:-}" ] && [ -n "${PR:-}" ] || deny "could not read owner/repo/pull number from the tool call."
case "$PR" in *[!0-9]*) deny "pull number '$PR' is not numeric." ;; esac
command -v gh >/dev/null 2>&1 || deny "GitHub CLI (gh) is required to verify the PR is docs-only."

FILES="$(gh api --paginate "repos/$OWNER/$REPO/pulls/$PR/files" --jq '.[].filename' 2>/dev/null)" \
  || deny "could not list the files changed by $OWNER/$REPO#$PR."
[ -n "$FILES" ] || deny "$OWNER/$REPO#$PR has no changed files listed."

NON_DOCS="$(printf '%s\n' "$FILES" | grep -v '^docs/' || true)"
if [ -n "$NON_DOCS" ]; then
  deny "MERGE_POLICY reserves code merges for a human. $OWNER/$REPO#$PR changes files outside docs/: $(printf '%s' "$NON_DOCS" | tr '\n' ' '). Label the PR awaiting-human-merge and stop."
fi
exit 0
