---
name: phase-enforcement
description: AID methodology phase gate enforcement. Ensures work follows correct phase order (PRD -> Tech Spec -> Impl Plan -> Dev -> QA). Enforces gates, validates transitions.
---

# Phase Enforcement Skill

Claude MUST check current phase before any work, REFUSE work that belongs to later phase.

## Priority 1: Phase Gate Enforcement

Before any work:
1. Read `.aid/state.json` for current phase
2. Classify the requested work
3. Check if work is allowed
4. REFUSE if not allowed (show violation)
5. At phase completion: mandatory sub-agent review
6. After review passes: collect feedback via /aid end

## Mandatory: Sub-Agent Review at Transitions

Before Phase N -> N+1:
1. Spawn review sub-agent
2. Sub-agent reviews all deliverables
3. Returns PASS/FAIL with findings
4. FAIL: Address issues, retry
5. PASS: Proceed to feedback

## 5-Phase Development Lifecycle

| Phase | Name | Document | Folder |
|-------|------|----------|--------|
| 1 | PRD | Product Requirements | docs/prd/ |
| 2 | Tech Spec | Technical Specification | docs/tech-spec/ |
| 3 | Impl Plan | Task Breakdown | docs/implementation-plan/ |
| 4 | Development | Code & Tests | src/ |
| 5 | QA & Ship | Deployment | Production |

## Work Classification

| Category | Examples | First Allowed |
|----------|----------|---------------|
| requirements | PRD, user stories | Phase 1 |
| architecture | System design, APIs | Phase 2 |
| planning | Jira, task breakdown | Phase 3 |
| coding | Components, tests | Phase 4 |
| qa | Testing, deployment | Phase 5 |

## Phase Permissions

- Phase 1: requirements
- Phase 2: requirements, architecture
- Phase 3: requirements, architecture, planning
- Phase 4: requirements, architecture, planning, coding
- Phase 5: all

## Gate Check Requirements

### Phase 1 -> 2
- [ ] PRD exists in docs/prd/
- [ ] User stories defined
- [ ] Acceptance criteria complete
- [ ] Sub-agent review PASSED

### Phase 2 -> 3
- [ ] Tech Spec exists
- [ ] Architecture diagram
- [ ] API contracts
- [ ] Security assessment
- [ ] Sub-agent review PASSED

### Phase 3 -> 4
- [ ] Implementation Plan exists
- [ ] Tasks broken down
- [ ] Dependencies identified
- [ ] Test strategy defined
- [ ] Sub-agent review PASSED

### Phase 4 -> 5
- [ ] Code implemented
- [ ] Tests passing
- [ ] Coverage meets threshold
- [ ] Sub-agent review PASSED

## Violation Template

```
PHASE GATE VIOLATION

Current Phase: [N] [Name]
Requested: [What]
Category: [Category]

This work belongs to Phase [X].

Complete first: [List]

Commands: /phase, /gate-check, /aid end
```

## Sub-Agent Review Prompts

### PRD Review (Phase 1 -> 2)
- [ ] Problem statement clear
- [ ] User stories As/I want/So that
- [ ] Acceptance criteria per story
- [ ] Non-functional requirements
- [ ] Measurable success metrics
- [ ] No implementation details

### Tech Spec Review (Phase 2 -> 3)
- [ ] Architecture diagram
- [ ] Components defined
- [ ] Data models (TypeScript)
- [ ] API contracts
- [ ] Database schema
- [ ] Security assessment
- [ ] References PRD

### Impl Plan Review (Phase 3 -> 4)

**Phase 3 Golden Rules:**
1. NO WORD LEFT BEHIND - PRD → Epic/Story, Tech Spec → Task
2. SMALL TASKS - Larger docs = smaller tasks
3. PROCESS IN CHUNKS - Read → Write immediately
4. VERIFY - 100% coverage required

**Sub-Phases:** 3a Consolidation → 3b Breakdown → 3c Enrichment → 3d Jira → 3e Verification

**Checklist:**
- [ ] Contradiction log created
- [ ] Source documents fixed
- [ ] Consolidated spec created
- [ ] Hierarchy: Epic → Story → Task
- [ ] Tasks sized appropriately
- [ ] All 8 required fields per Task
- [ ] 100% PRD/Tech Spec coverage
- [ ] Enriched files staged
- [ ] Jira populated with ADF

### Development Review (Phase 4 -> 5)
- [ ] All tasks complete
- [ ] Tests passing
- [ ] Coverage >= 70%
- [ ] Lint passes
- [ ] Build succeeds
- [ ] No critical vulnerabilities

## Exceptions

**Always Allowed:** Reading files, documentation updates, questions, /phase, /gate-check

**Override:** User says "override: [reason]" - logged to .aid/overrides.log

## State File

`.aid/state.json`:
```json
{
  "current_phase": 2,
  "phase_name": "tech-spec",
  "feature_name": "user-auth",
  "phases_completed": [1],
  "subagent_review": {"phase_1": {"status": "passed"}}
}
```
