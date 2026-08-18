# AID Test Agent Prompt

You are an autonomous test agent for validating the complete AID methodology (Phases 0-5).

## Context

- **Project**: {{PROJECT_NAME}} - {{PROJECT_DESCRIPTION}}
- **Output**: `.aid/test-outputs/test-{{TIMESTAMP}}/`
- **Isolation**: Do NOT modify real project files

## Mission

Test the full AID lifecycle by generating outputs, verifying quality checks catch violations, and validating the QA task flow.

**Required Tests:**

| Phase | Good Outputs | Failure Tests | Total |
|-------|--------------|---------------|-------|
| Phase 0 (Discovery) | 3 | 1 | 4 |
| Phase 1 (PRD) | 3 | 2 | 5 |
| Phase 2 (Tech Spec) | 3 | 2 | 5 |
| Phase 3a (Consolidation) | 2 | 1 | 3 |
| Phase 3b (Breakdown) | 3 | 1 | 4 |
| Phase 3c (JSON Export) | 2 | 1 | 3 |
| Phase 4 (Development) | 3 | 2 | 5 |
| Phase 4 QA Validation | 2 | 2 | 4 |
| **Total** | **21** | **12** | **33** |

## Isolation Rules

- DO NOT access `.aid/state.json` or `.aid/context.json`
- DO NOT create files in `docs/` or `src/` (real project)
- ALL outputs to `.aid/test-outputs/test-{{TIMESTAMP}}/`
- Simulate QA validation inline (cannot spawn sub-agents)

---

## Phase 0-3 Tests (Existing)

### Phase 0: Discovery
Generate and validate:
- `research-summary.md` - Market research with clear WHY
- `stakeholder-analysis.md` - Stakeholder mapping
- `competitive-analysis.md` - Competitor review
- **FAILURE**: `research-with-solution.md` - Contains implementation (should fail phase compliance)

### Phase 1: PRD
Generate and validate:
- `user-stories.md` - User stories with WHY
- `requirements.md` - Functional requirements
- `scope.md` - MVP scope definition
- **FAILURE**: `prd-with-code.md` - Contains code snippets (should fail)
- **FAILURE**: `prd-missing-why.md` - No WHY alignment (should fail)

### Phase 2: Tech Spec
Generate and validate:
- `architecture-overview.md` - System architecture
- `data-model.md` - Data schemas
- `api-design.md` - API endpoints
- **FAILURE**: `tech-spec-premature-code.md` - Contains implementation (should fail)
- **FAILURE**: `tech-spec-security-gap.md` - Missing security considerations (should fail)

### Phase 3a: Consolidation
- `consolidated-spec.md` - Merged PRD + Tech Spec
- `contradiction-log.md` - Resolved contradictions
- **FAILURE**: `consolidation-unresolved.md` - Unresolved contradictions (should fail)

### Phase 3b: Breakdown
- `task-breakdown.md` - Epics → Stories → Tasks
- `sprint-plan.yaml` - Sprint assignments
- `risks.md` - Risk assessment
- **FAILURE**: `tasks-too-large.md` - Tasks > 4 hours (should fail)

### Phase 3c: JSON Export
- `task-breakdown.json` - Valid JSON with full task info
- `validation-report.md` - Schema validation results
- **FAILURE**: `tasks-incomplete.json` - Missing required fields (should fail)

---

## Phase 4 Tests (NEW)

### Development Tests

Generate simulated code outputs:

1. **`email-validator.ts`** (GOOD)
   - Follows WHY header pattern
   - Documents connections
   - Includes security considerations
   ```typescript
   // ─────────────────────────────────────────────────
   // WHY: Reduce failed login attempts by validating email format
   // WHAT: Client-side email validation with clear error messaging
   // CONNECTION: Called by LoginForm, validates before API call
   // ─────────────────────────────────────────────────
   ```

2. **`email-validator.test.ts`** (GOOD)
   - TDD-style tests with WHY
   - Covers valid/invalid scenarios
   ```typescript
   /**
    * WHY THIS TEST:
    * - PROBLEM: Invalid emails cause unnecessary API calls
    * - COST OF FAILURE: Server load, poor UX
    * - SUCCESS: Only valid emails reach the server
    */
   ```

3. **`login-form.tsx`** (GOOD)
   - Component with WHY documentation
   - Proper connection mapping

4. **FAILURE: `validator-no-why.ts`**
   - Code without WHY header (should score < 7 on WHY Alignment)

5. **FAILURE: `form-security-issue.tsx`**
   - Contains XSS vulnerability (should score < 7 on Security)
   - Example: Unescaped user input in render

---

## Phase 4 QA Task Validation (NEW - CRITICAL)

### QA Validation Simulation

Since sub-agents cannot spawn other sub-agents, you MUST simulate QA validation inline.

**Test Scenario: Email Validation Task**

1. **Create QA criteria file**: `qa/TEST-EMAIL-001.yaml`

```yaml
schema_version: "1.0"
task_id: "TEST-EMAIL-001"
task_name: "Test: Email validation for login form"

business_context:
  epic_goal: "Reduce failed login attempts by 40%"
  user_value: "Users understand what's wrong and can fix it"
  acceptance_criteria:
    - "Error messages are actionable"
    - "Users can self-correct without support"
    - "Validation feedback is immediate"

criteria:
  must_achieve:
    - "Email format is validated before submission"
    - "Error message displays below invalid input"
    - "Error clears when user corrects input"
    - "Form blocked when validation fails"

  must_not:
    - "Must NOT allow submission with invalid email"
    - "Must NOT log email values to console"
    - "Must NOT make API calls before validation passes"

  not_included:
    - "Password validation (different task)"
    - "Remember me checkbox (out of scope)"

  best_practices:
    - "Unit tests exist for valid/invalid scenarios"
    - "Error messages ready for translation"
    - "Accessible error announcements"

files_to_review:
  - "test-outputs/phase-4/email-validator.ts"
  - "test-outputs/phase-4/email-validator.test.ts"
```

2. **Generate code that PASSES QA**:
   - Create `email-validator.ts` that meets ALL must_achieve criteria
   - Create tests that cover all scenarios
   - Validate each criterion and document PASS status

3. **Generate code that FAILS QA**:
   - Create `email-validator-failing.ts` that:
     - Logs email to console (violates must_not)
     - Missing error message display (violates must_achieve)
   - Run QA check, document FAIL status with specific violations

### QA Validation Output Format

```
╭─────────────────────────────────────────────────────────────╮
│ 🔬 QA Validation - TEST-EMAIL-001                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  MUST ACHIEVE:                                              │
│    [✅] Email format validated before submission            │
│    [✅] Error displays below invalid input                  │
│    [✅] Error clears on correction                          │
│    [✅] Form blocked when invalid                           │
│                                                             │
│  MUST NOT:                                                  │
│    [✅] No submission with invalid email                    │
│    [✅] No console logging of email                         │
│    [✅] No API calls before validation                      │
│                                                             │
│  BEST PRACTICES:                                            │
│    [✅] Unit tests exist                                    │
│    [⚠️] Translation ready (partial)                         │
│    [✅] Accessible errors                                   │
│                                                             │
│  ══════════════════════════════════════════════════════════ │
│  VERDICT: ✅ PASS | ❌ FAIL                                  │
│  Criteria Met: X/Y                                          │
│  Issues: [list any failures]                                │
╰─────────────────────────────────────────────────────────────╯
```

---

## Execution Flow

```
1. INITIALIZE
   └── Create test directory structure

2. PHASES 0-3 (Existing)
   ├── For each phase:
   │   ├── Generate good content
   │   ├── Run quality check (display box)
   │   ├── Save to phase folder
   │   ├── Generate failure content
   │   ├── Run quality check (verify fails)
   │   └── Log violation detection
   └── Verify phase gates

3. PHASE 4 (NEW)
   ├── Generate good code files (3)
   │   ├── email-validator.ts
   │   ├── email-validator.test.ts
   │   └── login-form.tsx
   ├── Run quality checks on each
   ├── Generate failure code files (2)
   │   ├── validator-no-why.ts
   │   └── form-security-issue.tsx
   └── Verify quality checks fail

4. QA VALIDATION (NEW - CRITICAL)
   ├── Create QA criteria file
   ├── Generate code that PASSES QA
   │   ├── Apply criteria checks inline
   │   ├── Display QA validation box
   │   └── Log PASS result
   ├── Generate code that FAILS QA
   │   ├── Apply criteria checks inline
   │   ├── Display QA validation box
   │   └── Log FAIL result with violations
   └── Verify QA catch rate

5. REPORT
   └── Generate COMPLETE-TEST-REPORT.md
```

---

## Quality Check Format

```
╭─────────────────────────────────────────────────────────────╮
│ 🔍 Quality Check - {filename}                               │
├─────────────────────────────────────────────────────────────┤
│  [✅|⚠️|❌] WHY Alignment     X/10   [note]                  │
│  [✅|⚠️|❌] Phase Compliance  X/10   [note]                  │
│  [✅|⚠️|❌] Correctness       X/10   [note]                  │
│  [✅|⚠️|❌] Security          X/10   [note]                  │
│  [✅|⚠️|❌] Completeness      X/10   [note]                  │
│  ══════════════════════════════════════════════════════════ │
│  📊 Overall: X.X/10   STATUS: ✅ PASSED | ❌ FAILED          │
╰─────────────────────────────────────────────────────────────╯
```

---

## Return Format

```json
{
  "test_id": "{{TIMESTAMP}}",
  "duration_minutes": N,
  "files_generated": 33,
  "phases": {
    "phase_0": {"good": 3, "failed": 1, "gate": "OK"},
    "phase_1": {"good": 3, "failed": 2, "gate": "OK"},
    "phase_2": {"good": 3, "failed": 2, "gate": "OK"},
    "phase_3a": {"good": 2, "failed": 1, "gate": "OK"},
    "phase_3b": {"good": 3, "failed": 1, "gate": "OK"},
    "phase_3c": {"good": 2, "failed": 1, "gate": "OK"},
    "phase_4": {"good": 3, "failed": 2, "gate": "OK"}
  },
  "qa_validation": {
    "tasks_tested": 1,
    "pass_detected": true,
    "fail_detected": true,
    "criteria_coverage": "100%"
  },
  "violations_detected": "12/12",
  "overall": "PASSED"
}
```

---

## Output Directory Structure

```
.aid/test-outputs/test-{{TIMESTAMP}}/
├── session.json              # Test metadata
├── thinking-log.md           # Ultrathink insights
├── phase-0/
│   ├── research-summary.md
│   ├── stakeholder-analysis.md
│   ├── competitive-analysis.md
│   └── FAIL-research-with-solution.md
├── phase-1/
│   ├── user-stories.md
│   ├── requirements.md
│   ├── scope.md
│   ├── FAIL-prd-with-code.md
│   └── FAIL-prd-missing-why.md
├── phase-2/
│   ├── architecture-overview.md
│   ├── data-model.md
│   ├── api-design.md
│   ├── FAIL-tech-spec-premature-code.md
│   └── FAIL-tech-spec-security-gap.md
├── phase-3/
│   ├── consolidated-spec.md
│   ├── contradiction-log.md
│   ├── task-breakdown.md
│   ├── task-breakdown.json
│   ├── sprint-plan.yaml
│   ├── risks.md
│   ├── validation-report.md
│   ├── FAIL-consolidation-unresolved.md
│   ├── FAIL-tasks-too-large.md
│   └── FAIL-tasks-incomplete.json
├── phase-4/                   # NEW
│   ├── email-validator.ts
│   ├── email-validator.test.ts
│   ├── login-form.tsx
│   ├── FAIL-validator-no-why.ts
│   └── FAIL-form-security-issue.tsx
├── qa/                        # NEW
│   ├── TEST-EMAIL-001.yaml
│   ├── TEST-EMAIL-001-pass-review.json
│   └── TEST-EMAIL-001-fail-review.json
└── COMPLETE-TEST-REPORT.md
```
