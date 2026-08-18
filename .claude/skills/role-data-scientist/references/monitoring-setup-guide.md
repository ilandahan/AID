# Monitoring Setup Guide

Production monitoring for ML systems.
**Use in**: Phase 6 — Deploy to Production & Monitoring

> **Iron Rule #3: No deployment without monitoring**

---

## The 4 Signal Categories

Every ML deployment must monitor all 4 categories.

```
┌──────────────────────────────────────────────────────┐
│                  ML Monitoring                        │
├──────────────┬──────────────┬────────────┬───────────┤
│ Data Quality │    Model     │    RAG     │  Prompt   │
│              │ Performance  │  Quality   │ Behavior  │
└──────────────┴──────────────┴────────────┴───────────┘
```

Skip categories that don't apply (e.g., no RAG signals if not using retrieval).
Document why a category was skipped.

---

## 1. Data Quality Signals

Monitor the inputs to your model — garbage in, garbage out.

| Signal | Metric | Threshold | Window | Severity |
|--------|--------|-----------|--------|----------|
| Schema violations | Count of invalid records | > 0 | 1h | Critical |
| Null rate | % null per feature | > 5% | 1h | Warning |
| Distribution drift (PSI) | Population Stability Index | > 0.10 | 24h | Warning |
| Distribution drift (PSI) | Population Stability Index | > 0.25 | 24h | Critical |
| Volume anomaly | Record count vs. expected | ±50% | 1h | Warning |
| Data freshness | Time since last update | > SLA | 1h | Critical |

**Drift detection method guide**:
- Categorical features → PSI or Chi-Square test
- Continuous features → KS test or KL divergence
- Always compare against the training distribution as reference

---

## 2. Model Performance Signals

Monitor model outputs and accuracy over time.

| Signal | Metric | Threshold | Window | Severity |
|--------|--------|-----------|--------|----------|
| Accuracy decay | vs. deploy baseline | > 5% drop | 7d | Warning |
| Accuracy decay | vs. deploy baseline | > 10% drop | 7d | Critical |
| Prediction distribution drift | KL divergence on output | > 0.15 | 24h | Warning |
| Latency P50 | Inference time | > 200ms | 1h | Warning |
| Latency P95 | Inference time | > 500ms | 1h | Warning |
| Latency P99 | Inference time | > 1000ms | 1h | Critical |
| Error rate | Failed predictions / total | > 1% | 1h | Critical |

**When ground truth is available (even delayed)**:
- Compare predictions vs. actuals using rolling 7–14 day window
- Alert on sustained decline, not single-point drops

**When ground truth is NOT available**:
- Monitor prediction distribution for drift
- Monitor confidence score distribution
- Set up random human review sampling (1–5% of predictions)

---

## 3. RAG Quality Signals

*Only relevant for systems using retrieval-augmented generation.*
*Skip and document if not applicable.*

| Signal | Metric | Threshold | Window | Severity |
|--------|--------|-----------|--------|----------|
| Retrieval relevance | Avg relevance score of top-K | < 0.70 | 1h | Warning |
| Empty retrieval rate | Queries returning no results | > 10% | 1h | Warning |
| Hallucination rate | Ungrounded claims in responses | > 5% | 24h | Critical |
| Source coverage | % response supported by sources | < 90% | 24h | Warning |
| Index freshness | Time since last index update | > SLA | 1h | Warning |

**Reference**: `rag-architecture-guide.md` for retrieval architecture decisions

---

## 4. Prompt Behavior Signals

*Only relevant for systems using LLM-generated outputs.*
*Skip and document if not applicable.*

| Signal | Metric | Threshold | Window | Severity |
|--------|--------|-----------|--------|----------|
| Refusal rate | % of refused requests | > 10% | 1h | Warning |
| Format compliance | % correctly formatted outputs | < 95% | 1h | Warning |
| Output token count | Mean tokens per response | > 2000 | 1h | Warning |
| Cost per call | Average LLM cost | > budget | 24h | Warning |
| Timeout rate | % calls exceeding timeout | > 2% | 1h | Critical |

**Reference**: `prompt-testing-patterns.md` for prompt test suite design

---

## Alert Routing

| Severity | Route To | Response Time |
|----------|----------|---------------|
| Critical | On-call engineer + team channel | < 15 min |
| Warning | Team channel | < 4 hours |
| Info | Dashboard only | Next business day |

**Rule**: Dashboards without alerts don't catch 3am failures.
Every Warning-level signal must have an alert, not just a dashboard tile.

---

## Deploy-Time Baseline Recording

**Required at every deployment** — this is the reference for drift detection.

Record at deployment time:
- [ ] All model performance metrics (accuracy, F1, AUC-ROC as applicable)
- [ ] Input feature distributions per column
- [ ] Prediction score distribution
- [ ] Latency P50/P95/P99 under expected load
- [ ] Null rates per feature in production traffic

Without this baseline, drift detection has no reference to compare against.

---

## Configuration Template

```python
# Stack-agnostic structure — adapt to your monitoring tool
MONITORING_CONFIG = {
    "data_quality": {
        "schema_violations": {"threshold": 0, "window": "1h", "severity": "critical"},
        "null_rate": {"threshold": 0.05, "window": "1h", "severity": "warning"},
        "distribution_drift": {"threshold": 0.10, "window": "24h", "method": "psi", "severity": "warning"},
    },
    "model_performance": {
        "accuracy_decay": {"threshold": 0.05, "window": "7d", "baseline": "deploy_metric", "severity": "warning"},
        "latency_p95_ms": {"threshold": 500, "window": "1h", "severity": "warning"},
        "prediction_drift": {"threshold": 0.15, "window": "24h", "method": "kl_divergence", "severity": "warning"},
    },
    # Only include if using RAG
    "rag_quality": {
        "retrieval_relevance": {"threshold": 0.70, "window": "1h", "severity": "warning"},
        "hallucination_rate": {"threshold": 0.05, "window": "24h", "severity": "critical"},
        "empty_retrieval_rate": {"threshold": 0.10, "window": "1h", "severity": "warning"},
    },
    # Only include if using LLM outputs
    "prompt_behavior": {
        "refusal_rate": {"threshold": 0.10, "window": "1h", "severity": "warning"},
        "format_compliance": {"threshold": 0.95, "window": "1h", "severity": "warning"},
        "avg_output_tokens": {"threshold": 2000, "window": "1h", "severity": "warning"},
    },
}
```

---

## Common Pitfalls

| Pitfall | Prevention |
|---------|------------|
| Monitoring only model metrics | Monitor all 4 applicable signal categories |
| No deploy-time baseline | Record reference metrics at every deployment |
| Dashboard but no alerts | Every warning-level signal needs an alert |
| Too many alerts → alert fatigue | Tune thresholds, use severity tiers |
| Skipping RAG/Prompt signals | Explicitly document if skipped and why |

---

**Cross-references**:
- `SKILL.md` — Phase 6 behaviors and Iron Rule #3
- `ml-pipeline-checklist.md` — Phase 6 deployment checklist
- `model-card-template.md` — Monitoring section of model card
- `rag-architecture-guide.md` — RAG system design (if applicable)
- `prompt-testing-patterns.md` — Prompt test design (if applicable)
