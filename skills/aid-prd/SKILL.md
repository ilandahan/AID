---
name: aid-prd
description: AID Phase 1 - PRD creation. Use for user stories, acceptance criteria, scoping features, transitioning from discovery to tech spec.
---

# Phase 1: PRD

Applies when: Discovery complete, problem validated, stakeholders identified.
Done when: PRD complete, user stories with acceptance criteria, scope defined.
Purpose: Define what will be built with clarity for unambiguous development.

## Deliverables

1. PRD Document - Readable by technical and non-technical
2. User Stories - "As a [role], I want [capability] so that [benefit]"
3. Acceptance Criteria - **Gherkin format (REQUIRED)**, executable specifications
4. Feature Files - Saved to `features/` directory as `.feature` files
5. Scope Definition - In-scope and out-of-scope explicit
6. Traceability - Every requirement links to research or flagged as assumption
7. §1.5 Solution Shape - Level 0-5 on the ladder, with justifications
8. §7A Agentic Design - 7A.1-7A.8, always filled, scaled to the level

Gherkin is REQUIRED because acceptance criteria become the tests; no PRD-to-QA translation step. Gherkin syntax reference: `cucumber-bdd` skill. Deeper guides: `references/user-stories-guide.md`, `references/acceptance-criteria-patterns.md`, `references/prd-template-extended.md`.

## Content order (what the PRD must contain)

1. Write the problem and users (§1.2, §3) from the research report.
2. Set the metric set (§1.4): North Star, supporting, and at least one guardrail.
3. Choose the solution shape (§1.5): answer the 6 intake questions, pick the LOWEST level that works, justify each step up in one sentence.
4. Write user stories, Gherkin acceptance criteria and scope (§4-§6).
5. Fill §7A Agentic Design: 7A.1 Charter, 7A.2 Tools & Permissions, 7A.3 Context & Data, 7A.4 Failure Modes & Guardrails, 7A.5 Why-Chain, 7A.6 Eval Plan, 7A.7 Telemetry & Traces, 7A.8 Rollout & Kill Switch.
6. Close dependencies, assumptions, risks; run the phase gate checklist.

## Phase 1 Flow (A9): agents draft in parallel; humans review and decide once

1. **WHY + shape brief** (PM, `why-driven-decision`): WHY / 5 Whys, the 6 shape questions, on whose behalf it acts, who bears an error, never-do, approvals, a level HYPOTHESIS. Saved as `docs/prd/WHY-SHAPE-BRIEF-<feature>.md`.
2. **`/prd`:** `prd-research-aggregator` reads the Phase 0 research and the brief, and writes the research brief (alone, first).
3. **Fan-out, in ONE message, in parallel:** `prd-writer` (§1-§7, §8-§13), `aid:phase1-solution-shaper` (§1.5 + 20-30 seed eval cases), `aid:phase1-charter-drafter` (7A.1-7A.4), `aid:phase1-eval-planner` (7A.5-7A.8, §1.4 with guardrail). Each returns a draft and writes no files.
4. **Merge** into `docs/prd/YYYY-MM-DD-<feature>.md` (template `references/prd-template-extended.md`) and the seed cases into `docs/prd/SEED-EVALS-<feature>.md`. Report conflicts between drafts to the PM; never resolve them silently.
5. **PM review.**
6. **Shaping session:** PM + tech lead review the proposed level and the seed cases (optional time-boxed spike: run the lowest level against the seed cases; a human runs it OUTSIDE the AID project, never Claude in Phase 1 (adding the command to `extra_allowed_commands` weakens the phase gate and is only the human's call), uses de-identified seed cases only, uses a model provider setup approved for that data (7A.3), and its result is recorded in the ADR (`docs/prd/ADR-SHAPE-<feature>.md`)). The tech lead signs the level as an ADR, `docs/prd/ADR-SHAPE-<feature>.md` (the A1 decision).
7. **`prd-validator`** (independent gate check), then `/gate-check` and `/phase-approve` (human).

Seed cases come from real examples; expert-written cases are allowed, tagged `source: SME:<role>` and kept distinct from real examples. `INSUFFICIENT_EXAMPLES` must be resolved before the Phase 1 gate: by collecting real examples, by adding SME cases, or by a recorded PM + tech lead decision to proceed with fewer.
Timing: seed cases are written here; QA grows the golden set and held-out split in parallel with Phases 2-4 (it does not block the tech spec); complete only for the Phase 5 release gate.

## Solution-Shape Ladder (§1.5)

Levels: 0 process change (no software); 1 deterministic automation; 2 single LLM call inside a fixed flow; 3 workflow; 4 agent; 5 multi-agent. Pick the LOWEST level that works. The ladder table, the 6 intake questions and the four multi-agent justifications (separate permission boundaries; contexts that would contaminate each other; genuinely parallel work; ownership by different teams) live once, in `references/prd-template-extended.md` §1.5.

§7A ALWAYS applies. Depth follows three tiers: levels 0-1, 2-3 and 4-5. At levels 0-1 each section takes its classic form (Eval Plan → acceptance tests, Telemetry → logs/metrics, Rollout → staged release + rollback, Charter → the process owner and who bears an error). A section is still never "N/A", but at levels 0-1 it may be one line pointing to where it is already covered (e.g. "7A.6: covered by §4 Gherkin ACs + negative tests"; "7A.7: see §7 NFR observability"). Reviewers score that as fully met. Why-Chain rule: a WHY that yields no requirement, eval or metric is an opinion, not a requirement. Guidance and worked example: `SKILL.extended.md`.

### Decision rights (RACI)

| Item | Responsible | Accountable / decides |
|---|---|---|
| §1.5 Solution Shape level | PM proposes (from segment, pain, error cost) | Tech lead decides and signs (ADR) |
| §1.4 metrics, 7A.1 Charter, 7A.5 Why-Chain | PM | PM |
| 7A.2 Tools & Permissions, 7A.4 Failure Modes & Guardrails | Tech lead (input: security) | Tech lead |
| 7A.3 Context & Data | Tech lead (input: privacy/DPO) | Tech lead |
| 7A.6 Eval Plan | Data scientist (metrics, judge); QA (eval sets) | QA owns the release gate |
| 7A.7 Telemetry & Traces | Tech lead | Tech lead |
| 7A.8 Rollout & Kill Switch | Tech lead + named on-call owner | Tech lead |

## User Story Format

```markdown
### US-001: [Title]
**Research Backing**: [PROJECT]-A-INT-XXX OR ASSUMPTION - [rationale]

**As a** [role]
**I want** [capability]
**So that** [benefit]

**Priority:** [Must Have | Should Have | Could Have | Won't Have]
**Complexity:** [XS | S | M | L | XL]
```

## Acceptance Criteria (Gherkin - REQUIRED)

Save as: `features/[feature-area]/[story-slug].feature`

```gherkin
# Research: [PROJECT]-A-INT-XXX
# PRD: US-001
@[feature-tag] @[priority-tag]
Feature: [Story Title]
  """
  WHY: [Copy the "So that" benefit here]
  """

  As a [role]
  I want [capability]
  So that [benefit]

  Background:
    Given [shared preconditions for all scenarios]

  @smoke @happy-path
  Scenario: [Happy path - main success]
    Given [precondition/context]
    And [additional setup if needed]
    When [user action]
    Then [expected outcome]
    And [additional verification]

  @error-handling
  Scenario: [Error case - validation failure]
    Given [precondition]
    When [invalid action]
    Then [error handling]
    And [user guidance shown]

  @edge-case
  Scenario: [Edge case - boundary condition]
    Given [edge condition]
    When [action]
    Then [expected behavior at boundary]
```

## Common Pitfalls

| Pitfall | Fix |
|---|---|
| Implementation in requirements | Keep focused on outcomes |
| Untestable criteria | "Should load in <2s" not "be fast" |
| Missing error cases | Define what happens when things fail |
| Scope creep | Explicit acknowledgment for additions |
| Orphan requirements | Link to research or flag assumption |

## Phase Gate Checklist

### Document Quality
- [ ] PRD document complete
- [ ] User stories follow proper format
- [ ] Scope explicitly defined (in AND out)
- [ ] Dependencies identified
- [ ] Every requirement has research ID OR assumption flag
- [ ] Traceability matrix updated

### Agentic Design (always, scaled to level)
- [ ] §1.5 Solution Shape: 6 intake questions answered, level chosen, each step up justified
- [ ] §1.4 metric set has North Star, supporting and at least one guardrail metric
- [ ] §7A.1-7A.8 all filled at the depth of the level, none "N/A"
- [ ] WHY + shape brief, seed evals (20-30, or a cross-reference at levels 0-1), level signed by the tech lead (ADR)

### Acceptance Criteria (Gherkin) ⭐ REQUIRED
- [ ] Every user story has acceptance criteria in **Gherkin format**
- [ ] Feature files saved to `features/` directory
- [ ] Each story has at least 2 scenarios: happy path + error case
- [ ] All scenarios have appropriate @tags (@critical, @smoke, etc.)
- [ ] Research backing noted as comment in feature files
- [ ] `npm run cucumber:dry` passes (validates Gherkin syntax)

### Validation Command
```bash
npm run cucumber:dry   # Must pass before advancing to Phase 2
```

## PRD Template

Use the one template, `references/prd-template-extended.md`. Reviewers check its numbering: §1.4 Success Metrics (North Star / supporting / guardrail), §1.5 Solution Shape, §4 User Stories, §7 Non-Functional Requirements, and §7A Agentic Design with 7A.1 Charter, 7A.2 Tools & Permissions, 7A.3 Context & Data, 7A.4 Failure Modes & Guardrails, 7A.5 Why-Chain, 7A.6 Eval Plan, 7A.7 Telemetry & Traces, 7A.8 Rollout & Kill Switch.

## Role Guidance

| Role | Focus |
|---|---|
| PM | Own PRD, user stories, acceptance criteria, 7A.1 Charter, 7A.5 Why-Chain, metrics with guardrails; propose the §1.5 level |
| Dev | Review feasibility, identify edge cases |
| QA | Review testability, identify scenarios; own the 7A.6 release gate |
| Tech Lead | Validate fit, flag non-functionals; decide and sign the §1.5 level (ADR); own 7A.2-7A.4, 7A.7, 7A.8 |

## Handoff to Tech Spec

- Approved PRD
- Prioritized user stories
- Complete acceptance criteria
- Dependencies identified
- Traceability matrix
- §1.5 Solution Shape (level + justifications)
- §7A.1-7A.8 Agentic Design, filled for the chosen level
- Metric set with guardrail metrics (§1.4)
- WHY + shape brief: `docs/prd/WHY-SHAPE-BRIEF-<feature>.md`
- Seed evals: `docs/prd/SEED-EVALS-<feature>.md` (20-30 cases, or a cross-reference at levels 0-1)
- Signed level: the tech lead's ADR for the §1.5 level

Save to: `docs/prd/YYYY-MM-DD-<feature>.md` (the `/prd` merge)
