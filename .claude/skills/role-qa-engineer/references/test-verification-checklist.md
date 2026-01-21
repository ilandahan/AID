# Test Verification Checklist

## Purpose

This checklist ensures tests actually work before marking them complete. A test that passes but doesn't catch bugs is worse than no test - it provides false confidence.

---

## Pre-Completion Verification

### MUST Complete Before Marking Tests Done

| # | Check | Command/Action | Expected Result |
|---|-------|----------------|-----------------|
| 1 | All tests pass | `npm test` | 0 failures |
| 2 | Tests run in random order | `jest --randomize` | 0 failures |
| 3 | Tests can fail | Mutation test (see below) | Tests fail when code broken |
| 4 | No hardcoded credentials | Manual review | No secrets in code |
| 5 | Correct directory structure | Visual check | unit/integration/e2e |
| 6 | Existing tests still pass | `npm test` | Same pass count as before |

---

## 1. All Tests Pass

### Run Full Test Suite

```bash
# Run all tests
npm test

# Or with verbose output
npm test -- --verbose
```

### Expected Output

```
PASS  tests/unit/user-service.test.ts
PASS  tests/unit/validation.test.ts
PASS  tests/integration/api.integration.test.ts

Test Suites: 15 passed, 15 total
Tests:       47 passed, 47 total
Snapshots:   0 total
Time:        3.542s
```

### Red Flags

- ❌ Any test failures
- ❌ Tests marked as `.skip` or `.todo`
- ❌ Console errors or warnings
- ❌ "Test suite failed to run" messages

---

## 2. Tests Run in Random Order

### Why This Matters

Tests that pass in a specific order but fail when shuffled have hidden dependencies. These tests will fail randomly in CI, causing "flaky" builds.

### Verification Commands

```bash
# Jest - Random order
jest --runInBand --randomize

# Vitest - Shuffle
vitest --sequence.shuffle

# Pytest - Random (requires pytest-randomly)
pytest --randomly-seed=random

# Run multiple times to verify
for i in {1..5}; do npm test -- --randomize && echo "Run $i passed"; done
```

### Red Flags

- ❌ Tests pass normally but fail with `--randomize`
- ❌ Different results on different runs
- ❌ Tests that only pass when run first/last

---

## 3. Tests Can Actually Fail (Mutation Testing)

### The Problem

A test that always passes catches no bugs:

```typescript
// This test ALWAYS passes, even if calculateTotal is broken
test('calculateTotal works', () => {
  const result = calculateTotal([{ price: 10 }]);
  expect(result).toBeDefined(); // Always true!
});
```

### Manual Mutation Test

**Step 1:** Identify the function being tested

```typescript
// src/utils/calculate.ts
export function calculateTotal(items: Item[]): number {
  return items.reduce((sum, item) => sum + item.price, 0);
}
```

**Step 2:** Break the implementation

```typescript
// Temporarily modify
export function calculateTotal(items: Item[]): number {
  // return items.reduce((sum, item) => sum + item.price, 0);
  return 0; // BROKEN - always returns 0
}
```

**Step 3:** Run the test

```bash
npm test -- --testNamePattern="calculateTotal"
```

**Step 4:** Verify test FAILS

- ✅ Test fails → Test is good (catches the bug)
- ❌ Test passes → Test is bad (doesn't catch bugs)

**Step 5:** Restore the implementation

### What to Mutate

| Code Pattern | Mutation | Test Should Fail? |
|--------------|----------|-------------------|
| `return value` | `return null` | Yes |
| `if (condition)` | `if (!condition)` | Yes |
| `a + b` | `a - b` | Yes |
| `array.push(x)` | Comment out | Yes |
| `await api.call()` | `return mockData` | Yes |

### Automated Mutation Testing

```bash
# Install Stryker (JS/TS)
npm install --save-dev @stryker-mutator/core

# Run mutation testing
npx stryker run

# For Python
pip install mutmut
mutmut run
```

---

## 4. No Hardcoded Credentials

### Search Commands

```bash
# Search for common credential patterns
grep -rn "password.*=.*['\"]" tests/
grep -rn "secret.*=.*['\"]" tests/
grep -rn "sk_live\|pk_live" tests/
grep -rn "AKIA[A-Z0-9]" tests/

# Search for email patterns that look real
grep -rn "@company.com\|@corp.com" tests/
```

### Manual Review Checklist

- [ ] No real-looking passwords (not `test123`, but also not `CompanyPass2024!`)
- [ ] No API keys with real prefixes (`sk_live_`, `pk_live_`)
- [ ] No database URLs with real hostnames
- [ ] No emails with company domains
- [ ] Factory functions use clearly fake data

---

## 5. Correct Directory Structure

### Quick Visual Check

```bash
# List test directory structure
find tests -type f -name "*.test.ts" | head -20

# Expected structure:
# tests/unit/services/user-service.test.ts
# tests/unit/utils/validation.test.ts
# tests/integration/api/auth.integration.test.ts
# tests/e2e/flows/login.e2e.test.ts
```

### Checklist

- [ ] Unit tests in `tests/unit/`
- [ ] Integration tests in `tests/integration/`
- [ ] E2E tests in `tests/e2e/`
- [ ] File names follow convention (`*.test.ts`, `*.integration.test.ts`, etc.)
- [ ] Tests organized by domain/feature, not randomly placed

---

## 6. Existing Tests Still Pass

### Before Making Changes

```bash
# Record baseline
npm test 2>&1 | tee test-baseline.log

# Note the counts:
# Tests: 47 passed, 47 total
```

### After Making Changes

```bash
# Run tests again
npm test

# Verify same or more tests pass
# If any test now fails that passed before:
# - Your change broke something
# - Fix before marking complete
```

### Regression Check

```bash
# Quick comparison
npm test 2>&1 | grep "Tests:"
# Should show: Tests: 47 passed (or more)

# If fewer tests pass, investigate:
npm test -- --listTests  # See what tests exist
```

---

## Quick Verification Script

Create this script for quick verification:

```bash
#!/bin/bash
# tests/verify-tests.sh

echo "=== Test Verification ==="

echo -e "\n1. Running all tests..."
npm test || { echo "❌ FAIL: Tests not passing"; exit 1; }

echo -e "\n2. Running in random order..."
npm test -- --randomize || { echo "❌ FAIL: Order-dependent tests"; exit 1; }

echo -e "\n3. Checking for credentials..."
if grep -rqE "(password|secret|sk_live|AKIA).*=.*['\"]" tests/; then
  echo "❌ FAIL: Possible hardcoded credentials found"
  grep -rn "(password|secret|sk_live|AKIA).*=.*['\"]" tests/
  exit 1
fi

echo -e "\n4. Checking directory structure..."
if ! ls tests/unit tests/integration tests/e2e 2>/dev/null; then
  echo "⚠️  WARNING: Expected tests/unit, tests/integration, tests/e2e directories"
fi

echo -e "\n✅ All verification checks passed!"
```

---

## Red Flags Summary

| Red Flag | What It Means | Action |
|----------|---------------|--------|
| Tests fail | Broken implementation or test | Fix before completion |
| Random order fails | Hidden test dependencies | Add `beforeEach` setup |
| Mutation test passes | Weak assertions | Strengthen assertions |
| Credentials found | Security risk | Use env vars/factories |
| Tests in root | Poor organization | Move to correct dirs |
| Fewer tests than before | Regression introduced | Find and fix broken test |

---

## Definition of Done for Tests

Only mark tests complete when ALL of the following are true:

- [ ] `npm test` passes with 0 failures
- [ ] `npm test -- --randomize` passes with 0 failures
- [ ] At least one mutation test was performed (test fails when code broken)
- [ ] No hardcoded credentials (verified by search)
- [ ] Tests are in correct directories
- [ ] Test count is same or higher than before changes
- [ ] No `.skip` or `.todo` tests (unless documented why)
