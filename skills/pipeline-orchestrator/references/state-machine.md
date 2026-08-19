# Pipeline State Machine

Visual state diagram and transition rules for the automated development pipeline.

---

## Full State Diagram

```
                            PHASE 4: DEVELOPMENT
  ┌──────────────────────────────────────────────────────────────────────────────┐
  │                                                                              │
  │  ┌─────────┐    ┌─────────────┐    ┌─────┐    ┌───────────┐  ┌───────────┐ │
  │  │ DEVELOP │───>│ CODE_REVIEW │───>│ TDD │───>│ VISUAL_QA │─>│TEST_REVIEW│ │
  │  └─────────┘    └──────┬──────┘    └──┬──┘    └─────┬─────┘  └─────┬─────┘ │
  │       ^                │              │             │               │        │
  │       │            [<8.0]          [FAIL]        [<7.0]          [<8.0]      │
  │       │                │              │             │               │        │
  │       │           ┌────┴────┐   ┌────┴─────┐ ┌────┴──────┐ ┌─────┴──────┐ │
  │       │           │FIX_CODE │   │FIX_TESTS │ │FIX_VISUAL │ │FIX_TEST_   │ │
  │       │           └────┬────┘   └────┬─────┘ └────┬──────┘ │   CODE     │ │
  │       │                │              │            │        └─────┬──────┘ │
  │       │                v              v            v              v        │
  │       │          CODE_REVIEW        TDD       VISUAL_QA    TEST_REVIEW    │
  │       │         (until ≥8.0)      (max 5)    (until ≥7.0)  (until ≥8.0)   │
  │       │                                                                   │
  │       │         ┌────────────┐                                            │
  │       +─[FAIL]──│ PHASE_GATE │                                            │
  │                 └─────┬──────┘                                            │
  │                     [PASS]                                                │
  └───────────────────────┼──────────────────────────────────────────────────┘
                          │
                          v
                            PHASE 5: QA & SHIP
  ┌───────────────────────────────────────────────────────────────┐
  │                                                               │
  │  ┌───────────┐    ┌───────────┐    ┌───────────────┐         │
  │  │ API_TESTS │───>│ E2E_TESTS │───>│ CERTIFICATION │──> DONE │
  │  └─────┬─────┘    └─────┬─────┘    └───────────────┘         │
  │      [FAIL]           [FAIL]                                  │
  │        │                │                                     │
  │  ┌─────┴───────┐ ┌─────┴───────┐                             │
  │  │FIX_API_TESTS│ │FIX_E2E_TESTS│                             │
  │  └─────┬───────┘ └─────┬───────┘                             │
  │        v                v                                     │
  │    API_TESTS        E2E_TESTS                                 │
  │    (max 5)          (max 5)                                   │
  │                                                               │
  └───────────────────────────────────────────────────────────────┘
```

---

## Escalation Path

```
Any step hits max iterations
         │
         v
   ┌───────────┐
   │ ESCALATED │──> Present to user
   └───────────┘
         │
    ┌────┼────┐
    v    v    v
 resume  override  reset
    │    │         │
    v    v         v
 [step]  [next]  DEVELOP
```

---

## State Values

### pipeline_status

| Value | Meaning |
|-------|---------|
| `idle` | Pipeline initialized but not started |
| `running` | Pipeline actively processing steps |
| `paused` | Pipeline paused (config issue, user request) |
| `escalated` | Step exceeded max iterations, waiting for user |
| `completed` | Pipeline finished successfully (CERTIFICATION passed) |

### current_step (Phase 4)

| Value | Entry Condition |
|-------|----------------|
| `DEVELOP` | Pipeline start OR PHASE_GATE fail |
| `CODE_REVIEW` | DEVELOP complete OR FIX_CODE complete |
| `FIX_CODE` | CODE_REVIEW fail |
| `TDD` | CODE_REVIEW pass OR FIX_TESTS complete |
| `FIX_TESTS` | TDD fail (tests fail) |
| `VISUAL_QA` | TDD pass (tests pass) OR FIX_VISUAL complete |
| `FIX_VISUAL` | VISUAL_QA fail |
| `TEST_REVIEW` | VISUAL_QA pass (or skipped) OR FIX_TEST_CODE complete |
| `FIX_TEST_CODE` | TEST_REVIEW fail |
| `PHASE_GATE` | TEST_REVIEW pass |

### current_step (Phase 5)

| Value | Entry Condition |
|-------|----------------|
| `API_TESTS` | PHASE_GATE pass OR FIX_API_TESTS complete |
| `FIX_API_TESTS` | API_TESTS fail |
| `E2E_TESTS` | API_TESTS pass OR FIX_E2E_TESTS complete |
| `FIX_E2E_TESTS` | E2E_TESTS fail |
| `CERTIFICATION` | E2E_TESTS pass |
| `ESCALATED` | Any step hits max iterations |

---

## Iteration Tracking

### Score-Driven Steps (no max iterations — cost limit is the brake)

| Step | Gate | Threshold | Escalation |
|------|------|-----------|------------|
| CODE_REVIEW | `scores.overall` | `config.thresholds.code_review_pass` (8.0) | Cost limit only |
| VISUAL_QA | `scores.overall` | `config.thresholds.visual_qa_pass` (7.0) | Cost limit only |
| TEST_REVIEW | `scores.overall` | `config.thresholds.test_review_pass` (8.0) | Cost limit only |

These steps iterate until the score threshold is met. The cost limit (`max_per_run_usd`) is the safety brake — when hit, the pipeline escalates to the user.

### Counter-Driven Steps (max iterations — no score to converge toward)

| Counter | Incremented At | Max (Default) |
|---------|---------------|---------------|
| `test_fix` | Each TDD re-run after FIX_TESTS | 5 |
| `api_fix` | Each API_TESTS re-run after fix | 5 |
| `e2e_fix` | Each E2E_TESTS re-run after fix | 5 |

These steps have binary pass/fail (test execution), no numeric scores. Max iterations prevent infinite loops.

---

## Sub-Agent Mapping

| Step | Agent | What It Evaluates | Returns Scores | Uses Tools |
|------|-------|-------------------|---------------|------------|
| CODE_REVIEW | code-review-agent | Security, quality, docs, architecture | Yes (1-10 per category + overall) | No (text only) |
| VISUAL_QA | visual-qa-agent | Design quality, originality, craft, functionality | Yes (1-10 per category + overall + lighthouse) | Yes (Chrome DevTools MCP) |
| TEST_REVIEW | test-review-agent | Test quality, coverage, independence, mocks | Yes (1-10 per category + overall) | No (text only) |
| PHASE_GATE | qa-validator-agent | Business acceptance criteria (.aid/qa/*.yaml) | No (PASS/FAIL only) | No (text only) |

---

## State Schema (v2)

The `state.json` file tracks:

| Field | Purpose |
|-------|---------|
| `pipeline_status` | Current status (idle, running, paused, escalated, completed) |
| `current_phase` | 4 or 5 |
| `current_step` | Current step in the sequence |
| `current_task_id` | Task being worked on |
| `iterations` | Retry counters per step type |
| `cost` | Token counts and USD estimates per step and cumulative |
| `step_summaries` | Compressed context summaries per completed step |
| `last_review_result` | Full JSON from last sub-agent (including scores) |
| `step_history` | Ordered log of all step transitions with scores and timestamps |

---

## References

| File | Purpose |
|------|---------|
| `escalation-protocol.md` | What happens when limits are hit |
| `load-bearing-assumptions.md` | What each step assumes about model capabilities |
