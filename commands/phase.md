---
description: "Show current AID phase and its status"
---

# /phase Command

Show the current AID phase, what it allows, and what it takes to move on.

`/phase` is read-only. It never changes the phase.

## Usage

```
/phase
```

## Where the Phase Comes From

The current phase is read from the project's `.aid/state.json` (`current_phase`, with
`phase_name` and the role-specific `phase_display`). If the file does not exist, the
project has not been initialized: suggest `/aid-init` or `/aid-start`.

Reading `.aid/state.json` is fine. Never write it: only `hooks/aid_session.py` writes it,
and the phase gates refuse any direct edit.

## Changing the Phase

The phase changes only through the gate commands, in this order:

1. `/gate-check` - check whether the current phase's deliverables are complete (read-only)
2. `/phase-approve` - human sign-off for the current phase
3. `/phase-advance` - move to the next phase

There is no way to jump to a phase with `/phase <number>`.

## Phases

AID has six phases, numbered 0-5. Names follow `references/role-phase-terminology.json`:
the first column is the phase's base name, the others are what each role sees.

| Phase | Name | Product Manager | Tech Lead | Developer | QA Engineer | Data Scientist |
|-------|------|-----------------|-----------|-----------|-------------|----------------|
| 0 | Discovery | Market & Competitive Research | Technology & Architecture Research | Technical Spike & Research | Test Strategy Research | EDA — Data Gathering & Analysis |
| 1 | PRD | Product Requirements (PRD) | Technical Requirements Report | Feature Specification | Test Requirements & Coverage Plan | Feasibility Assessment |
| 2 | Tech Spec | Solution Review | System Architecture Design | Technical Design | Test Architecture & Framework | Experiment Planning |
| 3 | Implementation Plan | Roadmap & Prioritization | Sprint Planning & Task Breakdown | Task Breakdown & Estimation | Test Plan & Case Design | ML Arch & Pipeline Design & Breakdown |
| 4 | Development | Feature Validation & UAT | Code Review & Architecture Oversight | Implementation & Coding | Test Execution & Automation | Development & Validation |
| 5 | QA & Ship | Launch & Post-Launch | Release Engineering & Deployment | Bug Fixes & Polish | Release Certification & Sign-off | Deploy to Production & Monitoring |

```
Phase 0 ──► Phase 1 ──► Phase 2 ──► Phase 3 ──► Phase 4 ──► Phase 5
Discovery     PRD      Tech Spec   Impl Plan     Dev       QA & Ship
```

## Phase Details

### Phase 0: Discovery
**Goal:** Validate that the problem is worth solving

**Allowed:** Research, stakeholders, competitive analysis

**Output:** `docs/research/` (research report, traceability matrix)

**Command:** `/discovery`

---

### Phase 1: PRD
**Goal:** Define what we build and why

**Allowed:** + Requirements, scope, user stories, Gherkin acceptance criteria

**Output:** `docs/prd/`

**Command:** `/prd`

---

### Phase 2: Tech Spec
**Goal:** Design the technical solution

**Allowed:** + Architecture, schemas, APIs

**Output:** `docs/tech-spec/`

**Command:** `/tech-spec`

---

### Phase 3: Implementation Plan
**Goal:** Turn the specs into actionable work

**Allowed:** + Consolidation of PRD and Tech Spec (3a), task breakdown and sprint
planning (3b), Jira epics, stories and tasks (3c)

**Output:** `docs/implementation-plan/`, Jira issues

**Command:** `/jira-breakdown`

---

### Phase 4: Development
**Goal:** Implement the planned tasks, tests first

**Allowed:** + Code, tests, components

**Commands:** `/pipeline`, `/write-tests`, `/code-review`, `/test-review`

---

### Phase 5: QA & Ship
**Goal:** Validate and release

**Allowed:** Everything

**Command:** `/qa-ship`

## Example Output

```
Current phase: 2 - Tech Spec (Solution Review)
Role: Product Manager
Source: .aid/state.json

Allowed now: architecture, schemas, APIs
Blocked until later: code (Phase 4), Jira issues (Phase 3)

Next: /gate-check, then /phase-approve, then /phase-advance
```

## Related Commands

- `/gate-check` - check readiness to advance
- `/phase-approve` - approve the current phase
- `/phase-advance` - move to the next phase
- `/aid-status` - phase and session state
