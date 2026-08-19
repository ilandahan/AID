---
name: code-review
description: Comprehensive code review for commits and pull requests. Covers security, TDD, code quality, and documentation standards.
---

# Code Review Skill

Review in this order, stopping only to record findings:

```
Code Changes -> Security Scan (P1) -> TDD Validation (P2) -> Code Quality -> Verdict
```

Deep examples live in `references/`. Do not re-derive them here:
- `references/security-patterns.md` - per-language vulnerable/safe pairs
- `references/tdd-patterns.md` - TDD process + test quality examples
- `references/review-templates.md` - copy-paste review templates
- `references/iso27001-guidelines.md` - compliance checklist
- `references/validation-false-positives.md` - anti-patterns when reviewing validation/audit code

## Security Checklist (Critical)

### OWASP Top 10

| Vulnerability | Red Flag |
|--------------|----------|
| Injection | String concatenation in queries |
| Broken Auth | Plain text passwords, weak tokens |
| Sensitive Data Exposure | Secrets in logs |
| XSS | innerHTML, dangerouslySetInnerHTML |
| Broken Access Control | Missing permission checks |

### Security Code Patterns

| Risk | BAD | GOOD |
|------|-----|------|
| SQL Injection | `` const query = `SELECT * FROM users WHERE id = ${userId}`; `` | `const query = 'SELECT * FROM users WHERE id = ?'; db.query(query, [userId]);` |
| XSS | `element.innerHTML = userInput;` | `element.textContent = userInput;` |
| Command injection | `` exec(`ls ${userPath}`); `` | `fs.readdir(userPath);` |
| Hardcoded secrets | `const apiKey = 'sk-1234567890';` | `const apiKey = process.env.API_KEY;` |

### Security Review Questions
- [ ] ALL user input validated/sanitized?
- [ ] Queries parameterized?
- [ ] Secrets in environment variables?
- [ ] Auth checked on protected routes?
- [ ] Error messages safe (no stack traces)?

## TDD Checklist (Priority)

| Question | Expected | Red Flag |
|----------|----------|----------|
| Tests written first? | Yes | Implementation without tests |
| Tests define behavior? | WHAT not HOW | Internal implementation tested |
| Coverage adequate? | Critical paths covered | Only happy path |
| Tests independent? | Run in isolation | Order-dependent |

### Test Quality Patterns

| Rule | BAD | GOOD |
|------|-----|------|
| Test behavior, not internals | `jest.spyOn(service, '_privateMethod')` then `expect(spy).toHaveBeenCalled()` (HOW) | `const result = service.doThing(); expect(result).toEqual(expectedOutput);` (WHAT) |
| Realistic test data | `const mockUser = { id: 1, name: 'test' };` | `const mockUser = { id: 'usr_abc123', name: 'Jane Smith', email: 'jane@example.com', createdAt: new Date('2024-01-15'), roles: ['user', 'admin'] };` |
| Cover edge cases, not just happy path | only `test('creates user', ...)` | plus `throws on missing email`, `throws on duplicate username`, `handles unicode names` |

## Code Quality Checklists

### No Shortcuts
| Pattern | Problem |
|---------|---------|
| `catch (e) { }` | Silent exception |
| TODO, FIXME, HACK | Incomplete work |
| Commented-out code | Dead code |
| `any` overuse | Type safety bypassed |

### No Hardcoded Values
| Bad | Good |
|-----|------|
| `if (status === 3)` | `if (status === Status.APPROVED)` |
| `setTimeout(fn, 5000)` | `setTimeout(fn, TIMEOUT_MS)` |
| `'http://localhost:3000'` | `process.env.API_URL` |

### Root Cause Fixes
| Symptom Fix (Bad) | Root Cause Fix (Good) |
|-------------------|----------------------|
| Add null check where crash occurs | Validate data at entry point |
| Retry failed request 3 times | Fix why request fails |
| Catch and ignore error | Handle error appropriately |
| Add delay to avoid race condition | Fix the race condition |

### Documentation (Mandatory)

| Level | Required |
|-------|----------|
| File | @file, @description, @related |
| Class | Purpose, responsibilities |
| Function | @param, @returns, @throws |

```typescript
// BAD: No documentation
export function createUser(data) {
  return db.create(data);
}

// GOOD: Full documentation
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
export async function createUser(data: CreateUserInput): Promise<User>
```

## Red Flags

| Flag | Severity | Action |
|------|----------|--------|
| SQL/Command injection | CRITICAL | Block |
| Hardcoded secrets | CRITICAL | Block |
| XSS vulnerability | CRITICAL | Block |
| No tests for new code | MAJOR | Request tests |
| Tests modified to pass | MAJOR | Investigate |
| Silent exception catch | MAJOR | Require logging |
| Missing file header | MAJOR | Add docs |

## Output Format

```markdown
# Code Review: [Branch/PR]

## Summary
| Metric | Value |
|--------|-------|
| Files reviewed | X |
| Security issues | X (Y critical) |
| TDD compliance | Y/N |
| Verdict | Ready/Review/Rework |

## Security Issues
### Critical
1. **[Type]** - `file:line`
   - Problem: [desc]
   - Impact: [potential damage]
   - Fix: [solution]

## TDD Issues
1. **[Issue]** - `file:line`
   - Fix: [tests to add]

## Code Quality Issues
[issues]

## Verdict
[decision + reasoning]

### Required Before Merge
- [ ] [action item]
```

## Review Workflow

### Step 1: Security Scan First
```bash
# Check for secrets
grep -r "password\|secret\|api_key\|token" --include="*.ts"

# Check for SQL injection
grep -r "SELECT.*\${" --include="*.ts"

# Check for XSS
grep -r "innerHTML\|dangerouslySetInnerHTML" --include="*.tsx"
```

### Step 2: TDD Validation
```bash
# Check test coverage
npm test -- --coverage

# Verify tests exist for changed files
```

## Verdict Rules

| Condition | Verdict |
|-----------|---------|
| Any critical security | Needs Rework |
| No tests for new functionality | Needs Review |
| Minor issues only | Ready (with suggestions) |
| No issues | Ready to merge |

## Example: Transparency Block

```markdown
<decision-transparency>
**Decision:** Approve with minor suggestions (Ready)

**Reasoning:**
- **Security**: No vulnerabilities found
- **Testing**: All new code has tests
- **Quality**: Minor naming suggestions only

**Issues Found:**
1. Minor: Variable name `d` could be `data` (line 42)
2. Minor: Consider extracting magic number 5 to constant

**Confidence:** High - Standard approval scenario
</decision-transparency>
```

## Example: Debate Invitation

```markdown
<debate-invitation>
**Topic:** Handling of deprecated API usage

**Option A: Block Until Fixed**
- Pros: No technical debt
- Cons: Delays release

**Option B: Approve with Follow-up Task**
- Pros: Pragmatic, allows progress
- Cons: Debt may linger

**My Lean:** Option B - Create ticket, set deadline

**Your Input Needed:** Is there a release deadline? How critical is this code path?
</debate-invitation>
```
