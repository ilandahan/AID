# /gate-check

Check if all exit criteria for current phase are met.

## Usage

```
/gate-check        # Check current phase
/gate-check 2      # Check specific phase
```

## What It Does

1. Read `.aid/state.json`
2. Check ALL exit criteria for the phase
3. Report pass/fail for each
4. Overall verdict: PASS or FAIL

## Output Examples

### Phase 1 (PRD) - PASS

```
Checking Phase 1 (PRD) Gate...

Artifacts:
  [✓] docs/prd/YYYY-MM-DD-[feature].md exists
  [✓] Has Problem Statement
  [✓] Has User Stories
  [✓] Has Acceptance Criteria
  [✓] Has Out of Scope

Approvals:
  [✓] .aid/approvals/prd-approved.md exists

═══════════════════════════════════════════════════════
GATE CHECK: ✅ PASS - Ready to advance to Phase 2
═══════════════════════════════════════════════════════
```

### Phase 2 (Tech Spec) - FAIL

```
Checking Phase 2 (Tech Spec) Gate...

Artifacts:
  [✓] docs/tech-spec/YYYY-MM-DD-[feature].md exists
  [✓] Architecture section present
  [✓] Data models defined
  [✗] API endpoints missing
  [✗] Component breakdown missing

Approvals:
  [✗] .aid/approvals/tech-spec-approved.md missing

═══════════════════════════════════════════════════════
GATE CHECK: ❌ FAIL

Missing:
  1. Add API endpoints to Tech Spec
  2. Add component breakdown
  3. Run /phase-approve after review
═══════════════════════════════════════════════════════
```

### Phase 3 (Implementation Plan) - PASS

```
Checking Phase 3 (Implementation Plan) Gate...

Artifacts:
  [✓] docs/implementation-plan/YYYY-MM-DD-[feature].md exists
  [✓] Has phases defined
  [✓] Has test requirements per phase
  [✓] Has rollout plan
  [✓] Has rollback plan

Approvals:
  [✓] .aid/approvals/implementation-plan-approved.md exists

═══════════════════════════════════════════════════════
GATE CHECK: ✅ PASS - Ready to advance to Phase 4
═══════════════════════════════════════════════════════
```

## Validation

Claude MUST actually verify:
- File existence (check filesystem)
- File content (parse and check sections)
- Approval files exist

Do NOT assume - actually check.
