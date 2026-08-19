# Bad Analysis Example

This shows what NOT to do when analyzing feedback.

---

## ❌ Example 1: Project-Specific Information Leaked

```json
{
  "patterns_found": {
    "positive": [
      {
        "id": "PAT-P01",
        "description": "Asking about the payment API integration helped identify Stripe dependencies",
        "supporting_quotes": [
          "The Acme Corp payment flow needed Stripe webhooks",
          "John mentioned we need PCI compliance"
        ]
      }
    ]
  }
}
```

### Why It's Bad

- ❌ "payment API integration" - project-specific feature
- ❌ "Stripe" - specific vendor
- ❌ "Acme Corp" - company name
- ❌ "John" - person's name
- ❌ "PCI compliance" - domain-specific term

### How to Fix

```json
{
  "patterns_found": {
    "positive": [
      {
        "id": "PAT-P01",
        "description": "Asking about third-party dependencies identifies integration requirements",
        "supporting_quotes": [
          "Third-party service question helped find dependencies",
          "Compliance requirements emerged from integration discussion"
        ]
      }
    ]
  }
}
```

---

## ❌ Example 2: Suggestions Without Evidence

```json
{
  "suggestions": [
    {
      "id": "SUG-001",
      "type": "skill_update",
      "confidence": 0.90,
      "content": "Always document your code thoroughly",
      "evidence": {}
    }
  ]
}
```

### Why It's Bad

- ❌ No evidence object or empty evidence
- ❌ High confidence (0.90) with no supporting data
- ❌ Vague suggestion ("thoroughly" is subjective)
- ❌ No pattern ID reference

### How to Fix

```json
{
  "suggestions": [
    {
      "id": "SUG-001",
      "type": "skill_update",
      "confidence": 0.72,
      "content": "Add inline comments explaining WHY, not WHAT, for complex logic blocks",
      "evidence": {
        "pattern_id": "PAT-P03",
        "occurrences": 3,
        "avg_rating": 4.0,
        "avg_revisions": 1.8
      }
    }
  ]
}
```

---

## ❌ Example 3: Invalid Memory Entry Format

```json
{
  "memory_candidates": [
    {
      "entry": "Remember to check stakeholders in the discovery phase for the user management feature",
      "confidence": 0.85
    },
    {
      "entry": "AID:PRODUCT_MANAGER:DISCOVERY:ACTION Check stakeholders early in the process to ensure nothing is missed and all relevant parties are included in discussions",
      "confidence": 0.80
    }
  ]
}
```

### Why It's Bad

Entry 1:
- ❌ Doesn't follow AID:ROLE:PHASE:TYPE format
- ❌ Project-specific ("user management feature")
- ❌ Vague ("remember to check")

Entry 2:
- ❌ Wrong role code (PRODUCT_MANAGER vs PM)
- ❌ Wrong phase code (DISCOVERY vs DISC)
- ❌ Wrong type code (ACTION vs DO/DONT/ASK/CHECK)
- ❌ Way over 200 characters

### How to Fix

```json
{
  "memory_candidates": [
    {
      "entry": "AID:PM:DISC:CHECK Verify all stakeholder groups identified before phase gate",
      "role": "product-manager",
      "phase": "discovery",
      "type": "CHECK",
      "confidence": 0.85,
      "evidence_summary": "5 occurrences, 4.2 avg rating"
    }
  ]
}
```

---

## ❌ Example 4: Inflated Confidence Scores

```json
{
  "patterns_found": {
    "positive": [
      {
        "id": "PAT-P01",
        "description": "Using TDD helps",
        "occurrences": 2,
        "avg_rating_when_present": 3.5
      }
    ]
  },
  "suggestions": [
    {
      "id": "SUG-001",
      "confidence": 0.95,
      "content": "Always use TDD"
    }
  ]
}
```

### Why It's Bad

- ❌ Only 2 occurrences (minimum is 3 for positive patterns)
- ❌ Average rating 3.5 is below 4.0 threshold
- ❌ Confidence 0.95 is way too high for this evidence
- ❌ "Always" is too absolute

### How to Fix

Either don't suggest (insufficient evidence), or:

```json
{
  "suggestions": [
    {
      "id": "SUG-001",
      "confidence": 0.62,
      "content": "Consider TDD for complex logic - early evidence suggests benefit",
      "evidence": {
        "pattern_id": "PAT-P01",
        "occurrences": 2,
        "avg_rating": 3.5
      }
    }
  ],
  "warnings": [
    {
      "type": "low_sample_size",
      "message": "TDD pattern based on only 2 occurrences - needs more data",
      "affected_items": ["SUG-001"]
    }
  ]
}
```

---

## ❌ Example 5: Missing Required Fields

```json
{
  "analysis_summary": {
    "feedback_count": 8
  },
  "suggestions": [
    {
      "content": "Do better planning"
    }
  ]
}
```

### Why It's Bad

- ❌ Missing date_range in summary
- ❌ Missing avg_rating and avg_revisions
- ❌ Missing trend comparison
- ❌ Suggestion missing: id, type, confidence, target, evidence
- ❌ Suggestion content is vague

### How to Fix

Include all required fields per the template.

---

## ❌ Example 6: Contradicting Suggestions

```json
{
  "suggestions": [
    {
      "id": "SUG-001",
      "content": "Write detailed technical specs before coding",
      "confidence": 0.75
    },
    {
      "id": "SUG-002",
      "content": "Start coding early to discover requirements",
      "confidence": 0.72
    }
  ]
}
```

### Why It's Bad

- ❌ SUG-001 says spec first
- ❌ SUG-002 says code first
- ❌ These contradict each other
- ❌ Agent should detect and flag conflicts

### How to Fix

```json
{
  "suggestions": [],
  "warnings": [
    {
      "type": "conflicting_patterns",
      "message": "Evidence shows both 'spec first' and 'code first' approaches with similar success - cannot determine which is better",
      "affected_items": ["PAT-P01", "PAT-P02"]
    }
  ]
}
```

---

## Summary: Red Flags

| Issue | Detection |
|-------|-----------|
| Project names | Any proper nouns that could identify a project |
| Person names | Any human names |
| Company names | Any organization names |
| No evidence | Empty or missing evidence object |
| High confidence + low data | Confidence > 0.8 with < 4 occurrences |
| Wrong format | Memory entries not matching AID:X:X:X pattern |
| Too long | Memory entries > 200 characters |
| Contradictions | Suggestions that conflict with each other |
| Vague content | "better", "more", "thoroughly" without specifics |
