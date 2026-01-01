---
name: phase-enforcement
description: AID methodology phase gate enforcement. Use this skill to ensure work follows the correct development phase order (PRD → Tech Spec → Implementation Plan → Development → QA). Enforces phase gates, validates transitions, and collects quality feedback. Essential for maintaining development discipline.
---

# Phase Enforcement Skill

Enforces AID phase gates with mandatory quality feedback collection. Claude MUST check current phase before any work, REFUSE work that belongs to a later phase, and collect feedback at phase completion for continuous improvement.

## PRIORITY 1: Phase Gate Enforcement

```
┌─────────────────────────────────────────────────────────────────┐
│  BEFORE ANY WORK, CLAUDE MUST:                                  │
│                                                                 │
│  1. Read `.aid/state.json` for current phase                    │
│  2. Classify the requested work                                 │
│  3. Check if work is allowed in current phase                   │
│  4. REFUSE if not allowed (show violation template)             │
│  5. At phase completion: MANDATORY SUB-AGENT REVIEW             │
│  6. After review passes: collect feedback via /aid end          │
└─────────────────────────────────────────────────────────────────┘
```

## MANDATORY: Sub-Agent Review at Phase Transitions

```
┌─────────────────────────────────────────────────────────────────┐
│  ⚠️  NO PHASE TRANSITION WITHOUT SUB-AGENT REVIEW               │
│                                                                 │
│  Before moving from Phase N to Phase N+1:                       │
│                                                                 │
│  1. Claude MUST spawn a review sub-agent using Task tool        │
│  2. Sub-agent reviews ALL deliverables for current phase        │
│  3. Sub-agent returns PASS/FAIL with detailed findings          │
│  4. If FAIL: Claude must address issues before retry            │
│  5. If PASS: Claude can proceed to collect feedback             │
│                                                                 │
│  THIS IS NOT OPTIONAL - CANNOT BE SKIPPED                       │
└─────────────────────────────────────────────────────────────────┘
```

### Sub-Agent Review Flow

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Phase N    │────▶│  Sub-Agent   │────▶│   Review     │
│  Complete    │     │   Review     │     │   Result     │
└──────────────┘     └──────────────┘     └──────┬───────┘
                                                 │
                          ┌──────────────────────┼──────────────────────┐
                          │                      │                      │
                          ▼                      ▼                      ▼
                    ┌──────────┐           ┌──────────┐          ┌──────────┐
                    │   PASS   │           │  PARTIAL │          │   FAIL   │
                    │          │           │          │          │          │
                    └────┬─────┘           └────┬─────┘          └────┬─────┘
                         │                      │                     │
                         ▼                      ▼                     ▼
                   ┌──────────┐          ┌──────────┐          ┌──────────┐
                   │ /aid end │          │  Fix &   │          │  Fix &   │
                   │ Feedback │          │  Re-run  │          │  Re-run  │
                   └──────────┘          └──────────┘          └──────────┘
```

### Sub-Agent Review Prompts by Phase

#### Phase 1 (PRD) → Phase 2 (Tech Spec) Review

```markdown
**SUB-AGENT TASK: PRD Review**

Review the PRD document at: [docs/prd/YYYY-MM-DD-feature.md]

**Checklist - ALL must pass:**
1. [ ] Problem statement is clear and specific
2. [ ] All user stories follow "As a... I want... So that..." format
3. [ ] Each user story has acceptance criteria
4. [ ] Non-functional requirements defined (performance, security, scalability)
5. [ ] Success metrics are measurable
6. [ ] Scope boundaries are explicit (what's in/out)
7. [ ] Stakeholders identified
8. [ ] No implementation details (that belongs in Tech Spec)

**Return Format:**
- PASS: All 8 items checked, ready for Tech Spec
- PARTIAL: [List items that need minor fixes]
- FAIL: [List critical missing items]

**Provide specific line references for any issues found.**
```

#### Phase 2 (Tech Spec) → Phase 3 (Implementation Plan) Review

```markdown
**SUB-AGENT TASK: Tech Spec Review**

Review the Tech Spec at: [docs/tech-spec/YYYY-MM-DD-feature.md]

**Checklist - ALL must pass:**
1. [ ] Architecture diagram exists (Mermaid or image)
2. [ ] All components and their responsibilities defined
3. [ ] Data models with TypeScript interfaces
4. [ ] API contracts (endpoints, request/response schemas)
5. [ ] Database schema with migrations
6. [ ] Security assessment complete:
   - Data classification (PUBLIC/INTERNAL/CONFIDENTIAL)
   - Authentication method specified
   - Authorization model documented
   - Encryption requirements defined
7. [ ] Error handling strategy documented
8. [ ] References PRD requirements (traceability)

**Return Format:**
- PASS: All 8 items checked, ready for Implementation Plan
- PARTIAL: [List items that need minor fixes]
- FAIL: [List critical missing items]

**Provide specific line references for any issues found.**
```

#### Phase 3 (Implementation Plan) → Phase 4 (Development) Review

```markdown
**SUB-AGENT TASK: Implementation Plan Review**

Review the Implementation Plan at: [docs/implementation-plan/YYYY-MM-DD-feature.md]

**Checklist - ALL must pass:**
1. [ ] Tasks broken down into actionable items (< 4 hours each)
2. [ ] Each task has clear acceptance criteria
3. [ ] Dependencies between tasks identified
4. [ ] Tasks ordered by dependency (critical path visible)
5. [ ] Test strategy defined:
   - Unit test scope
   - Integration test scope
   - E2E test scenarios (from user stories)
   - Coverage target (minimum 70%)
6. [ ] Risk assessment with mitigations
7. [ ] Each task maps back to Tech Spec components
8. [ ] Step-by-step implementation order is explicit

**CRITICAL: Implementation Plan must be step-by-step**
- Each step must be independently verifiable
- Steps must be in dependency order
- No step should require guessing previous work

**Return Format:**
- PASS: All 8 items checked, ready for Development
- PARTIAL: [List items that need minor fixes]
- FAIL: [List critical missing items]

**Provide specific task references for any issues found.**
```

#### Phase 4 (Development) → Phase 5 (QA & Ship) Review

```markdown
**SUB-AGENT TASK: Development Review**

Review the implementation against the Implementation Plan.

**Checklist - ALL must pass:**
1. [ ] All tasks in Implementation Plan marked complete
2. [ ] All tests written and passing
3. [ ] Test coverage >= 70%
4. [ ] No test-specific logic in production code
5. [ ] Code follows project standards (lint passes)
6. [ ] Build succeeds without errors
7. [ ] No critical security vulnerabilities (npm audit)
8. [ ] Documentation updated (README, API docs)
9. [ ] Code reviewed (PR approved or self-review documented)

**Run these commands and report results:**
- `npm test` or equivalent
- `npm run build` or equivalent
- `npm run lint` or equivalent
- Coverage report

**Return Format:**
- PASS: All 9 items checked, ready for QA & Ship
- PARTIAL: [List items that need minor fixes]
- FAIL: [List critical missing items]

**Provide specific file:line references for any issues found.**
```

### How to Invoke Sub-Agent Review

Claude MUST use the Task tool to spawn the review sub-agent:

```
Task tool invocation:
- subagent_type: "general-purpose"
- prompt: [Use appropriate review prompt from above]
- description: "Phase [N] gate review"
```

### Review Result Handling

**On PASS:**
```
✅ SUB-AGENT REVIEW PASSED

Phase: [N] [Phase Name]
Reviewed: [document/code path]
Result: PASS

All gate requirements verified. Proceeding to feedback collection.

Run: /aid end
```

**On PARTIAL:**
```
⚠️ SUB-AGENT REVIEW: PARTIAL PASS

Phase: [N] [Phase Name]
Reviewed: [document/code path]
Result: PARTIAL

Minor issues found:
1. [Issue 1 with location]
2. [Issue 2 with location]

Fix these issues and re-run review, or override with:
"override: [reason]"
```

**On FAIL:**
```
❌ SUB-AGENT REVIEW FAILED

Phase: [N] [Phase Name]
Reviewed: [document/code path]
Result: FAIL

Critical issues found:
1. [Critical issue 1 with location]
2. [Critical issue 2 with location]

These MUST be fixed before phase transition.
Cannot override critical failures.
```

## Phase Structure

### 5-Phase Development Lifecycle

| Phase | Name | Document Output | Folder |
|-------|------|-----------------|--------|
| 1 | PRD | Product Requirements | `docs/prd/` |
| 2 | Tech Spec | Technical Specification | `docs/tech-spec/` |
| 3 | Implementation Plan | Task Breakdown | `docs/implementation-plan/` |
| 4 | Development | Code & Tests | `src/`, `testing/` |
| 5 | QA & Ship | Deployment & Release | Production |

### Document Naming Convention

All documents follow: `YYYY-MM-DD-[feature-name].md`

```
docs/
├── prd/
│   └── 2024-12-11-user-authentication.md
├── tech-spec/
│   └── 2024-12-12-user-authentication.md
└── implementation-plan/
    └── 2024-12-13-user-authentication.md
```

## Work Classification

| Category | Examples | First Allowed | Gate Document |
|----------|----------|---------------|---------------|
| `requirements` | PRD, user stories, scope | Phase 1 | `docs/prd/` |
| `architecture` | System design, DB schema, APIs | Phase 2 | `docs/tech-spec/` |
| `planning` | Jira issues, task breakdown | Phase 3 | `docs/implementation-plan/` |
| `coding` | Components, features, tests | Phase 4 | Source code |
| `qa` | Testing review, deployment | Phase 5 | Release |

## Phase Permissions

```javascript
const PHASE_ALLOWED = {
  1: ["requirements"],
  2: ["requirements", "architecture"],
  3: ["requirements", "architecture", "planning"],
  4: ["requirements", "architecture", "planning", "coding"],
  5: ["requirements", "architecture", "planning", "coding", "qa"],
};

const PHASE_OUTPUT_FOLDERS = {
  1: "docs/prd/",
  2: "docs/tech-spec/",
  3: "docs/implementation-plan/",
  4: "src/",
  5: "deployment/",
};
```

## Detection Patterns

### Phase 1 Work (requirements)
- "create PRD", "write requirements", "define scope"
- "user stories", "acceptance criteria", "feature definition"

### Phase 2 Work (architecture)
- "design architecture", "create schema", "define API"
- "tech spec", "data model", "component design", "security architecture"

### Phase 3 Work (planning)
- "create epic", "jira", "break down", "implementation plan"
- "tasks", "estimate", "sprint", "phase breakdown"

### Phase 4 Work (coding)
- "create component", "implement", "write code"
- "build", "create file", "write tests"

### Phase 5 Work (qa)
- "deploy", "release", "ship"
- "review coverage", "performance test", "production"

## PRIORITY 2: Quality Feedback Integration

```
┌─────────────────────────────────────────────────────────────────┐
│  MANDATORY FEEDBACK COLLECTION                                  │
│                                                                 │
│  At EVERY phase completion:                                     │
│  1. Run /aid end to collect user feedback                       │
│  2. Rating (1-5) + What worked + What to improve                │
│  3. Save to ~/.aid/feedback/pending/                            │
│  4. Use feedback in /aid improve for skill enhancement          │
└─────────────────────────────────────────────────────────────────┘
```

### Quality Feedback Flow

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Phase N    │────▶│   /aid end   │────▶│   Feedback   │
│  Complete    │     │   (Rating)   │     │    Stored    │
└──────────────┘     └──────────────┘     └──────┬───────┘
                                                 │
                                                 ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│    Skill     │◀────│ /aid improve │◀────│   3+ Items   │
│   Updated    │     │  (Analysis)  │     │   Pending    │
└──────────────┘     └──────────────┘     └──────────────┘
```

### Feedback Schema

```json
{
  "timestamp": "2024-12-11T12:00:00Z",
  "phase": 2,
  "phase_name": "tech-spec",
  "rating": 4,
  "worked_well": "Security architecture well documented",
  "to_improve": "Need more detail on error handling",
  "document_path": "docs/tech-spec/2024-12-11-user-auth.md",
  "duration_minutes": 120
}
```

## Gate Check Requirements

### Phase 1 → Phase 2 Gate
- [ ] PRD exists in `docs/prd/YYYY-MM-DD-[feature].md`
- [ ] All user stories defined
- [ ] Acceptance criteria complete
- [ ] **⚠️ SUB-AGENT REVIEW PASSED** (mandatory)
- [ ] **Feedback collected** via `/aid end`

### Phase 2 → Phase 3 Gate
- [ ] Tech Spec exists in `docs/tech-spec/YYYY-MM-DD-[feature].md`
- [ ] Architecture diagram included
- [ ] API contracts defined
- [ ] Security assessment complete
- [ ] **⚠️ SUB-AGENT REVIEW PASSED** (mandatory)
- [ ] **Feedback collected** via `/aid end`

### Phase 3 → Phase 4 Gate
- [ ] Implementation Plan in `docs/implementation-plan/YYYY-MM-DD-[feature].md`
- [ ] Tasks broken down with effort estimates
- [ ] Dependencies identified
- [ ] Test strategy defined
- [ ] **Step-by-step implementation order explicit**
- [ ] **⚠️ SUB-AGENT REVIEW PASSED** (mandatory)
- [ ] **Feedback collected** via `/aid end`

### Phase 4 → Phase 5 Gate
- [ ] All code implemented
- [ ] Tests passing
- [ ] Coverage meets threshold
- [ ] Code reviewed
- [ ] **⚠️ SUB-AGENT REVIEW PASSED** (mandatory)
- [ ] **Feedback collected** via `/aid end`

## Violation Template

```
⛔ PHASE GATE VIOLATION

Current Phase: [N] [Phase Name]
Requested: [What user asked for]
Category: [Category]

This work belongs to Phase [X] ([Phase Name]).

Complete these phases first:
[List incomplete phases with their requirements]

Documents required:
- Phase [N]: docs/[folder]/YYYY-MM-DD-[feature].md

Commands:
  /phase        - See current status
  /gate-check   - See what's needed
  /aid end      - Complete current phase with feedback
```

## Phase Completion Template

```
✅ PHASE [N] COMPLETE: [Phase Name]

Deliverables:
- [Document/Output created]
- Location: [path]

⚠️ MANDATORY: Sub-Agent Review Required

Before advancing to Phase [N+1], Claude must:
1. Spawn review sub-agent to validate deliverables
2. Address any issues found
3. Collect feedback via /aid end

This ensures quality gates are enforced.
```

## Exceptions

### Always Allowed
- Reading/viewing files (exploration)
- Documentation updates (non-phase docs)
- Answering questions
- Running `/phase`, `/gate-check`, `/aid end`, `/aid improve`

### With Warning
- Fixing earlier phase artifacts (show warning but allow)
- Updating documents from completed phases

### Override
- User can say "override: [reason]"
- Log override in `.aid/overrides.log`
- Override does NOT skip feedback requirement
- **Override does NOT skip sub-agent review for critical failures**

## Skill Integration

This skill coordinates with other skills based on phase:

| Skill | Available From | Gate Requirement |
|-------|----------------|------------------|
| `system-architect` | Phase 2+ | PRD approved + sub-agent review passed |
| `atomic-design` | Phase 4+ | Tech Spec approved + sub-agent review passed |
| `code-review` | Phase 4+ | Implementation Plan approved + sub-agent review passed |
| `test-driven` | Phase 4+ | Implementation Plan approved + sub-agent review passed |

## State Management

### `.aid/state.json`

```json
{
  "current_phase": 2,
  "phase_name": "tech-spec",
  "feature_name": "user-authentication",
  "started_at": "2024-12-11T10:00:00Z",
  "phases_completed": [1],
  "documents": {
    "prd": "docs/prd/2024-12-11-user-authentication.md",
    "tech_spec": null,
    "implementation_plan": null
  },
  "feedback_collected": {
    "phase_1": true,
    "phase_2": false
  },
  "subagent_review": {
    "phase_1": {"status": "passed", "timestamp": "2024-12-11T09:00:00Z"},
    "phase_2": {"status": "pending"}
  }
}
```

## Commands Reference

| Command | Purpose | Phase |
|---------|---------|-------|
| `/phase` | Show current phase status | Any |
| `/gate-check` | Check gate requirements | Any |
| `/phase approve` | Approve phase advancement | End of phase |
| `/aid end` | Complete phase with feedback | End of phase (after sub-agent review) |
| `/aid improve` | Run improvement analysis | Any (3+ feedback) |
