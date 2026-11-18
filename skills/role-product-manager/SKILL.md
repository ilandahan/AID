---
name: role-product-manager
description: PM role in AID methodology. Use for requirements, user stories, acceptance criteria, stakeholder management, scope definition.
---

# Product Manager Role

Depth: `references/prd-writing-guide.md`, `references/metrics-definition-guide.md`, `references/stakeholder-management.md`.

## Core Responsibilities
- Understand and articulate user problems
- Create clear, testable requirements
- Ensure stakeholder alignment
- Validate solutions solve problems

## Phase Focus
| Phase | Focus | Output | Ask |
|---|---|---|---|
| Discovery | Problem validation | Problem statement, stakeholder map, solution shape hypothesis | "What problem for whom?" / "Who touches this?" / "What does success look like?" / "Cost of not solving?" |
| PRD | Requirements | PRD, user stories, acceptance criteria, §7A.1 Charter, §7A.5 Why-Chain, metrics with guardrails | "Is story testable?" / "Criteria specific?" / "What's out of scope?" / "Dependencies?" |
| Tech Spec | Review feasibility | Alignment review, clarifications | "Technical approach addresses all requirements?" / "Requirements technically problematic?" / "Trade-offs?" |
| Development | Clarify & validate | Requirement answers, acceptance testing | "Implementation matching intent?" / "Need to adjust scope?" |
| QA & Ship | Acceptance | Sign-off, release notes | "Solves original problem?" / "Acceptance criteria met?" |

## Product Sense and Decision Rights
Product sense = segment (who exactly), pain (what hurts, how much), solution shape (the LOWEST level 0-5 on the PRD §1.5 ladder that works). The PM proposes the level; the tech lead decides. §7A.1 Charter and §7A.5 Why-Chain (a WHY with no requirement, eval or metric is an opinion, not a requirement): `SKILL.extended.md`. Decision rights (RACI), the same table as in `aid-prd/SKILL.md`:

| Item | Responsible | Accountable / decides |
|---|---|---|
| §1.5 Solution Shape level | PM proposes (from segment, pain, error cost) | Tech lead decides and signs (ADR) |
| §1.4 metrics, 7A.1 Charter, 7A.5 Why-Chain | PM | PM |
| 7A.2 Tools & Permissions, 7A.4 Failure Modes & Guardrails | Tech lead (input: security) | Tech lead |
| 7A.3 Context & Data | Tech lead (input: privacy/DPO) | Tech lead |
| 7A.6 Eval Plan | Data scientist (metrics, judge); QA (eval sets) | QA owns the release gate |
| 7A.7 Telemetry & Traces | Tech lead | Tech lead |
| 7A.8 Rollout & Kill Switch | Tech lead + named on-call owner | Tech lead |

## Phase 1 Flow (A9): agents draft in parallel; humans review and decide once
1. Run the WHY + shape conversation (`why-driven-decision`): WHY / 5 Whys, the 6 shape questions, on whose behalf it acts, who bears an error, never-do, approvals. Save `docs/prd/WHY-SHAPE-BRIEF-<feature>.md` with a level HYPOTHESIS.
2. Run `/prd`: the aggregator, the 4-way fan-out (`prd-writer`, `aid:phase1-solution-shaper`, `aid:phase1-charter-drafter`, `aid:phase1-eval-planner`), the merge into the PRD and `docs/prd/SEED-EVALS-<feature>.md`.
3. Review the merged PRD; resolve every conflict the merge reports.
4. Join the tech lead in the shaping session; the tech lead signs the level (ADR). Then `prd-validator`, `/gate-check`, `/phase-approve`. Details: `aid-prd/SKILL.extended.md`.

## User Story Format
```
As a [role]
I want [capability]
So that [benefit]

Acceptance Criteria:
- Given [context], when [action], then [outcome]
```

## Anti-Patterns
| Anti-Pattern | Fix |
|---|---|
| Solution-first | Start with problem |
| Implementation in requirements | Focus on WHAT not HOW |
| Assuming stakeholders | Verify who's affected |
| Vague criteria | "It should be fast" -> "<2s" |
| Scope creep | Explicit acknowledgment |

## Scope Management
In-scope: explicitly requested; validated with stakeholders; defined acceptance criteria. Out-of-scope: future enhancements; nice-to-haves without approval; other user segments.
Change process: 1. Acknowledge request 2. Assess impact 3. Get approval 4. Update docs 5. Communicate

## Working with Roles
Developers: clear requirements, answer questions. QA: review scenarios, clarify edge cases. Tech leads: discuss feasibility, accept constraints, decide the §1.5 level.

## Success Metrics
Quantify. Bad: "Make dashboard faster". Good: "Reduce load from 4s to <1s (P95)".
Every set: North Star + supporting + at least one guardrail (e.g. "error rate stays < 1%"). State cost per *successful* task, not just per run.

## Handoff Checklist
- [ ] Stakeholders identified
- [ ] Problem validated
- [ ] Requirements testable
- [ ] Scope defined (in AND out)
- [ ] Dependencies identified
- [ ] Success metrics defined (North Star, supporting, at least one guardrail)
- [ ] §7A.1 Charter: on whose behalf, who bears the error, never-do, escalation
- [ ] §7A.5 Why-Chain: every WHY has a requirement, an eval and a metric
- [ ] WHY + shape brief saved; seed evals saved; level signed by the tech lead (ADR)
