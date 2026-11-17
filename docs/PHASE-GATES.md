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

## Enforcement

The write and bash phase gates are hooks that check every Write/Edit and Bash call against
the current phase. Since 3.0.8 they **block by default** in an AID project. Folders without
AID are never touched.

| Level | On a violation |
|-------|----------------|
| `block` (default) | The call is denied, with the reason and a way forward. |
| `warn` | The call is allowed, and Claude gets a warning. |
| `log` | The call is allowed and only recorded in `.aid/audit/`. |

To lower a gate for one project, set it in `.aid/hooks/config.json`. Levels are
case-insensitive, and an unknown value counts as `block`:

```json
{ "enforcement": { "phase_gate_write": "warn", "phase_gate_bash": "log" } }
```

Lowering a gate relaxes only the phase rules. Writes to AID's own control files (such as
this config file and `.claude/settings.json`) are refused at every level.

The gates are a guardrail, not a sandbox. See [SECURITY-MODEL.md](SECURITY-MODEL.md) for
what they guarantee and how to add a hard boundary.

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
