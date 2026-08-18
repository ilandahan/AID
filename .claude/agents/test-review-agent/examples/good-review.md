# Good Test Review Example

This shows a correct, well-calibrated test review response.

## What Makes This Good

1. **Cross-references implementation** — maps tests to actual functions
2. **Coverage map** — shows exactly what's tested and what's not
3. **Mock analysis with rationale** — each mock justified or flagged
4. **Specific file:line references** — every issue points to exact location
5. **Concrete fixes** — actionable, not vague

## Example Response

```json
{
  "review_id": "tr-2024-01-15T11:00:00Z",
  "timestamp": "2024-01-15T11:00:00Z",
  "verdict": "FAIL",
  "categories": {
    "test_quality": {
      "status": "FAIL",
      "issues": [
        {
          "severity": "MAJOR",
          "file": "tests/user.test.ts",
          "line": 34,
          "pattern": "Weak assertion",
          "description": "Test asserts `expect(result).toBeTruthy()` but result is an object — should check specific fields",
          "fix": "Change to: `expect(result).toEqual({ id: expect.any(String), name: 'John', email: 'john@example.com' })`"
        }
      ]
    },
    "coverage": {
      "status": "FAIL",
      "issues": [
        {
          "severity": "MAJOR",
          "file": "src/services/UserService.ts",
          "line": 67,
          "pattern": "Missing error test",
          "description": "deleteUser() has no test for 'user not found' error case. Function throws NotFoundError at line 72 but no test verifies this.",
          "fix": "Add test: `expect(deleteUser('nonexistent')).rejects.toThrow(NotFoundError)`"
        }
      ]
    },
    "independence": {
      "status": "PASS",
      "issues": []
    },
    "alignment": {
      "status": "PASS",
      "issues": [
        {
          "severity": "MINOR",
          "file": "tests/user.test.ts",
          "line": 15,
          "pattern": "Simplified test data",
          "description": "Test uses `{ name: 'a', email: 'a@a.com' }` — unrealistically simple",
          "fix": "Use realistic data: `{ name: 'Maria Garcia-Lopez', email: 'maria.garcia+test@example.com' }`"
        }
      ]
    },
    "production_safety": {
      "status": "PASS",
      "issues": []
    },
    "mock_analysis": {
      "status": "PASS",
      "issues": []
    }
  },
  "mock_analysis": {
    "total_dependencies": 5,
    "mocked_dependencies": 1,
    "mock_ratio_percent": 20,
    "mocked_items": [
      {
        "what": "EmailService",
        "why": "External SMTP boundary — would send real emails",
        "acceptable": true
      }
    ],
    "internal_mocks_flagged": []
  },
  "coverage_assessment": {
    "functions_found": 4,
    "functions_with_happy_path": 4,
    "functions_with_edge_cases": 2,
    "functions_with_error_cases": 2,
    "coverage_map": {
      "createUser": { "happy_path": "YES", "edge_cases": "YES", "error_cases": "YES" },
      "getUser": { "happy_path": "YES", "edge_cases": "YES", "error_cases": "NO" },
      "updateUser": { "happy_path": "YES", "edge_cases": "NO", "error_cases": "NO" },
      "deleteUser": { "happy_path": "YES", "edge_cases": "NO", "error_cases": "NO" }
    }
  },
  "summary": {
    "total_issues": 3,
    "critical": 0,
    "major": 2,
    "minor": 1
  },
  "strengths": [
    "Good use of test fixtures via beforeEach — each test starts with clean state",
    "Real test database used instead of mocking data layer",
    "createUser has comprehensive coverage including duplicate email edge case"
  ],
  "action_required": [
    "1. [MAJOR] Strengthen assertion in tests/user.test.ts:34 — check exact object shape, not truthiness",
    "2. [MAJOR] Add error case test for deleteUser() not-found scenario"
  ],
  "handoff": {
    "next_action": "fix_and_retry",
    "message": "Fix 2 MAJOR issues: strengthen weak assertion and add missing error test for deleteUser. Test independence and mock usage are solid."
  }
}
```
