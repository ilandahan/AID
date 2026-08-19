---
name: code-review
description: Comprehensive code review for commits and pull requests. Use when asked to review code changes, audit commits, verify code quality, check for shortcuts or workarounds, validate architectural patterns, or assess production-readiness. Covers pre-implementation workflow, code quality, security, testing, and Claude Code best practices.
---

# Code Review Skill

Thorough review of code changes against professional standards with emphasis on **Security** and **TDD**.

## Review Flow

```
Code Changes Received
     │
     ├─► 1. GATHER CONTEXT
     │        • List all changed files
     │        • Understand the purpose/ticket
     │        • Identify scope (feature/bugfix/refactor)
     │
     ├─► 2. SECURITY SCAN (Priority 1)
     │        • OWASP Top 10 vulnerabilities
     │        • Input validation
     │        • Authentication/Authorization
     │
     ├─► 3. TDD VALIDATION (Priority 2)
     │        • Tests written BEFORE implementation?
     │        • Test coverage adequate?
     │        • Tests test behavior, not implementation?
     │
     ├─► 4. CODE QUALITY REVIEW
     │        • Apply checklists below
     │        • Document issues with file:line
     │
     └─► 5. VERDICT
              • Ready ✓ | Needs Review ⚠️ | Needs Rework ✗
```

## Security Checklist (CRITICAL)

### OWASP Top 10 Scan

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

### Security Code Patterns

```typescript
// ❌ CRITICAL: SQL Injection
const query = `SELECT * FROM users WHERE id = ${userId}`;

// ✅ SAFE: Parameterized query
const query = 'SELECT * FROM users WHERE id = ?';
db.query(query, [userId]);

// ❌ CRITICAL: XSS vulnerability
element.innerHTML = userInput;

// ✅ SAFE: Text content or sanitization
element.textContent = userInput;

// ❌ CRITICAL: Command injection
exec(`ls ${userPath}`);

// ✅ SAFE: Avoid shell, use APIs
fs.readdir(userPath);

// ❌ CRITICAL: Hardcoded secrets
const apiKey = 'sk-1234567890';

// ✅ SAFE: Environment variables
const apiKey = process.env.API_KEY;
```

### Security Review Questions

- [ ] Is ALL user input validated and sanitized?
- [ ] Are queries parameterized (no string concatenation)?
- [ ] Are secrets stored in environment variables?
- [ ] Is authentication checked on every protected route?
- [ ] Is authorization (roles/permissions) enforced?
- [ ] Are error messages safe (no stack traces to users)?
- [ ] Is sensitive data encrypted at rest and in transit?
- [ ] Are dependencies up to date (no known CVEs)?

## TDD Checklist (PRIORITY)

### TDD Process Validation

| Question | Expected | Red Flag |
|----------|----------|----------|
| Were tests written first? | Yes, commit history shows tests before impl | Implementation committed without tests |
| Do tests define behavior? | Tests describe WHAT, not HOW | Tests check internal implementation details |
| Do tests fail first? | Red → Green → Refactor cycle | Tests that never failed |
| Is coverage adequate? | Critical paths covered | Only happy path tested |
| Are tests independent? | Each test runs in isolation | Tests depend on execution order |

### Test Quality Standards

```typescript
// ❌ BAD: Testing implementation details
test('calls internal method', () => {
  const spy = jest.spyOn(service, '_privateMethod');
  service.doThing();
  expect(spy).toHaveBeenCalled();  // Testing HOW, not WHAT
});

// ✅ GOOD: Testing behavior/outcome
test('returns processed result', () => {
  const result = service.doThing();
  expect(result).toEqual(expectedOutput);  // Testing WHAT
});

// ❌ BAD: Unrealistic mock data
const mockUser = { id: 1, name: 'test' };

// ✅ GOOD: Realistic test data
const mockUser = {
  id: 'usr_abc123',
  name: 'Jane Smith',
  email: 'jane@example.com',
  createdAt: new Date('2024-01-15'),
  roles: ['user', 'admin']
};

// ❌ BAD: Only happy path
test('creates user', () => {
  const user = createUser(validData);
  expect(user).toBeDefined();
});

// ✅ GOOD: Edge cases covered
test('creates user with valid data', () => { /* ... */ });
test('throws on missing email', () => { /* ... */ });
test('throws on duplicate username', () => { /* ... */ });
test('handles unicode names', () => { /* ... */ });
```

### TDD Review Questions

- [ ] Do tests exist for ALL new/changed functionality?
- [ ] Are tests testing behavior, not implementation?
- [ ] Is test data realistic (not just `{ id: 1 }`)?
- [ ] Are edge cases covered (nulls, empty, boundaries)?
- [ ] Are error scenarios tested?
- [ ] Do tests run independently (no shared state)?
- [ ] Were tests NOT modified just to make them pass?

## ISO 27001 Compliance Checklist

Quick checks aligned with ISO 27001 security controls:

| Control | Check | Review Question |
|---------|-------|-----------------|
| **A.8.1** Asset Management | Dependencies | Are all dependencies documented and licensed? |
| **A.8.2** Classification | Data Sensitivity | Is sensitive data (PII, credentials) identified and protected? |
| **A.9.2** Authentication | Auth Security | Is authentication secure (strong passwords, MFA, secure sessions)? |
| **A.9.4** Access Control | Authorization | Are permissions checked on all protected resources? |
| **A.12.2** Change Management | PR Process | Does change follow branching/review standards? |
| **A.12.4** Env Separation | Environments | Is prod data never used in dev? Configs separated? |
| **A.12.6** Logging | Audit Trail | Are security events logged (auth, access, changes)? |
| **A.14.2** Secure Dev | Security Tests | Are security tests included? Pre-commit hooks active? |
| **A.18.1** Compliance | Regulatory | Does code meet GDPR/PCI/HIPAA requirements if applicable? |

### Project Organization (ISO 27001 Aligned)

```
Required Files:
✓ SECURITY.md          - Security policy, vulnerability reporting
✓ .github/CODEOWNERS   - Code ownership for access control
✓ .gitignore           - Exclude secrets, logs, sensitive files
✓ .env.example         - Template only (no real values)
✓ docs/security/       - Security documentation

Must NOT be in repo:
✗ .env with credentials
✗ Private keys (*.pem, *.key)
✗ Database dumps
✗ Log files with sensitive data
```

## Code Quality Checklists

### 1. No Shortcuts or Workarounds

| Pattern | Problem |
|---------|---------|
| `catch (e) { }` | Silent exception swallowing |
| `// TODO`, `// FIXME`, `// HACK` | Incomplete work |
| Commented-out code | Dead code, unclear intent |
| `if (false) { }` or disabled logic | Tests/features disabled to pass |
| `any` type overuse | Type safety bypassed |

### 2. No Hardcoded Values

| Bad | Good |
|-----|------|
| `if (status === 3)` | `if (status === Status.APPROVED)` |
| `setTimeout(fn, 5000)` | `setTimeout(fn, TIMEOUT_MS)` |
| `'http://localhost:3000'` | `process.env.API_URL` |
| `width: '768px'` | `width: var(--breakpoint-md)` |

### 3. Root Cause Fixes

| Symptom Fix (Bad) | Root Cause Fix (Good) |
|-------------------|----------------------|
| Add null check where crash occurs | Validate data at entry point |
| Retry failed request 3 times | Fix why request fails |
| Catch and ignore error | Handle error appropriately |
| Add delay to avoid race condition | Fix the race condition |

### 4. Code Quality Standards

- [ ] Functions have single responsibility
- [ ] DRY: No copy-pasted logic
- [ ] Type hints on public functions
- [ ] Meaningful variable/function names
- [ ] No overly broad exception handling
- [ ] Error messages aid debugging

### 5. MANDATORY Documentation Standards

**EVERY file MUST have documentation at THREE levels:**

| Level | Required | Red Flag |
|-------|----------|----------|
| **File** | @file, @description, @related, @created | No file header comment |
| **Component/Class** | Purpose, responsibilities | Class without doc comment |
| **Function** | @param, @returns, @throws, @related | Undocumented functions |

```typescript
// ❌ MISSING: No documentation
export function createUser(data) {
  return db.create(data);
}

// ✅ CORRECT: Full documentation
/**
 * Creates a new user account with validation.
 *
 * @param data - User creation input
 * @returns Created user object
 * @throws {ValidationError} If email invalid
 *
 * @related
 *   - ./UserRepository.ts - Database persistence
 *   - ../validators/email.ts - Email validation
 */
export async function createUser(data: CreateUserInput): Promise<User> {
```

### Documentation Review Questions

- [ ] Does file have @file, @description, @related, @created header?
- [ ] Does every class/component have a purpose comment?
- [ ] Does every function have @param, @returns, @throws?
- [ ] Are cross-file dependencies documented with @related?
- [ ] Do inline comments explain non-obvious logic?

### 6. Architecture & Patterns

- [ ] Follows existing project patterns
- [ ] Proper separation of concerns
- [ ] No circular dependencies
- [ ] Thread-safe where required
- [ ] No business logic in controllers/routes

## Red Flags (Instant Attention)

| Flag | Severity | Action |
|------|----------|--------|
| SQL/Command injection | CRITICAL | Block merge |
| Hardcoded secrets | CRITICAL | Block merge |
| XSS vulnerability | CRITICAL | Block merge |
| No tests for new code | MAJOR | Request tests |
| Tests modified to pass | MAJOR | Investigate |
| Silent exception catch | MAJOR | Require logging |
| **Missing file header** | MAJOR | Add @file, @description, @related |
| **Undocumented functions** | MAJOR | Add @param, @returns, @related |
| **No @related for cross-file** | MAJOR | Document file dependencies |
| TODO/FIXME comments | MINOR | Track in backlog |
| Magic numbers | MINOR | Extract constants |

## Output Format

```markdown
# Code Review: [Branch/PR Name]

## Summary
| Metric | Value |
|--------|-------|
| Files reviewed | X |
| Security issues | X (Y critical) |
| TDD compliance | ✓/⚠️/✗ |
| Code quality | ✓/⚠️/✗ |
| **Verdict** | Ready ✓ / Review ⚠️ / Rework ✗ |

## Security Issues
### Critical
1. **[Vulnerability Type]** - `file:line`
   - Problem: [description]
   - Impact: [potential damage]
   - Fix: [specific code fix]

### Warning
[same format]

## TDD Issues
1. **[Issue]** - `file:line`
   - Problem: [description]
   - Fix: [what tests to add/change]

## Code Quality Issues
### Major
[issues]

### Minor
[issues]

## Verdict
[Final decision with reasoning]

### Required Before Merge
- [ ] [specific action item]
- [ ] [specific action item]
```

## Review Workflow

### Step 1: Security Scan First
```bash
# Check for secrets
grep -r "password\|secret\|api_key\|token" --include="*.ts" --include="*.js"

# Check for SQL injection patterns
grep -r "SELECT.*\${" --include="*.ts" --include="*.js"

# Check for XSS patterns
grep -r "innerHTML\|dangerouslySetInnerHTML" --include="*.tsx" --include="*.jsx"
```

### Step 2: TDD Validation
```bash
# Check test coverage
npm test -- --coverage

# Verify tests exist for changed files
# For each src/foo.ts, check if src/foo.test.ts exists
```

### Step 3: Code Quality
- Read each changed file
- Apply checklists
- Document issues with `file:line` references

### Step 4: Verdict
| Condition | Verdict |
|-----------|---------|
| Any critical security issue | ✗ Needs Rework |
| No tests for new functionality | ⚠️ Needs Review |
| Minor issues only | ✓ Ready (with suggestions) |
| No issues found | ✓ Ready to merge |

---

## Learning Mode Integration

### Decision Transparency Triggers
- **Verdict decisions**: Explain why specific verdict given
- **Issue severity**: Show reasoning for critical vs major vs minor
- **Exception handling**: Document when issues are acceptable

### Debate Invitations
- **Architectural concerns**: When patterns deviate from standards
- **Security trade-offs**: When perfect security conflicts with usability
- **Technical debt acceptance**: When shortcuts are being considered

### Feedback Requests
- After review complete: Validate findings are clear
- After significant findings: Confirm severity assessment
- Request feedback on review thoroughness

### Example Transparency Block for Code Review
```markdown
<decision-transparency>
**Decision:** Approve with minor suggestions (Ready ✓)

**Reasoning:**
- **Security**: No vulnerabilities found
- **Testing**: All new code has tests
- **Quality**: Minor naming suggestions only

**Issues Found:**
1. Minor: Variable name `d` could be `data` (line 42)
2. Minor: Consider extracting magic number 5 to constant

**Confidence:** High - Standard approval scenario

**Open to Debate:** No - Clear pass with minor improvements
</decision-transparency>
```

### Example Debate Invitation for Code Review
```markdown
<debate-invitation>
**Topic:** Handling of deprecated API usage

**Option A: Block Until Fixed**
- ✅ Pros: No technical debt
- ❌ Cons: Delays release

**Option B: Approve with Follow-up Task**
- ✅ Pros: Pragmatic, allows progress
- ❌ Cons: Debt may linger

**My Lean:** Option B - Create ticket, set deadline

**Your Input Needed:** Is there a release deadline? How critical is this code path?
</debate-invitation>
```

### Learning Capture Example
```markdown
<learning-captured>
**What I Learned:**
This team prefers blocking on any security warnings, even low severity.

**Source:**
- User feedback on: Code review verdict
- Context: Asked to escalate low-severity CORS warning

**Applied To:**
- Future reviews will flag all security warnings as requiring attention
- Will not auto-approve with security findings

**Verification:**
- Next review with security findings will flag for review
</learning-captured>
```
