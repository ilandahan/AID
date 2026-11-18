---
name: role-developer
description: Developer role in AID methodology. Use for implementation, debugging, technical design, TDD workflow, code review.
---

# Developer Role

## Core Responsibilities
- Translate requirements to technical designs
- Write clean, tested, maintainable code
- Debug systematically - never guess
- Identify risks and edge cases early

## Phase Focus
| Phase | Focus | Output |
|---|---|---|
| Discovery | Feasibility | Risk notes, complexity |
| PRD | Requirements clarity | Questions, edge cases |
| Tech Spec | Architecture | Spec, APIs, data models |
| Development | Implementation | Code, tests, docs |
| QA & Ship | Bug fixes | Fixes, deployment docs |

## TDD Workflow
RED (Write failing test) -> GREEN (Minimal code) -> REFACTOR (Clean up) -> REPEAT

## Eval-Driven Development (Agentic Layer)
Always applies, scaled by the PRD's §1.5 Solution Shape level. Levels 0-1: the TDD above plus logs and metrics.

For prompts, tools and agents (levels 2-5):
- **Evals first:** write new-behaviour cases in the dev/targeted suite, see them fail, then change the prompt, tool or agent. QA owns the golden set; propose additions through a QA-reviewed PR.
- **Trace by default** (§7A.7 Telemetry & Traces): plan, tool calls, results, escalations, cost, latency. No secrets in traces.
- **Version prompts and tool definitions** as files in the repo; bump on every behaviour change; log the version in each trace.
- **Regression eval on every change** (prompt, tool, model, agent): zero never-do failures. The release gate runs on QA's held-out split, which you never tune on.
- **Least privilege:** implement only the tools and permissions listed in §7A.2 Tools & Permissions.

Detail: `SKILL.extended.md` → Eval-Driven Development; cycle: `../test-driven/SKILL.md`.

## Systematic Debugging
NO FIXES WITHOUT ROOT CAUSE.

1. Root Cause - Read errors, reproduce, gather evidence
2. Pattern Analysis - Find working examples, compare
3. Hypothesis - Single theory, test minimally
4. Implementation - Failing test, single fix, verify

If 3+ fixes failed -> Stop, question architecture.

## Defense-in-Depth
Validate at EVERY layer:

| Layer | Purpose |
|---|---|
| Entry Point | Reject invalid at boundary |
| Business Logic | Validate for operation |
| Environment Guards | Block dangerous ops |
| Debug Instrumentation | Log for forensics |

## 300-Line Rule
| Size | Action |
|---|---|
| < 200 | Ideal |
| 200-300 | Consider splitting |
| 300-400 | Split now |
| > 400 | Must refactor |

## Module Structure
```
feature/
  feature.controller.ts   # HTTP (thin)
  feature.service.ts      # Business logic
  feature.repository.ts   # Data access
  feature.types.ts        # Types
  feature.validation.ts   # Validation
```

## Code Quality
Must have: single responsibility, DRY code, type hints, meaningful names, error handling, files < 300 lines.

Must not have: any types, TODO/FIXME, commented-out code, silent exceptions, business logic in controllers, arbitrary timeouts in tests.

## Async Testing
```typescript
// Wrong
await sleep(100);

// Right
await waitFor(() => result !== undefined);
```

## Anti-Patterns
| Anti-Pattern | Fix |
|---|---|
| No TDD | Tests first |
| if is_test in prod | No test logic |
| Happy path only | Test errors |
| Over-mocking | Real dependencies |
| Guessing at fixes | Systematic debug |
| Large files | Split modules |
| Prompt tweaked before an eval exists | Eval first |
| Unversioned prompt or tool | Version file, log it |

## Handoff Checklist
- [ ] All tests passing
- [ ] Code reviewed
- [ ] Error handling implemented
- [ ] Edge cases covered
- [ ] Files < 400 lines
- [ ] Multi-layer validation
- [ ] Evals written first; regression eval green (level 0-1: tests first)
- [ ] Traces on by default (level 0-1: logs and metrics)
- [ ] Prompts and tool definitions versioned
