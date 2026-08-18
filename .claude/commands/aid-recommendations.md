# /aid-recommendations — Skill Update Recommendations

View and manage recommendations for improving AID skills based on session feedback.

## Skills Loaded

This command loads:
- `skills/memory-system/SKILL.md`

## When to Use

- After running `/aid-analyze` or `/aid-improve`
- Want to see what skill improvements are pending
- Reviewing and applying learned improvements

## Process

1. **Load recommendations**
   - Read pending recommendations from memory system
   - Sort by impact score (highest first)

2. **Display recommendations**
   - Show each recommendation with context
   - Show which sessions/feedback generated it
   - Show estimated impact

3. **User actions**
   - Accept — apply the recommendation
   - Reject — dismiss with reason
   - Defer — revisit later

## Output

```
AID Skill Recommendations

Pending: [N] recommendations

1. [HIGH IMPACT] Update Phase 4 TDD guidance
   Source: 3 sessions reported weak test assertions
   Suggestion: Add assertion strength examples to test-driven skill
   Action: accept / reject / defer

2. [MEDIUM IMPACT] Improve Phase 1 user story format
   Source: 2 sessions had unclear acceptance criteria
   Suggestion: Add Gherkin examples to aid-prd skill
   Action: accept / reject / defer
```

## Related Commands

- `/aid-analyze` — Detailed quality analysis
- `/aid-dashboard` — Quality dashboard
- `/aid-improve` — Run full improvement cycle
