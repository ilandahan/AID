# Escalation Protocol

What happens when a pipeline step hits its maximum iteration count.

---

## When Escalation Triggers

### Trigger 1: Max Iterations (unscored steps only)

Unscored steps (binary pass/fail from test execution) escalate on max iterations:

| Step | Counter | Default Max |
|------|---------|-------------|
| TDD (re-run) | test_fix | 5 |
| API_TESTS (re-run) | api_fix | 5 |
| E2E_TESTS (re-run) | e2e_fix | 5 |

Scored steps (CODE_REVIEW, VISUAL_QA, TEST_REVIEW) do NOT have max iterations — they iterate until the score threshold is met. Their only escalation trigger is cost (Trigger 2).

### Trigger 2: Cost Limit

The pipeline escalates when `cost.estimated_cost_usd >= config.cost_limits.max_per_run_usd`:

```
Pipeline Cost Limit Reached
Current cost: $XX.XX (limit: $YY.YY)
Step: [current_step] | Iterations used: code_review [N]/[max], test_fix [N]/[max], ...

Cost Breakdown:
  CODE_REVIEW (x2): $X.XX
  TEST_REVIEW (x1): $X.XX
  PHASE_GATE:       $X.XX

Options:
  1. /pipeline resume — Continue (raises limit by 50%)
  2. /pipeline abort — Stop pipeline, save progress
```

A cost warning (non-blocking) is shown at `warn_at_usd`.

---

## Escalation Procedure

### Step 1: Update State

```json
{
  "pipeline_status": "ESCALATED",
  "current_step": "ESCALATED",
  "last_updated": "[now]"
}
```

### Step 2: Build Summary

Collect from `last_review_result`:
- Overall score and per-category scores
- All `action_required` items
- All issues with severity CRITICAL or MAJOR
- `biggest_gaps` and `score_justification`
- Iteration history for the failing step (scores across attempts)
- Cumulative cost from `cost.estimated_cost_usd`

### Step 3: Present to User

```
Pipeline Escalated
Step [STEP_NAME] failed after [N] iterations (max: [MAX]).
Cost so far: $X.XX / $Y.YY

Score Trend Across Attempts:
  Attempt 1: X.X/10 [security: X, quality: X, arch: X, docs: X]
  Attempt 2: X.X/10 [security: X, quality: X, arch: X, docs: X]
  Attempt 3: X.X/10 [security: X, quality: X, arch: X, docs: X]

Persistent Issues (not resolved across attempts):
[List of unresolved action_required items from last review]

Biggest Gaps: [from last review biggest_gaps]

Options:
  1. Resume — Reset this step's counter and try again
     Usage: Reply "resume" or "/pipeline resume"

  2. Override — Skip this step with documented justification
     Usage: Reply "override: [reason]" or "/pipeline override [reason]"
     Note: Override is logged in step_history with your justification

  3. Reset — Reset ALL counters and restart from DEVELOP
     Usage: Reply "reset" or "/pipeline reset"

  4. Abort — Stop the pipeline entirely
     Usage: Reply "abort" or "/pipeline abort"
```

### Step 4: Wait for User Decision

Do NOT proceed automatically. The pipeline is paused until the user responds.

---

## Handling User Responses

### Resume

1. Reset the specific counter to 0: `iterations[counter] = 0`
2. Set `pipeline_status: "running"`
3. Return to the failing step (e.g., CODE_REVIEW)
4. Log in `step_history`: `{ "step": "ESCALATION_RESUME", "note": "User resumed [step]" }`

### Override

1. Log in `step_history`: `{ "step": "ESCALATION_OVERRIDE", "note": "User skipped [step]: [justification]" }`
2. Set `pipeline_status: "running"`
3. Advance to the NEXT step in the sequence
4. Display warning: "Step [X] overridden. Justification logged."

### Reset

1. Reset ALL iteration counters to 0
2. Set `pipeline_status: "running"`, `current_step: "DEVELOP"`
3. Log in `step_history`: `{ "step": "ESCALATION_RESET", "note": "User reset pipeline" }`

### Abort

1. Set `pipeline_status: "completed"` (with note: aborted)
2. Archive to `history.json` with abort flag
3. Log in `step_history`: `{ "step": "ESCALATION_ABORT", "note": "User aborted pipeline" }`

---

## Anti-Patterns

| Don't | Why |
|-------|-----|
| Auto-resume after escalation | Defeats the purpose of human oversight |
| Skip security CRITICAL issues | Never override security — fix them |
| Reset without reviewing issues | Same issues will recur |
| Abort without documenting why | Lose learning opportunity |

---

## Escalation Metrics

Track in `history.json` for improvement:
- Which steps escalate most frequently
- Average iterations before escalation
- Most common persistent issues
- Whether overrides correlate with production bugs
- Average cost per pipeline run
- Score trends: which categories consistently score lowest
- Cost per iteration (are later iterations cheaper as issues narrow?)
