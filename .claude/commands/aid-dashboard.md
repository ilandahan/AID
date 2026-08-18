# /aid-dashboard — Quality Dashboard

Generate a quality dashboard report with metrics and visualizations.

## Skills Loaded

This command loads:
- `skills/memory-system/SKILL.md`

## When to Use

- Want a quick visual overview of AID quality metrics
- Weekly or monthly quality review
- Sharing progress with stakeholders

## Process

1. **Gather metrics**
   - Session ratings from `~/.aid/feedback/`
   - Revision counts per session
   - Phase completion times
   - Quality check scores

2. **Generate dashboard**
   - Overall health score
   - Trend charts (rating over time)
   - Phase-by-phase breakdown
   - Role-by-role comparison

## Options

| Option | Purpose |
|--------|---------|
| `/aid-dashboard` | Default: last 30 days |
| `/aid-dashboard --days 14` | Last 14 days |
| `/aid-dashboard --days 90` | Last 90 days |

## Output

```
AID Quality Dashboard (Last 30 Days)

Overall Health: [X]/5 [trend arrow]

Session Metrics:
  Total sessions: [N]
  Avg rating: [X]/5
  Avg revisions: [X]

Quality Trends:
  [sparkline or bar chart representation]

Top Improvement Areas:
  1. [area] — [suggestion]
  2. [area] — [suggestion]
```

## Related Commands

- `/aid-analyze` — Detailed pattern analysis
- `/aid-recommendations` — Actionable suggestions
- `/aid-improve` — Run improvement cycle
