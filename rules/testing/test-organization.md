---
paths:
  - "tests/**/*"
  - "**/*.test.ts"
  - "**/*.test.tsx"
  - "**/*.spec.ts"
  - "e2e/**/*"
---

# Test Organization Rules

Rules for organizing test files in this project.

---

## Directory Structure (REQUIRED)

```
tests/
├── unit/                    # Fast, isolated tests (<100ms each)
│   ├── services/            # Business logic tests
│   ├── utils/               # Utility function tests
│   └── models/              # Data transformation tests
├── integration/             # Real dependencies (DB, APIs)
│   ├── api/                 # HTTP endpoint tests
│   ├── db/                  # Database tests
│   └── external/            # Third-party integrations
├── e2e/                     # End-to-end browser tests
│   ├── flows/               # User journey tests
│   └── visual/              # Screenshot comparisons
├── fixtures/                # Test data factories
│   └── factories/
└── setup/                   # Global test configuration
```

---

## File Naming Conventions

| Test Type | Pattern | Example |
|-----------|---------|---------|
| Unit | `*.test.ts` | `user-service.test.ts` |
| Integration | `*.integration.test.ts` | `api.integration.test.ts` |
| E2E | `*.e2e.test.ts` | `login-flow.e2e.test.ts` |
| Visual | `*.visual.test.ts` | `dashboard.visual.test.ts` |

---

## Test Naming Pattern

```typescript
// Format: should_[expectedBehavior]_when_[condition]
describe('UserService', () => {
  describe('createUser', () => {
    // GOOD - describes behavior and condition
    test('should_create_user_when_valid_email_provided', () => {});
    test('should_throw_validation_error_when_email_invalid', () => {});
    test('should_throw_duplicate_error_when_email_exists', () => {});

    // BAD - vague or technical
    test('test1', () => {});
    test('works correctly', () => {});
    test('createUser function', () => {});
  });
});
```

---

## Test File Location

| Source File | Test File |
|-------------|-----------|
| `src/services/user-service.ts` | `tests/unit/services/user-service.test.ts` |
| `src/api/users.ts` | `tests/integration/api/users.integration.test.ts` |
| `src/pages/login.tsx` | `tests/e2e/flows/login-flow.e2e.test.ts` |

---

## Import Organization

```typescript
// 1. Test framework
import { describe, test, expect, beforeEach, afterEach } from 'vitest';

// 2. Test utilities
import { createTestUser, createTestOrder } from '@/tests/fixtures/factories';
import { setupTestDb, teardownTestDb } from '@/tests/setup/test-database';

// 3. Code under test
import { UserService } from '@/services/user-service';

// 4. Types
import type { User } from '@/types';
```

---

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| Flat test structure | Hard to find tests | Use nested directories |
| Mixed test types | Confusing, slow CI | Separate by type |
| Inconsistent naming | Hard to search | Follow conventions |
| Tests in source dirs | Pollutes build | Keep in `tests/` |
