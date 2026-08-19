#!/usr/bin/env bash
# End-to-end test of the escalation loop, in a throwaway git repo.
#   gate.mjs decides ESCALATE  ->  writes ESCALATION.json  ->  Stop hook BLOCKS
#   gate.mjs --resolve         ->  Stop hook stops blocking
# Nothing here touches a real project.
set -u
GATE="$HOME/.claude/skills/pipeline-orchestrator/gate.mjs"
HOOK="$HOME/.claude/hooks/dev-pipeline-gate.sh"

# Preflight. Every assertion below that "passes" does so on output NOT containing "block" — which is
# also what an empty string looks like. So a run where nothing executes at all still scores PASSes.
# That happened: the nightly manifest spawned a bare `bash`, which resolved to WSL's System32
# bash.exe, where node does not exist and HOME=/home/<user>. This script reported "4 passed, 8 failed"
# on a run in which the gate binary was never invoked once, and that mix read as a partial regression
# rather than as an environment that cannot test anything. Refuse to score instead.
command -v node >/dev/null 2>&1 || { echo "ABORT: no node on PATH (uname=$(uname -s), HOME=$HOME) — this environment cannot test the gate; not scoring any assertion"; exit 1; }
[ -f "$GATE" ] || { echo "ABORT: gate.mjs not found at $GATE (HOME=$HOME) — not scoring any assertion"; exit 1; }
[ -f "$HOOK" ] || { echo "ABORT: hook not found at $HOOK (HOME=$HOME) — not scoring any assertion"; exit 1; }

SANDBOX=$(mktemp -d)
pass=0; fail=0
ok()   { echo "  PASS  $1"; pass=$((pass+1)); }
bad()  { echo "  FAIL  $1"; echo "        got: $2"; fail=$((fail+1)); }

# "the hook did NOT block" — asserted so a CRASHED hook cannot score a pass.
# Four assertions here used `case "$out" in *'"decision":"block"'*) bad ;; *) ok ;; esac`, which scores a
# PASS on any output lacking the word "block" — including the empty string a hook that died on a missing
# jq, an unset variable or a bad path produces. The preflight above stops a wholly dead environment from
# scoring, but a hook broken for any other reason still banked four PASSes.
#
# Empty output alone is NOT the discriminator: measured, the real hook prints a {"systemMessage":...}
# line when it declines to block on a dirty repo, and prints NOTHING AT ALL on the stop_hook_active
# bypass — both legitimate, both exit 0. So require the exit code to be 0 as the positive evidence that
# the hook ran and made a decision, and treat a non-zero exit as the failure it is.
not_block() { # $1 = label, $2 = hook stdout, $3 = hook exit code
  case "$2" in
    *'"decision":"block"'*) bad "$1 (hook blocked)" "$2"; return ;;
  esac
  if [ "$3" != 0 ]; then
    bad "$1 (hook exited $3 — it FAILED rather than declined to block)" "${2:-<no output>}"
  else
    ok "$1"
  fi
}

cd "$SANDBOX" || exit 1

echo "== 0) unit tests for the gate decision function"
if unit=$( cd "$HOME/.claude/skills/pipeline-orchestrator" && node --test 2>&1 ); then
  ok "gate.test.mjs unit tests pass"
else
  # Report the runner's own last lines, not a canned "go run it yourself". Discarding this output is
  # the same defect this script exists to catch: a red that names no cause.
  bad "gate.test.mjs unit tests FAILED" "$(printf '%s' "$unit" | tail -5)"
fi

git init -q . 2>/dev/null
git config user.email t@t; git config user.name t
mkdir -p .aid/pipeline
# rounds=5, threshold=9.5 — same shape as the real config
cat > .aid/pipeline/config.json <<'JSON'
{ "max_iterations": { "code_review": 5, "test_review": 5, "phase_gate_reexamine": 5, "visual_qa": 5 },
  "thresholds": { "code_review_pass": 9.5, "test_review_pass": 9.5, "visual_qa_pass": 7,
                  "auto_fail_on_critical_security": true } }
JSON
# 5 of 5 rounds already spent — the exact state that produced a false PASS at 7.9 historically
cat > .aid/pipeline/state.json <<'JSON'
{ "pipeline_status": "running", "current_step": "CODE_REVIEW",
  "iterations": { "code_review": 5, "test_review": 0, "phase_gate_reexamine": 0 } }
JSON
echo "console.log(1)" > app.js   # a changed source file, so the hook has work to consider
# state.json must be the NEWEST write, or the hook's own freshness rule blocks for a reason that has
# nothing to do with escalations — and cases 1 and 6 assert "does not block". They were only passing
# because app.js and state.json landed in the same second; two seconds apart the hook legitimately
# blocks and the baseline reports a failure that is really a test-setup artefact.
sleep 1
touch .aid/pipeline/state.json

echo "== 1) baseline: no escalation -> hook must NOT block"
out=$(printf '{}' | bash "$HOOK" 2>/dev/null); rc=$?
not_block "clean repo does not block" "$out" "$rc"

echo "== 2) gate: 7.9 with 5/5 rounds spent -> ESCALATE (exit 2) and writes ESCALATION.json"
node "$GATE" --step CODE_REVIEW --scores '{"overall":7.9,"security":7}' --root "$SANDBOX" >/dev/null 2>&1
rc=$?
[ "$rc" = 2 ] && ok "exit code 2 (ESCALATE)" || bad "expected exit 2, got $rc" "$rc"
[ -f .aid/pipeline/ESCALATION.json ] && ok "ESCALATION.json written" || bad "no escalation file" "missing"
grep -q '"status": "open"' .aid/pipeline/ESCALATION.json 2>/dev/null \
  && ok "escalation is open" || bad "escalation not open" "$(cat .aid/pipeline/ESCALATION.json 2>/dev/null | head -3)"

echo "== 3) Stop hook must now BLOCK the turn (this is the escalation reaching the human)"
out=$(printf '{}' | bash "$HOOK" 2>/dev/null)
case "$out" in
  *'"decision":"block"'*ESCALATED*) ok "hook blocks with the escalation reason" ;;
  *'"decision":"block"'*)           ok "hook blocks (reason text differs)" ;;
  *)                                bad "hook did NOT block on an open escalation" "$out" ;;
esac

echo "== 4) the loop guard still holds: stop_hook_active must never block (no infinite loop)"
out=$(printf '{"stop_hook_active":true}' | bash "$HOOK" 2>/dev/null); rc=$?
# measured: this path legitimately prints NOTHING and exits 0, which is why not_block keys on the exit
# code rather than on the presence of output
not_block "stop_hook_active bypasses (one interruption per turn)" "$out" "$rc"

echo "== 5) SKIP_PIPELINE_GATE=1 bypasses"
out=$(printf '{}' | SKIP_PIPELINE_GATE=1 bash "$HOOK" 2>/dev/null); rc=$?
not_block "SKIP_PIPELINE_GATE=1 bypasses" "$out" "$rc"

echo "== 6) resolving is the HUMAN's decision -> after --resolve the hook stops blocking"
node "$GATE" --resolve "accepted 7.9 for now; tracked as debt" --root "$SANDBOX" >/dev/null 2>&1
rc=$?
[ "$rc" = 0 ] && ok "--resolve exits 0" || bad "--resolve failed" "$rc"
out=$(printf '{}' | bash "$HOOK" 2>/dev/null); rc=$?
not_block "resolved escalation no longer blocks" "$out" "$rc"

echo "== 7) --check-escalation reports state for scripts"
node "$GATE" --check-escalation --root "$SANDBOX" >/dev/null 2>&1
rc=$?   # capture BEFORE the test: in `[ "$?" = 0 ] && ok || bad "..." "$?"` the second $? is the
        # exit of `[`, so the failure message reported 1 forever instead of the gate's real code.
[ "$rc" = 0 ] && ok "--check-escalation exit 0 when resolved" || bad "--check-escalation wrong exit" "$rc"

echo "== 8) a passing score never writes an escalation"
rm -f .aid/pipeline/ESCALATION.json
node "$GATE" --step CODE_REVIEW --scores '{"overall":9.7}' --root "$SANDBOX" >/dev/null 2>&1
rc=$?
{ [ "$rc" = 0 ] && [ ! -f .aid/pipeline/ESCALATION.json ]; } \
  && ok "9.7 passes and writes no escalation" || bad "9.7 mishandled (exit $rc)" "$rc"

echo
echo "RESULT: $pass passed, $fail failed"
cd /; rm -rf "$SANDBOX" 2>/dev/null
[ "$fail" = 0 ] || exit 1
