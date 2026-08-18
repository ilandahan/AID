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
