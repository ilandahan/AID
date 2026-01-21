# /discovery

Start Phase 0: Discovery & Research.

## Purpose

Entry point for Phase 0 - the foundational research phase that ensures PRDs are built on validated insights rather than assumptions.

## What It Does

1. Verifies project is in Phase 0 (or initializes to Phase 0)
2. Loads research skills: `pre-prd-research`, `aid-discovery`
3. Creates research output folder structure
4. Guides through research workflow

## Usage

```
/discovery
/discovery [project-name]
```

## Phase 0 Overview

```
    Phase 0         Phase 1       Phase 2        Phase 3        Phase 4       Phase 5
  ┌───────────┐   ┌─────────┐   ┌──────────┐   ┌──────────┐   ┌─────────┐   ┌─────────┐
  │ DISCOVERY │──▶│   PRD   │──▶│ Tech Spec│──▶│Impl Plan │──▶│   Dev   │──▶│QA & Ship│
  │           │   │         │   │          │   │          │   │         │   │         │
  │ Research  │   │ Require-│   │ Architec-│   │ Task     │   │ Code &  │   │ Deploy &│
  │ Validate  │   │ ments   │   │ ture     │   │ Breakdown│   │ Tests   │   │ Release │
  └───────────┘   └─────────┘   └──────────┘   └──────────┘   └─────────┘   └─────────┘
       ▲
       │
    YOU ARE HERE
```

## Discovery Activities

### Activity A: Understand
- Problem Analysis (5 Whys, Problem Severity)
- Stakeholder Research (Interviews, Power/Interest Matrix)
- Market & Competitive Research (JTBD, Competitive Analysis)

### Activity B: Explore
- Divergent Thinking (SCAMPER, Crazy 8s, Six Hats)
- Root Cause Investigation (Systems Thinking, TRIZ)
- Opportunity Synthesis

### Activity C: Define
- Strategic Positioning (Blue Ocean, Value Proposition Canvas)
- Solution Evaluation (Opportunity Scoring, Assumption Mapping)
- Research Synthesis (Final Report)

## Output Structure

```
docs/research/YYYY-MM-DD-[project-name]/
├── research-report.md          # Final synthesis
├── traceability-matrix.md      # Research -> PRD linkage
├── interviews/
│   └── interview-[name].md
├── analysis/
│   ├── competitive-analysis.md
│   ├── jtbd-analysis.md
│   └── systems-map.md
├── ideation/
│   └── session-[date].md
├── opportunities/
│   └── opportunity-evaluation.md
└── assets/
    └── stakeholder-map.png     # Nano Banana Pro generated
```

## Exit Criteria (Gate to Phase 1)

Before advancing to PRD, verify:
- [ ] Problem validated with multiple stakeholders
- [ ] Root causes identified and verified
- [ ] Market/competitive landscape understood
- [ ] Solution space explored (not just one idea)
- [ ] Strategic positioning defined
- [ ] All assumptions made explicit and tested
- [ ] Go/No-Go decision justified with evidence
- [ ] Traceability matrix complete with IDs (RES-XXX)

## Visual Artifacts (Nano Banana Pro)

If `ENABLE_NANO_BANANA=true` in your .env:
- "Create stakeholder map" → Stakeholder power/interest diagram
- "Create competitive landscape" → Market positioning visual
- "Create user journey" → User experience flow
- "Create systems map" → System interaction diagram

## Related Commands

| Command | Purpose |
|---------|---------|
| `/phase` | Show current phase status |
| `/gate-check` | Check if ready to advance to Phase 1 |
| `/aid end` | Complete Phase 0 with feedback |
| `/phase-advance` | Move to Phase 1 (PRD) after gate passes |
| `/prd` | Start Phase 1 after Discovery approved |

## Example Session

```
> /discovery user-authentication

Starting Phase 0: Discovery for "user-authentication"

Created: docs/research/2024-12-21-user-authentication/

Skills loaded:
- pre-prd-research (Business Analysis, Brainstorming, Problem-Solving, Innovation Strategy)
- aid-discovery (Research methodology)
- nano-banana-visual (Optional - for visual artifacts)

Begin with Activity A: UNDERSTAND

Suggested first steps:
1. Define the problem statement (SCQ format)
2. Identify stakeholders to interview
3. Schedule stakeholder interviews

What would you like to focus on first?
```

## Notes

- Discovery is the foundation - skip it at your peril
- Every research finding gets a traceability ID (RES-XXX)
- Research informs PRD requirements - nothing in PRD without research backing
- Go/No-Go decision happens here - it's okay to stop if research says no
