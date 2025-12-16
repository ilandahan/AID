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

### Exit Criteria (Mandatory)

| Requirement | Location | Validation |
|-------------|----------|------------|
| Implementation Plan | `docs/implementation-plan/YYYY-MM-DD-[feature].md` | File exists |
| Phase Breakdown | Plan Section 2 | At least 3 phases |
| Task List | Plan Section 3 | Tasks with estimates |
| Dependencies | Plan Section 4 | External deps listed |
| Test Strategy | Plan Section 5 | Test types defined |
| Risk Assessment | Plan Section 6 | Risks with mitigations |
| **Feedback Collected** | `~/.aid/feedback/pending/` | `/aid end` completed |

### Test Strategy Requirements

```
┌─────────────────────────────────────────────────────────────────┐
│  TEST STRATEGY GATE CHECKS (Mandatory for Gate 3)               │
│                                                                 │
│  □ Unit test requirements defined                               │
│  □ Integration test scope identified                            │
│  □ E2E test scenarios from user stories                         │
│  □ Coverage targets set (minimum 70%)                           │
│  □ Test data strategy documented                                │
└─────────────────────────────────────────────────────────────────┘
```

### Gate Check Script

```javascript
function checkGate3(state, feedback) {
  const implPlan = state.documents.implementation_plan;

  const checks = {
    planExists: fs.existsSync(implPlan),
    hasPhases: contentIncludes(implPlan, 'Phase'),
    hasTasks: contentIncludes(implPlan, '- [ ]'),
    hasTests: contentIncludes(implPlan, 'Test'),
    feedbackCollected: feedback.phase_3 === true,
  };

  return Object.values(checks).every(v => v === true);
}
```

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
│  □ npm test passes with no failures                             │
│  □ npm run build completes without errors                       │
│  □ Code coverage >= 70%                                         │
│  □ No critical security vulnerabilities (npm audit)             │
│  □ All PRs merged to main branch                                │
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
