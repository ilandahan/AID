#!/usr/bin/env bash
# verify-run.sh <project-dir>
# Post-run checker for the auto-triggered AID pipeline. Inspects on-disk artifacts
# and reports PASS/WARN/FAIL per expectation. Read-only; never mutates anything.
# Usage:  bash verify-run.sh /path/to/your/project
set -u
ROOT="${1:-$(pwd)}"
P="$ROOT/.aid/pipeline"
pass=0; warn=0; fail=0
ok(){   printf '  PASS  %s\n' "$1"; pass=$((pass+1)); }
wn(){   printf '  WARN  %s\n' "$1"; warn=$((warn+1)); }
no(){   printf '  FAIL  %s\n' "$1"; fail=$((fail+1)); }

echo "Verifying pipeline run in: $ROOT"
echo

echo "[1] Task Brief frozen (compaction-proof intent)"
brief=$(ls "$P"/*/brief.md 2>/dev/null | head -1)
if [ -n "$brief" ]; then
  ok "brief.md exists: ${brief#$ROOT/}"
  grep -q "ORIGINAL_REQUEST" "$brief" && ok "has ORIGINAL_REQUEST section" || no "brief.md missing ORIGINAL_REQUEST"
  grep -q "STATED_WHY"       "$brief" && ok "has STATED_WHY section"       || no "brief.md missing STATED_WHY"
  grep -qi "frozen_at"       "$brief" && ok "has frozen_at timestamp"       || wn "brief.md missing frozen_at"
else
  no "no .aid/pipeline/*/brief.md — intent was NOT frozen (AR-3 would escalate)"
fi
echo

echo "[2] state.json visited the AR stages"
state="$P/state.json"
if [ -f "$state" ]; then
  ok "state.json exists"
  for step in AR_DESIGN AR_FUNCTION AR_ACCEPTANCE; do
    if grep -q "\"$step\"" "$state"; then ok "step_history/summaries mention $step"
    else wn "$step not found in state.json (stage may not have been reached yet)"; fi
  done
else
  no "no .aid/pipeline/state.json — pipeline never initialized"
fi
echo

echo "[3] Autoresearch experiment logs"
tsv=$(ls "$P"/autoresearch/*/results.tsv 2>/dev/null | head -1)
if [ -n "$tsv" ]; then ok "results.tsv exists: ${tsv#$ROOT/} ($(($(wc -l < "$tsv")-1)) iteration rows)"
else wn "no autoresearch/*/results.tsv (AR loops may not have logged, or ran 0 iters)"; fi
echo

echo "[4] Caps respected (counters <= configured maxima)"
if [ -f "$state" ] && command -v python >/dev/null 2>&1; then
  python - "$state" "$ROOT/.aid/pipeline/config.json" <<'PY'
import json,sys
st=json.load(open(sys.argv[1]))
try: cfg=json.load(open(sys.argv[2]))
except Exception: cfg={}
it=st.get("iterations",{}); mx=cfg.get("max_iterations",{})
checks=[("code_review",2),("test_review",2),("phase_gate_reexamine",2),("test_fix",2)]
bad=0
for k,d in checks:
    cap=mx.get(k,d); v=it.get(k,0)
    if v>cap: print("  FAIL  %s=%s exceeds cap %s"%(k,v,cap)); bad+=1
    else:     print("  PASS  %s=%s within cap %s"%(k,v,cap))
ar=(cfg.get("autoresearch") or {})
rounds=it.get("ar_acceptance_rounds",0); rcap=(ar.get("ar_acceptance") or {}).get("max_acceptance_rounds",2)
print(("  FAIL  " if rounds>rcap else "  PASS  ")+"ar_acceptance_rounds=%s cap %s"%(rounds,rcap))
PY
else
  wn "cannot check caps (state.json or python missing)"
fi
echo

echo "[5] Snapshot/restore integrity"
snapdir=$(ls -d "$P"/autoresearch/*/snapshots 2>/dev/null | head -1)
if [ -z "$snapdir" ] || [ ! -d "$snapdir" ]; then
  no "no autoresearch/*/snapshots dir — cannot verify snapshot/restore integrity"
else
  ok "snapshots dir exists: ${snapdir#$ROOT/}"
  baseline=$(ls -d "$snapdir"/000-baseline-* 2>/dev/null | head -1)
  if [ -z "$baseline" ] || [ ! -r "$baseline" ]; then
    no "no readable 000-baseline-* snapshot under ${snapdir#$ROOT/}"
  else
    ok "baseline snapshot present: $(basename "$baseline")"
    # Structural integrity: every pre-edit snapshot tag referenced in results.tsv must still
    # exist on disk (catches snapshots deleted/corrupted under us). WARN, not FAIL, since the
    # exact tag-to-file mapping is per-pass.
    if [ -n "${tsv:-}" ] && [ -r "$tsv" ]; then
      missing=0; refs=0
      while IFS= read -r tag; do
        [ -z "$tag" ] && continue
        [ "$tag" = "-" ] && continue
        refs=$((refs+1))
        if [ -z "$(ls -d "$snapdir/$tag" "$snapdir/$tag"* 2>/dev/null | head -1)" ]; then
          wn "results.tsv references a snapshot not found on disk: $tag"; missing=$((missing+1))
        fi
      done < <(awk -F'\t' 'NR>1 {print $(NF-1)}' "$tsv")
      [ "$refs" -gt 0 ] && [ "$missing" -eq 0 ] && ok "all $refs referenced pre-edit snapshot(s) present"
    fi
    # Keep semantics (program.ar-*.md): a KEPT edit leaves its POST-edit source on disk and
    # records only the PRE-edit snapshot, so on-disk MUST differ from any recorded snapshot —
    # diffing a kept run against its snapshot would FAIL on every correct run. The one disk-vs-
    # snapshot equality we CAN assert is the nothing-kept case: a full revert leaves on-disk
    # == baseline.
    kept_rows=0
    if [ -n "${tsv:-}" ] && [ -r "$tsv" ]; then
      kept_rows=$(awk -F'\t' 'NR>1 && $(NF-2)=="kept"' "$tsv" 2>/dev/null | wc -l | tr -d ' ')
    fi
    if [ "${kept_rows:-0}" -eq 0 ]; then
      if [ -d "$baseline" ]; then
        mism=0; checked=0
        while IFS= read -r snapf; do
          [ -f "$snapf" ] || continue
          rel="${snapf#$baseline/}"; cur="$ROOT/$rel"; checked=$((checked+1))
          if [ ! -r "$cur" ]; then
            no "mutable file missing on disk vs baseline: $rel"; mism=$((mism+1))
          elif ! diff -q "$snapf" "$cur" >/dev/null 2>&1; then
            no "nothing kept, yet on-disk differs from baseline (revert incomplete): $rel"; mism=$((mism+1))
          fi
        done < <(find "$baseline" -type f 2>/dev/null)
        [ "$checked" -gt 0 ] && [ "$mism" -eq 0 ] && ok "nothing kept: all $checked file(s) match baseline (clean full revert)"
        [ "$checked" -eq 0 ] && wn "baseline snapshot captured no files: $(basename "$baseline")"
      else
        wn "baseline snapshot is not a directory; skipping per-file revert check"
      fi
    else
      ok "$kept_rows kept iteration(s): on-disk holds best-kept post-edit source — no post-edit snapshot exists to diff (structural check only)"
    fi
  fi
fi
echo

echo "[6] Loop status scan (no halt hiding behind a green total)"
if [ -n "${tsv:-}" ] && [ -r "$tsv" ]; then
  # status is the 3rd-from-last column ($(NF-2)) on EVERY pass (status snapshot utc).
  # A halted/corrupted state (restore-failed) or a scoring crash MUST FAIL, never WARN —
  # otherwise a partial/aborted pass can pass review behind an otherwise-green run.
  halted=$(awk -F'\t' 'NR>1 && ($(NF-2)=="restore-failed" || $(NF-2)=="crash" || $(NF-2)=="state-write-failed" || $(NF-2)=="rubric-tampered") {c[$(NF-2)]++} END {for (k in c) printf "%s=%d ", k, c[k]}' "$tsv" 2>/dev/null)
  if [ -n "$halted" ]; then
    no "results.tsv contains halted/corrupted iteration(s): ${halted% } — pass did not complete cleanly"
  else
    ok "no halt/tamper rows (restore-failed/crash/state-write-failed/rubric-tampered) in results.tsv"
  fi
else
  wn "no readable results.tsv — cannot scan loop status"
fi
echo

echo "[7] TSV schema integrity (min columns, unique iter, numeric score, valid status slot)"
if [ -n "${tsv:-}" ] && [ -r "$tsv" ]; then
  # NOTE: per-pass rows legitimately differ in width (AR-1 = 10 cols, AR-2 = 9, AR-3 = 6) and may
  # coexist in one results.tsv (program.ar-acceptance.md), so do NOT assert a uniform column count.
  # The load-bearing invariant is right-anchored: the last three columns are always status snapshot utc.
  schema=$(awk -F'\t' '
    BEGIN { split("baseline kept reverted reverted-redtest crash restore-failed state-write-failed rubric-tampered done redevelop escalated", a, " "); for (i in a) st[a[i]]=1 }
    NR==1 { next }
    NF==0 { next }
    {
      rows++
      if (NF<6) { printf "COLS row %d has only %d columns (min 6: iter ... status snapshot utc)\n", NR, NF; bad++ }
      if ($1 in seen) { printf "ITER duplicate iter id %s (row %d)\n", $1, NR; bad++ }
      seen[$1]=1
      if ($2 !~ /^-?[0-9]+(\.[0-9]+)?$/) { printf "SCORE column $2=%s (row %d) does not parse as a number\n", $2, NR; bad++ }
      if (NF>=3 && !($(NF-2) in st)) { printf "STATUS column (NF-2)=%s (row %d) not a known status (column misalignment?)\n", $(NF-2), NR; bad++ }
    }
    END { if (rows==0) print "EMPTY no data rows" }
  ' "$tsv" 2>/dev/null)
  if [ -z "$schema" ]; then
    ok "results.tsv schema clean (>=6 cols, unique iter, numeric \$2, valid status slot)"
  elif [ "$schema" = "EMPTY no data rows" ]; then
    wn "results.tsv has no data rows to validate"
  else
    while IFS= read -r line; do
      [ -z "$line" ] && continue
      no "results.tsv schema: ${line#* }"
    done <<< "$schema"
  fi
else
  wn "no readable results.tsv — cannot validate TSV schema"
fi
echo

echo "[8] Rubric fingerprint (harness-tamper detection)"
sha_cmd=""
if command -v sha256sum >/dev/null 2>&1; then sha_cmd="sha256sum"
elif command -v shasum >/dev/null 2>&1; then sha_cmd="shasum -a 256"; fi
if [ ! -f "$state" ]; then
  wn "no state.json — cannot check rubric fingerprint"
elif ! command -v python >/dev/null 2>&1; then
  wn "python missing — cannot read recorded rubric_sha256 from state.json"
elif [ -z "$sha_cmd" ]; then
  wn "neither sha256sum nor shasum available — rubric fingerprint check skipped (tooling only)"
else
  # For each AR mode that recorded a rubric_sha256 for a passing run, recompute the SHA-256 over
  # the active criteria YAML (+ reflection-agent AGENT-PROMPT.md if locatable) and FAIL on drift.
  recorded=$(python - "$state" <<'PY'
import json,sys
try: st=json.load(open(sys.argv[1]))
except Exception: sys.exit(0)
ar=(st.get("autoresearch") or {})
for mode,m in (ar.items() if isinstance(ar,dict) else []):
    if isinstance(m,dict):
        h=m.get("rubric_sha256")
        c=m.get("criteria") or m.get("criteria_path") or ""
        if h: print("%s\t%s\t%s"%(mode,h,c))
PY
)
  if [ -z "$recorded" ]; then
    wn "state.json records no rubric_sha256 — nothing to verify (fingerprint not yet captured)"
  else
    # Locate the reflection-agent prompt (workspace-level, never a user-level path).
    agent_prompt=""
    for cand in "$ROOT/.claude/agents/reflection-agent.md"; do
      [ -r "$cand" ] && { agent_prompt="$cand"; break; }
    done
    # Workspace-level criteria dir (per the note above: never a user-level path).
    cdir="$ROOT/.claude/skills/reflection/criteria"
    while IFS=$'\t' read -r mode rhash cpath; do
      [ -z "$rhash" ] && continue
      yaml=""
      if [ -n "$cpath" ] && [ -r "$ROOT/$cpath" ]; then yaml="$ROOT/$cpath"
      elif [ -n "$cpath" ] && [ -r "$cpath" ]; then yaml="$cpath"
      else
        case "$mode" in
          *design*)   yaml=$(ls "$cdir"/*design*.yaml 2>/dev/null | head -1) ;;
          *function*) yaml=$(ls "$cdir"/*function*.yaml 2>/dev/null | head -1) ;;
          *)          yaml=$(ls "$cdir"/*"$mode"*.yaml 2>/dev/null | head -1) ;;
        esac
      fi
      if [ -z "$yaml" ] || [ ! -r "$yaml" ]; then
        wn "$mode: recorded rubric_sha256 but active criteria YAML not locatable — cannot recompute"
        continue
      fi
      if [ -n "$agent_prompt" ]; then
        cur=$(cat "$yaml" "$agent_prompt" 2>/dev/null | $sha_cmd | awk '{print $1}')
      else
        cur=$(cat "$yaml" 2>/dev/null | $sha_cmd | awk '{print $1}')
      fi
      if [ "$cur" = "$rhash" ]; then
        ok "$mode: rubric fingerprint matches recorded rubric_sha256 (harness unchanged)"
      else
        no "$mode: rubric fingerprint MISMATCH — on-disk harness $cur != recorded $rhash (criteria/agent-prompt drift; scores incomparable)"
      fi
    done <<< "$recorded"
  fi
fi
echo

echo "Summary: $pass PASS / $warn WARN / $fail FAIL"
[ "$fail" -eq 0 ] && echo "=> Pipeline artifacts look correct." || echo "=> Some expectations not met (see FAIL lines)."
