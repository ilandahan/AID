---
name: pipeline-orchestrator-extended
description: Extended details for the pipeline orchestrator skill — edge cases, variable extraction, and complete transition logic.
---

# Pipeline Orchestrator — Extended Details

## Variable Extraction Guide

### For code-review-agent

**Step 1: Task Context**
```bash
# Read context
cat .aid/context.json
# Extract: task_id, task_description, current_step
```

Format for `{{TASK_CONTEXT}}`:
```
Task ID: [task_id]
Description: [task_description]
Phase: 4 - Development
Step: CODE_REVIEW
```

**Step 2: Changed Files**
```bash
# Get list of changed files (staged + unstaged)
git diff --name-only HEAD
# Also check untracked files that are part of the task
git status --porcelain
```

Read EACH changed file's full content. Concatenate as:
```
--- FILE: path/to/file1.ts ---
[file content]

--- FILE: path/to/file2.ts ---
[file content]
```

**Step 3: Tech Spec Excerpt**
```bash
# Read the tech spec
cat docs/tech-spec/*.md
```
Extract the section relevant to the current task. If unclear, include the full spec.

**Step 4: Code Standards**
```bash
cat .claude/agents/code-review-agent/references/review-rules.md
```
Include verbatim — do not summarize.

### For test-review-agent

**Step 1: Task Context**
Same as code-review-agent.

**Step 2: Implementation Files**
Read ALL production source files that were modified in the current task. These are the files being tested.

**Step 3: Test Files**
Read ALL test files that correspond to the implementation files. Check common patterns:
- `src/foo.ts` → `tests/foo.test.ts`, `__tests__/foo.test.ts`, `src/foo.spec.ts`
- `src/services/UserService.ts` → `tests/services/UserService.test.ts`

**Step 4: Test Results**
Run the test command and capture output:
```bash
npm test 2>&1
```
Include full output (pass/fail counts, error messages, coverage if available).

---

## Transition Logic (Detailed)

### DEVELOP → CODE_REVIEW

**Trigger:** Developer signals implementation is ready.

**Actions:**
1. Run `git diff --name-only HEAD` to identify changed files
2. Read all changed files
3. Read tech spec excerpt
4. Read code standards reference
5. Construct code-review-agent prompt with variables
6. Spawn agent
7. Update state: `current_step: "CODE_REVIEW"`, increment `iterations.code_review`

### CODE_REVIEW → TDD (on PASS)

**Trigger:** Agent returns `verdict: "PASS"`

**Actions:**
1. Store review result in `last_review_result`
2. Log to `step_history`
3. Update state: `current_step: "TDD"`
4. Display: "Code review PASSED. Proceeding to TDD..."

### CODE_REVIEW → FIX_CODE (on FAIL)

**Trigger:** Agent returns `verdict: "FAIL"` OR `scores.overall < config.thresholds.code_review_pass`

**Actions:**
1. Check `iterations.code_review` < `max_iterations.code_review`
2. If at max → ESCALATE
3. Store FULL review result in `last_review_result` (including scores, score_justification, biggest_gaps)
4. Display full review context using the FIX_CODE template from SKILL.md:
   - Overall score and per-category scores
   - Score justification and biggest gaps
   - All `action_required` items with file:line references
   - Which categories need the most improvement (lowest scores)
5. Update state: `current_step: "FIX_CODE"`
6. Developer applies fixes, prioritizing lowest-scoring categories
7. After fixes → return to CODE_REVIEW (loop)

### TDD → VISUAL_QA (on PASS)

**Trigger:** All tests pass (exit code 0)

**Actions:**
1. Capture test output
2. Check if VISUAL_QA should run:
   - `config.visual_qa.enabled` must be `true`
   - If `config.visual_qa.skip_if_no_ui_changes` is `true`, check if any changed files are in `src/components/`, `src/pages/`, or contain JSX/TSX → if no UI files changed, skip to TEST_REVIEW
3. Check prerequisites: dev server running + Chrome DevTools MCP available
4. If prerequisites fail → skip VISUAL_QA with warning, advance to TEST_REVIEW
5. If all checks pass → Update state: `current_step: "VISUAL_QA"`, proceed to visual-qa-agent spawn

### VISUAL_QA → TEST_REVIEW (on PASS)

**Trigger:** Agent returns `verdict: "PASS"` AND `scores.overall >= config.thresholds.visual_qa_pass`

**Actions:**
1. Store review result in `last_review_result`
2. Log lighthouse scores alongside visual scores in `step_history`
3. Update state: `current_step: "TEST_REVIEW"`
4. Display: "Visual QA PASSED (X.X/10). Lighthouse: A11y X, SEO X, BP X. Proceeding to test review..."

### VISUAL_QA → FIX_VISUAL (on FAIL)

**Trigger:** Agent returns `verdict: "FAIL"` OR `scores.overall < config.thresholds.visual_qa_pass`

**Actions:**
1. Check `iterations.visual_qa` < `max_iterations.visual_qa`
2. If at max → ESCALATE
3. Store FULL review result in `last_review_result` (including scores, lighthouse, issues, testing_summary)
4. Display full review context using the FIX_VISUAL template from SKILL.md
5. Update state: `current_step: "FIX_VISUAL"`
6. Developer applies visual fixes, prioritizing functionality > craft > design quality
7. After fixes → return to VISUAL_QA (loop)

### TEST_REVIEW (unchanged) — on PASS

### TDD → FIX_TESTS (on FAIL)

**Trigger:** Tests fail (non-zero exit code)

**Actions:**
1. Check `iterations.test_fix` < `max_iterations.test_fix`
2. If at max → ESCALATE
3. Display failing test output
4. Update state: `current_step: "FIX_TESTS"`
5. Developer fixes tests
6. After fixes → re-run tests (TDD loop)

### TEST_REVIEW → PHASE_GATE (on PASS)

**Trigger:** Agent returns `verdict: "PASS"`

**Actions:**
1. Store review result
2. Update state: `current_step: "PHASE_GATE"`
3. Spawn qa-validator-agent

### PHASE_GATE → API_TESTS (on PASS)

**Trigger:** QA validator returns `verdict: "PASS"` or `can_proceed: true`

**Actions:**
1. Update state: `current_phase: 5`, `current_step: "API_TESTS"`
2. Display: "Phase 4 complete. Advancing to Phase 5: QA & Ship"
3. Reset Phase 5 iteration counters

### Phase 5 transitions follow the same PASS/FAIL pattern.

### CERTIFICATION

**Actions:**
1. Run ALL test commands from config in sequence:
   - `npm test` (unit)
   - `npm test -- --testPathPattern=integration` (integration)
   - `npx playwright test` (e2e)
   - `npm run cucumber` (cucumber)
2. Run `npm test -- --coverage` for coverage report
3. Verify coverage >= `min_coverage_percent` threshold
4. If all pass: set `pipeline_status: "completed"`, archive to `history.json`
5. Generate certification report

---

## Edge Cases

### No `.aid/context.json`

If context file doesn't exist when `/pipeline` is called:
- Display error: "No active task found. Set up a task context first with `/context-update`"
- Do not initialize pipeline

### Pipeline Already Running

If `state.json` exists with `pipeline_status: "running"`:
- Display current state
- Ask: "Pipeline already active at step [X]. Resume from here? (y/n)"

### Pipeline Already Completed

If `state.json` exists with `pipeline_status: "completed"`:
- Display: "Previous pipeline completed for task [X]. Start new pipeline? (y/n)"
- If yes, archive old state and initialize fresh

### Sub-Agent Parse Error

If agent returns non-JSON or malformed response:
- Log the raw response
- Display: "Sub-agent returned unexpected format. Treating as FAIL."
- Enter fix cycle as if FAIL

### Config File Missing

If `.aid/pipeline/config.json` doesn't exist:
- Create with default values
- Display: "Created pipeline config with defaults. Edit `.aid/pipeline/config.json` to customize."

### Test Command Not Found

If test command fails with "command not found":
- Display: "Test command `[command]` not found. Update `.aid/pipeline/config.json` test_commands."
- Set `pipeline_status: "paused"`
- Wait for user to fix config

---

## History Archive

When pipeline completes (CERTIFICATION passes), append to `.aid/pipeline/history.json`:

```json
{
  "runs": [
    {
      "task_id": "TASK-001",
      "started_at": "ISO-8601",
      "completed_at": "ISO-8601",
      "total_steps": 12,
      "iterations": { "code_review": 2, "test_fix": 1, "test_review": 1, "api_fix": 0, "e2e_fix": 0 },
      "final_scores": {
        "code_review": { "security": 9, "code_quality": 8, "documentation": 7, "architecture": 8, "overall": 8.1 },
        "test_review": { "test_quality": 8, "coverage": 7, "independence": 9, "alignment": 8, "production_safety": 10, "mock_analysis": 8, "overall": 8.2 }
      },
      "step_history": [...]
    }
  ]
}
```

---

## Pipeline Status Display

When `/pipeline-status` is invoked, read `state.json` and display:

```
Pipeline Status
Task: [task_id] — [description]
Phase: [current_phase]
Step: [current_step]
Status: [pipeline_status]
Started: [started_at]
Last Updated: [last_updated]

Iterations:
  Code Review: [N]/[max]
  Test Fix: [N]/[max]
  Test Review: [N]/[max]
  API Fix: [N]/[max]
  E2E Fix: [N]/[max]

Step History:
  1. DEVELOP → PASS (10:00)
  2. CODE_REVIEW → FAIL — 5.8/10 [security: 4, quality: 7, arch: 7, docs: 5] (10:05)
  3. FIX_CODE → done (10:10)
  4. CODE_REVIEW → PASS — 7.6/10 [security: 8, quality: 7, arch: 8, docs: 7] (10:15)
  ...

Last Review:
  Score: [overall]/10 (threshold: [from config])
  [Per-category scores]
  [Summary of biggest_gaps]
  [Summary of action_required]
```
