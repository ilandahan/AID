---
name: test-driven
description: TDD methodology for production-quality tests. Write tests FIRST driven by PRD, Tech Spec, Implementation Plan. Covers minimal mocking, realistic test data, strong assertions, test independence.
---

# Test-Driven Development Skill

Write tests FIRST, driven by project documents.

## Critical: Document-Driven Testing

Before writing any test:
1. Read latest PRD: docs/prd/[latest].md
2. Read latest Tech Spec: docs/tech-spec/[latest].md
3. Read Implementation Plan: docs/implementation-plan/[latest].md
4. CONFIRM with user: "Is [filename] the current document?"

## Test Pyramid

```
        GUI (E2E)       <- DevTools MCP (slow)
      Integration       <- Real DB, APIs (medium)
     Unit (Backend)     <- Fast, isolated

MORE tests at bottom, FEWER at top
```

| Type | Location | Tools | Speed | Tests |
|------|----------|-------|-------|-------|
| Unit | tests/unit/ | Jest, Vitest | Fast | Functions, logic |
| Integration | tests/integration/ | Supertest, real DB | Medium | APIs, DB |
| GUI/E2E | tests/e2e/ | DevTools MCP | Slow | User flows |

## TDD Cycle

```
RED (Write failing test) -> GREEN (Make pass) -> REFACTOR (Clean up) -> REPEAT
```

| Phase | Action | Rule |
|-------|--------|------|
| RED | Write failing test | MUST fail first |
| GREEN | Minimal code to pass | No extra features |
| REFACTOR | Clean up | Tests still pass |

## API Contract Testing (from Tech Spec)

```typescript
describe('POST /api/auth/login', () => {
  test('accepts valid credentials', async () => {
    const response = await request(app)
      .post('/api/auth/login')
      .send({ email: 'user@example.com', password: 'SecurePass123!' })
      .expect(200);

    expect(response.body).toEqual({
      token: expect.stringMatching(/^eyJ/),
      user: { id: expect.stringMatching(/^usr_/), email: 'user@example.com' },
      expiresIn: 3600
    });
  });

  test('returns 401 for invalid password', async () => {
    await request(app)
      .post('/api/auth/login')
      .send({ email: 'user@example.com', password: 'wrong' })
      .expect(401);
  });
});
```

## Database Integration Testing

```typescript
describe('UserRepository', () => {
  beforeEach(async () => { await prisma.user.deleteMany(); });

  test('creates user with required fields', async () => {
    const user = await userRepository.create({ email: 'new@example.com', name: 'New User' });
    const dbUser = await prisma.user.findUnique({ where: { id: user.id } });
    expect(dbUser?.email).toBe('new@example.com');
  });

  test('enforces unique email', async () => {
    await userRepository.create({ email: 'existing@example.com' });
    await expect(userRepository.create({ email: 'existing@example.com' }))
      .rejects.toThrow('Email already exists');
  });
});
```

## Unit Testing (Business Logic)

```typescript
describe('calculateTotal', () => {
  test('applies percentage discount', () => {
    const items = [{ price: 100, quantity: 2 }, { price: 50, quantity: 1 }];
    expect(calculateTotal(items, { discountPercent: 10 })).toBe(225);
  });

  test('handles empty cart', () => {
    expect(calculateTotal([], {})).toBe(0);
  });
});
```

## GUI Testing (DevTools MCP)

```typescript
describe('Login Page', () => {
  test('successful login redirects to dashboard', async () => {
    await mcp.devtools.navigate('http://localhost:3000/login');
    await mcp.devtools.type('#email', 'user@example.com');
    await mcp.devtools.type('#password', 'SecurePass123!');
    await mcp.devtools.click('#submit-btn');
    await mcp.devtools.waitForNavigation();
    expect(await mcp.devtools.getCurrentUrl()).toBe('http://localhost:3000/dashboard');
  });

  test('shows error for invalid credentials', async () => {
    await mcp.devtools.navigate('http://localhost:3000/login');
    await mcp.devtools.type('#password', 'wrong');
    await mcp.devtools.click('#submit-btn');
    await mcp.devtools.waitForSelector('.error-message');
    expect(await mcp.devtools.getText('.error-message')).toBe('Invalid email or password');
  });
});
```

## Test File Organization

```
tests/
  unit/services/, utils/, models/
  integration/api/, repositories/
  e2e/flows/, visual/, accessibility/
  factories/
  setup/database.ts, mcp.ts
```

## Document-to-Test Mapping

| PRD Section | Test Type |
|-------------|-----------|
| User Stories | E2E flow tests |
| Requirements | Feature tests |
| Success Metrics | Performance tests |

| Tech Spec Section | Test Type |
|-------------------|-----------|
| API Design | Contract tests |
| Data Model | DB integration |
| Error Handling | Error scenarios |

## Commands

```bash
npm test                           # All tests
npm test -- --testPathPattern=unit # Unit only
npm test -- --testPathPattern=integration
npm run test:e2e                   # GUI tests
npm test -- --coverage
```

## Checklist Before Writing Tests

- [ ] Found latest PRD, Tech Spec, Plan
- [ ] Confirmed with user
- [ ] Extracted user stories (GUI tests)
- [ ] Extracted API contracts (Backend tests)
- [ ] Extracted error scenarios
- [ ] Identified test phases

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| Testing implementation | Brittle | Test behavior/outcomes |
| Unrealistic mock data | Miss edge cases | Use realistic factories |
| Only happy path | Miss errors | Test edge cases & errors |
| Order-dependent tests | Flaky | Make independent |
| Over-mocking | Miss bugs | Real integrations (<20% mocking) |
| Weak assertions | False positives | Assert exact values |
