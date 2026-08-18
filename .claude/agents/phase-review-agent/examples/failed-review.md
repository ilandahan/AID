# Example: Failed Phase Review (FAIL)

Phase 1 PRD review - incomplete deliverable

## Response

```json
{
  "verdict": "FAIL",
  "checklist": [
    {"item": "Problem statement linked to research", "status": "fail", "note": "No RES-XXX references", "location": "prd-dashboard.md:10-15"},
    {"item": "Success metrics defined", "status": "fail", "note": "Only 'users should find it useful' - not measurable", "location": "prd-dashboard.md:20"},
    {"item": "User stories follow format", "status": "fail", "note": "Stories 2,4,5 missing 'so that'. Story 3 is a task.", "location": "prd-dashboard.md:30-80"},
    {"item": "Each story has acceptance criteria", "status": "fail", "note": "Only 2 of 6 stories have AC", "location": "prd-dashboard.md:30-80"},
    {"item": "No technical implementation details", "status": "fail", "note": "Contains database queries (110-115) and React structure (120-130)", "location": "prd-dashboard.md:110-130"}
  ],
  "summary": "7 of 10 items failed. Needs substantial revision.",
  "blocking_issues": [
    "Add acceptance criteria to stories 1,3,5,6",
    "Remove technical details (database queries, component structure)",
    "Define measurable success metrics",
    "Add research references (RES-XXX)"
  ],
  "phase_specific": {"completeness_score": 35, "quality_score": 40, "ready_for_next_phase": false}
}
```

## Fix Required

1. Add acceptance criteria to each story
2. Remove database queries and component structure
3. Add measurable metrics
4. Create traceability links
