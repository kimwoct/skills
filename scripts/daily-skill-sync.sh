#!/bin/bash
# Daily skill-sync loop for the skills-kimwoct collection.
# Scheduled daily at 05:00 via com.kimwoct.skill-sync (LaunchAgent).
#
# Rail 1 (deterministic): fast-forward onto origin/main, mirror the latest
#   skills in (repo-managed dirs, or dirs with files modified within
#   SYNC_WINDOW_DAYS=7; only dirs containing SKILL.md; never *workspace*),
#   run structural gates. Dry-run restores the tree afterward.
# Rail 2 (agent, only when changes exist): one pi --print pass reviews the
#   diff, updates README rows, lands logical commits per
#   skills/skills-kimwoct-patterns; it never pushes.
# Rail 3 (deterministic): gates again (incl. README coverage), push to
#   origin/main, verify. Never force-pushes; divergence is left for a human.
#
# Usage: daily-skill-sync.sh [-n]
#   -n  dry-run: rails + gates only; no commit, push, or persistent change

set -euo pipefail

REPO=/Users/user/Documents/GitHub/skills-kimwoct
LIVE_SKILLS=/Users/user/.agents/skills
LOG_DIR="$HOME/.local/state/skills-kimwoct"
LOG="$LOG_DIR/skill-sync.log"
PI_BIN="$HOME/.bun/bin/pi"
PI_TIMEOUT_S=$((60 * 60))
SYNC_WINDOW_DAYS=${SYNC_WINDOW_DAYS:-7}

case "${1:-}" in
  -n | --dry-run) DRY=1 ;;
  "") DRY=0 ;;
  *) echo "usage: $0 [-n|--dry-run]" >&2; exit 64 ;;
esac

mkdir -p "$LOG_DIR"
exec >>"$LOG" 2>&1
log() { printf '[%s] %s\n' "$(date '+%F %T')" "$*"; }
dry_restore() {
  [ "$DRY" = 1 ] || return 0
  git -C "$REPO" reset -q --hard origin/main
  find "$REPO/skills" -name '__pycache__' -type d -prune -exec rm -rf {} + 2>/dev/null || true
}
gate_fail() { log "GATE FAILED: $1"; dry_restore; log "dry=$DRY: repo tree restored to origin/main"; exit 1; }

PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$HOME/.local/bin:$HOME/.bun/bin"
export PATH

log "=== daily skill sync start (dry=$DRY) ==="
cd "$REPO"
BEFORE=$(git rev-parse origin/main 2>/dev/null || echo "none")

# Rail 1 — decide and mirror.
if [ "$DRY" = 0 ]; then
  git fetch origin
  AHEAD=$(git rev-list --count HEAD..origin/main)   # commits origin has, local lacks
  LOCAL_AHEAD=$(git rev-list --count origin/main..HEAD)
  if [ "$AHEAD" -gt 0 ]; then
    if [ "$LOCAL_AHEAD" -gt 0 ]; then
      log "FAIL: local and origin/main diverged; needs a human."
      exit 2
    fi
    git pull --ff-only origin main
    log "fast-forwarded to origin/main at $(git rev-parse --short HEAD)"
  fi
fi

candidates=""
while IFS= read -r d; do
  name=$(basename "$d")
  [ -f "$LIVE_SKILLS/$name/SKILL.md" ] || continue
  in_repo=1
  git ls-files --error-unmatch "skills/$name/SKILL.md" >/dev/null 2>&1 || in_repo=0
  recent=0
  [ -n "$(find "$d" -type f -mtime -"$SYNC_WINDOW_DAYS")" ] && recent=1 && true
  # Sync: repo-managed skills (updates) OR skills modified within the window (latest).
  if [ "$in_repo" = 1 ] || [ "$recent" = 1 ]; then
    candidates="$candidates $name"
  fi
done < <(find "$LIVE_SKILLS" -maxdepth 1 -mindepth 1 -type d)

RSYNC_EXCLUDES=(--exclude '.DS_Store' --exclude '__pycache__' --exclude '*workspace*' --exclude '.*')
for name in $candidates; do
  rsync -a --delete "${RSYNC_EXCLUDES[@]}" "$LIVE_SKILLS/$name/" "$REPO/skills/$name/"
done
for d in "$REPO"/skills/*/; do
  name=$(basename "$d")
  if [ ! -d "$LIVE_SKILLS/$name" ]; then
    if [ "$DRY" = 0 ]; then rm -rf "$d"; log "removed stale skill dir: $name"; fi
  fi
done

CHANGES=$(git status --porcelain)
if [ -z "$CHANGES" ]; then
  log "nothing to sync; done"
  exit 0
fi
log "changes detected: $(echo "$CHANGES" | wc -l | tr -d ' ') paths"
# Stage the mirror output only; repo infra (scripts/, dotfiles) stays out of sync commits.
git add -A -- skills README.md

# Rail 1 gates — structural validation before the agent sees anything.
CHECK=$(git diff --cached --check | head -3)
[ -z "$CHECK" ] || gate_fail "whitespace/conflict-marker errors: $CHECK"
for f in skills/*/SKILL.md; do
  name=$(basename "$(dirname "$f")")
  n=$(awk '/^---$/{c++;next} c==1 && $1=="name:"{print substr($0,7); exit}' "$f")
  [ "$n" = "$name" ] || gate_fail "$f: name '$n' != directory '$name'"
  deschq=$(awk '/^---$/{c++;next} c==1 && /^description:/{print; exit}' "$f")
  [ -n "$deschq" ] || gate_fail "$f: no description"
done
if git diff --cached | grep -qiE 'sk-[A-Za-z0-9]{16,}|BEGIN (RSA|OPENSSH|EC) PRIVATE KEY|ghp_[A-Za-z0-9]{20,}|aws_secret_access_key'; then
  gate_fail "possible secret in staged diff"
fi
py_files=$(find skills -name '*.py' -type f)
if [ -n "$py_files" ]; then
  python3 -m py_compile $py_files || gate_fail "py_compile failed"
fi
find "$REPO/skills" -name '__pycache__' -type d -prune -exec rm -rf {} + 2>/dev/null || true
log "rail-1 gates passed"

if [ "$DRY" = 1 ]; then
  dry_restore
  log "dry-run: mirrored paths restored; review/commit/push skipped"
  exit 0
fi

# Rail 2 — agent review; commits, never pushes.
PROMPT_FILE=$(mktemp /tmp/skill-sync-prompt.XXXXXX)
cat >"$PROMPT_FILE" <<'PROMPT'
You are the daily skill-sync reviewer for the skills-kimwoct collection (cwd).
A deterministic mirror just copied changed skills from the live skills directory;
git status / git diff --cached (skills/ + README.md only) shows exactly what arrived.

Steps, in order:
1. Read skills/skills-kimwoct-patterns/SKILL.md first - it holds this repo's conventions.
2. Review the diff. NEW skills: read each SKILL.md fully; verify frontmatter parses, name
   matches dir, no secrets, no hardcoded machine paths (binaries must be env-overridable).
   UPDATED skills: check diff DIRECTION - if the repo copy holds content the live copy lacks
   and it is a load-bearing improvement (e.g. a paragraph an upstream rework dropped),
   restore it or reconcile; never silently delete content.
3. Remove from the staged set any eval/benchmark-run artifacts, fixture dirs containing .git
   objects, or *workspace* dirs; those stay out of the repo.
4. Update README.md: one row per skill dir in the alphabetical "Included skills" table
   (trigger-first one-liners); fix coverage gaps for newly synced skills; keep the
   Attribution section accurate.
5. Commit in logical groups with the repo's conventions (type(scope): summary + bullet
   body). Do NOT push, rebase, or touch any branch; no --force anything.
6. If a change is ambiguous, restore the working tree to origin/main (git reset --hard
   origin/main) and finish with "SYNC HELD: <reason>". Otherwise finish "SYNC OK: <n> commits".
PROMPT

PI_OUT_FILE=$(mktemp /tmp/skill-sync-pi.XXXXXX)
"$PI_BIN" --print --no-session --name "daily-skill-sync" "$(cat "$PROMPT_FILE")" >"$PI_OUT_FILE" 2>&1 &
PI_PID=$!
( sleep "$PI_TIMEOUT_S"; kill -9 "$PI_PID" 2>/dev/null || true ) &
WD_PID=$!
wait "$PI_PID" || true
kill "$WD_PID" 2>/dev/null || true
wait "$WD_PID" 2>/dev/null || true
tail -5 "$PI_OUT_FILE" >>"$LOG" 2>/dev/null || true
rm -f "$PROMPT_FILE" "$PI_OUT_FILE"

# Rail 3 — gates again, then push (push is trusted only to this script).
for f in skills/*/SKILL.md; do
  name=$(basename "$(dirname "$f")")
  n=$(awk '/^---$/{c++;next} c==1 && $1=="name:"{print substr($0,7); exit}' "$f")
  [ "$n" = "$name" ] || { log "FAIL: post-review gate broke ($f)"; exit 4; }
done
for d in skills/*/; do
  s=$(basename "$d"); grep -q "\`$s\`" README.md || { log "FAIL: post-review gate: README row missing for $s"; exit 4; }
done
[ -z "$(git status --porcelain | head -1)" ] || log "note: uncommitted residue left by review; pushing committed work only"
AFTER_LOCAL=$(git rev-parse HEAD)
if [ "$BEFORE" != "none" ] && [ "$AFTER_LOCAL" = "$BEFORE" ]; then
  log "review landed no commits; nothing to push"
  exit 0
fi
PUSH_OK=0
for _ in 1 2 3; do
  if git push origin main; then PUSH_OK=1; break; fi
  git fetch origin
  if [ "$(git rev-list --count HEAD..origin/main)" -gt 0 ]; then
    git pull --ff-only origin main || { log "FAIL: origin/main diverged mid-push; commits left local for a human"; exit 5; }
  fi
done
if [ "$PUSH_OK" = 1 ]; then
  PUSHED=$(git rev-parse origin/main)
  log "pushed: $(git log --oneline "$BEFORE".."$PUSHED" | wc -l | tr -d ' ') commits; origin/main at $(git rev-parse --short "$PUSHED")"
else
  log "FAIL: push did not confirm after retries; commits left local for a human"
  exit 5
fi
log "=== daily skill sync end ==="

# Keep the log bounded.
if [ "$(wc -c <"$LOG")" -ge 1048576 ]; then
  tail -c 524288 "$LOG" >"$LOG.tmp" 2>/dev/null && mv "$LOG.tmp" "$LOG"
fi
exit 0