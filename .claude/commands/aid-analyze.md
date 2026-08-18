# /aid-analyze — Quality Analysis

Run full quality analysis with metrics and patterns across AID sessions.

## Skills Loaded

This command loads:
- `skills/memory-system/SKILL.md`

## When to Use

- Want to see quality trends across sessions
- Analyzing which phases or roles have recurring issues
- Looking for patterns in feedback data

## Process

1. **Collect data**
   - Read feedback from `~/.aid/feedback/pending/` and `~/.aid/feedback/processed/`
   - Read metrics from `~/.aid/metrics/trends.json` (if exists)

2. **Analyze patterns**
   - Average session rating by role and phase
   - Most common revision reasons
   - Quality score trends over time
   - Phase gate pass/fail rates

3. **Generate report**
   - Display metrics dashboard
   - Highlight improvement areas
   - Compare current vs. historical performance

## Output

```
AID Quality Analysis

Sessions analyzed: [N]
Average rating: [X]/5
Average revisions per session: [X]

By Role:
  Developer: [X]/5 ([N] sessions)
  PM: [X]/5 ([N] sessions)
  ...

By Phase:
  Discovery: [X]/5
  PRD: [X]/5
  ...

Patterns:
  - [pattern 1]
  - [pattern 2]
```

## Related Commands

- `/aid-dashboard` — Visual dashboard report
- `/aid-recommendations` — Actionable improvement suggestions
- `/aid-improve` — Run full improvement cycle
