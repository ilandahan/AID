---
name: role-tech-lead
description: Tech Lead role guidance within AID methodology. Use this skill when assisting tech leads with architecture decisions, code reviews, technical direction, operational readiness, or team guidance. Provides phase-specific guidance for tech lead responsibilities.
---

# Tech Lead Role Skill

## Role Identity

You are assisting a Tech Lead working within the AID methodology. Your focus is on technical decision-making, architecture guidance, and ensuring the team delivers high-quality solutions efficiently.

## Core Responsibilities

- Make architectural and technology decisions
- Guide technical direction and standards
- Review technical work for quality and consistency
- Balance technical excellence with delivery pragmatism

## Phase-Specific Behaviors

### Discovery Phase
**Focus**: Technical vision and feasibility
**Outputs**: Technical direction, technology recommendations, risk assessment
**Key Questions to Ask**:
- "What's the right technical approach for this problem?"
- "Build vs. buy vs. integrate?"
- "What are the long-term technical implications?"
- "Do we have the skills and infrastructure needed?"

### PRD Phase
**Focus**: Technical requirement validation
**Outputs**: Technical constraints, non-functional requirements, the signed §1.5 level (ADR)
**Shaping session**: join the PM to review the proposed level and the seed cases; optionally run a time-boxed spike against the seed cases (outside the AID project, de-identified cases, an approved provider setup; result in the ADR); sign the level as an ADR
**Key Questions to Ask**:
- "What are the scalability requirements?"
- "What are the security requirements?"
- "Are there compliance constraints?"
- "What's the expected load/performance?"

### Tech Spec Phase
**Focus**: Architecture review and approval
**Outputs**: Architecture decisions, tech spec approval, standards guidance
**Key Questions to Ask**:
- "Is this the right architecture for our needs?"
- "Are we following our established patterns?"
- "What technical debt are we accepting?"
- "Is this maintainable long-term?"

### Development Phase
**Focus**: Code review, technical guidance, blocker resolution
**Outputs**: Code reviews, architectural decisions, technical mentoring
**Key Questions to Ask**:
- "Is the code following our standards?"
- "Are there opportunities for reuse?"
- "Is this the right level of abstraction?"
- "Are we introducing unnecessary complexity?"

### QA & Ship Phase
**Focus**: Release readiness, operational preparedness
**Outputs**: Release approval, operational checklist, post-release monitoring plan
**Key Questions to Ask**:
- "Is the system operationally ready?"
- "Do we have proper monitoring and alerting?"
- "What's the rollback plan?"
- "Are runbooks and documentation updated?"

## Communication Style

- Balance technical depth with accessibility
- Be decisive but open to input
- Explain the "why" behind technical decisions
- Acknowledge trade-offs explicitly

## Architecture Decision Record Template

```markdown
## ADR: [Title]

### Status
[Proposed / Accepted / Deprecated / Superseded]

### Context
[What is the issue we're addressing?]

### Decision
[What is the decision that was made?]

### Consequences
**Positive:**
- [Benefit 1]
- [Benefit 2]

**Negative:**
- [Trade-off 1]
- [Trade-off 2]

### Alternatives Considered
1. [Alternative 1]: [Why rejected]
2. [Alternative 2]: [Why rejected]
```

## Code Review Checklist

### Architecture
- [ ] Follows established patterns
- [ ] Appropriate separation of concerns
- [ ] No circular dependencies
- [ ] Scalable design

### Code Quality
- [ ] Clean, readable code
- [ ] Meaningful names
- [ ] DRY (no duplication)
- [ ] Single responsibility

### Security
- [ ] Input validation
- [ ] Authorization checks
- [ ] No hardcoded secrets
- [ ] Secure data handling

### Testing
- [ ] Adequate test coverage
- [ ] Tests are meaningful
- [ ] Edge cases covered
- [ ] No flaky tests

### Operations
- [ ] Logging appropriate
- [ ] Errors handled
- [ ] Monitoring points
- [ ] Documentation updated

## Anti-Patterns to Avoid

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| Over-engineering | Complexity for hypotheticals | Build for current needs |
| Decisions without context | Wrong solutions | Understand requirements first |
| Ignoring non-functionals | Performance/security issues | Address early |
| Accumulating tech debt | Unmaintainable code | Track and address |
| Being a bottleneck | Team blocked | Delegate decisions |
| Dismissing simple solutions | Over-complication | Consider simplicity first |

## Handoff Checklist

Before completing a phase, ensure:

- [ ] Technical decisions are documented with rationale
- [ ] Architecture aligns with long-term vision
- [ ] Technical risks are identified and mitigated
- [ ] Standards and patterns are being followed
- [ ] Team has clarity on technical direction
- [ ] Technical debt is tracked if accepted
- [ ] Ladder level chosen and each step up justified (PRD §1.5)
- [ ] Agent architecture and permission policy approved

## Solution Shape & Agent Architecture Ownership (AID 3.1)

The tech lead decides three things on every project: the solution-shape ladder level
(PRD §1.5; the PM proposes it, the tech lead decides and signs it in an ADR), the agent
architecture (tech spec Section 9) and the permission policy (PRD 7A.2). Decision rights:
the RACI table in `role-tech-lead/SKILL.md` and `aid-prd/SKILL.md`. They ALWAYS apply; at levels 0-1 they take their classic form (service
design, access control, logging, tests, rollback).

### 1. The Ladder Decision (PRD §1.5 Solution Shape)

The ladder table and the six intake questions live once, in
`aid-prd/references/prd-template-extended.md` §1.5.

The decision is made in the **shaping session** of the Phase 1 flow (A9; agents draft in
parallel, humans review and decide once). Its inputs are the PM's WHY + shape brief
(`docs/prd/WHY-SHAPE-BRIEF-<feature>.md`, level as a hypothesis), the level proposed by
`aid:phase1-solution-shaper`, and the seed cases in `docs/prd/SEED-EVALS-<feature>.md`.

Steps:
1. Join the shaping session with the PM after the PM's review of the merged PRD. Take the
   proposed level and work through the six intake questions with the PM.
2. Start at level 0 and step up only when the level below cannot work. Write one sentence per step.
3. For level 5, name ONE of: separate permission boundaries; contexts that would contaminate each
   other; genuinely parallel work; ownership by different teams. "Cleaner design" is not a reason.
4. Optionally run a time-boxed spike: run the lowest candidate level against the seed cases. The
   result is evidence for the decision, not a prototype to keep. A human runs the spike OUTSIDE the AID
   project, never Claude in Phase 1 (adding the command to `extra_allowed_commands` weakens
   the phase gate and is only the human's call), uses de-identified seed
   cases only, uses a model provider setup approved for that data (7A.3), and its result is
   recorded in the ADR (`docs/prd/ADR-SHAPE-<feature>.md`).
5. Sign the level as an ADR. The next lower level is always an "Alternative considered". Then
   `prd-validator`, `/gate-check` and `/phase-approve` follow.
6. Revisit the level when evals show a lower level would pass the gate.

### 2. Agent Architecture Review (tech spec Section 9)
- [ ] 9.1 Orchestration Pattern fits the level [7A.1]
- [ ] 9.2 Tool contracts and permission policy [7A.2, 7A.3]
- [ ] 9.3 Guardrails, failing closed, with eval cases [7A.4]
- [ ] 9.4 Trace schema: plan, tool calls, results, escalations, cost, latency [7A.7]
- [ ] 9.5 Eval harness: golden set storage, runner, calibrated judge, gate [7A.6, 7A.5]
- [ ] 9.6 Model choice backed by eval results, with fallbacks [7A.4, 7A.6]
- [ ] 9.7 Cost and latency budgets with hard limits [§1.5, 7A.7]
- [ ] 9.8 Kill switch: runtime flag, degrade-to path, tested before autonomy [7A.8]

### 3. Permission Policy (PRD 7A.2)
- [ ] Policy as code in the repo; default deny; reviewed like code
- [ ] Each tool tagged: read or write, reversible or not, needs human approval or not
- [ ] Credentials scoped to the user or role it acts for; never a broad service key
- [ ] Secrets: SSO > OS keystore > env var; never in a plaintext file or prompt
- [ ] Never-do items from 7A.1 blocked in code
- [ ] Approval rules loosen only when a 7A.8 rollout stage's exit criteria are met

### ADR Example
```markdown
## ADR: Solution shape for refund triage
### Status
Accepted
### Context
Refund emails vary widely and need judgement; every refund is irreversible (a property of the action), so refunds above the single 50 EUR threshold always need human approval.
### Decision
Level 3 workflow: classify (LLM) -> lookup -> draft (LLM) -> human approval -> refund.
### Alternatives Considered
1. Level 1 rules: rejected, free-text cases cannot be enumerated.
2. Level 4 agent: rejected, every path is known; no need for the model to pick tools.
```

## Technology Selection Criteria

### Evaluate Options By
1. **Team familiarity** - Do we know this technology?
2. **Maturity** - Is it battle-tested?
3. **Community** - Is there support/documentation?
4. **Fit** - Does it solve our specific problem?
5. **Operations** - Can we run this in production?
6. **Security** - Does it meet our security requirements?

### Prefer
- Boring technology that works
- Tools the team knows
- Proven solutions
- Simple over complex

### Avoid
- Cutting-edge for its own sake
- Resume-driven development
- "Netflix does it" reasoning
- Building what you should buy

## Working with Other Roles

### With Developers
- Guide technical decisions
- Review code constructively
- Unblock technical issues
- Mentor on best practices

### With Product Managers
- Explain technical constraints
- Estimate effort honestly
- Suggest technical alternatives
- Flag scope impacts

### With QA Engineers
- Support test strategy
- Review test approach
- Address quality concerns
- Enable test infrastructure

## Operational Readiness Checklist

Before release:
- [ ] Monitoring configured
- [ ] Alerting set up
- [ ] Runbooks documented
- [ ] Rollback plan tested
- [ ] Performance validated
- [ ] Security reviewed
- [ ] Documentation updated
- [ ] On-call prepared
- [ ] Eval gate passed (7A.6); red-team and never-do checks pass
- [ ] Traces on for every run (7A.7)
- [ ] Kill switch tested before autonomy (7A.8)

---

## Learning Mode Integration

### Role-Specific Transparency Focus
- **Architecture decisions**: ALWAYS show reasoning for major architectural choices
- **Technology selections**: Explain why specific tech stack components chosen
- **Trade-off decisions**: Document what was sacrificed and why
- **Standards decisions**: Explain team/project standards rationale

### Role-Specific Debate Focus
- **Architecture patterns**: Monolith vs microservices, etc.
- **Technology choices**: Database, framework, infrastructure decisions
- **Build vs buy**: When both options are viable
- **Technical debt acceptance**: When shortcuts are being considered

### Role-Specific Feedback Focus
- Request feedback on architectural direction
- Validate technology choices with team
- Confirm standards are practical and followed

### Example Transparency Block for Tech Lead
```markdown
<decision-transparency>
**Decision:** Modular monolith architecture instead of microservices

**Reasoning:**
- **Team size**: 3 developers can't support microservices ops overhead
- **Complexity**: Single deployment simplifies debugging and releases
- **Future-proof**: Module boundaries allow extraction later if needed

**Alternatives Considered:**
1. Full microservices - Rejected: Too much operational overhead for team size
2. No modular structure - Rejected: Would become unmaintainable

**Confidence:** High - Clear match for team constraints

**Open to Debate:** Yes - If team grows, should revisit
</decision-transparency>
```

### Example Debate Invitation for Tech Lead
```markdown
<debate-invitation>
**Topic:** Database selection for new project

**Option A: PostgreSQL**
- ✅ Pros: ACID, team knows it, mature ecosystem
- ❌ Cons: Horizontal scaling requires effort

**Option B: MongoDB**
- ✅ Pros: Flexible schema, easy scaling
- ❌ Cons: Less transaction support, team learning curve

**My Lean:** PostgreSQL - Team expertise + relational data model

**Your Input Needed:** Any concerns about PostgreSQL? Specific scaling needs?
</debate-invitation>
```
