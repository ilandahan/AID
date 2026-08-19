---
paths:
  - "**/*.test.ts"
  - "**/*.test.tsx"
  - "**/*.spec.ts"
  - "tests/**/*"
---

# Test Quality Rules

Rules for writing high-quality tests that catch real bugs.

---

## IRON RULE: Tests Must Be Able to Fail

A test that cannot fail provides zero value. It creates false confidence.

### Mutation Test Check

Before marking tests complete:

```typescript
// 1. Comment out the code being tested
// 2. Run the test - it MUST FAIL
// 3. Uncomment and run again - it MUST PASS
```

---

## Test Independence

**IRON RULE: Every test must pass alone AND in any order.**

```typescript
// BAD - shared mutable state
let counter = 0;
describe('Counter', () => {
  test('increment', () => {
    counter++;
    expect(counter).toBe(1); // Fails if other tests ran first
  });
});

// GOOD - fresh state per test
describe('Counter', () => {
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

---

## Strong vs Weak Assertions

```typescript
// WEAK - always passes, catches nothing
test('calculateTotal works', () => {
  const result = calculateTotal([{ price: 10 }]);
  expect(result).toBeDefined();      // Passes even if result is 0
  expect(result).toBeTruthy();       // Passes if any non-zero
  expect(typeof result).toBe('number'); // Passes for any number
});

// STRONG - fails if implementation is wrong
test('should_sum_all_item_prices', () => {
  const items = [{ price: 10 }, { price: 20 }, { price: 5 }];
  const result = calculateTotal(items);
  expect(result).toBe(35);           // Exact value
});
```

---

## Assertion Anti-Patterns

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| `expect(x).toBeDefined()` | Almost never fails | `expect(x).toBe(value)` |
| `expect(x).toBeTruthy()` | Passes for many values | `expect(x).toBe(true)` |
| `expect(arr.length).toBeGreaterThan(0)` | Doesn't verify contents | `expect(arr).toEqual([...])` |
| `expect(fn).not.toThrow()` | Doesn't verify result | Assert return value |
| No assertions at all | Test always passes | Add meaningful assertions |

---

## Verification Commands

Before marking tests complete:

```bash
# 1. All tests pass
npm test

# 2. Tests pass in random order
jest --randomize
# OR
vitest --sequence.shuffle

# 3. Run multiple times (flaky check)
npm test && npm test && npm test
```

---

## Run All Tests Requirement

**IRON RULE: ALL existing tests must pass before marking complete.**

```bash
# Run full test suite
npm test

# Expected:
# - All tests pass
# - No skipped tests without documented reason
# - No console errors
```

---

## Checklist

- [ ] Every test has at least one assertion
- [ ] Assertions check specific values, not just existence
- [ ] Error paths have assertions (not just no-throw)
- [ ] Tests pass when run in isolation
- [ ] Tests pass in random order (`--randomize`)
- [ ] Mutation test passed (test fails when code breaks)
- [ ] ALL existing tests still pass
