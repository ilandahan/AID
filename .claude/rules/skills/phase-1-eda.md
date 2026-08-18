# Phase 1 — EDA: Data Gathering, Analysis & Dataset Creation

## Goal
Understand the data fully before any modeling decision is made.
No model. No hypothesis. No architecture. Data first.

## Mandatory Outputs
- [ ] Data audit report (schema, types, ranges, distributions)
- [ ] Quality issue log (each issue: type, column, count, decision)
- [ ] Cleaned/documented dataset ready for Phase 2

## Step-by-Step Behavior

### 1. Schema Profiling
For every column, document:
- Data type (actual vs. expected)
- Value range (min, max, unique count)
- Null rate (%)
- Sample values

### 2. Issue Classification
Separate issues into two distinct categories — handle them differently:

| Type | Definition | Examples | Action |
|------|-----------|---------|--------|
| **Impossible values** | Physically/logically invalid | age = -3, tenure = -10, date in 2087 | Remove or correct with documented rationale |
| **Statistical outliers** | Extreme but potentially valid | support_calls = 99, spend = $5,000 | Flag, investigate, cap with IQR or domain knowledge |

NEVER conflate these two categories. Document each separately.

### 3. Missing Value Analysis
For each column with nulls:
- Compute null rate
- Test if missingness correlates with the target variable
- Classify: MCAR / MAR / MNAR (if determinable)
- Document — do NOT impute yet (imputation happens in Phase 5)

### 4. Class Balance Check (Classification tasks)
- Compute target distribution
- Flag if minority class < 20% — record for Phase 3 metric selection
- Do NOT resample yet

### 5. Proxy Variable Check
Before finishing EDA, scan for features that may be proxies for protected attributes:
- Geographic features (zip code → race/income)
- Names → gender/ethnicity
- Device type → socioeconomic status
Document findings for Phase 2 risk assessment.

### 6. Derived Feature Check
Identify columns that are mathematically derived from others:
- `annual_spend = monthly_spend × 12` → flag as potential leakage
- Document ALL such relationships
These will be resolved in Phase 5.

## Output Format — Data Audit Report

```
## Data Audit Report

### Dataset Overview
- Rows: N | Columns: M | Target: [column]
- Class balance: [dist if classification]

### Schema
| Column | Type | Range | Null % | Notes |
|--------|------|-------|--------|-------|

### Impossible Values
| Column | Issue | Count | Decision |
|--------|-------|-------|---------|

### Statistical Outliers
| Column | Method | Threshold | Count | Decision |
|--------|--------|-----------|-------|---------|

### Missing Values
| Column | Null % | Correlation with Target | Classification |
|--------|--------|------------------------|---------------|

### Proxy Variable Risks
| Feature | Potential Proxy For | Risk Level |
|---------|-------------------|------------|

### Derived Features
| Feature | Derived From | Leakage Risk |
|---------|-------------|-------------|
```

## Phase Transition Gate → Phase 2

Do NOT move to Phase 2 until:
- [ ] All columns profiled
- [ ] All impossible values documented with decision
- [ ] All statistical outliers identified and noted
- [ ] Missing value patterns characterized
- [ ] Proxy variable scan completed
- [ ] Derived feature relationships documented

**Reference**: `references/ml-pipeline-checklist.md` → Phase 1 section
