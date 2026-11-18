---
name: aid-tech-spec
description: AID Phase 2 - Technical Specification creation. Use this skill when designing system architecture, defining API contracts, creating data models, planning security architecture, or transitioning from PRD to implementation planning. Ensures clear technical blueprint for developers.
---

# Tech Spec Phase Skill

## Phase Overview

**Purpose**: Design the technical solution that will implement the requirements. Create a blueprint that developers can follow without ambiguity.

**Entry Criteria**:
- PRD phase completed and approved
- Requirements are clear and testable
- Dependencies identified
- Non-functional requirements defined

**Exit Criteria**:
- Tech spec document complete and approved
- Architecture decisions documented
- API contracts defined
- Data models specified
- Implementation can begin

## Deliverables

### 1. Tech Spec Document
- **Description**: Technical design for implementing requirements
- **Format**: Structured document with architecture, APIs, data models
- **Quality bar**: Developer can implement without needing clarification

### 2. Architecture Diagram
- **Description**: Visual representation of system components
- **Format**: Component diagram, sequence diagrams as needed
- **Quality bar**: Shows all major components and their interactions

### 3. API Contracts
- **Description**: Interface definitions for all endpoints/services
- **Format**: OpenAPI/Swagger, or structured documentation
- **Quality bar**: Request/response schemas, error codes, examples

### 4. Data Models
- **Description**: Database schemas, data structures
- **Format**: ERD, schema definitions, type definitions
- **Quality bar**: All fields defined with types and constraints

### 5. Agent Architecture
- **Description**: Section 9 of the tech spec: how the solution shape chosen in PRD §1.5 is built, with every item traced to its §7A Agentic Design item
- **Format**: Orchestration pattern, tool contracts, permission policy (as code), guardrails, trace schema, eval harness, model choice and fallbacks, cost and latency budgets, kill switch
- **Quality bar**: Always present, never "N/A". At levels 0-1 each heading takes its classic form (process/service design, permissions, logging, test harness, rollback). See `references/agent-architecture.md`

## Role-Specific Guidance

### For Product Managers
- Validate technical approach addresses requirements
- Clarify requirements when questions arise
- Ensure user experience isn't compromised
- Review for scope alignment

### For Developers
- Own the tech spec document
- Design for maintainability and testability
- Consider error handling from the start
- Document trade-offs and decisions

### For QA Engineers
- Review for testability
- Identify integration test points
- Plan test environment needs
- Flag potential test data challenges

### For Tech Leads
- Review architecture decisions
- Ensure alignment with standards
- Validate scalability approach
- Approve technical direction
- Own the solution-shape ladder level (PRD §1.5): lowest level that works, each step up justified
- Approve the agent architecture (Section 9) and the permission policy

## Common Pitfalls

| Pitfall | Problem | Fix |
|---------|---------|-----|
| Over-engineering | Building for hypothetical futures | Design for current needs |
| Missing error handling | Errors undefined until coding | Define error scenarios upfront |
| Tight coupling | Hard to test and modify | Design for testability and modularity |
| Ignoring non-functionals | Performance issues later | Address performance, security, scalability |
| Unclear contracts | API ambiguity | APIs must be unambiguous with examples |
| Agent where a workflow works | Cost, risk and latency with no gain | Build the lowest ladder level that works |
| Section 9 marked "N/A" | Non-AI projects lose logging, rollback, tests | Use the classic form for levels 0-1 |
| Permissions only in the prompt | Model can be talked out of them | Policy as code, enforced outside the model |

## Phase Gate Checklist

Before requesting approval to proceed:

- [ ] Tech spec document is complete
- [ ] Architecture diagram created
- [ ] All API contracts defined
- [ ] Data models specified
- [ ] Error handling strategy defined
- [ ] Security considerations addressed
- [ ] Performance requirements addressed
- [ ] Agent Architecture (Section 9) filled at the §1.5 level, never "N/A"
- [ ] Every Section 9 item traces to its §7A item
- [ ] Level 5 only with one of the four multi-agent justifications
- [ ] Tech lead has approved

## Transition to Implementation Phase

Hand off:
- Approved tech spec
- API contracts
- Data models
- Architecture decisions with rationale
- Any spike/POC results
- Agent Architecture: permission policy, trace schema, eval harness design, kill switch

## Tech Spec Template

```markdown
# [Feature Name] Technical Specification

## 1. Overview

### Problem Summary
[Brief description of what we're solving]

### Proposed Solution
[High-level approach]

### Key Decisions
| Decision | Choice | Rationale |
|----------|--------|-----------|
| [Decision 1] | [Choice] | [Why] |

## 2. Architecture

### System Diagram
[Mermaid or image]

### Component Breakdown
| Component | Responsibility | Dependencies |
|-----------|---------------|--------------|
| [Component 1] | [What it does] | [What it needs] |

### Data Flow
[How data moves through the system]

## 3. API Design

### Endpoints

#### POST /api/[resource]
**Request:**
```json
{
  "field1": "string",
  "field2": "number"
}
```

**Response (200):**
```json
{
  "id": "string",
  "created_at": "datetime"
}
```

**Errors:**
| Code | Error | Description |
|------|-------|-------------|
| 400 | INVALID_INPUT | [When this occurs] |
| 401 | UNAUTHORIZED | [When this occurs] |

## 4. Data Model

### Entity: [Name]
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | uuid | PK | Unique identifier |
| [field] | [type] | [constraints] | [description] |

### Database Schema
```sql
CREATE TABLE [name] (
  id UUID PRIMARY KEY,
  ...
);
```

## 5. Security

### Authentication
[How users authenticate]

### Authorization
[How permissions are checked]

### Data Protection
[How sensitive data is protected]

## 6. Error Handling

| Scenario | Response | Recovery |
|----------|----------|----------|
| [Error scenario] | [What happens] | [How to recover] |

## 7. Non-Functional Requirements

| Requirement | Target | Measurement |
|-------------|--------|-------------|
| Response time | <200ms | P95 latency |
| Availability | 99.9% | Uptime monitoring |

## 8. Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| [Risk 1] | [Impact] | [How to mitigate] |

## 9. Agent Architecture

[Single copy of this section's template, with scaling by level and the classic forms for
levels 0-1: `references/agent-architecture.md`. Never "N/A". Headings:]

### 9.1 Orchestration Pattern
### 9.2 Tool Contracts & Permission Policy
### 9.3 Guardrails
### 9.4 Trace Schema
### 9.5 Eval Harness
### 9.6 Model Choice & Fallbacks
### 9.7 Cost & Latency Budgets
### 9.8 Kill Switch
```

**Eval timing (A9, no relay):** Section 9.5 designs the eval harness (storage, runner, scorers, judge, gate) from PRD 7A.6 and the 20-30 seed cases written in Phase 1 (`docs/prd/SEED-EVALS-<feature>.md`). The golden set is NOT a precondition for the tech spec: QA grows it and its held-out split IN PARALLEL with Phases 2-4, and it must be complete only for the Phase 5 release gate. The data scientist calibrates the LLM judge in Phase 4, when a judge is introduced; the tech spec only names the judge and the calibration method.

## Output Location

Save Tech Spec to: `docs/tech-spec/YYYY-MM-DD-[feature-name].md`

---

## Learning Mode Integration

### Decision Transparency Triggers
- **Architecture decisions**: ALWAYS show reasoning for architecture choices
- **Technology selections**: Explain why specific tech stack chosen
- **Trade-off decisions**: Document what was sacrificed and why
- **Pattern selection**: Show why specific patterns chosen over alternatives

### Debate Invitations
- **Database selection**: When multiple viable options exist
- **Architecture pattern**: Monolith vs microservices, etc.
- **API design**: REST vs GraphQL, sync vs async
- **Caching strategy**: When trade-offs are significant

### Feedback Requests
- After architecture diagram: Validate approach
- After API contracts: Confirm completeness
- At phase gate: Overall Tech Spec quality rating (1-5)

### Example Transparency Block
```markdown
<decision-transparency>
**Decision:** Using PostgreSQL with Prisma ORM

**Reasoning:**
- **Data relationships**: Complex user-org-project hierarchy = relational model
- **ACID compliance**: Financial data requires transactions
- **Team familiarity**: Team has PostgreSQL experience

**Alternatives Considered:**
1. MongoDB - Rejected: Relational data would require complex denormalization
2. MySQL - Viable but PostgreSQL has better JSON support

**Confidence:** High - Clear fit for requirements

**Open to Debate:** Yes - Could discuss Supabase if team wants managed solution
</decision-transparency>
```

### Example Debate Invitation
```markdown
<debate-invitation>
**Topic:** Architecture approach for small team

**Option A: Microservices**
- ✅ Pros: Independent scaling, tech flexibility
- ❌ Cons: Operational overhead, distributed debugging

**Option B: Modular Monolith**
- ✅ Pros: Simple ops, easy debugging, lower cost
- ❌ Cons: All-or-nothing deployments

**My Lean:** Option B - Team of 3 doesn't have capacity for microservices ops

**But Consider:** If specific service needs independent scaling, hybrid approach

**Your Input Needed:** What's the team size? Any services with unique scaling needs?
</debate-invitation>
```
