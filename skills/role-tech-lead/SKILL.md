---
name: role-tech-lead
description: Tech Lead role in AID methodology. Use for architecture decisions, code reviews, technical direction, operational readiness, team guidance.
---

# Tech Lead Role

## Core Responsibilities
- Make architecture and technology decisions
- Guide technical direction and standards
- Review work for quality and consistency
- Balance technical excellence with delivery
- Decide and sign the solution-shape level (PRD §1.5) after the PM proposes it; own the agent architecture and the permission policy

## Phase Focus and Key Questions
| Phase | Focus | Output | Key Questions |
|---|---|---|---|
| Discovery | Technical vision | Direction, recommendations, risks | "Right technical approach?" / "Build vs buy vs integrate?" / "Long-term implications?" / "Skills and infrastructure needed?" |
| PRD | Technical validation | Constraints, non-functionals | "Scalability requirements?" / "Security requirements?" / "Compliance constraints?" / "Expected load/performance?" / "Lowest ladder level that works?" |
| Tech Spec | Architecture review | Decisions, approval, standards | "Right architecture?" / "Following patterns?" / "Technical debt accepted?" / "Maintainable long-term?" / "Permission policy least-privilege?" |
| Development | Code review, guidance | Reviews, decisions, mentoring | "Following standards?" / "Opportunities for reuse?" / "Right abstraction level?" / "Unnecessary complexity?" |
| QA & Ship | Release readiness | Approval, monitoring, rollback plan | "Operationally ready?" / "Monitoring and alerting?" / "Rollback plan?" / "Documentation updated?" / "Eval gate passed, kill switch tested?" |

## Architecture Decision Record
```markdown
## ADR: [Title]

### Status
[Proposed / Accepted]

### Context
[What issue?]

### Decision
[What decision?]

### Consequences
Positive: [Benefits]
Negative: [Trade-offs]

### Alternatives
1. [Alt 1]: [Why rejected]
```

## Solution Shape, Agent Architecture & Permission Policy
Every project (AID 3.1; levels 0-1 use the classic form). Decision rights (RACI), the same table as in `aid-prd/SKILL.md`:

| Item | Responsible | Accountable / decides |
|---|---|---|
| §1.5 Solution Shape level | PM proposes (from segment, pain, error cost) | Tech lead decides and signs (ADR) |
| §1.4 metrics, 7A.1 Charter, 7A.5 Why-Chain | PM | PM |
| 7A.2 Tools & Permissions, 7A.4 Failure Modes & Guardrails | Tech lead (input: security) | Tech lead |
| 7A.3 Context & Data | Tech lead (input: privacy/DPO) | Tech lead |
| 7A.6 Eval Plan | Data scientist (metrics, judge); QA (eval sets) | QA owns the release gate |
| 7A.7 Telemetry & Traces | Tech lead | Tech lead |
| 7A.8 Rollout & Kill Switch | Tech lead + named on-call owner | Tech lead |

Ladder decision (PRD §1.5 Solution Shape; the PM proposes, the tech lead decides), made in the Phase 1 **shaping session** (A9; agents draft in parallel, humans review and decide once):
- [ ] Join the shaping session with the PM: review the WHY + shape brief, the level proposed by `aid:phase1-solution-shaper` and the seed cases (`docs/prd/SEED-EVALS-<feature>.md`)
- [ ] Optional: a time-boxed spike that runs the lowest level against the seed cases
- [ ] Six intake questions answered with the PM
- [ ] LOWEST level that works chosen (0 process change ... 5 multi-agent)
- [ ] Each step up justified in one sentence
- [ ] Level 5 only for: separate permission boundaries, contaminating contexts, parallel work, different team ownership
- [ ] Signed as an ADR; the next lower level listed as the rejected alternative

Agent architecture (tech spec Section 9):
- [ ] Orchestration pattern fits the level; every item traces to its §7A item
- [ ] Traces by default, eval gate, model fallbacks, cost and latency budgets, kill switch

Permission policy (7A.2):
- [ ] Default deny, least privilege per tool, kept as code
- [ ] Irreversible writes need human approval until the rollout stage allows otherwise
- [ ] Never-do items (7A.1) blocked in code, not only in the prompt
- [ ] Credentials scoped to whom it acts for: SSO > OS keystore > env var, never plaintext

## Code Review Checklist
- [ ] Architecture: follows patterns; separation of concerns; no circular deps; scalable
- [ ] Code quality: clean, readable; meaningful names; DRY; single responsibility
- [ ] Security: input validation; authorization; no hardcoded secrets
- [ ] Testing: adequate coverage; meaningful tests; edge cases
- [ ] Agentic: eval cases added before prompt or tool changes; tool calls go through the permission policy; traces emitted, versions recorded

## Anti-Patterns
| Anti-Pattern | Fix |
|---|---|
| Over-engineering | Build for current needs |
| Decisions without context | Understand requirements |
| Ignoring non-functionals | Address early |
| Being bottleneck | Delegate decisions |
| Dismissing simple | Consider simplicity |
| Agent where a workflow works | Lowest ladder level that works |

## Technology Selection
Evaluate by: 1. Team familiarity 2. Maturity 3. Community/docs 4. Problem fit 5. Operations 6. Security

Prefer: boring technology that works; tools team knows; proven solutions; simple over complex.

Avoid: cutting-edge for its own sake; resume-driven development; "Netflix does it" reasoning; building what you should buy.

## Operational Readiness
- [ ] Monitoring configured
- [ ] Alerting set up
- [ ] Runbooks documented
- [ ] Rollback plan tested
- [ ] Performance validated
- [ ] Security reviewed
- [ ] Documentation updated
- [ ] Eval gate passed; kill switch tested (7A.6, 7A.8)

## Handoff Checklist
- [ ] Technical decisions documented
- [ ] Architecture aligns with vision
- [ ] Risks identified
- [ ] Standards followed
- [ ] Team has clarity
- [ ] Tech debt tracked
- [ ] Ladder level decided and signed (ADR); permission policy approved
