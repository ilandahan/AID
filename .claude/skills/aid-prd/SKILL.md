---
name: aid-prd
description: AID Phase 1 - PRD creation. Use for user stories, acceptance criteria, scoping features, transitioning from discovery to tech spec.
---

# PRD Phase Skill

## Phase Overview

Purpose: Define what will be built with clarity for unambiguous development.

Entry: Discovery complete, problem validated, stakeholders identified
Exit: PRD complete, user stories with acceptance criteria, scope defined

## Deliverables

1. PRD Document - Readable by technical and non-technical
2. User Stories - "As a [role], I want [capability] so that [benefit]"
3. Acceptance Criteria - Given-When-Then, unambiguous, testable
4. Scope Definition - In-scope and out-of-scope explicit
5. Traceability - Every requirement links to research or flagged as assumption

## User Story Format

```markdown
### US-001: [Title]
**Research Backing**: [PROJECT]-A-INT-XXX OR ASSUMPTION - [rationale]

**As a** [role]
**I want** [capability]
**So that** [benefit]

**Acceptance Criteria:**
- [ ] Given [context], when [action], then [outcome]
```

## Common Pitfalls

| Pitfall | Fix |
|---------|-----|
| Implementation in requirements | Keep focused on outcomes |
| Untestable criteria | "Should load in <2s" not "be fast" |
| Missing error cases | Define what happens when things fail |
| Scope creep | Explicit acknowledgment for additions |
| Orphan requirements | Link to research or flag assumption |

## Phase Gate Checklist

- [ ] PRD document complete
- [ ] User stories proper format
- [ ] Every story has testable acceptance criteria
- [ ] Scope explicitly defined (in AND out)
- [ ] Dependencies identified
- [ ] Every requirement has research ID OR assumption flag
- [ ] Traceability matrix updated

## PRD Template

```markdown
# [Feature] PRD

## 1. Overview
### Problem Statement
[Problem] **Research**: [ID]

### Goals
[Goals] **Research**: [ID]

### Non-Goals
[Excluded items]

## 2. User Stories
[Stories with research backing]

## 3. Scope
### In Scope
| Item | Research Backing |
|------|------------------|

### Out of Scope
| Item | Rationale |
|------|-----------|

## 4. Dependencies
## 5. Success Metrics
## 6. Assumptions Log
| ID | Assumption | Risk | Validation Plan |
## 7. Open Questions
```

## Role Guidance

| Role | Focus |
|------|-------|
| PM | Own PRD, user stories, acceptance criteria |
| Dev | Review feasibility, identify edge cases |
| QA | Review testability, identify scenarios |
| Tech Lead | Validate fit, flag non-functionals |

## Handoff to Tech Spec

- Approved PRD
- Prioritized user stories
- Complete acceptance criteria
- Dependencies identified
- Traceability matrix

Save to: `docs/prd/YYYY-MM-DD-[feature].md`
