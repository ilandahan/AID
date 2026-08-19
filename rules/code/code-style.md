---
paths:
  - "src/**/*.ts"
  - "src/**/*.tsx"
  - "src/**/*.js"
  - "src/**/*.jsx"
  - "functions/**/*.ts"
  - "services/**/*.ts"
  - "shared/**/*.ts"
---

# Code Style Rules

Rules for writing clean, maintainable code in this project.

---

## WHY Documentation

Every function MUST include WHY documentation:

```typescript
// ─────────────────────────────────────────────────
// WHY: [Problem this function solves]
// WHAT: [What it does]
// CONNECTION: [What calls it, what it calls]
// ─────────────────────────────────────────────────
function functionName(params) {
  // implementation
}
```

---

## Component Documentation

Every component MUST document connections:

```typescript
/**
 * ComponentName
 *
 * WHY THIS EXISTS:
 * [Core purpose and problem it solves]
 *
 * CONNECTIONS:
 * - CALLED BY: [List callers and WHY they call this]
 * - CALLS: [List dependencies and WHY we need them]
 *
 * DESIGN DECISIONS:
 * - WHY [decision]: [Reasoning]
 */
```

---

## Over-Engineering Prevention

**IRON RULES:**

- Only make changes that are directly requested or clearly necessary
- Keep solutions simple and focused
- Don't add features, refactor code, or make "improvements" beyond what was asked
- Don't add docstrings, comments, or type annotations to code you didn't change
- Only add comments where the logic isn't self-evident

---

## Avoid These Patterns

| Anti-Pattern | Why It's Bad | Do This Instead |
|--------------|--------------|-----------------|
| Premature abstraction | Creates complexity | Write direct code first |
| Feature flags for one-off | Adds maintenance burden | Just change the code |
| Backwards-compat hacks | Clutters codebase | Delete unused code |
| Unused `_vars` | Confusing | Remove completely |
| `// removed` comments | Noise | Just delete the code |

---

## Simplicity Guidelines

- Three similar lines of code is better than a premature abstraction
- Don't design for hypothetical future requirements
- Don't create helpers for one-time operations
- Don't add error handling for scenarios that can't happen
- Trust internal code and framework guarantees

---

## Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Functions | camelCase, verb-first | `getUserById`, `validateEmail` |
| Components | PascalCase | `UserProfile`, `LoginForm` |
| Constants | UPPER_SNAKE | `MAX_RETRY_COUNT`, `API_BASE_URL` |
| Types/Interfaces | PascalCase | `UserConfig`, `ApiResponse` |
| Files | kebab-case | `user-service.ts`, `api-client.ts` |
