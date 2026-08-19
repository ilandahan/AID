---
name: aid-prd
description: AID Phase 1 - Research & PRD creation. Use this skill when creating PRDs, writing user stories, defining acceptance criteria, scoping features, or transitioning from discovery to technical specification. Ensures clear, testable requirements before development begins.
---

# PRD Phase Skill

## Phase Overview

**Purpose**: Define what will be built with enough clarity that development can proceed without ambiguity. Translate validated problems into actionable requirements.

**Entry Criteria**:
- Discovery phase completed and approved
- Problem statement validated
- Stakeholders identified
- Success metrics defined
- **Traceability matrix from Pre-PRD Research available**
- **All research findings have assigned IDs**

**Exit Criteria**:
- PRD document complete and approved
- All user stories have acceptance criteria
- Scope is explicitly defined (in and out)
- Dependencies identified
- **Every requirement linked to research finding(s) OR flagged as assumption**
- **Traceability matrix updated with PRD links**

## Deliverables

### 1. PRD Document
- **Description**: Comprehensive requirements document
- **Format**: Structured document with sections for context, requirements, scope
- **Quality bar**: Readable by both technical and non-technical stakeholders

### 2. User Stories
- **Description**: Requirements from user perspective
- **Format**: "As a [role], I want [capability] so that [benefit]"
- **Quality bar**: Each story is independent, testable, and valuable

### 3. Acceptance Criteria (Gherkin - REQUIRED)
- **Description**: Executable specifications for each user story
- **Format**: **Gherkin feature files (REQUIRED)** - Given-When-Then syntax
- **Location**: `features/[feature-area]/[story-slug].feature`
- **Quality bar**: Unambiguous, executable, tagged properly

> **WHY Gherkin is required:** Acceptance criteria become tests. Gherkin ensures requirements are executable from day one, eliminating the PRD-to-QA translation gap.

### 4. Feature Files
- **Description**: Gherkin feature files saved to repository
- **Format**: `.feature` files in `features/` directory
- **Quality bar**: Passes `npm run cucumber:dry` validation

### 5. Scope Definition
- **Description**: What's included and explicitly excluded
- **Format**: In-scope / Out-of-scope lists
- **Quality bar**: No ambiguous boundaries

### 6. Requirements Traceability
- **Description**: Linkage between research findings and PRD requirements
- **Format**: Updated traceability matrix with bidirectional links
- **Quality bar**: Every requirement has research backing OR explicit assumption flag

## Role-Specific Guidance

### For Product Managers
- Own the PRD document
- Write user stories from user perspective
- Ensure acceptance criteria are testable
- Guard against scope creep
- **Maintain traceability links to research**
- **Document and track assumptions**
- **Ensure no research findings are "lost"**

### For Developers
- Review for technical feasibility
- Identify missing edge cases
- Flag unclear requirements
- Estimate complexity per story
- **Verify requirements make sense given research context**

### For QA Engineers
- Review acceptance criteria for testability
- Identify test scenarios
- Flag missing error cases
- Plan test data needs
- **Use research findings to inform test scenarios**

### For Tech Leads
- Validate architectural fit
- Identify cross-cutting concerns
- Flag non-functional requirements
- Review for consistency with standards
- **Challenge assumptions without research backing**

## Common Pitfalls

| Pitfall | Problem | Fix |
|---------|---------|-----|
| Implementation in requirements | Mixing "what" with "how" | Keep requirements focused on outcomes |
| Untestable criteria | "Should be fast" | "Should load in <2 seconds" |
| Missing error cases | Only happy path defined | Define what happens when things go wrong |
| Scope creep | New requirements sneak in | Explicit acknowledgment for any additions |
| Hidden assumptions | Unstated expectations | Make all assumptions explicit |
| **Orphan requirements** | Requirements without research backing | Link to research ID or flag as assumption |
| **Lost research** | Research findings not becoming requirements | Review traceability matrix for unused findings |
| **Broken trace links** | IDs don't match between docs | Validate IDs exist in research report |

## Phase Gate Checklist

Before requesting approval to proceed:

### Document Quality
- [ ] PRD document is complete
- [ ] All user stories follow proper format
- [ ] Scope is explicitly defined (in AND out)
- [ ] Dependencies are identified
- [ ] Stakeholders have reviewed and approved
- [ ] Success metrics from Discovery are preserved
- [ ] **Every requirement has research ID(s) OR assumption flag**
- [ ] **Traceability matrix is updated**
- [ ] **No orphan research findings (all reviewed)**

### Acceptance Criteria (Gherkin) ⭐ REQUIRED
- [ ] Every user story has acceptance criteria in **Gherkin format**
- [ ] Feature files saved to `features/` directory
- [ ] Each story has at least 2 scenarios: happy path + error case
- [ ] All scenarios have appropriate @tags (@critical, @smoke, etc.)
- [ ] Research backing noted as comment in feature files
- [ ] `npm run cucumber:dry` passes (validates Gherkin syntax)

### Validation Commands
```bash
npm run cucumber:dry   # Must pass before advancing to Phase 2
```

## Transition to Tech Spec Phase

Hand off:
- Approved PRD document
- Prioritized user stories
- Complete acceptance criteria
- Identified dependencies
- Non-functional requirements
- **Updated traceability matrix**
- **Assumptions log with validation plans**

## Traceability Workflow

### When Writing Requirements

```
┌─────────────────────────────────────────────────────────────────┐
│              REQUIREMENT TRACEABILITY DECISION                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  New Requirement Identified                                     │
│           │                                                     │
│           ▼                                                     │
│  ┌─────────────────┐                                           │
│  │ Does research   │──── YES ───▶ Add Research ID(s)           │
│  │ finding exist?  │              to requirement               │
│  └─────────────────┘                                           │
│           │                                                     │
│          NO                                                     │
│           │                                                     │
│           ▼                                                     │
│  ┌─────────────────┐                                           │
│  │ Is this critical│──── NO ────▶ Consider deferring           │
│  │ for MVP?        │              to future phase              │
│  └─────────────────┘                                           │
│           │                                                     │
│          YES                                                    │
│           │                                                     │
│           ▼                                                     │
│  ┌─────────────────────────────────────────┐                   │
│  │ Add to Assumptions Log:                  │                   │
│  │ - Document the assumption                │                   │
│  │ - Assess risk if wrong                   │                   │
│  │ - Define validation plan                 │                   │
│  │ - Flag with ASSUMPTION                   │                   │
│  └─────────────────────────────────────────┘                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Traceability Validation Checklist

Before PRD approval, validate:

- [ ] **Forward Trace**: Every research finding marked INCLUDE has a linked requirement
- [ ] **Backward Trace**: Every requirement has research backing OR assumption flag
- [ ] **No Broken Links**: All referenced research IDs exist in research report
- [ ] **Assumption Risk**: All assumptions have documented risk and validation plan
- [ ] **Coverage Report**: Traceability summary section is complete

## PRD Template

```markdown
# [Feature Name] PRD

**Project ID**: [PROJECT]
**Research Report**: [Link to docs/research/YYYY-MM-DD-[project-name]/research-report.md]
**Traceability Matrix**: [Link to docs/research/YYYY-MM-DD-[project-name]/traceability-matrix.md]

## 1. Overview

### Problem Statement
[What problem are we solving?]

**Research Backing**: [PROJECT]-A-INT-XXX, [PROJECT]-A-JTBD-XXX
<!-- List the research IDs that validate this problem -->

### Goals
[What does success look like?]

**Research Backing**: [PROJECT]-C-OPP-XXX

### Non-Goals
[What are we explicitly NOT doing?]

**Research Backing**: [PROJECT]-C-OPP-XXX (excluded items)

## 2. User Stories

### US-001: [Title]
**Research Backing**: [PROJECT]-A-INT-XXX, [PROJECT]-B-IDEA-XXX
<!-- If no research backing, mark as: ASSUMPTION - [rationale] -->

**As a** [role]
**I want** [capability]
**So that** [benefit]

**Priority:** [Must Have | Should Have | Could Have | Won't Have]
**Complexity:** [XS | S | M | L | XL]

**Acceptance Criteria (Gherkin):** See `features/[feature-area]/us-001-[slug].feature`

### US-002: [Title]
**Research Backing**: [IDs] OR ASSUMPTION - [rationale]

**As a** [role]
**I want** [capability]
**So that** [benefit]

**Priority:** [Must Have | Should Have | Could Have | Won't Have]
**Complexity:** [XS | S | M | L | XL]

**Acceptance Criteria (Gherkin):** See `features/[feature-area]/us-002-[slug].feature`

---
<!--
IMPORTANT: All acceptance criteria must be written as Gherkin feature files.
Example feature file format:

```gherkin
# Research: [PROJECT]-A-INT-XXX
# PRD: US-001
@feature-tag @critical
Feature: [Story Title]
  """
  WHY: [Copy the "So that" benefit here]
  """

  As a [role]
  I want [capability]
  So that [benefit]

  @smoke @happy-path
  Scenario: [Happy path - main success]
    Given [precondition/context]
    When [user action]
    Then [expected outcome]

  @error-handling
  Scenario: [Error case]
    Given [precondition]
    When [invalid action]
    Then [error handling shown]
```
-->

## 3. Scope

### In Scope
| Item | Research Backing |
|------|------------------|
| [Feature/capability 1] | [PROJECT]-XXX |
| [Feature/capability 2] | [PROJECT]-XXX |

### Out of Scope
| Item | Research Backing | Rationale |
|------|------------------|-----------|
| [Excluded item 1] | [PROJECT]-XXX | [Why excluded] |
| [Excluded item 2] | N/A - stakeholder request | [Why excluded] |

## 4. Dependencies
- [Dependency 1]
- [Dependency 2]

## 5. Success Metrics
| Metric | Target | Research Backing |
|--------|--------|------------------|
| [Metric 1] | [Target] | [PROJECT]-A-XXX |
| [Metric 2] | [Target] | [PROJECT]-C-OPP-XXX |

## 6. Assumptions Log
<!-- Requirements without research backing must be logged here -->

| ID | Assumption | Risk if Wrong | Validation Plan |
|----|------------|---------------|-----------------|
| ASSUME-001 | [Assumption] | [Impact] | [How to validate] |

## 7. Open Questions
- [Question 1]
- [Question 2]

## 8. Traceability Summary

### Research -> Requirements Coverage
| Research Type | Total Findings | Used in PRD | Deferred | Excluded |
|---------------|----------------|-------------|----------|----------|
| Interviews (A-INT) | | | | |
| Competitive (A-COMP) | | | | |
| JTBD (A-JTBD) | | | | |
| Ideas (B-IDEA) | | | | |
| Root Causes (B-ROOT) | | | | |
| Opportunities (C-OPP) | | | | |

### Requirements -> Research Coverage
| Requirement Type | Total | With Research Backing | Assumptions |
|------------------|-------|----------------------|-------------|
| User Stories | | | |
| Acceptance Criteria | | | |
| Success Metrics | | | |
```

## Output Location

Save PRD to: `docs/prd/YYYY-MM-DD-[feature-name].md`

---

## Learning Mode Integration

### Decision Transparency Triggers
- **Scope decisions**: Show reasoning when features are in/out of scope
- **Prioritization**: Explain why certain stories are higher priority
- **Acceptance criteria choices**: Show why specific criteria were selected
- **Traceability decisions**: Explain research-to-requirement mappings

### Debate Invitations
- **Feature scope**: When feature boundaries are ambiguous
- **Story granularity**: When stories could be combined or split
- **Acceptance criteria stringency**: When criteria could be more/less strict
- **Assumption risk**: When assumptions have unclear impact

### Feedback Requests
- After user stories draft: Validate completeness and format
- After acceptance criteria: Confirm testability
- After traceability mapping: Verify research coverage
- At phase gate: Overall PRD quality rating (1-5)

### Example Feedback Request
```markdown
<feedback-request>
**Context:** PRD draft completed for User Authentication feature

**Seeking Feedback On:**
1. Completeness of user stories - did I capture all scenarios?
2. Clarity of acceptance criteria - are they testable?
3. Scope boundaries - is OAuth correctly deferred?
4. Traceability - are research findings properly linked?

**Questions:**
- Should "Remember me" be Phase 1 or Phase 2?
- Are there compliance requirements (SOC2, GDPR) I should address?
- Any research findings I missed linking?

**Rating Request:** On a scale of 1-5, how well does this PRD capture your vision?

**Improvement Ideas Welcome:** What would make this PRD better?
</feedback-request>
```

### Example Debate Invitation
```markdown
<debate-invitation>
**Topic:** Password requirements stringency

**Option A: Standard Requirements**
- Pros: Familiar to users, lower friction
- Cons: May not meet enterprise security needs
- Research Support: [PROJECT]-A-INT-003 (users prefer simplicity)

**Option B: Enterprise-Grade Requirements**
- Pros: Higher security, compliance-ready
- Cons: Higher user friction, more support tickets
- Research Support: [PROJECT]-A-COMP-001 (competitors use strict requirements)

**My Lean:** Option A for MVP, with Option B as Phase 2 enhancement

**Your Input Needed:** What's the target user segment? Enterprise or consumer?
</debate-invitation>
```

---

## Gherkin Best Practices for PRD

### Choosing the Right Tags

```
Is this scenario required for release?
├── YES → @critical
└── NO → Is it a quick sanity check?
    ├── YES → @smoke
    └── NO → Is it a complex edge case?
        ├── YES → @regression
        └── NO → Use feature-specific tag (@auth, @checkout)
```

### Tag Standards

| Tag | When to Use | CI Behavior |
|-----|-------------|-------------|
| `@critical` | Must pass for release | Blocks deployment |
| `@smoke` | Quick sanity checks | Runs on every PR |
| `@regression` | Full test suite | Runs nightly |
| `@wip` | Work in progress | Excluded from CI |
| `@skip` | Temporarily disabled | Excluded (document reason!) |
| `@security` | Security-related tests | Runs on security review |

### Common Gherkin Mistakes in PRD

| Mistake | Example | Fix |
|---------|---------|-----|
| UI details in Gherkin | "When I click the blue button at position 100,200" | "When I submit the form" |
| Implementation language | "When the API returns 200 OK" | "When the request succeeds" |
| Vague outcomes | "Then it should work" | "Then I should see order confirmation #12345" |
| Missing error cases | Only happy path scenarios | Add @error-handling scenarios |
| No tags | Scenarios without @ tags | Add @critical, @smoke, or feature tags |
| Hard-coded test data | "Given user john@example.com exists" | "Given I have a registered user account" |

### Data Table Example (for complex inputs)

```gherkin
Scenario: Bulk user import with various roles
  Given I am an admin
  When I import users with the following data:
    | email                | role    | department |
    | alice@example.com    | admin   | IT         |
    | bob@example.com      | user    | Sales      |
    | carol@example.com    | viewer  | Marketing  |
  Then all users should be created successfully
  And each user should receive a welcome email
```

### Scenario Outline for Parameterized Tests

```gherkin
@security
Scenario Outline: Password validation rules
  When I try to set password "<password>"
  Then validation should "<result>"
  And message should be "<message>"

  Examples:
    | password     | result | message                    |
    | short        | fail   | Password too short         |
    | NoNumbers!   | fail   | Must contain a number      |
    | Valid123!    | pass   | Password accepted          |
    | no-uppercase | fail   | Must contain uppercase     |
```

### Related Skills

- `cucumber-bdd` - Full Gherkin syntax reference and step definition patterns
- `test-driven` - How Cucumber fits in the test pyramid
- `aid-qa-ship` - Cucumber verification in Phase 5
