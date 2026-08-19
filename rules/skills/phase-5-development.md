# Phase 5 — Development & Validation

## Goal
Build, test, and validate — with no silent decisions.
Every choice must be documented. Every assumption must be tested.

## Mandatory Outputs
- [ ] Trained model meeting baseline threshold on all evaluation slices
- [ ] Feature engineering log (every decision documented)
- [ ] Evaluation results (overall + all pre-defined slices)
- [ ] Experiment record (config, data version, artifacts)
- [ ] Prompt test suite passing (if LLM involved)

---

## Feature Engineering Rules

These rules are MANDATORY. Violations are bugs, not style choices.

### Rule 1 — Document Every Feature
For every feature in the final set:
```
Feature: [name]
Source: [column or derivation formula]
Rationale: [why this feature, what it captures]
Imputation: [method used, rationale]
```

### Rule 2 — Imputation Must Be Context-Aware
Do NOT default to global median/mode without checking first.

**Decision flow for each column with missing values**:
```
Does missingness correlate with the target variable?
  ├── YES → Use group-level statistics (by target class or meaningful segment)
  │         Document: "Imputed with median per churn class because..."
  └── NO  → Global median/mode is acceptable
             Document: "Imputed with global median — missingness is random (MCAR)"
```

How to check: compare null indicator vs. target with chi-square or point-biserial correlation.

### Rule 3 — Recalculate Derived Features After Imputation
IMPORTANT: If any source feature was imputed, ALL features derived from it must be recalculated.

```
# WRONG — stale composite after imputation
df['login_freq'] = impute(df['login_freq'])
df['engagement'] = df['engagement']  # still uses pre-imputation values

# CORRECT — recalculate after imputation
df['login_freq'] = impute(df['login_freq'])
df['engagement'] = df['login_freq'] * 10 - df['days_since_login'] * 0.5  # fresh
```

### Rule 4 — Resolve Derived/Source Conflicts
When a derived feature and its source both exist → choose ONE, document why.

```
# NEVER keep both:
df['monthly_spend']   # source
df['annual_spend']    # = monthly × 12 → leakage AND multicollinearity

# Choose one:
# Keep monthly_spend — more granular, annual is just a scale transform
# OR keep annual_spend — if that's what stakeholders reference
# Document the choice
```

### Rule 5 — Check Multicollinearity Before Final Feature Set
- Compute correlation matrix
- Flag feature pairs with |r| > 0.85
- For each flagged pair: keep the one with higher business interpretability or predictive signal
- Document what was removed and why

### Rule 6 — Leakage Check (Final Gate)
Before training, verify:
- No target or target-derived column in feature set
- No future information (data not available at prediction time)
- No derived features that encode target information

---

## Training Rules

### Reproducibility
- Set random seeds before any split, shuffle, or initialization
- Log: data snapshot version, random seed, all hyperparameters, framework version

### Data Splits
- Apply split defined in Phase 3 — do not re-decide here
- Validate: no overlapping IDs between train/val/test
- For imbalanced classification: use stratified split

### Baseline Comparison (Iron Rule #1)
- Evaluate baseline on the same test set as all models
- All models must beat baseline to be considered
- If baseline beats all models: stop, re-examine features and problem definition

---

## Evaluation Rules

### Always Evaluate on Slices
A model that passes overall but fails a slice does NOT pass.
Use the slices defined in Phase 3.

### Confusion Matrix for Classification
Always produce and interpret the confusion matrix:
- What is the false negative rate? (missed positives)
- What is the false positive rate? (false alarms)
- Does this align with the cost-of-error definition from Phase 2?

### Calibration Check (Classification)
A model that assigns 97%+ of predictions to high/low confidence extremes is likely miscalibrated — even if accuracy looks good.

**Always check**:
- Plot predicted probability distribution — should not be bimodal or collapsed to extremes
- Compute calibration curve (reliability diagram): predicted probability bins vs. actual positive rate
- Flag if any bin deviates > 10% from the diagonal

**Warning signs**:
- Nearly all predictions clustered at > 0.8 or < 0.2 → overconfident model
- Flat probability distribution across bins → underconfident model
- High accuracy but poor calibration → model is decisive but not trustworthy for threshold tuning

**Fix options**: Platt scaling, isotonic regression, or temperature scaling post-training.

Document calibration results in the experiment record. A miscalibrated model must be noted in the model card under Limitations before Phase 6.

### Statistical Significance
If comparing two models: don't just compare point estimates.
For small test sets (< 1000), use bootstrap confidence intervals.

---

## Prompt Engineering Rules (if applicable)

Load: `skills/role-data-scientist/references/prompt-testing-patterns.md`

Required before any prompt goes to production:
- [ ] Version assigned (format: PROMPT_NAME_V{major}.{minor}.{patch})
- [ ] Happy path tests passing
- [ ] Edge case tests passing (empty, long, special characters)
- [ ] Adversarial tests passing (injection attempts)
- [ ] Consistency tests: same input → same output across 5+ runs
- [ ] Schema/format compliance > 99%
- [ ] Tested on the exact model that will be deployed

---

## Experiment Record Format

```
## Experiment: [Name] v[version]

### Hypothesis (from Phase 3)
If [approach], then [expected outcome], because [reasoning].

### Configuration
| Item | Value |
|------|-------|
| Data snapshot | [ID/hash] |
| Random seed | [value] |
| Framework | [ask user] |
| Key hyperparameters | [list] |

### Feature Set
| Feature | Source | Imputation | Rationale |
|---------|--------|-----------|-----------|

### Results
| Metric | Baseline | This Model | Delta | Slice | Pass |
|--------|----------|-----------|-------|-------|------|

### Decision
ACCEPT / REJECT / ITERATE — [Reasoning]

### Artifacts
- Model: [registry path]
- Data snapshot: [path]
- Code: [commit hash]
```

---

## Phase Transition Gate → Phase 6

Do NOT move to Phase 6 until:
- [ ] Model beats baseline on overall metric
- [ ] Model meets threshold on ALL evaluation slices
- [ ] Calibration check completed and documented (no collapsed probability distribution)
- [ ] Feature engineering log complete (every feature documented)
- [ ] Imputation decisions documented per column
- [ ] Derived feature conflicts resolved
- [ ] Multicollinearity check complete
- [ ] Leakage check passed
- [ ] Experiment record saved with artifacts
- [ ] Prompt test suite passing (if applicable)

**Reference**: `skills/role-data-scientist/references/ml-pipeline-checklist.md` → Phase 5 section  
**Reference**: `skills/role-data-scientist/references/prompt-testing-patterns.md` (if LLM involved)
