# Iron Rules: Phase 3 Information Architecture

## Overview

These rules define **UNBREAKABLE** information boundaries for Jira issue hierarchy.
Violation of these rules results in invalid breakdown and blocked Phase 3 completion.

---

## Information Boundaries

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║   ⛔ IRON RULES - PHASE 3 INFORMATION BOUNDARIES                              ║
║                                                                               ║
║   These rules are UNBREAKABLE. Violation = Invalid breakdown.                 ║
║                                                                               ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║   EPIC          │ Business Logic ONLY (from Research + PRD)                   ║
║   ─────────────────────────────────────────────────────────────────────────   ║
║   ✅ ALLOWED    │ • Business goal / outcome                                   ║
║                 │ • Market context                                            ║
║                 │ • Success metrics (business KPIs)                           ║
║                 │ • Stakeholder impact                                        ║
║                 │ • WHY we're building this                                   ║
║   ─────────────────────────────────────────────────────────────────────────   ║
║   ❌ FORBIDDEN  │ • Technical approach                                        ║
║                 │ • Architecture decisions                                    ║
║                 │ • API design                                                ║
║                 │ • Implementation details                                    ║
║                 │ • Component names                                           ║
║                                                                               ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║   STORY         │ Product Logic ONLY (from PRD)                               ║
║   ─────────────────────────────────────────────────────────────────────────   ║
║   ✅ ALLOWED    │ • User persona                                              ║
║                 │ • User need / problem                                       ║
║                 │ • User value / benefit                                      ║
║                 │ • Acceptance criteria (user perspective)                    ║
║                 │ • WHAT user can do                                          ║
║   ─────────────────────────────────────────────────────────────────────────   ║
║   ❌ FORBIDDEN  │ • Database schema                                           ║
║                 │ • API endpoints                                             ║
║                 │ • Technical constraints                                     ║
║                 │ • Architecture patterns                                     ║
║                 │ • HOW it's implemented                                      ║
║                                                                               ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║   TASK          │ Tech Spec ONLY                                              ║
║   ─────────────────────────────────────────────────────────────────────────   ║
║   ✅ ALLOWED    │ • Technical approach                                        ║
║                 │ • Architecture decisions                                    ║
║                 │ • API contracts                                             ║
║                 │ • Data models                                               ║
║                 │ • Dependencies                                              ║
║                 │ • HOW to implement                                          ║
║   ─────────────────────────────────────────────────────────────────────────   ║
║   ❌ FORBIDDEN  │ • Business justification                                    ║
║                 │ • User stories                                              ║
║                 │ • Market context                                            ║
║                 │ • Acceptance criteria (that's sub-task)                     ║
║                 │ • WHY we're doing this                                      ║
║                                                                               ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║   SUB-TASK      │ Acceptance Criteria ONLY                                    ║
║   (QA Gate)                                                                   ║
║   ─────────────────────────────────────────────────────────────────────────   ║
║   ✅ ALLOWED    │ • MUST achieve (success criteria)                           ║
║                 │ • MUST NOT (negative criteria)                              ║
║                 │ • NOT INCLUDED (scope boundary)                             ║
║                 │ • Best practices checklist                                  ║
║                 │ • WHAT to verify                                            ║
║   ─────────────────────────────────────────────────────────────────────────   ║
║   ❌ FORBIDDEN  │ • Technical approach                                        ║
║                 │ • Architecture reasoning                                    ║
║                 │ • Business context                                          ║
║                 │ • User stories                                              ║
║                 │ • HOW or WHY                                                ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

---

## Source Traceability Matrix

| Level | Source Document | Contains | Forbidden |
|-------|-----------------|----------|-----------|
| **Epic** | Research Report + PRD | Business WHY | Tech HOW |
| **Story** | PRD Only | User WHAT | Tech HOW |
| **Task** | Tech Spec Only | Tech HOW | Business WHY, User WHAT |
| **Sub-task** | Story AC + Task boundaries | Verify WHAT | Tech HOW, Business WHY |

---

## Validation Patterns

Use these regex patterns to detect violations during Phase 3:

### Epic Validation

```yaml
epic_validation:
  required_fields:
    - business_goal
    - success_metric
    - stakeholder_impact
  forbidden_patterns:
    - /\bAPI\b/i
    - /\bendpoint\b/i
    - /\bschema\b/i
    - /\bdatabase\b/i
    - /\bcomponent\b/i
    - /\bservice\b/i
    - /\bmodule\b/i
    - /\bimplement(ation)?\b/i
    - /\barchitecture\b/i
    - /\bdesign pattern\b/i
  source_required:
    - research-report
    - prd
```

### Story Validation

```yaml
story_validation:
  required_fields:
    - user_persona
    - user_need
    - user_value
    - acceptance_criteria
  forbidden_patterns:
    - /\bAPI\b/i
    - /\bendpoint\b/i
    - /\bschema\b/i
    - /\bdatabase\b/i
    - /\bZod\b/i
    - /\bReact\b/i
    - /\bPostgreSQL\b/i
    - /\bJWT\b/i
    - /\bcomponent\b/i
    - /\bservice\b/i
    - /\bmodule\b/i
  source_required:
    - prd
```

### Task Validation

```yaml
task_validation:
  required_fields:
    - technical_approach
    - dependencies
    - affected_files
  forbidden_patterns:
    - /\buser wants\b/i
    - /\bbusiness requires\b/i
    - /\bstakeholder\b/i
    - /\bas a user\b/i
    - /\bso that I can\b/i
    - /\bmarket\b/i
    - /\bcompetitor\b/i
    - /\brevenue\b/i
  source_required:
    - tech-spec
```

### Sub-task (QA Gate) Validation

```yaml
subtask_validation:
  required_fields:
    - must_achieve
    - must_not
    - not_included
  forbidden_patterns:
    - /\buse Zod\b/i
    - /\bimplement with\b/i
    - /\barchitecture\b/i
    - /\bbecause user\b/i
    - /\bbusiness goal\b/i
    - /\bdebounce\b/i
    - /\bschema\b/i
    - /\bendpoint\b/i
  source_required:
    - story.acceptance_criteria
    - task.scope
```

---

## Visual Hierarchy

```
┌─────────────────────────────────────────────────────────────────────────┐
│  EPIC: "Improve User Authentication"                                    │
│  ════════════════════════════════════                                   │
│  Source: Research + PRD                                                 │
│  Contains: Business Logic                                               │
│  ─────────────────────────────────────────────────────────────────────  │
│  • Goal: Reduce failed logins by 40%                                    │
│  • Context: Users abandon at login (23% drop-off)                       │
│  • Metric: Login success rate > 85%                                     │
│  • Stakeholders: End users, Support team                                │
│                                                                         │
│  ❌ NO: "Use React Hook Form", "JWT tokens", "PostgreSQL"               │
│                                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│  │                                                                      │
│  └── STORY: "Clear Validation Feedback"                                 │
│      ════════════════════════════════════                               │
│      Source: PRD Only                                                   │
│      Contains: Product Logic                                            │
│      ───────────────────────────────────────────────────────────────    │
│      • As a: User attempting to log in                                  │
│      • I want: Clear feedback when I make mistakes                      │
│      • So that: I can fix errors without confusion                      │
│      • Acceptance: Errors are actionable, users self-correct            │
│                                                                         │
│      ❌ NO: "Zod validation", "API returns 422", "Component X"          │
│                                                                         │
│      ├──────────────────────────────────────────────────────────────────┤
│      │                                                                  │
│      └── TASK: "Implement Email Validation"                             │
│          ════════════════════════════════════                           │
│          Source: Tech Spec Only                                         │
│          Contains: Technical Approach                                   │
│          ─────────────────────────────────────────────────────────────  │
│          • Use Zod schema for email validation                          │
│          • Integrate with React Hook Form                               │
│          • Display FormError component below input                      │
│          • Debounce validation by 300ms                                 │
│          • Error format: { field, message, code }                       │
│                                                                         │
│          ❌ NO: "Because users want...", "Business requires..."         │
│                                                                         │
│          ├──────────────────────────────────────────────────────────────┤
│          │                                                              │
│          └── SUB-TASK (QA Gate): "Acceptance Criteria"                  │
│              ════════════════════════════════════════                   │
│              Source: Derived from Story AC + Task Scope                 │
│              Contains: What to verify                                   │
│              ───────────────────────────────────────────────────────    │
│              ✅ MUST:                                                   │
│              • Email format validated before submit                     │
│              • Error displays below input field                         │
│              • Error clears when corrected                              │
│                                                                         │
│              ❌ MUST NOT:                                               │
│              • Submit with invalid email                                │
│              • Log email to console                                     │
│              • Call API before client validation                        │
│                                                                         │
│              🚫 NOT INCLUDED:                                           │
│              • Password validation (TASK-124)                           │
│              • Remember me (out of scope)                               │
│                                                                         │
│              ❌ NO: "Use Zod", "Debounce 300ms", "User wants..."        │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Enforcement Process

### During Phase 3c (Jira Population)

```
For each item being created:

1. VALIDATE content against iron rules
        │
        ▼
  ┌─────────────┐
  │ Rule Check  │
  └──────┬──────┘
         │
  ┌──────┴──────┐
  ▼             ▼
PASS         VIOLATION
  │             │
  │             ▼
  │      ┌─────────────────────────────────────┐
  │      │ ⛔ BLOCKED                          │
  │      │                                     │
  │      │ Epic contains tech spec content:   │
  │      │ "Use React Hook Form"              │
  │      │                                     │
  │      │ Move to: Task level                │
  │      │ Epic should only have: Business    │
  │      └─────────────────────────────────────┘
  │
  ▼
2. CREATE in Jira (only if validation passes)
```

---

## Why These Rules Matter

### The Problem They Solve

1. **Context Leakage Prevention**
   - QA sub-agent needs isolated context to provide "fresh eyes" review
   - If Epic contains tech details, QA agent gets biased

2. **Clear Responsibility Boundaries**
   - PM owns Epic/Story (business/product)
   - Dev owns Task (technical)
   - QA owns Sub-task (verification)

3. **Traceability**
   - Business decisions trace to Epic
   - User needs trace to Story
   - Technical decisions trace to Task
   - Quality gates trace to Sub-task

4. **Efficient Communication**
   - Each role reads only their relevant level
   - No information overload
   - Clear handoffs between phases

---

## Quick Reference

| If you're writing... | Ask yourself... | If answer is YES, it's WRONG |
|---------------------|-----------------|------------------------------|
| Epic | Does this mention HOW to build? | Move to Task |
| Story | Does this mention specific tech? | Move to Task |
| Task | Does this mention WHY users need it? | Move to Story |
| Sub-task | Does this mention HOW to implement? | Remove it |

---

## Related Files

- Templates: `templates/epic-template.md`, `templates/story-template.md`, `templates/task-template.md`, `templates/subtask-template.md`
- Content Mapping: `content-mapping.md`
- Phase 3 Methodology: `phase3-methodology.md`
