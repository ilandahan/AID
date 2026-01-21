# Acceptance Criteria Validation Guide

## Validation Process

### Step 1: Gather All Criteria
```markdown
For each user story:
1. List all acceptance criteria
2. Map to test cases
3. Identify dependencies
4. Note environment requirements
```

### Step 2: Create Traceability Matrix
```markdown
| Story ID | Acceptance Criteria | Test Case | Status | Evidence |
|----------|--------------------:|-----------|--------|----------|
| US-001 | AC-1: User can login | TC-101 | Pass | Screenshot |
| US-001 | AC-2: Error on wrong password | TC-102 | Pass | Log |
| US-001 | AC-3: Session expires after 30min | TC-103 | Pass | Timer test |
```

### Step 3: Validate Each Criterion

For each acceptance criterion:
```markdown
## AC: [Criterion Text]

### Given/When/Then
Given [precondition]
When [action]
Then [expected result]

### Test Evidence
- [ ] Functional test passed
- [ ] Edge cases covered
- [ ] Error handling verified
- Screenshot/Recording: [link]

### Sign-off
- [ ] QA verified
- [ ] PO accepted
```

## Common Validation Patterns

### Data Validation
```markdown
Criterion: "System validates email format"

Test Cases:
- Valid: user@domain.com -> Accepted
- Invalid: user@domain -> Rejected with message
- Invalid: user.domain.com -> Rejected with message
- Empty: "" -> Required field error
- Special chars: user+tag@domain.com -> Accepted (if supported)
```

### Performance Validation
```markdown
Criterion: "Page loads in under 2 seconds"

Test Cases:
- Cold start: [measured time]
- Warm cache: [measured time]
- Under load: [measured time at X users]
- Network throttle: [measured time on 3G]

Evidence: Performance test report attached
```

### Security Validation
```markdown
Criterion: "Only admins can delete users"

Test Cases:
- Admin role: Delete succeeds
- User role: Delete forbidden (403)
- No auth: Unauthorized (401)
- Expired token: Unauthorized (401)

Evidence: API response screenshots
```

### Integration Validation
```markdown
Criterion: "Order syncs to ERP within 5 minutes"

Test Cases:
- Create order -> Check ERP (timestamp: X)
- Update order -> Verify ERP update
- Delete order -> Verify ERP deletion
- ERP unavailable -> Retry mechanism works

Evidence: Logs showing timestamps
```

## Validation Report Template

```markdown
# Acceptance Validation Report

**Feature**: [Feature Name]
**Sprint**: [Sprint Number]
**Date**: [Date]
**Validated By**: [Name]

## Summary
| Total Criteria | Validated | Failed | Blocked |
|----------------|-----------|--------|---------|
| X | Y | Z | W |

## Detailed Results

### User Story: [US-XXX] [Title]

| AC | Description | Status | Notes |
|----|-------------|--------|-------|
| 1 | [criterion] | Pass | [notes] |
| 2 | [criterion] | Pass | [notes] |
| 3 | [criterion] | Fail | Bug: BUG-XXX |

### Evidence
- [Link to test results]
- [Link to screenshots]
- [Link to recordings]

## Failed Criteria

### AC-X: [Description]
**Reason**: [Why it failed]
**Bug**: [Bug ID]
**Impact**: [Business impact]
**Recommendation**: [Fix / Accept / Defer]

## Sign-off

| Role | Name | Status | Date |
|------|------|--------|------|
| QA | [name] | Approved | [date] |
| PO | [name] | [status] | [date] |
| Tech Lead | [name] | [status] | [date] |
```

## Edge Case Checklist

For each criterion, consider:
- [ ] Empty/null values
- [ ] Maximum length values
- [ ] Boundary values
- [ ] Special characters
- [ ] Unicode/internationalization
- [ ] Concurrent access
- [ ] Network failures
- [ ] Timeout scenarios
- [ ] Permission variations
- [ ] State transitions
