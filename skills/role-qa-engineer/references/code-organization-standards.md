# Test Code Organization Standards

## Purpose

This document defines the REQUIRED structure for test code in projects following AID methodology. Consistent organization ensures:
- Tests are easy to find and maintain
- Clear separation between test types
- Predictable patterns across projects

---

## Directory Structure

### Required Top-Level Structure

```
project-root/
├── src/                    # Source code
├── tests/                  # All test code (REQUIRED)
│   ├── unit/              # Unit tests
│   ├── integration/       # Integration tests
│   ├── e2e/               # End-to-end tests
│   ├── fixtures/          # Test data factories
│   └── setup/             # Global configuration
└── ...
```

### Alternative: Co-located Tests

For some projects, tests next to source files is acceptable:

```
src/
├── services/
│   ├── user-service.ts
│   └── user-service.test.ts    # Unit test co-located
├── __tests__/                   # Shared tests directory
│   └── integration/
│       └── user-api.integration.test.ts
└── ...
```

**Rule:** Choose ONE pattern and use it consistently.

---

## Detailed Directory Structure

### Unit Tests (`tests/unit/`)

Fast, isolated tests that mock external dependencies.

```
tests/unit/
├── services/               # Business logic tests
│   ├── user-service.test.ts
│   ├── order-service.test.ts
│   └── payment-service.test.ts
├── utils/                  # Utility function tests
│   ├── validation.test.ts
│   ├── formatting.test.ts
│   └── calculations.test.ts
├── models/                 # Data transformation tests
│   ├── user-model.test.ts
│   └── order-model.test.ts
└── hooks/                  # React hooks tests (if applicable)
    ├── use-auth.test.ts
    └── use-form.test.ts
```

**Characteristics:**
- Run in < 100ms each
- No external dependencies (DB, APIs, file system)
- Mock external calls
- Can run in parallel

### Integration Tests (`tests/integration/`)

Tests with real external dependencies.

```
tests/integration/
├── api/                    # HTTP endpoint tests
│   ├── auth.integration.test.ts
│   ├── users.integration.test.ts
│   └── orders.integration.test.ts
├── db/                     # Database tests
│   ├── user-repository.integration.test.ts
│   └── order-repository.integration.test.ts
├── external/               # Third-party service tests
│   ├── stripe.integration.test.ts
│   └── sendgrid.integration.test.ts
└── messaging/              # Queue/event tests
    └── order-events.integration.test.ts
```

**Characteristics:**
- Use real database (test instance)
- Use real HTTP calls (to test server)
- May take 1-5 seconds each
- Run sequentially by default

### E2E Tests (`tests/e2e/`)

Browser/UI tests simulating real user interactions.

```
tests/e2e/
├── flows/                  # User journey tests
│   ├── login-flow.e2e.test.ts
│   ├── checkout-flow.e2e.test.ts
│   └── registration-flow.e2e.test.ts
├── visual/                 # Screenshot comparison tests
│   ├── dashboard.visual.test.ts
│   └── product-page.visual.test.ts
├── accessibility/          # A11y tests
│   └── main-pages.a11y.test.ts
└── performance/            # Performance tests
    └── critical-pages.perf.test.ts
```

**Characteristics:**
- Use browser automation (Playwright, Cypress)
- Take 5-30 seconds each
- Require running application
- Run sequentially

### Fixtures (`tests/fixtures/`)

Test data factories and shared test data.

```
tests/fixtures/
├── factories/              # Data factory functions
│   ├── user-factory.ts
│   ├── order-factory.ts
│   └── product-factory.ts
├── mocks/                  # Mock implementations
│   ├── api-mocks.ts
│   └── service-mocks.ts
└── data/                   # Static test data
    ├── valid-users.json
    └── edge-case-inputs.json
```

### Setup (`tests/setup/`)

Global test configuration.

```
tests/setup/
├── jest.setup.ts           # Jest global setup
├── vitest.setup.ts         # Vitest global setup
├── test-database.ts        # Test DB connection
├── test-server.ts          # Test server setup
└── global-mocks.ts         # Always-applied mocks
```

---

## File Naming Conventions

### Test File Patterns

| Test Type | Pattern | Example |
|-----------|---------|---------|
| Unit | `{name}.test.ts` | `user-service.test.ts` |
| Integration | `{name}.integration.test.ts` | `api.integration.test.ts` |
| E2E | `{name}.e2e.test.ts` | `login-flow.e2e.test.ts` |
| Visual | `{name}.visual.test.ts` | `dashboard.visual.test.ts` |
| Accessibility | `{name}.a11y.test.ts` | `forms.a11y.test.ts` |
| Performance | `{name}.perf.test.ts` | `homepage.perf.test.ts` |

### Test Naming Pattern

```typescript
// Format: should_[expectedBehavior]_when_[condition]
describe('UserService', () => {
  describe('createUser', () => {
    test('should_create_user_when_valid_email_provided', () => {});
    test('should_throw_validation_error_when_email_invalid', () => {});
    test('should_throw_duplicate_error_when_email_exists', () => {});
  });

  describe('deleteUser', () => {
    test('should_mark_user_deleted_when_user_exists', () => {});
    test('should_throw_not_found_when_user_missing', () => {});
  });
});
```

---

## Import Organization

### Standard Import Order

```typescript
// 1. External packages
import { describe, test, expect, beforeEach, afterEach } from 'vitest';
import { faker } from '@faker-js/faker';

// 2. Internal test utilities
import { createTestUser, createTestOrder } from '@/tests/fixtures/factories';
import { setupTestDb, teardownTestDb } from '@/tests/setup/test-database';

// 3. Code under test
import { UserService } from '@/services/user-service';
import { OrderService } from '@/services/order-service';

// 4. Types
import type { User, Order } from '@/types';
```

---

## Common Anti-Patterns

### ❌ DON'T: Flat test structure

```
tests/
├── test1.ts
├── test2.ts
├── user-tests.ts
└── api-tests.ts
```

### ❌ DON'T: Mixed test types in one file

```typescript
// user.test.ts - BAD
test('unit test for validation', () => {});
test('integration test with database', () => {});
test('e2e test with browser', () => {});
```

### ❌ DON'T: Inconsistent naming

```
tests/
├── user.test.ts
├── UserTests.ts
├── test_orders.ts
└── PaymentTest.spec.ts
```

### ✅ DO: Consistent, organized structure

```
tests/
├── unit/
│   └── services/
│       └── user-service.test.ts
├── integration/
│   └── api/
│       └── user-api.integration.test.ts
└── e2e/
    └── flows/
        └── user-registration.e2e.test.ts
```

---

## Configuration Examples

### Jest Configuration

```javascript
// jest.config.js
module.exports = {
  projects: [
    {
      displayName: 'unit',
      testMatch: ['<rootDir>/tests/unit/**/*.test.ts'],
      setupFilesAfterEnv: ['<rootDir>/tests/setup/jest.setup.ts'],
    },
    {
      displayName: 'integration',
      testMatch: ['<rootDir>/tests/integration/**/*.integration.test.ts'],
      setupFilesAfterEnv: ['<rootDir>/tests/setup/test-database.ts'],
    },
  ],
};
```

### Vitest Configuration

```typescript
// vitest.config.ts
export default defineConfig({
  test: {
    include: ['tests/**/*.test.ts'],
    exclude: ['tests/**/*.integration.test.ts', 'tests/**/*.e2e.test.ts'],
  },
});

// vitest.integration.config.ts
export default defineConfig({
  test: {
    include: ['tests/**/*.integration.test.ts'],
    setupFiles: ['tests/setup/test-database.ts'],
  },
});
```

---

## Quick Reference

| Question | Answer |
|----------|--------|
| Where do unit tests go? | `tests/unit/{domain}/` |
| Where do integration tests go? | `tests/integration/{type}/` |
| Where do E2E tests go? | `tests/e2e/flows/` |
| Where do fixtures go? | `tests/fixtures/` |
| What pattern for unit tests? | `*.test.ts` |
| What pattern for integration? | `*.integration.test.ts` |
| What pattern for E2E? | `*.e2e.test.ts` |
