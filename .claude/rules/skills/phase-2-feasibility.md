# Phase 2 — Feasibility Assessment

## Goal
Decide whether ML is the right approach — and at what cost — before investing in modeling.

## Mandatory Outputs
- [ ] Feasibility report with explicit go/no-go recommendation
- [ ] Risk inventory (technical, ethical, regulatory)
- [ ] Bias inventory from EDA findings
- [ ] Cost-of-error definition (false positive vs. false negative asymmetry)

## The Core Questions

Answer all of these before recommending an approach:

### 1. Is ML actually needed?
- Can a rule or heuristic achieve 80% of the value?
- What's the cost/effort of rules vs. ML?
- Is the problem well-defined enough for ML to learn from?

### 2. What's the cost of being wrong?
Define explicitly — this drives everything in Phase 3:

| Error Type | Business Impact | Example |
|-----------|----------------|---------|
| False Positive | [cost] | Flagging loyal customer as churn risk |
| False Negative | [cost] | Missing a churner → lost revenue |
| Worse error type | → | This determines your primary metric |

### 3. What are the data constraints?
- Is there enough labeled data? (Classification: typically need 1K+ per class minimum)
- Is the data fresh enough to reflect current behavior?
- Are there features available at prediction time that weren't in training?

### 4. What are the regulatory/ethical constraints?
- GDPR / HIPAA / local data laws: what data can be used?
- Are protected attributes in the data? (From Phase 1 proxy scan)
- What explainability is required by law or business?

### 5. What's the deployment environment?
- Latency requirement? (< 100ms favors simpler models)
- Infrastructure available? (GPU vs. CPU, cloud vs. on-premise)
- Who maintains the model post-deployment?

## Decision Framework

```
Is labeled data sufficient AND problem well-defined?
  ├── No → Rules/heuristics first. Revisit after data collection.
  └── Yes → Continue.

Can rules/heuristics achieve >80% of value?
  ├── Yes → Rules recommended. ML only if gap is business-critical.
  └── No → ML justified. Continue.

Are ethical/regulatory constraints manageable?
  ├── No → Escalate before proceeding.
  └── Yes → Go.
```

## Output — Feasibility Report Structure

```
## Feasibility Report: [Project Name]

### Recommendation
GO / NO-GO / CONDITIONAL GO

### Rationale
[2-3 sentences explaining the recommendation]

### Cost of Error
- False Positive: [business impact]
- False Negative: [business impact]
- Primary concern: [which is worse and why]

### Approach Recommendation
[ML / Rules / Hybrid — with rationale]

### Constraints
- Data: [limitations]
- Regulatory: [applicable laws]
- Ethical: [risks from Phase 1 proxy scan]
- Infrastructure: [deployment constraints]

### Risks
| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|

### Conditions for GO
[If CONDITIONAL GO: what must be true before proceeding]
```

## Phase Transition Gate → Phase 3

Do NOT move to Phase 3 until:
- [ ] Explicit GO/NO-GO decision documented
- [ ] Cost of false positive vs. false negative defined
- [ ] Regulatory/ethical constraints identified
- [ ] Approach recommendation documented with rationale
