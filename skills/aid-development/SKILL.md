---
name: aid-development
description: AID Phase 4 - Development phase. Use for implementing features, TDD practices, code reviews, transitioning from planning to QA.
---

# Development Phase Skill

Phase 4. Purpose: implement solution with quality built-in through TDD.
Entry: tech spec completed, architecture defined.
Exit: all features implemented, tests passing, code reviewed.

Deliverables:
1. **Production Code** - Clean, documented, follows standards
2. **Test Suite** - Unit, integration, E2E, >80% coverage
3. **Documentation** - Code docs, API docs, README updates

## MANDATORY: QA Gate After EVERY Task

**Iron Rule:** Task complete → Spawn QA → Wait for result → PASS? Next task : Fix

Per-task flow:
1. Read task + QA criteria (`.aid/qa/{task-id}.yaml`)
2. Implement task (TDD)
3. Signal complete (TodoWrite)
4. **SPAWN QA SUB-AGENT** (mandatory):
```
Task(
  subagent_type="aid:qa-validator-agent",   # link-project route only: "qa-validator-agent"
  prompt="Task {TASK-ID}. Acceptance criteria: .aid/qa/{TASK-ID}.yaml. Changed files: [paths]. Return JSON with verdict: PASS or FAIL.",
  description="QA validation for {TASK-ID}"
)
```
5. Save the validator's JSON report as `.aid/qa/reports/{task-id}-report-{N}.json` (N = QA cycle).
6. Process QA report → PASS: record the pass (below), then proceed to next task. FAIL: fix issues in `action_required`, spawn QA again.

Recording a PASS. The Phase 4 QA Stop gate lets the task end only when `.aid/state.json`
holds a QA pass for the task's current criteria file. The one way to record it is this
command, which Claude Code asks the user to confirm:
```
python "${CLAUDE_PLUGIN_ROOT}/hooks/aid_session.py" qa-pass <TASK-ID> --note "<short summary>"
```
Never create a marker or verdict file under `.aid/qa/` yourself: those files are refused,
and the gate ignores them. If the criteria file changes after the pass, the pass no longer
counts and QA must run again.

QA criteria file `.aid/qa/{task-id}.yaml`:
```yaml
criteria:
  must_achieve:    # What code MUST do
  must_not:        # What code must NEVER do
  not_included:    # Scope boundaries
  best_practices:  # Quality standards
```

QA sub-agent context (isolated):
- **Sees:** Epic goal, Story value, Acceptance criteria, Changed files
- **Does NOT see:** Tech Spec, Architecture, Developer notes

QA gate rules:

| Rule | Enforcement |
|------|-------------|
| Hard block | Cannot proceed until PASS |
| Max 3 cycles | After 3 FAILs, escalate to human |
| Check all criteria | Reports ALL failures |
| No skipping | Mandatory for all tasks |

When QA fails:
1. Read report at `.aid/qa/reports/{task-id}-report-{N}.json`
2. Fix each issue in `action_required`
3. Re-spawn QA
4. Repeat until PASS or max cycles

## TDD Workflow

RED (failing test) → GREEN (make pass) → REFACTOR (clean up) → REPEAT

| Phase | Rule |
|-------|------|
| RED | Test MUST fail first |
| GREEN | Minimal code to pass |
| REFACTOR | Tests still pass |

## Common Pitfalls

| Pitfall | Fix |
|---------|-----|
| Skipping TDD | Write tests first |
| Test-specific code | No `if is_test:` in prod |
| Over-mocking | <20% mocking |
| Happy path only | Test errors & edge cases |
| Weak assertions | Assert exact values |

## Code Quality

**Required:**
- [ ] Single responsibility functions
- [ ] DRY - no copy-paste
- [ ] Type hints on public functions
- [ ] Meaningful names
- [ ] Error handling

**Forbidden:**
- [ ] No `any` types
- [ ] No TODO/FIXME
- [ ] No commented-out code
- [ ] No test-specific branching

## Documentation Standards

Full rules and per-language examples: `references/documentation-standards.md`

**File-Level:**
```typescript
/**
 * @file UserService.ts
 * @description Purpose
 * @related ./UserRepository.ts
 */
```

**Function:**
```typescript
/**
 * Creates user account.
 * @param data - User input
 * @returns Created user
 * @throws {ValidationError} If email invalid
 */
```

## Phase Gate Checklist

- [ ] All features per spec
- [ ] All tests passing
- [ ] Edge cases tested
- [ ] Code reviewed
- [ ] No test-specific logic in prod
- [ ] Documentation updated
- [ ] **All tasks passed QA gate**

## Role Guidance

| Role | Focus |
|------|-------|
| PM | Clarifications, validate intent |
| Dev | TDD, implement to pass tests |
| QA | Review coverage, test scenarios |
| Tech Lead | Code review, standards |

## Handoff to QA

- Complete, tested code
- Test results + coverage
- Known issues (if any)
- Deployment instructions

## Pipeline Integration

When the automated pipeline is active (`.aid/pipeline/state.json` exists with `pipeline_status: "running"`), Phase 4 step sequencing is driven by the **pipeline-orchestrator** skill. Run `/pipeline` to start it; when inactive, the manual flow above applies.

| Without Pipeline | With Pipeline |
|-----------------|---------------|
| Developer decides when to review | Pipeline enforces CODE_REVIEW after DEVELOP |
| Developer decides when to write tests | Pipeline enforces TDD after CODE_REVIEW passes |
| Developer decides when to validate | Pipeline enforces TEST_REVIEW + PHASE_GATE |
| Manual flow | Automated state machine with retry loops |

Unchanged under pipeline: TDD workflow (RED-GREEN-REFACTOR), code quality standards, QA gate enforcement (same qa-validator-agent), documentation standards.

See `../pipeline-orchestrator/SKILL.md` for full pipeline documentation.
