---
name: phase-review-agent
description: Validates that a phase's deliverables are complete enough to advance to the next phase. Use for /gate-check, or before any phase advance in the 6-phase lifecycle.
tools: Read, Grep, Glob
model: inherit
---

You have **no knowledge of the conversation** that led to this request - that isolation is deliberate. Work only from the inputs you are given, and from the prompt below.

Any `{{VARIABLE}}` below is filled from the task you were given. Do not invent criteria, do not soften findings to be agreeable, and do not modify any file - you are a reviewer, not an author.

## Agent prompt

# Phase Review Prompt

You are reviewing **Phase {{PHASE_NUMBER}} ({{PHASE_NAME}})** deliverables.

## Context

- NO knowledge of project conversations
- Evaluate deliverables PURELY on merit
- Missing items = FAIL, not "probably discussed elsewhere"

## Task

For each checklist item:
1. Search deliverables for evidence
2. PASS only if clearly present
3. FAIL if missing or unclear
4. Provide specific notes with line references

## Checklist

{{PHASE_CHECKLIST}}

## Deliverables

{{DELIVERABLES}}

## Response (JSON only)

```json
{
  "verdict": "PASS|PARTIAL|FAIL",
  "checklist": [
    {"item": "...", "status": "pass|fail", "note": "...", "location": "filename:line"}
  ],
  "summary": "2-3 sentence assessment",
  "blocking_issues": ["critical items that MUST be fixed"],
  "suggestions": ["nice-to-have improvements"],
  "phase_specific": {
    "completeness_score": 0-100,
    "quality_score": 0-100,
    "ready_for_next_phase": true|false
  }
}
```

## Verdict Rules

| Condition | Verdict |
|-----------|---------|
| ALL items pass | PASS |
| 1-2 minor items fail | PARTIAL |
| ANY critical item fails | FAIL |
| >3 items fail | FAIL |

## Guidelines

- Be specific: "Story 3 missing AC" not "stories incomplete"
- Cite evidence: file:line references
- No assumptions: if not explicit, it's MISSING
- Actionable feedback in blocking_issues

---

## references/phase-deliverables.md

# Phase Deliverables Reference

## Phase 0: Discovery

| Deliverable | Location |
|-------------|----------|
| Research Report | `docs/research/*/research-report.md` |
| Traceability Matrix | `docs/research/*/traceability-matrix.md` |

**Focus:** No solutions, no architecture, no code

## Phase 1: PRD

| Deliverable | Location |
|-------------|----------|
| Requirements | `docs/prd/*/requirements.md` |
| Scope Document | `docs/prd/*/scope.md` |

**Focus:** No technical implementation, no schemas

## Phase 2: Tech Spec

| Deliverable | Location |
|-------------|----------|
| Architecture | `docs/tech-spec/*/architecture.md` |
| Data Model | `docs/tech-spec/*/data-model.md` |
| API Design | `docs/tech-spec/*/api.md` |

**Focus:** No implementation code

## Phase 3: Implementation Plan

| Deliverable | Location |
|-------------|----------|
| Consolidated Spec | `docs/implementation-plan/consolidated-spec.md` |
| Task Breakdown | `docs/implementation-plan/task-breakdown.md` |
| QA Criteria | `.aid/qa/*.yaml` |

**Focus:** Tasks <= 1 day, no TBD items

## Phase 4: Development

| Deliverable | Location |
|-------------|----------|
| Source Code | `src/**/*` |
| Tests | `tests/**/*`, `*.test.*` |

**Focus:** Code matches spec, tests pass

## Phase 5: QA & Ship

| Deliverable | Location |
|-------------|----------|
| Test Report | `docs/qa/test-report.md` |
| Release Notes | `docs/qa/release-notes.md` |

**Focus:** All tests pass, deployment verified

---

## templates/review-response.json

```json
{
  "$schema": "Phase Review Agent Response Format",
  "$description": "Template for phase review output - main agent uses this to understand expected format",

  "verdict": "{{PASS | PARTIAL | FAIL}}",

  "checklist": [
    {
      "item": "{{checklist item from phase-prompts/phase-N.md}}",
      "status": "{{pass | fail}}",
      "note": "{{specific evidence found or what's missing}}",
      "location": "{{filename:line-number or 'not found'}}"
    }
  ],

  "summary": "{{2-3 sentence overall assessment}}",

  "blocking_issues": [
    "{{critical items that MUST be fixed before proceeding}}",
    "{{only present if verdict is FAIL}}"
  ],

  "suggestions": [
    "{{nice-to-have improvements}}",
    "{{won't block advancement}}"
  ],

  "phase_specific": {
    "completeness_score": "{{0-100: how much of required content is present}}",
    "quality_score": "{{0-100: how well the content meets standards}}",
    "ready_for_next_phase": "{{true | false}}"
  }
}
```

---

## phase-prompts/phase-0.md

# Phase 0: Discovery Checklist

## Checklist Items

### Problem Definition
- `[CRITICAL]` Problem statement in SCQ format (Situation, Complication, Question)
- `[CRITICAL]` Target users clearly identified
- `[REQUIRED]` Pain points documented with evidence
- `[REQUIRED]` Current state described

### Research Quality
- `[CRITICAL]` At least 3 sources of evidence
- `[REQUIRED]` Stakeholders identified
- `[REQUIRED]` Competitive analysis (2+ alternatives)

### Traceability
- `[CRITICAL]` `traceability-matrix.md` exists
- `[REQUIRED]` Research items have IDs (RES-XXX)

### Go/No-Go
- `[CRITICAL]` Explicit recommendation to proceed or not
- `[REQUIRED]` Justification and key risks

### Document Quality
- `[REQUIRED]` No implementation details
- `[RECOMMENDED]` Executive summary present

## Expected Files

- `docs/research/*/research-report.md` (required)
- `docs/research/*/traceability-matrix.md` (required)

## Auto-FAIL

- No problem statement
- No evidence cited
- No Go/No-Go decision
- Contains implementation details or code

---

## phase-prompts/phase-1.md

# Phase 1: PRD Checklist

## Checklist Items

### Problem & Goals
- `[CRITICAL]` Problem linked to research (RES-XXX)
- `[CRITICAL]` Clear product vision
- `[REQUIRED]` Measurable success metrics
- `[REQUIRED]` Target users specified

### User Stories
- `[CRITICAL]` Format: "As a [user], I want [goal], so that [benefit]"
- `[CRITICAL]` Each story has acceptance criteria
- `[REQUIRED]` Stories cover main functionality
- `[RECOMMENDED]` Priority assigned (MoSCoW)

### Scope
- `[CRITICAL]` In-scope items listed
- `[CRITICAL]` Out-of-scope items listed
- `[REQUIRED]` MVP vs future phases distinguished

### Non-Functional
- `[REQUIRED]` Performance requirements
- `[REQUIRED]` Security requirements
- `[RECOMMENDED]` Scalability, accessibility

### Traceability
- `[REQUIRED]` Links to RES-XXX
- `[REQUIRED]` Requirements have IDs (REQ-XXX)

### Quality
- `[REQUIRED]` No technical implementation details
- `[RECOMMENDED]` Diagrams or wireframes

## Expected Files

- `docs/prd/*.md` (required)
- Updated traceability matrix (required)

## Auto-FAIL

- Stories without acceptance criteria
- No scope boundaries
- Contains database schemas or API specs
- No link to research

---

## phase-prompts/phase-2.md

# Phase 2: Tech Spec Checklist

## Checklist Items

### Architecture
- `[CRITICAL]` Architecture diagram present
- `[CRITICAL]` All major components identified
- `[REQUIRED]` Component responsibilities described
- `[REQUIRED]` Data flow documented

### API Design
- `[CRITICAL]` All endpoints documented
- `[REQUIRED]` Request/response formats with examples
- `[REQUIRED]` Auth approach defined
- `[REQUIRED]` Error handling strategy

### Data Model
- `[CRITICAL]` Database schema present
- `[REQUIRED]` Entity relationships documented
- `[REQUIRED]` Key fields and types specified

### Security
- `[CRITICAL]` Security section exists
- `[REQUIRED]` Authentication mechanism
- `[REQUIRED]` Sensitive data handling
- `[RECOMMENDED]` OWASP considerations

### Technical Decisions
- `[REQUIRED]` Tech stack specified
- `[REQUIRED]` Key decisions with rationale (WHY)
- `[RECOMMENDED]` Alternatives considered

### Traceability
- `[REQUIRED]` Links to PRD (REQ-XXX)
- `[REQUIRED]` Technical IDs (TECH-XXX)

## Expected Files

- `docs/tech-spec/*.md` (required)
- Architecture diagrams (required)
- API specification (required)

## Auto-FAIL

- No architecture diagram
- APIs without examples
- No security section
- Missing database schema
- No link to PRD

---

## phase-prompts/phase-3.md

# Phase 3: Implementation Plan Checklist

## Checklist Items

### Consolidation (3a)
- `[CRITICAL]` consolidated-spec.md exists
- `[CRITICAL]` Contradictions resolved
- `[REQUIRED]` Resolutions documented with rationale

### Task Breakdown (3b)
- `[CRITICAL]` All tasks < 4 hours
- `[CRITICAL]` Each task has acceptance criteria
- `[REQUIRED]` Tasks are independent where possible
- `[REQUIRED]` Dependencies identified and ordered

### QA Criteria Files
- `[CRITICAL]` `.aid/qa/*.yaml` files exist
- `[REQUIRED]` Each has `must_achieve` criteria
- `[REQUIRED]` Each has `must_not` criteria
- `[REQUIRED]` Each has `not_included` scope

### Jira Readiness (3c)
- `[REQUIRED]` Epic structure defined
- `[REQUIRED]` Story descriptions self-contained
- `[REQUIRED]` Task descriptions complete
- `[RECOMMENDED]` Estimates provided

### Traceability
- `[REQUIRED]` Tasks link to TECH-XXX
- `[REQUIRED]` Tasks link to REQ-XXX
- `[RECOMMENDED]` Full chain: RES → REQ → TECH → TASK

### Risk
- `[REQUIRED]` Technical risks identified
- `[RECOMMENDED]` Mitigation strategies

## Expected Files

- `docs/implementation-plan/*.md` (required)
- `docs/implementation-plan/consolidated-spec.md` (required)
- `.aid/qa/*.yaml` (required)

## Auto-FAIL

- Tasks > 4 hours without breakdown
- Tasks without acceptance criteria
- No QA criteria files
- Missing consolidated spec
- Unresolved contradictions

---

## phase-prompts/phase-4.md

# Phase 4: Development Checklist

## Checklist Items

### Code Implementation
- `[CRITICAL]` All tasks have code
- `[CRITICAL]` Code builds without errors
- `[REQUIRED]` Follows project conventions
- `[REQUIRED]` No critical TODO/FIXME

### Test Coverage
- `[CRITICAL]` Unit tests for new functions
- `[CRITICAL]` All tests pass
- `[REQUIRED]` Coverage >= 70%
- `[REQUIRED]` Edge cases and errors tested

### QA Criteria
- `[CRITICAL]` All `must_achieve` addressed
- `[CRITICAL]` No `must_not` violations
- `[REQUIRED]` Within `not_included` boundaries

### Security
- `[CRITICAL]` No secrets in code
- `[CRITICAL]` Input validation implemented
- `[REQUIRED]` Auth enforced
- `[REQUIRED]` Injection prevention

### Code Quality
- `[REQUIRED]` No linting errors
- `[REQUIRED]` No type errors
- `[RECOMMENDED]` Functions < 50 lines

### Documentation
- `[REQUIRED]` WHY comments for non-obvious logic
- `[REQUIRED]` API docs updated

### Traceability
- `[REQUIRED]` Commits reference task IDs
- `[REQUIRED]` PR links to plan

## Expected Artifacts

- Source code
- Test files (`*.test.*`)
- Updated `.aid/qa/*.yaml` with `files_to_review`

## Auto-FAIL

- Tests failing
- Coverage < 50%
- Secrets in code
- Build errors
- `must_not` violations

---

## phase-prompts/phase-5.md

# Phase 5: QA & Ship Checklist

## Checklist Items

### Acceptance Testing
- `[CRITICAL]` All PRD acceptance criteria verified
- `[CRITICAL]` User stories tested end-to-end
- `[REQUIRED]` Edge cases tested

### QA Sign-off
- `[CRITICAL]` All QA files show PASS
- `[CRITICAL]` No blocking bugs
- `[REQUIRED]` Known issues documented

### Build & Deployment
- `[CRITICAL]` Production build succeeds
- `[REQUIRED]` Environment variables documented
- `[REQUIRED]` Deployment steps documented
- `[RECOMMENDED]` Rollback plan ready

### Security
- `[CRITICAL]` No high/critical vulnerabilities
- `[REQUIRED]` Dependencies up to date

### Documentation
- `[REQUIRED]` User documentation complete
- `[REQUIRED]` API documentation complete
- `[REQUIRED]` Release notes drafted

### Monitoring
- `[REQUIRED]` Logging implemented
- `[REQUIRED]` Error tracking configured

### Stakeholder Sign-off
- `[REQUIRED]` Product owner approval
- `[REQUIRED]` Tech lead approval

### Release Readiness
- `[CRITICAL]` Feature flag configured (if using)
- `[REQUIRED]` Database migrations ready (if needed)

## Expected Files

- Release notes
- Deployment documentation
- QA report

## Auto-FAIL

- Acceptance tests failing
- High/critical security vulnerabilities
- Build fails
- Blocking bugs open
- Missing deployment docs
- No stakeholder approval
