#!/usr/bin/env bash
# ─────────────────────────────────────────────────
# dev-pipeline-gate.sh  (ships with AID; registered by the plugin, so it runs in every git repo)
#
# WHY: promoted to ~/.claude/hooks from the kuri trial. A Stop hook that makes the
# "don't finish a turn with broken/unvalidated code" loop deterministic instead of
# relying on the agent to remember. Owner chose repo-wide scope.
#
# Behaviour on Stop:
#   0. Bypass if SKIP_PIPELINE_GATE=1, or if this stop was itself triggered by a
#      hook (stop_hook_active) — the loop guard makes every block a ONE-TIME
#      interruption per turn, never an infinite loop.
#   1. No changed .ts (vs HEAD + untracked) → allow.
#   2. tsc --noEmit on the changed code (per-function in a monorepo, else a single
#      root pass if a root tsconfig exists). Failures → BLOCK with the errors.
#   3. If the repo has .aid/pipeline/  → enforce the /pipeline freshness loop:
#         source newer than the last /pipeline run → BLOCK asking for /pipeline;
#         otherwise → emit a (non-blocking) commit nudge.
#      If the repo has NO .aid/pipeline/ → one-time generic "validate before
#      finishing" nudge (no /pipeline command exists here to point at).
#
# To narrow this to AID projects only, uncomment the marked line below.
# Output protocol: {"decision":"block","reason":..} blocks; {"systemMessage":..}
# just notifies; empty / exit 0 allows the stop.
# ─────────────────────────────────────────────────

input=$(cat 2>/dev/null)
# Loop guard. Whitespace is stripped first: this matched the literal
# '"stop_hook_active":true', so any payload serialized WITH a space after the colon
# slipped straight past the guard and the gate could re-block every turn. A loop
# guard must not depend on the sender's JSON formatting.
_sha_probe=$(printf '%s' "$input" | tr -d ' \t\n\r')
case "$_sha_probe" in *'"stop_hook_active":true'*) exit 0 ;; esac
[ "${SKIP_PIPELINE_GATE:-}" = "1" ] && exit 0

# cwd from the payload is the third fallback: outside a git repo `rev-parse` prints nothing, and
# without this the hook exited before doing anything at all in exactly the directories that have no
# other safety net.
ROOT="${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null)}"
[ -z "$ROOT" ] && ROOT=$(printf '%s' "$input" | python -c 'import json,sys
try: print((json.load(sys.stdin).get("cwd") or ""))
except Exception: print("")' 2>/dev/null)
[ -n "$ROOT" ] && cd "$ROOT" 2>/dev/null || exit 0

# Is git usable HERE? Not a reason to quit — only a choice of where the changed-file list comes from.
# 877 of this gate's recorded events were "skipped — not a git repo": it ran, found no git, and did
# nothing, in the directories least likely to have any other check. The language checks below never
# needed git, only a list of files.
HAVE_GIT=0
if command -v git >/dev/null 2>&1 && git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  HAVE_GIT=1
fi

# ── To restrict the whole gate to AID projects only, uncomment this line: ──
# [ -d "$ROOT/.aid/pipeline" ] || exit 0

# JSON-encode stdin (python preferred; sed fallback).
json_enc() { python -c 'import json,sys;print(json.dumps(sys.stdin.read()))' 2>/dev/null \
  || { printf '"'; sed 's/\\/\\\\/g; s/"/\\"/g' | tr '\n' ' '; printf '"'; }; }

# starthook-6: SHA-256 of a file (sha256sum preferred, shasum -a 256 fallback).
# Echoes the bare hash, or empty if neither tool exists / file unreadable.
sha256_of() {
  if command -v sha256sum >/dev/null 2>&1; then
    sha256sum "$1" 2>/dev/null | cut -d' ' -f1
  elif command -v shasum >/dev/null 2>&1; then
    shasum -a 256 "$1" 2>/dev/null | cut -d' ' -f1
  fi
}

# ── 0b) An OPEN pipeline escalation blocks the turn. ──
# This is what makes "ESCALATE" mean something. The gate used to be prose in the orchestrator skill,
# and an agent could log a sub-threshold score as PASS — which happened twice in this workspace
# (7.9 and 7.6 against a threshold of 8.0), so the gate silently was not one. gate.mjs now decides in
# code and writes ESCALATION.json; this branch makes the decision reach the HUMAN by refusing to end
# the turn quietly. Checked before the "no changed source" early exit, because an escalation is open
# regardless of whether this particular turn touched code.
# Deliberately grep, not node: the block must not depend on a runtime being installed.
ESC="$ROOT/.aid/pipeline/ESCALATION.json"
if [ -f "$ESC" ] && grep -q '"status"[[:space:]]*:[[:space:]]*"open"' "$ESC" 2>/dev/null; then
  esc_why=$(grep -o '"why"[[:space:]]*:[[:space:]]*"[^"]*"' "$ESC" 2>/dev/null | head -1 | sed 's/.*"why"[[:space:]]*:[[:space:]]*"//; s/"$//')
  esc_step=$(grep -o '"step"[[:space:]]*:[[:space:]]*"[^"]*"' "$ESC" 2>/dev/null | head -1 | sed 's/.*"step"[[:space:]]*:[[:space:]]*"//; s/"$//')
  reason="Stop blocked: the pipeline gate ESCALATED and it is UNRESOLVED (step: ${esc_step:-?}). ${esc_why:-below threshold with iterations exhausted}
This is a decision only the human can make. Present it to them and let them choose: (a) keep working to clear the threshold, (b) lower it in .aid/pipeline/config.json, or (c) accept this result. Then record the choice:
  node \"\$HOME/.claude/skills/pipeline-orchestrator/gate.mjs\" --resolve \"<what was decided>\"
Do NOT resolve it on the human's behalf. SKIP_PIPELINE_GATE=1 bypasses this gate entirely."
  printf '{"decision":"block","reason":%s}\n' "$(printf '%s' "$reason" | json_enc)"
  exit 0
fi

# Files this SESSION wrote, read out of the transcript Claude Code hands the hook. The changed-file
# source for a directory git cannot describe.
#
# Only Write/Edit/NotebookEdit count — a Read is not a change. Paths are kept only if they still exist
# and sit inside ROOT, so a file created and later deleted, or edited in some other project during the
# same session, cannot reach the compilers. Fails open (prints nothing) on any parse problem: this runs
# on every Stop in every project, so a bad transcript must cost a check, never the turn.
_edited_this_session() {
  printf '%s' "$input" | python -c '
import json, os, sys
try:
    d = json.load(sys.stdin)
except Exception:
    raise SystemExit(0)
tp = d.get("transcript_path") or ""
if not tp or not os.path.isfile(tp):
    # Second source for the same file. Claude Code names the transcript after the session id under
    # ~/.claude/projects/<slug>/; deriving the slug from a path is fiddly and gets it wrong on
    # worktrees, so glob for the id instead. Belt and braces: if the payload ever stops carrying
    # transcript_path, this keeps working rather than turning the whole check into a silent no-op.
    sid = d.get("session_id") or ""
    home = os.environ.get("USERPROFILE") or os.environ.get("HOME") or ""
    tp = ""
    if sid and home:
        import glob
        hits = glob.glob(os.path.join(home, ".claude", "projects", "*", sid + ".jsonl"))
        if hits:
            tp = hits[0]
    if not tp or not os.path.isfile(tp):
        raise SystemExit(0)
root = os.path.abspath(os.getcwd())
out, seen = [], set()
try:
    with open(tp, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if "file_path" not in line:
                continue
            try:
                entry = json.loads(line)
            except Exception:
                continue
            content = (entry.get("message") or {}).get("content")
            if not isinstance(content, list):
                continue
            for block in content:
                if not isinstance(block, dict) or block.get("type") != "tool_use":
                    continue
                if block.get("name") not in ("Write", "Edit", "NotebookEdit"):
                    continue
                p = (block.get("input") or {}).get("file_path") or ""
                if not p or p in seen:
                    continue
                seen.add(p)
                try:
                    ap = os.path.abspath(p)
                    if os.path.isfile(ap) and os.path.commonpath([ap, root]) == root:
                        out.append(os.path.relpath(ap, root).replace(chr(92), "/"))
                except Exception:
                    continue
except Exception:
    raise SystemExit(0)
print("\n".join(out))
' 2>/dev/null
}

# All changed source files (tracked-modified + untracked), excluding build/vendor artifacts.
_all_changed() {
  if [ "$HAVE_GIT" = "1" ]; then
    { git diff --name-only 2>/dev/null; git ls-files --others --exclude-standard 2>/dev/null; }
  else
    _edited_this_session
  fi \
  | grep -vE '/dist/|/node_modules/|/vendor/|/build/|/\.next/|/__pycache__/|/target/|/\.gradle/|/out/' \
  | sort -u
}

changed_ts=$(_all_changed | grep -E '\.ts$'  | grep -vE '\.d\.ts$')
changed_js=$(_all_changed | grep -E '\.js$'  | grep -vE '\.min\.js$')
changed_py=$(_all_changed | grep -E '\.py$')
changed_go=$(_all_changed | grep -E '\.go$')
changed_rs=$(_all_changed | grep -E '\.rs$')
changed_java=$(_all_changed | grep -E '\.java$')

# UI files for the browser-evidence check (6.5): style/markup types the language checks
# below can't see, plus anything under a public/ dir.
changed_ui=$(_all_changed | grep -E '\.(tsx|jsx|vue|svelte|css|scss)$|(^|/)public/')

# Any changed source at all? (UI files count: the freshness/commit summary below covers them too)
changed_all=$(printf '%s\n%s\n%s\n%s\n%s\n%s\n%s\n' \
  "$changed_ts" "$changed_js" "$changed_py" "$changed_go" "$changed_rs" "$changed_java" "$changed_ui" \
  | grep -v '^$' | sort -u)
[ -z "$changed_all" ] && exit 0

# ── 1) TypeScript — tsc --noEmit ──
# WHY the probe: `out=$(npx tsc --noEmit 2>&1)` captures ANY output, so a shell where
# node is not on PATH produced "exec: node: not found" and the gate blocked the turn
# reporting "tsc failed on changed TypeScript" — a type error that did not exist.
# Tool availability is a distinct state from tool failure; never infer one from the other.
errs=""
ran_tsc=0
tsc_runnable=0
if [ -n "$changed_ts" ] && npx tsc --version >/dev/null 2>&1; then
  tsc_runnable=1
fi
if [ -n "$changed_ts" ] && [ "$tsc_runnable" = 1 ]; then
  funcs=$(printf '%s\n' "$changed_ts" | grep -oE '^functions/[^/]+' | sort -u | sed 's#functions/##')
  for f in $funcs; do
    [ -f "functions/$f/tsconfig.json" ] || continue
    ran_tsc=1
    out=$(cd "functions/$f" && npx tsc --noEmit 2>&1)
    [ -n "$out" ] && errs="$errs [$f] $(printf '%s' "$out" | head -6 | tr '\n' ' ')"
  done
  if [ "$ran_tsc" = 0 ] && [ -f "tsconfig.json" ]; then
    out=$(npx tsc --noEmit 2>&1)
    [ -n "$out" ] && errs="$errs $(printf '%s' "$out" | head -8 | tr '\n' ' ')"
    ran_tsc=1
  fi
  if [ -n "$errs" ]; then
    reason="Stop blocked: tsc --noEmit failed on changed TypeScript.$errs  Fix the type errors before finishing (or set SKIP_PIPELINE_GATE=1)."
    printf '{"decision":"block","reason":%s}\n' "$(printf '%s' "$reason" | json_enc)"
    exit 0
  fi
fi
if [ "$ran_tsc" = 1 ]; then
  tsc_status="tsc --noEmit clean"
elif [ -n "$changed_ts" ] && [ "$tsc_runnable" = 0 ]; then
  # Stated, not silent: the turn is NOT blocked, but the human must know the type
  # check did not actually run rather than assuming a clean pass.
  tsc_status="WARN: tsc NOT RUN (node/typescript not runnable from this shell)"
elif [ -n "$changed_ts" ]; then
  tsc_status="WARN: tsc SKIPPED (no applicable tsconfig.json found)"
else
  tsc_status="n/a"
fi

# ── 2) JavaScript — node --check (syntax only; skipped if node absent) ──
if [ -n "$changed_js" ] && command -v node >/dev/null 2>&1; then
  js_errs=""
  while IFS= read -r f; do
    [ -f "$f" ] || continue
    out=$(node --check "$f" 2>&1)
    [ -n "$out" ] && js_errs="$js_errs [$f] $(printf '%s' "$out" | head -4 | tr '\n' ' ')"
  done <<< "$changed_js"
  if [ -n "$js_errs" ]; then
    reason="Stop blocked: node --check syntax error in changed JavaScript.$js_errs  Fix before finishing (or set SKIP_PIPELINE_GATE=1)."
    printf '{"decision":"block","reason":%s}\n' "$(printf '%s' "$reason" | json_enc)"
    exit 0
  fi
fi

# ── 3) Python — py_compile syntax check + mypy if available ──
if [ -n "$changed_py" ] && command -v python >/dev/null 2>&1; then
  py_errs=""
  while IFS= read -r f; do
    [ -f "$f" ] || continue
    out=$(python -m py_compile "$f" 2>&1)
    [ -n "$out" ] && py_errs="$py_errs [$f] $(printf '%s' "$out" | head -4 | tr '\n' ' ')"
  done <<< "$changed_py"
  if [ -n "$py_errs" ]; then
    reason="Stop blocked: Python syntax error in changed files.$py_errs  Fix before finishing (or set SKIP_PIPELINE_GATE=1)."
    printf '{"decision":"block","reason":%s}\n' "$(printf '%s' "$reason" | json_enc)"
    exit 0
  fi
  # mypy type-check (advisory block only if mypy is installed)
  if command -v mypy >/dev/null 2>&1; then
    mypy_out=$(printf '%s\n' "$changed_py" | xargs mypy --ignore-missing-imports 2>&1)
    if echo "$mypy_out" | grep -qE '^.*error:'; then
      reason="Stop blocked: mypy type errors in changed Python. $(printf '%s' "$mypy_out" | grep 'error:' | head -8 | tr '\n' ' ')  Fix or set SKIP_PIPELINE_GATE=1."
      printf '{"decision":"block","reason":%s}\n' "$(printf '%s' "$reason" | json_enc)"
      exit 0
    fi
  fi
fi

# ── 4) Go — go vet (skipped if go absent or no go.mod) ──
if [ -n "$changed_go" ] && command -v go >/dev/null 2>&1 && [ -f "go.mod" ]; then
  go_out=$(go vet ./... 2>&1)
  if [ -n "$go_out" ]; then
    reason="Stop blocked: go vet found issues in changed Go files. $(printf '%s' "$go_out" | head -8 | tr '\n' ' ')  Fix before finishing (or set SKIP_PIPELINE_GATE=1)."
    printf '{"decision":"block","reason":%s}\n' "$(printf '%s' "$reason" | json_enc)"
    exit 0
  fi
fi

# ── 5) Rust — cargo check (skipped if cargo absent or no Cargo.toml) ──
if [ -n "$changed_rs" ] && command -v cargo >/dev/null 2>&1 && [ -f "Cargo.toml" ]; then
  rs_out=$(cargo check 2>&1)
  if [ $? -ne 0 ]; then
    reason="Stop blocked: cargo check failed on changed Rust files. $(printf '%s' "$rs_out" | grep '^error' | head -6 | tr '\n' ' ')  Fix before finishing (or set SKIP_PIPELINE_GATE=1)."
    printf '{"decision":"block","reason":%s}\n' "$(printf '%s' "$reason" | json_enc)"
    exit 0
  fi
fi

# ── 6) Java — javac syntax check (skipped if javac absent) ──
if [ -n "$changed_java" ] && command -v javac >/dev/null 2>&1; then
  java_errs=""
  while IFS= read -r f; do
    [ -f "$f" ] || continue
    out=$(javac -proc:none "$f" 2>&1)
    [ $? -ne 0 ] && java_errs="$java_errs [$f] $(printf '%s' "$out" | head -4 | tr '\n' ' ')"
  done <<< "$changed_java"
  if [ -n "$java_errs" ]; then
    reason="Stop blocked: javac compile error in changed Java files.$java_errs  Fix before finishing (or set SKIP_PIPELINE_GATE=1)."
    printf '{"decision":"block","reason":%s}\n' "$(printf '%s' "$reason" | json_enc)"
    exit 0
  fi
fi

# ── 6.5) UI changes need browser evidence (the "Avoid buggy code" rule, mechanized) ──
# A UI file changed this turn requires proof the feature ran in a real browser: a
# .ui-verified marker (touched after a browser check) newer than the newest changed UI
# file. Own bypass var on purpose — SKIP_PIPELINE_GATE=1 silences the WHOLE gate, and a
# shared switch would let one bypass hide the other's reason.
if [ "${SKIP_UI_GATE:-}" != "1" ]; then
  if [ -n "$changed_ui" ]; then
    newest_ui=0
    while IFS= read -r f; do
      [ -f "$f" ] || continue
      m=$(stat -c %Y "$f" 2>/dev/null || echo 0)
      [ "$m" -gt "$newest_ui" ] && newest_ui=$m
    done <<< "$changed_ui"
    marker_m=$([ -f ".ui-verified" ] && stat -c %Y ".ui-verified" 2>/dev/null || echo 0)
    if [ "$newest_ui" -gt "$marker_m" ]; then
      ui_files=$(printf '%s\n' "$changed_ui" | head -6 | sed 's/^/  - /')
      reason="Stop blocked: UI file(s) changed with no browser evidence since the change:
$ui_files
Per the Avoid-buggy-code rule: run the feature in a real browser (dev server up, golden path + one edge case), then \`touch .ui-verified\` in the repo root and finish. If the UI is deliberately untested, SAY SO explicitly in your reply and set SKIP_UI_GATE=1."
      printf '{"decision":"block","reason":%s}\n' "$(printf '%s' "$reason" | json_enc)"
      exit 0
    fi
  fi
fi

# newest mtime among all changed files (for the pipeline freshness check).
newest=0
while IFS= read -r file; do
  [ -f "$file" ] || continue
  m=$(stat -c %Y "$file" 2>/dev/null || echo 0)
  [ "$m" -gt "$newest" ] && newest=$m
done <<< "$changed_all"
count=$(printf '%s\n' "$changed_all" | grep -c .)
files=$(printf '%s\n' "$changed_all" | head -10 | sed 's/^/  - /')

# ── 2) AID pipeline projects: enforce the /pipeline loop ──
if [ -d ".aid/pipeline" ]; then
  # starthook-6: detect mid-run tampering of the frozen brief.md.
  # First sight → record SHA-256 sidecar; later turns → warn loudly if it drifts.
  brief_warn=""
  brief=$(ls .aid/pipeline/*/brief.md 2>/dev/null | head -1)
  if [ -n "$brief" ] && [ -f "$brief" ]; then
    sidecar="$(dirname "$brief")/brief.sha256"
    cur_hash=$(sha256_of "$brief")
    if [ -n "$cur_hash" ]; then
      if [ -f "$sidecar" ]; then
        rec_hash=$(cut -d' ' -f1 < "$sidecar" 2>/dev/null)
        if [ -n "$rec_hash" ] && [ "$rec_hash" != "$cur_hash" ]; then
          brief_warn="*** WARNING: $brief was MODIFIED mid-run — the frozen intent no longer matches the hash recorded at $sidecar (was $rec_hash, now $cur_hash). The pipeline brief is supposed to be immutable once frozen; re-confirm this change was intended. ***
"
        fi
      else
        printf '%s\n' "$cur_hash" > "$sidecar" 2>/dev/null
      fi
    fi
  fi

  state=".aid/pipeline/state.json"
  state_m=$([ -f "$state" ] && stat -c %Y "$state" 2>/dev/null || echo 0)
  if [ "$newest" -gt "$state_m" ]; then
    # Approved 2026-07-28: block only while a pipeline run is actually in flight.
    # A completed/absent pipeline must not retro-block later sessions — that
    # produced 30 false blocks (benign post-AR-restore mtimes, ordinary edits
    # after a finished pipeline).
    if grep -q '"pipeline_status": *"running"' "$state" 2>/dev/null; then
      reason="${brief_warn}Stop blocked: a source file is newer than .aid/pipeline/state.json while a pipeline run is ACTIVE, so changes look unvalidated. Run /pipeline (CODE_REVIEW → TDD → TEST_REVIEW) to validate, then finish. NOTE: this can also be a benign post-AR-restore state — it self-clears once /pipeline writes state.json last. SKIP_PIPELINE_GATE=1 to bypass."
      printf '{"decision":"block","reason":%s}\n' "$(printf '%s' "$reason" | json_enc)"
      exit 0
    fi
    msg="${brief_warn}dev-pipeline-gate: $count source file(s) newer than the last (non-running) pipeline state - checks passed ($tsc_status); validate/commit at your own pace."
    printf '{"systemMessage":%s}\n' "$(printf '%s' "$msg" | json_enc)"
    exit 0
  fi
  if [ -f "scripts/commit-migration.sh" ]; then
    task=$(grep -o '"task_id"[^,]*' "$state" 2>/dev/null | head -1 | sed 's/.*: *"//; s/".*//')
    [ -z "$task" ] && task="task"
    msg="${brief_warn}Validated: $count file(s) ready to commit (NOT committed - your call). Review, then run:
  bash scripts/commit-migration.sh \"$task: <summary>\"
Changed:
$files"
  else
    msg="${brief_warn}Validated: $tsc_status + /pipeline fresh for $count changed file(s) (NOT committed - your call). Review the diff, then commit yourself.
Changed:
$files"
  fi
  printf '{"systemMessage":%s}\n' "$(printf '%s' "$msg" | json_enc)"
  exit 0
fi

# ── 7) Non-AID repo: everything PASSED → notify, never block. ──
# Approved 2026-07-28: this branch produced 216 of 267 recorded blocks (81%)
# while reporting "all language checks passed" — a review nudge implemented as a
# block, firing on ANY uncommitted file (including prior sessions' work), which
# interrupted even read-only turns. Real failures (tsc/mypy/syntax/vet/cargo/javac)
# still hard-block above; a clean pass is now a non-blocking notice.
msg="dev-pipeline-gate: $count source file(s) changed, all language checks passed (TS: $tsc_status). NOT committed - review and commit yourself (see the dashboard's Start the Day view).
Changed:
$files"
printf '{"systemMessage":%s}\n' "$(printf '%s' "$msg" | json_enc)"
exit 0
