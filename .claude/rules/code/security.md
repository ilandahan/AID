---
paths:
  - "**/*.ts"
  - "**/*.tsx"
  - "**/*.js"
  - "**/*.jsx"
  - "**/*.py"
---

# Security Rules

Security requirements for all code in this project.

---

## IRON RULE: No Hardcoded Secrets

**NEVER commit:**
- Passwords
- API keys
- Tokens
- Connection strings with credentials
- Private keys
- JWT secrets

```typescript
// NEVER
const apiKey = 'sk-live-abc123xyz';
const password = 'secretpassword';

// ALWAYS
const apiKey = process.env.API_KEY;
const password = process.env.DB_PASSWORD;
```

---

## Input Validation

All external input MUST be validated:

```typescript
// Validate before use
function processUserInput(input: unknown) {
  // 1. Type check
  if (typeof input !== 'string') {
    throw new ValidationError('Input must be a string');
  }

  // 2. Sanitize
  const sanitized = sanitizeInput(input);

  // 3. Validate format
  if (!isValidFormat(sanitized)) {
    throw new ValidationError('Invalid format');
  }

  return sanitized;
}
```

---

## OWASP Top 10 Awareness

| Vulnerability | Prevention |
|---------------|------------|
| Injection | Parameterized queries, input validation |
| Broken Auth | Proper session management, MFA |
| XSS | Output encoding, CSP headers |
| Insecure Direct Object Ref | Authorization checks |
| Security Misconfiguration | Secure defaults, minimal permissions |
| Sensitive Data Exposure | Encryption, minimal data retention |
| Missing Function Access Control | Role-based access checks |
| CSRF | Anti-CSRF tokens |
| Known Vulnerabilities | Keep dependencies updated |
| Insufficient Logging | Log security events |

---

## SQL Injection Prevention

```typescript
// NEVER - String concatenation
const query = `SELECT * FROM users WHERE id = ${userId}`;

// ALWAYS - Parameterized queries
const query = 'SELECT * FROM users WHERE id = $1';
await db.query(query, [userId]);
```

---

## XSS Prevention

```typescript
// NEVER - Direct HTML injection
element.innerHTML = userInput;

// ALWAYS - Use framework escaping or sanitize
element.textContent = userInput;
// Or use DOMPurify for HTML
element.innerHTML = DOMPurify.sanitize(userInput);
```

---

## Authentication/Authorization

1. **Verify authentication** before any protected operation
2. **Check authorization** - User has permission for this specific resource
3. **Use principle of least privilege** - Minimal permissions needed
4. **Log security events** - Failed auth attempts, permission denials

```typescript
async function updateResource(userId: string, resourceId: string) {
  // 1. Verify authenticated
  const user = await verifyAuth(userId);
  if (!user) throw new UnauthorizedError();

  // 2. Check authorization
  const canUpdate = await checkPermission(user, resourceId, 'update');
  if (!canUpdate) throw new ForbiddenError();

  // 3. Proceed with operation
  return await performUpdate(resourceId);
}
```

---

## Environment Variables

Required environment variables MUST be documented:

```typescript
// config.ts
export const config = {
  apiKey: requireEnv('API_KEY'),
  dbUrl: requireEnv('DATABASE_URL'),
  jwtSecret: requireEnv('JWT_SECRET'),
};

function requireEnv(name: string): string {
  const value = process.env[name];
  if (!value) {
    throw new Error(`Missing required environment variable: ${name}`);
  }
  return value;
}
```
