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
