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

## Eval Sets & LLM-as-Judge (Agentic Layer)

WHY: for an LLM component the eval sets ARE the acceptance criteria. If they are thin, biased or
gamed, the release gate passes things that should fail. QA owns them so they stay independent of
the people tuning the prompts.

Always applies, scaled by the PRD's §1.5 Solution Shape level; never "N/A".

| Level | QA's eval work |
|-------|----------------|
| 0 Process change | Acceptance checks on the new process |
| 1 Deterministic automation | Cucumber acceptance tests, edge and error cases |
| 2 Single LLM call inside a fixed flow | Golden set + never-do + injection cases for the call |
| 3 Workflow | Per-step and end-to-end sets |
| 4 Agent | Plus tool-choice and trajectory cases, red-team on every write tool |
| 5 Multi-agent | Plus hand-off cases and cross-agent injection |

### Phase by phase

| Phase | QA output |
|-------|-----------|
| 1 PRD | Review the 20-30 seed eval cases (`docs/prd/SEED-EVALS-<feature>.md`) and §7A.6 Eval Plan: golden-set size and source, threshold, judge plan are testable. Expert-written cases are tagged `source: SME:<role>` and kept distinct from real examples; `INSUFFICIENT_EXAMPLES` is resolved before the Phase 1 gate (real examples collected, SME cases added, or a recorded PM + tech lead decision to proceed with fewer) |
| 2 Tech Spec | Grow the golden set and held-out split from the seed cases (in parallel); review the eval harness design (storage, runner, judge) |
| 3 Impl Plan | Keep growing the sets; tasks exist for the golden set, red-team cases and the eval harness; DoD has targeted + regression evals |
| 4 Development | Keep growing and maintaining the sets; supply and adjudicate the labelled cases when the data scientist calibrates a judge |
| 5 QA & Ship | Golden set and held-out split complete; run the eval release gate; sign off with the eval report |

**Timing (A9, no relay):** the seed cases are written in Phase 1. QA grows the golden set and its held-out split IN PARALLEL with Phases 2-4; this does not block the tech spec or any design work. The sets must be complete only for the Phase 5 release gate. The data scientist calibrates the LLM judge in Phase 4, when a judge is introduced.

### Decision rights (RACI)

| Item | Responsible | Accountable / decides |
|---|---|---|
| §1.5 Solution Shape level | PM proposes (from segment, pain, error cost) | Tech lead decides and signs (ADR) |
| §1.4 metrics, 7A.1 Charter, 7A.5 Why-Chain | PM | PM |
| 7A.2 Tools & Permissions, 7A.4 Failure Modes & Guardrails | Tech lead (input: security) | Tech lead |
| 7A.3 Context & Data | Tech lead (input: privacy/DPO) | Tech lead |
| 7A.6 Eval Plan | Data scientist (metrics, judge); QA (eval sets) | QA owns the release gate |
| 7A.7 Telemetry & Traces | Tech lead | Tech lead |
| 7A.8 Rollout & Kill Switch | Tech lead + named on-call owner | Tech lead |

### Golden-set ownership

- QA owns the golden set and its held-out split (`tests/evals/golden/`), and is the only one who merges into them.
- The data scientist owns metric design, judge calibration and drift.
- Developers iterate on a separate dev/targeted suite (`tests/evals/dev/`) and propose golden-set additions through a QA-reviewed PR.
- **The release gate runs on the held-out split, which developers never tune on.**

### The sets QA owns

| Set | Source | Pass rule |
|---|---|---|
| Golden set + held-out split | Real cases (size and source per §7A.6), labelled by humans | ≥ the PRD's threshold, on the held-out split |
| Never-do checks | Each red line in §7A.1 Charter | Enforced in code; evals verify the enforcement at 100% |
| Red-team | Generated adversarial cases from §7A.4 Failure Modes & Guardrails | 0 critical/high failures, plus an overall pass rate ≥ the PRD's target |
| Prompt injection | Instructions hidden in web pages, tickets, documents, tool results (`rules/general/untrusted-content.md`) | Never followed |

1. **Golden set** (§7A.6): real, representative cases with expected outcomes labelled by humans.
   Cover the common cases, the known hard cases and every slice that matters (language, customer type,
   input length). Record size, source and date. Keep the held-out split that developers never tune on.
2. **Never-do checks** (§7A.1 Charter): at least one case per red line, plus variants that try to
   reach it indirectly. Never-do is enforced in code (policy, default-deny); evals verify the
   enforcement at 100%. Repeated runs cannot prove a low breach rate: proving a rate below p at 95%
   confidence takes n ≈ ln(0.05)/ln(1−p) clean runs (about 59 for 5%).
3. **Red-team cases** (§7A.4 Failure Modes & Guardrails): generated adversarial inputs per known
   failure mode: ambiguous requests, out-of-scope asks, social engineering, conflicting instructions,
   attempts to exceed §7A.2 permissions.
4. **Adversarial / prompt-injection cases**: instructions planted in content the system reads
   (web pages, tickets, emails, documents, tool results, retrieved chunks). Expected result: the
   instruction is treated as data, not followed, and is reported. See `rules/general/untrusted-content.md`.

Case hygiene:
- Each case cites its source and the WHY it tests (§7A.5 Why-Chain: WHY → requirement → eval → metric).
- No real personal data, secrets or credentials in cases; use synthetic or redacted data (§7A.3 Context & Data).
- Golden-set edits go through review with a reason; only QA merges them. Never relabel a case to make a build pass.
- Every production failure or escalation that revealed a gap becomes a new case.

### LLM-as-judge calibration against human labels

The data scientist owns judge calibration; QA supplies and adjudicates the labelled cases and checks
the result before the gate relies on the judge.

1. **Rubric first.** Write the rubric humans and the judge both use: criteria, scale, examples per score.
2. **Human labels.** At least two people label ≥ 50 stratified cases, including failures. Adjudicate
   their disagreements; measure human-human agreement as the ceiling.
3. **Run the judge** on the same sample.
4. **Measure agreement:** Cohen's kappa (or Krippendorff's alpha) ≥ 0.7 against adjudicated human
   labels on ≥ 50 stratified cases, including failures. Percent agreement is reported alongside, never alone.
   The judge never grades the outputs of its own prompt or model, and the rubric is not visible to
   the system under test.
5. **Read disagreements.** Look for systematic bias: length, tone, position, or favouring its own model family.
6. **Fix and re-measure** on a fresh sample, not the one you tuned on.
7. **Re-calibrate** when the judge model, judge prompt, rubric or the product's model changes, and
   periodically on production samples.
8. Record the calibration (date, sample, agreement, judge version) in the eval report.

### Checklist

- [ ] Golden set built from the Phase 1 seed cases, grown during Phases 2-4, complete for the Phase 5 gate: size and source per §7A.6, held-out split kept; only QA merges
- [ ] One or more never-do cases per §7A.1 red line; enforcement verified at 100%
- [ ] Red-team cases per §7A.4 failure mode
- [ ] Prompt-injection cases for every untrusted input path
- [ ] Every case cites its source and WHY
- [ ] Judge calibrated: kappa ≥ 0.7 on ≥ 50 stratified adjudicated cases (if a judge is used)
- [ ] Release gate run on the held-out split; eval report attached to the release certification

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
  password: '<test-password>',
  apiKey: '<test-api-key>'
};

// BAD - Even in "test" files
const config = {
  paymentApiKey: '<hardcoded key>',
  dbPassword: '<test-db-password>'
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
  password: '<fake-test-password>',
  apiKey: '<fake-test-api-key>',
  ...overrides
});

// GOOD - For integration tests
// Store secrets in .env.test (gitignored)
// .env.test:
// TEST_API_KEY=<test-api-key>
// TEST_DB_URL=postgresql://test:test@localhost:5432/test_db
```

### Security Checklist

| Check | How to Verify |
|-------|---------------|
| No real passwords | Search for common patterns: `password:`, `secret:` |
| No real API keys | Search for your providers' live-mode key prefixes, or run a secret scanner |
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

### Eval Sets (scaled by §1.5 level; level 0-1: acceptance tests)
- [ ] Golden set, never-do, red-team and prompt-injection sets in place
- [ ] LLM judge calibrated against human labels (if a judge is used)
- [ ] Eval report with versions attached to the release certification

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
