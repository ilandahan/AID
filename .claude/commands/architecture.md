# /architecture Command

Design system architecture for new systems or major refactors.

## Usage

```
/architecture <system-name>
```

## What It Does

1. **Analyzes Requirements**
   - Business drivers and constraints
   - User journeys and flows
   - Scale and performance needs

2. **Designs Architecture**
   - System components and boundaries
   - Data flow and storage
   - API contracts
   - Integration points

3. **Documents Decisions**
   - Technology choices with rationale
   - Trade-offs considered
   - Risks and mitigations

4. **Uses Skill**
   - `system-architect` skill for methodology

## Examples

```bash
# Design a new system
/architecture payment-service

# Design with specific focus
/architecture user-auth --focus security

# Design for specific scale
/architecture analytics-pipeline --scale 10M-events-day
```

## Related Commands

| Command | Use Case |
|---------|----------|
| `/architecture` | System-level design |
| `/tech-spec` | Feature-level specification |

## Guiding Principles

1. **User Journeys Drive Architecture**
   - Every decision traces to user need
   - Start with "what is user trying to accomplish?"

2. **Simplicity First**
   - Monolith → Modular Monolith → Microservices
   - Don't solve problems you don't have

3. **Boring Technology Wins**
   - PostgreSQL over newest DB
   - REST over GraphQL (unless reason)
   - Proven over cutting-edge

4. **Design for Failure**
   - Everything fails eventually
   - Graceful degradation
   - Explicit error handling

## Technology Defaults

| Category | Default | Why |
|----------|---------|-----|
| Database | PostgreSQL | Battle-tested, flexible |
| Cache | Redis | Simple, fast |
| Queue | Redis/BullMQ | Start simple |
| API | REST + OpenAPI | Universal, cacheable |
| Auth | OAuth2 + JWT | Industry standard |
| Cloud | AWS or GCP | Mature, reliable |

## Output Format

```markdown
# Architecture: [System Name]

## 1. Context & Goals
- Business drivers
- User journeys
- Constraints

## 2. System Overview
- High-level diagram (Mermaid)
- Component breakdown
- Boundaries

## 3. Data Architecture
- Storage strategy
- Data flow
- Consistency model

## 4. API Design
- Endpoints overview
- Authentication
- Rate limiting

## 5. Integration Points
- External systems
- Events/messaging
- Third-party services

## 6. Non-Functional Requirements
- Performance targets
- Scalability plan
- Security measures

## 7. Decision Log
- Key choices
- Alternatives considered
- Trade-offs

## 8. Risks & Mitigations
```

## Key Questions

Before starting:
1. Who is the user and what are they accomplishing?
2. What does success look like?
3. What are hard constraints?
4. Expected scale now vs. 12 months vs. 3 years?
5. What existing systems to integrate with?

Before adding complexity:
1. Do we actually need this?
2. What's the operational cost?
3. Can team maintain this at 2 AM?
4. Is there a simpler 80% solution?

## Anti-Patterns to Avoid

- ❌ Resume-Driven Development
- ❌ Distributed Monolith
- ❌ Premature Abstraction
- ❌ Cargo Culting ("Netflix does it")
- ❌ NIH Syndrome
- ❌ Silver Bullet Thinking

## Tips

- Start with user journeys
- Question every complexity
- Document decisions with rationale
- Consider operational burden
- Plan for failure from day one

---

## Prompt

```markdown
**Role**: You are a senior system architect with expertise in distributed systems, API design, and cloud infrastructure. You favor proven "boring" technology over trends.

**Task**: Design the system architecture for [SYSTEM_NAME], including components, data flow, APIs, and deployment strategy.

**Context**:
- System: [SYSTEM_NAME]
- Scale: [EXPECTED_SCALE]
- Constraints: [CONSTRAINTS]
- Read: `skills/system-architect/SKILL.md`

**Reasoning**:
- User journeys drive architecture
- Simplicity first, scale when needed
- Boring technology wins
- Design for failure
- Consider operational complexity

**Output Format**:
1. Context & Goals
2. System Overview (with Mermaid diagram)
3. Component Deep Dive
4. Data Architecture
5. API Design
6. Integration Points
7. Non-Functional Requirements
8. Decision Log
9. Risks & Mitigations

**Stopping Condition**:
- All major components documented
- Data flow clear
- API contracts defined
- Security addressed
- Deployment strategy outlined
- Key decisions documented with rationale

**Steps**:
1. Understand business context and user journeys
2. Identify key constraints and scale requirements
3. Design high-level system components
4. Define data storage and flow
5. Specify API contracts
6. Plan integration points
7. Address security and compliance
8. Document non-functional requirements
9. Log key decisions with alternatives considered
10. Identify risks and mitigations

---
System: [SYSTEM_NAME]
Context: [BUSINESS_CONTEXT]
---
```
