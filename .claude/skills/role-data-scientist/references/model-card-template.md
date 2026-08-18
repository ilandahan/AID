# Model Card Template

Standard documentation for every ML model before deployment.
**Use in**: Phase 6 — Deploy to Production & Monitoring

> **Iron Rule #6: No prediction without explainability**
> Every model must have a completed model card before going to production.

---

## How to Use

1. Copy this template for each model
2. Fill in all sections — write "N/A" only with explicit justification
3. Review with Tech Lead and Product Manager
4. Store alongside model artifacts in the model registry
5. Update whenever the model is retrained or behavior changes

---

## Model Card: [Model Name]

### Model Details

| Field | Value |
|-------|-------|
| **Model Name** | |
| **Version** | |
| **Type** | Classification / Regression / Generation / Retrieval / Ranking |
| **Framework** | [Stack used — ask user at project start] |
| **Owner** | Team / Person responsible |
| **Created** | Date |
| **Last Updated** | Date |
| **Status** | Development / Staging / Production / Deprecated |

---

### Intended Use

**Primary use case:**
> [What problem this model solves and for whom]

**Intended users:**
> [Internal teams / end users / automated systems]

**Out-of-scope uses:**
> [What this model must NOT be used for — be specific]

---

### Training Data

| Field | Value |
|-------|-------|
| **Source** | [Data source with lineage] |
| **Size** | [N samples, date range] |
| **Collection method** | [How data was gathered] |
| **Preprocessing** | [Key transforms — imputation strategy, outlier handling, feature decisions] |
| **Split** | Train: _% / Validation: _% / Test: _% |
| **Known limitations** | [Biases, gaps, staleness] |
| **PII handling** | [How PII was handled] |
| **Data version** | [Snapshot ID or commit hash] |

**Feature engineering decisions** *(critical — document explicitly)*:
- Imputation method per column and rationale
- Derived features kept vs. removed, and why
- Leakage checks performed and results

---

### Architecture

> [Brief description of model type and key design decisions]
> Include: why this architecture over alternatives considered

**Key hyperparameters:**

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| | | |

---

### Evaluation Results

**Overall performance** *(compare against baseline)*:

| Metric | Value | Baseline | Threshold | Pass |
|--------|-------|----------|-----------|------|
| | | | | |

**Per-slice performance** *(required — aggregate metrics hide disparities)*:

| Slice | Metric | Value | vs. Overall | Flag |
|-------|--------|-------|-------------|------|
| | | | | |

**Confusion matrix** *(for classification)*:

| | Predicted Negative | Predicted Positive |
|--|---|---|
| **Actual Negative** | TN: | FP: |
| **Actual Positive** | FN: | TP: |

**Latency** *(measured under production-representative load)*:

| Percentile | Value | SLA |
|------------|-------|-----|
| P50 | ms | ms |
| P95 | ms | ms |
| P99 | ms | ms |

---

### Bias & Fairness

**Audit date:** [Date]  
**Audited by:** [Person/Team]

| Protected Attribute | Metric | Group A | Group B | Gap | Pass |
|---------------------|--------|---------|---------|-----|------|
| | | | | | |

**Fairness metrics used:** [List with rationale for selection]  
**Mitigation applied:** [Techniques used, or "None required — justify"]

**Reference**: `bias-audit-checklist.md` for full audit methodology

---

### Limitations & Risks

**Known failure modes:**
- [Scenario where model performs poorly]

**Edge cases:**
- [Input types that cause degraded performance]

**Data freshness:**
> [How quickly the training data becomes stale — and what happens when it does]

**Confidence score interpretation:**
> [What a score of 0.8 actually means in this context]

---

### Ethical Considerations

- [Potential for harm if misused]
- [Groups that could be disproportionately affected]
- [Safeguards in place]

---

### Monitoring & Maintenance

| Field | Value |
|-------|-------|
| **Monitoring dashboard** | [Link] |
| **Alert channels** | [Slack / PagerDuty / other] |
| **Drift detection method** | [PSI / KL / KS — and threshold] |
| **Retraining trigger** | [Metric drop threshold or schedule] |
| **Retraining frequency** | [Scheduled or event-driven] |
| **Rollback procedure** | [How to roll back — tested: Yes / No] |

**Reference**: `monitoring-setup-guide.md` for monitoring configuration

---

### Experiment Lineage

| Field | Value |
|-------|-------|
| **Experiment ID** | |
| **Code commit** | |
| **Data snapshot** | |
| **Config file** | |
| **Training logs** | |

---

## Approval

| Role | Name | Approved | Date | Notes |
|------|------|----------|------|-------|
| Data Scientist | | | | |
| Tech Lead | | | | |
| Product Manager | | | | |
| QA Engineer | | | | |

---

## Change Log

| Date | Version | Change | Author |
|------|---------|--------|--------|
| | | Initial model card | |

---

## Quick Checklist

- [ ] All sections filled (or N/A with justification)
- [ ] Per-slice evaluation results included
- [ ] Bias audit completed and results documented
- [ ] Feature engineering decisions explicitly documented
- [ ] Limitations section is honest and specific
- [ ] Monitoring configured, tested, and linked
- [ ] Rollback procedure documented and tested
- [ ] All approvals obtained

---

**Cross-references**:
- `SKILL.md` — Phase 6 behaviors and Iron Rule #6
- `ml-pipeline-checklist.md` — Phase 6 deployment checklist
- `bias-audit-checklist.md` — Bias & Fairness section
- `monitoring-setup-guide.md` — Monitoring & Maintenance section
