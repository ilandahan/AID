# Analysis Rules

Rules for analyzing feedback and generating improvement suggestions.

---

## Confidence Score Calculation

### Base Score (0.5)

Start with 0.5 and adjust based on:

| Factor | Adjustment |
|--------|------------|
| 3-4 occurrences | +0.10 |
| 5-7 occurrences | +0.20 |
| 8+ occurrences | +0.30 |
| Low rating variance (σ < 0.5) | +0.10 |
| High rating variance (σ > 1.0) | -0.10 |
| Clear action → result | +0.10 |
| Vague correlation | -0.05 |

### Confidence Thresholds

| Score | Classification | Action |
|-------|---------------|--------|
| 0.85+ | High confidence | Safe to auto-apply |
| 0.70-0.84 | Medium confidence | Suggest with strong recommendation |
| 0.60-0.69 | Low confidence | Suggest as experimental |
| < 0.60 | Insufficient | Do not suggest |

---

## Pattern Detection Rules

### Positive Pattern Criteria

A positive pattern MUST have:
- ✅ 3+ occurrences in feedback
- ✅ Average rating ≥ 4.0 when pattern present
- ✅ Average revisions ≤ 2 when pattern present
- ✅ Mentioned in "what worked" at least once

### Negative Pattern Criteria

A negative pattern MUST have:
- ✅ 2+ occurrences in feedback
- ✅ Average rating ≤ 2.5 when pattern present OR
- ✅ Average revisions ≥ 4 when pattern present
- ✅ Mentioned in "what didn't work" at least once

### Conflicting Pattern Rules

If same behavior appears in both positive AND negative:
1. Do NOT generate a suggestion
2. Flag for human review
3. Note the conflict in output
4. Suggest more data collection

---

## Suggestion Generation Rules

### Skill Update Suggestions

Must include:
- Target file path (e.g., `skills/memory-system/references/roles/developer/cumulative.md`)
- Target section (e.g., "High-Confidence Patterns")
- Exact content to add
- Evidence reference (pattern ID, occurrences, ratings)

Must NOT:
- Reference specific projects
- Include code snippets
- Mention company names
- Be longer than 3 sentences

### Memory Candidate Suggestions

Must include:
- Full entry in `AID:{ROLE}:{PHASE}:{TYPE} {insight}` format
- Role, phase, and type classification
- Evidence summary
- Confidence score

Must NOT:
- Exceed 200 characters
- Reference specific contexts
- Be vague or non-actionable

---

## Clustering Rules

### Role × Phase Clustering

Primary grouping for analysis:
```
developer × discovery
developer × prd
developer × tech-spec
...
```

### Rating-Based Clustering

| Cluster | Rating Range | Label |
|---------|--------------|-------|
| Poor | 1.0 - 2.4 | Needs improvement |
| Acceptable | 2.5 - 3.4 | Room to grow |
| Good | 3.5 - 4.4 | Working well |
| Excellent | 4.5 - 5.0 | Best practices |

### Revision-Based Clustering

| Cluster | Revisions | Label |
|---------|-----------|-------|
| Smooth | 0-1 | First-time-right |
| Normal | 2-3 | Expected iteration |
| Problematic | 4+ | Process issue |

---

## Text Analysis Keywords

### Positive Indicators

```
helped, useful, effective, clear, exactly, perfect,
worked well, great, excellent, smooth, fast, easy
```

### Negative Indicators

```
missed, forgot, overlooked, unclear, confusing,
incomplete, wrong, had to fix, needed to change,
missing, should have, didn't work
```

### Methodology Mentions

```
SCQ, stakeholder, TDD, test-first, acceptance criteria,
user story, tech spec, architecture, phase gate,
WHY, validation, research, discovery
```

---

## Output Validation

Before returning results, verify:

- [ ] All suggestions have evidence
- [ ] No project-specific information leaked
- [ ] Confidence scores are within valid range
- [ ] Memory entries fit format and length
- [ ] No conflicting suggestions
- [ ] Trends are based on real comparisons
