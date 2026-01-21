---
description: Test phase-review-agent gate validation accuracy
---

# /test-phase-review

Test the phase-review-agent to verify it:
1. Correctly validates phase deliverables against checklist
2. Returns PASS only when ALL required items present
3. Returns FAIL for missing critical items
4. Provides specific location references

## Usage

```
/test-phase-review            # Full test with all phases
/test-phase-review --phase 1  # Test only Phase 1 validation
/test-phase-review --quick    # 2 scenarios only
/test-phase-review --verbose  # Show full agent responses
```

## What This Tests

### Phase Checklists

| Phase | Key Requirements |
|-------|------------------|
| 0 Discovery | Problem statement, stakeholders, research |
| 1 PRD | User stories, acceptance criteria, scope |
| 2 Tech Spec | Architecture, data model, security |
| 3 Impl Plan | Task breakdown, estimates, dependencies |

### Test Scenarios

| Scenario | Deliverables | Expected |
|----------|--------------|----------|
| Complete Phase 1 | All PRD items | PASS |
| Missing user stories | PRD without stories | FAIL |
| Missing security | Tech spec no security | FAIL |
| Partial deliverables | 80% complete | PARTIAL |

## Test Execution

When invoked, spawn a test agent:

```
Task(
  subagent_type: "general-purpose",
  prompt: "You are testing the phase-review-agent for accuracy.

OUTPUT TO: .aid/agent-tests/phase-review-test-{timestamp}/

## Test 1: Complete Phase 1 (Should PASS)

Create deliverables:
- prd/user-stories.md (3 user stories with AC)
- prd/requirements.md (functional requirements)
- prd/scope.md (MVP scope definition)

PHASE_CHECKLIST:
- [ ] User stories with acceptance criteria
- [ ] Functional requirements documented
- [ ] MVP scope clearly defined
- [ ] Stakeholder sign-off section

Run phase review. Expected: verdict = PASS

## Test 2: Missing User Stories (Should FAIL)

Create deliverables:
- prd/requirements.md ✓
- prd/scope.md ✓
- NO user-stories.md ✗

Expected: verdict = FAIL, blocking_issues includes 'User stories missing'

## Test 3: Missing Security (Phase 2, Should FAIL)

Create deliverables:
- tech-spec/architecture.md ✓
- tech-spec/data-model.md ✓
- NO security section ✗

Expected: verdict = FAIL, checklist 'Security considerations' = fail

## Test 4: Partial Deliverables (Should PARTIAL)

Create deliverables:
- All required files present ✓
- 1 user story missing acceptance criteria ✗

Expected: verdict = PARTIAL, suggestions include 'Add AC to Story 3'

## Report Format

Generate phase-review-test-report.md with results.
",
  description: "Test phase review agent"
)
```

## Expected Output

```
Phase Review Agent Test Complete
================================
Test ID: 20260120-143022

Test Results:
  Test 1 (Complete P1):     PASS ✓ (expected PASS)
  Test 2 (Missing Stories): FAIL ✓ (expected FAIL)
  Test 3 (No Security):     FAIL ✓ (expected FAIL)
  Test 4 (Partial):         PARTIAL ✓ (expected PARTIAL)

Checklist Accuracy:
  Required items:    8/8 correctly evaluated ✓
  Location refs:     All present ✓
  Blocking issues:   Actionable ✓

Overall: PASSED ✓

Report: .aid/agent-tests/phase-review-test-{timestamp}/report.md
```

## Verification Checks

The test verifies the agent:
- Evaluates EVERY checklist item (not skipping)
- Returns PASS only when ALL items pass
- Identifies specific missing items
- Provides file:line references
- Distinguishes critical vs minor issues
- Gives actionable blocking_issues

## Related Commands

- `/aid-test` - Full AID methodology test
- `/test-reflection` - Test reflection agent
- `/test-qa-validator` - Test QA validator agent
- `/test-all-agents` - Run all agent tests
