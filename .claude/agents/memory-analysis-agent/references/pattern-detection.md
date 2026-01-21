# Pattern Detection Heuristics

How to identify meaningful patterns from feedback data.

---

## Text Analysis Pipeline

### Step 1: Tokenize Qualitative Feedback

Extract key phrases from:
- "What worked well" responses
- "What could be improved" responses
- Additional notes

### Step 2: Normalize Terms

Map variations to canonical forms:

| Variations | Canonical |
|------------|-----------|
| stakeholder, stakeholders, people involved | `stakeholder` |
| test, tests, testing, TDD | `testing` |
| missed, forgot, overlooked, didn't include | `missing` |
| unclear, confusing, ambiguous | `unclear` |

### Step 3: Count Co-occurrences

Track which terms appear together with:
- High ratings (4-5)
- Low ratings (1-2)
- High revisions (4+)
- Low revisions (0-1)

---

## Semantic Clustering

### Methodology Concepts

| Cluster | Keywords |
|---------|----------|
| Research | stakeholder, interview, competitive, market, problem |
| Requirements | user story, acceptance criteria, scope, requirement |
| Architecture | API, schema, data model, service, component |
| Implementation | code, function, test, TDD, refactor |
| Quality | bug, defect, coverage, validation, edge case |

### Action Concepts

| Cluster | Keywords |
|---------|----------|
| Asking | ask, question, verify, confirm, check with |
| Creating | write, create, draft, generate, build |
| Reviewing | review, check, validate, ensure, verify |
| Missing | forgot, missed, overlooked, didn't, should have |

---

## Correlation Analysis

### Direct Correlation

Look for patterns where:
```
IF feedback mentions X
AND rating >= 4.0
AND revisions <= 2
THEN X is a positive pattern
```

### Inverse Correlation

Look for patterns where:
```
IF feedback mentions "didn't do X"
AND rating <= 2.5
AND revisions >= 4
THEN X might be important to do
```

---

## Statistical Thresholds

### Minimum Sample Sizes

| Analysis Type | Minimum |
|--------------|---------|
| Overall trends | 5 feedback items |
| Role-specific patterns | 3 feedback items per role |
| Phase-specific patterns | 3 feedback items per phase |
| Role × Phase specific | 2 feedback items |

### Significance Thresholds

| Metric | Significant Difference |
|--------|----------------------|
| Rating difference | ≥ 0.5 points |
| Revision difference | ≥ 1.5 revisions |
| Occurrence rate | ≥ 30% of feedback |

---

## Pattern Templates

### Template 1: Action Success

```
Pattern: Doing [ACTION] leads to [OUTCOME]
Evidence: [N] sessions, [RATING] avg rating
Suggestion: AID:{ROLE}:{PHASE}:DO [ACTION]
```

### Template 2: Missing Check

```
Pattern: Not [CHECKING] leads to [PROBLEM]
Evidence: [N] sessions mentioned missing [ITEM]
Suggestion: AID:{ROLE}:{PHASE}:CHECK [CHECKING]
```

### Template 3: Useful Question

```
Pattern: Asking [QUESTION] helps [OUTCOME]
Evidence: [N] sessions, [RATING] avg rating
Suggestion: AID:{ROLE}:{PHASE}:ASK [QUESTION]
```

### Template 4: Anti-Pattern

```
Pattern: [ACTION] leads to [NEGATIVE_OUTCOME]
Evidence: [N] sessions, [LOW_RATING] avg rating, [HIGH_REVISIONS] revisions
Suggestion: AID:{ROLE}:{PHASE}:DONT [ACTION]
```

---

## Edge Case Handling

### Too Few Samples

If < 3 feedback items for a category:
- Mark all patterns as "low confidence"
- Include disclaimer in output
- Suggest waiting for more data

### Conflicting Evidence

If same pattern has both positive and negative associations:
- Do NOT generate suggestion
- Flag for human review
- Note both pieces of evidence

### No Clear Patterns

If no patterns meet thresholds:
- Return empty suggestions array
- Provide summary statistics only
- Suggest possible reasons (data too diverse, etc.)

### Outliers

If one feedback item is drastically different:
- Check if it's an outlier (Tukey's method)
- If outlier, exclude from pattern detection
- Note exclusion in analysis
