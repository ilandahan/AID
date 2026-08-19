---
description: "Run Phase 5 QA validation, acceptance testing, and release preparation"
---

# /qa-ship — QA Validation and Release

Run Phase 5 QA validation, acceptance testing, and release preparation.

## Skills Loaded

This command loads:
- `skills/aid-qa-ship/SKILL.md`
- `skills/cucumber-bdd/SKILL.md` (for Gherkin acceptance verification)
- `skills/test-driven/SKILL.md` (for test quality validation)

## When to Use

- Phase 4 (Development) is complete and all tasks passed QA gates
- Ready to validate the full implementation against acceptance criteria
- Preparing for release and deployment

## Prerequisites

- Current phase must be 4 (ready to transition) or 5
- All development tasks must have passed their QA gates
- Test suite must be passing

## Process

1. **Cucumber Acceptance Verification**
   - Run `npm run cucumber:dry` — verify no undefined steps
   - Run `npm run cucumber` — all scenarios must pass
   - Run `npm run test:critical` — all @critical scenarios must pass
   - Review HTML report at `reports/cucumber-report.html`

2. **Test Quality Gates**
   - Run `npm test` — all tests pass with 0 failures
   - Run tests in random order (`--randomize`) — verify independence
   - Check for hardcoded credentials in test code
   - Verify all existing tests still pass (no regressions)
   - Mutation test — verify tests catch real bugs

3. **Non-Functional Validation**
   - Performance meets requirements
   - Security scan passed
   - Accessibility checked

4. **Release Preparation**
   - Prepare release notes
   - Verify rollback procedure
   - Get stakeholder sign-off
   - Schedule deployment

## Output

```
QA & Ship Status

Cucumber: [X] scenarios passed, [Y] failed
Tests: [X] passed, [Y] failed
Coverage: [X]%
Critical Scenarios: ALL PASSED / [N] FAILED

Release Readiness: READY / NOT READY
Blockers: [list if any]
```

## Related Commands

- `/pipeline` — Automated pipeline (includes QA steps)
- `/write-tests` — Write additional tests
- `/test-review` — Review test quality
- `/gate-check` — Check phase gate requirements
