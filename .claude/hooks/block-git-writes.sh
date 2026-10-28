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

PROJECT_ROOT="${CLAUDE_PROJECT_DIR:-$(pwd)}"

# Backslashes are dropped first because the shell would unescape g\it to git.
is_git_word() { local w="${1//\\/}"; w="${w##*/}"; w="${w%.exe}"; [ "$w" = "git" ]; }

is_project_root() {
  local p="$1"
  case "$p" in /*) ;; *) p="$PROJECT_ROOT/$p" ;; esac
  [ "$(realpath -m "$p" 2>/dev/null)" = "$(realpath -m "$PROJECT_ROOT" 2>/dev/null)" ]
}

# Arguments: the words following "git". Returns 0 if the invocation is read-only.
git_invocation_ok() {
  # Skip harmless global options. -c, --config-env, --exec-path, --git-dir and
  # --work-tree are deliberately absent: they can load a config (aliases, pager,
  # fsmonitor) that runs arbitrary commands. -C may only point at the project root.
  while [ $# -gt 0 ]; do
    case "$1" in
      -C) [ $# -ge 2 ] && is_project_root "$2" || return 1; shift 2 ;;
      -C?*) is_project_root "${1#-C}" || return 1; shift ;;
      --no-pager|-P|--no-optional-locks|--literal-pathspecs|--no-replace-objects) shift ;;
      *) break ;;
    esac
  done
  local sub="${1:-}"; [ $# -gt 0 ] && shift
  local a name d
  for a in "$@"; do                            # options that write files or run commands
    case "$a" in -O*) return 1 ;; esac
    case "$a" in
      --?*)                                    # git accepts unambiguous prefixes: --out == --output
        name="${a%%=*}"
        for d in --output --open-files-in-pager --upload-pack --exec --exec-path --ext-diff --textconv; do
          case "$d" in "$name"*) return 1 ;; esac
        done ;;
    esac
  done
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
    checkout|switch)                           # move to an existing commit only — no create, discard or force
      local ref=""
      for a in "$@"; do
        case "$a" in
          --detach|-q|--quiet) ;;
          -*) return 1 ;;
          *) [ -z "$ref" ] || return 1; ref="$a" ;;
        esac
      done
      # A path (git checkout file.py) would discard local changes; require a real commit-ish.
      [ -n "$ref" ] && [ ! -e "$PROJECT_ROOT/$ref" ] \
        && git -C "$PROJECT_ROOT" rev-parse --verify --quiet "$ref^{commit}" >/dev/null 2>&1 ;;
    *) return 1 ;;
  esac
}

# Split into simple commands on ; & | ( ) ` and newlines; strip quotes so that
# bash -c "git push" is still seen as git push.
SEGMENTS="$(printf '%s\n' "$CMD" | tr ';&|()`' '\n\n\n\n\n\n' | tr -d "\"'")"

HAS_GIT=0 ENV_OR_CD=""
while IFS= read -r segment; do
  read -r -a words <<< "$segment" || true
  [ "${#words[@]}" -eq 0 ] && continue
  for i in "${!words[@]}"; do
    w="${words[$i]}"
    # Assignments (GIT_PAGER=…, export PAGER=…) and directory changes can point git at
    # a different config; they are only rejected if the command also runs git.
    if [[ "$w" =~ ^[A-Za-z_][A-Za-z0-9_]*= ]] || [ "$w" = "cd" ] || [ "$w" = "pushd" ]; then
      ENV_OR_CD="$w"
    fi
    # Command position: the first word, or the word after a wrapper such as xargs.
    if [ "$i" = 0 ] || case "${words[$((i - 1))]}" in xargs|env|command|nohup|nice|time|sudo|builtin) true ;; *) false ;; esac; then
      case "$w" in
        *\$*|*\**|*\?*|*\[*|*\{*) block "command name '$w' uses expansion" ;;
      esac
    fi
    # Anywhere else (e.g. find -exec g?t), a glob that could expand to "git" counts as git.
    # A lone * is left alone so that ls * and cat docs/* keep working.
    base="${w//\\/}"; base="${base##*/}"
    if [ "$base" != "*" ] && [[ "$base" == *[\*\?\[]* ]] && [[ git == $base || git.exe == $base ]]; then
      block "'$w' could expand to git"
    fi
    case "$w" in
      eval|exec) block "'$w' is not permitted" ;;
      *=git|*=*/git|*=git.exe) block "assigning git to a variable" ;;
    esac
    if is_git_word "$w"; then
      HAS_GIT=1
      git_invocation_ok "${words[@]:$((i + 1))}" || block "non-read-only git command"
    fi
  done
done <<< "$SEGMENTS"

[ "$HAS_GIT" = 1 ] && [ -n "$ENV_OR_CD" ] && block "'$ENV_OR_CD' cannot be combined with git; run git from the project root without environment overrides"

exit 0
