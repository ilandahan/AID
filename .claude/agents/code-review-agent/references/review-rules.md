# Code Review Rules (Condensed)

Quick reference for the code-review-agent. Distilled from security-patterns.md and review-templates.md.

---

## Security Red Flags (Auto-CRITICAL)

| Pattern | Vulnerability | Fix |
|---------|--------------|-----|
| `${var}` in SQL | SQL Injection | Parameterized queries |
| `innerHTML = userData` | XSS | `textContent` or DOMPurify |
| `dangerouslySetInnerHTML` | XSS | Sanitize with DOMPurify |
| `eval(userInput)` | Code Injection | Parse with JSON.parse or safe alternatives |
| `exec(string + var)` | Command Injection | `spawn()` with array args |
| `md5(password)` / `sha1()` | Weak Hashing | bcrypt (12+ rounds) or argon2 |
| `Math.random()` for tokens | Weak Randomness | `crypto.randomBytes()` or `crypto.randomUUID()` |
| `cors({ origin: '*' })` | CORS Misconfiguration | Whitelist specific origins |
| Hardcoded `sk-`, `AKIA`, passwords | Secret Exposure | Environment variables |
| `console.log(password)` | Secret in Logs | Redact sensitive fields |
| `res.json(err.stack)` | Info Leakage | Generic error message to client |
| `findById(req.params.id)` alone | IDOR | Add ownership check |
| No `authMiddleware` on route | Missing Auth | Add authentication middleware |

## Code Quality Rules

| Rule | Detection | Severity |
|------|-----------|----------|
| Silent catch block | `catch(e) {}` or `except: pass` | MAJOR |
| Any type abuse | `any` in TypeScript | MAJOR |
| Dead code | Commented-out code blocks | MINOR |
| TODO/FIXME | In deliverable code | MAJOR |
| God function | > 50 lines | MAJOR |
| Copy-paste | Near-identical code blocks | MAJOR |
| Magic numbers | Unexplained numeric literals | MINOR |
| Poor naming | Single-letter vars (except `i`, `j` in loops) | MINOR |

## Documentation Rules

| Rule | Requirement | Severity |
|------|------------|----------|
| File header | `@file`, `@description`, `@related` | MINOR |
| Public function docs | JSDoc/docstring with params | MINOR |
| WHY comments | Non-obvious logic explained | MINOR |
| Connection tags | `@related` links to dependencies | MINOR |

## Architecture Rules

| Rule | Check | Severity |
|------|-------|----------|
| Spec compliance | Implementation matches tech spec | MAJOR |
| Separation of concerns | UI/business/data layers separated | MAJOR |
| Dependency direction | Domain doesn't depend on infrastructure | MAJOR |
| API contract | Public interfaces match spec | MAJOR |
