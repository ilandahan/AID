# Research Documents (Phase 0: Discovery)

This folder contains research artifacts created during Phase 0 (Discovery).

## Naming Convention

Research projects use folder-based organization:

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
    ├── stakeholder-map.png     # Nano Banana Pro generated
    └── competitive-landscape.png
```

## Purpose

Phase 0 research validates problem spaces before committing to PRD creation.

**Key Activities:**
- Problem Analysis (5 Whys, Problem Severity)
- Stakeholder Research (Interviews, Power/Interest Matrix)
- Market & Competitive Research (JTBD, Competitive Analysis)
- Root Cause Investigation
- Go/No-Go Decision

## Traceability IDs

All research findings use IDs for PRD linkage:

```
[Project]-[Activity]-[Type]-[Number]

Examples:
- PROJ-A-INT-001  = Interview finding #1
- PROJ-B-IDEA-003 = Brainstorming idea #3
- PROJ-C-OPP-002  = Opportunity #2
```

## Exit Criteria (Gate to Phase 1)

Before advancing to PRD:
- [ ] Problem validated with multiple stakeholders
- [ ] Root causes identified and verified
- [ ] Market/competitive landscape understood
- [ ] Solution space explored (not just one idea)
- [ ] Strategic positioning defined
- [ ] All assumptions made explicit
- [ ] Go/No-Go decision justified with evidence
- [ ] Traceability matrix complete

## Commands

| Command | Purpose |
|---------|---------|
| `/discovery [project]` | Start Phase 0 research |
| `/gate-check` | Check Phase 0 → 1 requirements |
| `/aid end` | Complete phase with feedback |
| `/phase-advance` | Move to Phase 1 (PRD) |
