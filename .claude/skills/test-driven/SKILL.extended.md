---
name: test-driven
description: Comprehensive TDD (Test-Driven Development) methodology for writing production-quality tests. Use this skill when writing tests before implementation, reviewing test quality, ensuring comprehensive coverage, avoiding test anti-patterns, or when asked about testing best practices. Covers minimal mocking strategies, realistic test data, strong assertions, and test independence.
---

# Test-Driven Development Skill

Write tests FIRST, driven by project documents (PRD, Tech Spec, Implementation Plan).

## CRITICAL: Document-Driven Testing

```
┌─────────────────────────────────────────────────────────────────┐
│  BEFORE WRITING ANY TEST:                                       │
│                                                                 │
│  1. Read latest PRD         → docs/prd/[latest].md              │
│  2. Read latest Tech Spec   → docs/tech-spec/[latest].md        │
│  3. Read Implementation Plan → docs/implementation-plan/[latest].md │
│                                                                 │
│  4. CONFIRM with user: "Is [filename] the current document?"    │
└─────────────────────────────────────────────────────────────────┘
```

### Document Workflow

```
User Request: "Write tests for feature X"
     │
     ├─► Step 1: FIND DOCUMENTS
     │        │
     │        ├─► ls docs/prd/ → Find latest PRD
     │        ├─► ls docs/tech-spec/ → Find latest Tech Spec
     │        └─► ls docs/implementation-plan/ → Find latest Plan
     │
     ├─► Step 2: CONFIRM WITH USER
     │        │
     │        └─► "I found these documents for feature X:
     │             - PRD: 2024-06-15-feature-x.md
     │             - Tech Spec: 2024-06-16-feature-x.md
     │             - Plan: 2024-06-17-feature-x.md
     │             Are these the current documents?"
     │
     ├─► Step 3: READ & EXTRACT
     │        │
     │        ├─► From PRD: User stories, requirements
     │        ├─► From Tech Spec: API contracts, schemas, errors
     │        └─► From Plan: Test strategy, phases
     │
     └─► Step 4: WRITE TESTS
              │
              ├─► Backend/API Tests (Unit + Integration)
              └─► GUI Tests (DevTools MCP)
```

## Test Types Separation

```
┌─────────────────────────────────────────────────────────────────┐
│                         TEST PYRAMID                            │
│                                                                 │
│                         ┌─────────┐                             │
│                         │   GUI   │  ← DevTools MCP             │
│                         │  Tests  │    (E2E, Visual)            │
│                       ┌─┴─────────┴─┐                           │
│                       │ Integration │  ← Real DB, APIs          │
│                       │    Tests    │    (supertest, etc.)      │
│                     ┌─┴─────────────┴─┐                         │
│                     │   Unit Tests    │  ← Fast, isolated       │
│                     │   (Backend)     │    (jest, vitest)       │
│                     └─────────────────┘                         │
│                                                                 │
│  MORE tests at bottom, FEWER at top                             │
└─────────────────────────────────────────────────────────────────┘
```

| Test Type | Location | Tools | Speed | What to Test |
|-----------|----------|-------|-------|--------------|
| **Unit** | `tests/unit/` | Jest, Vitest | Fast | Functions, classes, logic |
| **Integration** | `tests/integration/` | Supertest, real DB | Medium | APIs, DB operations |
| **GUI/E2E** | `tests/e2e/` | DevTools MCP | Slow | User flows, visual |

## The TDD Cycle

```
┌─────────────────────────────────────────────────────┐
│                                                     │
│    1. RED      →    2. GREEN    →    3. REFACTOR   │
│    Write test       Make it          Clean up      │
│    (fails)          pass             (tests pass)  │
│                                                     │
│         ↑                                 │        │
│         └─────────────────────────────────┘        │
│                     REPEAT                         │
└─────────────────────────────────────────────────────┘
```

| Phase | Action | Rule |
|-------|--------|------|
| **RED** | Write failing test | Test MUST fail first |
| **GREEN** | Write minimal code to pass | No extra features |
| **REFACTOR** | Clean up code | Tests still pass |

## Part 1: Backend & API Testing

### API Contract Testing (from Tech Spec)

```typescript
// Read from Tech Spec: API Design section
// docs/tech-spec/2024-06-15-user-auth.md

describe('POST /api/auth/login', () => {
  // From Tech Spec: Request Schema
  test('accepts valid credentials', async () => {
    const response = await request(app)
      .post('/api/auth/login')
      .send({
        email: 'user@example.com',
        password: 'SecurePass123!'
      })
      .expect(200);

    // From Tech Spec: Response Schema
    expect(response.body).toEqual({
      token: expect.stringMatching(/^eyJ/),
      user: {
        id: expect.stringMatching(/^usr_/),
        email: 'user@example.com',
        role: expect.stringMatching(/^(admin|user)$/)
      },
      expiresIn: 3600
    });
  });

  // From Tech Spec: Error Handling section
  test('returns 401 for invalid password', async () => {
    const response = await request(app)
      .post('/api/auth/login')
      .send({
        email: 'user@example.com',
        password: 'wrong'
      })
      .expect(401);

    expect(response.body).toEqual({
      error: 'INVALID_CREDENTIALS',
      message: 'Invalid email or password'
    });
  });

  // From Tech Spec: Rate Limiting
  test('returns 429 after 5 failed attempts', async () => {
    for (let i = 0; i < 5; i++) {
      await request(app)
        .post('/api/auth/login')
        .send({ email: 'user@example.com', password: 'wrong' });
    }

    const response = await request(app)
      .post('/api/auth/login')
      .send({ email: 'user@example.com', password: 'wrong' })
      .expect(429);

    expect(response.body.error).toBe('RATE_LIMITED');
  });
});
```

### Database Integration Testing

```typescript
// tests/integration/user.integration.test.ts
import { prisma } from '../setup/database';

describe('UserRepository', () => {
  beforeEach(async () => {
    await prisma.$transaction([
      prisma.user.deleteMany(),
    ]);
  });

  // From PRD: User Stories
  test('creates user with all required fields', async () => {
    const user = await userRepository.create({
      email: 'new@example.com',
      name: 'New User',
      password: 'SecurePass123!'
    });

    // Verify in database
    const dbUser = await prisma.user.findUnique({
      where: { id: user.id }
    });

    expect(dbUser).not.toBeNull();
    expect(dbUser?.email).toBe('new@example.com');
    expect(dbUser?.passwordHash).not.toBe('SecurePass123!'); // Hashed!
  });

  // From Tech Spec: Data Constraints
  test('enforces unique email constraint', async () => {
    await userRepository.create({
      email: 'existing@example.com',
      name: 'First User'
    });

    await expect(userRepository.create({
      email: 'existing@example.com',
      name: 'Second User'
    })).rejects.toThrow('Email already exists');
  });
});
```

### Unit Testing (Business Logic)

```typescript
// tests/unit/orderCalculator.test.ts

describe('OrderCalculator', () => {
  // From PRD: Business Rules
  describe('calculateTotal', () => {
    test('applies percentage discount correctly', () => {
      const items = [
        { price: 100, quantity: 2 },
        { price: 50, quantity: 1 }
      ];

      const total = calculateTotal(items, { discountPercent: 10 });

      expect(total).toBe(225); // (200 + 50) * 0.9
    });

    // From Tech Spec: Edge Cases
    test('handles empty cart', () => {
      expect(calculateTotal([], {})).toBe(0);
    });

    test('rounds to 2 decimal places', () => {
      const items = [{ price: 10.333, quantity: 3 }];
      expect(calculateTotal(items, {})).toBe(31.00);
    });
  });
});
```

## Part 2: GUI Testing (DevTools MCP)

### DevTools MCP Integration

GUI tests use the **Chrome DevTools MCP** server for:
- Visual regression testing
- User flow testing
- Accessibility testing
- Performance monitoring

### GUI Test Structure

```typescript
// tests/e2e/login.e2e.test.ts
// Uses DevTools MCP for browser automation

describe('Login Page', () => {
  // From PRD: User Story - "As a user, I can log in"
  test('successful login redirects to dashboard', async () => {
    // DevTools MCP: Navigate to page
    await mcp.devtools.navigate('http://localhost:3000/login');

    // DevTools MCP: Fill form
    await mcp.devtools.type('#email', 'user@example.com');
    await mcp.devtools.type('#password', 'SecurePass123!');
    await mcp.devtools.click('#submit-btn');

    // DevTools MCP: Wait for navigation
    await mcp.devtools.waitForNavigation();

    // DevTools MCP: Verify URL
    const url = await mcp.devtools.getCurrentUrl();
    expect(url).toBe('http://localhost:3000/dashboard');

    // DevTools MCP: Verify element visible
    const welcomeText = await mcp.devtools.getText('.welcome-message');
    expect(welcomeText).toContain('Welcome');
  });

  // From PRD: Error handling
  test('shows error message for invalid credentials', async () => {
    await mcp.devtools.navigate('http://localhost:3000/login');
    await mcp.devtools.type('#email', 'user@example.com');
    await mcp.devtools.type('#password', 'wrong');
    await mcp.devtools.click('#submit-btn');

    // DevTools MCP: Wait for error
    await mcp.devtools.waitForSelector('.error-message');

    const errorText = await mcp.devtools.getText('.error-message');
    expect(errorText).toBe('Invalid email or password');
  });

  // Visual regression test
  test('login form matches design', async () => {
    await mcp.devtools.navigate('http://localhost:3000/login');

    // DevTools MCP: Take screenshot
    const screenshot = await mcp.devtools.screenshot();

    // Compare with baseline
    expect(screenshot).toMatchImageSnapshot();
  });
});
```

### Accessibility Testing (DevTools MCP)

```typescript
describe('Accessibility', () => {
  test('login page passes accessibility audit', async () => {
    await mcp.devtools.navigate('http://localhost:3000/login');

    // DevTools MCP: Run Lighthouse accessibility audit
    const audit = await mcp.devtools.runAccessibilityAudit();

    expect(audit.score).toBeGreaterThanOrEqual(90);
    expect(audit.violations).toHaveLength(0);
  });

  test('all form inputs have labels', async () => {
    await mcp.devtools.navigate('http://localhost:3000/login');

    const inputs = await mcp.devtools.querySelectorAll('input');
    for (const input of inputs) {
      const label = await mcp.devtools.getAttribute(input, 'aria-label');
      const labelledBy = await mcp.devtools.getAttribute(input, 'aria-labelledby');
      expect(label || labelledBy).toBeTruthy();
    }
  });
});
```

## Test File Organization

```
tests/
├── unit/                          # Fast, isolated tests
│   ├── services/
│   │   ├── userService.test.ts
│   │   └── orderService.test.ts
│   ├── utils/
│   │   └── validators.test.ts
│   └── models/
│       └── user.test.ts
│
├── integration/                   # API & DB tests
│   ├── api/
│   │   ├── auth.integration.test.ts
│   │   └── users.integration.test.ts
│   └── repositories/
│       └── userRepository.integration.test.ts
│
├── e2e/                          # GUI tests (DevTools MCP)
│   ├── flows/
│   │   ├── login.e2e.test.ts
│   │   ├── registration.e2e.test.ts
│   │   └── checkout.e2e.test.ts
│   ├── visual/
│   │   └── components.visual.test.ts
│   └── accessibility/
│       └── audit.a11y.test.ts
│
├── factories/                     # Test data factories
│   ├── userFactory.ts
│   └── orderFactory.ts
│
└── setup/
    ├── database.ts               # Test DB setup
    ├── mcp.ts                    # DevTools MCP setup
    └── jest.setup.ts
```

## Document-to-Test Mapping

### From PRD → GUI Tests

| PRD Section | Test Type |
|-------------|-----------|
| User Stories | E2E flow tests |
| Requirements | Feature tests |
| Success Metrics | Performance tests |

### From Tech Spec → Backend Tests

| Tech Spec Section | Test Type |
|-------------------|-----------|
| API Design | Contract tests |
| Data Model | DB integration tests |
| Error Handling | Error scenario tests |
| Security | Security tests |

### From Implementation Plan → Test Phases

| Plan Phase | Test Focus |
|------------|------------|
| Phase 1 | Unit tests for core logic |
| Phase 2 | Integration tests |
| Phase 3 | E2E tests |
| Phase 4 | Performance/load tests |

## Quick Commands

```bash
# Run all tests
npm test

# Run only unit tests
npm test -- --testPathPattern=unit

# Run only integration tests
npm test -- --testPathPattern=integration

# Run only E2E tests (requires DevTools MCP)
npm run test:e2e

# Run with coverage
npm test -- --coverage

# Run specific file
npm test -- path/to/test.ts
```

## Checklist Before Writing Tests

- [ ] Found latest PRD in `docs/prd/`
- [ ] Found latest Tech Spec in `docs/tech-spec/`
- [ ] Found latest Implementation Plan in `docs/implementation-plan/`
- [ ] Confirmed with user these are current documents
- [ ] Extracted user stories (→ GUI tests)
- [ ] Extracted API contracts (→ Backend tests)
- [ ] Extracted error scenarios (→ Error tests)
- [ ] Identified test phases from plan

## Anti-Patterns to Avoid

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| Testing implementation details | Brittle tests | Test behavior/outcomes |
| Unrealistic mock data | Miss edge cases | Use realistic factories |
| Only happy path | Miss errors | Test edge cases & errors |
| Tests depend on order | Flaky tests | Make tests independent |
| Over-mocking | Miss integration bugs | Use real integrations (<20% mocking) |
| Weak assertions | False positives | Assert exact values |

---

## Learning Mode Integration

### Decision Transparency Triggers
- **Test strategy choices**: Explain why specific test distribution chosen
- **Coverage decisions**: Show reasoning for coverage targets
- **Mock vs real**: Document when mocking is appropriate

### Debate Invitations
- **Test type balance**: When unit vs integration vs E2E trade-offs exist
- **Coverage targets**: When "good enough" vs "comprehensive" is unclear
- **Test data approach**: Factories vs fixtures vs inline data

### Feedback Requests
- After test suite written: Validate coverage completeness
- After test strategy defined: Confirm approach is appropriate
- At phase gate: Overall test quality rating (1-5)

### Example Transparency Block for Testing
```markdown
<decision-transparency>
**Decision:** Testing Trophy approach - 40% unit, 40% integration, 20% E2E

**Reasoning:**
- **CI time**: Full E2E would exceed 10 min target
- **Coverage balance**: Integration tests catch most real bugs
- **E2E focus**: Critical checkout path only

**Alternatives Considered:**
1. Heavy E2E (40%) - Rejected: CI too slow, tests too brittle
2. Heavy unit (80%) - Rejected: Misses integration issues

**Confidence:** High - Proven pattern for this type of app

**Open to Debate:** Yes - If CI time constraint changes
</decision-transparency>
```

### Example Debate Invitation for Testing
```markdown
<debate-invitation>
**Topic:** Test data strategy for user tests

**Option A: Inline Test Data**
- ✅ Pros: Easy to read, explicit
- ❌ Cons: Repetitive, hard to maintain

**Option B: Factory Functions**
- ✅ Pros: DRY, realistic data
- ❌ Cons: Slight indirection

**My Lean:** Option B - Factories produce realistic data consistently

**Your Input Needed:** Does team have factory pattern experience?
</debate-invitation>
```
