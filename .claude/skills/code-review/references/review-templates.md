# Code Review Templates

Copy-paste templates for different review scenarios.

---

## Quick Review Template (Small PR)

```markdown
# Review: [PR Title]

**Files:** X | **Risk:** Low/Medium/High

## Security ✓/✗
- [ ] No hardcoded secrets
- [ ] Input validated
- [ ] No injection risks

## Tests ✓/✗
- [ ] Tests exist for changes
- [ ] Edge cases covered

## Quality ✓/✗
- [ ] No shortcuts/workarounds
- [ ] Follows project patterns

**Verdict:** ✓ Ready / ⚠️ Review / ✗ Rework
```

---

## Full Review Template (Feature PR)

```markdown
# Code Review: [Feature Name]

## Summary
| Metric | Value |
|--------|-------|
| Files reviewed | X |
| Lines changed | +X / -X |
| Security issues | X (Y critical) |
| TDD compliance | ✓/⚠️/✗ |
| Code quality | ✓/⚠️/✗ |
| **Verdict** | Ready ✓ / Review ⚠️ / Rework ✗ |

---

## Security Audit 🔒

### Critical Issues 🔴
| File:Line | Issue | Impact | Fix |
|-----------|-------|--------|-----|
| `src/api.ts:45` | SQL injection | Data breach | Use parameterized query |

### Warnings 🟠
| File:Line | Issue | Recommendation |
|-----------|-------|----------------|
| `src/auth.ts:12` | Weak token | Use crypto.randomUUID() |

### Checklist
- [ ] All user input sanitized
- [ ] Queries parameterized
- [ ] Secrets in env vars
- [ ] Auth on protected routes
- [ ] No sensitive data in logs
- [ ] Dependencies up to date

---

## TDD Audit 🧪

### Missing Tests 🔴
| File | Missing Coverage |
|------|-----------------|
| `src/user.ts` | createUser(), deleteUser() |

### Test Quality Issues 🟠
| Test File:Line | Issue | Fix |
|----------------|-------|-----|
| `user.test.ts:23` | Tests implementation | Test behavior instead |

### Checklist
- [ ] Tests for all new functions
- [ ] Tests for modified functions
- [ ] Edge cases (null, empty, boundary)
- [ ] Error scenarios
- [ ] Realistic test data
- [ ] Independent tests (no shared state)

---

## Code Quality 📝

### Major Issues 🟠
1. **[Issue Type]** - `file:line`
   - Problem: [description]
   - Fix: [recommendation]

### Minor Issues 🟡
- `file:line` - [brief description]

### Checklist
- [ ] No TODO/FIXME/HACK comments
- [ ] No commented-out code
- [ ] No silent catch blocks
- [ ] No hardcoded values
- [ ] No `any` type abuse
- [ ] Single responsibility functions
- [ ] Meaningful names
- [ ] Follows project patterns

---

## Verdict

**Decision:** [Ready ✓ / Needs Review ⚠️ / Needs Rework ✗]

**Reasoning:** [Why this decision]

### Required Before Merge
- [ ] [Action item 1]
- [ ] [Action item 2]

### Suggestions (Optional)
- [Optional improvement 1]
- [Optional improvement 2]
```

---

## Security-Focused Review Template

```markdown
# Security Review: [PR Title]

## Risk Assessment
| Factor | Level |
|--------|-------|
| User input handling | Low/Medium/High |
| Authentication changes | Low/Medium/High |
| Data access changes | Low/Medium/High |
| External API calls | Low/Medium/High |
| **Overall Risk** | Low/Medium/High |

## OWASP Top 10 Scan

| Vulnerability | Status | Notes |
|--------------|--------|-------|
| Injection | ✓/✗ | |
| Broken Auth | ✓/✗ | |
| Sensitive Data Exposure | ✓/✗ | |
| XXE | ✓/✗ | N/A if no XML |
| Broken Access Control | ✓/✗ | |
| Security Misconfiguration | ✓/✗ | |
| XSS | ✓/✗ | |
| Insecure Deserialization | ✓/✗ | |
| Vulnerable Components | ✓/✗ | |
| Insufficient Logging | ✓/✗ | |

## Findings

### Critical 🔴 (Block Merge)
[None / List issues]

### High 🟠 (Must Fix)
[None / List issues]

### Medium 🟡 (Should Fix)
[None / List issues]

### Low 🔵 (Consider)
[None / List issues]

## Verdict
**Security Approval:** ✓ Approved / ✗ Not Approved

**Conditions:** [Any conditions for approval]
```

---

## TDD-Focused Review Template

```markdown
# TDD Review: [PR Title]

## Test Coverage Analysis

| File Changed | Has Tests | Coverage | Quality |
|--------------|-----------|----------|---------|
| `src/user.ts` | ✓/✗ | 80% | Good/Poor |
| `src/auth.ts` | ✓/✗ | 45% | Good/Poor |

## TDD Process Check

| Criterion | Status | Evidence |
|-----------|--------|----------|
| Tests written first | ✓/✗ | Commit history shows... |
| Red-Green-Refactor | ✓/✗ | |
| Tests define behavior | ✓/✗ | |
| No implementation testing | ✓/✗ | |

## Test Quality Issues

### Critical (Tests that don't test)
| Test | Problem |
|------|---------|
| `user.test.ts:45` | Only checks truthy, not value |

### Test Data Issues
| Test | Problem |
|------|---------|
| `auth.test.ts:12` | Uses `{ id: 1 }` - unrealistic |

### Missing Edge Cases
| Function | Missing Tests |
|----------|---------------|
| `createUser()` | null input, duplicate email |

## Verdict
**TDD Compliance:** ✓ Compliant / ⚠️ Partial / ✗ Non-compliant

**Required:**
- [ ] Add tests for [function]
- [ ] Fix test data in [file]
```

---

## Hotfix Review Template (Expedited)

```markdown
# Hotfix Review: [Issue]

**Severity:** Critical/High
**Production Impact:** [Description]

## Quick Checks
- [ ] Fix addresses root cause (not just symptom)
- [ ] No new security vulnerabilities
- [ ] Existing tests still pass
- [ ] Minimal change scope

## Risk Assessment
- Regression risk: Low/Medium/High
- Rollback plan: [Yes/No - describe]

## Verdict
**Approved for hotfix:** ✓ Yes / ✗ No

**Follow-up required:**
- [ ] Add comprehensive tests
- [ ] Full code review post-deploy
```
