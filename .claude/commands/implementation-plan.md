# /implementation-plan Command

Generate an Implementation Plan from PRD and Tech Spec.

## Usage

```
/implementation-plan [feature-name]
```

## What It Does

1. **Reads Documents**
   - Finds latest `docs/prd/YYYY-MM-DD-[feature-name].md`
   - Finds latest `docs/tech-spec/YYYY-MM-DD-[feature-name].md`

2. **Generates Implementation Plan**
   - Phases and milestones
   - Task breakdown
   - Test strategy per phase
   - Dependencies
   - Rollout plan

3. **Saves Document**
   - Location: `docs/implementation-plan/YYYY-MM-DD-[feature-name].md`
   - Uses date prefix for version tracking
   - Latest file is used by test-driven skill

## CRITICAL: Document Path

```
docs/implementation-plan/YYYY-MM-DD-[feature-name].md

Example: docs/implementation-plan/2024-06-17-user-authentication.md
```

This path is used by the **test-driven skill** to:
- Plan test phases
- Identify integration test sequence
- Define E2E test scenarios

## Implementation Plan Structure

```markdown
# Implementation Plan: [Feature Name]

**Created:** YYYY-MM-DD
**Status:** Draft | Review | Approved
**PRD Reference:** docs/prd/YYYY-MM-DD-[feature-name].md
**Tech Spec Reference:** docs/tech-spec/YYYY-MM-DD-[feature-name].md

## Overview
Implementation approach summary

## Phases

### Phase 1: Foundation
**Goal:** Set up core infrastructure

**Tasks:**
| Task | Description | Tests Required |
|------|-------------|----------------|
| 1.1 | Create database schema | DB migration tests |
| 1.2 | Define TypeScript interfaces | Type tests |
| 1.3 | Set up API structure | Unit tests |

**Test Strategy:**
- Unit tests for validators
- Database migration tests
- Type checking (tsc)

**Exit Criteria:**
- [ ] Database schema created
- [ ] Types defined
- [ ] All Phase 1 tests pass

---

### Phase 2: Core Features
**Goal:** Implement main functionality

**Tasks:**
| Task | Description | Tests Required |
|------|-------------|----------------|
| 2.1 | Implement registration API | API contract tests |
| 2.2 | Implement login API | API contract tests |
| 2.3 | Add authentication middleware | Integration tests |

**Test Strategy:**
- API contract tests for all endpoints
- Integration tests with real database
- Security tests

**Exit Criteria:**
- [ ] All API endpoints working
- [ ] Authentication verified
- [ ] All Phase 2 tests pass

---

### Phase 3: UI Implementation
**Goal:** Build user interface

**Tasks:**
| Task | Description | Tests Required |
|------|-------------|----------------|
| 3.1 | Create form atoms | Component tests |
| 3.2 | Build registration form | Component tests |
| 3.3 | Build login form | Component tests |

**Test Strategy:**
- Component unit tests
- Visual regression tests
- Accessibility tests

**Exit Criteria:**
- [ ] All forms working
- [ ] Visual tests pass
- [ ] Accessibility audit passes

---

### Phase 4: Integration & E2E
**Goal:** End-to-end verification

**Tasks:**
| Task | Description | Tests Required |
|------|-------------|----------------|
| 4.1 | Integration testing | Full integration suite |
| 4.2 | E2E testing | DevTools MCP E2E tests |
| 4.3 | Performance testing | Load tests |

**Test Strategy:**
- Full E2E flows with DevTools MCP
- Performance benchmarks
- Security penetration tests

**Exit Criteria:**
- [ ] All E2E tests pass
- [ ] Performance targets met
- [ ] Security audit passes

---

## Dependencies

### External Dependencies
| Dependency | Required By | Status |
|------------|-------------|--------|
| PostgreSQL | Phase 1 | Ready |
| Redis | Phase 2 | Ready |
| Email service | Phase 2 | Pending |

### Internal Dependencies
```
Phase 1 → Phase 2 → Phase 3 → Phase 4
   ↓          ↓          ↓
Database   API Ready  UI Ready
```

## Test Phases Summary

| Phase | Test Focus | Tools |
|-------|------------|-------|
| Phase 1 | Unit tests, DB migrations | Jest, Prisma |
| Phase 2 | API tests, Integration | Supertest, real DB |
| Phase 3 | Component tests, Visual | Jest, DevTools MCP |
| Phase 4 | E2E tests, Performance | DevTools MCP, k6 |

## Rollout Plan

### Staging Deployment
1. Deploy database migrations
2. Deploy API changes
3. Deploy frontend
4. Run smoke tests
5. Performance validation

### Production Deployment
1. Announce maintenance window
2. Backup database
3. Deploy with feature flag (disabled)
4. Run smoke tests
5. Enable feature flag (gradual rollout)
6. Monitor for 24 hours

## Rollback Plan

### Triggers for Rollback
- Error rate > 1%
- Response time > 500ms
- Failed smoke tests
- Critical security issue

### Rollback Steps
1. Disable feature flag
2. Revert API deployment
3. Revert database (if needed)
4. Notify stakeholders
5. Post-mortem analysis

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| Database migration failure | High | Test migrations in staging |
| Performance degradation | Medium | Load testing before release |
| Security vulnerability | High | Security audit before release |

## Timeline

| Phase | Start | End | Owner |
|-------|-------|-----|-------|
| Phase 1 | Week 1 | Week 1 | Backend |
| Phase 2 | Week 2 | Week 2 | Backend |
| Phase 3 | Week 2 | Week 3 | Frontend |
| Phase 4 | Week 3 | Week 4 | QA |
```

## Examples

```bash
# Generate implementation plan
/implementation-plan user-authentication
# Reads: docs/prd/2024-06-15-user-authentication.md
# Reads: docs/tech-spec/2024-06-16-user-authentication.md
# Creates: docs/implementation-plan/2024-06-17-user-authentication.md

# Interactive mode
/implementation-plan
```

## Phase Integration

This command is used in **Phase 3: Implementation Plan**

After Implementation Plan creation:
1. Review phases with team
2. Validate dependencies
3. Get approval with `/phase-approve`
4. Move to Phase 4: Development with `/phase-advance`

## Test-Driven Integration

The Implementation Plan is used by `/write-tests` command to:
- Plan test phases
- Identify integration test sequence
- Define E2E test scenarios

```
Implementation Plan Phases → Test phases
Implementation Plan Tasks → Test coverage requirements
Implementation Plan Exit Criteria → Test assertions
```

## Tips

- Break work into testable phases
- Include test requirements for each task
- Define clear exit criteria
- Plan rollback before rollout
- Identify dependencies early

---

## Prompt

```markdown
**Role**: You are a senior engineering lead creating a comprehensive implementation plan.

**Task**: Generate an Implementation Plan for [FEATURE_NAME].

**Context**:
- Feature: [FEATURE_NAME]
- Read PRD from: docs/prd/ (find latest for this feature)
- Read Tech Spec from: docs/tech-spec/ (find latest for this feature)
- Save to: docs/implementation-plan/YYYY-MM-DD-[feature-name].md
- This document will be used by test-driven skill

**Output Format**:
1. Read PRD and Tech Spec first
2. Create phased implementation plan
3. Include test requirements per phase
4. Define rollout and rollback plans
5. Save to docs/implementation-plan/ with date prefix

**Stopping Condition**:
- Plan saved to docs/implementation-plan/YYYY-MM-DD-[feature-name].md
- All phases have test requirements
- Rollout and rollback plans defined
- PRD and Tech Spec references included

**Steps**:
1. Find and read latest PRD for feature
2. Find and read latest Tech Spec for feature
3. Confirm documents with user
4. Design implementation phases
5. Define tasks per phase with test requirements
6. Identify dependencies
7. Create rollout plan
8. Create rollback plan
9. Save document to docs/implementation-plan/

---
Feature: [FEATURE_NAME]
---
```
