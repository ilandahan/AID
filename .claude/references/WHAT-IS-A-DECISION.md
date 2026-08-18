# What Is a Decision?

> This document defines what qualifies as a "decision" worth logging in the AID Decision Log system.

---

## Quick Definition

> **A Decision is a choice that meets 2+ of these criteria:**
> 1. **Affects architecture** - shapes system structure
> 2. **Hard to reverse** - would require significant rework
> 3. **Multiple valid alternatives** - reasonable people could disagree
> 4. **Has tradeoffs** - each option has pros AND cons
> 5. **Impacts future work** - other work will depend on this
> 6. **Would be debated** - team members could reasonably argue
> 7. **Cross-cutting concern** - affects multiple components

---

## Decision Criteria Checklist

A choice qualifies as a decision if it meets **2 or more** of these criteria:

| Criterion | Question to Ask | Example YES | Example NO |
|-----------|-----------------|-------------|------------|
| **Affects architecture** | Does this shape system structure? | "Use microservices vs monolith" | "Name this function `getUser`" |
| **Hard to reverse** | Would changing this require significant rework? | "Use PostgreSQL" | "Use tabs vs spaces" |
| **Multiple valid alternatives** | Could reasonable people disagree? | "React vs Vue vs Svelte" | "Use `const` for constants" |
| **Has tradeoffs** | Does each option have pros AND cons? | "REST vs GraphQL" | "Fix this typo" |
| **Impacts future work** | Will other work depend on this? | "Use JWT for auth" | "Add this log statement" |
| **Would be debated** | Could team members reasonably argue? | "Monorepo vs polyrepo" | "Use descriptive variable names" |
| **Cross-cutting concern** | Does it affect multiple components? | "Error handling strategy" | "Local helper function" |

---

## Decision Categories

| Category | Examples | Typical Phase |
|----------|----------|---------------|
| **Architecture** | Monolith vs microservices, event-driven vs sync, serverless vs containers | Phase 2 (Tech Spec) |
| **Technology** | Database, framework, language, major libraries | Phase 0-2 |
| **Security** | Auth method, encryption approach, data handling policy | Phase 2 |
| **Integration** | Third-party APIs, external services, MCP servers | Phase 2-3 |
| **Data Model** | Schema design, relationships, storage format | Phase 2 |
| **API Design** | REST vs GraphQL, versioning strategy, error format | Phase 2 |
| **Testing Strategy** | Unit vs E2E ratio, mocking approach, coverage target | Phase 3 |
| **Scope** | Feature in/out, MVP boundaries, phase priorities | Phase 1 |
| **Process** | Deployment strategy, branching model, review process | Phase 3-5 |

---

## Decision Severity Levels

| Level | Description | Example | Action |
|-------|-------------|---------|--------|
| **Critical** | Foundational, very hard to change | Database choice, primary language, core framework | Always log immediately |
| **Major** | Significant impact, costly to change | Auth strategy, API design pattern, state management | Always log |
| **Minor** | Some impact, moderate effort to change | Specific library choice, folder structure convention | Log if debated |
| **Tactical** | Low impact, easy to change | Helper function approach, local optimization | Don't log |

---

## What is NOT a Decision

These are **implementation details** - do NOT log them:

| Not a Decision | Why |
|----------------|-----|
| Variable/function naming | Easy to change, local scope |
| Code formatting | Handled by linter, trivial to change |
| File organization within established pattern | Minor, easy to refactor |
| Specific CSS values | Implementation detail |
| Log message wording | Trivial to change |
| Comment text | Documentation, not architecture |
| Import order | Trivial, often auto-sorted |
| Which test to write first | Tactical, not strategic |
| Specific error message text | Easy to change |
| Internal helper function design | Local scope, easy to refactor |

---

## Decision Detection Flow

```
Choice made in conversation
        │
        ▼
┌───────────────────────────────────────┐
│ Does it affect architecture/technology? │
└─────────────────┬─────────────────────┘
                  │
        ┌─────────┴─────────┐
        ▼                   ▼
       YES                  NO
        │                   │
        ▼                   ▼
┌───────────────┐   ┌─────────────────────┐
│ Hard to reverse│   │ Were alternatives   │
│ or cross-cutting│  │ seriously debated?  │
└───────┬───────┘   └──────────┬──────────┘
        │                      │
   ┌────┴────┐            ┌────┴────┐
   ▼         ▼            ▼         ▼
  YES       NO           YES        NO
   │         │            │         │
   ▼         │            ▼         ▼
┌──────┐     │        ┌──────┐  ┌──────────┐
│ LOG  │     │        │ LOG  │  │ DON'T    │
│ IT   │     │        │ IT   │  │ LOG      │
└──────┘     │        └──────┘  └──────────┘
             │
             ▼
    ┌─────────────────┐
    │ Impacts future  │
    │ conversations?  │
    └────────┬────────┘
             │
        ┌────┴────┐
        ▼         ▼
       YES        NO
        │         │
        ▼         ▼
    ┌──────┐  ┌──────────┐
    │ LOG  │  │ DON'T    │
    │ IT   │  │ LOG      │
    └──────┘  └──────────┘
```

---

## Automatic Logging Triggers

Claude SHOULD automatically log a decision when:

| Trigger | Example |
|---------|---------|
| User explicitly asks "should we use X or Y?" | "Should we use REST or GraphQL?" |
| Debate occurs with 2+ options discussed | User challenges Claude's initial suggestion |
| Architecture diagram is created | System design in Tech Spec phase |
| Technology stack is defined | "We'll use Next.js, PostgreSQL, Prisma" |
| Security approach is chosen | "JWT with refresh tokens" |
| Major scope decision is made | "Feature X is out of scope for MVP" |
| User says "let's go with X" after discussion | Confirms a debated choice |

---

## Semi-Automatic Logging

When Claude detects a potential decision but isn't certain, ask:

```
💡 This seems like an important decision. Should I log it?

Decision: Use Prisma as ORM
Alternatives considered: TypeORM, Drizzle, raw SQL

[Yes, log it] [No, skip] [Let me clarify first]
```

---

## Manual Logging

User can explicitly request decision logging:

```
/log-decision "Title of decision"
```

Claude then prompts for:
- What was decided
- What alternatives were considered
- Why this choice was made

---

## Examples: Log or Not?

| Scenario | Log? | Reason |
|----------|------|--------|
| "Let's use PostgreSQL instead of MongoDB" | ✅ **YES** | Technology choice, hard to reverse, debated |
| "Let's use `camelCase` for variables" | ❌ No | Convention, handled by linter |
| "We'll implement auth with JWT + refresh tokens" | ✅ **YES** | Security architecture, affects all endpoints |
| "I'll add a try-catch here" | ❌ No | Local implementation detail |
| "Let's use React Query for server state" | ✅ **YES** | Library choice with codebase-wide patterns |
| "I'll name this component `UserCard`" | ❌ No | Naming, easy to change |
| "We'll use feature flags for gradual rollout" | ✅ **YES** | Deployment/process strategy |
| "Let's add a comment explaining this" | ❌ No | Documentation, trivial |
| "MVP will NOT include admin panel" | ✅ **YES** | Scope decision, affects planning |
| "I'll use a `for` loop instead of `map`" | ❌ No | Code style, easy to change |
| "Let's use Tailwind instead of styled-components" | ✅ **YES** | CSS strategy, affects all components |
| "I'll extract this to a helper function" | ❌ No | Local refactor |
| "We'll version the API with URL prefix `/v1/`" | ✅ **YES** | API design, affects all consumers |
| "Let's use pnpm instead of npm" | ⚠️ Maybe | Minor tooling, log if team debated it |

---

## Decision Log Entry Format

When a decision IS logged, it goes to `.aid/decisions/{YYYY-MM-DD}-{slug}.json`:

```json
{
  "$schema": "aid-decision-v1",
  "version": "1.0",

  "metadata": {
    "id": "DEC-2025-12-31-001",
    "created_at": "2025-12-31T14:30:00Z",
    "updated_at": null,
    "phase": 2,
    "phase_name": "Tech Spec",
    "role": "lead",
    "conversation_id": null,
    "supersedes": null
  },

  "decision": {
    "title": "Database Selection",
    "category": "technology",
    "summary": "Use PostgreSQL as primary database",
    "status": "approved",
    "severity": "critical"
  },

  "context": {
    "problem": "Need database for user data with complex queries",
    "constraints": ["Team knows SQL", "Need JSONB support"],
    "requirements_ref": ["REQ-DB-001"]
  },

  "alternatives": [
    { "option": "PostgreSQL", "pros": [...], "cons": [...] },
    { "option": "MongoDB", "pros": [...], "cons": [...] }
  ],

  "rationale": "PostgreSQL selected because team has SQL experience and we need JSONB for flexible schemas."
}
```

**Note**: The index at `.aid/decisions/index.json` uses `phases_relevant` (array) to track which phases a decision is relevant to.

---

## Key Principle

> **When in doubt, ask the user.** It's better to offer to log a decision and have them decline than to lose important context that future conversations will need.

---

## Related Files

- Decision Log Schema: `docs/research/2025-12-31-phase-gate-enforcement.md` (Section 13)
- Decision Storage: `.aid/decisions/`
- Reading Decisions: See CLAUDE.md "Decision Context Loading" section
