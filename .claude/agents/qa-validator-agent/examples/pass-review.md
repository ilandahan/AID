# Example: Passing QA Review

Task: AUTH-123 - Email format validation on login form

## Response

```json
{
  "task_id": "AUTH-123",
  "verdict": "PASS",
  "results": {
    "must_achieve": [
      {"criterion": "Email format validated before submission", "status": "PASS"},
      {"criterion": "Error message displays below invalid field", "status": "PASS"},
      {"criterion": "Form submission blocked when invalid", "status": "PASS"}
    ],
    "must_not": [
      {"criterion": "Must NOT log email to console", "status": "PASS"},
      {"criterion": "Must NOT call API before validation", "status": "PASS"}
    ],
    "not_included": [
      {"criterion": "Password validation (AUTH-124)", "status": "PASS", "note": "Correctly deferred"}
    ],
    "best_practices": [
      {"criterion": "Unit tests exist", "status": "PASS"}
    ]
  },
  "summary": {"total_criteria": 7, "passed": 7, "failed": 0},
  "can_proceed": true,
  "handoff": {"next_action": "proceed_to_next_task"}
}
```

## What Makes It Good

1. Every criterion checked
2. Scope respected (password validation deferred)
3. Best practices met (tests included)
4. Clear handoff to next task
