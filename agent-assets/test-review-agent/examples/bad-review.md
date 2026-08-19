# Bad Test Review Example — Anti-Patterns to Avoid

This shows what a BAD test review looks like. Do NOT produce output like this.

## Anti-Pattern 1: No Cross-Reference with Implementation

```json
{
  "coverage_assessment": {
    "functions_found": 0,
    "functions_with_happy_path": 0,
    "functions_with_edge_cases": 0,
    "functions_with_error_cases": 0,
    "coverage_map": {}
  }
}
```

**Why this is wrong:**
- Reviewer didn't read the implementation files
- Coverage map is empty — must list EVERY public function
- Can't assess test quality without knowing what's being tested

## Anti-Pattern 2: Accepting Weak Assertions

```json
{
  "verdict": "PASS",
  "categories": {
    "test_quality": {
      "status": "PASS",
      "issues": []
    }
  }
}
```

When the test code contains:
```javascript
expect(result).toBeTruthy();
expect(result).toBeDefined();
assert result is not None
```

**Why this is wrong:**
- Weak assertions are ALWAYS at least MAJOR
- These tests provide false confidence
- A function returning `{ error: true }` would pass `toBeTruthy()`

## Anti-Pattern 3: Ignoring Mock Ratio

```json
{
  "mock_analysis": {
    "total_dependencies": 10,
    "mocked_dependencies": 8,
    "mock_ratio_percent": 80,
    "mocked_items": [],
    "internal_mocks_flagged": []
  },
  "categories": {
    "mock_analysis": {
      "status": "PASS",
      "issues": []
    }
  }
}
```

**Why this is wrong:**
- 80% mock ratio is far above the 20% target
- Status shows PASS despite extreme mocking
- No internal mocks flagged even though 8/10 are mocked
- Missing justification for each mock

## Anti-Pattern 4: Missing Production Safety Scan

```json
{
  "categories": {
    "production_safety": {
      "status": "PASS",
      "issues": []
    }
  }
}
```

When implementation contains:
```python
def process(data, is_test=False):
    if is_test:
        return mock_result
```

**Why this is wrong:**
- `is_test` parameter in production code is ALWAYS CRITICAL
- Reviewer failed to scan implementation files for test-specific code
- This is the #1 anti-pattern in production safety

## Anti-Pattern 5: Vague Fixes

```json
{
  "action_required": [
    "1. Improve test coverage",
    "2. Write better tests",
    "3. Add more assertions"
  ]
}
```

**Why this is wrong:**
- No file references
- No specific functions mentioned
- "Better" and "more" are not actionable
- Should be: "Add error case test for deleteUser() in tests/user.test.ts — expect NotFoundError when ID doesn't exist"
