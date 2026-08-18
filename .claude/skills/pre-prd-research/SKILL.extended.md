---
name: pre-prd-research
description: Comprehensive Pre-PRD Research methodology combining Business Analysis, Creative Problem-Solving, Brainstorming, and Innovation Strategy. Use this skill before writing any PRD - when validating problem spaces, conducting market research, competitive analysis, stakeholder interviews, ideation sessions, root cause analysis, or strategic positioning. This is the essential foundation that ensures PRDs are built on validated insights rather than assumptions.
---

# Pre-PRD Research Skill

## Overview & Philosophy

This skill represents a comprehensive research methodology that precedes and enables effective PRD creation. It integrates four distinct but complementary disciplines into a unified approach.

**Core Belief**: Every great product starts not with a solution, but with deep understanding. This phase is about falling in love with the problem, not the solution.

### The Four Pillars

| Pillar | Focus | Key Question |
|--------|-------|--------------|
| **Business Analysis** | Evidence & Requirements | "What do we know for certain?" |
| **Creative Problem-Solving** | Root Causes & Systems | "What's really going on?" |
| **Brainstorming** | Possibilities & Ideas | "What could we do?" |
| **Innovation Strategy** | Value & Positioning | "Why would anyone care?" |

## Position in AID Methodology

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         AID METHODOLOGY PHASES                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────┐   ┌─────┐   ┌──────────┐   ┌─────┐   ┌────────────┐  │
│  │   PHASE 1    │──▶│  2  │──▶│    3     │──▶│  4  │──▶│     5      │  │
│  │PRD+RESEARCH │   │TECH │   │ BREAKDOWN│   │ DEV │   │  QA/SHIP   │  │
│  │              │   │     │   │          │   │     │   │            │  │
│  │ ┌──────────┐ │   │     │   │          │   │     │   │            │  │
│  │ │THIS SKILL│ │   │     │   │          │   │     │   │            │  │
│  │ │ OPERATES │ │   │     │   │          │   │     │   │            │  │
│  │ │  HERE    │ │   │     │   │          │   │     │   │            │  │
│  │ └──────────┘ │   │     │   │          │   │     │   │            │  │
│  └──────────────┘   └─────┘   └──────────┘   └─────┘   └────────────┘  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

> **Note**: This skill expands Phase 1 (PRD) with structured research activities that feed into PRD creation.
> The "Activities" below are NOT phases - they are workflows within Discovery.

## Research Activities Flow

```
┌─────────────────────────────────────────────────────────────────┐
│          PHASE 1: PRD - RESEARCH ACTIVITIES                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ACTIVITY A: UNDERSTAND    ACTIVITY B: EXPLORE    ACTIVITY C: DEFINE
│  ┌─────────────────┐       ┌──────────────────┐   ┌────────────┐
│  │ Problem Analysis │  ──▶  │ Ideation &       │──▶│ Strategic  │
│  │ Stakeholder Map  │       │ Exploration      │   │ Synthesis  │
│  │ Market Research  │       │ Root Cause Hunt  │   │ Validation │
│  └─────────────────┘       └──────────────────┘   └────────────┘
│                                                                 │
│  Business Analyst +         Brainstorming +       Innovation    │
│  Creative Problem-          Creative Problem-     Strategist +  │
│  Solver Lead                Solver Lead           Business      │
│                                                   Analyst Lead  │
└─────────────────────────────────────────────────────────────────┘
```

## Requirements Traceability

Every insight discovered in research MUST be traceable to PRD requirements. Use this tracking system:

### Traceability ID Format
```
[Project]-[Activity]-[Type]-[Number]

Examples:
- PROJ-A-INT-001  = Project, Activity A (Understand), Interview finding #1
- PROJ-B-IDEA-003 = Project, Activity B (Explore), Idea #3
- PROJ-C-OPP-002  = Project, Activity C (Define), Opportunity #2
```

### Traceability Matrix Template

```markdown
## Requirements Traceability Matrix

| Research ID | Finding/Insight | Source | PRD Requirement | User Story |
|-------------|-----------------|--------|-----------------|------------|
| PROJ-A-INT-001 | Users frustrated by X | Interview: [Name] | REQ-001 | US-001 |
| PROJ-A-COMP-002 | Competitor lacks Y | Competitive Analysis | REQ-003 | US-004 |
| PROJ-B-IDEA-005 | Solution approach Z | Brainstorm Session | REQ-002 | US-002 |
| PROJ-C-OPP-001 | Market gap in W | Strategic Analysis | REQ-004 | US-005 |

### Orphan Check
**Research findings NOT linked to requirements:**
- [ ] Review each - intentional exclusion or oversight?

**Requirements WITHOUT research backing:**
- [ ] Flag as assumptions - add to assumption tracking
```

### Handoff Checklist to PRD Phase

Before transitioning from Discovery to PRD:

- [ ] All research findings have traceability IDs
- [ ] Traceability matrix is populated
- [ ] Each finding marked as: INCLUDE / EXCLUDE / DEFER
- [ ] Excluded items have documented rationale
- [ ] Deferred items logged in backlog
- [ ] No requirements exist without research backing (or flagged as assumptions)

## Entry & Exit Criteria

### Entry Criteria
- Initial idea, request, or observed problem exists
- Stakeholder(s) available for consultation
- Time allocated for proper research (minimum 2-3 sessions)
- Commitment to follow evidence, not assumptions

### Exit Criteria (Gate to PRD Phase)
- [ ] Problem validated with multiple stakeholders
- [ ] Root causes identified and verified
- [ ] Market/competitive landscape understood
- [ ] Solution space explored (not just one idea)
- [ ] Strategic positioning defined
- [ ] All assumptions made explicit and tested
- [ ] Go/No-Go decision justified with evidence

---

# ACTIVITY A: UNDERSTAND

## Pillar: Business Analyst Mode

### Mindset Activation
> *"Treat analysis like a treasure hunt - get excited by every clue, thrilled when patterns emerge. Ask questions that spark 'aha!' moments while structuring insights with precision."*

### 1.1 Problem Space Analysis

#### The 5 Whys Deep Dive
For every stated problem, ask "Why?" at least 5 times to reach root causes.

```markdown
## 5 Whys Analysis

**Stated Problem**: [Initial problem statement]

**Why 1**: Why does this happen?
-> [Answer]

**Why 2**: Why does [Answer 1] occur?
-> [Answer]

**Why 3**: Why does [Answer 2] occur?
-> [Answer]

**Why 4**: Why does [Answer 3] occur?
-> [Answer]

**Why 5**: Why does [Answer 4] occur?
-> [Root Cause Hypothesis]

**Validation Method**: [How will we verify this root cause?]
```

#### Problem Severity Assessment

| Dimension | Questions | Rating (1-10) |
|-----------|-----------|---------------|
| **Frequency** | How often does this occur? | |
| **Impact** | How severe when it happens? | |
| **Reach** | How many users affected? | |
| **Urgency** | How time-sensitive is the fix? | |
| **Strategic** | How does it affect company goals? | |

**Problem Priority Score** = (Frequency x Impact x Reach) + (Urgency x 2) + (Strategic x 3)

### 1.2 Stakeholder Research

#### Stakeholder Interview Framework

**Before the Interview:**
- Research the stakeholder's role, history, and perspective
- Prepare open-ended questions
- Set up note-taking system
- Plan for 60-90 minutes

**Interview Structure:**

```markdown
## Stakeholder Interview: [Name/Role]
**Date**: [Date]
**Duration**: [Time]
**Traceability Prefix**: [PROJECT]-A-INT-[XXX]

### Opening (5 min)
- Thank them for time
- Explain purpose: understanding, not selling
- Ask permission to take notes

### Context Questions (15 min)
- "Walk me through your typical day/workflow"
- "What's the most frustrating part of [relevant area]?"
- "If you had a magic wand, what would you change?"

### Problem Exploration (20 min)
- "Tell me about a recent time when [problem] occurred"
- "What did you do? What happened?"
- "How did that make you feel?"
- "What workarounds have you tried?"

### Impact Questions (10 min)
- "How much time/money does this cost you?"
- "What would you do with that time/money if you had it back?"
- "Who else is affected by this?"

### Solution Space (10 min)
- "What have you tried to solve this?"
- "What would an ideal solution look like?"
- "What would make you say 'this is exactly what I needed'?"

### Closing (5 min)
- "What question should I have asked but didn't?"
- "Who else should I talk to?"
- Thank them

### Post-Interview Notes
**Key Insights**:
**Surprising Findings**:
**Quotes to Remember**:
**Follow-up Questions**:
```

#### Stakeholder Power/Interest Matrix

```
                    INTEREST IN PROJECT
                    Low              High
              ┌─────────────┬─────────────┐
        High  │   KEEP      │   MANAGE    │
    P         │ SATISFIED   │   CLOSELY   │
    O         │             │             │
    W         ├─────────────┼─────────────┤
    E         │   MONITOR   │   KEEP      │
    R    Low  │   (MINIMAL) │  INFORMED   │
              │             │             │
              └─────────────┴─────────────┘
```

### 1.3 Market & Competitive Research

#### Competitive Analysis Framework

```markdown
## Competitive Landscape Analysis

### Direct Competitors
| Competitor | Target Market | Key Features | Pricing | Strengths | Weaknesses |
|------------|---------------|--------------|---------|-----------|------------|
| [Name] | | | | | |

### Indirect Competitors
| Alternative | How It Solves Same Problem | Why Users Choose It |
|-------------|---------------------------|---------------------|
| [Name] | | |

### Non-Consumption
**Who has this problem but uses NO solution?**
- [Segment 1]: Why not?
- [Segment 2]: Why not?

### Competitive Positioning Map
[Create 2x2 matrix with relevant dimensions]

### Key Insights
- **Gap in Market**:
- **Overserved Needs**:
- **Underserved Needs**:
- **Emerging Trends**:
```

#### Jobs-to-be-Done Analysis

```markdown
## Jobs-to-be-Done Analysis

### Core Functional Job
**When** [situation/trigger]
**I want to** [progress I'm trying to make]
**So I can** [expected outcome]

### Related Jobs
- **Emotional Job**: How do they want to feel?
- **Social Job**: How do they want to be perceived?

### Job Map
| Stage | Customer Action | Pain Points | Gains Sought |
|-------|-----------------|-------------|--------------|
| 1. Define | | | |
| 2. Locate | | | |
| 3. Prepare | | | |
| 4. Confirm | | | |
| 5. Execute | | | |
| 6. Monitor | | | |
| 7. Modify | | | |
| 8. Conclude | | | |

### Hiring & Firing Criteria
**When would they "hire" a solution?**
-

**When would they "fire" a solution?**
-

### Forces of Progress
```
                    PUSH OF SITUATION
                    "Current situation is frustrating"
                           │
                           ▼
    ┌──────────────────────────────────────────┐
    │                                          │
    │            DECISION TO CHANGE            │
    │                                          │
    └──────────────────────────────────────────┘
                           ▲
          PULL OF NEW ─────┼───── ANXIETY OF NEW
          "Better future"  │      "What if it fails?"
                           │
          HABIT OF ────────┘
          PRESENT
          "This works okay"
```

---

# ACTIVITY B: EXPLORE

## Pillar: Brainstorming Coach Mode

### Mindset Activation
> *"YES AND! Build on every idea. Wild thinking today becomes innovation tomorrow. Psychological safety unlocks breakthroughs. Humor and play are serious innovation tools."*

### 2.1 Divergent Thinking Session

#### Pre-Session Setup
- **Environment**: Remove judgment, enable play
- **Rules**: No criticism, quantity over quality, wild ideas welcome, build on others
- **Materials**: Timer, capture method, energy snacks

#### Brainstorming Techniques Menu

**1. Classic Brainstorm (10 min)**
- State the challenge as "How Might We..."
- Generate as many ideas as possible
- No evaluation during generation

**2. SCAMPER Method**
| Letter | Question | Ideas |
|--------|----------|-------|
| **S**ubstitute | What can we replace? | |
| **C**ombine | What can we merge? | |
| **A**dapt | What else is like this? | |
| **M**odify | What can we change? | |
| **P**ut to other use | Other applications? | |
| **E**liminate | What can we remove? | |
| **R**everse | What if we flip it? | |

**3. Crazy 8s (8 min)**
- 8 ideas in 8 minutes
- One sketch/concept per minute
- Forces rapid ideation, prevents overthinking

**4. Worst Possible Idea**
- Generate terrible solutions intentionally
- Then reverse them into good ideas
- Breaks creative blocks

**5. Random Input**
- Pick random word/image
- Force connections to the problem
- Sparks unexpected associations

**6. Six Thinking Hats**
| Hat | Focus | Time |
|-----|-------|------|
| White | Facts only | 5 min |
| Red | Emotions, intuition | 3 min |
| Black | Risks, problems | 5 min |
| Yellow | Benefits, optimism | 5 min |
| Green | Creativity, alternatives | 8 min |
| Blue | Process, next steps | 5 min |

### 2.2 Idea Capture Template

```markdown
## Idea: [Title]
**Traceability ID**: [PROJECT]-B-IDEA-[XXX]

**One-Liner**: [Explain in one sentence]

**Origin**: [Which technique generated this?]

**The "What If"**: What if [bold assumption]?

**User Value**: [Why would someone want this?]

**Wild Rating**: 1-5 (how bold/unconventional)

**Build On It**: [How could this be even bigger?]

**YES AND**: [Add to this idea...]
```

## Pillar: Creative Problem-Solver Mode

### Mindset Activation
> *"Every problem is a system revealing weaknesses. Hunt for root causes relentlessly. The right question beats a fast answer. AHA moments come to the prepared mind."*

### 2.3 Root Cause Investigation

#### Systems Thinking Analysis

```markdown
## System Map

### System Boundaries
- What's inside the system?
- What's outside but connected?
- Where are the interfaces?

### Feedback Loops
**Reinforcing Loops** (amplify change):
- [Loop 1]: A -> B -> C -> more A

**Balancing Loops** (resist change):
- [Loop 1]: A -> B -> C -> less A

### Leverage Points
Where small changes create big effects:
1.
2.
3.

### Unintended Consequences
If we change X, what else changes?
```

#### Theory of Constraints Analysis

```markdown
## Constraint Analysis

### The Five Focusing Steps

**1. IDENTIFY the constraint**
What is the ONE thing limiting the system?
->

**2. EXPLOIT the constraint**
How can we get maximum output from it as-is?
->

**3. SUBORDINATE everything else**
What should other parts do to support the constraint?
->

**4. ELEVATE the constraint**
How do we increase capacity of the constraint?
->

**5. REPEAT**
What's the new constraint after we fix this one?
->
```

#### TRIZ Contradiction Analysis

```markdown
## TRIZ Analysis

### Technical Contradiction
We want to improve [Parameter A]
But this worsens [Parameter B]

### Physical Contradiction
The system must be [State X] to achieve [Goal 1]
But must be [State Y] to achieve [Goal 2]

### Inventive Principles to Try
1. **Segmentation**: Divide the object into independent parts
2. **Taking Out**: Extract the disturbing part
3. **Local Quality**: Different parts should have different functions
4. **Asymmetry**: Change symmetrical forms to asymmetrical
5. **Merging**: Combine identical or similar objects
6. **Universality**: Make one part perform multiple functions
7. **Nested Doll**: Place one object inside another
8. **Prior Action**: Perform required changes before they're needed
9. **Inversion**: Instead of direct action, use opposite
10. **Dynamicity**: Allow system characteristics to change
```

### 2.4 Opportunity Synthesis

#### Insight Clustering

```markdown
## Insight Clusters

### Cluster 1: [Theme Name]
**Insights**:
- [Insight 1]
- [Insight 2]
- [Insight 3]

**Pattern**: What do these have in common?

**Opportunity**: What does this cluster suggest we should do?

### Cluster 2: [Theme Name]
...

### Cross-Cluster Opportunities
What emerges when we combine clusters?
```

---

# ACTIVITY C: DEFINE

## Pillar: Innovation Strategist Mode

### Mindset Activation
> *"Markets reward genuine new value. Innovation without business model thinking is theater. Think like a chess grandmaster - bold declarations, devastating simplicity."*

### 3.1 Strategic Positioning

#### Blue Ocean Strategy Canvas

```markdown
## Strategy Canvas

### Current Industry Factors
List what competitors compete on:
1.
2.
3.
4.
5.

### Four Actions Framework

| Factor | ELIMINATE | REDUCE | RAISE | CREATE |
|--------|-----------|--------|-------|--------|
| [Factor 1] | | | | |
| [Factor 2] | | | | |
| [Factor 3] | | | | |
| [Factor 4] | | | | |

**ELIMINATE**: Which factors should be eliminated that the industry takes for granted?

**REDUCE**: Which factors should be reduced well below the industry standard?

**RAISE**: Which factors should be raised well above the industry standard?

**CREATE**: Which factors should be created that the industry has never offered?

### New Value Curve
[Sketch the before/after value curve]
```

#### Value Proposition Design

```markdown
## Value Proposition Canvas

### Customer Profile

**Jobs**:
- Functional:
- Emotional:
- Social:

**Pains**:
- [Pain 1]: Severity (1-10)
- [Pain 2]: Severity (1-10)
- [Pain 3]: Severity (1-10)

**Gains**:
- [Gain 1]: Importance (1-10)
- [Gain 2]: Importance (1-10)
- [Gain 3]: Importance (1-10)

### Value Map

**Products & Services**:
-

**Pain Relievers**:
| Pain | How We Relieve It |
|------|-------------------|
| | |

**Gain Creators**:
| Gain | How We Create It |
|------|------------------|
| | |

### Fit Assessment
Which pains/gains do we address?
Which do we NOT address (and why)?
```

### 3.2 Solution Evaluation

#### Opportunity Scoring Matrix

| Criterion | Weight | Option A | Option B | Option C |
|-----------|--------|----------|----------|----------|
| User Value | 30% | | | |
| Feasibility | 25% | | | |
| Strategic Fit | 20% | | | |
| Time to Value | 15% | | | |
| Risk Level | 10% | | | |
| **TOTAL** | 100% | | | |

#### Assumption Mapping

```markdown
## Assumption Map

### Critical Assumptions (High Impact, High Uncertainty)
| Assumption | Impact | Certainty | Validation Method |
|------------|--------|-----------|-------------------|
| [Assumption] | High | Low | [How to test] |

### Important Assumptions (High Impact, Medium Uncertainty)
| Assumption | Impact | Certainty | Validation Method |
|------------|--------|-----------|-------------------|
| [Assumption] | High | Medium | [How to test] |

### Test Plan
Priority order for assumption testing:
1.
2.
3.
```

### 3.3 Research Synthesis

#### Final Research Report Template

```markdown
# Pre-PRD Research Report: [Project Name]

**Research Period**: [Start Date] - [End Date]
**Research Lead**: [Name]
**Participants**: [Names/Roles]

## Executive Summary
[2-3 paragraphs summarizing key findings and recommendation]

## 1. Problem Definition

### The Problem We're Solving
[Clear problem statement]

### Who Has This Problem
[User segments and characteristics]

### Problem Evidence
| Evidence Type | Source | Finding |
|---------------|--------|---------|
| Interviews | [N] stakeholders | [Key insight] |
| Data | [Source] | [Key metric] |
| Market | [Research] | [Key finding] |

### Root Causes Identified
1. [Root cause 1]
2. [Root cause 2]
3. [Root cause 3]

## 2. Market Context

### Competitive Landscape
[Summary of competitive analysis]

### Market Gaps & Opportunities
[Where we can win]

### Relevant Trends
[What's changing in this space]

## 3. User Insights

### Jobs to Be Done
[Primary JTBD statement]

### Key Pain Points
| Pain Point | Severity | Frequency | Quote |
|------------|----------|-----------|-------|
| | | | |

### Desired Gains
| Gain | Importance | Current Satisfaction |
|------|------------|---------------------|
| | | |

## 4. Solution Space Exploration

### Ideas Generated
[Summary of brainstorming output]

### Top Opportunities
| Opportunity | Value | Feasibility | Strategic Fit |
|-------------|-------|-------------|---------------|
| | | | |

### Recommended Direction
[Which opportunity to pursue and why]

## 5. Strategic Positioning

### Value Proposition
[One-liner value proposition]

### Differentiation
[How this differs from alternatives]

### Success Metrics
| Metric | Current State | Target | Timeline |
|--------|---------------|--------|----------|
| | | | |

## 6. Assumptions & Risks

### Critical Assumptions
[List with validation plans]

### Key Risks
| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| | | | |

## 7. Recommendation

### Go / No-Go
[Clear recommendation]

### Rationale
[Why this recommendation]

### Next Steps
1. [Step 1]
2. [Step 2]
3. [Step 3]

## 8. Traceability Summary

### Research Artifacts Index
| ID Range | Type | Count | Key Findings |
|----------|------|-------|--------------|
| [PROJ]-A-INT-001 to XXX | Interviews | [N] | [Summary] |
| [PROJ]-A-COMP-001 to XXX | Competitive | [N] | [Summary] |
| [PROJ]-A-JTBD-001 to XXX | Jobs-to-be-Done | [N] | [Summary] |
| [PROJ]-B-IDEA-001 to XXX | Ideas | [N] | [Summary] |
| [PROJ]-B-ROOT-001 to XXX | Root Causes | [N] | [Summary] |
| [PROJ]-C-OPP-001 to XXX | Opportunities | [N] | [Summary] |

### Ready for PRD
Findings approved for PRD inclusion:
- [ ] Traceability matrix complete
- [ ] All IDs assigned
- [ ] Exclusions documented

## Appendices
- A: Interview Transcripts/Notes
- B: Competitive Analysis Details
- C: Brainstorming Session Outputs
- D: Data Sources
```

---

# Quick Reference Cards

## Business Analyst Mode

**Trigger**: "I need to gather evidence and requirements"

**Key Questions**:
- What do we know for certain?
- What's the evidence?
- Who are the stakeholders?
- How do we measure success?

**Tools**: Interviews, 5 Whys, JTBD, Competitive Analysis

**Output**: Validated problem statement, stakeholder map, market insights

---

## Brainstorming Coach Mode

**Trigger**: "We need new ideas and possibilities"

**Key Questions**:
- What if we tried...?
- YES AND what else?
- What's the wildest version?
- How might we...?

**Tools**: SCAMPER, Crazy 8s, Six Hats, Random Input

**Output**: Idea backlog, opportunity list, creative options

---

## Creative Problem-Solver Mode

**Trigger**: "We need to understand root causes"

**Key Questions**:
- What's really going on?
- What's the system doing?
- Where's the constraint?
- What contradictions exist?

**Tools**: Systems Mapping, 5 Whys, TOC, TRIZ

**Output**: Root cause analysis, system map, leverage points

---

## Innovation Strategist Mode

**Trigger**: "We need to position this strategically"

**Key Questions**:
- Why would anyone care?
- What's our unfair advantage?
- What can we stop doing?
- Where's the blue ocean?

**Tools**: Blue Ocean Canvas, Value Proposition Canvas, Strategy Canvas

**Output**: Strategic positioning, value proposition, differentiation

---

# Common Pitfalls

| Pitfall | Symptom | Fix |
|---------|---------|-----|
| **Solution Bias** | Already decided on solution before research | Write down your assumptions, then actively try to disprove them |
| **Confirmation Seeking** | Only finding evidence that supports initial idea | Assign someone to argue the opposite position |
| **Stakeholder Sampling Bias** | Only talking to friendly/available stakeholders | Create stakeholder matrix, ensure coverage |
| **Analysis Paralysis** | Research never ends, no decisions made | Set time-box, define "good enough" criteria upfront |
| **Idea Attachment** | Team falls in love with first idea | Force generation of 10+ alternatives before evaluating |
| **Missing the Why** | Understanding what but not why | Keep asking "why does that matter?" |
| **Surface Problems** | Treating symptoms, not causes | Use 5 Whys until you hit organizational/systemic issues |
| **Competitive Tunnel Vision** | Only looking at direct competitors | Include non-consumption and indirect alternatives |

---

# Facilitation Tips

## For Remote Sessions
- Use collaborative tools (Miro, FigJam, etc.)
- Build in extra breaks (Zoom fatigue is real)
- Use round-robin to ensure all voices heard
- Record sessions (with permission) for later reference

## For Difficult Stakeholders
- Start with their concerns, not yours
- Use "I'm curious about..." not "Why do you..."
- Find common ground first
- Follow up 1:1 if needed

## For Time-Constrained Research
**Minimum Viable Research** (if you only have 1 week):
1. Day 1-2: 3-5 stakeholder interviews
2. Day 3: Competitive scan (2 hours)
3. Day 4: 90-minute brainstorm session
4. Day 5: Synthesis and recommendation

## Transition to PRD Phase

Hand off to PRD phase:
- Validated problem statement
- Stakeholder map with priorities
- Competitive positioning
- Top 3-5 opportunity areas
- Critical assumptions list
- Success metrics definition
- Go/No-Go recommendation with rationale

---

# Output Location

Save research deliverables to: `docs/research/YYYY-MM-DD-[project-name]/`

Recommended structure:
```
docs/research/YYYY-MM-DD-[project-name]/
├── research-report.md          # Final synthesis
├── traceability-matrix.md      # ID tracking -> PRD linkage
├── interviews/                  # Interview notes (A-INT-XXX)
│   ├── interview-[name].md
│   └── ...
├── analysis/                    # Analysis artifacts (A-COMP, A-JTBD, B-ROOT)
│   ├── competitive-analysis.md
│   ├── jtbd-analysis.md
│   └── systems-map.md
├── ideation/                    # Brainstorm outputs (B-IDEA-XXX)
│   └── session-[date].md
├── opportunities/               # Strategic outputs (C-OPP-XXX)
│   └── opportunity-evaluation.md
└── assets/                      # Supporting materials
    └── ...
```

---

## Learning Mode Integration

### Decision Transparency Triggers
- **Research direction**: Explain why certain research methods were chosen
- **Stakeholder selection**: Show reasoning for interview prioritization
- **Insight interpretation**: Explain how findings lead to conclusions
- **Go/No-Go reasoning**: Full transparency on recommendation rationale

### Debate Invitations
- **Problem framing**: When problem could be defined multiple ways
- **Root cause selection**: When multiple root causes seem valid
- **Opportunity prioritization**: When several paths seem viable
- **Assumption risk**: When critical assumptions have unclear impact

### Feedback Requests
- After stakeholder interviews: Validate completeness of perspective
- After competitive analysis: Confirm competitor coverage
- After brainstorming: Rate idea quality and quantity
- At phase gate: Research quality rating (1-5)

### Example Feedback Request
```markdown
<feedback-request>
**Context:** Research phase completed for [Project Name]

**Seeking Feedback On:**
1. Did we interview the right stakeholders?
2. Is the competitive landscape complete?
3. Are the root causes we identified accurate?
4. Is the recommended direction sound?

**Questions:**
- Any stakeholders we missed?
- Competitors we overlooked?
- Alternative interpretations of the data?

**Rating Request:** On a scale of 1-5, how confident are you in our research findings?

**Improvement Ideas Welcome:** What would make this research stronger?
</feedback-request>
```
