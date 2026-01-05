---
name: aid-development
description: AID Phase 4 - Development phase. Use for implementing features, TDD practices, code reviews, transitioning from planning to QA.
---

# Development Phase Skill

## Phase Overview

Purpose: Implement solution with quality built-in through TDD.

Entry: Tech spec completed, architecture defined, data models specified
Exit: All features implemented, tests passing, code reviewed

## Deliverables

1. Production Code - Clean, documented, follows standards
2. Test Suite - Unit, integration, E2E, >80% coverage
3. Documentation - Code docs, API docs, README updates

## TDD Workflow

```
RED (Write failing test) -> GREEN (Make pass) -> REFACTOR (Clean up) -> REPEAT
```

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

### Required
- [ ] Single responsibility functions
- [ ] DRY - no copy-paste
- [ ] Type hints on public functions
- [ ] Meaningful names
- [ ] Error handling

### Forbidden
- [ ] No `any` types
- [ ] No TODO/FIXME
- [ ] No commented-out code
- [ ] No test-specific branching

## Documentation Standards

Every file must have:

### File-Level
```typescript
/**
 * @file UserService.ts
 * @description Purpose of file
 * @related ./UserRepository.ts, ./UserController.ts
 * @created 2025-12-15 by AID
 */
```

### Function
```typescript
/**
 * Creates user account.
 * @param data - User input
 * @returns Created user
 * @throws {ValidationError} If email invalid
 * @related ../validators/emailValidator.ts
 */
```

## Phase Gate Checklist

- [ ] All features per spec
- [ ] All tests passing
- [ ] Realistic test data
- [ ] Edge cases tested
- [ ] Code reviewed
- [ ] No test-specific logic in prod
- [ ] Documentation updated

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
