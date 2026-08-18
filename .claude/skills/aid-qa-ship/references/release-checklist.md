# Release Checklist

## Pre-Release Checklist

### Code Quality
- [ ] All tests passing
- [ ] Code review approved
- [ ] No critical/high bugs open
- [ ] Technical debt documented
- [ ] Dependencies updated and secure

### Testing Complete
- [ ] Functional testing complete
- [ ] Integration testing complete
- [ ] Performance testing complete
- [ ] Security scan passed
- [ ] Accessibility tested
- [ ] Cross-browser/device tested (if applicable)

### Documentation
- [ ] Release notes prepared
- [ ] API documentation updated
- [ ] User documentation updated
- [ ] Runbooks updated
- [ ] Architecture docs current

### Stakeholder Sign-off
- [ ] Product Owner approved
- [ ] Tech Lead approved
- [ ] QA Lead approved
- [ ] Security approved (if required)
- [ ] Compliance approved (if required)

## Deployment Checklist

### Pre-Deployment
- [ ] Deployment plan reviewed
- [ ] Rollback plan documented
- [ ] Database migration tested
- [ ] Feature flags configured
- [ ] Monitoring alerts configured
- [ ] On-call team notified

### Deployment Steps
1. [ ] Notify stakeholders of deployment start
2. [ ] Create database backup
3. [ ] Deploy to staging
4. [ ] Run staging smoke tests
5. [ ] Deploy to production (canary if applicable)
6. [ ] Run production smoke tests
7. [ ] Monitor error rates
8. [ ] Gradual rollout (if applicable)
9. [ ] Notify stakeholders of completion

### Post-Deployment
- [ ] Smoke tests passing
- [ ] Error rates normal
- [ ] Performance metrics normal
- [ ] User feedback monitored
- [ ] Documentation published

## Rollback Procedure

### When to Rollback
- Error rate > [X]% threshold
- Critical functionality broken
- Security vulnerability discovered
- Data corruption detected

### Rollback Steps
1. [ ] Notify stakeholders
2. [ ] Execute rollback deployment
3. [ ] Restore database (if needed)
4. [ ] Verify rollback successful
5. [ ] Investigate root cause
6. [ ] Document incident

## Emergency Contacts

```markdown
| Role | Name | Contact |
|------|------|---------|
| On-Call Engineer | [name] | [contact] |
| Tech Lead | [name] | [contact] |
| Product Owner | [name] | [contact] |
| DevOps | [name] | [contact] |
```

## Monitoring Checklist

### Metrics to Watch
- [ ] Error rate
- [ ] Response time (P50, P95, P99)
- [ ] Throughput
- [ ] CPU/Memory usage
- [ ] Database connections
- [ ] Queue depths

### Alert Thresholds
| Metric | Warning | Critical |
|--------|---------|----------|
| Error rate | > 1% | > 5% |
| P95 latency | > 500ms | > 2s |
| CPU | > 70% | > 90% |
| Memory | > 80% | > 95% |

## Post-Release Tasks

### Immediate (Day 1)
- [ ] Monitor metrics
- [ ] Check user feedback
- [ ] Address critical issues
- [ ] Update status page

### Short-term (Week 1)
- [ ] Gather user feedback
- [ ] Performance analysis
- [ ] Bug triage
- [ ] Retrospective scheduled

### Documentation
- [ ] Close Jira issues
- [ ] Update project status
- [ ] Archive release artifacts
- [ ] Document lessons learned
