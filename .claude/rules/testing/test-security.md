---
paths:
  - "**/*.test.ts"
  - "**/*.test.tsx"
  - "**/*.spec.ts"
  - "tests/**/*"
  - "e2e/**/*"
---

# Test Security Rules

Security requirements for test code.

---

## IRON RULE: No Hardcoded Credentials

This applies to:
- Test files
- README files
- Example code
- Fixtures
- Documentation

---

## Never Do This

```typescript
// BAD - Real-looking credentials
const testUser = {
  email: 'admin@company.com',
  password: 'P@ssw0rd123!',
  apiKey: 'sk-live-abc123xyz'
};

// BAD - Even in "test" files
const config = {
  stripeKey: 'sk_test_abcdefg',
  dbPassword: 'mysecretpassword'
};
```

---

## Always Do This

```typescript
// GOOD - Environment variables with safe defaults
const testUser = {
  email: process.env.TEST_USER_EMAIL || 'test@example.com',
  password: process.env.TEST_USER_PASSWORD || 'test-only-password-123'
};

// GOOD - Factory with clearly fake data
const createTestUser = (overrides = {}) => ({
  email: `test-${Date.now()}@example.com`,
  password: 'DefinitelyNotARealPassword',
  apiKey: 'test_key_not_real_00000000',
  ...overrides
});
```

---

## Environment Variables for Tests

Create `.env.test` (gitignored):

```bash
# .env.test (ADD TO .gitignore)
TEST_DB_URL=postgresql://test:testpassword@localhost:5432/test_db
TEST_API_KEY=sk_test_your_sandbox_key_here
```

Create `.env.example` (safe to commit):

```bash
# .env.example (SAFE TO COMMIT)
TEST_DB_URL=postgresql://user:password@localhost:5432/test_db
TEST_API_KEY=your_test_api_key_here
```

---

## Security Verification Commands

Before committing test code:

```bash
# Search for common credential patterns
grep -rn "password.*=.*['\"]" tests/
grep -rn "secret.*=.*['\"]" tests/
grep -rn "sk_live\|pk_live" tests/
grep -rn "AKIA[A-Z0-9]" tests/

# Should return NO matches
```

---

## Security Checklist

- [ ] No real passwords in test code
- [ ] No real API keys (sk_live_, pk_live_, AKIA)
- [ ] No credentials in README examples
- [ ] `.env.test` is in `.gitignore`
- [ ] Using factories with clearly fake data
- [ ] No database URLs with real hostnames
- [ ] No emails with company domains

---

## Test Data Patterns

### For User Credentials

```typescript
// Factory pattern
export const createTestCredentials = () => ({
  email: `test-${Date.now()}@example.test`,
  password: 'TestOnlyPassword123!',
});
```

### For API Keys

```typescript
// Clearly fake keys
const testApiKey = 'test_key_0000000000000000';
const testStripeKey = 'sk_test_fake_key_for_testing';
```

### For Database

```typescript
// Use env vars
const testDbUrl = process.env.TEST_DB_URL
  || 'postgresql://test:test@localhost:5432/test_db';
```

---

## CI/CD Integration

Use repository secrets for CI:

```yaml
# GitHub Actions
- name: Run tests
  env:
    TEST_API_KEY: ${{ secrets.TEST_API_KEY }}
    TEST_DB_URL: ${{ secrets.TEST_DB_URL }}
  run: npm test
```
