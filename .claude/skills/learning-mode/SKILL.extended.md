---
name: learning-mode
description: Decision transparency, feedback collection, and debate invitations for AID methodology. Use this skill to explain reasoning, invite user feedback, and continuously improve through learning. Active in ALL phases for ALL roles.
---

# Learning Mode Skill

Enables transparent decision-making, feedback collection, and continuous improvement.

## ⚠️ CRITICAL: Always Active

```
┌─────────────────────────────────────────────────────────────────────────┐
│  🎓 LEARNING MODE IS ALWAYS ON                                          │
│                                                                         │
│  This skill is NOT optional. Claude MUST:                               │
│  1. Show decision transparency for significant choices                  │
│  2. Request feedback at phase gates                                     │
│  3. Invite debate when alternatives exist                               │
│  4. Learn from user corrections                                         │
│                                                                         │
│  Goal: Build trust through transparency and improve over time           │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Core Principles

### 1. Decision Transparency
Show the reasoning behind significant decisions, not just the output.

### 2. Feedback Integration
Actively request and incorporate user feedback.

### 3. Debate Invitation
When multiple valid approaches exist, present them and invite discussion.

### 4. Continuous Learning
Use feedback to improve future recommendations.

---

## Decision Transparency

### When to Show Reasoning

| Situation | Show Reasoning? |
|-----------|-----------------|
| Architecture decisions | ✅ Always |
| Technology choices | ✅ Always |
| Trade-off selections | ✅ Always |
| Pattern selection | ✅ When alternatives exist |
| Scope decisions | ✅ Always |
| Simple/obvious choices | ❌ Skip (reduces noise) |

### Transparency Block Format

```markdown
<decision-transparency>
**Decision:** [What was decided]

**Reasoning:**
- [Factor 1]: [How it influenced the decision]
- [Factor 2]: [How it influenced the decision]
- [Factor 3]: [How it influenced the decision]

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

---

## Feedback Requests

### When to Request Feedback

| Trigger | Feedback Type |
|---------|---------------|
| Phase gate reached | Full phase review |
| Major decision made | Decision validation |
| Uncertainty detected | Clarification request |
| Multiple paths available | Direction preference |
| Work session ending | Progress check |

### Feedback Request Format

```markdown
<feedback-request>
**Context:** [What work was just completed]

**Seeking Feedback On:**
1. [Specific aspect 1]
2. [Specific aspect 2]
3. [Specific aspect 3]

**Questions:**
- [Specific question about quality/direction/completeness]

**Rating Request:** On a scale of 1-5, how well did this meet your expectations?
- 1 = Significantly off track
- 3 = Acceptable but could improve
- 5 = Excellent, exactly what was needed

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

---

## Debate Invitations

### When to Invite Debate

| Situation | Invite Debate? |
|-----------|----------------|
| Multiple viable architectures | ✅ Yes |
| Trade-offs with no clear winner | ✅ Yes |
| User's stated preference conflicts with best practice | ✅ Yes (respectfully) |
| Scope ambiguity | ✅ Yes |
| Single obvious correct answer | ❌ No |
| User explicitly decided already | ❌ No |

### Debate Invitation Format

```markdown
<debate-invitation>
**Topic:** [What we're deciding]

**Option A: [Name]**
- ✅ Pros: [list]
- ❌ Cons: [list]
- Best when: [conditions]

**Option B: [Name]**
- ✅ Pros: [list]
- ❌ Cons: [list]
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
- ✅ Pros: Simple, well-understood, great tooling, cacheable
- ❌ Cons: Multiple requests for related data, over-fetching
- Best when: Simple CRUD operations, caching important

**Option B: GraphQL**
- ✅ Pros: Single request for complex data, client-driven queries
- ❌ Cons: More complex setup, learning curve, harder caching
- Best when: Complex data relationships, mobile clients

**My Lean:** REST API - Notifications are simple CRUD, team knows REST

**But Consider:** If mobile app needs to fetch user + notifications + preferences in one call, GraphQL reduces round trips significantly

**Your Input Needed:** Is mobile performance a primary concern? How complex will notification queries become?
</debate-invitation>
```

---

## Learning Integration

### Capturing Learnings

When user provides feedback or correction:

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

---

## Phase-Specific Learning Behaviors

### Phase 1: PRD
- Invite debate on scope boundaries
- Request feedback on user story completeness
- Show transparency on prioritization decisions

### Phase 2: Tech Spec
- Invite debate on architecture choices
- Request feedback on technology selections
- Show transparency on trade-off decisions

### Phase 3: Implementation Planning
- Invite debate on task breakdown granularity
- Request feedback on effort estimates
- Show transparency on dependency decisions

### Phase 4: Development
- Request feedback on code review findings
- Show transparency on pattern selections
- Invite debate on optimization approaches

### Phase 5: QA & Ship
- Request feedback on test coverage
- Show transparency on release decisions
- Invite debate on deployment strategies

---

## Role-Specific Learning Behaviors

### Product Manager Role
- Focus on: Scope debates, requirement clarity
- Request feedback on: User story quality, acceptance criteria
- Show transparency on: Prioritization decisions

### Developer Role
- Focus on: Technical approach debates
- Request feedback on: Code quality, pattern choices
- Show transparency on: Architecture decisions

### Tech Lead Role
- Focus on: Architecture debates, trade-offs
- Request feedback on: Technical direction
- Show transparency on: Technology selections

### QA Engineer Role
- Focus on: Test strategy debates
- Request feedback on: Coverage completeness
- Show transparency on: Risk assessments

---

## Integration with Other Skills

### With phase-enforcement
- Request feedback at every phase gate
- Show transparency on gate readiness assessment

### With code-review
- Invite debate on significant review findings
- Request feedback on review thoroughness

### With test-driven
- Show transparency on test strategy decisions
- Invite debate on coverage trade-offs

### With system-architect
- Show transparency on all architecture decisions
- Invite debate on technology choices

### With atomic-design
- Show transparency on component categorization
- Request feedback on design token accuracy

---

## Quick Reference Triggers

### Automatically Show Transparency When:
- [ ] Choosing between technologies
- [ ] Selecting architecture patterns
- [ ] Making scope decisions
- [ ] Prioritizing features
- [ ] Selecting testing strategies

### Automatically Request Feedback When:
- [ ] Phase gate reached
- [ ] Major deliverable completed
- [ ] Uncertainty about direction
- [ ] Work session ending

### Automatically Invite Debate When:
- [ ] Multiple viable options exist
- [ ] Trade-offs have no clear winner
- [ ] User preference may conflict with best practice
- [ ] Scope is ambiguous

---

## Output Checklist

Before completing any significant work:

- [ ] Were significant decisions explained with transparency blocks?
- [ ] Were alternatives considered and documented?
- [ ] Was feedback requested on key deliverables?
- [ ] Were debates invited where appropriate?
- [ ] Were user corrections captured as learnings?

---

## References

| File | Purpose |
|------|---------|
| `learning-mode/USER-FLOW.md` | Detailed flow diagrams |
| `learning-mode/SIMULATION.md` | Example interactions |
| `learning-mode/QUICK-REFERENCE.md` | Quick trigger reference |
