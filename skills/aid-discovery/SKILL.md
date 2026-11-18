---
name: aid-discovery
description: AID Phase 0 - Research & discovery. Use for validating problem spaces, identifying stakeholders, defining success metrics, deciding whether to proceed.
---

# aid-discovery - AID Phase 0

Purpose: Validate problem space before committing to solution.
Entry: Initial idea/request exists, stakeholders available.
Exit: Problem validated, stakeholders identified, success metrics defined, go/no-go decision.

## Deliverables

1. Problem Statement (SCQ format) - Validated, no solution assumptions
2. Stakeholder Map - All affected parties identified
3. Success Metrics - Quantified, measurable outcomes
4. Solution Shape Hypothesis - A first level 0-5 on the solution-shape ladder, in the research report

## Discovery Questions

Ask these:

- Problem: What problem are we solving? Who has this problem? How painful? (Quantify) What if we don't solve it?
- Stakeholders: Who are end users? Who owns data/process? Who makes decisions? Who else touches this?
- Success: What does success look like? How will we measure? What's minimum viable outcome? What must NOT get worse (guardrail)?
- Variation: How much does the problem vary from case to case?
- Cost of error: Who bears the cost of an error, and is it reversible?
- Technical feasibility: Is this feasible? Major technical risks? Required skills? Infrastructure needs?

## Problem Statement Template (SCQ)

```markdown
## Problem Statement

### Situation
[Current state]

### Complication
[What's wrong]

### Question
[What solving this answers]

### Impact
- [Quantified impact]

### Success Metrics
| Metric | Current | Target |
|--------|---------|--------|
| [Metric] | [Now] | [Goal] |
```

## Solution Shape Hypothesis (research report section)

Add this section to `docs/research/YYYY-MM-DD-[project]/research-report.md`. It is a first guess on the solution-shape ladder (defined in `aid-prd`, PRD §1.5); the PRD confirms or changes it.

```markdown
## Solution Shape Hypothesis

Levels: 0 process change (no software); 1 deterministic automation; 2 single LLM call inside a fixed flow; 3 workflow; 4 agent; 5 multi-agent (full ladder: `aid-prd/references/prd-template-extended.md` §1.5).

- How much the problem varies from case to case: [Low/Medium/High + evidence]
- Who bears the cost of an error, and is it reversible: [Who, how much, reversible?]
- Hypothesis: level [0-5], because [one sentence]. Lowest level that might work: [level].
- Evidence still needed to confirm it: [list]
```

## Stakeholder Map Template

```markdown
### Decision Makers
- [Name/Role]: [Responsibility]

### Data/System Owners
- [Name/Role]: [What they own]

### End Users
- [Type]: [How affected]

### Integrations
- [System]: [Relationship]
```

## Common Pitfalls

|Pitfall|Fix|
|---|---|
|Solution-first|Start with "what problem?"|
|Missing stakeholders|Ask "who else touches this?"|
|Vague problems|If can't measure, not defined|
|Assumption blindness|Make assumptions explicit|

## Phase Gate Checklist

- [ ] Problem statement validated
- [ ] All stakeholders identified
- [ ] Success metrics specific
- [ ] Technical feasibility assessed
- [ ] Solution shape hypothesis recorded (level + variation + who bears an error)
- [ ] Proceed/not-proceed decision clear
- [ ] Scope boundaries established

## Handoff to PRD

- Validated problem statement
- Stakeholder map
- Success metrics
- Constraints identified
- Scope boundaries
- Solution shape hypothesis (input to PRD §1.5)
