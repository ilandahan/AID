# Phase 4 — ML Architecture & Pipeline Design

## Goal
Blueprint the full system before writing implementation code.
Architecture decisions made here are expensive to reverse.

## Mandatory Outputs
- [ ] Architecture decision document (approach + rationale)
- [ ] Data flow diagram (source → features → training → serving)
- [ ] Versioning strategy (data, features, models, prompts)
- [ ] Monitoring signal specification (defined before development starts)
- [ ] Task breakdown ready for Phase 5

## Step 1 — Choose Model Architecture

For every architecture decision, document:
1. **Why this approach** — specific reasons for this use case
2. **Alternatives considered** — at least 2, with why rejected
3. **Trade-offs accepted** — what you're giving up

Do NOT accept "it's the most common choice" as a rationale.

### Architecture Selection Guide

**Classification / Regression**:
| Scenario | Starting Point |
|----------|---------------|
| Tabular data, < 100K rows | Logistic Regression or Gradient Boosting |
| Tabular data, > 100K rows | Gradient Boosting or Neural Network |
| Text as input | Pretrained LLM fine-tune or embedding + classifier |
| Time series | LSTM, Transformer, or statistical models (ARIMA/Prophet) |
| Mixed tabular + text | Embedding layer + tabular features concatenated |

**RAG vs. Fine-Tuning decision**:
- Use `references/rag-architecture-guide.md` → Decision Matrix
- Default to RAG when: < 10K docs, frequent updates, explainability needed
- Move to fine-tuning only when RAG's retrieval ceiling is confirmed

## Step 2 — Data Flow Design

Map the complete path from source to prediction:

```
[Data Source] → [Ingestion] → [Validation] → [Feature Store / Transform]
                                                         ↓
                                          [Training Pipeline]
                                                         ↓
                                          [Model Registry]
                                                         ↓
                                          [Serving Endpoint] → [User / System]
                                                         ↓
                                          [Monitoring Layer]
```

For each step, document:
- What happens
- Who owns it
- What can fail and how it's handled

## Step 3 — Versioning Strategy

Define before development:

| Artifact | Versioning Approach | Storage |
|----------|-------------------|---------|
| Raw data | Snapshot ID + date | Data lake / S3 |
| Features | Feature definition version | Feature store or snapshot |
| Models | Semantic versioning (1.2.0) | Model registry |
| Prompts | Semantic versioning (2.1.0) | Version control |
| Configs | Commit hash | Version control |

## Step 4 — Specify Monitoring Signals (Before Development)

Define what will be monitored before writing code — not after deployment.

Required signal categories:
1. **Data Quality**: null rates, schema violations, distribution drift
2. **Model Performance**: accuracy decay, prediction distribution drift, latency
3. **RAG Quality** (if applicable): retrieval relevance, hallucination rate
4. **Prompt Behavior** (if applicable): format compliance, refusal rate

For each signal: metric, threshold, window, alert severity.

**Reference**: `references/monitoring-setup-guide.md` for full signal catalog

## Step 5 — Task Breakdown

Break implementation into atomic tasks for Phase 5.
Each task should be:
- Completable in one session
- Independently testable
- Clearly sequenced (dependencies explicit)

Template:
```
## Task Breakdown

### Data & Features
- [ ] [Task 1] — Input: X, Output: Y, Depends on: —
- [ ] [Task 2] — Input: X, Output: Y, Depends on: Task 1

### Model Training
- [ ] [Task 3] — ...

### Evaluation
- [ ] [Task 4] — ...

### Integration
- [ ] [Task 5] — ...
```

## Architecture Decision Document Format

```
## Architecture Decision: [Name]

### Decision
[What we decided in one sentence]

### Context
[Why this decision needed to be made]

### Options Considered
1. [Option A] — Pros: ... | Cons: ... | Rejected because: ...
2. [Option B] — Pros: ... | Cons: ... | Rejected because: ...
3. [Chosen option] — Pros: ... | Cons: ... | Chosen because: ...

### Trade-offs Accepted
[What we're giving up with this choice]

### Reversibility
[How hard is this to change later]
```

## Phase Transition Gate → Phase 5

Do NOT move to Phase 5 until:
- [ ] Architecture documented with rationale and alternatives
- [ ] Data flow from source to serving mapped
- [ ] Versioning strategy defined for all artifact types
- [ ] Monitoring signals specified (metric, threshold, window, severity)
- [ ] Task breakdown complete and sequenced

**Reference**: `references/ml-pipeline-checklist.md` → Phase 4 section  
**Reference**: `references/rag-architecture-guide.md` (if RAG system)
