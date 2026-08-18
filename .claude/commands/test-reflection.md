---
description: Test reflection-agent isolation and scoring accuracy
---

# /test-reflection

Test the reflection-agent to verify it:
1. Evaluates output WITHOUT conversation context bias
2. Correctly scores good content (>= 7)
3. Correctly fails bad content (< 7)
4. Provides specific, actionable feedback

## Usage

```
/test-reflection              # Full test with all scenarios
/test-reflection --quick      # 2 scenarios only (1 pass, 1 fail)
/test-reflection --verbose    # Show full agent responses
```

## What This Tests

### Context Isolation
The reflection-agent should evaluate ONLY based on:
- Original request (verbatim)
- Stated WHY
- Output to evaluate
- Files to verify
- Phase criteria

It should NOT have access to conversation history or reasoning.

### Scoring Accuracy

| Test Case | Expected Score | Why |
|-----------|----------------|-----|
| Good code with WHY headers | >= 8 | Meets all criteria |
| Good PRD with clear scope | >= 8 | WHY aligned, complete |
| Code without WHY | < 7 | Fails WHY alignment |
| PRD with implementation | < 7 | Phase violation |
| Security vulnerability | < 6 | Auto-fail condition |
| Output ignores request | < 5 | Fails completeness |

## Test Execution

When invoked, spawn a test agent:

```
Task(
  subagent_type: "general-purpose",
  prompt: "You are testing the reflection-agent for isolation and accuracy.

OUTPUT TO: .aid/agent-tests/reflection-test-{timestamp}/

## Test 1: Good Code (Should PASS >= 8)

Simulate reflection-agent evaluation with:
- ORIGINAL_REQUEST: 'Create an email validation function with clear error messages'
- STATED_WHY: 'Reduce failed logins by validating input before API calls'
- PHASE: 4 (Development)
- OUTPUT_TO_EVALUATE: [Good code with WHY headers, validation logic, tests]
- FILES_TO_VERIFY: [The generated code]

Run evaluation. Expected: score >= 8, pass = true

## Test 2: Bad Code - No WHY (Should FAIL < 7)

Same request, but OUTPUT_TO_EVALUATE is:
- Code WITHOUT WHY headers
- No connection documentation
- Missing test coverage

Expected: score < 7, pass = false, revision_guidance includes 'Add WHY header'

## Test 3: Phase Violation (Should FAIL < 6)

- ORIGINAL_REQUEST: 'Research competitors in the market'
- STATED_WHY: 'Understand market landscape before building'
- PHASE: 0 (Discovery)
- OUTPUT_TO_EVALUATE: [Contains implementation code]

Expected: score < 6 (auto-fail for phase violation)

## Test 4: Security Issue (Should FAIL < 6)

- ORIGINAL_REQUEST: 'Create login form handler'
- STATED_WHY: 'Secure user authentication'
- PHASE: 4 (Development)
- OUTPUT_TO_EVALUATE: [Code with SQL injection vulnerability]

Expected: score < 6 (auto-fail for security vulnerability)

## Report Format

Generate reflection-test-report.md with:
| Test | Expected | Actual | Pass? |
|------|----------|--------|-------|
| Good code | >= 8 | X.X | ✓/✗ |
| No WHY | < 7 | X.X | ✓/✗ |
| Phase violation | < 6 | X.X | ✓/✗ |
| Security issue | < 6 | X.X | ✓/✗ |

Detection Rate: X/4 (X%)
",
  description: "Test reflection-agent isolation"
)
```

## Expected Output

```
Reflection Agent Test Complete
==============================
Test ID: 20260120-143022

Test Results:
  Test 1 (Good Code):     8.2/10 PASS ✓ (expected >= 8)
  Test 2 (No WHY):        5.4/10 FAIL ✓ (expected < 7)
  Test 3 (Phase Violation): 4.1/10 FAIL ✓ (expected < 6)
  Test 4 (Security Issue):  3.8/10 FAIL ✓ (expected < 6)

Detection Rate: 4/4 (100%)
Isolation Verified: YES

Overall: PASSED ✓

Report: .aid/agent-tests/reflection-test-{timestamp}/report.md
```

## Isolation Verification

The test also verifies isolation by checking that the agent:
- Does NOT reference conversation history
- Does NOT mention "previous attempts"
- Does NOT give benefit of the doubt
- DOES cite specific file:line evidence
- DOES provide actionable revision guidance

## Related Commands

- `/aid-test` - Full AID methodology test
- `/test-qa-validator` - Test QA validation agent
- `/test-phase-review` - Test phase review agent
- `/test-all-agents` - Run all agent tests
