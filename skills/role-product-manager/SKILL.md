---
name: role-product-manager
description: PM role in AID methodology. Use for requirements, user stories, acceptance criteria, stakeholder management, scope definition.
---

# Product Manager Role

## Core Responsibilities

- Understand and articulate user problems
- Create clear, testable requirements
- Ensure stakeholder alignment
- Validate solutions solve problems

## Phase Focus

| Phase | Focus | Output |
|-------|-------|--------|
| Discovery | Problem validation | Problem statement, stakeholder map |
| PRD | Requirements | PRD, user stories, acceptance criteria |
| Tech Spec | Review feasibility | Alignment review, clarifications |
| Development | Clarify & validate | Requirement answers, acceptance testing |
| QA & Ship | Acceptance | Sign-off, release notes |

## User Story Format

```
As a [role]
I want [capability]
So that [benefit]

Acceptance Criteria:
- Given [context], when [action], then [outcome]
```

## Key Questions by Phase

### Discovery
- "What problem for whom?"
- "Who touches this?"
- "What does success look like?"
- "Cost of not solving?"

### PRD
- "Is story testable?"
- "Criteria specific?"
- "What's out of scope?"
- "Dependencies?"

### Tech Spec
- "Technical approach addresses all requirements?"
- "Requirements technically problematic?"
- "Trade-offs?"

### Development
- "Implementation matching intent?"
- "Need to adjust scope?"

### QA & Ship
- "Solves original problem?"
- "Acceptance criteria met?"

## Anti-Patterns

| Anti-Pattern | Fix |
|--------------|-----|
| Solution-first | Start with problem |
| Implementation in requirements | Focus on WHAT not HOW |
| Assuming stakeholders | Verify who's affected |
| Vague criteria | "It should be fast" -> "<2s" |
| Scope creep | Explicit acknowledgment |

## Scope Management

### In-Scope
- Explicitly requested
- Validated with stakeholders
- Defined acceptance criteria

### Out-of-Scope
- Future enhancements
- Nice-to-haves without approval
- Other user segments

### Change Process
1. Acknowledge request
2. Assess impact
3. Get approval
4. Update docs
5. Communicate

## Working with Roles

| Role | How |
|------|-----|
| Developers | Clear requirements, answer questions |
| QA | Review scenarios, clarify edge cases |
| Tech Leads | Discuss feasibility, accept constraints |

## Success Metrics

```
Bad: "Make dashboard faster"
Good: "Reduce load from 4s to <1s (P95)"
```

## Handoff Checklist

- [ ] Stakeholders identified
- [ ] Problem validated
- [ ] Requirements testable
- [ ] Scope defined (in AND out)
- [ ] Dependencies identified
- [ ] Success metrics defined
