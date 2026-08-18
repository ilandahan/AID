---
description: Test qa-validator-agent criteria checking accuracy
---

# /test-qa-validator

Test the qa-validator-agent to verify it:
1. Correctly validates code against criteria files
2. Catches violations in must_achieve and must_not
3. Provides specific file:line references
4. Returns proper PASS/FAIL verdicts

## Usage

```
/test-qa-validator            # Full test with all criteria types
/test-qa-validator --quick    # 2 scenarios only (1 pass, 1 fail)
/test-qa-validator --verbose  # Show full agent responses
```

## What This Tests

### Criteria Types

| Type | Purpose | Test |
|------|---------|------|
| must_achieve | Required functionality | Code MUST do X |
| must_not | Forbidden actions | Code MUST NOT do Y |
| not_included | Scope boundaries | Verify scope respected |
| best_practices | Quality standards | Tests, accessibility, etc. |

### Test Scenarios

| Scenario | Criteria | Code | Expected |
|----------|----------|------|----------|
| All criteria met | Email validation | Good validator | PASS |
| Must_achieve violated | Error display | No error UI | FAIL |
| Must_not violated | No console logs | Has console.log | FAIL |
| Best practice missed | Unit tests | No tests | FAIL (warn) |

## Test Execution

When invoked, spawn a test agent:

```
Task(
  subagent_type: "general-purpose",
  prompt: "You are testing the qa-validator-agent for accuracy.

OUTPUT TO: .aid/agent-tests/qa-validator-test-{timestamp}/

## Setup: Create Test Criteria File

Create qa/TEST-QA-001.yaml:
```yaml
schema_version: '1.0'
task_id: 'TEST-QA-001'
task_name: 'Email validation for login'

business_context:
  epic_goal: 'Reduce failed logins by 40%'
  user_value: 'Users get clear feedback'

criteria:
  must_achieve:
    - 'Email format is validated'
    - 'Error message displays below input'
    - 'Form blocked when invalid'

  must_not:
    - 'Must NOT log email to console'
    - 'Must NOT allow submission with invalid email'

  best_practices:
    - 'Unit tests exist'
    - 'Accessible error messages'

files_to_review:
  - 'test-code/email-validator.ts'
```

## Test 1: Code Passes All Criteria

Create email-validator.ts that:
- Validates email format ✓
- Shows error below input ✓
- Blocks invalid submissions ✓
- NO console.log ✓
- Has unit tests ✓

Run QA validation. Expected: verdict = PASS, all criteria pass

## Test 2: Code Violates must_achieve

Create failing-validator.ts that:
- Validates email format ✓
- NO error display ✗ (violates must_achieve)
- Blocks invalid submissions ✓

Expected: verdict = FAIL, must_achieve[1] status = fail

## Test 3: Code Violates must_not

Create logging-validator.ts that:
- All must_achieve met ✓
- Has console.log(email) ✗ (violates must_not)

Expected: verdict = FAIL, must_not[0] status = fail

## Test 4: Missing best_practices

Create no-tests-validator.ts that:
- All must_achieve met ✓
- All must_not met ✓
- NO unit tests ✗ (best_practices)

Expected: verdict = PASS with warnings, best_practices[0] status = fail

## Report Format

Generate qa-validator-test-report.md with results table.
",
  description: "Test QA validator agent"
)
```

## Expected Output

```
QA Validator Agent Test Complete
================================
Test ID: 20260120-143022

Test Results:
  Test 1 (All Pass):        PASS ✓ (expected PASS)
  Test 2 (Must Achieve):    FAIL ✓ (expected FAIL)
  Test 3 (Must Not):        FAIL ✓ (expected FAIL)
  Test 4 (Best Practices):  PASS* ✓ (expected PASS with warning)

Criteria Detection:
  must_achieve violations:   1/1 detected ✓
  must_not violations:       1/1 detected ✓
  best_practices warnings:   1/1 detected ✓

File:Line References: All present ✓

Overall: PASSED ✓

Report: .aid/agent-tests/qa-validator-test-{timestamp}/report.md
```

## Verification Checks

The test verifies the agent:
- Checks EVERY criterion (not just some)
- Provides file:line references for findings
- Returns actionable suggestions for failures
- Correctly distinguishes PASS vs FAIL verdicts
- Handles edge cases (empty files, missing files)

## Related Commands

- `/aid-test` - Full AID methodology test
- `/test-reflection` - Test reflection agent
- `/test-phase-review` - Test phase review agent
- `/test-all-agents` - Run all agent tests
