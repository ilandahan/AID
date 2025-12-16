# 7-Component Prompt Framework

Structured approach to creating effective prompts for AI-assisted development.

## Framework Overview

Every prompt should include these 7 components:

```
┌─────────────────────────────────────────────────────────┐
│  1. ROLE        - Who is Claude acting as?              │
│  2. TASK        - What needs to be done?                │
│  3. CONTEXT     - Background information                │
│  4. REASONING   - How to approach the problem           │
│  5. OUTPUT      - Expected format and structure         │
│  6. STOPPING    - When is the task complete?            │
│  7. STEPS       - Ordered execution sequence            │
└─────────────────────────────────────────────────────────┘
```

---

## Component Details

### 1. ROLE

Define Claude's persona and expertise level.

```markdown
**Role**: You are a senior software architect with expertise in:
- Distributed systems design
- API architecture
- PostgreSQL database design
- TypeScript/Node.js development
```

**Purpose**: Sets context for decision-making style and technical depth.

### 2. TASK

Clear statement of what needs to be accomplished.

```markdown
**Task**: Create a technical specification for the user authentication system that includes:
- System architecture
- API endpoints
- Database schema
- Security considerations
```

**Purpose**: Defines the primary objective and deliverable.

### 3. CONTEXT

Background information needed to complete the task.

```markdown
**Context**:
- This is for a B2B SaaS application
- Expected users: 10,000 in first year
- Existing infrastructure: AWS, PostgreSQL, Redis
- Team uses TypeScript and React
- Must comply with SOC2 requirements
```

**Purpose**: Provides constraints and existing conditions.

### 4. REASONING

How Claude should approach the problem.

```markdown
**Reasoning**:
- Prioritize simplicity over complexity
- Use proven patterns over cutting-edge solutions
- Consider operational burden of each choice
- Design for failure and graceful degradation
- Apply security-by-default principles
```

**Purpose**: Guides decision-making philosophy.

### 5. OUTPUT

Expected format and structure of the deliverable.

```markdown
**Output Format**:
- Markdown document with clear sections
- Include Mermaid diagrams for architecture
- TypeScript interfaces for all data models
- OpenAPI spec for REST endpoints
- SQL schema with proper constraints
```

**Purpose**: Ensures consistent, usable output.

### 6. STOPPING CONDITION

When is the task considered complete?

```markdown
**Stopping Condition**:
- All major components documented
- API contracts fully specified
- Database schema complete with migrations
- Security review section included
- No TODOs or placeholders remain
```

**Purpose**: Defines completion criteria.

### 7. PROMPT STEPS

Ordered sequence of actions.

```markdown
**Steps**:
1. Analyze requirements from PRD
2. Design high-level architecture
3. Define data models as TypeScript interfaces
4. Specify API endpoints with request/response types
5. Create database schema
6. Document security considerations
7. Review for completeness
8. Generate final document
```

**Purpose**: Provides structured execution path.

---

## Complete Prompt Templates

### PRD Generation Prompt

```markdown
**Role**: You are a senior product manager with experience in B2B SaaS products, user research, and agile methodologies.

**Task**: Transform the provided raw content into a comprehensive Product Requirements Document (PRD).

**Context**:
- Product: [Product Name]
- Target market: [Market description]
- Company stage: [Startup/Growth/Enterprise]
- Timeline: [Launch target]
- Raw content attached below

**Reasoning**:
- Focus on user problems, not solutions
- Prioritize features that deliver core value
- Be specific about success metrics
- Consider technical feasibility
- Apply MoSCoW prioritization

**Output Format**:
```
1. Executive Summary (1 paragraph)
2. Problem Statement
3. Goals & Success Metrics (measurable)
4. User Personas (2-3 detailed)
5. User Stories (As a... I want... So that...)
6. Feature Requirements
   - Must Have
   - Should Have
   - Could Have
   - Won't Have
7. Non-Functional Requirements
8. Out of Scope
9. Risks & Mitigations
10. Timeline
```

**Stopping Condition**:
- All sections complete
- Success metrics are measurable
- Features are prioritized
- Risks identified
- No ambiguous requirements

**Steps**:
1. Read and analyze all raw content
2. Identify key user problems
3. Create user personas
4. Write user stories
5. Extract and prioritize features
6. Define success metrics
7. Identify risks
8. Compile into PRD format
9. Review for completeness

---
[RAW CONTENT HERE]
---
```

### Tech Spec Generation Prompt

```markdown
**Role**: You are a senior system architect with expertise in distributed systems, API design, PostgreSQL, and TypeScript.

**Task**: Create a detailed technical specification for [Feature Name] based on the PRD.

**Context**:
- Existing stack: TypeScript, Node.js, PostgreSQL, Redis
- Infrastructure: AWS (ECS, RDS, ElastiCache)
- Team size: [X developers]
- Authentication: JWT + OAuth2
- API style: REST with OpenAPI
- PRD attached below

**Reasoning**:
- Favor simplicity and maintainability
- Use boring, proven technology
- Design for failure and graceful degradation
- Consider operational complexity
- Apply security-by-default

**Output Format**:
```
1. Overview
   - Problem summary
   - Proposed solution
   - Key decisions

2. Architecture
   - System diagram (Mermaid)
   - Component breakdown
   - Data flow

3. Data Models (TypeScript interfaces)
   - Entity definitions
   - Relationships
   - Validation rules

4. API Specification
   - Endpoints table
   - Request/Response types
   - Error handling

5. Database Schema
   - Tables (SQL)
   - Indexes
   - Migrations

6. Security
   - Authentication
   - Authorization
   - Data protection

7. Non-Functional Requirements
   - Performance targets
   - Scalability plan
   - Monitoring

8. Risks & Mitigations
```

**Stopping Condition**:
- All components specified
- TypeScript interfaces complete
- API contracts defined
- Database schema ready for migration
- Security review complete

**Steps**:
1. Analyze PRD requirements
2. Design system architecture
3. Define data models
4. Specify API endpoints
5. Create database schema
6. Document security measures
7. Define NFRs
8. Identify risks
9. Review for completeness

---
[PRD CONTENT HERE]
---
```

### Jira Breakdown Prompt

```markdown
**Role**: You are a technical project manager experienced in agile methodologies, sprint planning, and estimation.

**Task**: Create a complete Jira project breakdown from the technical specification.

**Context**:
- Sprint duration: 2 weeks
- Team capacity: [X] story points per sprint
- Tech spec attached below
- Story point scale: 1, 2, 3, 5, 8, 13

**Reasoning**:
- Break work into independently testable units
- Stories should be completable in 1-3 days
- Tasks should be 2-8 hours
- Include buffer for unknowns
- Front-load risky items

**Output Format**:
```
## Epic: [Epic Name]
**Description**: [What this epic delivers]
**Total Points**: [Sum]

### Story 1: [Story Title]
**Points**: [X]
**Description**: As a [user], I want [goal] so that [benefit]
**Acceptance Criteria**:
- [ ] Criterion 1
- [ ] Criterion 2

#### Tasks:
- [ ] Task 1 (Xh)
- [ ] Task 2 (Xh)
- [ ] Task 3 (Xh)
```

**Stopping Condition**:
- All features from spec have stories
- Every story has acceptance criteria
- All tasks have time estimates
- Total fits within timeline
- Dependencies documented

**Steps**:
1. Identify major epics from spec
2. Break epics into stories
3. Write acceptance criteria
4. Create technical tasks
5. Estimate story points
6. Identify dependencies
7. Validate against timeline
8. Generate final breakdown

---
[TECH SPEC CONTENT HERE]
---
```

---

## Quick Reference

### Prompt Component Checklist

Before submitting any prompt, verify:

- [ ] **Role** - Clear expertise and persona defined
- [ ] **Task** - Specific deliverable stated
- [ ] **Context** - All necessary background provided
- [ ] **Reasoning** - Decision-making philosophy specified
- [ ] **Output** - Format and structure defined
- [ ] **Stopping** - Completion criteria clear
- [ ] **Steps** - Execution sequence provided

### Common Mistakes

| Mistake | Impact | Fix |
|---------|--------|-----|
| Vague role | Inconsistent tone | Specify expertise level |
| Unclear task | Wrong deliverable | State exact output needed |
| Missing context | Assumptions made | Provide all constraints |
| No reasoning | Poor decisions | Define approach philosophy |
| Unspecified format | Unusable output | Show exact structure |
| No stopping condition | Endless generation | Define "done" criteria |
| Missing steps | Disorganized output | Provide execution order |

### Prompt Size Guidelines

| Component | Target Length |
|-----------|--------------|
| Role | 2-4 lines |
| Task | 3-5 lines |
| Context | 5-15 lines |
| Reasoning | 3-7 lines |
| Output | 10-30 lines |
| Stopping | 3-5 lines |
| Steps | 5-10 items |
