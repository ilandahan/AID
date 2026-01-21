---
name: aid-qa-ship
description: AID Phase 5 - QA and Release. Use for validating implementations, acceptance tests, preparing releases, deployment, operational readiness.
---

# QA & Ship Phase Skill

## Phase Overview

Purpose: Validate implementation meets requirements, ensure production readiness, ship with confidence.

Entry: Development complete, tests passing, code reviewed
Exit: Acceptance criteria verified, no blockers, deployed, stakeholders informed

## Deliverables

1. Test Results - All acceptance criteria covered
2. Release Certification - Checklist, stakeholder approvals
3. Release Notes - User-facing changelog
4. Deployment - Verified, monitoring active

## QA Testing Checklist

### Functional
- [ ] All user stories verified
- [ ] All acceptance criteria tested
- [ ] Edge cases covered
- [ ] Error handling tested
- [ ] Cross-browser/device (if applicable)

### Non-Functional
- [ ] Performance meets requirements
- [ ] Security scan passed
- [ ] Accessibility checked
- [ ] Load testing (if applicable)

### Integration
- [ ] All integrations verified
- [ ] API contracts honored
- [ ] Data flows end-to-end

### Test Code Quality (REQUIRED)
- [ ] Tests organized in correct directories (unit/integration/e2e)
- [ ] No hardcoded credentials in test code
- [ ] No secrets in README or documentation
- [ ] Tests run successfully in random order (`--randomize`)
- [ ] ALL existing tests still pass (no regressions)
- [ ] Assertions check specific values (not just existence)
- [ ] Tests verified to fail when code is broken

## Test Verification Steps

Before marking QA complete, MUST verify:

### 1. Run All Tests
```bash
npm test
# All tests must pass
# No skipped tests without documented reason
```

### 2. Run in Random Order
```bash
jest --randomize
# OR
vitest --sequence.shuffle
# All tests must pass
```

### 3. Check for Credentials
```bash
# Search for hardcoded secrets
grep -rn "password.*=.*['\"]" tests/
grep -rn "sk_live\|pk_live\|AKIA" tests/
# Should return no matches
```

### 4. Verify Assertions (Mutation Test)
1. Comment out a key line of code being tested
2. Run the related test
3. Test MUST fail
4. Restore code and verify test passes

### 5. Regression Check
- Compare test count before vs after changes
- Same or more tests should pass

## Release Process

### Pre-Release
1. Complete QA checklist
2. Stakeholder sign-off
3. Prepare release notes
4. Verify rollback procedure
5. Schedule deployment

### Deployment
1. Deploy to staging
2. Run smoke tests
3. Deploy to production
4. Verify production smoke
5. Enable monitoring

### Post-Release
1. Monitor errors & performance
2. Gather user feedback
3. Address critical issues
4. Document lessons learned
5. Close project artifacts

## Phase Gate Checklist

### Test Quality Gates (MUST PASS)
- [ ] All tests pass (`npm test` returns 0 failures)
- [ ] Tests pass in random order (`--randomize` flag)
- [ ] No hardcoded credentials in test code
- [ ] ALL existing tests still pass (no regressions)
- [ ] Tests verified to catch bugs (mutation test)

### Acceptance & Quality
- [ ] All acceptance criteria verified
- [ ] No blocking bugs
- [ ] Performance validated
- [ ] Security review completed

### Release Readiness
- [ ] Rollback plan documented
- [ ] Monitoring configured
- [ ] Release notes prepared
- [ ] Stakeholder approval
- [ ] Deployment instructions verified

## Release Notes Template

```markdown
# Release Notes - [Feature]
**Date**: YYYY-MM-DD
**Version**: X.Y.Z

## What's New
- [Feature]: [Description]

## Improvements
- [Improvement]

## Bug Fixes
- [Fix]: [What was fixed]

## Known Issues
- [Issue]: [Workaround]
```

## Common Pitfalls

| Pitfall | Fix |
|---------|-----|
| Rushing to ship | Respect checklist |
| Testing in production | Use staging |
| Missing rollback | Always have way back |
| No monitoring | Set up first |
| Poor communication | Keep everyone informed |

## Role Guidance

| Role | Focus |
|------|-------|
| PM | Acceptance testing, UX, approve release |
| Dev | Fix bugs, support deploy, monitor |
| QA | Execute test plan, verify fixes, sign-off |
| Tech Lead | Operational readiness, approve deploy |
