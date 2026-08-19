# AID Phase Gate System

The AID methodology enforces a 6-phase lifecycle with strict gates between each phase. No phase can be skipped, and each gate requires explicit approval before advancing.

## 6-Phase Lifecycle

```
Phase 0 --> Phase 1 --> Phase 2 --> Phase 3 --> Phase 4 --> Phase 5
Discovery     PRD      Tech Spec   Impl Plan     Dev       QA & Ship
```

## Phase Permissions

| Phase | Allowed | Blocked |
|-------|---------|---------|
| 0 Discovery | Research, stakeholders, competitive analysis | PRD, architecture, code |
| 1 PRD | + Requirements, scope, user stories | Architecture, code, Jira |
| 2 Tech Spec | + Architecture, schemas, APIs | Code, Jira issues |
| 3a Consolidation | + Contradiction resolution, consolidate specs | Jira issues, code |
| 3b Breakdown | + Task decomposition, sprint planning | Jira creation, code |
| 3c Jira Population | + Jira epics, stories, tasks with full info | Production code |
| 4 Development | + Code, tests, components | Deployment |
| 5 QA & Ship | Everything | - |

## Gate Transition Requirements

Before advancing to the next phase, ALL of the following must be true:

1. **Deliverables complete** — All required outputs for the current phase exist
2. **Quality check passed** — Score of 7.0+ from the reflection agent
3. **Human approval** — Explicit sign-off via `/phase-approve`
4. **No blockers** — No open questions or unresolved issues

## Commands

| Command | Purpose |
|---------|---------|
| `/phase` | Show current phase and status |
| `/gate-check` | Check if ready to advance |
| `/phase-approve` | Human sign-off for current phase |
| `/phase-advance` | Move to next phase |

## Phase-Specific WHY Questions

Each phase has a core WHY question that must be answered:

| Phase | Core WHY Question |
|-------|-------------------|
| 0 | "WHY is this problem worth solving?" |
| 1 | "WHY does the user need this?" |
| 2 | "WHY this architecture?" |
| 3 | "WHY this breakdown? WHY these dependencies?" |
| 4 | "WHY this code? WHY these connections?" |
| 5 | "WHY is this ready to ship?" |

## State Tracking

Phase state is tracked in `.aid/state.json`. Claude reads this file before every action to verify phase compliance.

## Related

- Rules: `.claude/rules/general/phase-gates.md`
- Skill: `.claude/skills/phase-enforcement/SKILL.md`
- Agent: `.claude/agents/phase-review-agent.md`
