---
description: Run all agent tests in sequence or parallel
---

# /test-all-agents

Run comprehensive tests for all 4 AID sub-agents to verify they work correctly.

## Usage

```
/test-all-agents              # Run all tests sequentially
/test-all-agents --parallel   # Run tests in parallel (faster)
/test-all-agents --quick      # Quick version of each test
/test-all-agents --verbose    # Show all agent responses
```

## Agents Tested

| Agent | Purpose | Test Focus |
|-------|---------|------------|
| **aid-test-agent** | AID methodology validation | Phase 0-4 outputs, QA flow |
| **reflection-agent** | Quality evaluation | Context isolation, scoring accuracy |
| **qa-validator-agent** | Task validation | Criteria checking, PASS/FAIL verdicts |
| **phase-review-agent** | Phase gate validation | Checklist verification, deliverables |

## Test Execution

When invoked, run the four tests yourself, in this session, one after the other. Each test
spawns its agent by name; the agent returns its result as text (its verdict JSON) and is
not asked to write any file. You, the parent session, write every report file from the
returned results.

OUTPUT TO: `.aid/agent-tests/full-suite-{timestamp}/`

### Test Sequence

1. **AID Test Agent**: follow `/aid-test --quick`. Expected: all phases pass, QA validation
   works. Then write `aid-test-agent/report.md` from the returned results.
2. **Reflection Agent**: follow `/test-reflection --quick`. Expected: isolation verified,
   scoring accurate. Then write `reflection-agent/report.md` from the returned results.
3. **QA Validator Agent**: follow `/test-qa-validator --quick`. Expected: criteria checking
   accurate. Then write `qa-validator-agent/report.md` from the returned results.
4. **Phase Review Agent**: follow `/test-phase-review --quick`. Expected: gate validation
   accurate. Then write `phase-review-agent/report.md` from the returned results.

Each `report.md` holds the test table (test, expected, actual, pass) built from what the
agent returned. Do not ask a sub-agent to write it.

### Generate Combined Report

Then write `full-suite-report.md` yourself:

```
AID Agent Test Suite - Complete
===============================
Date: {timestamp}
Duration: X minutes

AGENT RESULTS
─────────────
| Agent | Tests | Pass | Fail | Status |
|-------|-------|------|------|--------|
| aid-test | 5 | 5 | 0 | ✓ PASS |
| reflection | 4 | 4 | 0 | ✓ PASS |
| qa-validator | 4 | 4 | 0 | ✓ PASS |
| phase-review | 4 | 4 | 0 | ✓ PASS |

OVERALL: 17/17 PASSED ✓

Individual Reports:
- aid-test-agent/report.md
- reflection-agent/report.md
- qa-validator-agent/report.md
- phase-review-agent/report.md
```

## Expected Output

```
AID Agent Test Suite Complete
=============================
Test Suite ID: 20260120-143022
Duration: 8 minutes

Agent Results:
  aid-test-agent:     5/5 passed ✓
  reflection-agent:   4/4 passed ✓
  qa-validator-agent: 4/4 passed ✓
  phase-review-agent: 4/4 passed ✓

Total: 17/17 tests passed (100%)

Overall: ALL AGENTS PASSED ✓

Reports saved to:
  .aid/agent-tests/full-suite-20260120-143022/
    ├── full-suite-report.md
    ├── aid-test-agent/
    ├── reflection-agent/
    ├── qa-validator-agent/
    └── phase-review-agent/
```

## What Each Test Verifies

### aid-test-agent
- Generates valid outputs for Phases 0-4
- Quality checks catch violations
- QA validation detects pass/fail correctly
- Phase gates enforced

### reflection-agent
- Context isolation (no conversation bias)
- Scoring accuracy (good >= 8, bad < 7)
- Auto-fail conditions work
- Provides actionable guidance

### qa-validator-agent
- Checks ALL criteria types
- Returns only PASS or FAIL: a missed best practice is a `warnings` entry, not a FAIL
- Provides file:line references
- Returns correct PASS/FAIL verdicts
- Handles edge cases

### phase-review-agent
- Validates against checklist
- Identifies missing items
- Provides location references
- Distinguishes PASS/PARTIAL/FAIL

## Troubleshooting

### If a test fails:
1. Run the individual test with `--verbose` flag
2. Check the agent's response for specific errors
3. Review the test report for details
4. Fix any issues in agent prompts

### Common issues:
- **Scoring too high**: Reflection agent may need stricter criteria
- **Missing references**: Agents should always cite file:line
- **Wrong verdict**: Check criteria parsing logic

## Related Commands

- `/aid-test` - Full AID methodology test
- `/test-reflection` - Test reflection agent only
- `/test-qa-validator` - Test QA validator only
- `/test-phase-review` - Test phase review only
