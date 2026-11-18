---
description: "View and manage recommendations for improving AID skills based on session feedback"
---

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
   - Run `python "${CLAUDE_PLUGIN_ROOT}/hooks/aid_session.py" memory-preview` and show its
     queue, ordered by priority

2. **Display recommendations**
   - Show each recommendation: id, priority, target file and proposed change

3. **User actions**
   - Accept — `python "${CLAUDE_PLUGIN_ROOT}/hooks/aid_session.py" memory-apply <id>`.
     Claude Code asks the user to confirm. It only appends to a role or phase
     `cumulative.md` in `skills/memory-system/references/`; anything else is refused.
     Skill-wide recommendations (no learnings file) are shown but cannot be applied by the tool.
   - Reject — `python "${CLAUDE_PLUGIN_ROOT}/hooks/aid_session.py" memory-reject <id>` (no prompt)
   - Defer — leave it in the queue (`$AID_HOME/recommendations/queue.json`)

   Run each command exactly in that shape (see `commands/aid-improve.md`). Never edit a
   skill file another way, and never work around a refusal or a declined prompt.

## Output

```
AID Skill Recommendations

Pending: [N] recommendations

1. [HIGH] Update Phase 4 TDD guidance
   Source: 3 sessions reported weak test assertions
   Suggestion: Add assertion strength examples to test-driven skill
   Action: accept / reject / defer

2. [MEDIUM] Improve Phase 1 user story format
   Source: 2 sessions had unclear acceptance criteria
   Suggestion: Add Gherkin examples to aid-prd skill
   Action: accept / reject / defer
```

## Related Commands

- `/aid-analyze` — Detailed quality analysis
- `/aid-dashboard` — Quality dashboard
- `/aid-improve` — Run full improvement cycle
