# Story Template

## Story Hierarchy

```
EPIC-{N}: {Domain}
└── Story {N}.{S}: {Capability Name}
    ├── Task {N}.{S}.1: {Implementation}
    ├── Task {N}.{S}.2: {Implementation}
    └── Task {N}.{S}.3: {Implementation}
```

**Critical Rule**: Stories are the BRIDGE between business (PRD) and technical (Tasks).

---

## Story Description Template

### Title Format
```
Story {N}.{S}: {Capability/Feature Name}
```

**Examples:**
- Story 2.1: User Registration
- Story 2.2: User Login
- Story 2.3: Session Management
- Story 8.1: Project Setup
- Story 8.4: Session Flow

---

### Description Format (Jira-Ready)

```markdown
## User Story
As a {role/persona from PRD},
I want {action/capability},
So that {benefit/value}.

## Context
{Brief explanation of why this story exists and how it fits the bigger picture}

## Acceptance Criteria (Gherkin Format)

### AC-1: {Scenario Name}
```gherkin
Given {precondition/context}
When {action taken}
Then {expected outcome}
And {additional outcome}
```

### AC-2: {Scenario Name}
```gherkin
Given {precondition/context}
When {action taken}
Then {expected outcome}
```

### AC-3: {Edge Case / Error Scenario}
```gherkin
Given {error condition}
When {action taken}
Then {error handling outcome}
```

## Design References
- Figma: {Link to designs if available}
- Wireframe: {Link or description}
- UI Components: {List of components needed}

## API Endpoints (from Tech Spec)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/v1/... | {What it does} |
| GET | /api/v1/... | {What it does} |

## Data Requirements
- Input: {What data is needed}
- Output: {What data is produced}
- Validation: {Key validation rules}

## Non-Functional Requirements
- Performance: {Response time, throughput}
- Security: {Auth, encryption, validation}
- Accessibility: {WCAG level if applicable}

## Out of Scope
{Explicitly list what this story does NOT include to prevent scope creep}
- {Item 1}
- {Item 2}

## Definition of Done
- [ ] All acceptance criteria pass
- [ ] Unit tests written (80%+ coverage)
- [ ] Integration tests pass
- [ ] Code reviewed and approved
- [ ] Deployed to staging
- [ ] QA verified
- [ ] Documentation updated

## PRD Traceability
- User Story ID: {US-XX from PRD}
- Requirement Section: {PRD section reference}

## Tasks
{List of implementation tasks}
1. Task {N}.{S}.1: {Name}
2. Task {N}.{S}.2: {Name}
3. Task {N}.{S}.3: {Name}

## Story Points
{Fibonacci: 1, 2, 3, 5, 8, 13, 21}
**Estimate**: {X} points

## Priority
{MoSCoW or numeric}
- Must Have / Should Have / Could Have / Won't Have
- P0 (Critical) / P1 (High) / P2 (Medium) / P3 (Low)
```

---

## Content Mapping Rules

### What Goes in Story (FROM PRD)

| PRD Element | Story Field |
|-------------|-------------|
| User Story | User Story section |
| Acceptance Criteria | AC in Gherkin |
| UI Requirements | Design References |
| Success Metrics | Definition of Done |
| Persona | Role in User Story |

### What Goes in Story (FROM TECH SPEC)

| Tech Spec Element | Story Field |
|-------------------|-------------|
| API Endpoints | API Endpoints table |
| Request/Response | Data Requirements |
| Validation Rules | Non-Functional Requirements |
| Security Requirements | Non-Functional Requirements |

---

## Story Sizing Guide

| Points | Complexity | Duration | Example |
|--------|------------|----------|---------|
| 1 | Trivial | < 2 hours | Config change, copy update |
| 2 | Simple | 2-4 hours | Single component, minor feature |
| 3 | Small | 4-8 hours | Feature with 2-3 tasks |
| 5 | Medium | 1-2 days | Feature with API + UI |
| 8 | Large | 2-3 days | Complex feature, multiple integrations |
| 13 | Very Large | 3-5 days | Consider splitting |
| 21 | Epic-sized | > 5 days | MUST split into smaller stories |

---

## Story Grouping Principles

### Group by User Capability, Not Technical Layer

**Good Grouping:**
```
Story: User Registration
├── Task: Create signup API endpoint
├── Task: Create signup form component
├── Task: Add email validation
└── Task: Write registration tests
```

**Bad Grouping:**
```
Story: Backend APIs        ← Too broad, spans multiple features
Story: Frontend Forms      ← Too broad, spans multiple features
Story: Database Setup      ← Technical layer, not user capability
```

### Story Independence (INVEST Criteria)

| Criterion | Meaning | Test |
|-----------|---------|------|
| **I**ndependent | Can be built without other stories | No blocking dependencies within sprint |
| **N**egotiable | Details can be discussed | Not over-specified |
| **V**aluable | Delivers user value | Answers "so what?" |
| **E**stimable | Can be sized | Team understands scope |
| **S**mall | Fits in a sprint | Typically 1-5 days |
| **T**estable | Has clear acceptance criteria | Can write tests before code |

---

## Anti-Patterns to Avoid

| Anti-Pattern | Problem | Solution |
|--------------|---------|----------|
| Technical stories | "Set up database" | Attach to user-facing story |
| Orphan stories | No parent epic | Every story belongs to an epic |
| Vague AC | "Works correctly" | Use Gherkin Given/When/Then |
| No edge cases | Only happy path | Include error scenarios |
| Missing DoD | Unclear completion | Always include Definition of Done |
| Story = Task | Too granular | Story = user capability, not code change |
