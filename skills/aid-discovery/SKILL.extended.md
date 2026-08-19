---
name: aid-discovery
description: AID Phase 1 - Research & PRD guidance. Use this skill when validating problem spaces, identifying stakeholders, defining success metrics, or deciding whether to proceed with a project. Essential first step before writing any PRD.
---

# Discovery Phase Skill

## Phase Overview

**Purpose**: Validate the problem space before committing to a solution. Ensure we understand who has the problem, what the problem is, and why it matters.

**Entry Criteria**:
- Initial idea or request exists
- Stakeholder(s) available for consultation

**Exit Criteria**:
- Problem statement validated with stakeholders
- All affected parties identified
- Success metrics defined
- Decision to proceed (or not) made

## Deliverables

### 1. Problem Statement
- **Description**: Clear articulation of the problem being solved
- **Format**: SCQ (Situation-Complication-Question) or similar structured format
- **Quality bar**: Validated by at least one stakeholder, no solution assumptions

### 2. Stakeholder Map
- **Description**: All people/systems affected by or involved in the solution
- **Format**: Visual map or structured list with roles
- **Quality bar**: Includes data owners, decision makers, and affected users

### 3. Success Metrics
- **Description**: How we'll know if the solution works
- **Format**: Quantified, measurable outcomes
- **Quality bar**: Specific numbers or clear criteria, not vague improvements

## Role-Specific Guidance

### For Product Managers
- Lead stakeholder interviews
- Own the problem statement
- Resist jumping to solutions
- Quantify the cost of the problem

### For Developers
- Assess technical feasibility early
- Identify technical constraints
- Flag potential technical risks
- Estimate rough complexity

### For QA Engineers
- Consider testability from the start
- Identify quality risks
- Think about test data needs
- Flag compliance requirements

### For Tech Leads
- Evaluate architectural implications
- Consider build vs. buy
- Assess team capability gaps
- Identify infrastructure needs

## Common Pitfalls

| Pitfall | Problem | Fix |
|---------|---------|-----|
| Solution-first thinking | Building without understanding | Start with "what problem?" not "what feature?" |
| Missing stakeholders | Unexpected requirements later | Ask "who else touches this?" |
| Vague problems | Can't measure success | If you can't measure it, you haven't defined it |
| Assumption blindness | Hidden risks | Make assumptions explicit and validate them |

## Phase Gate Checklist

Before requesting approval to proceed:

- [ ] Problem statement is written and validated
- [ ] All stakeholders identified (data owners, users, decision makers)
- [ ] Success metrics are specific and measurable
- [ ] Technical feasibility assessed (at high level)
- [ ] Decision to proceed/not proceed is clear
- [ ] Scope boundaries are established

## Discovery Questions

### Understanding the Problem
- What problem are we solving?
- Who has this problem?
- How painful is this problem? (Quantify)
- What happens if we don't solve it?
- Is this the real problem or a symptom?

### Identifying Stakeholders
- Who are the end users?
- Who owns the data/process?
- Who makes decisions about this area?
- Who else touches this system?
- Who needs to approve changes?

### Defining Success
- What does success look like?
- How will we measure improvement?
- What's the target state?
- How will we know we're done?
- What's the minimum viable outcome?

### Technical Feasibility
- Is this technically feasible?
- What are the major technical risks?
- Do we have the required skills?
- What infrastructure is needed?
- Are there existing solutions to leverage?

## Problem Statement Template

### SCQ Format (Situation-Complication-Question)

```markdown
## Problem Statement

### Situation
[Describe the current state - what exists today]

### Complication
[What's wrong with the current state - the problem]

### Question
[What question does solving this answer?]

### Impact
- [Quantified impact 1]
- [Quantified impact 2]

### Success Metrics
| Metric | Current | Target |
|--------|---------|--------|
| [Metric 1] | [Current value] | [Target value] |
| [Metric 2] | [Current value] | [Target value] |
```

## Stakeholder Map Template

```markdown
## Stakeholder Map

### Decision Makers
- [Name/Role]: [Responsibility]

### Data/System Owners
- [Name/Role]: [What they own]

### End Users
- [User type 1]: [How they're affected]
- [User type 2]: [How they're affected]

### Integrations
- [System 1]: [Relationship]
- [System 2]: [Relationship]

### Informed Parties
- [Name/Role]: [Why they need to know]
```

## Transition to PRD Phase

Hand off:
- Validated problem statement
- Stakeholder map
- Success metrics
- Any constraints identified
- Initial scope boundaries

---

## Learning Mode Integration

### Decision Transparency Triggers
- **Problem scope decisions**: Show reasoning when narrowing/expanding problem scope
- **Stakeholder identification**: Explain why certain parties are/aren't included
- **Metric selection**: Show why specific metrics were chosen over alternatives

### Debate Invitations
- **Problem framing**: When multiple valid problem statements exist
- **Scope boundaries**: When inclusion/exclusion decisions are ambiguous
- **Build vs. buy**: When solution approach affects discovery scope

### Feedback Requests
- After problem statement draft: Validate understanding
- After stakeholder map: Confirm completeness
- At phase gate: Overall discovery quality rating

### Example Transparency Block
```markdown
<decision-transparency>
**Decision:** Focused problem statement on internal users, excluding external partners

**Reasoning:**
- **Scope control**: External partners have different workflows
- **Validation speed**: Can validate with internal users faster
- **Risk reduction**: Smaller initial scope = clearer success criteria

**Alternatives Considered:**
1. Include external partners - Deferred: Adds 3+ more stakeholder groups
2. Start with partners only - Rejected: Less access for validation

**Confidence:** Medium - May need to revisit if usage data shows partner impact

**Open to Debate:** Yes - If partners are major users, should reconsider
</decision-transparency>
```
