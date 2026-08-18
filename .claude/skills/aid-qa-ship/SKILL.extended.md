---
name: aid-qa-ship
description: AID Phase 5 - QA and Release phase guidance. Use this skill when validating implementations, running acceptance tests, preparing releases, deploying to production, or ensuring operational readiness. Final quality gate before shipping to users.
---

# QA & Ship Phase Skill

## Phase Overview

**Purpose**: Validate the implementation meets requirements, ensure production readiness, and ship with confidence.

**Entry Criteria**:
- Development phase completed and approved
- All developer tests passing
- Code reviewed
- Deployment environment available

**Exit Criteria**:
- All acceptance criteria verified
- No blocking bugs
- Production deployment successful
- Stakeholders informed

## Deliverables

### 1. Test Results
- **Description**: Comprehensive QA validation results
- **Format**: Test report with pass/fail status
- **Quality bar**: All acceptance criteria covered, realistic scenarios

### 2. Release Certification
- **Description**: Sign-off that system is ready for production
- **Format**: Checklist completion, stakeholder approvals
- **Quality bar**: All critical items verified

### 3. Release Notes
- **Description**: User-facing summary of changes
- **Format**: Structured changelog
- **Quality bar**: Clear, accurate, complete

### 4. Deployment
- **Description**: Production release
- **Format**: Deployed, verified application
- **Quality bar**: Smoke tests passing, monitoring active

## Role-Specific Guidance

### For Product Managers
- Perform acceptance testing
- Verify user experience
- Approve for release
- Communicate to stakeholders

### For Developers
- Fix reported bugs
- Support deployment
- Monitor initial release
- Address production issues

### For QA Engineers
- Execute test plan
- Report and verify bugs
- Validate fixes
- Sign off on quality

### For Tech Leads
- Verify operational readiness
- Approve deployment
- Ensure monitoring/alerting
- Lead incident response if needed

## Common Pitfalls

| Pitfall | Problem | Fix |
|---------|---------|-----|
| Rushing to ship | Quality gates bypassed | Respect the checklist |
| Testing in production | Users see bugs | Use staging/preview environments |
| Missing rollback plan | Stuck with broken release | Always have a way back |
| No monitoring | Can't detect problems | Set up monitoring first |
| Poor communication | Stakeholders surprised | Keep everyone informed |

## Cucumber Acceptance Verification

In Phase 5, QA validates that all acceptance criteria (Gherkin scenarios) pass before release.

### Verification Commands

| Step | Command | Expected Result | If Fails |
|------|---------|-----------------|----------|
| 1 | `npm run cucumber:dry` | No undefined steps | Implement missing step definitions |
| 2 | `npm run cucumber` | All scenarios pass | Debug failing scenarios |
| 3 | `npm run test:critical` | @critical scenarios pass | BLOCKER - must fix |
| 4 | `npm run test:bdd` | HTML report generated | Review `reports/cucumber-report.html` |

### Interpreting Results

**Passing Test Output:**
```
50 scenarios (50 passed)
150 steps (150 passed)
0m15.234s
```

**Failing Test Output:**
```
50 scenarios (48 passed, 2 failed)
150 steps (145 passed, 3 failed, 2 skipped)

Failures:
1) Scenario: User login with invalid credentials
   Step: Then I should see error "Invalid credentials"
   Error: Expected "Invalid credentials" but got "Login failed"
```

### What to Check in HTML Report

1. **Scenario Pass Rate** - Should be 100% for release
2. **Failed Scenarios** - Click to see step-by-step failure
3. **Pending Steps** - Yellow = not implemented (blocker)
4. **Duration** - Flag unusually slow scenarios
5. **Tags** - Verify no @wip or @skip in release

---

## Cucumber Verification Procedures

### Failure Investigation Workflow

1. **Identify failing scenario**
   ```bash
   npm run cucumber 2>&1 | grep -A 5 "failed"
   ```

2. **Run single scenario for debugging**
   ```bash
   npx cucumber-js features/auth/login.feature:15  # Line number
   ```

3. **Check step definition**
   - Is the step implemented?
   - Does it match the Gherkin exactly?
   - Are assertions correct?

4. **Check test data**
   - Is database in expected state?
   - Are test fixtures correct?
   - Is cleanup happening between scenarios?

### Flaky Test Detection

```bash
# Run 3 times to detect flaky tests
npm run cucumber && npm run cucumber && npm run cucumber

# Run with retry to identify flaky
npx cucumber-js --retry 2 --retryTagFilter @flaky
```

**If test is flaky:**
1. Tag with @flaky temporarily
2. Create bug ticket
3. Investigate timing/state issues
4. Remove @flaky when fixed

### Evidence Collection for Release

1. **Generate comprehensive report**
   ```bash
   npm run test:bdd
   ```

2. **Archive report**
   ```bash
   cp reports/cucumber-report.html docs/qa/release-v1.0.0-cucumber.html
   ```

3. **Screenshot key results**
   - Overall pass rate
   - Critical scenario results
   - Duration metrics

### Check for Forbidden Tags

```bash
# Must return no matches for release
grep -r "@wip\|@skip" features/ && echo "BLOCKED: Remove @wip/@skip tags"
```

### Release Certification Template

```markdown
## Cucumber Acceptance Test Results

**Release:** v1.0.0
**Date:** YYYY-MM-DD
**QA Engineer:** [Name]

### Results Summary
- Total Scenarios: XX
- Passed: XX (100%)
- Failed: 0
- Pending: 0

### Critical Scenarios (@critical)
- [ ] User login: PASS
- [ ] Payment processing: PASS
- [ ] Order creation: PASS

### Report Location
`docs/qa/release-v1.0.0-cucumber.html`

### Sign-off
[x] All acceptance criteria verified
[x] No blocking issues
[x] Approved for release
```

---

## Phase Gate Checklist

Before requesting approval to ship:

### Cucumber Acceptance Gates (MUST PASS) ⭐
- [ ] `npm run cucumber` exits with code 0
- [ ] `npm run test:critical` passes (all @critical scenarios)
- [ ] No undefined or pending step definitions
- [ ] HTML report generated and reviewed
- [ ] No @wip or @skip tags in release scenarios

### Quality Gates
- [ ] All acceptance criteria verified
- [ ] No blocking bugs open
- [ ] Performance validated
- [ ] Security review completed (if applicable)
- [ ] Rollback plan documented
- [ ] Monitoring and alerting configured
- [ ] Release notes prepared
- [ ] Stakeholder approval obtained
- [ ] Deployment instructions verified

## QA Testing Checklist

### Functional Testing
- [ ] All user stories verified
- [ ] All acceptance criteria tested
- [ ] Edge cases covered
- [ ] Error handling tested
- [ ] Cross-browser/device tested (if applicable)

### Non-Functional Testing
- [ ] Performance meets requirements
- [ ] Security scan passed
- [ ] Accessibility compliance checked
- [ ] Load testing completed (if applicable)

### Integration Testing
- [ ] All integrations verified
- [ ] API contracts honored
- [ ] Data flows correctly end-to-end
- [ ] Third-party dependencies working

## Release Process

### Pre-Release
1. Complete QA checklist
2. Get stakeholder sign-off
3. Prepare release notes
4. Verify rollback procedure
5. Schedule deployment window

### Deployment
1. Deploy to staging (final verification)
2. Run smoke tests
3. Deploy to production
4. Verify production smoke tests
5. Enable monitoring/alerting

### Post-Release
1. Monitor error rates and performance
2. Gather user feedback
3. Address critical issues immediately
4. Document lessons learned
5. Close out project artifacts

## Release Notes Template

```markdown
# Release Notes - [Feature Name]
**Date**: YYYY-MM-DD
**Version**: X.Y.Z

## What's New
- [Feature 1]: [Brief description]
- [Feature 2]: [Brief description]

## Improvements
- [Improvement 1]
- [Improvement 2]

## Bug Fixes
- [Fix 1]: [What was fixed]
- [Fix 2]: [What was fixed]

## Known Issues
- [Issue 1]: [Workaround if any]

## Notes
[Any important information for users]
```

## Post-Ship Activities

After deployment:
- Monitor error rates and performance
- Gather user feedback
- Document lessons learned
- Update documentation if needed
- Close out project artifacts
- Collect feedback via `/aid end`

---

## Learning Mode Integration

### Decision Transparency Triggers
- **Test coverage decisions**: Show reasoning for coverage targets
- **Release timing**: Explain why releasing now vs waiting
- **Bug severity classification**: Show why bugs are blocking/non-blocking
- **Rollback decisions**: Document criteria for rollback

### Debate Invitations
- **Test strategy**: When coverage trade-offs have significant impact
- **Release scope**: When partial release is an option
- **Bug triage**: When severity classification is unclear

### Feedback Requests
- After test execution: Validate coverage completeness
- Before release: Confirm stakeholder readiness
- After deployment: Overall release quality rating (1-5)

### Example Transparency Block
```markdown
<decision-transparency>
**Decision:** Proceeding with release despite 2 minor UI bugs

**Reasoning:**
- **User impact**: Bugs are cosmetic, don't affect core functionality
- **Business timing**: Marketing campaign starts Monday
- **Fix timeline**: Bugs can be fixed in patch release this week

**Alternatives Considered:**
1. Delay release - Rejected: Minor bugs don't justify missing campaign
2. Disable affected features - Rejected: Features work, just minor visual issues

**Confidence:** High - Clear separation between blocking and non-blocking issues

**Open to Debate:** Yes - If stakeholders prefer waiting, we can discuss
</decision-transparency>
```

### Example Debate Invitation
```markdown
<debate-invitation>
**Topic:** Test strategy for checkout flow

**Option A: Heavy E2E Coverage**
- ✅ Pros: Tests what users actually do, highest confidence
- ❌ Cons: Slow CI, more brittle, expensive to maintain

**Option B: Testing Trophy (Balanced)**
- ✅ Pros: Fast CI, comprehensive, maintainable
- ❌ Cons: E2E gaps possible

**My Lean:** Option B - 40% unit, 40% integration, 20% E2E critical paths

**Your Input Needed:** What's acceptable CI pipeline time? How critical is checkout?
</debate-invitation>
```
