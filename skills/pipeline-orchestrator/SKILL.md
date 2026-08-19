---
name: pipeline-orchestrator
description: Automated development pipeline state machine for Phase 4-5. Enforces DEVELOP > CODE_REVIEW (<=2 cycles) > AR_DESIGN > TDD (<=2 cycles) > AR_FUNCTION > VISUAL_QA > TEST_REVIEW > PHASE_GATE > AR_ACCEPTANCE > REALITY_CHECK (AR-3b) > API_TESTS > E2E_TESTS > CERTIFICATION sequence with sub-agent reviews and bounded autoresearch (AR) keep/revert loops at each gate.
---

# Pipeline Orchestrator Skill

Drives an automated state machine through Phase 4 (Development) and Phase 5 (QA & Ship). Augments the existing `aid-development` and `aid-qa-ship` skills — when active, it controls step sequence and sub-agent spawning. When inactive, manual flows still work.

## Activation

The pipeline activates in two ways:

1. **Manually** — the user runs `/pipeline`.
2. **Automatically on plan execution** — when an approved plan begins execution, the
   `plan-execution-pipeline.sh` `PostToolUse(ExitPlanMode)` hook injects an instruction to
   initialize the pipeline. On that signal you MUST, before writing implementation code:
   (a) initialize `.aid/pipeline/state.json` (`pipeline_status: running`, `current_step: DEVELOP`);
   (b) **freeze the immutable Task Brief** (see Initialize step 4) from the verbatim original
   request + WHY + the approved plan; and (c) drive all implementation through this state machine
   rather than coding ad-hoc. This is why the brief must be frozen at kickoff: plan-approval is the
   last moment the original prompt is reliably in context before a long run or compaction.

Also treat any request to *implement/execute an approved plan* as an automatic activation, even if
the hook signal is absent (e.g. "implement the plan in X.md"). `/pipeline` remains the manual entry
point, and the `dev-pipeline-gate.sh` Stop hook remains the turn-end safety net.

## State Machine

### Phase 4: Development Loop

Transitions (every edge; targets are exact step names):

```
DEVELOP --> CODE_REVIEW
CODE_REVIEW    PASS --> AR_DESIGN        FAIL --> FIX_CODE --> CODE_REVIEW (<=2 cycles)
AR_DESIGN      PASS --> TDD
TDD            PASS --> AR_FUNCTION      FAIL --> FIX_TESTS --> TDD (max 2)
AR_FUNCTION    PASS --> VISUAL_QA
VISUAL_QA      PASS --> TEST_REVIEW      FAIL --> FIX_VISUAL --> VISUAL_QA (until 7.0+)
TEST_REVIEW    PASS --> PHASE_GATE       FAIL --> FIX_TEST_CODE --> TEST_REVIEW (until 7.0+, <=2 cycles)
PHASE_GATE     PASS --> AR_ACCEPTANCE    FAIL --> DEVELOP (re-examine, bounded)
AR_ACCEPTANCE  DONE --> REALITY_CHECK (AR-3b)   gap --> DEVELOP (re-enter, bounded)
REALITY_CHECK  MATCH --> Phase 5         GAP --> DEVELOP (full traversal, bounded by max_reality_rounds)

Scored steps (CODE_REVIEW, VISUAL_QA, TEST_REVIEW): iterate until score threshold met
  (CODE_REVIEW and TEST_REVIEW now HARD-CAPPED at 2 review->fix cycles, then ESCALATE).
PHASE_GATE FAIL->DEVELOP re-examine is HARD-CAPPED at config.max_iterations.phase_gate_reexamine
  (default 2) rounds, then ESCALATE (DISTINCT from AR-3's max_acceptance_rounds).
Autoresearch steps (AR_DESIGN, AR_FUNCTION, AR_ACCEPTANCE): bounded keep/revert loops run by the
  shared autoresearch runner skill. Each is bounded by its own
  config.autoresearch.<pass> max_iterations / max_consecutive_reverts (+ AR_ACCEPTANCE max_acceptance_rounds).
Unscored steps (TDD, API_TESTS, E2E_TESTS): iterate until pass, max iterations as safety net (TDD = max 2).
REALITY_CHECK (AR-3b): outer reality-validation loop after AR_ACCEPTANCE — runs the eval harness
  (smoke mode) and diffs its results against acceptance_record.md. Bounded by
  config.autoresearch.ar_acceptance.max_reality_rounds (default 2); acceptance re-entries stay
  bounded by max_acceptance_rounds (default 3).
Cost limit ($50 default) is the universal safety brake for all steps — eval-harness spend during
  REALITY_CHECK COUNTS against it.
```

### Phase 5: QA Loop

```
API_TESTS   PASS --> E2E_TESTS       FAIL --> FIX_API_TESTS --> API_TESTS (max 5)
E2E_TESTS   PASS --> CERTIFICATION   FAIL --> FIX_E2E_TESTS --> E2E_TESTS (max 5)
CERTIFICATION --> DONE
```

## Step Definitions

### Phase 4 Steps

| Step | Action | Sub-Agent | On PASS | On FAIL |
|---|---|---|---|---|
| DEVELOP | Implement feature per spec using TDD (RED-GREEN-REFACTOR) | No | CODE_REVIEW | N/A |
| CODE_REVIEW | Spawn code-review-agent with changed files. **HARD CAP: 2 review->fix cycles** (`config.max_iterations.code_review`, default 2), then ESCALATE | Yes | AR_DESIGN | FIX_CODE |
| FIX_CODE | Apply fixes using full review feedback (scores + action_required) | No | CODE_REVIEW | N/A |
| AR_DESIGN | **AR-1 (pre-TDD).** Invoke the autoresearch runner skill (the shared `autoresearch` skill) in `mode=design` with `program.ar-design.md`. Judge-only (reflection-agent + `phase-4a-code-design.yaml`); bounded keep/revert loop; **NO interface / public-API / data-shape changes**. Logs final scores to `step_history`; the `state.json` write is the step's FINAL action (hook-safety note below) | Yes (runner) | TDD | (bounded by max_iterations / max_consecutive_reverts) |
| TDD | Write/run tests using test command from config. **Max 2 iterations** (`config.max_iterations.test_fix`, default 2) | No | AR_FUNCTION | FIX_TESTS |
| FIX_TESTS | Fix failing tests | No | TDD (re-run) | FIX_TESTS (loop) |
| AR_FUNCTION | **AR-2 (post-TDD).** Invoke the autoresearch runner (`mode=function`, `program.ar-function.md`). Harness = frozen test suite (`{{TEST_COMMAND}}` + coverage) as a HARD Tier-1 gate × reflection quality (`phase-4b-code-function.yaml`). Composite = quality × (all Tier-1 gates pass ? 1 : 0); a test going red => automatic revert. Logs final scores to `step_history`; the `state.json` write is the step's FINAL action (hook-safety note below) | Yes (runner) | VISUAL_QA | (bounded by max_iterations / max_consecutive_reverts) |
| VISUAL_QA | Spawn visual-qa-agent with Chrome DevTools MCP | Yes | TEST_REVIEW | FIX_VISUAL |
| FIX_VISUAL | Apply visual fixes using evaluator feedback (scores + screenshots) | No | VISUAL_QA | N/A |
| TEST_REVIEW | Spawn test-review-agent with impl + test files. **HARD CAP: 2 review->fix cycles** (`config.max_iterations.test_review`, default 2), then ESCALATE (mirrors CODE_REVIEW) | Yes | PHASE_GATE | FIX_TEST_CODE |
| FIX_TEST_CODE | Apply fixes using full review feedback (scores + action_required) | No | TEST_REVIEW | N/A |
| PHASE_GATE | Spawn qa-validator-agent (existing). **FAIL->DEVELOP re-examine HARD CAP: `config.max_iterations.phase_gate_reexamine` rounds (default 2), then ESCALATE** (DISTINCT from AR-3's `max_acceptance_rounds`) | Yes | AR_ACCEPTANCE | DEVELOP (re-examine, bounded) |
| AR_ACCEPTANCE | **AR-3a (post-QA).** Invoke the autoresearch runner (`mode=acceptance`, `program.ar-acceptance.md`). Validates the COMPLETE feature vs `ORIGINAL_REQUEST` + `STATED_WHY` (phase5-acceptance-validator + phase4-intent-validator + reflection `phase-5-qa-ship.yaml`). On **gap** -> re-enter DEVELOP (bounded by `max_acceptance_rounds`); on cap with open blockers ESCALATE. **REQUIRED: write `.aid/pipeline/{task_id}/acceptance_record.md`** (see AR_ACCEPTANCE Output below) BEFORE the state write. Logs final scores to `step_history`; the `state.json` write is the step's FINAL action (hook-safety note below) | Yes (runner) | REALITY_CHECK (on DONE) | DEVELOP (re-enter, bounded) |
| REALITY_CHECK | **AR-3b (outer loop).** Run the eval harness in smoke mode with gates + machine-readable output into the task dir, then diff `acceptance_record.md` vs `eval_results.json` criterion-by-criterion. **GAP** -> compile gap items referencing criterion ids, re-enter DEVELOP (FULL traversal — existing counters bound the inner rings), bounded by `max_reality_rounds`. **MATCH** -> write `.aid/pipeline/{task_id}/delta_record.md`, then write `state.json` LAST. Exhausted -> ESCALATE. Eval spend COUNTS against the $50 cost brake | No (eval harness) | Phase 5 (on MATCH) | DEVELOP (re-enter, bounded) |

**Note:** VISUAL_QA requires a running dev server and Chrome DevTools MCP. If the dev server is not running or Chrome is not available, skip VISUAL_QA with a logged warning and proceed to TEST_REVIEW.

**Note (autoresearch steps):** AR_DESIGN, AR_FUNCTION, and AR_ACCEPTANCE delegate to the shared autoresearch runner skill, which runs a bounded `snapshot -> one focused edit -> score -> keep-if-strictly-better-else-revert -> log` loop. Each appends rows to `.aid/pipeline/autoresearch/<task_id>/results.tsv`, is bounded by its own `config.autoresearch.<pass>` caps plus the existing `cost_limits.max_per_run_usd` brake, and NEVER auto-commits / NEVER runs destructive git (rollback is via snapshot copies only). For the mandatory `state.json`-last write order, see **CRITICAL — HOOK-SAFETY** under "After each AR step" below; it applies to all three AR steps without exception.

### DEVELOP Step — Review Criteria Preview

Before implementing, display the review criteria so code passes on first attempt:

```
Your code will be reviewed by isolated sub-agents. Write code that PASSES on first attempt.

CODE REVIEW CRITERIA (scored 1-10, need 7.0+ overall):
  Security (30%): OWASP Top 10 — any vulnerability = auto-FAIL
  Code Quality (30%): Single responsibility, proper types, no silent catches, no TODO
  Architecture (25%): Tech spec compliance, separation of concerns, dependency direction
  Documentation (15%): File headers, WHY comments, connection tags

VISUAL QA CRITERIA (scored 1-10, need 7.0+ overall — if UI changes):
  Functionality (30%): Every button, form, and link MUST work. Broken interaction = auto-FAIL
  Design Quality (30%): Coherent visual identity, consistent colors/fonts, clear hierarchy
  Craft (25%): Pixel-precise spacing, alignment, typography, contrast (WCAG AA)
  Originality (15%): Custom design choices, not pure default framework styling
  Note: A visual evaluator will NAVIGATE your running app, CLICK every element,
  and SCREENSHOT at desktop + mobile viewports. Build accordingly.

TEST REVIEW CRITERIA (scored 1-10, need 7.0+ overall):
  Test Quality (25%): Strong assertions with exact values, not just toBeTruthy()
  Coverage (25%): Happy path + edge cases + error cases per public function
  Independence (15%): No shared state, tests run in any order
  Alignment (15%): Tests verify behavior, not implementation details
  Production Safety (10%): No test-specific code in production files
  Mock Analysis (10%): Mock ratio < 20%, only external boundaries mocked

AUTORESEARCH AR-1 (DESIGN) KPIs (judge-only, pre-TDD — need each >= config.autoresearch.kpi_target, default 8.0):
  Structural health: Single responsibility, low coupling, no dead code, no duplicated logic
  Loudness of failures: NO silent catches / `|| DEFAULT` / `?? DEFAULT` / `.catch` swallows — fail loud, rethrow or surface
  Naming clarity: Intention-revealing names; no abbreviations that hide meaning
  Docs & traceability: File headers, WHY comments, connection/spec tags
  Note: AR-1 is a bounded keep/revert loop that improves quality WITHOUT changing any exported
  signature / public API / data shape (so TDD has a stable target). Write code that already
  scores >= target so AR-1 keeps few/no edits.

AUTORESEARCH AR-2 (FUNCTION) KPIs (post-TDD, composite — quality x Tier-1 gates):
  Functional correctness: Behavior matches spec for happy + edge + error paths
  Correctness of defaults: Safe defaults; no permissive/insecure fallbacks
  Security: No injection, no secret leakage, least privilege
  Tier-1 HARD gates (composite multiplier — any miss => composite 0 => revert / blocks advance):
    - 100% of tests pass (a test going red is an automatic revert)
    - Coverage >= config.thresholds.min_coverage_percent
    - ZERO new silent-failure paths vs baseline (no new `catch` / `|| DEFAULT` / `?? DEFAULT`
      / `.catch` without rethrow, judge-confirmed)
  Note: tests are FROZEN in AR-2 (they are the harness) — write them right in TDD, since AR-2
  cannot edit them to make code pass.
```

### FIX_CODE Step — Full Review Context

When entering FIX_CODE, provide the FULL review result (not just action_required):

```
## Code Review Feedback (iteration N/max)

Overall Score: X.X/10 (need 7.0+ to pass)
  Security:      X/10 — [reviewer note]
  Code Quality:  X/10 — [reviewer note]
  Architecture:  X/10 — [reviewer note]
  Documentation: X/10 — [reviewer note]

Biggest gaps: [from score_justification]

Action Items (priority order):
  1. [CRITICAL] ...
  2. [MAJOR] ...

Focus on the lowest-scoring categories first.
```

### FIX_TEST_CODE Step — Full Review Context

Same pattern as FIX_CODE but with test review scores:

```
## Test Review Feedback (iteration N/max)

Overall Score: X.X/10 (need 7.0+ to pass)
  Test Quality:      X/10 — [reviewer note]
  Coverage:          X/10 — [reviewer note]
  Independence:      X/10 — [reviewer note]
  Alignment:         X/10 — [reviewer note]
  Production Safety: X/10 — [reviewer note]
  Mock Analysis:     X/10 — [reviewer note]

Biggest gaps: [from score_justification]

Action Items (priority order):
  1. [CRITICAL] ...
  2. [MAJOR] ...

Focus on the lowest-scoring categories first.
```

### Phase 5 Steps

| Step | Action | On PASS | On FAIL |
|---|---|---|---|
| API_TESTS | Run integration test command from config | E2E_TESTS | FIX_API_TESTS |
| FIX_API_TESTS | Fix integration test failures | API_TESTS | loop |
| E2E_TESTS | Run `npx playwright test` + `npm run cucumber` | CERTIFICATION | FIX_E2E_TESTS |
| FIX_E2E_TESTS | Fix E2E/Cucumber failures | E2E_TESTS | loop |
| CERTIFICATION | Run ALL tests (random order), verify coverage, generate report | DONE | N/A |

## How to Spawn Sub-Agents

**CRITICAL: Each sub-agent MUST be spawned as an isolated Agent (sub-agent) using the Agent tool. DO NOT evaluate the code yourself — the whole point is isolated, unbiased review.**

### code-review-agent

**Step-by-step execution (follow exactly):**

1. Read `.aid/context.json` → extract task ID + description → this is `{{TASK_CONTEXT}}`
2. Run `git diff --name-only HEAD` → read each changed file's full content → this is `{{CHANGED_FILES}}`
3. Read relevant section from `docs/tech-spec/` → this is `{{TECH_SPEC_EXCERPT}}`
4. Read `../../agents/code-review-agent.md` verbatim → this is `{{CODE_STANDARDS}}`
5. Read `../../agents/code-review-agent.md`
6. Replace all `{{VARIABLE}}` placeholders with extracted values
7. Spawn the agent:

```
Agent(
  subagent_type: "general-purpose",
  prompt: [the rendered AGENT-PROMPT.md with all variables replaced],
  description: "Isolated code review — pipeline step",
  model: "opus"
)
```

8. Parse the returned JSON response

**Parse response:**
- Extract `scores.overall` and compare against `config.thresholds.code_review_pass` (default: 7.0)
- `scores.overall >= threshold` → advance to AR_DESIGN
- `scores.overall < threshold` → enter FIX_CODE, then re-run CODE_REVIEW
- **HARD CAP: 2 review→fix cycles** (`config.max_iterations.code_review`, default 2). The score
  threshold is the pass gate, but iteration is now bounded — increment a `code_review` iteration
  counter on each FIX_CODE→CODE_REVIEW cycle. After 2 cycles still below threshold → **ESCALATE**
  to the user (escalation protocol) instead of looping indefinitely. The cost limit remains an
  additional safety brake.
- If cost limit hit during iteration → ESCALATE (user decides: continue or stop)
- Store FULL response (including `scores`, `score_justification`, `biggest_gaps`) in `last_review_result`
- Log scores to `step_history` entry: `{ "step": "CODE_REVIEW", "result": "PASS|FAIL", "scores": {...}, "timestamp": "..." }`

### test-review-agent

**Step-by-step execution:**

1. Read `.aid/context.json` → extract task context → `{{TASK_CONTEXT}}`
2. Read all production source files modified in current task → `{{IMPLEMENTATION_FILES}}`
3. Read corresponding test files → `{{TEST_FILES}}`
4. Run test command, capture output → `{{TEST_RESULTS}}`
5. Read `../../agents/test-review-agent.md`, replace variables
6. Spawn:

```
Agent(
  subagent_type: "general-purpose",
  prompt: [rendered AGENT-PROMPT.md],
  description: "Isolated test review — pipeline step",
  model: "opus"
)
```

7. Parse the returned JSON response

**Parse response:**
- Extract `scores.overall` and compare against `config.thresholds.test_review_pass` (default: 7.0)
- `scores.overall >= threshold` → advance to PHASE_GATE
- `scores.overall < threshold` → enter FIX_TEST_CODE, then re-run TEST_REVIEW
- **HARD CAP: 2 review→fix cycles** (`config.max_iterations.test_review`, default 2). The score
  threshold is the pass gate, but iteration is now bounded — increment a `test_review` iteration
  counter on each FIX_TEST_CODE→TEST_REVIEW cycle. After 2 cycles still below threshold → **ESCALATE**
  to the user (escalation protocol) instead of looping indefinitely (mirrors CODE_REVIEW). The cost
  limit remains an additional safety brake.
- If cost limit hit during iteration → ESCALATE (user decides: continue or stop)
- Store FULL response (including `scores`, `score_justification`, `biggest_gaps`) in `last_review_result`
- Log scores to `step_history` entry: `{ "step": "TEST_REVIEW", "result": "PASS|FAIL", "scores": {...}, "timestamp": "..." }`

### visual-qa-agent

**Prerequisites check (before spawning):**
1. Verify dev server is running: `curl -s -o /dev/null -w "%{http_code}" {{TARGET_URL}}` → expect 200
2. Verify Chrome DevTools MCP is available: check for `mcp__chrome-devtools__navigate_page` tool
3. If either fails → skip VISUAL_QA with warning, advance to TEST_REVIEW

**Step-by-step execution:**

1. Read `.aid/context.json` → `{{TASK_CONTEXT}}`
2. Read `config.visual_qa.dev_server_url` (default: `http://localhost:5173`) → `{{TARGET_URL}}`
3. Read `step_summaries.DEVELOP` from state.json → `{{IMPLEMENTATION_SUMMARY}}`
4. List routes/pages from changed files or tech spec → `{{PAGES_TO_TEST}}`
5. Read `../../agents/visual-qa-agent.md`, replace variables
6. Spawn:

```
Agent(
  subagent_type: "general-purpose",
  prompt: [rendered AGENT-PROMPT.md],
  description: "Isolated visual QA — pipeline step",
  model: "opus"
)
```

7. Parse the returned JSON response

**Parse response:**
- Extract `scores.overall` and compare against `config.thresholds.visual_qa_pass` (default: 7.0)
- `verdict: "PASS"` AND `scores.overall >= threshold` → advance to TEST_REVIEW
- `verdict: "FAIL"` OR `scores.overall < threshold` → enter FIX_VISUAL
- Store FULL response (including `scores`, `lighthouse`, `issues`, `testing_summary`) in `last_review_result`
- Log scores to `step_history` entry: `{ "step": "VISUAL_QA", "result": "PASS|FAIL", "scores": {...}, "lighthouse": {...}, "timestamp": "..." }`

### FIX_VISUAL Step — Full Review Context

When entering FIX_VISUAL, provide the FULL visual review result:

```
## Visual QA Feedback (iteration N/max)

Overall Score: X.X/10 (need 7.0+ to pass)
  Design Quality:  X/10 — [reviewer observations]
  Originality:     X/10 — [reviewer observations]
  Craft:           X/10 — [reviewer observations]
  Functionality:   X/10 — [reviewer observations]

Lighthouse: Accessibility X/100 | SEO X/100 | Best Practices X/100

Testing Summary: X screenshots, X elements tested, X viewports, X pages

Biggest gaps: [from score_justification]

Action Items (priority order):
  1. [CRITICAL] ...
  2. [MAJOR] ...

Focus on functionality issues first, then craft, then design quality.
```

### qa-validator-agent (existing)

```
Task(
  subagent_type: "general-purpose",
  prompt: "You are a QA Validator. Read .aid/qa/{TASK-ID}.yaml and review modified files. Return JSON with verdict: PASS or FAIL.",
  description: "QA validation for {TASK-ID}"
)
```

**Parse response:**
- `verdict: "PASS"` → advance to AR_ACCEPTANCE (AR-3); AR_ACCEPTANCE on DONE → REALITY_CHECK (AR-3b); on MATCH → Phase 5 (API_TESTS)
- `verdict: "FAIL"` → return to DEVELOP (re-examine approach)
- **HARD CAP: `config.max_iterations.phase_gate_reexamine` rounds (default 2).** Increment a
  `phase_gate_reexamine` counter on each PHASE_GATE-FAIL→DEVELOP re-examine round. After 2 rounds
  still FAIL → **ESCALATE** to the user (escalation protocol) instead of looping indefinitely.
  This re-examine cap is **DISTINCT** from AR-3's `max_acceptance_rounds`, which bounds only the
  AR_ACCEPTANCE-gap re-entry into DEVELOP — not PHASE_GATE failures. The cost limit remains an
  additional safety brake.

### autoresearch runner (AR_DESIGN / AR_FUNCTION / AR_ACCEPTANCE)

These three steps do NOT spawn a review agent that returns a single JSON verdict. Instead they
invoke the shared **autoresearch runner skill** in the matching mode, which runs the bounded
keep/revert loop and itself spawns the harness agents — the subagent named `reflection-agent`
(prompt loaded from `{{WORKSPACE}}/.claude/agents/reflection-agent.md`), and for AR-3
the phase5-acceptance-validator / phase4-intent-validator:

| Step | Mode | Prompt file | On success | On gap/incomplete |
|---|---|---|---|---|
| AR_DESIGN | `design` | `program.ar-design.md` | advance to TDD | (bounded loop; revert non-improving edits) |
| AR_FUNCTION | `function` | `program.ar-function.md` | advance to VISUAL_QA | (bounded loop; test red => auto-revert) |
| AR_ACCEPTANCE | `acceptance` | `program.ar-acceptance.md` | DONE → advance to REALITY_CHECK (AR-3b) | gap → re-enter DEVELOP (bounded by `max_acceptance_rounds`, else ESCALATE) |

**After each AR step:**
- Read the runner's final composite scores from `.aid/pipeline/autoresearch/<task_id>/results.tsv`.
- Log to `step_history`: `{ "step": "AR_DESIGN|AR_FUNCTION|AR_ACCEPTANCE", "result": "PASS|GAP", "scores": {...}, "timestamp": "..." }`.
- **CRITICAL — HOOK-SAFETY.** The `dev-pipeline-gate.sh` Stop hook re-blocks when the newest source
  mtime > `state.json` mtime. A rollback via `cp <snapshot> <file>` sets the source mtime to NOW, and
  the plateau stop often fires right after a run of REVERTS — so the last disk write is frequently a
  revert, not a kept edit. THEREFORE on stop the step MUST: (1) FIRST restore the editable set to the
  best-kept version, then (2) WRITE `state.json` **UNCONDITIONALLY as the FINAL action — after the last
  source mutation of ANY kind (kept edit, revert/restore cp, or crash restore)**. Update `last_updated`
  and persist `state.json` as the final write of the step. If `state.json` is not the newest write, the
  hook will wrongly re-block the next turn.

### AR_ACCEPTANCE Output — acceptance_record.md (REQUIRED)

On every AR_ACCEPTANCE verdict (DONE or gap), write `.aid/pipeline/{task_id}/acceptance_record.md`
BEFORE the step's final `state.json` write. This is the durable AR-3a verdict that REALITY_CHECK
(AR-3b) diffs against reality — without it AR-3b has nothing to validate. Overwrite on each round
(latest round wins; prior rounds live in `step_history`).

```markdown
---
task_id: <id>
round: <ar_acceptance_rounds counter at time of writing>
written_at: <ISO-8601 now>
---

## Acceptance Record (AR-3a)

- pass_rate: <NN>%          # from the runner's final acceptance pass rate
- why_alignment: <X.X>/10   # from reflection phase-5-qa-ship scoring
- verdict: DONE | GAP

### criteria_met
- <criterion id> — <one-line evidence>

### criteria_not_met
- <criterion id> — <what is missing>
```

Criterion ids come from the brief's `EVAL_METRICS` section when present, else from
`.aid/qa/<task_id>.yaml` criteria names. Use the SAME ids the eval harness reports
(`eval_results.json`) so AR-3b can diff mechanically.

### REALITY_CHECK Step — AR-3b Reality Validation (outer loop)

WHY: AR-3a validates the feature against the frozen brief; AR-3b validates that verdict against
reality — the eval harness run on a real corpus. An acceptance verdict that does not hold under
the corpus is a gap, not a ship.

Entry: AR_ACCEPTANCE verdict DONE (`acceptance_record.md` exists — if missing, ESCALATE; never
diff against a paraphrase).

1. **Run the eval harness (smoke mode, gates on, machine-readable output into the task dir):**

   ```bash
   cd e2e && RUN_PM_PIPELINE_EVAL=1 PM_EVAL_MODE=smoke PM_EVAL_GATES=1 \
     PM_EVAL_OUT_DIR=../.aid/pipeline/{task_id} \
     E2E_CLAUDE_API_KEY=... npm run test:pm-eval
   ```

   `PM_EVAL_OUT_DIR` makes `e2e/src/evaluation/report.ts` write
   `.aid/pipeline/{task_id}/eval_results.json` (per-criterion `id`, `pass_rate`, `target`, `pass`)
   alongside the normal report.
2. **Count the cost:** add the eval run's token spend to `cost.*` — the $50 `max_per_run_usd`
   brake COUNTS eval spend. Brake hit → ESCALATE (standard protocol).
3. **Diff** `acceptance_record.md` vs `eval_results.json` criterion-by-criterion:
   - **GAP** — any criterion claimed in `criteria_met` has `pass: false` in `eval_results.json`,
     or the eval gate failed overall: compile gap items referencing the criterion ids, write them
     to `step_summaries.REALITY_CHECK`, increment `iterations.reality_rounds`, and re-enter
     DEVELOP for a **FULL traversal** (DEVELOP → … → AR_ACCEPTANCE → REALITY_CHECK). The existing
     per-step counters bound the inner rings; no counter resets.
   - **MATCH** — every claimed criterion holds and the gate passed: write the final delta record
     `.aid/pipeline/{task_id}/delta_record.md`, then write `state.json` **LAST** (hook-safety:
     `state.json` must be the newest write of the step).

   ```markdown
   ---
   task_id: <id>
   written_at: <ISO-8601 now>
   ---

   ## Delta Record (AR-3b final)

   - acceptance_rounds_used: <n>/<max_acceptance_rounds>
   - reality_rounds_used: <n>/<max_reality_rounds>

   ### criteria deltas (acceptance vs eval)
   <!-- SCALES DIFFER: acceptance pass_rate is a percent; eval pass_rate is the 0-10
        judge-score scale. The delta column is PASS-AGREEMENT ONLY (both-pass /
        acceptance-only / eval-only) — never numeric subtraction across scales. -->
   | criterion id | acceptance | eval pass_rate | target | delta (pass agreement) |
   |---|---|---|---|---|
   ```

4. **Bounds:** read `autoresearch.ar_acceptance.max_acceptance_rounds` (default 3) and
   `autoresearch.ar_acceptance.max_reality_rounds` (default 2) from `.aid/pipeline/config.json`.
   `reality_rounds` exhausted with GAP still open → existing escalation protocol.

## State Management

### Initialize Pipeline

When `/pipeline` is invoked:

1. Read `.aid/pipeline/config.json` for settings
2. Read `.aid/context.json` for current task
3. Create `.aid/pipeline/state.json`:

```json
{
  "$schema": "aid-pipeline-state-v2",
  "pipeline_status": "running",
  "current_phase": 4,
  "current_step": "DEVELOP",
  "current_task_id": "[from context.json]",
  "started_at": "[ISO-8601 now]",
  "last_updated": "[ISO-8601 now]",
  "iterations": {
    "code_review": 0,
    "test_review": 0,
    "phase_gate_reexamine": 0,
    "test_fix": 0,
    "api_fix": 0,
    "e2e_fix": 0,
    "ar_design": 0,
    "ar_function": 0,
    "ar_acceptance_rounds": 0,
    "reality_rounds": 0
  },
  "cost": {
    "total_input_tokens": 0,
    "total_output_tokens": 0,
    "estimated_cost_usd": 0.00,
    "per_step": {}
  },
  "step_summaries": {},
  "last_review_result": null,
  "step_history": []
}
```

4. **Freeze the immutable Task Brief** (compaction-proofing — do this NOW, at kickoff, while the original prompt is still in context).

   Write `.aid/pipeline/<task_id>/brief.md` **once**. If the file already exists (resume case), DO NOT overwrite it — read it. This file is the durable source of intent that survives context compaction and long runs; every later step (especially **AR_ACCEPTANCE**) reads intent from here, never from conversation memory.

   ```markdown
   ---
   task_id: <id>
   frozen_at: <ISO-8601 now>        # immutable after first write
   source: conversation | prd | user-provided
   prd_ref: <path to docs/prd/… or "">
   tech_spec_ref: <path to docs/tech-spec/… or "">
   impl_plan_ref: <path to docs/impl-plan/… or "">
   acceptance_criteria_ref: .aid/qa/<task_id>.yaml
   ---

   ## ORIGINAL_REQUEST (verbatim — never edit)
   <the first user message that initiated this feature, VERBATIM — not paraphrased>

   ## STATED_WHY (exact text — never edit)
   <the business/user WHY established for this feature>

   ## DEVELOP PLAN (snapshot at kickoff)
   <the agreed implementation plan, or a link to docs/impl-plan; the WHAT/HOW the build follows>

   ## EVAL_METRICS (frozen at plan time — never edit)
   <measurable CORPUS-LEVEL metrics the delivered feature must hit, one row per criterion.
    Use the SAME criterion ids the eval harness emits in eval_results.json so REALITY_CHECK
    (AR-3b) can diff acceptance_record.md vs reality mechanically.>

   | criterion_id | metric | target |
   |---|---|---|
   ```

   `EVAL_METRICS` authoring rules: freeze it WITH the brief at kickoff (plan-approval is the last
   moment success metrics are honestly negotiable — after code exists, metrics drift toward what
   was built). Briefs frozen before this section existed are **grandfathered**: REALITY_CHECK
   falls back to the eval harness's default gate criteria.

   Capture order (never fabricate intent):
   - If `original_request` / `stated_why` are already persisted (existing `brief.md`, or an existing PRD's problem/why) → use those (`source: prd`).
   - Else capture them VERBATIM from the current conversation's first user message + the established WHY (`source: conversation`).
   - If neither is available (e.g. `/pipeline` invoked cold with no prompt and no PRD) → **ESCALATE: ask the user for the original request + WHY before proceeding.** A pipeline with no frozen intent cannot be accepted by AR-3.

5. Also mirror the verbatim `original_request` and `stated_why` into `.aid/context.json` (so existing reflection tooling can read them from disk too), but `brief.md` is the authoritative immutable copy.

### Update State on Transitions

After EACH step transition:

1. Update `current_step` to new step
2. Increment relevant iteration counter
3. Append to `step_history`: `{ "step": "...", "result": "PASS|FAIL", "scores": {...}, "timestamp": "..." }`
4. Update `last_updated`
5. If sub-agent ran, store result in `last_review_result`
6. **Update cost tracking** (see Cost Tracking section)
7. **Write step summary** (see Context Management section)
8. Write updated state to `.aid/pipeline/state.json`

### Resume on Session Restart

When loading a project with an active pipeline:

1. Read `.aid/pipeline/state.json`
2. If `pipeline_status: "running"`, resume from `current_step`
3. Read `step_summaries` to restore context without replaying full conversation
4. Display: "Pipeline active — resuming from [current_step] for task [task_id] ($[cost] spent)"

## Cost Tracking

Multi-agent runs can cost $50-200; without cost visibility, pipeline runs silently burn through budgets.

### How to Track

After EACH sub-agent call (CODE_REVIEW, TEST_REVIEW, PHASE_GATE), update cost:

1. Extract token counts from the sub-agent's response metadata (or estimate: ~4K input + ~2K output per review)
2. Calculate cost: `(input_tokens / 1M * pricing.input_per_mtok) + (output_tokens / 1M * pricing.output_per_mtok)`
3. Update `cost.total_input_tokens`, `cost.total_output_tokens`, `cost.estimated_cost_usd`
4. Add step entry: `cost.per_step[step_name] = { input_tokens, output_tokens, cost_usd, timestamp }`

### Cost Limits

Read limits from `config.cost_limits`:

| Threshold | Action |
|---|---|
| `cost >= warn_at_usd` | Display: "Cost warning: $X.XX spent (limit: $Y.YY)" |
| `cost >= max_per_run_usd` | ESCALATE: "Pipeline cost limit reached ($X.XX / $Y.YY). Continue? (y/n)" |

Cost escalation uses the same protocol as iteration escalation — user can resume, override, or abort.

### Display in Pipeline Status

Include cost in all pipeline displays:

```
Pipeline: [task_id] | Phase [4|5] | Cost: $X.XX / $Y.YY
[=====>-----------] Step: CODE_REVIEW (iteration 2/3)
```

## Context Management

Long pipeline runs accumulate context, and the harness may **compact** the conversation mid-run, discarding the original prompt and WHY. Anything the pipeline needs later must live **on disk**, not in conversation memory.

### Task Brief (immutable intent record)

`.aid/pipeline/<task_id>/brief.md` (frozen at Initialize, step 4) holds the **verbatim ORIGINAL_REQUEST, the STATED_WHY, and the DEVELOP plan**. It is written once and never overwritten. This is what makes **AR_ACCEPTANCE** correct: AR-3 must validate the delivered feature against the *original* ask, and a mid-run compaction would otherwise erase it. AR-3 reads intent from `brief.md`, and **escalates loudly** if it is missing rather than validating against a paraphrase.

**Re-hydrate from disk at every step entry.** Each step (and especially any step entered after a compaction or session resume) must reconstruct what it needs from disk — `brief.md` for intent, `state.step_summaries` for prior-step outcomes, `state.json` for counters — and must NOT assume the original prompt or earlier results are still in the conversation. Never silently fall back to a paraphrase or a guess: if `brief.md` is absent, escalate.

### Step Summaries

After each step completes, write a structured summary to `state.step_summaries`:

```json
{
  "step_summaries": {
    "DEVELOP": "Implemented auth middleware for /api/v1/users. Files: src/middleware/auth.ts, src/routes/users.ts. 142 lines added.",
    "CODE_REVIEW_1": "FAIL (5.8/10). Security: 4 (SQL injection auth.ts:45). Quality: 7. Docs: 5. Arch: 7.",
    "FIX_CODE_1": "Fixed SQL injection (parameterized query). Added WHY comments to auth.ts.",
    "CODE_REVIEW_2": "PASS (7.6/10). Security: 8. Quality: 7. Docs: 7. Arch: 8.",
    "TDD": "12 tests written. 11 pass, 1 fail (timeout on async test). Coverage: 78%."
  }
}
```

### How Summaries Prevent Context Degradation

1. **On session resume:** Read `step_summaries` instead of replaying full conversation
2. **On FIX steps:** Show the summary + last review result, not the entire review history
3. **On escalation:** Build the escalation summary from `step_summaries`, not conversation
4. **Key rule:** Each summary is max 2-3 sentences. Include: what happened, key files, score if applicable

### What Goes in a Summary

| Step Type | Summary Contains |
|---|---|
| DEVELOP | Files created/modified, lines added, what was implemented |
| CODE_REVIEW | PASS/FAIL, overall score, per-category scores, key issues, cycle count (max 2) |
| FIX_CODE | What was fixed, which categories improved |
| AR_DESIGN | Baseline→final composite, kept/reverted count, top kept edits, KPI dims (struct/loudness/naming/docs) |
| TDD | Tests written, pass/fail count, coverage %, iteration count (max 2) |
| TEST_REVIEW | PASS/FAIL, overall score, per-category scores, key issues |
| FIX_TEST_CODE | What was fixed, which tests added/changed |
| AR_FUNCTION | Baseline→final composite, Tier-1 gate status (tests/coverage/silent-paths), kept/reverted count |
| PHASE_GATE | PASS/FAIL, which criteria passed/failed |
| AR_ACCEPTANCE | Round count (max_acceptance_rounds), pass_rate, why_alignment, blockers, DONE or re-entered DEVELOP |
| REALITY_CHECK | Round count (max_reality_rounds), MATCH or GAP, gap items (criterion ids), eval cost added |
| API/E2E_TESTS | Pass/fail count, which tests failed |

## Escalation Protocol

When any step hits its max iteration count:

1. Set `pipeline_status: "ESCALATED"` and `current_step: "ESCALATED"`
2. Present summary to user:

```
Pipeline Escalated: [step_name] exceeded max iterations ([count]/[max])

Issues from last review:
[List action_required from last_review_result]

Options:
1. /pipeline resume — Reset counter for this step, try again
2. /pipeline override — Skip this step (with documented justification)
3. /pipeline reset — Reset all counters, restart from DEVELOP
```

3. Wait for user decision before proceeding

## Pipeline Display

Show pipeline progress at each step transition:

```
Pipeline: [task_id] | Phase [4|5]
[=====>-----------] Step: CODE_REVIEW (iteration 2/3)

Last result: FAIL — 1 CRITICAL (SQL injection), 1 MAJOR (missing auth)
Action: Fixing issues from code review...
```

## Configuration

Read from `.aid/pipeline/config.json`:

| Setting | Default | Purpose |
|---|---|---|
| `max_iterations.code_review` | 2 | Max CODE_REVIEW→FIX_CODE cycles (HARD CAP — then ESCALATE) |
| `max_iterations.test_review` | 2 | Max TEST_REVIEW→FIX_TEST_CODE cycles (HARD CAP — then ESCALATE, mirrors CODE_REVIEW) |
| `max_iterations.phase_gate_reexamine` | 2 | Max PHASE_GATE-FAIL→DEVELOP re-examine rounds (HARD CAP — then ESCALATE; DISTINCT from AR-3 `max_acceptance_rounds`) |
| `max_iterations.test_fix` | 2 | Max test fix attempts (unscored — needs hard limit) |
| `max_iterations.api_fix` | 5 | Max API test fix attempts (unscored) |
| `max_iterations.e2e_fix` | 5 | Max E2E test fix attempts (unscored) |
| `autoresearch.kpi_target` | 8.0 | AR quality-score target (0–10) for AR_DESIGN / AR_FUNCTION |
| `autoresearch.ar_design.max_iterations` | (project) | AR-1 iteration cap |
| `autoresearch.ar_design.max_consecutive_reverts` | (project) | AR-1 plateau cap |
| `autoresearch.ar_function.max_iterations` | (project) | AR-2 iteration cap |
| `autoresearch.ar_function.max_consecutive_reverts` | (project) | AR-2 plateau cap |
| `autoresearch.ar_acceptance.max_acceptance_rounds` | 3 | AR-3a outer DEVELOP-re-entry round cap (then ESCALATE) |
| `autoresearch.ar_acceptance.max_reality_rounds` | 2 | AR-3b REALITY_CHECK GAP→DEVELOP re-entry round cap (then ESCALATE) |
| `autoresearch.ar_acceptance.pass_rate_target` | 90 | AR-3 acceptance pass-rate target (%) |
| `test_commands.unit` | `npm test` | Unit test command |
| `test_commands.integration` | `npm test -- --testPathPattern=integration` | Integration test command |
| `test_commands.e2e` | `npx playwright test` | E2E test command |
| `test_commands.cucumber` | `npm run cucumber` | Cucumber test command |
| `test_commands.coverage` | `npm test -- --coverage` | Coverage report command |
| `thresholds.code_review_pass` | 7.0 | Minimum code review score (1-10) |
| `thresholds.test_review_pass` | 7.0 | Minimum test review score (1-10) |
| `thresholds.visual_qa_pass` | 7.0 | Minimum visual QA score (1-10) |
| `thresholds.auto_fail_on_critical_security` | true | Auto-fail on security issues |
| `thresholds.min_coverage_percent` | 70 | Minimum test coverage % |
| `cost_limits.warn_at_usd` | 25.00 | Show warning when cost exceeds this |
| `cost_limits.max_per_run_usd` | 50.00 | Escalate when cost exceeds this |
| `cost_limits.pricing.input_per_mtok` | 15.00 | $/million input tokens (Opus 4.6) |
| `cost_limits.pricing.output_per_mtok` | 75.00 | $/million output tokens (Opus 4.6) |
| `visual_qa.dev_server_url` | `http://localhost:5173` | URL of running dev server for visual QA |
| `visual_qa.enabled` | true | Enable/disable visual QA step |
| `visual_qa.skip_if_no_ui_changes` | true | Skip if no JSX/TSX/CSS files changed |
| `auto_advance_phase` | true | Auto-advance from Phase 4 to 5 |
