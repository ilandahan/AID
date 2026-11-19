# AID Phase Gate System

The AID methodology describes a 6-phase lifecycle with a gate between each phase. The
method is to finish each phase and get explicit approval before advancing. This is
guidance for how to work: the user can move forward without it with a `jump` (run by
`/aid-start`, which Claude Code asks the user to confirm). What the hooks actually enforce
is described under [Enforcement](#enforcement).

## 6-Phase Lifecycle

```
Phase 0 --> Phase 1 --> Phase 2 --> Phase 3 --> Phase 4 --> Phase 5
Discovery     PRD      Tech Spec   Impl Plan     Dev       QA & Ship
```

## Phase Permissions

| Phase | Allowed | Not yet (methodology) |
|-------|---------|---------|
| 0 Discovery | Research, stakeholders, competitive analysis | PRD, architecture, code |
| 1 PRD | + Requirements, scope, user stories | Architecture, code, Jira |
| 2 Tech Spec | + Architecture, schemas, APIs | Code, Jira issues |
| 3a Consolidation | + Contradiction resolution, consolidate specs | Jira issues, code |
| 3b Breakdown | + Task decomposition, sprint planning | Jira creation (guidance), code |
| 3c Jira Population | + Jira epics, stories, tasks with full info | Production code |
| 4 Development | + Code, tests, components | Deployment (guidance) |
| 5 QA & Ship | Everything | - |

The hooks enforce only the code rows: source writes and code runs before Phase 4. Jira
work and deployment are not checked by any hook; those rows are the method's guidance.

## Gate Transition Requirements

The method's checklist before advancing to the next phase (guidance; `/phase-advance`
checks the recorded review and approval, and the user can override or `jump`):

1. **Deliverables complete** — All required outputs for the current phase exist
2. **Quality check passed** — Score of 7.0+ from the reflection agent
3. **Human approval** — Explicit sign-off via `/phase-approve`
4. **No blockers** — No open questions or unresolved issues

## Enforcement

The write and bash phase gates are hooks that check every Write, Edit, MultiEdit,
NotebookEdit, Bash and PowerShell call against the current phase (PowerShell has its own
rules; see [SECURITY-MODEL.md](SECURITY-MODEL.md#the-powershell-tool)). Since 3.0.8 they
**block by default** in an AID project.

| Level | On a violation |
|-------|----------------|
| `block` (default) | The call is denied, with the reason and a way forward. |
| `warn` | The call is allowed, and Claude gets a warning. Code runs and interpreter one-liners (`python -c`, `node -e`) are allowed before Phase 4, so project code can do anything your account can; control files stay refused. |
| `log` | The call is allowed and only recorded in `.aid/audit/`. Same cost as `warn`: code runs and interpreter one-liners are allowed before Phase 4; control files stay refused. |

Every session start in a project with a gate at `log` or `warn` states each such gate and
its level, whether or not it changed since the last session.

### Hooks that act outside AID projects

The phase rules apply only in AID projects, but three of AID's hooks are not limited to them:

- **dev-pipeline-gate (Stop)** runs in every git repo. When a turn ends with changed
  source files, it may run the repo's own checkers (for example
  `node_modules/typescript/bin/tsc`) and can block the turn on errors.
- **plan-execution-pipeline (ExitPlanMode)** runs in every project. When a plan is
  approved it injects the pipeline instructions and writes a session marker,
  `~/.claude/.loop1-kickoff/<session_id>`.
- **The Bash gate (PreToolUse)** answers "ask" in every folder for the confirmed
  `aid_session.py` commands, the breather installer and `scripts/init-project.sh`, from the
  Bash and the PowerShell tool, in their exact forms only (other spellings of the two
  scripts are not asked outside AID projects, from Phase 4 on, or at `log` or `warn`), and
  denies other spellings of a confirmed call that it can parse (see
  [SECURITY-MODEL.md](SECURITY-MODEL.md#human-confirmation-ask)).

To lower a gate for one project, set it in `.aid/hooks/config.json`. Levels are
case-insensitive, and an unknown value counts as `block`:

```json
{ "enforcement": { "phase_gate_write": "warn", "phase_gate_bash": "log" } }
```

Lowering a gate relaxes only the phase rules. Writes to AID's own control files (such as
this config file and `.claude/settings.json`) are refused at every level. From the
PowerShell tool, the exact canonical form of a human-confirmed `aid_session.py` subcommand,
and the exact form of the breather installer and of `scripts/init-project.sh`, get "ask" in
every folder, phase and level, and in an AID project every other PowerShell command whose text
names `aid_session` is refused at every level. That check reads the command text, so it is
best effort: a PowerShell call whose script name is hidden in a variable
(`python $env:SCRIPT reset`) runs without a prompt outside AID projects, and in an AID
project from Phase 4 on, or at `log` or `warn`.

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
