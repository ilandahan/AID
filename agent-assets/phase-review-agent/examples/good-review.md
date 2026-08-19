# Example: Good Phase Review (PASS)

Phase 1 PRD review for user authentication

## Response

```json
{
  "verdict": "PASS",
  "checklist": [
    {"item": "Problem statement linked to research", "status": "pass", "note": "Clear reference to RES-001, RES-003", "location": "prd-user-auth.md:12-18"},
    {"item": "User stories follow format", "status": "pass", "note": "All 8 stories follow As a/I want/So that format", "location": "prd-user-auth.md:45-120"},
    {"item": "Each story has acceptance criteria", "status": "pass", "note": "3-5 testable criteria each", "location": "prd-user-auth.md:45-120"},
    {"item": "No technical implementation details", "status": "pass", "note": "Focuses on WHAT not HOW", "location": "entire document"}
  ],
  "summary": "All critical items passed. Ready for Tech Spec.",
  "blocking_issues": [],
  "suggestions": ["Consider adding user personas", "Add simple user flow diagrams"],
  "phase_specific": {"completeness_score": 95, "quality_score": 92, "ready_for_next_phase": true}
}
```

## What Made It PASS

1. Specific evidence with file:line references
2. Actionable suggestions (not vague)
3. Objective assessment based on content
