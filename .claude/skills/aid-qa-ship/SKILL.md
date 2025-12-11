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

## Phase Gate Checklist

Before requesting approval to ship:

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
