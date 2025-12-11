# /write-tests Command

Write tests using Test-Driven Development (TDD) methodology, driven by project documents.

## Usage

```
/write-tests <feature-or-function> [--type unit|integration|e2e]
```

## What It Does

1. **Reads Project Documents**
   - Finds latest PRD: `docs/prd/YYYY-MM-DD-[feature].md`
   - Finds latest Tech Spec: `docs/tech-spec/YYYY-MM-DD-[feature].md`
   - Finds latest Implementation Plan: `docs/implementation-plan/YYYY-MM-DD-[feature].md`

2. **Confirms with User**
   - Shows found documents
   - Asks if these are the correct/current versions

3. **Writes Tests FIRST**
   - Before any implementation
   - Driven by document requirements
   - Strong, specific assertions

4. **Uses Skill**
   - `test-driven` skill for methodology

## CRITICAL: Document-Driven Testing

```
┌─────────────────────────────────────────────────────────────────┐
│  BEFORE WRITING ANY TEST:                                       │
│                                                                 │
│  1. Read latest PRD         → docs/prd/[latest].md              │
│  2. Read latest Tech Spec   → docs/tech-spec/[latest].md        │
│  3. Read Implementation Plan → docs/implementation-plan/[latest].md │
│                                                                 │
│  4. CONFIRM with user: "Are these the current documents?"       │
└─────────────────────────────────────────────────────────────────┘
```

## Document-to-Test Mapping

| Document | Test Type | What to Extract |
|----------|-----------|-----------------|
| **PRD** | GUI/E2E Tests | User stories → E2E flows |
| **Tech Spec** | Backend Tests | API contracts → Contract tests |
| **Tech Spec** | Backend Tests | Error codes → Error tests |
| **Implementation Plan** | Test Phases | Exit criteria → Assertions |

## Test Types

### Backend Tests (Unit + Integration)

From **Tech Spec**:
```typescript
// API Contract Test (from Tech Spec API Endpoints section)
describe('POST /api/auth/register', () => {
  test('returns 201 with valid data', async () => {
    const response = await request(app)
      .post('/api/auth/register')
      .send({ email: 'test@example.com', password: 'SecurePass123!' })
      .expect(201);

    expect(response.body).toMatchObject({
      user: { id: expect.any(String), email: 'test@example.com' },
      token: expect.stringMatching(/^eyJ/)
    });
  });

  // From Tech Spec Error Handling section
  test('returns 409 when email exists', async () => {
    await request(app)
      .post('/api/auth/register')
      .send({ email: 'existing@example.com', password: 'Pass123!' })
      .expect(409);
  });
});
```

### GUI Tests (E2E with DevTools MCP)

From **PRD User Stories**:
```typescript
// E2E Test (from PRD User Story US-001)
describe('User Registration Flow', () => {
  // PRD US-001: "As a user, I can register an account"
  test('complete registration creates account', async () => {
    await mcp.devtools.navigate('http://localhost:3000/register');
    await mcp.devtools.type('#email', 'newuser@example.com');
    await mcp.devtools.type('#password', 'SecurePass123!');
    await mcp.devtools.click('#submit');

    await mcp.devtools.waitForSelector('.success-message');
    const message = await mcp.devtools.getText('.success-message');
    expect(message).toContain('Registration successful');
  });
});
```

## Examples

```bash
# Write tests for a feature (auto-detects types needed)
/write-tests user-authentication

# Write only backend tests
/write-tests user-authentication --type backend

# Write only E2E tests
/write-tests user-authentication --type e2e

# Write tests for specific function
/write-tests validate-email --type unit
```

## TDD Workflow

```
1. Read docs → 2. Confirm → 3. Write test → 4. Run (FAIL) → 5. Implement → 6. Run (PASS)
```

## Critical Rules

```
DO:
✓ Read PRD, Tech Spec, Implementation Plan FIRST
✓ Confirm documents with user
✓ Write tests BEFORE implementation
✓ Use realistic test data
✓ Test happy paths AND edge cases
✓ Use strong assertions

DON'T:
✗ Skip document reading
✗ Mock more than 20% of dependencies
✗ Use weak assertions
✗ Use simplified test data
```

## Test Categories

| Category | Location | From Document |
|----------|----------|---------------|
| Unit | `tests/unit/` | Tech Spec (interfaces) |
| Integration | `tests/integration/` | Tech Spec (API endpoints) |
| E2E | `tests/e2e/` | PRD (user stories) |

## Coverage Checklist

- [ ] All PRD user stories have E2E tests
- [ ] All Tech Spec endpoints have integration tests
- [ ] All error codes have error tests
- [ ] All Implementation Plan exit criteria have assertions

## Output Format

```
# Test Plan for [Feature]

## Documents Found
- PRD: docs/prd/2024-06-15-user-authentication.md
- Tech Spec: docs/tech-spec/2024-06-16-user-authentication.md
- Implementation Plan: docs/implementation-plan/2024-06-17-user-authentication.md

## Test Coverage

### From PRD User Stories
- US-001: Registration flow → tests/e2e/registration.e2e.test.ts
- US-002: Login flow → tests/e2e/login.e2e.test.ts

### From Tech Spec API Endpoints
- POST /api/auth/register → tests/integration/auth.integration.test.ts
- POST /api/auth/login → tests/integration/auth.integration.test.ts

## Test Files Created
- tests/unit/validators.test.ts
- tests/integration/auth.integration.test.ts
- tests/e2e/registration.e2e.test.ts
```

## Tips

- Tests are requirements documentation
- If hard to test, design might be wrong
- Realistic data catches real bugs
- Strong assertions prevent false confidence

---

## Prompt

```markdown
**Role**: You are a senior QA engineer specializing in Test-Driven Development.

**Task**: Write comprehensive tests for [FEATURE_OR_FUNCTION].

**Context**:
- Feature: [FEATURE_OR_FUNCTION]
- Framework: Jest (TypeScript)

**Skill to use**:
- test-driven skill

**CRITICAL STEPS**:
1. List files in docs/prd/, docs/tech-spec/, docs/implementation-plan/
2. Find latest documents for this feature
3. CONFIRM with user: "Found these documents: [list]. Are these current?"
4. Wait for user confirmation
5. Read documents and extract test requirements
6. Write tests based on documents

**Document Mapping**:
- PRD User Stories → E2E tests (tests/e2e/)
- Tech Spec API Endpoints → Integration tests (tests/integration/)
- Tech Spec Error Handling → Error tests
- Implementation Plan Exit Criteria → Assertions

**Stopping Condition**:
- User confirmed documents are current
- All PRD user stories have E2E tests
- All Tech Spec endpoints have integration tests

---
Feature: [FEATURE_OR_FUNCTION]
---
```
