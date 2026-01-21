# Bug Investigation Checklist

Quick reference for investigating bugs before reporting. Print this and keep it visible.

---

## Before Reporting

```
□ Can I reproduce it?
□ Do I have exact steps?
□ Do I have evidence (screenshots, logs)?
□ Have I tried to isolate the issue?
```

**If any answer is NO → Investigate more.**

---

## Phase 1: Reproduce

### Consistency Check
```
□ Does it happen every time?
□ Does it happen with fresh data?
□ Does it happen in different browsers?
□ Does it happen in different environments?
```

### Exact Steps
```
Step 1: ________________________________
Step 2: ________________________________
Step 3: ________________________________
Step 4: ________________________________

Result: ________________________________
```

### Environment
```
Browser:    _________________ Version: _______
OS:         _________________ Version: _______
Environment: □ Local  □ Staging  □ Production
User type:   □ New user  □ Existing user  □ Admin
Test data:   ________________________________
```

---

## Phase 2: Isolate

### Simplify
```
□ What's the MINIMAL reproduction?
□ Can I remove any steps?
□ Can I use simpler data?
□ Is it specific to certain input values?
```

### Narrow Down
```
□ Does it happen with all users?
□ Does it happen with all data?
□ Does it happen at all times?
□ Does it depend on previous actions?
```

### Minimal Case
```
Simplified steps:
1. ________________________________
2. ________________________________

With data: ________________________________
```

---

## Phase 3: Classify

### Severity
```
□ Critical - System down, data loss, security breach
□ Major    - Feature broken, no workaround
□ Minor    - Feature impaired, workaround exists
□ Trivial  - Cosmetic, typo, minor UI issue
```

### Type
```
□ Functional    - Feature doesn't work as specified
□ Performance   - Too slow, high resource usage
□ Security      - Vulnerability, access issue
□ Usability     - Confusing, hard to use
□ Compatibility - Works in X, not in Y
□ Data          - Incorrect data, corruption
```

### Reproducibility
```
□ Always        - 100% reproduction
□ Often         - 70-99%
□ Sometimes     - 30-70%
□ Rarely        - <30%
□ Once          - Cannot reproduce again
```

---

## Phase 4: Document

### Title Formula
```
[Action] + [Problem] + [Context]

Examples:
- "Checkout fails with international address"
- "Search returns wrong results for unicode queries"
- "Login timeout after password reset"
```

### Evidence Checklist
```
□ Screenshot of the issue
□ Console errors (F12 → Console)
□ Network requests (F12 → Network)
□ Error messages shown to user
□ Logs (if accessible)
□ Video recording (for complex flows)
```

---

## Flaky Bug Investigation

When bug appears intermittently:

### Timing Issues
```
□ Does it happen more under load?
□ Does it happen more on slow connections?
□ Is there a race condition?
□ Does adding delays help?
```

### Data Issues
```
□ Is it specific to certain data values?
□ Is it related to data state (fresh vs existing)?
□ Is it related to data volume?
```

### Environment Issues
```
□ Is it CI-specific?
□ Is it browser-specific?
□ Is it timezone-specific?
□ Is it locale-specific?
```

### Investigation Notes
```
Happens when: ________________________________
Does NOT happen when: ________________________
Possibly related to: _________________________
```

---

## Test Failure Investigation

When a test fails:

### Quick Checks
```
□ Is it a new test or existing?
□ Did it pass before? When did it start failing?
□ What changed recently?
□ Does it pass locally?
□ Does it pass when run alone?
```

### Flaky Test Indicators
```
□ Passes sometimes, fails sometimes
□ Passes locally, fails in CI
□ Passes alone, fails with other tests
□ Uses setTimeout/sleep
□ Tests async operations
```

### Root Cause Categories
```
□ Race condition (timing)
□ Test pollution (shared state)
□ Environment difference (CI vs local)
□ Data dependency (external data)
□ Order dependency (test order)
```

---

## Bug Report Template

```markdown
## [Title: Action + Problem + Context]

**Severity:** Critical / Major / Minor
**Environment:** [Browser, OS, Environment]
**Reproducibility:** Always / Sometimes (X/10) / Once

### Steps to Reproduce
1. [Prerequisite state]
2. [Action taken]
3. [Another action]

### Expected Result
[What should happen]

### Actual Result
[What actually happens]

### Evidence
- Screenshot: [attached]
- Console errors: [if any]
- Network: [relevant requests/responses]

### Investigation Notes
- Reproduces in: [environments]
- Does NOT reproduce in: [environments]
- Possibly related to: [observations]

### Minimal Reproduction
[Simplest steps to trigger]
```

---

## Quick Commands

```bash
# Get browser info
navigator.userAgent

# Get console errors
# F12 → Console → Copy all errors

# Get network requests
# F12 → Network → Right-click → Copy → Copy all as HAR

# Clear cache and retry
# Ctrl+Shift+Delete → Clear → Retry

# Test in incognito
# Ctrl+Shift+N (Chrome) / Ctrl+Shift+P (Firefox)
```

---

## Post-Report Checklist

```
□ Bug report is complete
□ Steps are reproducible by someone else
□ Evidence is attached
□ Severity is appropriate
□ Related bugs are linked (if any)
□ Team is notified (if critical)
```
