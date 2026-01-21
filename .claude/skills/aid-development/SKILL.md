---
name: aid-development
description: AID Phase 4 - Development phase. Use for implementing features, TDD practices, code reviews, transitioning from planning to QA.
---

# Development Phase Skill

## MANDATORY: QA Gate After EVERY Task

**Iron Rule:** Task complete → Spawn QA → Wait for result → PASS? Next task : Fix

```
Task(
  subagent_type="general-purpose",
  prompt="You are a QA Validator. Read .aid/qa/{TASK-ID}.yaml and review modified files. Return JSON with verdict: PASS or FAIL.",
  description="QA validation for {TASK-ID}"
)
```

- PASS → Proceed to next task
- FAIL → Fix issues in `action_required`, spawn QA again

---

## Phase Overview

**Purpose:** Implement solution with quality built-in through TDD.

**Entry:** Tech spec completed, architecture defined
**Exit:** All features implemented, tests passing, code reviewed

## Deliverables

1. **Production Code** - Clean, documented, follows standards
2. **Test Suite** - Unit, integration, E2E, >80% coverage
3. **Documentation** - Code docs, API docs, README updates

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

## QA Gate Enforcement

### Per-Task Flow

1. Read Task + QA Criteria (`.aid/qa/{task-id}.yaml`)
2. Implement Task (TDD)
3. Signal Complete (TodoWrite)
4. **SPAWN QA SUB-AGENT** (mandatory)
5. Process QA Report → PASS: next task, FAIL: fix & retry

### QA Criteria Location

`.aid/qa/{task-id}.yaml`:
```yaml
criteria:
  must_achieve:    # What code MUST do
  must_not:        # What code must NEVER do
  not_included:    # Scope boundaries
  best_practices:  # Quality standards
```

### QA Sub-Agent Context (Isolated)

**Sees:** Epic goal, Story value, Acceptance criteria, Changed files
**Does NOT see:** Tech Spec, Architecture, Developer notes

### QA Gate Rules

| Rule | Enforcement |
|------|-------------|
| Hard block | Cannot proceed until PASS |
| Max 3 cycles | After 3 FAILs, escalate to human |
| Check all criteria | Reports ALL failures |
| No skipping | Mandatory for all tasks |

### When QA Fails

1. Read report at `.aid/qa/{task-id}-review-{N}.json`
2. Fix each issue in `action_required`
3. Re-spawn QA
4. Repeat until PASS or max cycles

---

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
