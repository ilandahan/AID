# Bias Audit Checklist

Pre-deployment fairness audit for ML models.
**Use in**: Phase 6 — Deploy to Production & Monitoring

> **Iron Rule #7: No model without bias audit**

---

## When to Run This Audit

- Before every production deployment
- After retraining on new data
- After significant changes to features or preprocessing
- On a scheduled quarterly basis in production

---

## Step 1 — Protected Attributes Inventory

- [ ] List all protected attributes relevant to your domain and jurisdiction
- [ ] Identify which attributes are in the training data (directly or as proxies)
- [ ] Document proxy variables — features that correlate with protected attributes

**Common protected attributes and their proxies**:

| Attribute | Proxies to Watch |
|-----------|-----------------|
| Race / Ethnicity | Name, zip code, language, neighborhood |
| Gender | Name, occupation, job title |
| Age | Graduation year, years of experience |
| Disability | Medical codes, accommodation flags |
| Religion | Name, dietary preferences, holidays |
| Socioeconomic status | Zip code, education level, device type |
| Geographic location | IP address, language, timezone |

---

## Step 2 — Data Bias Assessment

- [ ] Check training data distribution across protected groups
- [ ] Compare group sizes vs. population representation — flag underrepresented groups
- [ ] Check for historical bias in labels (e.g., past hiring decisions encoding past discrimination)
- [ ] Check for sampling bias in data collection method
- [ ] Document known data gaps or limitations

**Distribution check**:

| Group | Training % | Population % | Gap | Action Required |
|-------|-----------|-------------|-----|-----------------|
| Group A | | | | |
| Group B | | | | |
| Group C | | | | |

---

## Step 3 — Fairness Metric Selection

No single metric captures all fairness concerns. Select metrics appropriate to your use case and document why.

| Metric | Definition | When to Use |
|--------|-----------|-------------|
| **Demographic Parity** | P(positive prediction) equal across groups | When selection rates should be equal |
| **Equal Opportunity** | True positive rate equal across groups | When equal benefit is the priority |
| **Equalized Odds** | TPR and FPR equal across groups | When both error types should be equal |
| **Predictive Parity** | Precision equal across groups | When prediction trust should be equal |
| **Calibration** | P(Y=1 | score=s) equal across groups | When scores should mean the same thing per group |

**Domain guide**:
- Hiring / lending → Demographic parity + equal opportunity
- Healthcare → Equal opportunity + calibration
- Criminal justice / risk scoring → Equalized odds + calibration
- Content recommendation → Demographic parity

---

## Step 4 — Slice-Based Evaluation

> Aggregate metrics hide disparities. Always evaluate on slices.

- [ ] Evaluate model performance on each protected group separately
- [ ] Evaluate intersectional groups (e.g., age AND gender, not just each alone)
- [ ] Flag any group whose metric differs by more than **10%** from the overall metric
- [ ] Document per-slice results in the model card

**Evaluation table**:

| Slice | Accuracy | TPR (Recall) | FPR | Precision | N Samples | Flag |
|-------|----------|-------------|-----|-----------|-----------|------|
| Overall | | | | | | |
| Group A | | | | | | |
| Group B | | | | | | |
| A ∩ Group X | | | | | | |
| B ∩ Group X | | | | | | |

**Flag if**: Any group metric differs > 10% from overall metric.

---

## Step 5 — Mitigation (If Bias Detected)

| Stage | Strategy | How |
|-------|----------|-----|
| **Pre-processing** | Resampling | Oversample underrepresented groups |
| **Pre-processing** | Reweighting | Higher loss weight for underrepresented groups |
| **In-processing** | Fairness constraints | Add fairness term to loss function |
| **In-processing** | Adversarial debiasing | Train adversary to predict protected attribute |
| **Post-processing** | Threshold adjustment | Different decision thresholds per group |
| **Post-processing** | Calibration | Calibrate scores independently per group |

Document which strategy was applied and its measured effect on both fairness and overall performance.

---

## Step 6 — Documentation

- [ ] All protected attributes considered are listed
- [ ] Fairness metrics selected with rationale documented
- [ ] Per-slice evaluation results recorded
- [ ] Any bias detected and mitigation applied are documented
- [ ] Limitations of this audit are noted (attributes not tested, data gaps)
- [ ] Results entered in the model card (`model-card-template.md` → Bias & Fairness section)

---

## Step 7 — Sign-Off

| Role | Responsibility | Signed | Date |
|------|---------------|--------|------|
| Data Scientist | Conducted audit and documented results | | |
| Tech Lead | Reviewed methodology and results | | |
| Product Manager | Accepted risk level and mitigation approach | | |
| Legal / Compliance | Confirmed regulatory compliance | | |

---

## Ongoing Monitoring

Bias audit is not one-time — bias can drift as data changes.

- [ ] Configure fairness metrics in the production monitoring dashboard
- [ ] Schedule quarterly bias reviews
- [ ] Re-audit when training data changes significantly
- [ ] Re-audit after every retraining run
- [ ] Track fairness metrics over time for degradation

**Reference**: `monitoring-setup-guide.md` — add fairness metrics to Model Performance signals

---

## Common Pitfalls

| Pitfall | Prevention |
|---------|------------|
| Only checking aggregate metrics | Always evaluate on per-group slices |
| Ignoring intersectional groups | Test combinations, not just individual attributes |
| One-time audit only | Schedule recurring audits |
| No proxy variable check | Actively search for proxy correlations before modeling |
| Choosing one fairness metric | Use multiple metrics — document trade-offs honestly |
| Audit without documentation | Results must appear in model card |

---

**Cross-references**:
- `SKILL.md` — Phase 6 behaviors and Iron Rule #7
- `model-card-template.md` — Where audit results are recorded
- `ml-pipeline-checklist.md` — Phase 6 deployment checklist
- `monitoring-setup-guide.md` — Ongoing fairness monitoring
