# Test Quality Rules (Condensed)

Quick reference for the test-review-agent. Distilled from review-checklist.md and anti-patterns.md.

---

## Critical Anti-Patterns (Auto-FAIL)

| Anti-Pattern | Detection Signal | Severity |
|---|---|---|
| Test-specific production code | `if is_test:`, `if NODE_ENV === 'test'` in implementation | CRITICAL |
| Hidden failures | `catch(e) {}` or `except: pass` in test code | CRITICAL |
| Tests modified to pass | Assertion weakened instead of fixing implementation | CRITICAL |
| No tests for critical path | Core business function has zero tests | CRITICAL |
| Hardcoded overfitting | Implementation returns hardcoded values matching test inputs | CRITICAL |

## Major Anti-Patterns (Auto-FAIL)

| Anti-Pattern | Detection Signal | Severity |
|---|---|---|
| Weak assertions | `toBeTruthy()`, `is not None`, `> 0` instead of exact values | MAJOR |
| Mock hell | > 5 `@patch` decorators or `jest.mock()` calls | MAJOR |
| Internal mocking | Mocking private/internal functions | MAJOR |
| No error tests | Zero `pytest.raises` / `expect().toThrow()` | MAJOR |
| Simplified data | `{ id: 1 }`, `"test"`, single-char values | MAJOR |
| Shared state | Class variables, global state, numbered tests | MAJOR |
| Happy path only | No edge cases, no boundary conditions, no null/empty | MAJOR |

## Minor Issues

| Issue | Detection Signal | Severity |
|---|---|---|
| Poor test names | `test_1`, `test_function`, no description | MINOR |
| Missing cleanup | No afterEach/teardown for resources | MINOR |
| Duplicate tests | Multiple tests verify identical behavior | MINOR |
| Slow tests | > 10s without justification | MINOR |
| Missing docs | No test docstrings explaining purpose | MINOR |

---

## Assertion Strength Guide

| Weak (Flag) | Strong (Accept) |
|---|---|
| `assert result` | `assert result == expected_value` |
| `assert result is not None` | `assert result.id == 42` |
| `expect(x).toBeTruthy()` | `expect(x).toEqual({ name: "John" })` |
| `assert len(result) > 0` | `assert len(result) == 3` |
| `expect(fn).toHaveBeenCalled()` | `expect(fn).toHaveBeenCalledWith(arg1, arg2)` |

---

## Mock Ratio Thresholds

| Ratio | Assessment |
|---|---|
| 0-10% | Excellent — real integration |
| 10-20% | Acceptable — within target |
| 20-40% | Warning — consider replacing mocks with test doubles |
| 40%+ | Fail — tests likely don't test real behavior |

## What Should Be Mocked

| Mock (Acceptable) | Don't Mock (Flag) |
|---|---|
| External HTTP APIs | Internal functions |
| Third-party SDKs | Database queries (use test DB) |
| Email/SMS services | Cache layer (use test Redis) |
| Payment processors | Business logic |
| Clock/time for determinism | File system (usually) |

---

## Coverage Requirements

For each public function in implementation:
- **Happy path**: At least 1 test with valid input → expected output
- **Edge cases**: null, empty string, boundary values, special characters
- **Error cases**: Invalid input → expected error/exception

Missing ANY category for a critical-path function → MAJOR.

---

## Test Independence Check

| Signal | Issue |
|---|---|
| `test_01_`, `test_02_` naming | Ordered dependencies |
| Class-level variables | Shared state |
| `setUp` modifies shared resource | Side effects leak |
| Test fails when run alone | Hidden dependency |
| Test fails in random order | Shared state |

---

## Production Safety Scan

Scan ALL implementation files (not test files) for:
```
is_test
test_mode
NODE_ENV === 'test'
process.env.TEST
__test__
mock_mode
```

Any match → CRITICAL. Production code must work identically in test and production.
