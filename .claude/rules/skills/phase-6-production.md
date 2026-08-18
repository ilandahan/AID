# Phase 6 — Deploy to Production & Monitoring

## Goal
Ship safely, observe continuously, document completely.
Iron Rule #3: No deployment without monitoring.
Iron Rule #6: No prediction without explainability.
Iron Rule #7: No model without bias audit.

## Mandatory Outputs
- [ ] Live serving endpoint with health checks
- [ ] Monitoring dashboard + alerts configured (all 4 signal categories)
- [ ] Model card completed and approved
- [ ] Bias audit completed and signed off
- [ ] Rollback procedure documented and tested
- [ ] Deploy-time baseline metrics recorded

---

## Pre-Deployment Checklist

Complete ALL items before first production request is served.

### Model Quality Gate
- [ ] Model meets acceptance thresholds on ALL evaluation slices (from Phase 5)
- [ ] Baseline comparison documented
- [ ] Experiment record saved with artifacts and lineage

### Monitoring Setup (Iron Rule #3)
Configure before deployment — not after.

Required signal categories (skip only with documented justification):

**1. Data Quality Signals**
- Schema violations: threshold = 0 | window = 1h | severity = critical
- Null rate per feature: threshold = 5% | window = 1h | severity = warning
- Distribution drift (PSI): threshold = 0.10 | window = 24h | severity = warning
- Distribution drift (PSI): threshold = 0.25 | window = 24h | severity = critical

**2. Model Performance Signals**
- Accuracy decay vs. deploy baseline: threshold = 5% drop | window = 7d | severity = warning
- Prediction distribution drift (KL): threshold = 0.15 | window = 24h | severity = warning
- Latency P95: threshold = 500ms | window = 1h | severity = warning
- Error rate: threshold = 1% | window = 1h | severity = critical

**3. RAG Quality Signals** (if applicable)
- Retrieval relevance: threshold = 0.70 | window = 1h | severity = warning
- Hallucination rate: threshold = 5% | window = 24h | severity = critical
- Empty retrieval rate: threshold = 10% | window = 1h | severity = warning

**4. Prompt Behavior Signals** (if applicable)
- Format compliance: threshold = 95% | window = 1h | severity = warning
- Refusal rate: threshold = 10% | window = 1h | severity = warning
- Timeout rate: threshold = 2% | window = 1h | severity = critical

**Reference**: `references/monitoring-setup-guide.md` for full configuration template

### Deploy-Time Baseline Recording
Record at deployment — this is the drift detection reference:
- [ ] All performance metrics (accuracy, F1, AUC-ROC as applicable)
- [ ] Input feature distributions per column
- [ ] Prediction score distribution
- [ ] Latency P50/P95/P99 under expected load
- [ ] Null rates per feature in production traffic

### Bias Audit (Iron Rule #7)
- [ ] Bias audit completed per `references/bias-audit-checklist.md`
- [ ] Per-slice metrics documented (not just aggregate)
- [ ] Protected attributes and proxies verified
- [ ] Sign-off obtained from all required roles

### Model Card (Iron Rule #6)
- [ ] Model card completed per `references/model-card-template.md`
- [ ] All sections filled (or N/A with justification)
- [ ] Feature engineering decisions documented
- [ ] Limitations section is honest and specific
- [ ] Monitoring section links to dashboard
- [ ] Tech Lead and PM approval obtained

### Rollback Procedure
Document and test before going live:
```
## Rollback Procedure

### Trigger Criteria
Roll back if any of:
- Critical alert fires and cannot be resolved in [X] minutes
- Accuracy drops more than [Y]% from deploy baseline
- [domain-specific trigger]

### Steps
1. [Step 1 — e.g., route traffic to previous model version]
2. [Step 2 — e.g., notify on-call and stakeholders]
3. [Step 3 — e.g., open post-mortem]

### Tested: YES / NO — Date: [date]
```

A rollback procedure that has NOT been tested does not count.

---

## Post-Deployment: Ongoing Operations

### Weekly
- Review monitoring dashboards for trends
- Check prediction distribution drift
- Review alert history — tune thresholds if false positives are high

### Monthly
- Review accuracy if ground truth is available
- Check latency trends
- Assess feature distribution drift

### Quarterly
- Scheduled bias audit
- Model card review and update
- Assess retraining need against retraining criteria

### Retraining Triggers
Define at deployment time — do not decide reactively:
- Accuracy drops > [threshold]% sustained over [window]
- Input distribution drift (PSI > 0.25) sustained over [window]
- Business context change (new product, new customer segment)
- Scheduled retraining: every [N] months regardless

---

## Alert Routing

| Severity | Route To | Response Time |
|----------|----------|---------------|
| Critical | On-call + team channel | < 15 minutes |
| Warning | Team channel | < 4 hours |
| Info | Dashboard only | Next business day |

Dashboards without alerts do not catch failures.
Every Warning-level signal must have an alert — not just a tile.

---

## Phase Complete Gate

Production is operating when ALL of the following are true:
- [ ] Monitoring dashboard live with all 4 applicable signal categories
- [ ] Alerts configured and tested (not just dashboard)
- [ ] Deploy-time baseline metrics recorded
- [ ] Model card complete and approved
- [ ] Bias audit complete and signed off
- [ ] Rollback procedure documented and tested
- [ ] Retraining criteria defined
- [ ] On-call rotation aware of the model and its failure modes

**Reference**: `references/monitoring-setup-guide.md`  
**Reference**: `references/model-card-template.md`  
**Reference**: `references/bias-audit-checklist.md`
