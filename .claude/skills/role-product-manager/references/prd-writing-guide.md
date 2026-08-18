# PRD Writing Guide for Product Managers

## PRD Structure

### Essential Sections

```markdown
# [Feature Name] PRD

## 1. Overview
### Problem Statement
[What problem are we solving? For whom?]

### Success Metrics
| Metric | Current | Target | Measurement |
|--------|---------|--------|-------------|
| [KPI] | [baseline] | [goal] | [how] |

### Scope
**In Scope**: [What's included]
**Out of Scope**: [What's explicitly excluded]

## 2. User Stories

### Epic: [Epic Name]

#### US-001: [Story Title]
**As a** [role]
**I want** [capability]
**So that** [benefit]

**Acceptance Criteria:**
- Given [context], when [action], then [outcome]
- Given [context], when [action], then [outcome]

**Priority**: P1/P2/P3
**Story Points**: [estimate]

## 3. Requirements

### Functional Requirements
| ID | Requirement | Priority | Notes |
|----|-------------|----------|-------|
| FR-001 | [requirement] | Must | [notes] |

### Non-Functional Requirements
| ID | Requirement | Target | Notes |
|----|-------------|--------|-------|
| NFR-001 | Performance | <2s load | [notes] |

## 4. Constraints & Dependencies
- [Constraint 1]
- [Dependency 1]

## 5. Risks
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| [risk] | H/M/L | H/M/L | [plan] |

## 6. Timeline
| Milestone | Target Date |
|-----------|-------------|
| PRD Approved | [date] |
| Dev Complete | [date] |
| Release | [date] |
```

## Writing Tips

### Problem Statements

**Bad:**
> "We need a better dashboard"

**Good:**
> "Regional managers spend 2+ hours daily compiling reports from 5 different systems to understand team performance. This manual process leads to delayed decisions and inconsistent data interpretation."

### User Stories

**Bad:**
> "As a user, I want to click a button so that something happens"

**Good:**
> "As a regional manager, I want to see all team KPIs on one screen so that I can identify underperforming areas within 5 minutes instead of 2 hours"

### Acceptance Criteria

**Bad:**
- The system should work
- It should be fast

**Good:**
- Given I am on the dashboard, when I select a region, then I see only that region's data within 1 second
- Given I am viewing team data, when I click "Export", then a PDF downloads containing all visible metrics
- Given an API error occurs, when loading fails, then I see an error message with a retry button

## Prioritization Framework

### MoSCoW
| Priority | Meaning | Criteria |
|----------|---------|----------|
| Must | Critical | Launch blocker |
| Should | Important | Significant value |
| Could | Desirable | Nice to have |
| Won't | Excluded | Future/never |

### RICE Score
```
RICE = (Reach × Impact × Confidence) / Effort

Reach: Users affected per quarter (number)
Impact: 0.25 (minimal) to 3 (massive)
Confidence: 50% to 100%
Effort: Person-weeks
```

## Common Anti-Patterns

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| Solution-first | Prescribing HOW | Focus on WHAT and WHY |
| Vague metrics | "Improve engagement" | Specific: "+20% DAU" |
| Missing edge cases | Incomplete scenarios | Ask "What if...?" |
| Scope creep | Ever-growing scope | Explicit out-of-scope |
| Assuming context | Others don't know | Write for new reader |

## Stakeholder Communication

### Status Update Template
```markdown
## [Feature] Status Update - [Date]

### Progress
- [x] Completed item
- [ ] In progress item

### Blockers
- [Blocker 1]: [Status/Action needed]

### Decisions Needed
- [Decision 1]: Options A/B/C

### Next Week
- [Planned item 1]
- [Planned item 2]

### Risks
- [Risk]: [Mitigation]
```

### Change Request Template
```markdown
## Change Request: [Title]

### Current State
[What was agreed]

### Proposed Change
[What's changing]

### Reason
[Why this change]

### Impact
- Timeline: [impact]
- Scope: [impact]
- Resources: [impact]

### Recommendation
[Approve/Reject with rationale]
```

## Checklist Before Handoff

- [ ] Problem validated with users
- [ ] Success metrics defined and measurable
- [ ] All user stories have acceptance criteria
- [ ] Scope clearly defined (in AND out)
- [ ] Dependencies identified
- [ ] Risks documented with mitigations
- [ ] Stakeholders reviewed and approved
- [ ] Edge cases considered
- [ ] Non-functional requirements specified
