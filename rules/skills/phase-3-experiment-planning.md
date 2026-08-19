# Phase 3 — Experiment Planning

## Goal
Define the experiment completely before running it.
Write the hypothesis. Choose the metrics. Define success.
Iron Rule #8: No experiment without hypothesis.
Iron Rule #2: No training without validation strategy.

## Mandatory Outputs
- [ ] Experiment log entry (hypothesis + config)
- [ ] Evaluation metric definitions aligned to business KPIs
- [ ] Evaluation slice definitions
- [ ] Train/validation/test split strategy documented
- [ ] Baseline approach defined (Iron Rule #1)

## Step 1 — Write the Hypothesis First

Format (mandatory):
> **If** [specific change or approach], **then** [expected measurable outcome], **because** [reasoning].

Examples:
- "If we use tenure_months as the primary feature, then churn recall will exceed 0.85, because tenure is the strongest behavioral signal."
- "If we apply IQR capping to support_calls, then model F1 will improve by >2%, because extreme outliers inflate variance without signal."

Do NOT start training until a hypothesis is written.

## Step 2 — Choose Primary Evaluation Metric

Use this decision guide — primary metric must match the Phase 2 cost-of-error analysis:

| Scenario | Primary Metric | Why |
|----------|---------------|-----|
| Class imbalance + FN costs more | Recall / F2 | Catching all positives matters most |
| Class imbalance + FP costs more | Precision / F0.5 | Avoiding false alarms matters most |
| Balanced cost of errors | F1 | Harmonic balance |
| Need probability ranking | AUC-ROC | Threshold-independent |
| Business cost defined explicitly | Cost-weighted metric | Direct alignment |
| Regression, outliers matter | RMSE | Penalizes large errors |
| Regression, outliers don't matter | MAE | Robust to extremes |
| Ranking | NDCG / MRR | Position-aware |
| RAG generation | Groundedness + Faithfulness | Grounded outputs |

Document: primary metric, secondary metric, and why.

## Step 3 — Define Evaluation Slices

Aggregate metrics hide disparities. Define slices upfront.

Mandatory slice types:
- Protected attribute groups (from Phase 1 proxy scan + Phase 2 risk inventory)
- Data quality segments (rows with vs. without imputed values)
- Time periods (if temporal patterns exist)
- Business-meaningful segments (contract type, product tier, region)

A model that passes overall but fails a slice does NOT pass.

## Step 4 — Define Train/Validation/Test Split

Document before splitting:
- Split ratios (e.g., 70/15/15)
- Split method (random / stratified / time-based)
- Rationale for method choice
- IMPORTANT: Test set is reserved for final evaluation ONLY — never for tuning

For time-series data: use time-based split, NEVER random.

## Step 5 — Establish Baseline (Iron Rule #1)

The baseline must be:
- Simple (rule, heuristic, or dummy model)
- Evaluated on the same test set as all subsequent models
- Documented — all future experiments must beat this

Baseline ideas:
- "Predict churn if tenure < 6 months"
- "Predict majority class always"
- "Logistic regression with raw features, no tuning"

## Experiment Log Entry Format

```
## Experiment: [Name]

### Hypothesis
If [approach], then [expected outcome], because [reasoning].

### Configuration
| Item | Value |
|------|-------|
| Task type | Classification / Regression / ... |
| Primary metric | [metric + target threshold] |
| Secondary metric | [metric] |
| Split | [ratios + method] |
| Baseline | [approach + baseline score] |
| Evaluation slices | [list] |

### Expected Results
[What we expect to see if hypothesis is correct]

### Failure Criteria
[What would falsify the hypothesis]
```

## Phase Transition Gate → Phase 4

Do NOT move to Phase 4 until:
- [ ] Hypothesis written
- [ ] Primary and secondary metrics chosen with rationale
- [ ] Evaluation slices defined
- [ ] Train/val/test split strategy documented
- [ ] Baseline approach and evaluation method defined

**Reference**: `skills/role-data-scientist/references/ml-pipeline-checklist.md` → Phase 3 section
