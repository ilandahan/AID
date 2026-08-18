# Load-Bearing Assumptions

Every pipeline step encodes assumptions about model limitations. As models improve,
these assumptions may become outdated. Review quarterly.

Source: "Load-bearing assumptions deserve testing" — Anthropic, Harness Design (March 2026)

---

## Assumptions by Step

| # | Assumption | Step It Affects | Why We Believe It | How to Test | Last Verified |
|---|-----------|----------------|-------------------|-------------|---------------|
| 1 | Self-review is biased — models praise their own work | CODE_REVIEW, TEST_REVIEW | Anthropic article + observed score inflation | Run inline review vs sub-agent review on same code, compare scores | Not yet |
| 2 | Human fixes are more reliable than auto-fix | FIX_CODE, FIX_TESTS | Model can introduce regressions when auto-fixing | Enable auto-fix on 10 tasks, compare iteration count and final scores | Not yet |
| 3 | 3 code review iterations is sufficient | max_iterations.code_review | Empirical: issues usually resolve in 2 | Track actual iterations — if >50% reach max, increase | Not yet |
| 4 | Sequential steps are better than parallel | Step ordering | Fixing code before testing prevents wasted test-writing | Run parallel variant, compare total cost and final quality | Not yet |
| 5 | Code review must happen before tests | CODE_REVIEW → TDD order | Catching security/quality issues early saves test rework | Swap order on 5 tasks, measure rework rate | Not yet |
| 6 | Sub-agent isolation improves review quality | All review steps | Anthropic article: context causes confirmation bias | Run non-isolated review (inline), compare severity distribution | Not yet |
| 7 | Binary PASS/FAIL is the right gate mechanism | CODE_REVIEW, TEST_REVIEW | Simple, decisive, no ambiguity | Now upgraded to numeric scoring — monitor if threshold tuning is needed | Sprint 1 |
| 8 | Opus 4.6 needs the same step decomposition | All steps | Untested — article suggests Opus can sustain longer tasks | Create simplified pipeline (fewer steps), compare output quality | Not yet |
| 9 | Review criteria preview improves first-pass quality | DEVELOP step | Article: "criteria steer outputs" | Compare first-pass review scores before/after criteria preview | Sprint 1 |
| 10 | Skepticism prompting improves review quality | CODE_REVIEW, TEST_REVIEW | Article: "evaluators respond better to skepticism prompting" | Compare score distributions before/after skepticism prompts | Sprint 1 |

---

## How to Test an Assumption

1. **Define the experiment**: What exactly will you change?
2. **Define the metric**: What will you measure? (scores, iterations, cost, time)
3. **Run A/B**: Same task, different pipeline config
4. **Record results**: Add to `history.json` with experiment tag
5. **Update this doc**: Change "Last Verified" and add findings

---

## When to Re-Test

- After a major model upgrade (new Claude version)
- After changing pipeline config significantly
- If a step consistently escalates (assumption #3 may be wrong)
- If pipeline costs exceed expectations (assumption #8 may be wrong)
- Quarterly, regardless

---

## Retired Assumptions

| # | Assumption | Retired | Why |
|---|-----------|---------|-----|
| — | None yet | — | — |
