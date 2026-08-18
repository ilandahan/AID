# Discovery Phase Skill

> **Source**: `.claude/skills/pre-prd-research/SKILL.md`, `.claude/skills/aid-discovery/SKILL.md`
>
> This file is a quick reference. The main skill definitions are in the `.claude/skills/` directory.

## Quick Reference

**Phase**: 0 - Discovery
**Purpose**: Validate problem space and gather research insights before PRD
**Output**: `docs/research/YYYY-MM-DD-[project-name]/`

## Key Activities

### Activity A: UNDERSTAND
- Problem Analysis (5 Whys, Problem Severity Assessment)
- Stakeholder Research (Interviews, Power/Interest Matrix)
- Market & Competitive Research (JTBD, Competitive Analysis)

### Activity B: EXPLORE
- Divergent Thinking (SCAMPER, Crazy 8s, Six Hats)
- Root Cause Investigation (Systems Thinking, TRIZ, TOC)
- Opportunity Synthesis (Insight Clustering)

### Activity C: DEFINE
- Strategic Positioning (Blue Ocean Canvas, Value Proposition)
- Solution Evaluation (Opportunity Scoring, Assumption Mapping)
- Research Synthesis (Final Report)

## Exit Criteria (Gate to Phase 1)

- [ ] Problem validated with multiple stakeholders
- [ ] Root causes identified and verified
- [ ] Market/competitive landscape understood
- [ ] Solution space explored (not just one idea)
- [ ] Strategic positioning defined
- [ ] All assumptions made explicit and tested
- [ ] Go/No-Go decision justified with evidence
- [ ] Traceability matrix complete with IDs (RES-XXX)

## Traceability ID Format

```
[Project]-[Activity]-[Type]-[Number]

Examples:
- PROJ-A-INT-001  = Interview finding #1
- PROJ-B-IDEA-003 = Idea #3
- PROJ-C-OPP-002  = Opportunity #2
```

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
    └── stakeholder-map.png     # Nano Banana Pro
```

## Skills Loaded in Phase 0

| Skill | Purpose |
|-------|---------|
| `pre-prd-research` | Comprehensive research methodology |
| `aid-discovery` | Research validation and Go/No-Go |
| `nano-banana-visual` | Visual artifacts (optional) |

## Commands

| Command | Purpose |
|---------|---------|
| `/discovery` | Start Phase 0 research |
| `/gate-check` | Check Phase 0 → 1 requirements |
| `/aid end` | Complete phase with feedback |
| `/phase-advance` | Move to Phase 1 (PRD) |

## Cumulative Learnings

See `cumulative.md` for project-specific learnings captured by the memory system.
