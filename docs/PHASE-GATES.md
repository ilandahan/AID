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

## Agentic Deliverables (3.1)

Every project, AI or not, delivers these at each gate, scaled to its solution-shape level
on the ladder (0 Process change, 1 Deterministic automation, 2 Single LLM call inside a fixed
flow, 3 Workflow, 4 Agent, 5 Multi-agent), in three tiers of depth: levels 0-1, 2-3 and 4-5.
At level 0-1 each takes its classic form (Eval Plan → acceptance tests, Telemetry → logs and
metrics, Rollout → staged release plus rollback). No deliverable may be "N/A", but at levels 0-1
it may be one line pointing to where it is already covered; reviewers score that as fully met.

| Phase | Agentic deliverable | Skill |
|-------|---------------------|-------|
| 0 Discovery | Solution shape hypothesis on the ladder; how much the problem varies; who bears the cost of an error | `aid-discovery` |
| 1 PRD | §1.5 Solution Shape (lowest level that works, every step up justified); §7A.1 Charter, 7A.2 Tools & Permissions, 7A.3 Context & Data, 7A.4 Failure Modes & Guardrails, 7A.5 Why-Chain, 7A.6 Eval Plan, 7A.7 Telemetry & Traces, 7A.8 Rollout & Kill Switch; North Star / supporting / guardrail metrics; WHY + shape brief (`docs/prd/WHY-SHAPE-BRIEF-<feature>.md`); 20-30 seed eval cases (`docs/prd/SEED-EVALS-<feature>.md`, or a cross-reference at levels 0-1); level signed by the tech lead (`docs/prd/ADR-SHAPE-<feature>.md`, matching the §1.5 "Signed level" line) | `aid-prd`, `why-driven-decision` |
| 2 Tech Spec | Agent architecture traced to every §7A item: orchestration pattern, permission policy, guardrails, trace schema, eval harness, model fallbacks, cost/latency budgets, kill switch | `aid-tech-spec`, `system-architect` |
| 3 Impl Plan | 3a: §1.5 level and §7A carried into the consolidated spec. 3b: 8 agentic tasks: golden set, eval harness and gate, red-team cases, telemetry and traces, rollout stages, kill switch, permission policy + guardrails (9.2/9.3), data access, redaction, retention (7A.3); at levels 0-1 they fold into existing test, logging and release tasks, tagged with their 7A item; "Targeted + regression evals at threshold for the slices it touches" in the Definition of Done (the eval release gate is Phase 5 only) | `aid-impl-plan` |
| 4 Development | Eval-driven development (evals before prompt/agent changes), traces on by default, versioned prompts and tools, regression eval on every change | `aid-development`, `test-driven` |
| 5 QA & Ship | Phase 5 exit: eval release gate passed (on the held-out split: 7A.6 threshold, red-team, never-do checks), shadow stage live, kill switch tested, stage criteria agreed; monitoring of drift, cost per successful task, escalation rate and response time, guardrail metrics. Each later promotion (human approval → autonomous) is a recorded decision by the 7A.8 owner, outside the phase gate | `aid-qa-ship` |

The reflection criteria (`skills/reflection/criteria/phase-*.yaml`), `phase-review-agent`,
`prd-validator` and `phase2-techspec-pm-reviewer` check these.

### The Phase 1 flow (A9): agents draft in parallel; humans review and decide once

1. **WHY + shape brief.** The PM runs the WHY conversation (`why-driven-decision`): WHY / 5 Whys,
   the 6 shape questions (§1.5), on whose behalf it acts, who bears the cost of an error, what must
   never happen (who approves actions is Q6). Saved as `docs/prd/WHY-SHAPE-BRIEF-<feature>.md`, with a
   level hypothesis (0-5).
2. **`/prd`:** `prd-research-aggregator` (alone, first), then in ONE message, in parallel:
   `prd-writer`, `phase1-solution-shaper`, `phase1-charter-drafter`, `phase1-eval-planner`.
3. **Merge** into `docs/prd/PRD-<feature>.md` and the seed cases into
   `docs/prd/SEED-EVALS-<feature>.md`; conflicts between drafts go to the PM, never resolved silently.
4. **PM review.**
5. **Shaping session:** the PM and the tech lead review the proposed level and the seed cases
   (optionally a time-boxed spike that runs the lowest level against them, run by a human OUTSIDE the AID project, never by
   Claude in Phase 1, on de-identified cases, with an approved provider setup); the tech
   lead signs the level (`docs/prd/ADR-SHAPE-<feature>.md`), recording any spike result.
6. **`prd-validator`**, then `/gate-check` and `/phase-approve` (human).

**Timing (no relay):** the seed cases are written in Phase 1. QA grows the golden set and its
held-out split (`tests/evals/golden/`) in parallel with Phases 2-4; it does not block the tech spec,
and it must be complete only for the Phase 5 release gate. Phase 3 ordering: seed cases + dev/targeted suite -> eval harness -> prompt/tool/agent tasks; QA grows the golden set in parallel; it must be complete before the Phase 5 gate. The data scientist calibrates the LLM judge in
Phase 4, when a judge is introduced.

## Enforcement

The write and bash phase gates are hooks that check every Write, Edit, MultiEdit,
NotebookEdit, Bash and PowerShell call against the current phase (PowerShell has its own
rules; see [SECURITY-MODEL.md](SECURITY-MODEL.md#the-powershell-tool)). Since 3.0.8 they
**block by default** in an AID project. Folders without AID are never touched.

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
this config file and `.claude/settings.json`) are refused at every level. So is any
`aid_session.py` call from the PowerShell tool.

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
