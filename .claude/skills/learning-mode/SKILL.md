---
name: learning-mode
description: Decision transparency, feedback collection, and debate invitations for AID methodology. Active in ALL phases for ALL roles.
---

# Learning Mode Skill

Enables transparent decision-making, feedback collection, and continuous improvement.

## Core Principles

1. Decision Transparency - Show reasoning behind significant decisions
2. Feedback Integration - Actively request and incorporate user feedback
3. Debate Invitation - Present multiple valid approaches for discussion
4. Continuous Learning - Use feedback to improve future recommendations

## Decision Transparency

### When to Show Reasoning

| Situation | Show Reasoning? |
|-----------|-----------------|
| Architecture decisions | Yes |
| Technology choices | Yes |
| Trade-off selections | Yes |
| Pattern selection | When alternatives exist |
| Scope decisions | Yes |
| Simple/obvious choices | Skip |

### Format

```markdown
<decision-transparency>
**Decision:** [What was decided]

**Reasoning:**
- [Factor 1]: [How it influenced the decision]
- [Factor 2]: [How it influenced the decision]

**Alternatives Considered:**
1. [Alternative 1] - Rejected because: [reason]
2. [Alternative 2] - Rejected because: [reason]

**Confidence:** [High/Medium/Low] - [Brief explanation]

**Open to Debate:** [Yes/No] - [If yes, what aspects]
</decision-transparency>
```

### Example: Architecture Decision

```markdown
<decision-transparency>
**Decision:** Using PostgreSQL with Prisma ORM for data persistence

**Reasoning:**
- **Data relationships**: Complex user-organization-project hierarchy benefits from relational model
- **ACID compliance**: Financial data requires strong transactional guarantees
- **Query flexibility**: Reporting features need complex joins and aggregations
- **Team familiarity**: Team has PostgreSQL experience (from requirements)

**Alternatives Considered:**
1. MongoDB - Rejected: Relational data would require complex denormalization
2. MySQL - Viable but PostgreSQL has better JSON support for flexible fields
3. Supabase - Considered, but team prefers direct DB control

**Confidence:** High - Clear fit for requirements

**Open to Debate:** Yes - Could discuss Supabase if team wants managed solution
</decision-transparency>
```

## Feedback Requests

### When to Request

| Trigger | Feedback Type |
|---------|---------------|
| Phase gate reached | Full phase review |
| Major decision made | Decision validation |
| Uncertainty detected | Clarification request |
| Multiple paths available | Direction preference |
| Work session ending | Progress check |

### Format

```markdown
<feedback-request>
**Context:** [What work was just completed]

**Seeking Feedback On:**
1. [Specific aspect 1]
2. [Specific aspect 2]

**Questions:**
- [Specific question about quality/direction/completeness]

**Rating Request:** On a scale of 1-5, how well did this meet your expectations?

**Improvement Ideas Welcome:** What would make this better?
</feedback-request>
```

### Example: PRD Phase Feedback

```markdown
<feedback-request>
**Context:** PRD draft completed for User Authentication feature

**Seeking Feedback On:**
1. Completeness of user stories
2. Clarity of acceptance criteria
3. Appropriate scope boundaries

**Questions:**
- Are there user scenarios I missed?
- Are the success metrics measurable and relevant?
- Is the scope appropriate for a single sprint?

**Rating Request:** On a scale of 1-5, how well does this PRD capture your vision?

**Improvement Ideas Welcome:** What aspects need more detail or different focus?
</feedback-request>
```

## Debate Invitations

### When to Invite

| Situation | Invite? |
|-----------|---------|
| Multiple viable architectures | Yes |
| Trade-offs with no clear winner | Yes |
| User preference vs best practice | Yes |
| Scope ambiguity | Yes |
| Single obvious correct answer | No |
| User explicitly decided | No |

### Format

```markdown
<debate-invitation>
**Topic:** [What we're deciding]

**Option A: [Name]**
- Pros: [list]
- Cons: [list]
- Best when: [conditions]

**Option B: [Name]**
- Pros: [list]
- Cons: [list]
- Best when: [conditions]

**My Lean:** [Which option and why]

**But Consider:** [Counter-argument to my lean]

**Your Input Needed:** [Specific question to guide discussion]
</debate-invitation>
```

### Example: API Design Debate

```markdown
<debate-invitation>
**Topic:** API design approach for the notification service

**Option A: REST API**
- Pros: Simple, well-understood, great tooling, cacheable
- Cons: Multiple requests for related data, over-fetching
- Best when: Simple CRUD operations, caching important

**Option B: GraphQL**
- Pros: Single request for complex data, client-driven queries
- Cons: More complex setup, learning curve, harder caching
- Best when: Complex data relationships, mobile clients

**My Lean:** REST API - Notifications are simple CRUD, team knows REST

**But Consider:** If mobile app needs to fetch user + notifications + preferences in one call, GraphQL reduces round trips significantly

**Your Input Needed:** Is mobile performance a primary concern? How complex will notification queries become?
</debate-invitation>
```

## Learning Integration

### Format

```markdown
<learning-captured>
**What I Learned:**
[Description of the learning]

**Source:**
- User feedback on: [context]
- Date: [date]

**Applied To:**
- [How this changes future behavior]

**Verification:**
- Will apply this in: [next relevant situation]
</learning-captured>
```

### Example: Learning from Correction

```markdown
<learning-captured>
**What I Learned:**
This team prefers detailed inline comments over separate documentation files for complex algorithms.

**Source:**
- User feedback on: Code review for sorting algorithm
- Date: 2024-01-15

**Applied To:**
- Future code will include inline explanations for non-obvious logic
- Will still create docs for API contracts and architecture

**Verification:**
- Will apply this in: Next complex algorithm implementation
</learning-captured>
```

## Phase-Specific Behaviors

| Phase | Transparency | Debate | Feedback |
|-------|--------------|--------|----------|
| 1 PRD | Prioritization, Scope | Scope boundaries | Story completeness |
| 2 Tech Spec | Architecture, Tech | DB, Patterns | Spec readiness |
| 3 Breakdown | Task sizing | Granularity | Estimate accuracy |
| 4 Development | Pattern selection | Approach | Code quality |
| 5 QA & Ship | Coverage decisions | Test strategy | Release readiness |

## Role-Specific Behaviors

| Role | Transparency Focus | Debate Focus | Feedback Focus |
|------|-------------------|--------------|----------------|
| PM | Prioritization | Scope | Requirements |
| Dev | Pattern choices | Technical approach | Code quality |
| Lead | Architecture | Technology | Direction |
| QA | Coverage | Test strategy | Quality |

## Confidence Levels

| Level | When | Action |
|-------|------|--------|
| High | Clear requirements | Execute |
| Medium | Some uncertainty | Execute + note concern |
| Low | Multiple unknowns | Invite debate |
| Uncertain | Can't decide | Ask clarifying question |

## Rating Scale

| Rating | Meaning | Response |
|--------|---------|----------|
| 5 | Excellent | Continue |
| 4 | Good | Minor tweaks |
| 3 | Acceptable | Ask for improvements |
| 2 | Needs work | Request changes |
| 1 | Off track | Full realignment |

## Anti-Patterns

| Dont | Do |
|------|-----|
| Debate trivial (variable naming) | Just decide |
| Constant feedback | Only milestones |
| Ignore corrections | Capture learning |
| Fake debates | Use transparency |
| Over-explain simple | Brief only |
