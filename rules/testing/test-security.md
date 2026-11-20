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
  password: '<test-password>',
  apiKey: '<test-api-key>'
};

// BAD - Even in "test" files
const config = {
  paymentApiKey: '<hardcoded key>',
  dbPassword: '<test-db-password>'
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
  password: '<fake-test-password>',
  apiKey: '<fake-test-api-key>',
  ...overrides
});
```

---

## Environment Variables for Tests

`.env.test` (gitignored) holds **non-secret settings only**: hosts, ports, database names,
feature flags. Never put a key, token or password in it, even a test one: a plaintext file
gets copied, synced, attached and committed by mistake.

```bash
# .env.test (ADD TO .gitignore) - non-secret settings only
TEST_DB_HOST=localhost
TEST_DB_PORT=5432
TEST_DB_NAME=test_db
TEST_BASE_URL=http://localhost:3000
```

Test keys and passwords come from, in order of preference: SSO/OAuth (no key at all), then
the OS keystore (macOS Keychain `security`, Windows Credential Manager `cmdkey` /
`Get-StoredCredential`, Linux `secret-tool`), loaded into the shell's environment, then an
environment variable set by the CI secret store. Never a file. For example (macOS):

```bash
export TEST_API_KEY=$(security find-generic-password -s aid-test-api -w)
export TEST_DB_PASSWORD=$(security find-generic-password -s aid-test-db -w)
```

`.env.example` (safe to commit) lists the same non-secret settings, and names the secrets
the tests read from the environment without a value:

```bash
# .env.example (SAFE TO COMMIT)
TEST_DB_HOST=localhost
TEST_DB_NAME=test_db
# Secrets (TEST_API_KEY, TEST_DB_PASSWORD) come from the OS keystore or the CI secret store.
```

---

## Security Verification Commands

Before committing test code:

```bash
# Search for common credential patterns
grep -rn "password.*=.*['\"]" tests/
grep -rn "secret.*=.*['\"]" tests/
grep -rnE "['\"][A-Za-z0-9_-]{32,}['\"]" tests/   # long opaque literals: likely keys or tokens
grep -rn "AKIA[A-Z0-9]" tests/

# Should return NO matches
```

---

## Security Checklist

- [ ] No real passwords in test code
- [ ] No real API keys (no live-mode provider keys, no cloud access-key IDs)
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
  password: '<test-password>',
});
```

### For API Keys

```typescript
// Clearly fake keys
const testApiKey = '<test-api-key>';
const testProviderKey = '<hardcoded key>';
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
