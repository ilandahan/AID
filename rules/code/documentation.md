---
paths:
  - "src/**/*.ts"
  - "src/**/*.tsx"
  - "functions/**/*.ts"
  - "services/**/*.ts"
---

# Documentation Rules

Rules for documenting code in this project.

---

## When to Document

| Document | Don't Document |
|----------|----------------|
| WHY something exists | WHAT code does (if obvious) |
| Non-obvious decisions | Every function |
| Complex algorithms | Simple CRUD operations |
| API contracts | Internal implementation details |
| Workarounds with context | Self-explanatory code |

---

## Function Documentation

Only add comments when logic isn't self-evident:

```typescript
// GOOD - Explains WHY
// Rate limit to prevent API abuse (max 100 req/min per user)
const rateLimiter = createRateLimiter({ max: 100, window: 60000 });

// BAD - States the obvious
// This function gets a user by ID
function getUserById(id: string) { ... }
```

---

## Decision Documentation

Document non-obvious decisions:

```typescript
// WHY: Using in-memory cache instead of Redis because:
// 1. Data is small (<10MB) and user-specific
// 2. Avoids network latency for frequent reads
// 3. Acceptable to lose on restart (rebuilds in <1s)
const cache = new Map<string, UserPreferences>();
```

---

## API Documentation

Document public APIs with JSDoc:

```typescript
/**
 * Creates a new user account.
 *
 * @param email - User's email address (must be unique)
 * @param password - Password (min 8 chars, requires special char)
 * @returns The created user object without password
 * @throws {ValidationError} If email format invalid
 * @throws {ConflictError} If email already exists
 *
 * @example
 * const user = await createUser('user@example.com', 'SecurePass123!');
 */
async function createUser(email: string, password: string): Promise<User> {
  // implementation
}
```

---

## README Documentation

Project README should include:

1. **What** - Brief description of project purpose
2. **Why** - Problem it solves
3. **Quick Start** - Get running in <5 minutes
4. **Environment Setup** - Required env vars (without values)
5. **Development** - How to run locally
6. **Testing** - How to run tests

---

## Inline Comments

**DO:**
- Explain WHY, not WHAT
- Document workarounds with ticket references
- Note performance considerations
- Explain regex patterns

**DON'T:**
- Comment obvious code
- Leave TODO without ticket
- Comment out code (delete it)
- Add change history (use git)

```typescript
// GOOD
// Workaround for Safari bug with date parsing (ISSUE-1234)
const date = new Date(dateString.replace(/-/g, '/'));

// BAD
// Increment counter by 1
counter++;
```

---

## Type Documentation

Use TypeScript types as documentation:

```typescript
// Types serve as documentation
interface CreateUserRequest {
  /** User's email address - must be unique */
  email: string;

  /** Password - min 8 chars, must include number and special char */
  password: string;

  /** Optional display name - defaults to email username */
  displayName?: string;
}
```
