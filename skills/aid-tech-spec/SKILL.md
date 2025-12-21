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

## Common Pitfalls

| Pitfall | Problem | Fix |
|---------|---------|-----|
| Over-engineering | Building for hypothetical futures | Design for current needs |
| Missing error handling | Errors undefined until coding | Define error scenarios upfront |
| Tight coupling | Hard to test and modify | Design for testability and modularity |
| Ignoring non-functionals | Performance issues later | Address performance, security, scalability |
| Unclear contracts | API ambiguity | APIs must be unambiguous with examples |

## Phase Gate Checklist

Before requesting approval to proceed:

- [ ] Tech spec document is complete
- [ ] Architecture diagram created
- [ ] All API contracts defined
- [ ] Data models specified
- [ ] Error handling strategy defined
- [ ] Security considerations addressed
- [ ] Performance requirements addressed
- [ ] Tech lead has approved

## Transition to Implementation Phase

Hand off:
- Approved tech spec
- API contracts
- Data models
- Architecture decisions with rationale
- Any spike/POC results

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
```

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
