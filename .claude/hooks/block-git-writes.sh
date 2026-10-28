#!/usr/bin/env bash
# -----------------------------------------------------------------------------
# block-git-writes.sh — PreToolUse guard for Bash in read-only roles
# (reviewers, master, analysts, planners). Every git invocation in the command
# must be a read-only subcommand on the allowlist below; anything else, plus
# eval and indirect command names ($cmd ...), is blocked.
# Exit 2 blocks the command and shows the message to the agent.
#
# This is defence in depth, not a sandbox: shell parsing here is approximate.
# The authoritative controls are GitHub branch protection and token scope.
# -----------------------------------------------------------------------------
set -u
INPUT="$(cat)"
if command -v jq >/dev/null 2>&1; then
  CMD="$(printf '%s' "$INPUT" | jq -r '.tool_input.command // empty')"
elif command -v python3 >/dev/null 2>&1; then
  CMD="$(printf '%s' "$INPUT" | python3 -c 'import sys,json; print(json.load(sys.stdin).get("tool_input",{}).get("command",""))')"
else
  echo "Git guard: neither jq nor python3 is installed; command blocked. Install jq." >&2
  exit 2
fi

block() {
  echo "Git guard: your role is read-only on the repository ($1). Allowed git commands: status, diff, log, show, blame, grep, ls-files, ls-tree, rev-parse, describe, shortlog, cat-file, merge-base, fetch, remote -v/get-url/show, branch (listing only), checkout/switch <existing-ref>. Report the change you need in your hand-off instead of running: $CMD" >&2
  exit 2
}

is_git_word() { local w="${1##*/}"; w="${w%.exe}"; [ "$w" = "git" ]; }

# Arguments: the words following "git". Returns 0 if the invocation is read-only.
git_invocation_ok() {
  while [ $# -gt 0 ]; do                       # skip git's global options
    case "$1" in
      -C|-c|--git-dir|--work-tree|--namespace) shift 2 2>/dev/null || shift ;;
      -C*|-c*|--git-dir=*|--work-tree=*|--namespace=*|--no-pager|-P|--no-optional-locks|--bare|--literal-pathspecs|--no-replace-objects) shift ;;
      *) break ;;
    esac
  done
  local sub="${1:-}"; [ $# -gt 0 ] && shift
  case "$sub" in
    status|diff|log|show|blame|grep|ls-files|ls-tree|rev-parse|describe|shortlog|cat-file|merge-base|fetch) return 0 ;;
    remote)
      case "${1:-}" in ""|-v|--verbose|get-url|show) return 0 ;; esac
      return 1 ;;
    branch)                                    # listing only; any positional creates a branch unless --list
      local listing=0 skip=0 a
      for a in "$@"; do
        if [ "$skip" = 1 ]; then skip=0; continue; fi
        case "$a" in
          --list|-l) listing=1 ;;
          -a|--all|-r|--remotes|-v|-vv|--verbose|--show-current|--no-color|--color*|--sort=*|--format=*|--contains=*|--merged=*|--no-merged=*|--points-at=*) ;;
          --contains|--merged|--no-merged|--points-at|--sort|--format) skip=1 ;;
          -*) return 1 ;;
          *) [ "$listing" = 1 ] || return 1 ;;
        esac
      done
      return 0 ;;
    checkout|switch)                           # move to an existing ref only — no create, discard or force
      local refs=0 a
      for a in "$@"; do
        case "$a" in
          --detach|-q|--quiet) ;;
          -*|.) return 1 ;;
          *) refs=$((refs + 1)) ;;
        esac
      done
      [ "$refs" = 1 ] ;;
    *) return 1 ;;
  esac
}

# Split into simple commands on ; & | ( ) ` and newlines; strip quotes so that
# bash -c "git push" is still seen as git push.
SEGMENTS="$(printf '%s\n' "$CMD" | tr ';&|()`' '\n\n\n\n\n\n' | tr -d "\"'")"

while IFS= read -r segment; do
  read -r -a words <<< "$segment" || true
  [ "${#words[@]}" -eq 0 ] && continue
  case "${words[0]}" in
    \$*) block "indirect command name '${words[0]}'" ;;
  esac
  for i in "${!words[@]}"; do
    w="${words[$i]}"
    case "$w" in
      eval|exec) block "'$w' is not permitted" ;;
      *=git|*=*/git|*=git.exe) block "assigning git to a variable" ;;
    esac
    if is_git_word "$w"; then
      git_invocation_ok "${words[@]:$((i + 1))}" || block "non-read-only git command"
    fi
  done
done <<< "$SEGMENTS"

exit 0
