# Phase Gates Reference

Detailed requirements for each phase gate in the AID methodology.

---

## Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    PHASE GATE STRUCTURE                         │
│                                                                 │
│  Phase 1 ──▶ Gate 1 ──▶ Phase 2 ──▶ Gate 2 ──▶ Phase 3         │
│    PRD         │        Tech        │        Impl               │
│                │        Spec        │        Plan               │
│                │                    │                           │
│                ▼                    ▼                           │
│           Feedback             Feedback                         │
│           Required             Required                         │
│                                                                 │
│  Phase 3 ──▶ Gate 3 ──▶ Phase 4 ──▶ Gate 4 ──▶ Phase 5         │
│   Impl         │         Dev        │         QA &              │
│   Plan         │                    │         Ship              │
│                ▼                    ▼                           │
│           Feedback             Feedback                         │
│           Required             Required                         │
└─────────────────────────────────────────────────────────────────┘
```

---

## Gate 1: PRD → Tech Spec

### Entry Criteria
- Feature request received from user
- Scope clearly defined

### Exit Criteria (Mandatory)

| Requirement | Location | Validation |
|-------------|----------|------------|
| PRD Document | `docs/prd/YYYY-MM-DD-[feature].md` | File exists |
| Problem Statement | PRD Section 1 | Not empty |
| User Stories | PRD Section 2 | At least 1 story |
| Acceptance Criteria | PRD Section 3 | Each story has criteria |
| Non-Functional Requirements | PRD Section 4 | Defined |
| **Feedback Collected** | `~/.aid/feedback/pending/` | `/aid end` completed |

### Gate Check Script

```javascript
function checkGate1(state, feedback) {
  const checks = {
    prdExists: fs.existsSync(state.documents.prd),
    prdValid: validatePRDContent(state.documents.prd),
    feedbackCollected: feedback.phase_1 === true,
  };

  return Object.values(checks).every(v => v === true);
}
```

### Blocked Message

```
⛔ GATE 1 NOT PASSED

Cannot proceed to Phase 2 (Tech Spec) until:

□ PRD document created
  → Run: /prd [feature-name]
  → Save to: docs/prd/YYYY-MM-DD-[feature].md

□ Feedback collected
  → Run: /aid end
  → Rate the PRD quality (1-5)

Commands:
  /gate-check  - See detailed status
  /prd         - Create PRD document
  /aid end     - Complete phase with feedback
```

---

## Gate 2: Tech Spec → Implementation Plan

### Entry Criteria
- Gate 1 passed
- PRD approved by stakeholder

### Exit Criteria (Mandatory)

| Requirement | Location | Validation |
|-------------|----------|------------|
| Tech Spec Document | `docs/tech-spec/YYYY-MM-DD-[feature].md` | File exists |
| Architecture Diagram | Tech Spec Section 3 | Mermaid diagram present |
| Data Models | Tech Spec Section 4 | TypeScript interfaces |
| API Specification | Tech Spec Section 5 | Endpoints defined |
| Security Assessment | Tech Spec Section 2 | Threat model, classification |
| Database Schema | Tech Spec Section 6 | SQL migrations |
| **Feedback Collected** | `~/.aid/feedback/pending/` | `/aid end` completed |

### Security Gate Requirements

```
┌─────────────────────────────────────────────────────────────────┐
│  SECURITY GATE CHECKS (Mandatory for Gate 2)                    │
│                                                                 │
│  □ Data Classification defined (PUBLIC/INTERNAL/CONFIDENTIAL)   │
│  □ Authentication method specified (OAuth2/JWT/API Keys)        │
│  □ Authorization model documented (RBAC/ABAC)                   │
│  □ Encryption requirements (TLS, at-rest, field-level)         │
│  □ Audit logging requirements identified                        │
└─────────────────────────────────────────────────────────────────┘
```

### Gate Check Script

```javascript
function checkGate2(state, feedback) {
  const techSpec = state.documents.tech_spec;

  const checks = {
    techSpecExists: fs.existsSync(techSpec),
    hasArchitecture: contentIncludes(techSpec, 'mermaid'),
    hasDataModels: contentIncludes(techSpec, 'interface'),
    hasAPISpec: contentIncludes(techSpec, 'Endpoint'),
    hasSecurity: contentIncludes(techSpec, 'Security'),
    feedbackCollected: feedback.phase_2 === true,
  };

  return Object.values(checks).every(v => v === true);
}
```

---

## Gate 3: Implementation Plan → Development

### Entry Criteria
- Gate 2 passed
- Tech Spec approved
- Resources allocated

### ⚠️ PHASE 3 GOLDEN RULES

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                          │
│   GOLDEN RULE #1: NO WORD LEFT BEHIND                                   │
│   Every word in PRD → appears in Epic or Story                          │
│   Every word in Tech Spec → appears in Task                             │
│   If it's not in Jira, it won't get built.                             │
│                                                                          │
│   GOLDEN RULE #2: SMALL TASKS, BIG DOCUMENTS                            │
│   >100 pages source = XS tasks (1-2 hours each)                        │
│   50-100 pages source = S tasks (2-4 hours each)                       │
│   Small tasks = more checkboxes = nothing lost.                        │
│                                                                          │
│   GOLDEN RULE #3: PROCESS IN CHUNKS, WRITE IMMEDIATELY                  │
│   Read section → Write to enriched file → Next section                  │
│   Don't hold it in memory. Write as you go.                            │
│                                                                          │
│   GOLDEN RULE #4: VERIFY BEFORE PROCEEDING                              │
│   100% PRD coverage or NO PROCEED                                       │
│   100% Tech Spec coverage or NO PROCEED                                │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Phase 3 Sub-Phases (All Required)

```
┌─────────────────────────────────────────────────────────────────────────┐
│  Phase 3a: CONTRADICTION RESOLUTION & CONSOLIDATION                     │
│  ─────────────────────────────────────────────────                      │
│  • Find contradictions FIRST (before consolidating)                     │
│  • Compare PRD and Tech Spec section-by-section                        │
│  • Log each contradiction with resolution rationale                     │
│  • Fix SOURCE documents (not Jira tasks!)                              │
│  • Then create consolidated spec                                        │
│                                                                          │
│  Output: contradiction-log.md, 00-consolidated-spec.md                  │
├─────────────────────────────────────────────────────────────────────────┤
│  Phase 3b: TASK BREAKDOWN                                               │
│  ────────────────────────                                               │
│  • Create Epic → Story → Task hierarchy (NEVER skip Story!)            │
│  • Apply templates from aid-impl-plan/references/templates/            │
│  • Stage in enriched-jiras/*.md files                                  │
│                                                                          │
│  Output: 01-task-breakdown.md, EPIC-N-enriched.md files                │
├─────────────────────────────────────────────────────────────────────────┤
│  Phase 3c: SUCCESS CRITERIA GENERATION (QA Gate Setup) ◄── NEW         │
│  ────────────────────────────────────────────────────                   │
│  • Generate acceptance criteria for each task                          │
│  • Apply Iron Rules (no tech spec in criteria)                         │
│  • Create .aid/qa/{task-id}.yaml files                                 │
│  • MUST ACHIEVE, MUST NOT, NOT INCLUDED per task                       │
│  • Human batch review before proceeding                                │
│                                                                          │
│  Output: .aid/qa/*.yaml files for QA sub-agent                         │
├─────────────────────────────────────────────────────────────────────────┤
│  Phase 3d: ENRICHMENT                                                   │
│  ───────────────────                                                    │
│  • Add full content using content-mapping rules                        │
│  • PRD content → Epic description, Story acceptance criteria           │
│  • Tech Spec content → Task technical details                          │
│  • Every Task needs 8 required fields                                  │
│                                                                          │
│  Output: Fully enriched EPIC-N-enriched.md files                       │
├─────────────────────────────────────────────────────────────────────────┤
│  Phase 3e: JIRA POPULATION                                              │
│  ─────────────────────────                                              │
│  • Push to Jira with proper hierarchy                                  │
│  • Use ADF format for rich descriptions                                │
│  • Link dependencies between issues                                    │
│  • Create QA sub-tasks (reference .aid/qa/ files)                      │
│                                                                          │
│  Output: All Epics, Stories, Tasks, QA Sub-tasks in Jira               │
├─────────────────────────────────────────────────────────────────────────┤
│  Phase 3f: VERIFICATION                                                 │
│  ──────────────────────                                                 │
│  • Run PRD coverage agent (every user story → Story)                   │
│  • Run Tech Spec coverage agent (every component → Tasks)              │
│  • Verify QA criteria files exist for all tasks                        │
│  • Gap remediation: add missing, re-verify                             │
│  • 100% coverage required before Phase 4                               │
│                                                                          │
│  Output: Verification report, 100% coverage                            │
└─────────────────────────────────────────────────────────────────────────┘
```

### Exit Criteria (Mandatory)

| Requirement | Location | Validation |
|-------------|----------|------------|
| Contradiction Log | `docs/implementation-plan/contradiction-log.md` | All contradictions resolved |
| Consolidated Spec | `docs/implementation-plan/00-consolidated-spec.md` | File exists |
| Enriched EPICs | `docs/implementation-plan/enriched-jiras/*.md` | One per EPIC |
| **QA Criteria Files** | `.aid/qa/{task-id}.yaml` | One per task |
| **Criteria Follow Iron Rules** | `.aid/qa/*.yaml` | No tech spec content |
| Hierarchy | Jira | Epic → Story → Task → QA Sub-task |
| Task Size | All tasks | Sized per document size rule |
| Task Completeness | All tasks | 8 required fields present |
| **QA Sub-tasks Created** | Jira | Reference .aid/qa/ files |
| PRD Coverage | Verification | 100% user stories covered |
| Tech Spec Coverage | Verification | 100% components covered |
| Test Strategy | Plan | Test types defined |
| **Feedback Collected** | `~/.aid/feedback/pending/` | `/aid end` completed |

### Content Mapping Rules

```
┌─────────────────────────────────────────────────────────────────────────┐
│  SOURCE DOCUMENT              →  TARGET JIRA LEVEL                      │
│  ─────────────────────           ──────────────────                     │
│                                                                          │
│  PRD Product Goals            →  Epic: Business Value                   │
│  PRD User Personas            →  Epic: User Impact                      │
│  PRD Success Metrics          →  Epic: Success Criteria                 │
│  PRD User Stories             →  Story: User Story                      │
│  PRD Acceptance Criteria      →  Story: AC (Gherkin)                    │
│                                                                          │
│  Tech Spec Architecture       →  Epic: Technical Context                │
│  Tech Spec Components         →  Task: Implementation Details           │
│  OpenAPI Endpoints            →  Task: API Contract                     │
│  Prisma Models                →  Task: Database Changes                 │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Task Required Fields (All 8 Mandatory)

```
┌─────────────────────────────────────────────────────────────────────────┐
│  EVERY TASK MUST HAVE:                                                  │
│                                                                          │
│  1. Description         - What to build and WHY (2-3 sentences)        │
│  2. Files to modify     - Exact file paths                             │
│  3. Code pattern        - Example or snippet to follow                 │
│  4. API contract        - Method, path, request, response (if API)     │
│  5. Error handling      - Table of error cases                         │
│  6. Acceptance criteria - Specific, testable outcomes                  │
│  7. Size estimate       - XS/S/M/L/XL with hours                       │
│  8. Tech Spec reference - Section number                               │
│                                                                          │
│  Task missing ANY field = NOT ready for development                    │
└─────────────────────────────────────────────────────────────────────────┘
```

### Gate Check Script

```javascript
function checkGate3(state, feedback) {
  const implPlan = state.documents.implementation_plan;
  const enrichedDir = 'docs/implementation-plan/enriched-jiras/';

  const checks = {
    // Phase 3a checks
    contradictionLogExists: fs.existsSync('docs/implementation-plan/contradiction-log.md'),
    consolidatedSpecExists: fs.existsSync('docs/implementation-plan/00-consolidated-spec.md'),

    // Phase 3b checks
    enrichedFilesExist: fs.readdirSync(enrichedDir).filter(f => f.endsWith('-enriched.md')).length > 0,

    // Phase 3c checks
    tasksHaveRequiredFields: validateTaskFields(enrichedDir),

    // Phase 3d checks
    jiraPopulated: state.jira_issues_created > 0,
    hierarchyValid: state.stories_created > 0, // Story layer not skipped

    // Phase 3e checks
    prdCoverage: state.prd_coverage === 100,
    techSpecCoverage: state.tech_spec_coverage === 100,

    // Feedback
    feedbackCollected: feedback.phase_3 === true,
  };

  return Object.values(checks).every(v => v === true);
}
```

### Templates Reference

Use templates from `skills/aid-impl-plan/references/templates/`:
- `epic-template.md` - Epic format and content rules
- `story-template.md` - Story format with INVEST criteria
- `task-template.md` - Task format with all 8 required fields
- `contradiction-log-template.md` - Contradiction tracking format

---

## Gate 4: Development → QA & Ship

### Entry Criteria
- Gate 3 passed
- Implementation Plan approved
- Development environment ready

### Exit Criteria (Mandatory)

| Requirement | Location | Validation |
|-------------|----------|------------|
| Code Complete | `src/` | All features implemented |
| Unit Tests | `testing/unit/` | Tests pass |
| Integration Tests | `testing/integration/` | Tests pass |
| E2E Tests | `testing/e2e/` | Tests pass |
| Coverage Met | CI/CD | >= 70% coverage |
| Code Reviewed | PR | Approved |
| **Feedback Collected** | `~/.aid/feedback/pending/` | `/aid end` completed |

### Development Completion Checks

```
┌─────────────────────────────────────────────────────────────────┐
│  DEVELOPMENT GATE CHECKS (Mandatory for Gate 4)                 │
│                                                                 │
│  □ All tasks in Implementation Plan marked complete             │
│  □ All tasks PASSED QA gate validation ◄── NEW                  │
│  □ npm test passes with no failures                             │
│  □ npm run build completes without errors                       │
│  □ Code coverage >= 70%                                         │
│  □ No critical security vulnerabilities (npm audit)             │
│  □ All PRs merged to main branch                                │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  QA GATE VALIDATION (Per-Task During Phase 4) ◄── NEW           │
│                                                                 │
│  For EACH task completed:                                       │
│  □ QA sub-agent reviewed against .aid/qa/{task-id}.yaml        │
│  □ All must_achieve criteria passed                             │
│  □ No must_not violations                                       │
│  □ Scope boundaries (not_included) respected                    │
│  □ Best practices followed                                      │
│                                                                 │
│  QA Gate Rules:                                                 │
│  • Hard block - cannot proceed to next task until PASS          │
│  • Max 3 review cycles before escalation                        │
│  • QA agent has isolated context (no tech spec)                 │
└─────────────────────────────────────────────────────────────────┘
```

### Gate Check Script

```javascript
function checkGate4(state, feedback) {
  const checks = {
    testsPass: runCommand('npm test').success,
    buildPasses: runCommand('npm run build').success,
    coverageMet: getCoverage() >= 70,
    noSecurityIssues: runCommand('npm audit').exitCode === 0,
    feedbackCollected: feedback.phase_4 === true,
  };

  return Object.values(checks).every(v => v === true);
}
```

---

## Gate 5: QA & Ship → Complete

### Entry Criteria
- Gate 4 passed
- All tests passing
- Staging environment verified

### Exit Criteria (Mandatory)

| Requirement | Location | Validation |
|-------------|----------|------------|
| QA Sign-off | QA Team | Approved |
| Performance Verified | Staging | Meets SLAs |
| Security Verified | Staging | Pen test passed |
| Documentation | `docs/` | Updated |
| Release Notes | `CHANGELOG.md` | Version documented |
| **Feedback Collected** | `~/.aid/feedback/pending/` | `/aid end` completed |

---

## Feedback Integration

Each gate requires mandatory feedback collection before advancement:

```
┌──────────────────────────────────────────────────────────────┐
│                    FEEDBACK AT GATES                         │
│                                                              │
│  Gate 1: "How was the PRD quality?"                          │
│          - Rating (1-5)                                      │
│          - What worked well                                  │
│          - What to improve                                   │
│                                                              │
│  Gate 2: "How was the Tech Spec quality?"                    │
│          - Rating (1-5)                                      │
│          - Security coverage                                 │
│          - Architecture clarity                              │
│                                                              │
│  Gate 3: "How was the Implementation Plan?"                  │
│          - Rating (1-5)                                      │
│          - Task breakdown quality                            │
│          - Estimate accuracy                                 │
│                                                              │
│  Gate 4: "How was the Development phase?"                    │
│          - Rating (1-5)                                      │
│          - Code quality                                      │
│          - Test coverage                                     │
└──────────────────────────────────────────────────────────────┘
```

---

## Gate Override

Users can override gates with explicit reason:

```
User: "override: urgent hotfix required"

Claude Response:
⚠️ GATE OVERRIDE LOGGED

Reason: urgent hotfix required
Phase: 1 → 4 (skipping 2, 3)
Logged to: .aid/overrides.log

Note: Feedback will still be collected at phase completion.
Proceed with caution - skipped phases may cause issues.
```

### Override Log Format

```json
{
  "timestamp": "2024-12-11T14:00:00Z",
  "from_phase": 1,
  "to_phase": 4,
  "skipped": [2, 3],
  "reason": "urgent hotfix required",
  "user": "developer"
}
```

---

## Commands

| Command | Description |
|---------|-------------|
| `/gate-check` | Show current gate status |
| `/gate-check --detailed` | Show all requirements |
| `/phase approve` | Mark gate as passed |
| `/aid end` | Collect feedback (required for gate) |
