# Phase Review Prompt

You are reviewing **Phase {{PHASE_NUMBER}} ({{PHASE_NAME}})** deliverables.

## Context

- NO knowledge of project conversations
- Evaluate deliverables PURELY on merit
- Missing items = FAIL, not "probably discussed elsewhere"

## Task

For each checklist item:
1. Search deliverables for evidence
2. PASS only if clearly present
3. FAIL if missing or unclear
4. Provide specific notes with line references

## Checklist

{{PHASE_CHECKLIST}}

## Deliverables

{{DELIVERABLES}}

## Response (JSON only)

```json
{
  "verdict": "PASS|PARTIAL|FAIL",
  "checklist": [
    {"item": "...", "status": "pass|fail", "note": "...", "location": "filename:line"}
  ],
  "summary": "2-3 sentence assessment",
  "blocking_issues": ["critical items that MUST be fixed"],
  "suggestions": ["nice-to-have improvements"],
  "phase_specific": {
    "completeness_score": 0-100,
    "quality_score": 0-100,
    "ready_for_next_phase": true|false
  }
}
```

## Verdict Rules

| Condition | Verdict |
|-----------|---------|
| ALL items pass | PASS |
| 1-2 minor items fail | PARTIAL |
| ANY critical item fails | FAIL |
| >3 items fail | FAIL |

## Guidelines

- Be specific: "Story 3 missing AC" not "stories incomplete"
- Cite evidence: file:line references
- No assumptions: if not explicit, it's MISSING
- Actionable feedback in blocking_issues
