# AID Phase Gates System

## ⛔ CRITICAL RULE

**You CANNOT proceed to the next phase until ALL exit criteria are met.**

Claude Code MUST check `.aid/state.json` before any work and REFUSE to do work that belongs to a phase the project hasn't reached.

---

## Overview

```
Phase 1 ──► Gate ──► Phase 2 ──► Gate ──► Phase 3 ──► Gate ──► Phase 4 ──► Gate ──► Phase 5
  PRD        ✓      Tech Spec     ✓      Breakdown     ✓      Dev           ✓      QA & Ship
```

Each phase has:
- **Entry Criteria** - What must exist before starting
- **Required Work** - What happens in this phase
- **Exit Criteria** - What must be complete to proceed
- **Artifacts** - What files are produced

---

## Phase State Tracking

Every AID project has a state file at `.aid/state.json`:

```json
{
  "current_phase": 1,
  "phase_name": "PRD",
  "started_at": "2025-12-10T10:00:00Z",
  "phases": {
    "1": { "status": "in_progress", "started_at": "2025-12-10T10:00:00Z" },
    "2": { "status": "locked" },
    "3": { "status": "locked" },
    "4": { "status": "locked" },
    "5": { "status": "locked" }
  },
  "artifacts": {}
}
```

---

## The 5 Phases

### Phase 1: Raw → PRD

**Entry Criteria:**
- [ ] Raw input exists (notes, calls, ideas, requirements)
- [ ] Project folder initialized with `.aid/`

**Required Work:**
- Transform raw materials into structured PRD
- Define features, scope, priorities
- Create user stories with acceptance criteria

**Exit Criteria (ALL required):**
- [ ] `docs/PRD.md` exists
- [ ] PRD has: Problem Statement, User Stories, Acceptance Criteria, Out of Scope
- [ ] PRD approved (`.aid/approvals/prd-approved.md` exists)

**Artifacts:**
```
docs/PRD.md
.aid/approvals/prd-approved.md
```

---

### Phase 2: PRD → Tech Spec

**Entry Criteria:**
- [ ] Phase 1 complete (PRD approved)

**Required Work:**
- System architecture design
- Database schema
- API contracts
- Component breakdown
- TypeScript interfaces

**Exit Criteria (ALL required):**
- [ ] `docs/TECH-SPEC.md` exists
- [ ] Tech Spec has: Architecture, Data Models, API Endpoints, Components
- [ ] Tech Spec approved

**Artifacts:**
```
docs/TECH-SPEC.md
.aid/approvals/tech-spec-approved.md
```

---

### Phase 3: Tech Spec → Task Breakdown

**Entry Criteria:**
- [ ] Phase 2 complete (Tech Spec approved)
- [ ] Jira MCP configured (if using Jira)

**Required Work:**
- Create Epic(s) from Tech Spec
- Break down into Stories
- Define Tasks and Subtasks
- Add estimates

**Exit Criteria (ALL required):**
- [ ] Jira Epic(s) created (or `docs/TASK-BREAKDOWN.md`)
- [ ] All Stories have acceptance criteria
- [ ] All Tasks estimated
- [ ] Breakdown approved

**Artifacts:**
```
docs/JIRA-BREAKDOWN.md
.aid/approvals/breakdown-approved.md
```

---

### Phase 4: Development

**Entry Criteria:**
- [ ] Phase 3 complete (Breakdown approved)
- [ ] MCPs configured (Figma, Jira, etc.)

**Required Work:**
- Pick task from breakdown
- Write tests FIRST (TDD - mandatory)
- Implement feature
- Update status
- Update CLAUDE.md

**Exit Criteria (per task):**
- [ ] Tests written before implementation
- [ ] All tests pass
- [ ] Code reviewed

**Exit Criteria (phase complete):**
- [ ] All tasks complete
- [ ] All tests pass
- [ ] No critical issues

---

### Phase 5: QA & Ship

**Entry Criteria:**
- [ ] Phase 4 complete (all tasks done)
- [ ] All tests passing

**Required Work:**
- Full test suite execution
- Review against `test-review-checklist.md`
- Check for `anti-patterns.md` violations
- Documentation review
- Deployment preparation

**Exit Criteria:**
- [ ] Test coverage meets threshold (e.g., 80%)
- [ ] No anti-pattern violations
- [ ] Code review checklist complete
- [ ] Release notes created
- [ ] Deployment verified

**Artifacts:**
```
docs/RELEASE-NOTES.md
.aid/approvals/release-approved.md
```

---

## Enforcement Rules

### BLOCKED Actions by Phase

| Current Phase | ❌ BLOCKED | ✅ ALLOWED |
|---------------|-----------|-----------|
| 1 (PRD) | Code, Components, DB | Requirements, Scope |
| 2 (Tech Spec) | Code, Jira issues | + Architecture, Schemas |
| 3 (Breakdown) | Production code | + Jira, Planning |
| 4 (Development) | Deployment | + Code, Tests |
| 5 (QA) | - | Everything |

### Violation Response

When someone tries blocked work:

```
⛔ PHASE GATE VIOLATION

Current Phase: 2 (Tech Spec)
Requested Work: "Create a Button component"
This belongs to: Phase 4 (Development)

To proceed, complete:
  Phase 2: [✗] docs/TECH-SPEC.md missing
  Phase 3: [locked]
  Phase 4: [locked]

Run /phase for status, /gate-check to see requirements.
```

---

## Commands

| Command | Description |
|---------|-------------|
| `/aid-init` | Initialize new project with AID |
| `/phase` | Show current phase status |
| `/gate-check` | Check if ready to advance |
| `/phase-approve` | Human sign-off for current phase |
| `/phase-advance` | Move to next phase (if gates pass) |

---

## Quick Reference

### Starting a New Project
```
/aid-init
→ Creates .aid/ structure
→ Starts Phase 1 (PRD)
```

### Moving Through Phases
```
1. Do the work for current phase
2. /gate-check - verify requirements
3. /phase-approve - get human sign-off
4. /phase-advance - move to next phase
```

### Checking Status
```
/phase - Where am I? What's needed?
```
