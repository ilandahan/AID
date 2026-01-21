---
name: aid-development
description: AID Phase 4 - Development phase guidance. Use this skill when implementing features, writing production code, following TDD practices, conducting code reviews, or transitioning from implementation planning to QA. Ensures quality code with tests built in from the start.
---

# Development Phase Skill

## Phase Overview

**Purpose**: Implement the technical solution according to the spec, with quality built in from the start through TDD practices.

**Entry Criteria**:
- Tech spec phase completed and approved
- Architecture and APIs defined
- Data models specified
- Development environment ready

**Exit Criteria**:
- All features implemented
- All tests passing
- Code reviewed
- Ready for QA validation

## Deliverables

### 1. Production Code
- **Description**: Implementation of all requirements
- **Format**: Clean, documented code following team standards
- **Quality bar**: Passes all tests, follows coding standards, reviewed

### 2. Test Suite
- **Description**: Comprehensive tests at all levels
- **Format**: Unit tests, integration tests, E2E tests as appropriate
- **Quality bar**: >80% coverage, realistic test data, minimal mocking

### 3. Documentation
- **Description**: Code documentation, API docs, README updates
- **Format**: Inline comments, generated docs, markdown
- **Quality bar**: New developer can understand the code

## Role-Specific Guidance

### For Product Managers
- Available for requirement clarifications
- Validate implementation matches intent
- Review user-facing aspects
- Make scope decisions when needed

### For Developers
- Write tests FIRST (TDD)
- Implement to make tests pass
- Keep implementation general (no test-specific code)
- Request clarification rather than assuming

### For QA Engineers
- Review test coverage
- Validate test data quality
- Identify missing test scenarios
- Prepare for QA phase

### For Tech Leads
- Conduct code reviews
- Ensure standards compliance
- Unblock technical issues
- Validate architectural alignment

## TDD Workflow

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

## Common Pitfalls

| Pitfall | Problem | Fix |
|---------|---------|-----|
| Skipping TDD | Tests written after code | Write tests first, then implement |
| Test-specific code | `if is_test:` in production | No test-specific logic in prod code |
| Hardcoded values | Matching test expectations exactly | Use proper algorithms, not shortcuts |
| Over-mocking | Everything is mocked | Use real integrations (<20% mocking) |
| Happy path only | Only success cases tested | Test errors and edge cases |
| Weak assertions | `expect(result).toBeDefined()` | Assert exact values |

## Phase Gate Checklist

Before requesting approval to proceed:

- [ ] All features implemented per spec
- [ ] All tests written and passing
- [ ] Tests use realistic data
- [ ] Edge cases and errors tested
- [ ] Code reviewed and approved
- [ ] No test-specific logic in production code
- [ ] Documentation updated
- [ ] No skipped tests without justification

## Development Workflow

### Step 1: Load Context
```
1. Read Tech Spec for current task
2. Review API contracts and data models
3. Understand acceptance criteria
```

### Step 2: Write Failing Test
```typescript
// Start with test that describes behavior
test('creates user with valid data', async () => {
  const userData = {
    email: 'test@example.com',
    name: 'Test User'
  };

  const user = await userService.create(userData);

  expect(user.id).toMatch(/^usr_/);
  expect(user.email).toBe('test@example.com');
  expect(user.createdAt).toBeInstanceOf(Date);
});
```

### Step 3: Implement to Pass
```typescript
// Write minimal code to make test pass
async create(data: CreateUserInput): Promise<User> {
  const user = await this.repository.create({
    id: generateId('usr'),
    ...data,
    createdAt: new Date()
  });
  return user;
}
```

### Step 4: Refactor
```typescript
// Clean up while keeping tests green
async create(data: CreateUserInput): Promise<User> {
  this.validateEmail(data.email);
  return this.repository.create(this.buildUser(data));
}
```

### Step 5: Repeat
Continue with next test case (error handling, edge cases, etc.)

## Transition to QA & Ship Phase

Hand off:
- Complete, tested code
- Test results and coverage report
- Known issues list (if any)
- Deployment instructions
- Any configuration requirements

## Code Quality Standards

### Required
- [ ] Functions have single responsibility
- [ ] DRY: No copy-pasted logic
- [ ] Type hints on public functions
- [ ] Meaningful variable/function names
- [ ] Error handling implemented
- [ ] No hardcoded configuration values

### Forbidden
- [ ] No `any` types without justification
- [ ] No `// TODO` or `// FIXME` comments
- [ ] No commented-out code
- [ ] No test-specific branching
- [ ] No silent exception swallowing

## MANDATORY: Code Documentation Standards

**EVERY file written by AID MUST include documentation at THREE levels:**

See full reference: `references/documentation-standards.md`

### 1. File-Level Comment (TOP OF FILE)
```typescript
/**
 * @file UserService.ts
 * @description What this file does and its purpose.
 *
 * @related
 *   - ./UserRepository.ts - Data access layer
 *   - ./UserController.ts - HTTP endpoints
 *
 * @created 2025-12-15 by AID
 */
```

### 2. Component/Class Comment
```typescript
/**
 * UserService - Business logic for user operations.
 *
 * Responsibilities:
 * - User creation and validation
 * - Authentication and session management
 */
export class UserService {
```

### 3. Function Comment (with @related for cross-file references)
```typescript
/**
 * Creates a new user account.
 *
 * @param data - User creation data
 * @returns The created user object
 * @throws {ValidationError} If email invalid
 *
 * @related
 *   - ../validators/emailValidator.ts - Email validation
 *   - ./UserRepository.ts - Database persistence
 */
async createUser(data: CreateUserInput): Promise<User> {
```

### Documentation Checklist
- [ ] File has @file, @description, @related, @created at top
- [ ] Every class/component has purpose comment
- [ ] Every function has @param, @returns, @throws, @related
- [ ] Cross-file dependencies documented with @related
- [ ] Non-obvious logic has inline comments

---

## Learning Mode Integration

### Decision Transparency Triggers
- **Pattern selection**: Show reasoning when choosing design patterns
- **Library choices**: Explain why specific libraries selected
- **Optimization decisions**: Document trade-offs in performance choices
- **Error handling strategy**: Explain approach to error management

### Debate Invitations
- **Implementation approach**: When multiple valid patterns exist
- **Test strategy**: When coverage trade-offs are significant
- **Refactoring scope**: When "good enough" vs "ideal" is unclear

### Feedback Requests
- After significant feature completion: Validate approach
- After code review findings: Confirm understanding of feedback
- At phase gate: Overall code quality rating (1-5)

### Example Transparency Block
```markdown
<decision-transparency>
**Decision:** Using Repository pattern for data access

**Reasoning:**
- **Testability**: Allows mocking data layer in unit tests
- **Abstraction**: Hides database specifics from business logic
- **Consistency**: Matches existing codebase patterns

**Alternatives Considered:**
1. Direct ORM calls - Rejected: Harder to test, couples business logic to DB
2. Active Record - Rejected: Less explicit, harder to mock

**Confidence:** High - Standard pattern for this type of application

**Open to Debate:** No - This aligns with team standards
</decision-transparency>
```

### Learning Capture Example
```markdown
<learning-captured>
**What I Learned:**
This team prefers inline comments for complex algorithms over separate docs.

**Source:**
- User feedback on: Code review suggestions
- Context: Was told to add inline explanation instead of README section

**Applied To:**
- Future complex logic will include inline explanations
- Will still use docs for API contracts and architecture

**Verification:**
- Will apply this in next algorithm implementation
</learning-captured>
```
