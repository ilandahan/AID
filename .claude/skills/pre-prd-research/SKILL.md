---
name: pre-prd-research
description: Pre-PRD Research methodology combining Business Analysis, Creative Problem-Solving, Brainstorming, and Innovation Strategy. Use before writing any PRD for problem validation, market research, competitive analysis, stakeholder interviews, ideation, root cause analysis.
---

# Pre-PRD Research Skill

## Core Belief

Every great product starts with deep understanding. Fall in love with the problem, not the solution.

## The Four Pillars

| Pillar | Focus | Key Question |
|--------|-------|--------------|
| Business Analysis | Evidence & Requirements | What do we know for certain? |
| Creative Problem-Solving | Root Causes & Systems | What's really going on? |
| Brainstorming | Possibilities & Ideas | What could we do? |
| Innovation Strategy | Value & Positioning | Why would anyone care? |

## Research Activities Flow

```
ACTIVITY A: UNDERSTAND -> ACTIVITY B: EXPLORE -> ACTIVITY C: DEFINE
Problem Analysis          Ideation & Exploration   Strategic Synthesis
Stakeholder Map           Root Cause Hunt          Validation
Market Research
```

## Traceability

### ID Format
```
[Project]-[Activity]-[Type]-[Number]
Examples:
PROJ-A-INT-001 = Interview finding #1
PROJ-B-IDEA-003 = Idea #3
PROJ-C-OPP-002 = Opportunity #2
```

### Traceability Matrix
| Research ID | Finding | Source | PRD Requirement | User Story |
|-------------|---------|--------|-----------------|------------|
| PROJ-A-INT-001 | Users frustrated by X | Interview | REQ-001 | US-001 |

## Entry & Exit Criteria

### Entry
- Initial idea/request/problem exists
- Stakeholders available
- Time allocated (minimum 2-3 sessions)

### Exit (Gate to PRD)
- [ ] Problem validated with multiple stakeholders
- [ ] Root causes identified and verified
- [ ] Market/competitive landscape understood
- [ ] Solution space explored
- [ ] Strategic positioning defined
- [ ] Assumptions explicit and tested
- [ ] Go/No-Go decision justified

---

# ACTIVITY A: UNDERSTAND

## 5 Whys Analysis
```
Stated Problem: [Initial statement]
Why 1: -> [Answer]
Why 2: -> [Answer]
Why 3: -> [Answer]
Why 4: -> [Answer]
Why 5: -> [Root Cause]
Validation Method: [How to verify]
```

## Problem Severity
| Dimension | Rating (1-10) |
|-----------|---------------|
| Frequency | |
| Impact | |
| Reach | |
| Urgency | |
| Strategic | |

Score = (Frequency x Impact x Reach) + (Urgency x 2) + (Strategic x 3)

## Stakeholder Interview Structure

1. Opening (5 min): Purpose, permission
2. Context (15 min): Workflow, frustrations, magic wand
3. Problem Exploration (20 min): Recent occurrence, actions, feelings, workarounds
4. Impact (10 min): Time/money cost, others affected
5. Solution Space (10 min): What tried, ideal solution
6. Closing (5 min): Missing questions, who else to talk to

## Stakeholder Power/Interest Matrix

```
            INTEREST
            Low     High
      High | Satisfy | Manage Closely |
POWER Low  | Monitor | Keep Informed  |
```

## Competitive Analysis

| Competitor | Target | Features | Pricing | Strengths | Weaknesses |
|------------|--------|----------|---------|-----------|------------|

### Key Questions
- Gap in market?
- Overserved needs?
- Underserved needs?
- Emerging trends?

## Jobs-to-be-Done

When [situation] I want to [progress] So I can [outcome]

Related: Emotional job, Social job

---

# ACTIVITY B: EXPLORE

## Brainstorming Techniques

1. Classic: How Might We... (10 min)
2. SCAMPER: Substitute, Combine, Adapt, Modify, Put to use, Eliminate, Reverse
3. Crazy 8s: 8 ideas in 8 minutes
4. Worst Possible Idea: Generate terrible solutions, then reverse
5. Six Thinking Hats: White(facts), Red(emotion), Black(risks), Yellow(benefits), Green(creative), Blue(process)

## Idea Capture

```
Idea: [Title]
ID: [PROJECT]-B-IDEA-[XXX]
One-Liner: [Explain in one sentence]
User Value: [Why would someone want this?]
Wild Rating: 1-5
```

## Root Cause Investigation

### Systems Map
- System boundaries
- Feedback loops (reinforcing/balancing)
- Leverage points (small changes, big effects)
- Unintended consequences

### Theory of Constraints
1. IDENTIFY the constraint
2. EXPLOIT it (maximize output as-is)
3. SUBORDINATE everything else
4. ELEVATE the constraint (increase capacity)
5. REPEAT (find new constraint)

## Insight Clustering

```
Cluster: [Theme Name]
Insights: [List]
Pattern: [Common thread]
Opportunity: [What to do]
```

---

# ACTIVITY C: DEFINE

## Blue Ocean Strategy

### Four Actions Framework
| Factor | ELIMINATE | REDUCE | RAISE | CREATE |
|--------|-----------|--------|-------|--------|
| [Factor] | | | | |

## Value Proposition Canvas

### Customer Profile
- Jobs: Functional, Emotional, Social
- Pains: [Pain]: Severity (1-10)
- Gains: [Gain]: Importance (1-10)

### Value Map
- Products & Services
- Pain Relievers
- Gain Creators

## Opportunity Scoring

| Criterion | Weight | Option A | Option B |
|-----------|--------|----------|----------|
| User Value | 30% | | |
| Feasibility | 25% | | |
| Strategic Fit | 20% | | |
| Time to Value | 15% | | |
| Risk Level | 10% | | |

## Assumption Mapping

| Assumption | Impact | Certainty | Validation Method |
|------------|--------|-----------|-------------------|
| [Critical] | High | Low | [How to test] |

---

# Quick Reference

| Mode | Trigger | Tools | Output |
|------|---------|-------|--------|
| Business Analyst | Need evidence | Interviews, 5 Whys, JTBD | Problem statement, stakeholder map |
| Brainstorming | Need ideas | SCAMPER, Crazy 8s, Six Hats | Idea backlog, opportunities |
| Problem-Solver | Need root causes | Systems Map, TOC, TRIZ | Root cause analysis |
| Innovation Strategist | Need positioning | Blue Ocean, Value Prop | Strategic positioning |

## Common Pitfalls

| Pitfall | Fix |
|---------|-----|
| Solution Bias | Write assumptions, try to disprove |
| Confirmation Seeking | Assign devil's advocate |
| Sampling Bias | Cover stakeholder matrix |
| Analysis Paralysis | Time-box, define "good enough" |
| Idea Attachment | Generate 10+ alternatives first |

## Minimum Viable Research (1 week)

1. Day 1-2: 3-5 stakeholder interviews
2. Day 3: Competitive scan (2 hours)
3. Day 4: 90-minute brainstorm
4. Day 5: Synthesis and recommendation

## Output Location

```
docs/research/YYYY-MM-DD-[project]/
  research-report.md
  traceability-matrix.md
  interviews/
  analysis/
  ideation/
  opportunities/
```
