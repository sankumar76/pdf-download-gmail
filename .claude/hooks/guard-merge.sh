#!/usr/bin/env bash
# -----------------------------------------------------------------------------
# guard-merge.sh — PreToolUse guard for mcp__github__merge_pull_request.
# Enforces MERGE_POLICY from CLAUDE.md: unless it is "all-auto", agents may only
# merge PRs whose changed files are all under docs/. Code PRs wait for a human.
# The policy is read from CLAUDE.md on the branch-protected main branch via the
# GitHub API — never from the working tree or local refs, which an agent can
# rewrite. If the policy cannot be read the strict (docs-only) rule applies, and
# the merge is blocked when the PR's files cannot be read.
#
# Requires: gh (authenticated) and jq or python3.
# -----------------------------------------------------------------------------
set -u
INPUT="$(cat)"

deny() { echo "Merge guard: $1" >&2; exit 2; }

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

if gh api -H "Accept: application/vnd.github.raw" "repos/$OWNER/$REPO/contents/CLAUDE.md?ref=main" 2>/dev/null \
    | grep -qE '^\|[[:space:]]*`MERGE_POLICY`[[:space:]]*\|[[:space:]]*\*{0,2}all-auto\*{0,2}[[:space:]]*\|'; then
  exit 0
fi

EXPECTED="$(gh api "repos/$OWNER/$REPO/pulls/$PR" --jq '.changed_files' 2>/dev/null | tr -d '\r')" \
  || deny "could not read $OWNER/$REPO#$PR."
# One line per file; renames also emit the old path so a move out of code is caught.
# Names are JSON-encoded so a newline inside a filename cannot forge extra lines.
LISTING="$(gh api --paginate "repos/$OWNER/$REPO/pulls/$PR/files" --jq '.[] | "F \(.filename | @json)", (select(.previous_filename) | "F \(.previous_filename | @json)"), "#"' 2>/dev/null | tr -d '\r')" \
  || deny "could not list the files changed by $OWNER/$REPO#$PR."
LISTED="$(printf '%s\n' "$LISTING" | grep -c '^#$')"
# The files API stops at 3000 entries; a count mismatch means we did not see everything.
[ -n "$EXPECTED" ] && [ "$LISTED" = "$EXPECTED" ] \
  || deny "$OWNER/$REPO#$PR reports ${EXPECTED:-?} changed files but ${LISTED} were listed."
FILES="$(printf '%s\n' "$LISTING" | sed -n 's/^F //p')"
[ -n "$FILES" ] || deny "$OWNER/$REPO#$PR has no changed files listed."

NON_DOCS="$(printf '%s\n' "$FILES" | grep -v '^"docs/' || true)"
if [ -n "$NON_DOCS" ]; then
  deny "MERGE_POLICY reserves code merges for a human. $OWNER/$REPO#$PR changes files outside docs/: $(printf '%s' "$NON_DOCS" | tr '\n' ' '). Label the PR awaiting-human-merge and stop."
fi
exit 0
