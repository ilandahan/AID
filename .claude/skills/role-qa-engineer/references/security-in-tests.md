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
| API Keys | `sk_live_xxx`, `AKIA...` | Service abuse/billing |
| Tokens | `ghp_xxx`, `xoxb-xxx` | API access |
| Connection strings | `postgresql://user:pass@host` | Database access |
| Private keys | `-----BEGIN RSA PRIVATE KEY-----` | Full compromise |
| Secrets | `JWT_SECRET=abc123` | Token forgery |

---

## Patterns: What NOT to Do

### ❌ Hardcoded in Test Files

```typescript
// BAD - Real-looking credentials
const testUser = {
  email: 'admin@company.com',
  password: 'CompanyPass123!'
};

// BAD - API keys that look real
const config = {
  stripeKey: 'sk_test_FAKE_KEY_EXAMPLE_12345',
  awsKey: 'AKIA_FAKE_KEY_EXAMPLE'
};
```

### ❌ Hardcoded in Fixtures

```typescript
// tests/fixtures/users.ts - BAD
export const testUsers = [
  { email: 'john@company.com', password: 'JohnPass123' },
  { email: 'admin@company.com', password: 'AdminPass!' }
];
```

### ❌ Hardcoded in README

```markdown
<!-- BAD - README.md -->
## Running Tests

Set up your environment:
```
TEST_DB_PASSWORD=mysecretpassword
STRIPE_KEY=sk_test_abcdef123456
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
    password: 'TestOnlyPassword-' + faker.string.alphanumeric(8),
    name: faker.person.fullName(),
    ...overrides
  };
}

// Usage
const user = createTestUser();
const adminUser = createTestUser({ role: 'admin' });
```

### ✅ .env.test File (Gitignored)

```bash
# .env.test (ADD TO .gitignore)
TEST_DB_URL=postgresql://test:testpassword@localhost:5432/test_db
TEST_API_KEY=sk_test_your_sandbox_key_here
TEST_STRIPE_KEY=sk_test_your_stripe_test_key
```

```gitignore
# .gitignore
.env
.env.*
!.env.example
```

### ✅ .env.example with Placeholders

```bash
# .env.example (SAFE TO COMMIT)
TEST_DB_URL=postgresql://user:password@localhost:5432/test_db
TEST_API_KEY=your_test_api_key_here
TEST_STRIPE_KEY=sk_test_your_key_here
```

### ✅ README with Placeholders

```markdown
<!-- GOOD - README.md -->
## Running Tests

1. Copy `.env.example` to `.env.test`
2. Fill in your test credentials
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
// GOOD - Stripe
const stripeKey = process.env.STRIPE_TEST_KEY || 'sk_test_fake_key_for_testing';

// GOOD - AWS
const awsConfig = {
  accessKeyId: process.env.AWS_ACCESS_KEY_ID || 'AKIATEST00000000000',
  secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY || 'test/secret/key/not/real'
};

// GOOD - GitHub
const githubToken = process.env.GITHUB_TOKEN || 'ghp_testtoken00000000000000000000000000';
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
- [ ] Search for `sk_live`, `pk_live` - no production keys?
- [ ] Search for `AKIA` - no real AWS keys?
- [ ] Search for `ghp_`, `xoxb-` - no real tokens?
- [ ] Check README - no real credentials in examples?
- [ ] Check `.gitignore` - includes `.env*`?

### Automated Checks

Add to CI pipeline:

```yaml
# .github/workflows/security.yml
- name: Check for secrets
  run: |
    # Fail if we find patterns that look like real credentials
    ! grep -rE "(sk_live_|pk_live_|AKIA[A-Z0-9]{16})" tests/
    ! grep -rE "password.*=.*['\"][^'\"]{8,}['\"]" tests/ --include="*.ts"
```

---

## What If I Need Real Credentials for Tests?

### For Local Development

1. Create `.env.test` (gitignored)
2. Add real test/sandbox credentials there
3. Never commit this file

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
- Stripe: `sk_test_...` keys (safe for testing)
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
| Local development | .env.test (gitignored) |
