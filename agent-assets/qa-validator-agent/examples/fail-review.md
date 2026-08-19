# Example: Failing QA Review

Task: AUTH-123 - Same task, but with issues

## Response

```json
{
  "task_id": "AUTH-123",
  "verdict": "FAIL",
  "results": {
    "must_achieve": [
      {"criterion": "Form submission blocked when invalid", "status": "FAIL", "file": "LoginForm.tsx", "line": 45, "finding": "Submit button not disabled", "suggestion": "Add disabled={!isValid}"}
    ],
    "must_not": [
      {"criterion": "Must NOT call API before validation", "status": "FAIL", "file": "LoginForm.tsx", "line": 32, "finding": "API call on every keystroke", "suggestion": "Move API call inside handleSubmit"}
    ],
    "best_practices": [
      {"criterion": "Unit tests exist", "status": "FAIL", "finding": "No test file found", "suggestion": "Create LoginForm.test.tsx"}
    ]
  },
  "summary": {"total_criteria": 7, "passed": 4, "failed": 3},
  "action_required": [
    "1. Add disabled={!isValid} to submit button (LoginForm.tsx:45)",
    "2. Move API call inside handleSubmit (LoginForm.tsx:32)",
    "3. Create LoginForm.test.tsx with validation tests"
  ],
  "can_proceed": false,
  "handoff": {"next_action": "fix_and_retry"}
}
```

## What Makes It Good FAIL Review

1. Specific line numbers (45, 32)
2. Clear findings ("Submit button not disabled")
3. Actionable suggestions ("Add disabled={!isValid}")
4. Numbered action list for developer

After 3 failed cycles: escalate to `human_review_required`
