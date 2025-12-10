# Phase Enforcement Skill

## Purpose

Enforces AID phase gates. Claude MUST check current phase before any work and REFUSE work that belongs to a later phase.

---

## Core Rule

**Before doing ANY work, Claude MUST:**
1. Read `.aid/state.json`
2. Classify the requested work
3. Check if that work is allowed in current phase
4. REFUSE if not allowed

---

## Work Classification

| Category | Examples | First Allowed |
|----------|----------|---------------|
| `requirements` | PRD, user stories, scope | Phase 1 |
| `architecture` | System design, DB schema, APIs | Phase 2 |
| `planning` | Jira issues, task breakdown | Phase 3 |
| `coding` | Components, features, tests | Phase 4 |
| `qa` | Testing review, deployment | Phase 5 |

---

## Phase Permissions

```javascript
const PHASE_ALLOWED = {
  1: ["requirements"],
  2: ["requirements", "architecture"],
  3: ["requirements", "architecture", "planning"],
  4: ["requirements", "architecture", "planning", "coding"],
  5: ["requirements", "architecture", "planning", "coding", "qa"],
};
```

---

## Detection Patterns

### Phase 1 Work (requirements)
- "create PRD", "write requirements", "define scope"
- "user stories", "acceptance criteria"

### Phase 2 Work (architecture)
- "design architecture", "create schema", "define API"
- "tech spec", "data model", "component design"

### Phase 3 Work (planning)
- "create epic", "jira", "break down"
- "tasks", "estimate", "sprint"

### Phase 4 Work (coding)
- "create component", "implement", "write code"
- "build", "create file", "test" (writing tests)

### Phase 5 Work (qa)
- "deploy", "release", "ship"
- "review coverage", "performance test"

---

## Violation Template

```
⛔ PHASE GATE VIOLATION

Current Phase: [N] [Phase Name]
Requested: [What user asked for]
Category: [Category]

This work belongs to Phase [X] ([Phase Name]).

Complete these phases first:
[List incomplete phases with their requirements]

Commands:
  /phase - See current status
  /gate-check - See what's needed
```

---

## Exceptions

### Always Allowed
- Reading/viewing files
- Documentation updates
- Answering questions

### With Warning
- Fixing earlier phase artifacts (show warning but allow)

### Override
- User can say "override: [reason]"
- Log override in `.aid/overrides.log`

---

## Integration

This skill works WITH other skills:
- `system-architect` → Only active in Phase 2+
- `atomic-design-system` → Only active in Phase 4+
- `code-review` → Only active in Phase 4+

Claude checks phases BEFORE loading specialized skills.
