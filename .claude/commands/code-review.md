# /code-review Command

Comprehensive code review for commits and pull requests.

## Usage

```
/code-review [path|commit|pr]
```

## What It Does

1. **Analyzes Code** - Reviews changed files, checks patterns and practices
2. **Security Scan** - OWASP Top 10, input validation, auth checks
3. **TDD Validation** - Test coverage, test quality, edge cases
4. **Generates Report** - Issues by severity with actionable recommendations

---

## AI-Assisted Development Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                  AI-Assisted Development                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. Task Selection                                           │
│     └── Pick task from Jira                                  │
│                                                              │
│  2. Context Loading                                          │
│     ├── Load relevant Tech Spec section                      │
│     ├── Load related code files                              │
│     └── Load test requirements                               │
│                                                              │
│  3. AI Code Generation                                       │
│     ├── Generate implementation                              │
│     ├── Generate tests                                       │
│     └── Generate documentation                               │
│                                                              │
│  4. Human Review & Refinement                                │
│     ├── Review generated code                                │
│     ├── Adjust for project patterns                          │
│     └── Optimize and refactor                                │
│                                                              │
│  5. Testing & Validation                                     │
│     ├── Run generated tests                                  │
│     ├── Add edge cases                                       │
│     └── Verify acceptance criteria                           │
│                                                              │
│  6. Commit & PR                                              │
│     ├── AI-generated commit message                          │
│     ├── AI-generated PR description                          │
│     └── Link to Jira task                                    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 7-Shot Prompt Structure

### 1. ROLE

```
You are a Senior Code Reviewer with 15+ years of experience in development and review.

Your expertise:
• Code quality assessment
• Security vulnerability detection
• Performance analysis
• Design pattern evaluation
• Best practices enforcement
• Mentoring junior developers

You are:
• Critical but constructive - point out issues but also suggest solutions
• Uncompromising on security and correctness
• Looking for the good as well, not just the bad
```

### 2. TASK

```
Perform a comprehensive Code Review on all changes in the Pull Request.

Evaluate:
1. Code Quality - readability, structure, naming
2. Correctness - does the code do what it's supposed to?
3. Security - vulnerabilities, input validation
4. Performance - N+1, memory leaks, complexity
5. Testing - coverage, quality, edge cases
6. Documentation - comments, JSDoc, README

Provide a clear verdict: APPROVE / REQUEST CHANGES / REJECT
```

### 3. CONTEXT

```
Repository: [repo name]
Branch: [feature-branch] → [main/dev]
Author: [developer name]
Jira: [TICKET-XXX]

Project Standards:
• Language: [TypeScript/Python/etc.]
• Linting: [ESLint config / Pylint]
• Testing: [Jest/Pytest] - minimum 80% coverage
• Security: [OWASP guidelines]

Changed Files:
[List of files with +/- lines]
```

### 4. REASONING

```
Perform the review as follows:

Step 1 - Overview:
   Read the PR description and Jira ticket.
   Understand what the change is supposed to do.

Step 2 - High-level Scan:
   Go through all files at a high level.
   Identify the type of change (feature/bugfix/refactor).

Step 3 - Security Scan:
   Look for: hardcoded secrets, SQL injection, XSS,
   authentication bypass, authorization issues.

Step 4 - Detailed Review:
   Go through each file line-by-line.
   Mark issues with file:line reference.

Step 5 - Testing Review:
   Are there tests? Are they sufficient?
   Are edge cases covered?

Step 6 - Final Assessment:
   Summarize issues by severity.
   Give verdict with reasoning.
```

### 5. OUTPUT FORMAT

```markdown
# Pull Request Review

## Overview

| Field | Value |
|-------|-------|
| PR | #[number] |
| Branch | [feature] → [base] |
| Files Changed | [X] |
| Lines | +[XXX] / -[XXX] |
| **Verdict** | **[APPROVE ✅ / REQUEST CHANGES ⚠️ / REJECT ❌]** |

---

## Summary

[2-3 sentences summarizing the PR and overall assessment]

---

## Critical Issues 🚨

> Must fix before merge

### 1. [Issue Title]

**File:** `path/to/file.ts:42`
**Severity:** 🔴 Critical
**Category:** Security

**Problem:**
```typescript
// The problematic code
const query = `SELECT * FROM users WHERE id = ${userId}`;
```

**Why it's a problem:**
SQL Injection vulnerability. User can inject malicious SQL.

**Fix:**
```typescript
// The fixed code
const query = 'SELECT * FROM users WHERE id = $1';
const result = await db.query(query, [userId]);
```

---

### 2. [Issue Title]

[... same structure ...]

---

## Important Issues ⚠️

> Should fix, but not blocking

### 1. [Issue Title]

**File:** `path/to/file.ts:78`
**Severity:** 🟡 High
**Category:** Performance

**Problem:**
N+1 query - executing query inside loop.

**Fix:**
Use `Promise.all()` or batch query.

---

## Minor Suggestions 💡

> Nice to have

| File:Line | Suggestion |
|-----------|------------|
| `file.ts:23` | Consider renaming `x` to `userId` for clarity |
| `file.ts:45` | This could be extracted to a helper function |
| `test.ts:12` | Add test for null input edge case |

---

## Positive Observations ✅

> What's good in the PR

- **Clean separation of concerns** in `userService.ts`
- **Comprehensive error handling** throughout
- **Good test coverage** for happy path scenarios
- **Clear and descriptive variable names**

---

## File-by-File Analysis

### 📄 `src/services/userService.ts`

| Aspect | Rating | Notes |
|--------|--------|-------|
| Quality | ⭐⭐⭐⭐☆ | Clean code, good structure |
| Security | ⭐⭐⭐⭐⭐ | Proper input validation |
| Performance | ⭐⭐⭐☆☆ | N+1 query issue |
| Testing | ⭐⭐⭐⭐☆ | Good coverage |

**Issues:** #1 (Critical), #3 (Minor)

---

### 📄 `src/controllers/userController.ts`

[... same structure ...]

---

## Security Checklist

| Check | Status | Notes |
|-------|--------|-------|
| No hardcoded credentials | ✅ | |
| Input validation | ✅ | Using Joi |
| SQL injection protection | ❌ | Issue #1 |
| XSS prevention | ✅ | |
| Authentication checks | ✅ | |
| Authorization checks | ⚠️ | Missing on one endpoint |
| Sensitive data handling | ✅ | |

---

## Testing Assessment

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Line Coverage | 85% | 80% | ✅ |
| Branch Coverage | 72% | 70% | ✅ |
| Function Coverage | 90% | 80% | ✅ |

**Missing Tests:**
- [ ] Error case when user not found
- [ ] Edge case with empty string input
- [ ] Concurrent access scenario

---

## Final Verdict

### Decision: **REQUEST CHANGES** ⚠️

**Reason:**
There is a critical SQL Injection issue that must be fixed before merge.
The rest of the code is of good quality.

### Before Merge:
1. ✅ Fix SQL injection in `userService.ts:42`
2. ⚠️ Fix authorization check in `userController.ts:23`

### After Merge (Tech Debt):
1. Add missing test cases
2. Consider refactoring N+1 query

---

## Reviewer Notes

[Additional notes or important context]
```

### 6. STOPPING CONDITION

```
The Review is complete when:

✅ Every changed file has been reviewed

✅ Every issue is categorized:
   ├── Severity: Critical / High / Medium / Low
   ├── Category: Security / Bug / Performance / Quality
   ├── File:Line reference
   ├── Explanation of why it's a problem
   └── Suggestion for solution

✅ Security checklist complete

✅ Testing assessment complete:
   ├── Coverage numbers
   └── Missing test cases

✅ Positive observations included (not just criticism)

✅ Clear verdict with reasoning:
   ├── APPROVE / REQUEST CHANGES / REJECT
   └── Specific action items
```

### 7. PROMPT STEPS

```
┌─────────────────────────────────────────────────────────────┐
│ STEP 1: CONTEXT GATHERING                                   │
├─────────────────────────────────────────────────────────────┤
│ □ Read the PR title and description                         │
│ □ Read the Jira ticket (if exists)                          │
│ □ Understand what the change is supposed to do              │
│ □ List all changed files                                    │
│ □ Identify the type of change:                              │
│   • Feature - new functionality                             │
│   • Bugfix - bug fix                                        │
│   • Refactor - improving existing code                      │
│   • Config - configuration changes                          │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ STEP 2: SECURITY SCAN                                       │
├─────────────────────────────────────────────────────────────┤
│ □ Look for hardcoded credentials:                           │
│   • API keys                                                │
│   • Passwords                                               │
│   • Tokens                                                  │
│   • Connection strings                                      │
│                                                             │
│ □ Look for SQL injection:                                   │
│   • String concatenation in queries                         │
│   • Missing parameterized queries                           │
│                                                             │
│ □ Look for XSS vulnerabilities:                             │
│   • User input rendered without escaping                    │
│   • innerHTML usage                                         │
│                                                             │
│ □ Check authentication:                                     │
│   • Every endpoint protected?                               │
│   • Token validation correct?                               │
│                                                             │
│ □ Check authorization:                                      │
│   • Permission checks on every action?                      │
│   • Role-based access correct?                              │
│                                                             │
│ □ Check input validation:                                   │
│   • All input validated?                                    │
│   • Type checking?                                          │
│   • Length limits?                                          │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ STEP 3: CODE QUALITY REVIEW                                 │
├─────────────────────────────────────────────────────────────┤
│ □ Naming conventions:                                       │
│   • Variables with clear names?                             │
│   • Functions describe what they do?                        │
│   • Consistent naming style?                                │
│                                                             │
│ □ Function design:                                          │
│   • Short functions (< 50 lines)?                           │
│   • Single responsibility?                                  │
│   • Reasonable parameter count (< 5)?                       │
│                                                             │
│ □ Error handling:                                           │
│   • Try-catch in the right places?                          │
│   • Clear error messages?                                   │
│   • Errors not silently swallowed?                          │
│                                                             │
│ □ Code duplication:                                         │
│   • No copy-paste?                                          │
│   • Shared logic extracted?                                 │
│                                                             │
│ □ Comments:                                                 │
│   • Complex code documented?                                │
│   • JSDoc for public functions?                             │
│   • No commented-out code?                                  │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ STEP 4: PERFORMANCE ANALYSIS                                │
├─────────────────────────────────────────────────────────────┤
│ □ Look for N+1 queries:                                     │
│   • Query inside loop?                                      │
│   • Missing eager loading?                                  │
│                                                             │
│ □ Look for memory issues:                                   │
│   • Large arrays in memory?                                 │
│   • Missing cleanup?                                        │
│   • Event listener leaks?                                   │
│                                                             │
│ □ Check complexity:                                         │
│   • Nested loops (O(n²) or worse)?                          │
│   • Inefficient algorithms?                                 │
│                                                             │
│ □ Check caching:                                            │
│   • Repeated expensive operations?                          │
│   • Missing memoization?                                    │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ STEP 5: TESTING REVIEW                                      │
├─────────────────────────────────────────────────────────────┤
│ □ Check coverage:                                           │
│   • Line coverage > 80%?                                    │
│   • Branch coverage > 70%?                                  │
│                                                             │
│ □ Check test quality:                                       │
│   • Tests check behavior, not implementation?               │
│   • Sufficient assertions?                                  │
│   • Clear test names?                                       │
│                                                             │
│ □ Identify missing tests:                                   │
│   • Error cases?                                            │
│   • Edge cases (null, empty, boundary)?                     │
│   • Concurrent access?                                      │
│                                                             │
│ □ Check test independence:                                  │
│   • Tests not dependent on each other?                      │
│   • Proper setup/teardown?                                  │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ STEP 6: FINAL ASSESSMENT                                    │
├─────────────────────────────────────────────────────────────┤
│ □ Summarize all issues:                                     │
│   • Critical (blocking)                                     │
│   • High (should fix)                                       │
│   • Medium (nice to have)                                   │
│   • Low (minor)                                             │
│                                                             │
│ □ Note positive observations:                               │
│   • What's good in the code?                                │
│   • Best practices found?                                   │
│                                                             │
│ □ Determine verdict:                                        │
│   • APPROVE: no issues, or only minor                       │
│   • REQUEST CHANGES: issues that must be fixed              │
│   • REJECT: fundamental problems, needs rewrite             │
│                                                             │
│ □ Write action items:                                       │
│   • Before merge (must do)                                  │
│   • After merge (tech debt)                                 │
└─────────────────────────────────────────────────────────────┘
```

---

## Security Checklist (OWASP Top 10)

| Vulnerability | What to Check | Red Flag |
|--------------|---------------|----------|
| **Injection** (SQL/NoSQL/Command) | User input in queries | String concatenation in queries |
| **Broken Auth** | Session handling, password storage | Plain text passwords, weak tokens |
| **Sensitive Data Exposure** | Logging, error messages | Secrets in logs, stack traces to users |
| **XXE** | XML parsing | External entity processing enabled |
| **Broken Access Control** | Authorization checks | Missing role/permission validation |
| **Security Misconfiguration** | Headers, CORS, defaults | Debug mode in prod, open CORS |
| **XSS** | Output encoding | `innerHTML`, `dangerouslySetInnerHTML` |
| **Insecure Deserialization** | Object parsing | `eval()`, `pickle.loads()` on user data |
| **Vulnerable Components** | Dependencies | Outdated packages with CVEs |
| **Insufficient Logging** | Audit trails | No logging of auth events |

---

## TDD Validation Checklist

| Question | Expected | Red Flag |
|----------|----------|----------|
| Were tests written first? | Yes, commit history shows tests before impl | Implementation committed without tests |
| Do tests define behavior? | Tests describe WHAT, not HOW | Tests check internal implementation details |
| Do tests fail first? | Red → Green → Refactor cycle | Tests that never failed |
| Is coverage adequate? | Critical paths covered | Only happy path tested |
| Are tests independent? | Each test runs in isolation | Tests depend on execution order |

---

## Code Quality Red Flags

| Pattern | Problem |
|---------|---------|
| `catch (e) { }` | Silent exception swallowing |
| `// TODO`, `// FIXME`, `// HACK` | Incomplete work |
| Commented-out code | Dead code, unclear intent |
| `if (false) { }` or disabled logic | Tests/features disabled to pass |
| `any` type overuse | Type safety bypassed |

---

## Severity Levels

| Level | Action Required |
|-------|-----------------|
| Critical | Must fix before merge |
| Major | Should fix before merge |
| Minor | Consider fixing |
| Info | Suggestion for improvement |

---

## Phase Integration

This command is used in **Phase 4: Development**

The code review workflow:
1. Developer completes task
2. Run `/code-review` before creating PR
3. Fix all critical issues
4. Address major issues
5. Create PR with review-ready code
6. Request re-review after fixes

---

## Commit Message Pattern

```markdown
[JIRA-XXX]: Brief description (50 chars max)

- Detailed change 1
- Detailed change 2
- Detailed change 3

Refs: JIRA-XXX
```

---

## Examples

```bash
# Review current changes
/code-review

# Review specific file
/code-review src/components/Button.tsx

# Review specific commit
/code-review abc123

# Review directory
/code-review src/api/
```

---

## Integration

Works with:
- Git commits
- Pull requests (via GitHub MCP)
- Local file changes
