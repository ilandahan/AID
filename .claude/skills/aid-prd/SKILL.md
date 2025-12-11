---
name: aid-prd
description: AID Phase 1 - Product Requirements Document creation. Use this skill when creating PRDs, writing user stories, defining acceptance criteria, scoping features, or transitioning from discovery to technical specification. Ensures clear, testable requirements before development begins.
---

# PRD Phase Skill

## Phase Overview

**Purpose**: Define what will be built with enough clarity that development can proceed without ambiguity. Translate validated problems into actionable requirements.

**Entry Criteria**:
- Discovery phase completed and approved
- Problem statement validated
- Stakeholders identified
- Success metrics defined

**Exit Criteria**:
- PRD document complete and approved
- All user stories have acceptance criteria
- Scope is explicitly defined (in and out)
- Dependencies identified

## Deliverables

### 1. PRD Document
- **Description**: Comprehensive requirements document
- **Format**: Structured document with sections for context, requirements, scope
- **Quality bar**: Readable by both technical and non-technical stakeholders

### 2. User Stories
- **Description**: Requirements from user perspective
- **Format**: "As a [role], I want [capability] so that [benefit]"
- **Quality bar**: Each story is independent, testable, and valuable

### 3. Acceptance Criteria
- **Description**: Specific conditions for each requirement
- **Format**: Given-When-Then or checklist format
- **Quality bar**: Unambiguous, testable, complete

### 4. Scope Definition
- **Description**: What's included and explicitly excluded
- **Format**: In-scope / Out-of-scope lists
- **Quality bar**: No ambiguous boundaries

## Role-Specific Guidance

### For Product Managers
- Own the PRD document
- Write user stories from user perspective
- Ensure acceptance criteria are testable
- Guard against scope creep

### For Developers
- Review for technical feasibility
- Identify missing edge cases
- Flag unclear requirements
- Estimate complexity per story

### For QA Engineers
- Review acceptance criteria for testability
- Identify test scenarios
- Flag missing error cases
- Plan test data needs

### For Tech Leads
- Validate architectural fit
- Identify cross-cutting concerns
- Flag non-functional requirements
- Review for consistency with standards

## Common Pitfalls

| Pitfall | Problem | Fix |
|---------|---------|-----|
| Implementation in requirements | Mixing "what" with "how" | Keep requirements focused on outcomes |
| Untestable criteria | "Should be fast" | "Should load in <2 seconds" |
| Missing error cases | Only happy path defined | Define what happens when things go wrong |
| Scope creep | New requirements sneak in | Explicit acknowledgment for any additions |
| Hidden assumptions | Unstated expectations | Make all assumptions explicit |

## Phase Gate Checklist

Before requesting approval to proceed:

- [ ] PRD document is complete
- [ ] All user stories follow proper format
- [ ] Every story has testable acceptance criteria
- [ ] Scope is explicitly defined (in AND out)
- [ ] Dependencies are identified
- [ ] Stakeholders have reviewed and approved
- [ ] Success metrics from Discovery are preserved

## Transition to Tech Spec Phase

Hand off:
- Approved PRD document
- Prioritized user stories
- Complete acceptance criteria
- Identified dependencies
- Non-functional requirements

## PRD Template

```markdown
# [Feature Name] PRD

## 1. Overview
### Problem Statement
[What problem are we solving?]

### Goals
[What does success look like?]

### Non-Goals
[What are we explicitly NOT doing?]

## 2. User Stories

### Story 1: [Title]
**As a** [role]
**I want** [capability]
**So that** [benefit]

**Acceptance Criteria:**
- [ ] Given [context], when [action], then [outcome]
- [ ] Given [context], when [action], then [outcome]

## 3. Scope

### In Scope
- [Feature/capability 1]
- [Feature/capability 2]

### Out of Scope
- [Explicitly excluded item 1]
- [Explicitly excluded item 2]

## 4. Dependencies
- [Dependency 1]
- [Dependency 2]

## 5. Success Metrics
- [Metric 1]: [Target]
- [Metric 2]: [Target]

## 6. Open Questions
- [Question 1]
- [Question 2]
```

## Output Location

Save PRD to: `docs/prd/YYYY-MM-DD-[feature-name].md`
