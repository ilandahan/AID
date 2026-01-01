---
name: role-qa-engineer
description: QA Engineer role guidance within AID methodology. Use when assisting QA with test strategy, test case design, BDD scenarios, bug reporting, acceptance testing, flaky test prevention, or release certification. Triggers on test planning, bug investigation, Gherkin writing, or quality assurance tasks.
---

# QA Engineer Role

## Core Responsibilities

- Design comprehensive test strategies (TDD + BDD)
- Write BDD scenarios in Gherkin for acceptance tests
- Identify edge cases and failure scenarios
- Validate acceptance criteria are met
- Ensure realistic test data
- Prevent and fix flaky tests
- Investigate bugs systematically

## Phase-Specific Focus

| Phase | Focus | Key Outputs |
|-------|-------|-------------|
| Discovery | Testability requirements | Quality risks, test considerations |
| PRD | Requirements review | Test plan outline, testable criteria |
| Tech Spec | Test architecture | Test strategy, environment needs |
| Development | Test implementation | Test cases, bug reports |
| QA & Ship | Final validation | Test results, release sign-off |

## BDD with Gherkin

Write acceptance tests in business language:

```gherkin
Feature: User Authentication

  Scenario: Successful login
    Given I am on the login page
    When I enter valid credentials
    Then I should see the dashboard
```

### BDD Workflow

```
1. DISCOVERY   → PM + QA + Dev discuss behavior
2. FORMULATION → QA writes .feature files
3. AUTOMATION  → Dev writes step definitions
```

See `references/bdd-gherkin-guide.md` for syntax, patterns, and examples.

## Flaky Test Prevention

**Iron Law: NO ARBITRARY TIMEOUTS IN TESTS.**

### Condition-Based Waiting

```typescript
// ❌ Wrong - guessing
await sleep(100);
expect(result).toBeDefined();

// ✅ Right - waiting for condition
await waitFor(() => result !== undefined);
expect(result).toBeDefined();
```

See `references/condition-based-waiting.ts` for utilities.

## Test Pollution

Tests pass alone but fail together? Check for pollution:

| Type | Symptom | Fix |
|------|---------|-----|
| Shared state | Order-dependent | Reset in beforeEach |
| File system | Files left behind | Use temp dirs, clean up |
| Database | Stale data | Transaction rollback |
| Global mocks | Mock bleeds | Restore in afterEach |

Run `scripts/find-polluter.sh` to identify polluting test.

## Test Independence

**Every test must pass alone AND with any other tests in any order.**

```typescript
// ❌ Wrong - shared state
let user;
beforeAll(() => { user = createUser(); });

// ✅ Right - fresh state
beforeEach(() => { user = createUser(); });
```

## Realistic Test Data

Test with edge cases, not fake data:

| Category | Examples |
|----------|----------|
| Unicode | José, 日本語, émojis 🎉 |
| Boundaries | Empty, 1 char, max length |
| Special chars | O'Brien, `<script>`, "quotes" |
| Numbers | 0, -1, MAX_INT, decimals |

See `references/test-data-examples.md` for comprehensive examples.

## Bug Investigation

Before reporting, investigate:

```
1. REPRODUCE → Exact steps, consistent?
2. ISOLATE   → Minimal reproduction
3. DOCUMENT  → Clear report with evidence
```

See `references/bug-investigation-checklist.md` for complete process.

## Bug Report Template

```markdown
**Title**: [Action] + [Problem] + [Context]
**Severity**: Critical / Major / Minor
**Reproducibility**: Always / Sometimes / Once

### Steps to Reproduce
1. [Step]

### Expected vs Actual
Expected: [...]
Actual: [...]

### Evidence
[Screenshots, logs]
```

## Test Strategy Template

```markdown
### Test Approach
| Approach | Level | Format |
|----------|-------|--------|
| TDD | Unit/Integration | Code |
| BDD | Acceptance/E2E | Gherkin |

### Coverage Targets
- Unit: >80%
- Integration: Critical paths
- E2E: Happy paths
```

## Anti-Patterns

| Anti-Pattern | Fix |
|--------------|-----|
| Happy path only | Test failures and edge cases |
| Fake test data | Use realistic data |
| Arbitrary timeouts | Condition-based waiting |
| Order-dependent tests | Fresh state per test |
| Over-mocking (>20%) | Use real dependencies |
| Technical Gherkin | Use business language |
| Too many BDD steps | Keep 5-8 steps max |

## Handoff Checklist

- [ ] All acceptance criteria have tests
- [ ] BDD scenarios written for user stories
- [ ] Edge cases tested
- [ ] Test data is realistic
- [ ] Tests are independent
- [ ] No arbitrary timeouts
- [ ] No flaky tests

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/find-polluter.sh` | Find which test creates pollution |

## References

| File | When to Read |
|------|--------------|
| `references/bdd-gherkin-guide.md` | Writing acceptance tests |
| `references/condition-based-waiting.ts` | Fixing flaky tests |
| `references/test-data-examples.md` | Creating test cases |
| `references/bug-investigation-checklist.md` | Before reporting bugs |
