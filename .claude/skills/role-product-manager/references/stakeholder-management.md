# Stakeholder Management Guide

## Stakeholder Identification

### Stakeholder Categories

```markdown
## Primary Stakeholders (Direct Impact)
- End users
- Paying customers
- Product team

## Secondary Stakeholders (Indirect Impact)
- Support team
- Sales team
- Marketing team
- Partner teams

## Decision Makers
- Executive sponsor
- Budget owner
- Technical approver

## Influencers
- Subject matter experts
- Key opinion leaders
- Power users
```

### Stakeholder Register Template

```markdown
| Name | Role | Interest | Influence | Communication | Concerns |
|------|------|----------|-----------|---------------|----------|
| [Name] | Executive Sponsor | High | High | Weekly 1:1 | Budget, timeline |
| [Name] | Tech Lead | High | High | Daily standup | Technical feasibility |
| [Name] | End User Rep | High | Medium | Bi-weekly feedback | Usability |
| [Name] | Support Lead | Medium | Low | Release notes | Training needs |
```

## Stakeholder Analysis

### Power/Interest Grid

```
           High Interest
                │
    KEEP        │    MANAGE
    SATISFIED   │    CLOSELY
    (Inform)    │    (Engage)
                │
────────────────┼────────────────
                │
    MONITOR     │    KEEP
    (Minimal)   │    INFORMED
                │    (Update)
                │
           Low Interest

High Power ←─────────────→ Low Power
```

### RACI Matrix

```markdown
| Activity | Responsible | Accountable | Consulted | Informed |
|----------|-------------|-------------|-----------|----------|
| PRD approval | PM | VP Product | Tech Lead, UX | Dev Team |
| Tech decisions | Tech Lead | CTO | PM | Stakeholders |
| Release go/no-go | PM | VP Product | QA, Tech Lead | All |
| Bug prioritization | PM | PM | Dev, Support | Stakeholders |
```

## Communication Planning

### Communication Matrix

```markdown
| Stakeholder | Channel | Frequency | Content | Owner |
|-------------|---------|-----------|---------|-------|
| Executive | Email + Meeting | Weekly | Summary, risks, decisions | PM |
| Dev Team | Standup + Slack | Daily | Tasks, blockers | PM |
| Customers | Newsletter | Monthly | Updates, roadmap | Marketing |
| Support | Wiki + Training | Per release | New features, FAQs | PM |
```

### Meeting Templates

#### Stakeholder Sync (30 min)
```markdown
1. Progress Update (5 min)
   - What's done
   - What's in progress

2. Decisions Needed (10 min)
   - [Decision 1]: Options, recommendation
   - [Decision 2]: Options, recommendation

3. Risks & Blockers (10 min)
   - [Risk]: Status, mitigation
   - [Blocker]: Action needed

4. Next Steps (5 min)
   - Action items
   - Next meeting
```

#### Requirements Workshop (60 min)
```markdown
1. Context Setting (5 min)
   - Problem we're solving
   - Goals for session

2. Current State Review (10 min)
   - How it works today
   - Pain points

3. Requirements Gathering (30 min)
   - User needs
   - Business needs
   - Constraints

4. Prioritization (10 min)
   - Must have vs nice to have
   - Quick wins vs later

5. Next Steps (5 min)
   - Follow-up items
   - Timeline
```

## Managing Expectations

### Setting Expectations
```markdown
## At Project Start
- Clearly define scope (in AND out)
- Agree on success metrics
- Set realistic timeline with buffers
- Define decision-making process
- Establish communication cadence

## During Project
- Provide regular updates
- Escalate risks early
- Document decisions
- Manage scope changes formally

## At Project End
- Review against original goals
- Celebrate successes
- Document learnings
- Plan follow-up work
```

### Handling Difficult Conversations

#### Scope Creep
```markdown
"I understand the value of [feature]. Let me show you the impact:

Current scope: X sprints, releases [date]
With addition: Y sprints, releases [date]

Options:
A) Add to scope, delay release
B) Add to scope, remove [other feature]
C) Add to backlog for phase 2

Which would you prefer?"
```

#### Timeline Pressure
```markdown
"I hear the urgency. Here's what I can do:

Option A: Full scope by [later date]
Option B: Reduced scope by [target date]
  - Include: [essential features]
  - Defer: [nice-to-haves]

Which aligns better with your priorities?"
```

#### Conflicting Requirements
```markdown
"I've received different input from stakeholders:

[Stakeholder A] wants: [requirement]
[Stakeholder B] wants: [conflicting requirement]

I'd like to schedule a session to align on:
1. What's the core user need?
2. How do we prioritize?
3. Can we satisfy both in phases?"
```

## Feedback Collection

### User Feedback Session
```markdown
1. Introduction (5 min)
   - Thank participant
   - Explain purpose
   - Get consent to record

2. Context Questions (10 min)
   - Role/background
   - Current workflow
   - Pain points

3. Feature Feedback (20 min)
   - Show prototype/design
   - Observe reactions
   - Ask open questions

4. Wrap-up (5 min)
   - Any other thoughts?
   - Can we follow up?
```

### Feedback Synthesis Template
```markdown
## Feedback Summary: [Feature]

### Participants
- [N] users interviewed
- Roles: [list]

### Key Themes
1. [Theme]: [N] mentions
2. [Theme]: [N] mentions

### Quotes
> "[Direct quote]" - [Role]

### Recommendations
1. [Action item]
2. [Action item]

### Open Questions
- [Question needing more research]
```
