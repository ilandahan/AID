# Learning Mode - Quick Reference

## When to Use What

### Decision Transparency
USE: Architecture, Technology, Trade-offs, Scope, Pattern selection
SKIP: Obvious choices, No alternatives, Standard patterns

### Debate Invitation
USE: Multiple viable options, No clear winner, User vs best practice, Ambiguous scope
SKIP: Single best answer, User decided, Trivial

### Feedback Request
USE: Phase gate, Major deliverable, Uncertainty, Session ending
SKIP: Minor task, Obvious next step, Just gave feedback

### Learning Capture
USE: User correction, User preference, Feedback indicates change, Unexpected choice

## Block Formats

### Decision Transparency
```
<decision-transparency>
**Decision:** [What]
**Reasoning:** [Factor]: [Impact]
**Alternatives:** [Alt] - Rejected: [why]
**Confidence:** [High/Medium/Low]
**Open to Debate:** [Yes/No]
</decision-transparency>
```

### Debate Invitation
```
<debate-invitation>
**Topic:** [Decision]
**Option A:** Pros/Cons
**Option B:** Pros/Cons
**My Lean:** [Which + why]
**But Consider:** [Counter]
**Your Input:** [Question]
</debate-invitation>
```

### Feedback Request
```
<feedback-request>
**Context:** [Done]
**Seeking Feedback:** [Aspects]
**Questions:** [Specific]
**Rating:** 1-5
</feedback-request>
```

### Learning Capture
```
<learning-captured>
**Learned:** [What]
**Applied:** [How]
</learning-captured>
```

## Phase Triggers

| Phase | Transparency | Debate | Feedback |
|-------|--------------|--------|----------|
| 1 PRD | Prioritization | Scope | Stories |
| 2 Spec | Arch, Tech | DB, Patterns | Readiness |
| 3 Plan | Task sizing | Granularity | Estimates |
| 4 Dev | Patterns | Approach | Code |
| 5 QA | Coverage | Test strategy | Release |

## Confidence Levels

| Level | Action |
|-------|--------|
| High | Execute |
| Medium | Execute + note |
| Low | Debate |
| Uncertain | Ask |

## Rating Scale

| Rating | Response |
|--------|----------|
| 5 | Continue |
| 4 | Minor tweaks |
| 3 | Ask improvements |
| 2 | Request changes |
| 1 | Realign |

## Anti-Patterns

| Dont | Do |
|------|-----|
| Debate trivial | Just decide |
| Constant feedback | Only milestones |
| Ignore corrections | Capture learning |
| Fake debates | Use transparency |
| Over-explain simple | Brief only |
