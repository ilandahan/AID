# QA Test Templates

## Test Case Template

```markdown
### TC-[ID]: [Test Case Name]

**Priority**: Critical / High / Medium / Low
**Type**: Functional / Integration / Performance / Security

**Preconditions**:
- [System state required]
- [Data setup needed]

**Steps**:
1. [Action]
2. [Action]
3. [Action]

**Expected Result**:
- [Specific, measurable outcome]

**Actual Result**: [Fill during execution]
**Status**: Pass / Fail / Blocked
**Notes**: [Any observations]
```

## Test Scenarios by Type

### Functional Testing
```gherkin
Feature: [Feature Name]

  Scenario: Happy path
    Given [initial state]
    When [user action]
    Then [expected outcome]

  Scenario: Invalid input
    Given [initial state]
    When [invalid action]
    Then [error handling]

  Scenario: Edge case
    Given [boundary condition]
    When [action]
    Then [correct handling]
```

### Integration Testing
```markdown
### Integration: [System A] -> [System B]

**Data Flow**:
1. [System A] sends [data type]
2. [System B] receives and [processes]
3. [System B] returns [response]

**Verify**:
- [ ] Data format correct
- [ ] All fields mapped
- [ ] Error responses handled
- [ ] Timeout handling works
- [ ] Retry logic functions
```

### Performance Testing
```markdown
### Performance: [Endpoint/Feature]

**Baseline**:
- Response time: [current ms]
- Throughput: [current req/s]
- Error rate: [current %]

**Target**:
- Response time: [target ms] (P95)
- Throughput: [target req/s]
- Error rate: < [target %]

**Load Scenarios**:
1. Normal load: [X] concurrent users
2. Peak load: [Y] concurrent users
3. Stress test: [Z] concurrent users
```

### Security Testing
```markdown
### Security: [Feature/Endpoint]

**Authentication**:
- [ ] Unauthenticated access blocked
- [ ] Invalid token rejected
- [ ] Expired token rejected
- [ ] Session timeout works

**Authorization**:
- [ ] Role permissions enforced
- [ ] Cross-user access blocked
- [ ] Privilege escalation prevented

**Input Validation**:
- [ ] SQL injection prevented
- [ ] XSS prevented
- [ ] Command injection prevented
- [ ] Path traversal blocked

**Data Protection**:
- [ ] Sensitive data encrypted
- [ ] PII not logged
- [ ] Secure transmission
```

## Bug Report Template

```markdown
## Bug: [Short Description]

**ID**: BUG-[number]
**Severity**: Critical / High / Medium / Low
**Priority**: P1 / P2 / P3 / P4
**Environment**: [env details]

### Description
[Clear description of the issue]

### Steps to Reproduce
1. [Step 1]
2. [Step 2]
3. [Step 3]

### Expected Behavior
[What should happen]

### Actual Behavior
[What actually happens]

### Screenshots/Logs
[Attach evidence]

### Impact
[Who is affected, how many, business impact]

### Workaround
[If any exists]
```

## Test Execution Report

```markdown
# Test Execution Report

**Release**: [version]
**Date**: [date]
**Environment**: [env]
**Tester**: [name]

## Summary
| Category | Total | Passed | Failed | Blocked |
|----------|-------|--------|--------|---------|
| Functional | X | X | X | X |
| Integration | X | X | X | X |
| Performance | X | X | X | X |
| Security | X | X | X | X |

## Pass Rate: [X]%

## Failed Tests
| ID | Name | Severity | Bug ID |
|----|------|----------|--------|
| TC-X | [name] | [sev] | BUG-Y |

## Blocked Tests
| ID | Name | Blocker |
|----|------|---------|
| TC-X | [name] | [reason] |

## Risks
- [Risk 1]
- [Risk 2]

## Recommendation
[ ] Ready for release
[ ] Ready with known issues
[ ] Not ready - [reason]
```
