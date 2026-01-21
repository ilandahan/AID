---
name: role-developer
description: Developer role guidance within AID methodology. Use when assisting developers with implementation, writing code, debugging issues, reviewing technical feasibility, or translating requirements into robust solutions. Triggers on code writing, debugging, technical design, TDD workflow, or code review tasks.
---

# Developer Role

## Core Responsibilities

- Translate requirements into technical designs
- Write clean, tested, maintainable code
- Debug systematically - never guess
- Identify technical risks and edge cases early
- Ensure code quality through testing and review

## Phase-Specific Focus

| Phase | Focus | Key Outputs |
|-------|-------|-------------|
| Discovery | Technical feasibility | Risk notes, complexity estimates |
| PRD | Requirements clarity | Technical questions, edge cases |
| Tech Spec | Architecture design | Tech spec, API contracts, data models |
| Development | Implementation | Production code, tests, docs |
| QA & Ship | Bug fixes, release | Fixes, deployment docs |

## TDD Workflow

Follow RED-GREEN-REFACTOR cycle:

```
1. RED      → Write failing test
2. GREEN   → Write minimal code to pass
3. REFACTOR → Clean up (tests still pass)
4. REPEAT
```

## Systematic Debugging

**Iron Law: NO FIXES WITHOUT ROOT CAUSE INVESTIGATION.**

### Four Phases

1. **Root Cause** - Read errors, reproduce, check changes, gather evidence
2. **Pattern Analysis** - Find working examples, compare, identify differences
3. **Hypothesis** - Form single theory, test minimally, one variable at a time
4. **Implementation** - Create failing test, single fix, verify

If 3+ fixes failed → Stop and question architecture.

See `references/debugging-checklist.md` for complete checklist.
See `references/root-cause-tracing.md` for tracing technique.

## Defense-in-Depth

Validate at EVERY layer data passes through:

| Layer | Purpose |
|-------|---------|
| Entry Point | Reject invalid input at API boundary |
| Business Logic | Validate for specific operation |
| Environment Guards | Block dangerous ops in test/CI |
| Debug Instrumentation | Log context for forensics |

See `references/defense-in-depth.ts` for implementation example.

## Development Constraints

### 300-Line Rule

| File Size | Action |
|-----------|--------|
| < 200 lines | ✅ Ideal |
| 200-300 lines | ⚠️ Consider splitting |
| 300-400 lines | 🔴 Split now |
| > 400 lines | ❌ Must refactor |

Split when: multiple responsibilities, approaching limit, hard to name, multiple test files needed.

### Module Structure

```
feature/
├── feature.controller.ts   # HTTP layer (thin)
├── feature.service.ts      # Business logic
├── feature.repository.ts   # Data access
├── feature.types.ts        # Types/interfaces
└── feature.validation.ts   # Input validation
```

## Async Testing

Never use arbitrary timeouts. Wait for conditions:

```typescript
// ❌ Wrong
await sleep(100);
expect(result).toBeDefined();

// ✅ Right
await waitFor(() => result !== undefined);
expect(result).toBeDefined();
```

See `references/condition-based-waiting.ts` for utilities.

## Code Quality Standards

### Must Have
- Single responsibility functions
- DRY code
- Type hints on public functions
- Meaningful names
- Proper error handling
- Files under 300 lines
- Multi-layer validation

### Must Not Have
- `any` types without justification
- TODO/FIXME comments (track separately)
- Commented-out code
- Silent exception swallowing
- Business logic in controllers
- Arbitrary timeouts in tests
- Files over 400 lines

## Anti-Patterns

| Anti-Pattern | Fix |
|--------------|-----|
| No TDD | Write tests first |
| `if is_test:` in prod | No test logic in prod code |
| Happy path only | Test errors and edge cases |
| Over-mocking (>20%) | Use real dependencies |
| Guessing at fixes | Systematic debugging |
| Large files (>400) | Split into modules |

## Handoff Checklist

- [ ] All tests passing
- [ ] Code reviewed
- [ ] Error handling implemented
- [ ] Edge cases covered
- [ ] No files exceed 400 lines
- [ ] Multi-layer validation added

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/find-polluter.sh` | Find which test creates pollution |
| `scripts/check-file-size.sh` | Enforce 300-line rule |

## References

| File | When to Read |
|------|--------------|
| `references/debugging-checklist.md` | During any debugging session |
| `references/root-cause-tracing.md` | Bug deep in call stack |
| `references/defense-in-depth.ts` | After fixing data validation bugs |
| `references/condition-based-waiting.ts` | Writing async tests |
