# Security in Test Code

## Purpose

This document defines security requirements for test code. Test code often has less scrutiny than production code, making it a common source of credential leaks.

---

## IRON RULE

**NO HARDCODED CREDENTIALS ANYWHERE**

This includes:
- Test files (`.test.ts`, `.spec.ts`)
- Fixture files
- README and documentation
- Example code
- Configuration files committed to git
- Comments

---

## What Counts as Credentials?

| Type | Examples | Risk |
|------|----------|------|
| Passwords | `password123`, `P@ssw0rd!` | Account compromise |
| API Keys | `key_live_xxxx`, cloud access-key IDs | Service abuse/billing |
| Tokens | personal access tokens, chat bot tokens | API access |
| Connection strings | `postgresql://user:pass@host` | Database access |
| Private keys | `-----BEGIN [RSA] PRIVATE KEY-----` | Full compromise |
| Secrets | `JWT_SECRET=<token-value>` | Token forgery |

---

## Patterns: What NOT to Do

### ❌ Hardcoded in Test Files

```typescript
// BAD - Real-looking credentials
const testUser = {
  email: 'admin@company.com',
  password: '<example-password>'
};

// BAD - API keys hardcoded in source (imagine real values here)
const config = {
  paymentApiKey: '<hardcoded key>',
  cloudAccessKey: '<hardcoded key>'
};
```

### ❌ Hardcoded in Fixtures

```typescript
// tests/fixtures/users.ts - BAD
export const testUsers = [
  { email: 'john@company.com', password: '<test-password>' },
  { email: 'admin@company.com', password: '<test-password>' }
];
```

### ❌ Hardcoded in README

```markdown
<!-- BAD - README.md -->
## Running Tests

Set up your environment:
```
TEST_DB_PASSWORD=mysecretpassword
PAYMENT_PROVIDER_KEY=<your-api-key>
```
```

### ❌ Hardcoded in Config

```javascript
// jest.config.js - BAD
module.exports = {
  globals: {
    TEST_API_KEY: 'real-api-key-here'
  }
};
```

---

## Patterns: What TO Do

### ✅ Environment Variables with Safe Defaults

```typescript
// GOOD - Environment variables with obvious fake defaults
const testConfig = {
  apiKey: process.env.TEST_API_KEY || 'test_key_not_real_00000000',
  dbUrl: process.env.TEST_DB_URL || 'postgresql://test:test@localhost:5432/test_db',
  secret: process.env.TEST_SECRET || 'not-a-real-secret-for-testing-only'
};

// GOOD - In test files
const testUser = {
  email: process.env.TEST_USER_EMAIL || 'test@example.com',
  password: process.env.TEST_USER_PASSWORD || 'TestOnlyPassword123'
};
```

### ✅ Factory Functions with Fake Data

```typescript
// tests/fixtures/user-factory.ts - GOOD
import { faker } from '@faker-js/faker';

export function createTestUser(overrides = {}) {
  return {
    id: faker.string.uuid(),
    email: faker.internet.email({ provider: 'test-example.com' }),
    password: 'pw-' + faker.string.alphanumeric(16),
    name: faker.person.fullName(),
    ...overrides
  };
}

// Usage
const user = createTestUser();
const adminUser = createTestUser({ role: 'admin' });
```

### ✅ .env.test File (Gitignored, non-secret settings only)

```bash
# .env.test (ADD TO .gitignore) - no keys, tokens or passwords here
TEST_DB_HOST=localhost
TEST_DB_PORT=5432
TEST_DB_NAME=test_db
TEST_BASE_URL=http://localhost:3000
```

Keys and passwords for tests come from the OS keystore (macOS Keychain `security`, Windows
Credential Manager `cmdkey` / `Get-StoredCredential`, Linux `secret-tool`) or, in CI, the CI
secret store, as environment variables: SSO/OAuth first, then the keystore, then an
environment variable, never a file.

```gitignore
# .gitignore
.env
.env.*
!.env.example
```

### ✅ .env.example with Placeholders

```bash
# .env.example (SAFE TO COMMIT)
TEST_DB_HOST=localhost
TEST_DB_NAME=test_db
# Secrets (TEST_API_KEY, TEST_PAYMENT_PROVIDER_KEY, TEST_DB_PASSWORD) come from the
# OS keystore or the CI secret store, never from this file or .env.test.
```

### ✅ README with Placeholders

```markdown
<!-- GOOD - README.md -->
## Running Tests

1. Copy `.env.example` to `.env.test` (non-secret settings only)
2. Load the test credentials from your OS keystore into the shell's environment
3. Run `npm test`

See `.env.example` for required variables.
```

---

## Credential Patterns by Service

### Database Connections

```typescript
// GOOD
const dbConfig = {
  host: process.env.TEST_DB_HOST || 'localhost',
  port: parseInt(process.env.TEST_DB_PORT || '5432'),
  database: process.env.TEST_DB_NAME || 'test_db',
  user: process.env.TEST_DB_USER || 'test_user',
  password: process.env.TEST_DB_PASSWORD || 'test_password'
};
```

### API Keys

```typescript
// GOOD - Third-party API
const providerKey = process.env.PROVIDER_TEST_API_KEY || '<hardcoded key>';

// GOOD - AWS
const awsConfig = {
  accessKeyId: process.env.AWS_ACCESS_KEY_ID || '<hardcoded key>',
  secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY || 'test/secret/key/not/real'
};

// GOOD - GitHub
const githubToken = process.env.GITHUB_TOKEN || '<hardcoded token>';
```

### JWT Secrets

```typescript
// GOOD
const jwtSecret = process.env.JWT_SECRET || 'test-jwt-secret-not-for-production-use';
```

---

## Security Checklist

### Before Committing Test Code

- [ ] Search for `password` - no real passwords?
- [ ] Search for `secret` - no real secrets?
- [ ] Search for your providers' live-mode key prefixes - no production keys?
- [ ] Search for `AKIA` - no real AWS keys?
- [ ] Search for personal-access-token and bot-token prefixes - no real tokens?
- [ ] Check README - no real credentials in examples?
- [ ] Check `.gitignore` - includes `.env*`?

### Automated Checks

Add to CI pipeline:

```yaml
# .github/workflows/security.yml
- name: Check for secrets
  run: |
    # Fail if we find patterns that look like real credentials
    ! grep -rE "(AKIA[A-Z0-9]{16}|['\"][A-Za-z0-9_-]{32,}['\"])" tests/
    ! grep -rE "password.*=.*['\"][^'\"]{8,}['\"]" tests/ --include="*.ts"
```

---

## What If I Need Real Credentials for Tests?

### For Local Development

1. Store the test/sandbox credentials in your OS keystore (SSO/OAuth if the service
   offers it), never in a file
2. Load them into the shell's environment before running the tests, for example
   `export TEST_API_KEY=$(security find-generic-password -s aid-test-api -w)` (macOS)
3. Keep only non-secret settings in `.env.test` (gitignored)

### For CI/CD

1. Use repository secrets (GitHub Secrets, GitLab CI Variables)
2. Inject at runtime:

```yaml
# GitHub Actions
- name: Run tests
  env:
    TEST_API_KEY: ${{ secrets.TEST_API_KEY }}
    TEST_DB_URL: ${{ secrets.TEST_DB_URL }}
  run: npm test
```

### For Test/Sandbox Environments

Use sandbox/test API keys provided by services:
- Payment and other third-party APIs: sandbox or test-mode keys (safe for testing)
- AWS: IAM user with minimal test permissions
- Database: Dedicated test database with test data only

---

## Quick Reference

| Scenario | Solution |
|----------|----------|
| Need user credentials | Factory with fake data |
| Need API key | Env var with fake default |
| Need database URL | Env var with localhost default |
| Need to document setup | .env.example with placeholders |
| Running in CI | Repository secrets |
| Local development | OS keystore -> environment (settings in .env.test, no secrets) |
