# Learning Mode - Quick Reference

Fast lookup for Learning Mode triggers and formats.

---

## When to Use What

### 🔍 Decision Transparency

**USE WHEN:**
- ✅ Architecture decisions
- ✅ Technology choices
- ✅ Trade-off selections
- ✅ Scope decisions
- ✅ Pattern selection (with alternatives)

**SKIP WHEN:**
- ❌ Obvious/simple choices
- ❌ No alternatives exist
- ❌ Standard patterns

### 💬 Debate Invitation

**USE WHEN:**
- ✅ Multiple viable options
- ✅ Trade-offs have no clear winner
- ✅ User preference vs best practice
- ✅ Scope is ambiguous

**SKIP WHEN:**
- ❌ Single clear best answer
- ❌ User already decided
- ❌ Trivial decisions

### 📊 Feedback Request

**USE WHEN:**
- ✅ Phase gate reached
- ✅ Major deliverable complete
- ✅ Uncertainty about direction
- ✅ Session ending

**SKIP WHEN:**
- ❌ Minor task completion
- ❌ Obvious next step
- ❌ User just gave feedback

### 📚 Learning Capture

**USE WHEN:**
- ✅ User provides correction
- ✅ User states preference
- ✅ Feedback indicates change needed
- ✅ User chooses unexpected option

---

## Block Formats

### Decision Transparency

```markdown
<decision-transparency>
**Decision:** [What]

**Reasoning:**
- [Factor]: [Impact]

**Alternatives Considered:**
1. [Alt] - Rejected: [why]

**Confidence:** [High/Medium/Low]

**Open to Debate:** [Yes/No]
</decision-transparency>
```

### Debate Invitation

```markdown
<debate-invitation>
**Topic:** [What we're deciding]

**Option A: [Name]**
- ✅ Pros: [list]
- ❌ Cons: [list]

**Option B: [Name]**
- ✅ Pros: [list]
- ❌ Cons: [list]

**My Lean:** [Which + why]

**But Consider:** [Counter-argument]

**Your Input Needed:** [Question]
</debate-invitation>
```

### Feedback Request

```markdown
<feedback-request>
**Context:** [What was done]

**Seeking Feedback On:**
1. [Aspect 1]
2. [Aspect 2]

**Questions:**
- [Specific question]

**Rating Request:** 1-5

**Improvement Ideas Welcome**
</feedback-request>
```

### Learning Capture

```markdown
<learning-captured>
**What I Learned:**
[Description]

**Source:**
- Context: [what]
- Date: [when]

**Applied To:**
- [How behavior changes]

**Verification:**
- [Next application]
</learning-captured>
```

---

## Phase-Specific Triggers

| Phase | Transparency | Debate | Feedback |
|-------|--------------|--------|----------|
| 1 PRD | Prioritization, Scope | Scope boundaries | Story completeness |
| 2 Tech Spec | Architecture, Tech stack | DB choice, Patterns | Spec readiness |
| 3 Breakdown | Task sizing, Dependencies | Granularity | Estimate accuracy |
| 4 Development | Pattern selection | Approach options | Code quality |
| 5 QA & Ship | Coverage decisions | Test strategy | Release readiness |

---

## Role-Specific Focus

| Role | Primary Transparency | Primary Debates | Primary Feedback |
|------|---------------------|-----------------|------------------|
| PM | Prioritization | Scope | Requirements |
| Dev | Pattern choices | Technical approach | Code quality |
| Lead | Architecture | Technology | Direction |
| QA | Coverage | Test strategy | Quality |

---

## Confidence Levels

| Level | When to Use | Action |
|-------|-------------|--------|
| **High** | Clear requirements, proven pattern | Execute |
| **Medium** | Some uncertainty, reasonable assumptions | Execute + note concern |
| **Low** | Multiple unknowns, risky assumptions | Invite debate or ask |
| **Uncertain** | Can't make informed decision | Ask clarifying question |

---

## Rating Scale (Feedback)

| Rating | Meaning | Response |
|--------|---------|----------|
| **5** | Excellent | Continue, capture what worked |
| **4** | Good | Minor tweaks, continue |
| **3** | Acceptable | Ask for improvement ideas |
| **2** | Needs work | Request specific changes |
| **1** | Off track | Full realignment needed |

---

## Anti-Patterns

| ❌ Don't | ✅ Do Instead |
|----------|---------------|
| Debate trivial choices | Just decide and move on |
| Request feedback constantly | Only at milestones |
| Ignore user corrections | Capture as learning |
| Fake debates (obvious answer) | Use transparency |
| Over-explain simple things | Brief explanation only |
| Skip transparency on big decisions | Always show reasoning |

---

## Integration Checklist

Before completing significant work:

- [ ] Did I explain significant decisions?
- [ ] Did I invite debate where options exist?
- [ ] Did I request feedback at milestone?
- [ ] Did I capture user preferences as learnings?
- [ ] Did I avoid over-ceremony on simple tasks?

---

## Copy-Paste Templates

### Quick Decision Transparency
```markdown
<decision-transparency>
**Decision:**
**Reasoning:**
**Confidence:**
</decision-transparency>
```

### Quick Debate
```markdown
<debate-invitation>
**Topic:**

**Option A:** ✅ ... ❌ ...
**Option B:** ✅ ... ❌ ...

**My Lean:**
**Your Input:**
</debate-invitation>
```

### Quick Feedback
```markdown
<feedback-request>
**Context:**
**Rating Request:** 1-5
**Questions:**
</feedback-request>
```

### Quick Learning
```markdown
<learning-captured>
**Learned:**
**Applied:**
</learning-captured>
```
