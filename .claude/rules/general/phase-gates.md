# Phase Gate Enforcement Rules

Claude MUST enforce phase gates. Work that belongs to a later phase is BLOCKED.

---

## 6-Phase Lifecycle

```
Phase 0 ──► Phase 1 ──► Phase 2 ──► Phase 3 ──► Phase 4 ──► Phase 5
Discovery     PRD      Tech Spec   Impl Plan     Dev       QA & Ship
```

---

## Phase Permissions

| Phase | Allowed | Blocked |
|-------|---------|---------|
| 0 Discovery | Research, stakeholders, competitive analysis | PRD, architecture, code |
| 1 PRD | + Requirements, scope, user stories | Architecture, code, Jira |
| 2 Tech Spec | + Architecture, schemas, APIs | Code, Jira issues |
| 3a Consolidation | + Contradiction resolution, consolidate specs | Jira issues, code |
| 3b Breakdown | + Task decomposition, sprint planning | Jira creation, code |
| 3c Jira Population | + Jira epics, stories, tasks with full info | Production code |
| 4 Development | + Code, tests, components | Deployment |
| 5 QA & Ship | Everything | - |

---

## Phase-Specific WHY Questions

| Phase | Core WHY Question |
|-------|-------------------|
| 0 Discovery | "WHY is this problem worth solving?" |
| 1 PRD | "WHY does the user need this?" |
| 2 Tech Spec | "WHY this architecture?" |
| 3a Consolidation | "WHY does this contradiction exist? WHY this resolution?" |
| 3b Breakdown | "WHY this task size? WHY these dependencies?" |
| 3c Jira Population | "WHY is this information complete? WHY can dev work from this alone?" |
| 4 Development | "WHY this code? WHY these connections?" |
| 5 QA & Ship | "WHY is this test? WHY is this ready?" |

---

## State Management

Claude MUST:
1. Read `.aid/state.json` to determine current phase
2. Read `.aid/context.json` to understand current task/step
3. Verify requested work is allowed in current phase
4. **REFUSE work that belongs to a later phase**

---

## Gate Transition Requirements

Before advancing to the next phase:

1. All deliverables for current phase complete
2. Quality check passed (7.0+ score)
3. Human approval obtained (`/phase-approve`)
4. No blocking issues or open questions

---

## Phase Violation Response

When user requests work for a later phase:

```
⚠️ Phase Gate Violation

Current Phase: [X] - [Name]
Requested Work: [Description]
Required Phase: [Y] - [Name]

This work is blocked until Phase [Y].

To proceed:
1. Complete Phase [X] deliverables
2. Get approval with /phase-approve
3. Advance with /phase-advance
```
