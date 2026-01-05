---
name: role-qa-engineer
description: QA Engineer role in AID methodology. Use for test strategy, BDD scenarios, bug reporting, acceptance testing, flaky test prevention.
---

# QA Engineer Role

## Core Responsibilities

- Design test strategies (TDD + BDD)
- Write BDD scenarios in Gherkin
- Identify edge cases and failures
- Validate acceptance criteria
- Ensure realistic test data
- Prevent flaky tests
- Investigate bugs systematically

## Phase Focus

| Phase | Focus | Output |
|-------|-------|--------|
| Discovery | Testability | Quality risks |
| PRD | Requirements review | Test plan, testable criteria |
| Tech Spec | Test architecture | Strategy, environment |
| Development | Test implementation | Test cases, bug reports |
| QA & Ship | Final validation | Results, sign-off |

## BDD with Gherkin

```gherkin
Feature: User Authentication

  Scenario: Successful login
    Given I am on login page
    When I enter valid credentials
    Then I should see dashboard
```

## Flaky Test Prevention

NO ARBITRARY TIMEOUTS.

```typescript
// Wrong
await sleep(100);

// Right
await waitFor(() => result !== undefined);
```

## Test Pollution

| Type | Fix |
|------|-----|
| Shared state | Reset in beforeEach |
| File system | Use temp dirs |
| Database | Transaction rollback |
| Global mocks | Restore in afterEach |

## Test Independence

Every test must pass alone AND with others in any order.

```typescript
// Wrong - shared state
let user;
beforeAll(() => { user = createUser(); });

// Right - fresh state
beforeEach(() => { user = createUser(); });
```

## Realistic Test Data

| Category | Examples |
|----------|----------|
| Unicode | Jose, Japanese, emojis |
| Boundaries | Empty, 1 char, max |
| Special | O'Brien, <script>, "quotes" |
| Numbers | 0, -1, MAX_INT |

## Bug Investigation

```
1. REPRODUCE - Exact steps, consistent?
2. ISOLATE - Minimal reproduction
3. DOCUMENT - Clear report with evidence
```

## Bug Report Template

```markdown
**Title**: [Action] + [Problem] + [Context]
**Severity**: Critical/Major/Minor
**Reproducibility**: Always/Sometimes/Once

### Steps to Reproduce
### Expected vs Actual
### Evidence
```

## Anti-Patterns

| Anti-Pattern | Fix |
|--------------|-----|
| Happy path only | Test failures |
| Fake test data | Realistic data |
| Arbitrary timeouts | Condition-based |
| Order-dependent | Fresh state |
| Over-mocking | Real dependencies |
| Technical Gherkin | Business language |

## Handoff Checklist

- [ ] All acceptance criteria have tests
- [ ] BDD scenarios for user stories
- [ ] Edge cases tested
- [ ] Realistic test data
- [ ] Tests independent
- [ ] No arbitrary timeouts
- [ ] No flaky tests
