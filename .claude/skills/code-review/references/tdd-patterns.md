# TDD Patterns & Anti-Patterns

Test-Driven Development review guide with examples.

---

## TDD Process

### The Red-Green-Refactor Cycle

```
1. RED:    Write a failing test first
2. GREEN:  Write minimal code to pass the test
3. REFACTOR: Clean up without changing behavior
4. REPEAT
```

### Commit Pattern (Evidence of TDD)

```
✅ GOOD commit history (TDD followed):
- "test: add failing test for user creation"
- "feat: implement createUser to pass test"
- "refactor: extract validation logic"
- "test: add edge case for duplicate email"
- "feat: handle duplicate email error"

❌ BAD commit history (TDD not followed):
- "feat: implement user management"
- "test: add tests for user management"  // Tests after!
```

---

## Test Quality Patterns

### Behavior vs Implementation Testing

```typescript
// ❌ BAD: Testing implementation (HOW)
test('calls validateEmail helper', () => {
  const spy = jest.spyOn(utils, 'validateEmail');
  createUser({ email: 'test@example.com' });
  expect(spy).toHaveBeenCalled();
});

// ❌ BAD: Testing private methods
test('_hashPassword uses bcrypt', () => {
  const hash = userService._hashPassword('test');
  expect(hash).toContain('$2b$');
});

// ✅ GOOD: Testing behavior (WHAT)
test('creates user with valid email', async () => {
  const user = await createUser({ email: 'test@example.com', name: 'Test' });
  expect(user.id).toBeDefined();
  expect(user.email).toBe('test@example.com');
});

// ✅ GOOD: Testing outcome
test('rejects invalid email', async () => {
  await expect(createUser({ email: 'invalid' }))
    .rejects.toThrow('Invalid email format');
});
```

### Realistic Test Data

```typescript
// ❌ BAD: Minimal/unrealistic data
const mockUser = { id: 1, name: 'test' };
const mockOrder = { id: 1 };

// ✅ GOOD: Realistic, production-like data
const mockUser = {
  id: 'usr_a1b2c3d4e5f6',
  email: 'jane.smith@company.com',
  name: 'Jane Smith',
  role: 'admin',
  createdAt: new Date('2024-01-15T10:30:00Z'),
  lastLoginAt: new Date('2024-06-20T14:22:00Z'),
  preferences: {
    theme: 'dark',
    notifications: true
  }
};

const mockOrder = {
  id: 'ord_xyz789',
  userId: 'usr_a1b2c3d4e5f6',
  items: [
    { productId: 'prod_001', quantity: 2, price: 29.99 },
    { productId: 'prod_002', quantity: 1, price: 49.99 }
  ],
  total: 109.97,
  status: 'pending',
  shippingAddress: {
    street: '123 Main St',
    city: 'Springfield',
    state: 'IL',
    zip: '62701'
  },
  createdAt: new Date('2024-06-20T15:00:00Z')
};
```

### Test Factories (Better Than Inline Data)

```typescript
// ✅ BETTER: Use factories for consistent test data
// tests/factories/userFactory.ts
export const createMockUser = (overrides = {}) => ({
  id: `usr_${Math.random().toString(36).slice(2)}`,
  email: `user${Date.now()}@example.com`,
  name: 'Test User',
  role: 'user',
  createdAt: new Date(),
  ...overrides
});

// Usage in tests
test('admin can delete users', async () => {
  const admin = createMockUser({ role: 'admin' });
  const target = createMockUser({ role: 'user' });

  await deleteUser(target.id, { actor: admin });

  expect(await getUser(target.id)).toBeNull();
});
```

---

## Edge Cases to Test

### Input Validation

```typescript
describe('createUser', () => {
  // Happy path
  test('creates user with valid data', async () => { /* ... */ });

  // Edge cases - Required fields
  test('throws when email is missing', async () => {
    await expect(createUser({ name: 'Test' }))
      .rejects.toThrow('Email is required');
  });

  test('throws when email is empty string', async () => {
    await expect(createUser({ email: '', name: 'Test' }))
      .rejects.toThrow('Email is required');
  });

  // Edge cases - Format validation
  test('throws when email format is invalid', async () => {
    await expect(createUser({ email: 'not-an-email', name: 'Test' }))
      .rejects.toThrow('Invalid email format');
  });

  // Edge cases - Boundaries
  test('accepts name at max length (100 chars)', async () => {
    const name = 'a'.repeat(100);
    const user = await createUser({ email: 'test@example.com', name });
    expect(user.name).toHaveLength(100);
  });

  test('throws when name exceeds max length', async () => {
    const name = 'a'.repeat(101);
    await expect(createUser({ email: 'test@example.com', name }))
      .rejects.toThrow('Name too long');
  });

  // Edge cases - Special characters
  test('handles unicode in name', async () => {
    const user = await createUser({
      email: 'test@example.com',
      name: '日本語名前 Émile Müller'
    });
    expect(user.name).toBe('日本語名前 Émile Müller');
  });

  // Edge cases - Duplicates
  test('throws when email already exists', async () => {
    await createUser({ email: 'existing@example.com', name: 'First' });
    await expect(createUser({ email: 'existing@example.com', name: 'Second' }))
      .rejects.toThrow('Email already registered');
  });
});
```

### Async & Error Handling

```typescript
describe('fetchUserData', () => {
  // Success
  test('returns user data on success', async () => { /* ... */ });

  // Network errors
  test('throws on network timeout', async () => {
    mockApi.timeout();
    await expect(fetchUserData('usr_123'))
      .rejects.toThrow('Request timeout');
  });

  test('throws on network failure', async () => {
    mockApi.networkError();
    await expect(fetchUserData('usr_123'))
      .rejects.toThrow('Network error');
  });

  // HTTP errors
  test('throws NotFound for 404', async () => {
    mockApi.respondWith(404);
    await expect(fetchUserData('usr_nonexistent'))
      .rejects.toThrow('User not found');
  });

  test('throws Unauthorized for 401', async () => {
    mockApi.respondWith(401);
    await expect(fetchUserData('usr_123'))
      .rejects.toThrow('Authentication required');
  });

  // Malformed responses
  test('handles malformed JSON response', async () => {
    mockApi.respondWith(200, 'not-json');
    await expect(fetchUserData('usr_123'))
      .rejects.toThrow('Invalid response format');
  });
});
```

---

## Test Independence

### Anti-Pattern: Shared State

```typescript
// ❌ BAD: Tests share state and depend on order
let testUser;

beforeAll(async () => {
  testUser = await createUser({ email: 'shared@test.com' });
});

test('can update user', async () => {
  await updateUser(testUser.id, { name: 'Updated' });
  // Modifies shared state!
});

test('can read user', async () => {
  const user = await getUser(testUser.id);
  expect(user.name).toBe('Original'); // FAILS if previous test ran first!
});
```

### Pattern: Independent Tests

```typescript
// ✅ GOOD: Each test manages its own state
describe('user operations', () => {
  test('can update user', async () => {
    const user = await createUser({ email: 'update-test@test.com', name: 'Original' });

    await updateUser(user.id, { name: 'Updated' });

    const updated = await getUser(user.id);
    expect(updated.name).toBe('Updated');

    // Cleanup (or use afterEach)
    await deleteUser(user.id);
  });

  test('can read user', async () => {
    const user = await createUser({ email: 'read-test@test.com', name: 'Test' });

    const fetched = await getUser(user.id);

    expect(fetched.name).toBe('Test');

    await deleteUser(user.id);
  });
});
```

---

## Test Anti-Patterns

### Tests That Don't Test

```typescript
// ❌ BAD: Only checks existence, not value
test('creates user', async () => {
  const user = await createUser(validData);
  expect(user).toBeDefined();  // Passes even if wrong data returned!
});

// ✅ GOOD: Verify actual values
test('creates user with correct data', async () => {
  const user = await createUser({ email: 'test@example.com', name: 'Test' });
  expect(user.email).toBe('test@example.com');
  expect(user.name).toBe('Test');
  expect(user.id).toMatch(/^usr_/);  // Verify format
});
```

### Tests Modified to Pass

```typescript
// ❌ RED FLAG: Test changed to match broken code
// Original test (correct):
test('returns total with tax', () => {
  expect(calculateTotal(100)).toBe(108); // 8% tax
});

// Modified to pass (WRONG - hiding bug):
test('returns total with tax', () => {
  expect(calculateTotal(100)).toBe(100); // Changed to match bug!
});
```

### Over-Mocking

```typescript
// ❌ BAD: Everything mocked, nothing actually tested
test('processOrder', async () => {
  jest.mock('./validateOrder', () => ({ validateOrder: () => true }));
  jest.mock('./calculateTotal', () => ({ calculateTotal: () => 100 }));
  jest.mock('./sendEmail', () => ({ sendEmail: () => true }));
  jest.mock('./saveOrder', () => ({ saveOrder: () => ({ id: 1 }) }));

  const result = await processOrder(mockOrder);
  expect(result.id).toBe(1);
  // This tests nothing! All logic is mocked away.
});

// ✅ GOOD: Mock only external dependencies
test('processOrder', async () => {
  // Mock only the external email service
  jest.mock('./emailService', () => ({
    sendEmail: jest.fn().mockResolvedValue(true)
  }));

  // Use real implementations for business logic
  const result = await processOrder({
    items: [{ productId: 'prod_1', quantity: 2, price: 50 }],
    userId: 'usr_123'
  });

  expect(result.total).toBe(108); // Real calculation with tax
  expect(result.status).toBe('pending');
  expect(emailService.sendEmail).toHaveBeenCalledWith(
    expect.objectContaining({ type: 'order_confirmation' })
  );
});
```

---

## Coverage Guidelines

### What to Cover

| Must Cover | Should Cover | Optional |
|------------|--------------|----------|
| All public functions | Complex private logic | Simple getters/setters |
| All code paths | Error recovery | Logging statements |
| Edge cases | Boundary conditions | UI formatting |
| Error handling | Integration points | Pure delegation |

### Coverage Commands

```bash
# Jest with coverage
npm test -- --coverage

# Minimum thresholds (jest.config.js)
coverageThreshold: {
  global: {
    branches: 80,
    functions: 80,
    lines: 80,
    statements: 80
  }
}
```

---

## Review Checklist

### TDD Process
- [ ] Commit history shows tests before implementation
- [ ] Each feature has corresponding tests
- [ ] Tests were not modified to pass (check git diff)

### Test Quality
- [ ] Tests verify behavior, not implementation
- [ ] Test data is realistic
- [ ] Edge cases covered (null, empty, boundary, errors)
- [ ] Tests are independent (no shared state)

### Coverage
- [ ] All new code paths tested
- [ ] Error scenarios tested
- [ ] Integration points tested

### Red Flags
- [ ] No `expect(x).toBeDefined()` without value checks
- [ ] No implementation details tested (private methods, spies)
- [ ] No tests modified just to pass
- [ ] No over-mocking (test actual logic)
