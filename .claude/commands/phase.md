# /phase Command

Show current phase status and navigate the AID 6-phase development lifecycle.

## Usage

```
/phase              # Show current phase status
/phase <number>     # Navigate to specific phase (0-5)
```

## 6-Phase Lifecycle

```
    Phase 0         Phase 1       Phase 2        Phase 3        Phase 4       Phase 5
  ┌───────────┐   ┌─────────┐   ┌──────────┐   ┌──────────┐   ┌─────────┐   ┌─────────┐
  │ DISCOVERY │──▶│   PRD   │──▶│ Tech Spec│──▶│Impl Plan │──▶│   Dev   │──▶│QA & Ship│
  │           │   │         │   │          │   │          │   │         │   │         │
  │ Research  │   │ Require-│   │ Architec-│   │ Task     │   │ Code &  │   │ Deploy &│
  │ Validate  │   │ ments   │   │ ture     │   │ Breakdown│   │ Tests   │   │ Release │
  └───────────┘   └─────────┘   └──────────┘   └──────────┘   └─────────┘   └─────────┘
```

## Phase Overview

| Phase | Name | Description | Output Folder |
|-------|------|-------------|---------------|
| 0 | Discovery | Research, validate problem, stakeholders | `docs/research/` |
| 1 | PRD | Product Requirements Document | `docs/prd/` |
| 2 | Tech Spec | Technical Specification | `docs/tech-spec/` |
| 3 | Implementation Plan | Task breakdown, estimates | `docs/implementation-plan/` |
| 4 | Development | Code & Tests (TDD) | `src/`, `testing/` |
| 5 | QA & Ship | Testing, review, deployment | Production |

## Examples

```bash
# Show current phase status
/phase

# Start Discovery phase
/phase 0

# Jump to Development (if previous phases complete)
/phase 4
```

## Phase Details

### Phase 0: Discovery
**Goal:** Validate problem space and gather research insights

**Activities:**
- Problem analysis (5 Whys, Problem Severity)
- Stakeholder research (Interviews, Power/Interest Matrix)
- Market & competitive research (JTBD, Competitive Analysis)
- Root cause investigation
- Strategic positioning

**Output:** `docs/research/YYYY-MM-DD-[project]/`
- `research-report.md`
- `traceability-matrix.md`
- `stakeholder-map.png` (via Nano Banana Pro)

**Command:** `/discovery`

**Skills:** `pre-prd-research`, `aid-discovery`, `nano-banana-visual`

---

### Phase 1: PRD Creation
**Goal:** Document product requirements

**Activities:**
- Define user stories (linked to research IDs)
- Specify acceptance criteria
- Define success metrics
- Define MVP scope

**Output:** `docs/prd/YYYY-MM-DD-[feature].md`

**Command:** `/prd`

**Skill:** `aid-prd`

---

### Phase 2: Technical Specification
**Goal:** Design technical solution

**Activities:**
- Database schema design
- API endpoint definitions
- Component architecture
- Security architecture (ISO 27001)
- TypeScript interfaces

**Output:** `docs/tech-spec/YYYY-MM-DD-[feature].md`

**Command:** `/tech-spec`

**Skill:** `system-architect`

---

### Phase 3: Implementation Plan
**Goal:** Create actionable task breakdown

**Activities:**
- Break into tasks (< 4 hours each)
- Define acceptance criteria per task
- Map dependencies
- Create Jira epics/stories/tasks
- Define test strategy

**Output:** `docs/implementation-plan/YYYY-MM-DD-[feature].md`

**Command:** `/jira-breakdown`

---

### Phase 4: Development
**Goal:** Implement features with TDD

**Activities:**
- TDD: Write tests first
- Implement components (atoms → pages)
- API development
- Database migrations
- Code review

**Skills:**
- `atomic-design` - Component development
- `atomic-page-builder` - Page composition
- `test-driven` - TDD methodology
- `code-review` - Code quality

---

### Phase 5: QA & Ship
**Goal:** Validate and deploy

**Activities:**
- Acceptance testing
- E2E tests with Puppeteer
- Performance testing
- Security review
- Deployment
- Monitoring

**Command:** `/qa-ship`

## Gate Requirements

Each phase has exit criteria that must pass before advancing:

| Transition | Key Gate Requirements |
|------------|----------------------|
| 0 → 1 | Research report, traceability matrix, Go/No-Go decision |
| 1 → 2 | PRD complete, user stories with acceptance criteria |
| 2 → 3 | Architecture diagram, API contracts, security assessment |
| 3 → 4 | Tasks broken down, dependencies mapped, test strategy |
| 4 → 5 | All code implemented, tests passing, coverage ≥ 70% |

Use `/gate-check` to see detailed requirements.

## Sub-Agent Review

**MANDATORY**: Before any phase transition, Claude spawns a review sub-agent to validate deliverables. This cannot be skipped.

```
Phase N Complete → Sub-Agent Review → PASS/FAIL → Feedback Collection → Phase N+1
```

## Related Commands

| Command | Purpose |
|---------|---------|
| `/discovery` | Start Phase 0 research |
| `/prd` | Create PRD (Phase 1) |
| `/tech-spec` | Create Tech Spec (Phase 2) |
| `/jira-breakdown` | Create Implementation Plan (Phase 3) |
| `/code-review` | Review code (Phase 4-5) |
| `/qa-ship` | QA and deployment (Phase 5) |
| `/gate-check` | Check gate requirements |
| `/phase-advance` | Move to next phase |
| `/aid end` | Complete current phase with feedback |

## Tips

- Start at Phase 0 (Discovery) for new projects
- Complete each phase before moving to the next
- Document decisions in gate documents
- Use `/gate-check` frequently to track progress
- Sub-agent review is mandatory at phase transitions
