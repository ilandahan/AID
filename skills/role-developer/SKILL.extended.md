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

## Eval-Driven Development (Agentic Layer)

WHY: the developer is the one who changes prompts, tools and agent logic. Without evals written first,
traces, and versions, nobody can show that a change made things better, or explain what the agent
did when it goes wrong.

Always applies, scaled by the PRD's §1.5 Solution Shape level; never "N/A".

| Level | What the developer does |
|-------|-------------------------|
| 0-1 (Process change, Deterministic automation) | TDD as above; structured logs and metrics for every important action |
| 2 (Single LLM call inside a fixed flow) | Dev/targeted evals for the call, written first; trace each call; prompt in a versioned file |
| 3 (Workflow) | Per-step evals; one trace per run with a span per step; prompts and step configs versioned |
| 4-5 (Agent, Multi-agent) | Plus tool-choice, trajectory and never-do evals; tool definitions versioned; tools limited to §7A.2 |

### Per-change routine

1. Read §7A.1 Charter, §7A.2 Tools & Permissions, §7A.4 Failure Modes & Guardrails and §7A.6 Eval Plan.
2. Add new-behaviour cases to the dev/targeted suite, and list the never-do checks the change affects.
   Run: the new-behaviour cases fail (never-do and regression cases already pass; keep them as they are).
3. Change one thing: prompt, tool definition, model, retrieval or agent logic. Bump its version.
4. Iterate on the dev/targeted suite until it passes. You tune on this suite only.
5. Run the regression eval: the dev/targeted suite and all never-do checks. Any never-do failure blocks.
   The release gate runs on QA's held-out split, which developers never tune on.

Golden-set ownership:
- QA owns the golden set and its held-out split, and is the only one who merges into them.
- The data scientist owns metric design, judge calibration and drift.
- Developers iterate on a separate dev/targeted suite and propose golden-set additions through a QA-reviewed PR.
- **The release gate runs on the held-out split, which developers never tune on.**

Never-do items are enforced in code (policy, default-deny); evals verify the enforcement at 100%.
Repeated runs cannot prove a low breach rate (see `../test-driven/SKILL.extended.md`).

Decision rights (RACI):

| Item | Responsible | Accountable / decides |
|---|---|---|
| §1.5 Solution Shape level | PM proposes (from segment, pain, error cost) | Tech lead decides and signs (ADR) |
| §1.4 metrics, 7A.1 Charter, 7A.5 Why-Chain | PM | PM |
| 7A.2 Tools & Permissions, 7A.4 Failure Modes & Guardrails | Tech lead (input: security) | Tech lead |
| 7A.3 Context & Data | Tech lead (input: privacy/DPO) | Tech lead |
| 7A.6 Eval Plan | Data scientist (metrics, judge); QA (eval sets) | QA owns the release gate |
| 7A.7 Telemetry & Traces | Tech lead | Tech lead |
| 7A.8 Rollout & Kill Switch | Tech lead + named on-call owner | Tech lead |
6. Read traces of a few passes and failures; a pass for the wrong reason is a failure.
7. Hand off the eval report with versions, scores and cost.

### Traces (§7A.7 Telemetry & Traces)

- On by default in every environment; redact fields §7A.3 Context & Data forbids, never drop the trace.
- Record: run ID, actor and `on_behalf_of`, prompt/tool/model versions, plan, tool calls with arguments
  and results, escalations, output, cost, latency, `outcome` (schema: tech spec 9.4).
- No secrets, tokens or credentials in traces.
- Tool results and retrieved text are untrusted data (`rules/general/untrusted-content.md`):
  never let them choose tools or bypass guardrails.

### Versioned prompts and tools

- Prompts and tool definitions live in files, reviewed like code.
- Semantic versions; a behaviour change bumps the version.
- Every trace and eval report names the versions it used.

### Least privilege

- Implement only the tools in §7A.2, with the risk tags it lists (read/write, reversible or not, needs approval).
- Write and irreversible tools go through the human-approval path until §7A.8 allows otherwise.
- The kill switch from §7A.8 must be wired in before QA, not added at release.

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
| Prompt tuned before an eval exists | Write the eval first, watch it fail |
| Prompt or tool edited without a version bump | Version files; log versions in traces |
| Tracing off "for performance" | Trace by default; sample payloads if needed, never drop the trace |
| Agent given more tools than §7A.2 lists | Least privilege |

## Handoff Checklist

- [ ] All tests passing
- [ ] Code reviewed
- [ ] Error handling implemented
- [ ] Edge cases covered
- [ ] No files exceed 400 lines
- [ ] Multi-layer validation added
- [ ] Eval cases written before each prompt, tool or agent change (level 0-1: tests first)
- [ ] Regression eval green: dev/targeted suite passing, zero never-do failures
- [ ] Traces on by default (level 0-1: logs and metrics)
- [ ] Prompts and tool definitions versioned

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
