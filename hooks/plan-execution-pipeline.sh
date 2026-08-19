#!/usr/bin/env bash
# ─────────────────────────────────────────────────
# plan-execution-pipeline.sh  (ships with AID — PostToolUse on ExitPlanMode)
#
# WHY: the AID pipeline (DEVELOP → CODE_REVIEW → AR_DESIGN → TDD → AR_FUNCTION →
# VISUAL_QA → TEST_REVIEW → PHASE_GATE → AR_ACCEPTANCE) otherwise starts ONLY when
# the user types /pipeline. This makes it ALSO run automatically whenever an approved
# plan begins execution. ExitPlanMode (plan approved → implementation begins) is the
# deterministic signal, and it fires while the original request + WHY + the approved
# plan are still in context — the correct moment to FREEZE THE TASK BRIEF.
#
# Behaviour on ExitPlanMode:
#   0. Bypass if SKIP_PIPELINE_GATE=1 (same switch as dev-pipeline-gate.sh).
#   1. AID project (has .aid/) → inject an instruction: initialize the pipeline,
#      freeze .aid/pipeline/<task>/brief.md from the verbatim original request + WHY
#      + the approved plan, then drive ALL implementation through the orchestrator.
#   2. Non-AID project → inject a lighter "review before finishing" instruction.
# The Stop hook (dev-pipeline-gate.sh) remains the turn-end safety net.
#
# Output protocol (PostToolUse): hookSpecificOutput.additionalContext injects the
# instruction into the model's context; systemMessage is shown to the user.
# ─────────────────────────────────────────────────

input=$(cat 2>/dev/null)
# Only act on ExitPlanMode (the settings matcher should already scope this, but guard).
case "$input" in *'"ExitPlanMode"'*) ;; *) exit 0 ;; esac

# Bypass switch — but NOT silently. On an ExitPlanMode we would otherwise act on, announce the
# skip so a stale SKIP_PIPELINE_GATE env var can't quietly disable brief-freeze + pipeline init
# on a later implementation plan. (Static message, no control chars — safe to emit literally.)
if [ "${SKIP_PIPELINE_GATE:-}" = "1" ]; then
  printf '%s\n' '{"systemMessage":"plan-execution-pipeline: SKIP_PIPELINE_GATE=1 set — pipeline gate bypassed; brief.md NOT frozen and pipeline NOT initialized. Unset SKIP_PIPELINE_GATE to re-enable."}'
  exit 0
fi

# ── Payload extraction: ONE node process, UTF-8 in and UTF-8 out ─────────────────────────────────
# WHY NODE AND NOT PYTHON (changed 2026-08-05 after this hook was found to have saved 0 plans across
# 34 approvals): python on Windows picks its stdio codec from the LOCALE, so the previous version was
# broken in two different ways at once and neither one raised.
#   * With python on PATH: stdin arrived as UTF-8 and was decoded as cp1252, then re-encoded as UTF-8.
#     Measured — "→" (E2 86 92) came out as "â†’" (C3 A2 E2 80 A0 ...). No exception, exit 0, and the
#     plan was POSTed and stored CORRUPTED, along with the copy injected into the model's context.
#   * Without python on PATH: the extraction produced an empty string, the `-n` guard below skipped
#     the POST entirely, and the hook fell through to its mtime guess. This is what production was
#     doing — 25 successful fires, 0 saved plans.
# Node reads and writes UTF-8 regardless of locale, and it is guaranteed present wherever Claude Code
# runs. jq is gone too: the jq on PATH here is a broken npm shim that prints a node stack trace.
#
# Everything crosses via FILES, never argv: MSYS path-translates argv and turns "C:\a\b" into "C:ab",
# which silently breaks project identity so a prediction can never resolve.
_hk_dir=$(mktemp -d 2>/dev/null || echo "${TMPDIR:-/tmp}/cc-plan-hook.$$")
mkdir -p "$_hk_dir" 2>/dev/null
_hk_fail=""
if command -v node >/dev/null 2>&1; then
  # Buffer in, Buffer out. Writes plan.txt, cwd.txt and payload.json — the API body is assembled here
  # so the plan text never has to survive a shell variable round-trip.
  printf '%s' "$input" | node -e '
const fs = require("fs"), path = require("path");
const dir = process.argv[1];
let buf = [];
process.stdin.on("data", (c) => buf.push(c));
process.stdin.on("end", () => {
  let d = {};
  try { d = JSON.parse(Buffer.concat(buf).toString("utf8")); } catch { /* leave empty */ }
  // Root cause (found 2026-08-09 via a live captured payload, session 68f877a4): the ExitPlanMode
  // tool description says it does NOT take the plan content as a parameter -- it reads the plan
  // from the file it wrote -- so a live-captured real hook invocation had tool_input: {} and the
  // plan under tool_response.plan / tool_response.filePath. tool_response is read FIRST for that
  // reason. tool_input is read as a fallback, not removed: the transcript logs under
  // ~/.claude/projects/**/*.jsonl show the ExitPlanMode tool_use block input field populated with
  // plan/planFilePath in every recorded call, which may be a display-layer reconstruction rather
  // than the literal hook payload, or may reflect a shape this hook has not yet been captured
  // receiving live. Reading both, tool_response first, means the fix does not depend on which
  // theory is correct.
  const tr = d.tool_response || {};
  const ti = d.tool_input || {};
  const plan = typeof tr.plan === "string" && tr.plan ? tr.plan : typeof ti.plan === "string" ? ti.plan : "";
  fs.writeFileSync(path.join(dir, "plan.txt"), plan, "utf8");
  fs.writeFileSync(path.join(dir, "cwd.txt"), d.cwd || "", "utf8");
  fs.writeFileSync(path.join(dir, "payload.json"), JSON.stringify({
    content: plan,
    project: d.cwd || "",
    session_id: d.session_id || "",
    // filePath is the MUTABLE origin of the plan (tool_response first, same reasoning as plan above).
    source_path: typeof tr.filePath === "string" && tr.filePath ? tr.filePath : typeof ti.planFilePath === "string" ? ti.planFilePath : "",
    // Provenance, recorded rather than inferred: this is how "has the hook ever actually saved a plan"
    // becomes a query instead of a guess. The store once held two rows believed to be hook output that
    // were manual API calls, and the hook had in fact never produced one.
    written_by: "exitplanmode-hook",
  }), "utf8");
});' "$_hk_dir" 2>/dev/null
fi
# `cat`, not $(node ...): command substitution is byte-transparent in bash, but only if the bytes get
# there via a file. Reading them back here keeps the plan exact.
plan_text=""
[ -f "$_hk_dir/plan.txt" ] && plan_text=$(cat "$_hk_dir/plan.txt")
cwd=""
[ -f "$_hk_dir/cwd.txt" ] && cwd=$(cat "$_hk_dir/cwd.txt")
[ -f "$_hk_dir/payload.json" ] || _hk_fail="could not read the ExitPlanMode payload (node unavailable or payload unparseable)"
# An EMPTY plan is the same outcome as a failed parse — no snapshot happens — and it must announce
# itself for exactly the reason this rewrite exists. The node step falls back to `{}` on malformed
# JSON, which yields an empty plan and would otherwise skip the POST in total silence: the original
# defect wearing new clothes.
if [ -z "$plan_text" ] && [ -z "$_hk_fail" ]; then
  _hk_fail="the ExitPlanMode payload carried no plan text"
fi
ROOT="${cwd:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"

# Claim the session's Loop 1 kickoff. loop1-implicit-kickoff.sh (UserPromptSubmit) starts the same
# loop for implementation prompts that never went through plan mode, and both write this marker — so
# whichever entrance fires first wins and an approved plan cannot start the pipeline twice. Plan
# approval is the MORE specific signal, but it necessarily arrives second (the prompt came first), so
# it claims the marker here rather than checking it.
_l1_home="${USERPROFILE:-$HOME}"
_l1_sid=$(printf '%s' "$input" | node -e 'let b=[];process.stdin.on("data",c=>b.push(c));process.stdin.on("end",()=>{try{process.stdout.write(String(JSON.parse(Buffer.concat(b).toString("utf8")).session_id||""))}catch{}})' 2>/dev/null)
if [ -n "$_l1_home" ] && [ -n "$_l1_sid" ]; then
  mkdir -p "$_l1_home/.claude/.loop1-kickoff" 2>/dev/null && : > "$_l1_home/.claude/.loop1-kickoff/$_l1_sid" 2>/dev/null
fi

# JSON-encode helper. Node for the same reason as above; the sed fallback is kept for the case where
# node is genuinely absent, since emitting invalid JSON would make the hook's whole reply be dropped.
json_enc() { node -e 'let b=[];process.stdin.on("data",c=>b.push(c));process.stdin.on("end",()=>process.stdout.write(Buffer.from(JSON.stringify(Buffer.concat(b).toString("utf8")),"utf8")))' 2>/dev/null \
  || { printf '"'; sed 's/\\/\\\\/g; s/"/\\"/g' | tr '\t\n\r' '   ' | tr -d '\000-\010\013\014\016-\037'; printf '"'; }; }
plan_line=""
if [ -n "$plan_text" ]; then
  plan_line="The approved plan (verbatim, from the ExitPlanMode payload — use it as the DEVELOP plan in the brief):
<<<APPROVED_PLAN
${plan_text}
APPROVED_PLAN
"
else
  # FALLBACK ONLY — the payload had no plan text. Guessing by newest mtime is
  # unreliable (shared plans dir, many stale plans), so flag it as best-effort and
  # tell the model to defer to the approved plan already in its context.
  plan_file=$(ls -t "$HOME/.claude/plans"/*.md 2>/dev/null | head -1)
  [ -n "$plan_file" ] && plan_line="Best-effort plan-file guess: $plan_file (newest by mtime — NOT confirmed to be the plan you just approved). If this isn't the plan you just approved, IGNORE it and use the approved plan from your context. "
fi

# A private plan-snapshot/prediction integration was removed for the public release:
# it POSTed the approved plan to a service on the author's own machine, which nobody
# else runs. Nothing downstream depended on it; the brief is frozen from the plan text
# captured above.
# Report a failure to read the approved plan in BOTH channels: systemMessage so the human
# sees it, and additionalContext so the model knows it must fall back to its own context
# rather than assuming the plan text below is complete. Never blocks execution.
fail_line=""
if [ -n "$_hk_fail" ]; then
  fail_line="WARNING: the approved plan could not be captured by this hook — ${_hk_fail}. Proceed with the work, but freeze the Task Brief from the approved plan in your own context, not from this hook's output.
"
fi
rm -rf "$_hk_dir" 2>/dev/null

# The engine ships with AID at project level (.claude/skills/), so it is available wherever
# AID is installed or linked. .aid/ (PRD/qa/validators) is enrichment used when present.
if [ -d "$ROOT/.aid" ]; then
  enrich="This project has AID state (.aid/ present): the pipeline will use its PRD/specs, .aid/qa/<task>.yaml acceptance criteria, and the phase4/5 validator agents as enrichment when available."
else
  enrich="This project has no .aid/ yet: run /aid-init or ./link-project.sh to create it. AR_ACCEPTANCE derives acceptance from the frozen brief, so no PRD is required."
fi
instr="A plan was just approved. The dev pipeline (pipeline-orchestrator + reflection + autoresearch) ships with AID in .claude/skills/ — BUT it must only drive IMPLEMENTATION plans.
${fail_line}${plan_line}INTENT GATE — do this FIRST, before anything else:
Classify the just-approved plan as either (a) IMPLEMENTATION (it will write/modify/delete code, config, or other project files) or (b) READ-ONLY (research, analysis, investigation, debugging-to-understand, audit, explanation — it produces findings/answers but makes no source changes).
- If READ-ONLY: do NOT initialize or drive the dev pipeline. Do NOT freeze a brief, do NOT create/refresh .aid/pipeline/state.json, do NOT bootstrap config. Stay advisory-only and just carry out the approved plan. (Steps 1-3 below do not apply.) Set SKIP_PIPELINE_GATE=1 if a downstream gate still nags.
- If IMPLEMENTATION: proceed with steps 1-3 below BEFORE writing implementation code.
1. INITIALIZE the pipeline (pipeline-orchestrator skill): if .aid/pipeline/config.json is missing, BOOTSTRAP it by copying the one shipped with AID at .aid/pipeline/config.json in the AID install; then create/refresh .aid/pipeline/state.json (pipeline_status=running, current_step=DEVELOP, counters).
2. FREEZE THE TASK BRIEF now, while the original prompt is still in context: write .aid/pipeline/<task_id>/brief.md ONCE (never overwrite) with the VERBATIM original request, the STATED_WHY, and the approved plan above as the DEVELOP plan. Use the verbatim APPROVED_PLAN block when present; if only a best-effort plan-file guess was given, prefer the approved plan from your own context over that file on any mismatch. AR_ACCEPTANCE validates against this; it survives a later compaction.
3. DRIVE all implementation through the orchestrator: DEVELOP → CODE_REVIEW (≤2) → AR_DESIGN → TDD (≤2) → AR_FUNCTION → VISUAL_QA → TEST_REVIEW → PHASE_GATE (≤2 re-examine) → AR_ACCEPTANCE. Resolve agents from .claude/agents/ and criteria from .claude/skills/reflection/criteria/. ${enrich} Do not finish the turn until the pipeline is satisfied (the dev-pipeline-gate Stop hook also enforces this).
Set SKIP_PIPELINE_GATE=1 to bypass for a one-off."
msg="plan approved → classify intent: IMPLEMENTATION plans run the pipeline (freeze brief + DEVELOP→…→AR_ACCEPTANCE); read-only/research/analysis plans stay advisory-only. SKIP_PIPELINE_GATE=1 to bypass."
[ -n "$_hk_fail" ] && msg="approved plan not captured by the hook — ${_hk_fail}. Execution continues; freeze the brief from the plan in context. ${msg}"

ac=$(printf '%s' "$instr" | json_enc)
sm=$(printf '%s' "$msg"  | json_enc)
printf '{"hookSpecificOutput":{"hookEventName":"PostToolUse","additionalContext":%s},"systemMessage":%s}\n' "$ac" "$sm"
exit 0
