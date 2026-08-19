# Good Analysis Example

This shows what a high-quality analysis output looks like.

---

## Input Summary

- **Feedback count**: 12 items
- **Date range**: 2025-01-01 to 2025-01-15
- **Roles covered**: PM (4), Developer (5), QA (3)
- **Phases covered**: Discovery (3), PRD (4), Tech Spec (3), Development (2)

---

## Analysis Output

```json
{
  "analysis_summary": {
    "feedback_count": 12,
    "date_range": "2025-01-01 to 2025-01-15",
    "overall_avg_rating": 3.8,
    "overall_avg_revisions": 2.1,
    "trend_vs_previous": {
      "rating": "+0.3",
      "revisions": "-0.5"
    }
  },

  "by_role_phase": [
    {
      "role": "product-manager",
      "phase": "discovery",
      "feedback_count": 3,
      "avg_rating": 4.3,
      "avg_revisions": 1.3
    },
    {
      "role": "developer",
      "phase": "development",
      "feedback_count": 4,
      "avg_rating": 3.5,
      "avg_revisions": 2.8
    }
  ],

  "patterns_found": {
    "positive": [
      {
        "id": "PAT-P01",
        "description": "Asking about data flow early identifies hidden stakeholders",
        "occurrences": 4,
        "avg_rating_when_present": 4.5,
        "avg_revisions_when_present": 1.0,
        "supporting_quotes": [
          "Data flow question helped me find the IT team",
          "Asking who touches this data uncovered compliance",
          "Would have missed finance without data flow question"
        ]
      },
      {
        "id": "PAT-P02",
        "description": "Writing test before implementation reduces revisions",
        "occurrences": 3,
        "avg_rating_when_present": 4.2,
        "avg_revisions_when_present": 1.5,
        "supporting_quotes": [
          "TDD caught the edge case early",
          "Test-first helped clarify requirements"
        ]
      }
    ],
    "negative": [
      {
        "id": "PAT-N01",
        "description": "Skipping acceptance criteria review leads to scope creep",
        "occurrences": 3,
        "avg_rating_when_present": 2.3,
        "avg_revisions_when_present": 4.7,
        "supporting_quotes": [
          "Had to rewrite because AC was ambiguous",
          "Scope changed three times - should have verified AC"
        ]
      }
    ]
  },

  "suggestions": [
    {
      "id": "SUG-001",
      "type": "skill_update",
      "confidence": 0.87,
      "target": {
        "file": "skills/memory-system/references/roles/product-manager/cumulative.md",
        "section": "High-Confidence Patterns"
      },
      "content": "- **Ask about data flow early**: \"Who else touches this data?\" consistently identifies hidden stakeholders. (Evidence: 4 sessions, 4.5 avg rating, 1.0 avg revisions)",
      "evidence": {
        "pattern_id": "PAT-P01",
        "occurrences": 4,
        "avg_rating": 4.5,
        "avg_revisions": 1.0
      }
    },
    {
      "id": "SUG-002",
      "type": "skill_update",
      "confidence": 0.82,
      "target": {
        "file": "skills/memory-system/references/phases/development/cumulative.md",
        "section": "High-Confidence Patterns"
      },
      "content": "- **Write failing test first**: TDD approach catches edge cases early and clarifies requirements before implementation. (Evidence: 3 sessions, 4.2 avg rating)",
      "evidence": {
        "pattern_id": "PAT-P02",
        "occurrences": 3,
        "avg_rating": 4.2,
        "avg_revisions": 1.5
      }
    },
    {
      "id": "SUG-003",
      "type": "skill_update",
      "confidence": 0.79,
      "target": {
        "file": "skills/memory-system/references/phases/prd/cumulative.md",
        "section": "Anti-Patterns"
      },
      "content": "- **Don't skip AC review**: Ambiguous acceptance criteria leads to scope creep and multiple rewrites. Always verify AC with stakeholders before dev. (Evidence: 3 sessions, 2.3 avg rating, 4.7 avg revisions)",
      "evidence": {
        "pattern_id": "PAT-N01",
        "occurrences": 3,
        "avg_rating": 2.3,
        "avg_revisions": 4.7
      }
    }
  ],

  "memory_candidates": [
    {
      "entry": "AID:PM:DISC:ASK \"Who else touches this data?\" to find hidden stakeholders",
      "role": "product-manager",
      "phase": "discovery",
      "type": "ASK",
      "confidence": 0.87,
      "evidence_summary": "4 occurrences, 4.5 avg rating, 1.0 avg revisions"
    }
  ],

  "trends_analysis": {
    "improving": [
      "PM/Discovery ratings improved 15% vs previous period",
      "Overall revision count decreased by 0.5"
    ],
    "declining": [
      "Developer/Development revisions increased slightly"
    ],
    "stable": [
      "QA phases maintaining consistent quality"
    ]
  },

  "meta": {
    "agent_version": "1.0",
    "analysis_timestamp": "2025-01-16T10:30:00Z",
    "processing_notes": "All patterns meet minimum thresholds. One memory candidate promoted."
  }
}
```

---

## Why This Is Good

### ✅ Evidence-Based Suggestions

Every suggestion includes:
- Pattern ID reference
- Occurrence count
- Rating/revision metrics
- Supporting quotes (anonymized)

### ✅ Appropriate Confidence Scores

- 0.87 for 4 occurrences with strong metrics
- 0.82 for 3 occurrences with good metrics
- 0.79 for negative pattern (conservative)

### ✅ Actionable Content

Suggestions are specific and actionable:
- "Ask about data flow early" - clear action
- "Write failing test first" - specific technique
- "Don't skip AC review" - clear anti-pattern

### ✅ Proper Memory Format

```
AID:PM:DISC:ASK "Who else touches this data?" to find hidden stakeholders
```
- Correct format: AID:ROLE:PHASE:TYPE
- Under 200 characters
- Actionable insight
- No project-specific content

### ✅ Meaningful Trends

Trends compare to previous period and identify:
- What's improving
- What's declining
- What's stable

### ✅ No Project Leakage

No mention of:
- Project names
- Company names
- Specific features
- Code snippets
