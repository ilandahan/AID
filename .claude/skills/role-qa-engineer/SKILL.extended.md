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
| Hardcoded credentials | Use env vars or factories |
| Weak assertions | Assert specific values |
| Messy file organization | Follow directory structure |
| Tests that can't fail | Use mutation testing |

---

## Test Code Organization

### Directory Structure (REQUIRED)

Tests MUST be organized in this structure:

```
tests/
├── unit/                    # Fast, isolated tests (<100ms each)
│   ├── services/            # Business logic
│   │   └── user-service.test.ts
│   ├── utils/               # Utility functions
│   │   └── validation.test.ts
│   └── models/              # Data transformations
│       └── user-model.test.ts
├── integration/             # Real dependencies (DB, APIs)
│   ├── api/                 # HTTP endpoint tests
│   │   └── auth.integration.test.ts
│   ├── db/                  # Database tests
│   │   └── user-repository.integration.test.ts
│   └── external/            # Third-party integrations
│       └── payment-gateway.integration.test.ts
├── e2e/                     # End-to-end browser tests
│   ├── flows/               # User journey tests
│   │   └── login-flow.e2e.test.ts
│   └── visual/              # Screenshot comparisons
│       └── dashboard.visual.test.ts
├── fixtures/                # Test data factories
│   ├── users.ts
│   └── orders.ts
└── setup/                   # Global test configuration
    ├── jest.setup.ts
    └── test-database.ts
```

### File Naming Conventions

| Test Type | File Pattern | Example |
|-----------|--------------|---------|
| Unit | `*.test.ts` | `user-service.test.ts` |
| Integration | `*.integration.test.ts` | `api.integration.test.ts` |
| E2E | `*.e2e.test.ts` | `checkout-flow.e2e.test.ts` |
| Visual | `*.visual.test.ts` | `dashboard.visual.test.ts` |

### Test Naming Pattern

```typescript
// Format: should_[expectedBehavior]_when_[condition]
describe('UserService', () => {
  // ✅ Good - describes behavior and condition
  test('should_return_error_when_email_is_invalid', () => {});
  test('should_create_user_when_all_fields_valid', () => {});
  test('should_throw_duplicate_error_when_email_exists', () => {});

  // ❌ Bad - vague or technical
  test('test1', () => {});
  test('works correctly', () => {});
  test('validateEmail function', () => {});
});
```

---

## Security in Test Code

### IRON RULE: NO HARDCODED CREDENTIALS

**This applies to:**
- Test files
- README files
- Example code
- Fixtures
- Documentation

### ❌ NEVER Do This:

```typescript
// BAD - Real-looking credentials in code
const testUser = {
  email: 'admin@company.com',
  password: 'P@ssw0rd123!',
  apiKey: 'sk-live-abc123xyz'
};

// BAD - Even in "test" files
const config = {
  stripeKey: 'sk_test_abcdefg',
  dbPassword: 'mysecretpassword'
};
```

### ✅ ALWAYS Do This:

```typescript
// GOOD - Environment variables with safe defaults
const testUser = {
  email: process.env.TEST_USER_EMAIL || 'test@example.com',
  password: process.env.TEST_USER_PASSWORD || 'test-only-password-123'
};

// GOOD - Factory with clearly fake data
const createTestUser = (overrides = {}) => ({
  email: `test-${Date.now()}@example.com`,
  password: 'DefinitelyNotARealPassword',
  apiKey: 'test_key_not_real_00000000',
  ...overrides
});

// GOOD - For integration tests
// Store secrets in .env.test (gitignored)
// .env.test:
// TEST_API_KEY=sk_test_your_sandbox_key
// TEST_DB_URL=postgresql://test:test@localhost:5432/test_db
```

### Security Checklist

| Check | How to Verify |
|-------|---------------|
| No real passwords | Search for common patterns: `password:`, `secret:` |
| No real API keys | Search for `sk_live`, `pk_live`, real key prefixes |
| No credentials in README | Review all documentation examples |
| `.env.test` gitignored | Check `.gitignore` includes `*.env*` |
| Factories use fake data | Review fixture files |

See `references/security-in-tests.md` for detailed patterns.

---

## Test Independence Verification

### IRON RULE: Tests Must Run in Any Order

Every test MUST pass when run:
1. Alone
2. First in the suite
3. Last in the suite
4. In random order with all other tests

### Verification Commands

```bash
# Jest - Run in random order
jest --runInBand --randomize

# Jest - Run single test isolated
jest path/to/file.test.ts --testNamePattern="specific test name"

# Vitest - Shuffle order
vitest --sequence.shuffle

# Vitest - Run single test
vitest path/to/file.test.ts -t "specific test name"

# Pytest - Random order (install pytest-randomly)
pip install pytest-randomly
pytest --randomly-seed=random

# Run 5 times with different orders
for i in {1..5}; do jest --runInBand --randomize; done
```

### Common Independence Violations

```typescript
// ❌ BAD - Shared mutable state
let counter = 0;
describe('Counter tests', () => {
  test('increment', () => {
    counter++;
    expect(counter).toBe(1); // Fails if other tests ran first
  });
});

// ✅ GOOD - Fresh state per test
describe('Counter tests', () => {
  let counter: number;

  beforeEach(() => {
    counter = 0; // Reset before each test
  });

  test('increment', () => {
    counter++;
    expect(counter).toBe(1); // Always passes
  });
});
```

```typescript
// ❌ BAD - beforeAll creates shared state
let testUser: User;
beforeAll(async () => {
  testUser = await createUser(); // Same user for all tests
});

// ✅ GOOD - beforeEach creates fresh state
beforeEach(async () => {
  testUser = await createUser(); // New user for each test
});

afterEach(async () => {
  await deleteUser(testUser.id); // Clean up
});
```

### Independence Checklist

- [ ] No `let` variables at describe level (use `beforeEach`)
- [ ] No `beforeAll` for mutable state (use `beforeEach`)
- [ ] All tests have cleanup in `afterEach`
- [ ] Tests verified with `--randomize` flag
- [ ] Each test works when run in isolation

---

## Run All Tests Requirement

### IRON RULE: ALL EXISTING TESTS MUST PASS

Before marking ANY task complete:

```bash
# 1. Run the full test suite
npm test

# 2. Verify output shows:
#    - All tests pass
#    - No tests skipped
#    - No warnings about test pollution
#    - No console errors

# 3. Run again to check for flakiness
npm test
```

### Workflow for Test Changes

```
1. BEFORE making changes:
   └── npm test (record baseline - all should pass)

2. AFTER making changes:
   └── npm test (all must still pass)

3. IF any test fails:
   ├── Did YOUR change cause it?
   │   └── YES → Fix your code
   │   └── NO  → Document as pre-existing issue
   └── NEVER mark complete with failing tests
```

### Regression Prevention Checklist

| Step | Command | Expected |
|------|---------|----------|
| Baseline check | `npm test` | All pass |
| After changes | `npm test` | All pass |
| Random order check | `jest --randomize` | All pass |
| Flaky check (run 3x) | `npm test && npm test && npm test` | All pass each time |

---

## Assertion Quality - Prevent False Success

### IRON RULE: TESTS MUST BE ABLE TO FAIL

A test that cannot fail provides zero value. Worse, it provides false confidence.

### The "Mutation Test" Check

Before marking tests complete, verify they can actually catch bugs:

```typescript
// Step 1: Find the code being tested
function calculateTotal(items) {
  return items.reduce((sum, item) => sum + item.price, 0);
}

// Step 2: Comment out the implementation
function calculateTotal(items) {
  // return items.reduce((sum, item) => sum + item.price, 0);
  return 0; // <- Broken implementation
}

// Step 3: Run the test - it MUST FAIL
// If the test passes with broken code, your assertions are too weak

// Step 4: Restore code, test should pass again
```

### Weak vs Strong Assertions

```typescript
// ❌ WEAK - Always passes, catches nothing
test('calculateTotal works', () => {
  const result = calculateTotal([{ price: 10 }]);
  expect(result).toBeDefined();      // Passes even if result is 0
  expect(result).toBeTruthy();       // Passes if result is any non-zero
  expect(typeof result).toBe('number'); // Passes for any number
});

// ✅ STRONG - Fails if implementation is wrong
test('should_sum_all_item_prices', () => {
  const items = [
    { price: 10 },
    { price: 20 },
    { price: 5 }
  ];

  const result = calculateTotal(items);

  expect(result).toBe(35);           // Exact value
});

// ✅ STRONG - Tests edge cases
test('should_return_0_when_items_empty', () => {
  expect(calculateTotal([])).toBe(0);
});

test('should_handle_decimal_prices', () => {
  const items = [{ price: 10.50 }, { price: 20.75 }];
  expect(calculateTotal(items)).toBeCloseTo(31.25, 2);
});
```

### Assertion Anti-Patterns

| Anti-Pattern | Why It's Bad | Fix |
|--------------|--------------|-----|
| `expect(x).toBeDefined()` | Almost never fails | `expect(x).toBe(specificValue)` |
| `expect(x).toBeTruthy()` | Passes for any value | `expect(x).toBe(true)` or specific value |
| `expect(arr.length).toBeGreaterThan(0)` | Doesn't verify contents | `expect(arr).toEqual([...expected])` |
| `expect(fn).not.toThrow()` | Doesn't verify result | Assert the return value |
| No assertions at all | Test always passes | Add meaningful assertions |

### Assertion Quality Checklist

- [ ] Every test has at least one assertion
- [ ] Assertions check SPECIFIC values, not just existence
- [ ] Error paths verify the ERROR, not just that something threw
- [ ] "Mutation test" passed - code change causes test failure
- [ ] Edge cases have specific expected values

---

## Handoff Checklist

### Test Coverage
- [ ] All acceptance criteria have tests
- [ ] BDD scenarios written for user stories
- [ ] Edge cases tested
- [ ] Test data is realistic

### Test Quality
- [ ] Tests are independent (verified with `--randomize`)
- [ ] No arbitrary timeouts (condition-based waiting only)
- [ ] No flaky tests (ran 3+ times)
- [ ] Strong assertions (specific values, not just existence)
- [ ] "Mutation test" passed (tests fail when code breaks)

### Security
- [ ] No hardcoded credentials in test code
- [ ] No real API keys or secrets
- [ ] No credentials in README or documentation
- [ ] Sensitive data uses env vars or factories

### Organization
- [ ] Tests in correct directories (unit/integration/e2e)
- [ ] File naming follows conventions
- [ ] Test names describe behavior and condition

### Regression Prevention
- [ ] ALL existing tests still pass
- [ ] Tests run successfully in random order
- [ ] No test pollution detected

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
