# ML Pipeline Checklist

Step-by-step checklist for building production ML pipelines.
Aligned to the 6 Data Scientist phases in `SKILL.md`.

---

## Phase 1 — EDA: Data Validation

- [ ] Profile schema: column names, types, expected ranges
- [ ] Validate schema at ingestion — fail fast on violations
- [ ] Check null rates per column — document patterns (random vs. systematic)
- [ ] Separate **impossible values** (negative age, future dates) from **statistical outliers** (IQR/z-score extremes)
- [ ] Check for duplicate rows
- [ ] Check class balance for classification targets
- [ ] Detect distribution drift vs. reference dataset (PSI or KL divergence)
- [ ] Verify data freshness — is the source current?
- [ ] Document data lineage: source, collection method, access controls
- [ ] Identify proxy variables that could cause leakage or bias

**Output**: Data audit report  
**Next**: `SKILL.md` Phase 2 — Feasibility Assessment

---

## Phase 3 — Experiment Planning: Baseline & Evaluation

- [ ] Write hypothesis before running any experiment
- [ ] Establish a simple baseline (rule, heuristic, or dummy model)
- [ ] Measure baseline on the same evaluation set as all future models
- [ ] Record baseline metrics — all models must beat this
- [ ] Define evaluation metrics aligned to business KPIs
- [ ] Define evaluation slices (segments where performance must hold)
- [ ] Specify train / validation / test split strategy

**Iron Rule #1**: No model without baseline  
**Iron Rule #2**: No training without validation strategy  
**Iron Rule #8**: No experiment without hypothesis

---

## Phase 4 — ML Architecture: Training Pipeline Design

- [ ] Set random seeds for reproducibility
- [ ] Define train / validation / test split with strict separation
- [ ] Verify no data leakage between splits
- [ ] Log hyperparameters and configuration
- [ ] Track experiment lineage: data version, code commit, config
- [ ] Reserve test set for final evaluation only — never for tuning
- [ ] Set up early stopping or convergence criteria

---

## Phase 5 — Development & Validation: Feature Engineering

- [ ] Start with simple features before complex ones
- [ ] Version feature definitions alongside code
- [ ] Document each feature: definition, source, rationale
- [ ] Check for feature leakage — no target information in features
- [ ] After imputation: recalculate all derived features (never leave stale composites)
- [ ] When derived feature and its source both exist → choose one, document why
- [ ] Check multicollinearity across final feature set
- [ ] Ensure feature computation is reproducible

**Imputation rules**:
- Check if missingness correlates with target before choosing strategy
- If correlated → use group-level statistics (by target class or segment)
- If random → median/mode imputation is acceptable
- Document imputation method and rationale for every column

---

## Phase 5 — Development & Validation: Evaluation

- [ ] Evaluate on overall test set AND all pre-defined slices
- [ ] Compare against baseline — improvement must be meaningful
- [ ] For imbalanced classification: use F1, AUC-ROC, Precision-Recall curve
- [ ] Check confusion matrix — understand false positive vs. false negative costs
- [ ] Check for bias across protected attributes
- [ ] Measure latency under expected production load
- [ ] Document evaluation results

**Reference**: `bias-audit-checklist.md` for full fairness evaluation

---

## Phase 6 — Deploy: Model Registration & Release

- [ ] Register model in model registry with version
- [ ] Attach evaluation metrics and experiment artifacts
- [ ] Document intended use and out-of-scope uses
- [ ] Assign ownership and maintenance responsibility
- [ ] Complete model card (see `model-card-template.md`)
- [ ] Complete bias audit (see `bias-audit-checklist.md`)
- [ ] Configure monitoring for all 4 signal categories (see `monitoring-setup-guide.md`)
- [ ] Set up alerting for threshold violations
- [ ] Test rollback procedure end-to-end
- [ ] Record deploy-time metrics as monitoring baseline

**Iron Rule #3**: No deployment without monitoring  
**Iron Rule #6**: No prediction without explainability  
**Iron Rule #7**: No model without bias audit

---

## Pipeline Flow

```
Phase 1: Source → Ingest → Validate → Audit
                                         ↓
Phase 3: Define Hypothesis → Baseline → Metrics → Slices
                                                      ↓
Phase 4: Architecture → Data Flow → Feature Store
                                         ↓
Phase 5: Train → Validate → Evaluate → Register
                                            ↓
Phase 6: Deploy → Monitor → Alert → Retrain trigger
```

---

## Common Pitfalls

| Pitfall | Prevention |
|---------|------------|
| Silent imputation | Document every imputation method and rationale |
| Stale derived features after imputation | Recalculate all composites after imputation |
| Keeping derived + source features | Choose one, document why |
| Training on test data | Strict split separation, verified before training |
| Overfitting to validation set | Use test set only once for final evaluation |
| Non-reproducible results | Fixed seeds, versioned data, logged configs |
| Missing baseline comparison | Always train simple model first |
| Deploying without monitoring | Monitoring is a deployment prerequisite |

---

**Cross-references**:
- `SKILL.md` — Phase behaviors and Iron Rules
- `model-card-template.md` — Required for Phase 6 release
- `bias-audit-checklist.md` — Required before Phase 6 deployment
- `monitoring-setup-guide.md` — Required for Phase 6 observability
