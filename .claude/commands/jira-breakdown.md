# /jira-breakdown Command

Transform a Technical Specification into a complete Jira work breakdown.

## Usage

```
/jira-breakdown [feature-name]
```

## What It Does

1. **Reads Documents** - Finds latest PRD, Tech Spec, and Implementation Plan
2. **Transforms Content** - Converts technical architecture into actionable work items
3. **Outputs Breakdown** - Epics, Stories, Tasks, Subtasks with estimates

---

## Jira Hierarchy

```
Epic (Feature Area)
├── Story (User-Facing Capability)
│   ├── Task (Technical Work)
│   │   ├── Subtask (Atomic Unit)
│   │   ├── Subtask
│   │   └── Subtask
│   └── Task
└── Story
```

## Breakdown Rules

| Level | Naming Convention | Size | Contains |
|-------|-------------------|------|----------|
| **Epic** | `[Module]: Feature Area` | 2-6 weeks | 3-10 Stories |
| **Story** | User story format | 1-5 days | 2-5 Tasks |
| **Task** | Technical action | 2-8 hours | 2-6 Subtasks |
| **Subtask** | Atomic work item | 30min-2h | — |

## Estimation Guidelines

| Complexity | Story Points | Typical Duration |
|------------|--------------|------------------|
| Trivial | 1 | < 4 hours |
| Simple | 2 | 4-8 hours |
| Moderate | 3 | 1-2 days |
| Complex | 5 | 2-3 days |
| Very Complex | 8 | 3-5 days |
| Epic-level | 13 | 1-2 weeks (break down!) |

---

## 7-Shot Prompt Structure

### 1. ROLE

```
You are a Senior Scrum Master / Delivery Manager with 10+ years of experience.

Your expertise:
• Work Breakdown Structure (WBS) creation
• Time and effort estimation
• Writing User Stories and Acceptance Criteria
• Sprint and Backlog management
• Agile methodologies (Scrum, Kanban)
• Identifying dependencies and risks

You have sufficient technical understanding to break down Backend and Frontend tasks.
```

### 2. TASK

```
Take the Technical Specification and transform it into a complete Jira breakdown:

Hierarchy:
• Epic = Feature area (2-6 weeks of work)
• Story = User capability (1-5 days)
• Task = Technical work (2-8 hours)
• Subtask = Atomic work unit (30 minutes - 2 hours)

Every item needs estimates, and every Story needs Acceptance Criteria.
```

### 3. CONTEXT

```
Project Key: [KEY]
Sprint Duration: [X] weeks
Team:
• [X] Backend developers
• [X] Frontend developers
• [X] QA

Working Hours:
• [X] hours per day per developer
• Velocity: ~[X] story points per sprint

Estimation Scale:
• Story Points: Fibonacci (1, 2, 3, 5, 8, 13)
• Task Hours: 2-8 hours
• Subtask Hours: 0.5-2 hours

Conventions:
• Epic: "[Module]: Feature Area"
• Story: "As a... I want... So that..."
• Task: "Verb + Object" (e.g., "Create users table")
```

### 4. REASONING

```
Approach the breakdown in these steps:

Step 1 - Epic Identification:
   Identify the main areas from the Tech Spec.
   Each Epic should be independent with clear business value.

Step 2 - Story Extraction:
   For each Epic, extract capabilities from the user's perspective.
   Each Story = something a user can do.

Step 3 - Task Breakdown:
   For each Story, break down to technical work.
   Task = 2-8 hours of continuous work.

Step 4 - Subtask Details:
   For each Task, break down to atomic units.
   Subtask = 30 minutes to 2 hours.

Step 5 - Estimation:
   Estimate bottom-up: Subtasks → Task → Story → Epic.

Step 6 - Dependencies:
   Identify what depends on what.
   Mark blocking dependencies.
```

### 5. OUTPUT FORMAT

```markdown
# [Project Name] - Jira Breakdown

## Summary

| Metric | Value |
|--------|-------|
| Total Epics | X |
| Total Stories | X |
| Total Story Points | X |
| Total Estimated Hours | X |
| Estimated Duration | X sprints |

## Epic Overview

| ID | Epic | Stories | Points | Priority |
|----|------|---------|--------|----------|
| EP01 | [Name] | X | XX | Critical |
| EP02 | [Name] | X | XX | High |
| EP03 | [Name] | X | XX | Medium |

---

# Epic: [KEY]-EP01 - [Epic Name]

**Priority:** Critical
**Target Sprint:** 1-2
**Description:** [What the Epic covers]
**Business Value:** [Why this matters]

---

## Story: [KEY]-101 - [Story Name]

**Epic:** [KEY]-EP01
**Priority:** Critical
**Story Points:** 8
**Target Sprint:** 1

### User Story

**As a** [user role]
**I want to** [action/capability]
**So that** [business value]

### Acceptance Criteria

```gherkin
GIVEN [precondition]
WHEN [action]
THEN [expected result]

GIVEN [precondition]
WHEN [action]
THEN [expected result]
```

Or in list format:
- [ ] [Criterion 1 - specific and measurable]
- [ ] [Criterion 2 - specific and measurable]
- [ ] [Criterion 3 - specific and measurable]

### Technical Notes

- [Technical note 1]
- [Technical note 2]

### Dependencies

- **Blocked by:** [KEY]-100 (must complete first)
- **Blocks:** [KEY]-102

---

### Tasks

#### Task [KEY]-101-T1: [Task Name]

**Estimate:** 4h
**Type:** Backend
**Assignee:** [Role]

**Description:**
[Detailed technical description of the task]

**Subtasks:**

| # | Subtask | Est. | Done |
|---|---------|------|------|
| 1 | [Create migration file for X table] | 1h | ☐ |
| 2 | [Add indexes for Y fields] | 30m | ☐ |
| 3 | [Write seed data] | 30m | ☐ |
| 4 | [Write unit tests for model] | 1h | ☐ |
| 5 | [Update documentation] | 1h | ☐ |

**Definition of Done:**
- [ ] Code reviewed and approved
- [ ] Unit tests passing (coverage > 80%)
- [ ] Documentation updated

---

#### Task [KEY]-101-T2: [Task Name]

**Estimate:** 6h
**Type:** Backend
**Assignee:** [Role]

**Description:**
[Technical description]

**Subtasks:**

| # | Subtask | Est. | Done |
|---|---------|------|------|
| 1 | [Implement POST endpoint] | 2h | ☐ |
| 2 | [Implement GET endpoint] | 1.5h | ☐ |
| 3 | [Add validation middleware] | 1h | ☐ |
| 4 | [Write integration tests] | 1h | ☐ |
| 5 | [Add error handling] | 30m | ☐ |

---

#### Task [KEY]-101-T3: [Task Name]

**Estimate:** 4h
**Type:** Frontend
**Assignee:** [Role]

[... same structure ...]

---

## Story: [KEY]-102 - [Story Name]

[... same structure ...]

---

# Sprint Planning

## Sprint 1 (Foundation)

| Story | Points | Focus |
|-------|--------|-------|
| [KEY]-101 | 8 | Auth setup |
| [KEY]-102 | 5 | Base schema |
| **Total** | **13** | |

## Sprint 2 (Core Features)

| Story | Points | Focus |
|-------|--------|-------|
| [KEY]-201 | 8 | Feature A |
| [KEY]-202 | 5 | Feature B |
| **Total** | **13** | |

---

# Dependencies Map

```
[KEY]-101 (Auth)
    │
    ├──▶ [KEY]-102 (Users)
    │        │
    │        └──▶ [KEY]-201 (Permissions)
    │
    └──▶ [KEY]-103 (API Base)
             │
             └──▶ [KEY]-202 (Endpoints)
```

---

# Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| [Risk 1] | High | Medium | [Strategy] |
| [Risk 2] | Medium | Low | [Strategy] |
```

### 6. STOPPING CONDITION

```
The breakdown is complete when:

✅ Every section in Tech Spec is covered by Epic/Story/Task

✅ Every Epic includes:
   ├── Name and description
   ├── Priority
   ├── At least 2 Stories
   └── Target sprint range

✅ Every Story includes:
   ├── Valid User Story format (As a... I want... So that...)
   ├── At least 3 Acceptance Criteria
   ├── Story Points (Fibonacci)
   ├── At least 2 Tasks
   └── Dependencies (if any)

✅ Every Task includes:
   ├── Technical description
   ├── Estimate in hours (2-8h)
   ├── Type (Backend/Frontend/QA)
   └── At least 2 Subtasks

✅ Every Subtask:
   ├── 30 minutes to 2 hours
   └── Can be completed "in one sitting"

✅ Estimates sum correctly:
   Sum(Subtasks) ≈ Task estimate

✅ Dependencies are identified and documented

✅ Sprint plan exists
```

### 7. PROMPT STEPS

```
┌─────────────────────────────────────────────────────────────┐
│ STEP 1: TECH SPEC ANALYSIS                                  │
├─────────────────────────────────────────────────────────────┤
│ □ Read the entire Tech Spec                                 │
│ □ List all modules/sections:                                │
│   • Authentication                                          │
│   • Data Models                                             │
│   • API Endpoints                                           │
│   • etc.                                                    │
│ □ List all technical components:                            │
│   • Database tables                                         │
│   • API endpoints                                           │
│   • Services                                                │
│   • UI components                                           │
│ □ Identify the natural dependency order                     │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ STEP 2: EPIC DEFINITION                                     │
├─────────────────────────────────────────────────────────────┤
│ □ Group related components into Epics                       │
│ □ For each Epic ensure:                                     │
│   • Independent as much as possible                         │
│   • Clear business value                                    │
│   • 2-6 weeks of work                                       │
│ □ Define priority for each Epic:                            │
│   • Critical = required for MVP                             │
│   • High = needed for first release                         │
│   • Medium = can wait                                       │
│   • Low = Nice to have                                      │
│ □ Write description and business value                      │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ STEP 3: STORY EXTRACTION                                    │
├─────────────────────────────────────────────────────────────┤
│ □ For each Epic, ask: "What can the user do?"              │
│ □ Write each Story in format:                               │
│   "As a [role], I want to [action], so that [benefit]"     │
│                                                             │
│ □ Add Acceptance Criteria:                                  │
│   • Specific - not "works well"                             │
│   • Measurable - can be tested                              │
│   • Achievable - realistic                                  │
│   • Relevant - related to Story                             │
│                                                             │
│ □ Estimate Story Points:                                    │
│   │ Points │ Complexity  │ Duration      │                 │
│   │ 1      │ Trivial     │ < 4 hours     │                 │
│   │ 2      │ Simple      │ 4-8 hours     │                 │
│   │ 3      │ Moderate    │ 1-2 days      │                 │
│   │ 5      │ Complex     │ 2-3 days      │                 │
│   │ 8      │ Very Complex│ 3-5 days      │                 │
│   │ 13     │ Epic-level  │ Break it down!│                 │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ STEP 4: TASK BREAKDOWN                                      │
├─────────────────────────────────────────────────────────────┤
│ □ For each Story, identify technical work                   │
│ □ Common Task types:                                        │
│   • Database: Create table, Add index, Migration            │
│   • Backend: Implement service, Create endpoint             │
│   • Frontend: Create component, Add form                    │
│   • Testing: Write unit tests, Integration tests            │
│   • Documentation: Update README, API docs                  │
│                                                             │
│ □ For each Task:                                            │
│   • Estimate: 2-8 hours (if more - break it down!)          │
│   • Type: Backend/Frontend/QA/DevOps                        │
│   • Clear technical description                             │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ STEP 5: SUBTASK DETAILS                                     │
├─────────────────────────────────────────────────────────────┤
│ □ For each Task, break down to atomic steps                 │
│ □ Each Subtask should be:                                   │
│   • 30 minutes to 2 hours                                   │
│   • Can be completed without interruption                   │
│   • Clear and verifiable outcome                            │
│                                                             │
│ □ Phrasing examples:                                        │
│   ✓ "Create migration file for users table"                │
│   ✓ "Add index on email column"                            │
│   ✓ "Implement password hashing in service"                │
│   ✓ "Write unit test for login function"                   │
│   ✗ "Work on authentication" (too vague)                   │
│   ✗ "Fix bugs" (undefined scope)                           │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ STEP 6: ESTIMATION VALIDATION                               │
├─────────────────────────────────────────────────────────────┤
│ □ Sum Subtasks for each Task:                               │
│   Sum(Subtask estimates) ≤ Task estimate                   │
│                                                             │
│ □ Ensure Task doesn't exceed 8 hours                        │
│   If it does → break into 2 Tasks                          │
│                                                             │
│ □ Sum Tasks for each Story:                                 │
│   Total hours ≈ Story Points × 4                           │
│                                                             │
│ □ Ensure estimates are realistic:                           │
│   Add 20% buffer to each sprint                            │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ STEP 7: DEPENDENCIES MAPPING                                │
├─────────────────────────────────────────────────────────────┤
│ □ Identify dependencies between Stories:                    │
│   • Story A must complete before Story B?                   │
│                                                             │
│ □ Identify dependencies between Tasks:                      │
│   • DB schema before API                                    │
│   • API before Frontend                                     │
│                                                             │
│ □ Mark blocking dependencies:                               │
│   • "Blocked by: [KEY]-100"                                │
│   • "Blocks: [KEY]-102"                                    │
│                                                             │
│ □ Draw dependency graph                                     │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ STEP 8: SPRINT PLANNING                                     │
├─────────────────────────────────────────────────────────────┤
│ □ Distribute Stories to Sprints by:                         │
│   • Dependencies (what must come first)                     │
│   • Priority (Critical first)                               │
│   • Capacity (not more than velocity)                       │
│                                                             │
│ □ For each Sprint ensure:                                   │
│   • Total points ≤ Team velocity                           │
│   • Dependencies are satisfied                              │
│   • Business value at end of Sprint                         │
│                                                             │
│ □ Add buffer (20%) to each sprint                          │
│                                                             │
│ □ Identify risks and mitigations                            │
└─────────────────────────────────────────────────────────────┘
```

---

## Quality Checklist

Before finalizing the breakdown:

- [ ] All Tech Spec sections covered
- [ ] Every Epic has clear business value
- [ ] Stories follow user story format
- [ ] Acceptance criteria are testable
- [ ] Tasks are 2-8 hours
- [ ] Subtasks are 30min-2h
- [ ] Estimates sum correctly
- [ ] Dependencies documented
- [ ] Sprint plan created
- [ ] Risks identified

---

## Document-to-Jira Mapping

| Document | Jira Item | What to Extract |
|----------|-----------|-----------------|
| **PRD** | Stories | User stories → Jira Stories |
| **Tech Spec** | Tasks | API endpoints, components → Technical Tasks |
| **Implementation Plan** | Subtasks | Phase tasks → Atomic subtasks |

---

## Phase Integration

This command is used in **Phase 3: Breakdown**

After breakdown creation:
1. Review estimates with team
2. Prioritize stories
3. Assign to sprint
4. Get approval with `/phase-approve`
5. Move to Phase 4: Development with `/phase-advance`

---

## Jira MCP Integration

If Atlassian MCP is configured in `.mcp.json`:

```json
{
  "mcpServers": {
    "jira": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-atlassian"],
      "env": {
        "ATLASSIAN_SITE_URL": "${ATLASSIAN_SITE_URL}",
        "ATLASSIAN_USER_EMAIL": "${ATLASSIAN_USER_EMAIL}",
        "ATLASSIAN_API_TOKEN": "${ATLASSIAN_API_TOKEN}"
      }
    }
  }
}
```

The command will:
1. Create Epic in Jira
2. Create Stories linked to Epic
3. Create Tasks linked to Stories
4. Set estimates and assignees

---

## Examples

```bash
# Generate from project documents
/jira-breakdown user-authentication
# Reads:
#   - docs/prd/2024-06-15-user-authentication.md
#   - docs/tech-spec/2024-06-16-user-authentication.md
#   - docs/implementation-plan/2024-06-17-user-authentication.md

# Interactive mode
/jira-breakdown
```

---

## Story Template

```markdown
# [STORY_ID]: [Story Name]

**Epic:** [EPIC_ID]
**Priority:** [Priority]
**Story Points:** [Points]

## User Story
**As a** [role]
**I want to** [action]
**So that** [benefit]

## Acceptance Criteria
- [ ] Criteria 1
- [ ] Criteria 2

## Tasks
### Task 1: [Name] (Xh)
- [ ] Subtask 1.1
- [ ] Subtask 1.2

### Task 2: [Name] (Xh)
- [ ] Subtask 2.1

## Technical Notes
[Any technical context]

## Dependencies
- [Dependency 1]
```
