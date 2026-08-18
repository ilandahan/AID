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
