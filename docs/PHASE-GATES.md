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
3. **Merge** into `docs/prd/YYYY-MM-DD-<feature>.md` and the seed cases into
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
**block by default** in an AID project.

| Level | On a violation |
|-------|----------------|
| `block` (default) | The call is denied, with the reason and a way forward. |
| `warn` | The call is allowed, and Claude gets a warning. Code runs and interpreter one-liners (`python -c`, `node -e`) are allowed before Phase 4, so project code can do anything your account can; control files stay refused. |
| `log` | The call is allowed and only recorded in `.aid/audit/`. Same cost as `warn`: code runs and interpreter one-liners are allowed before Phase 4; control files stay refused. |

Every session start in a project with a gate at `log` or `warn` states each such gate and
its level, whether or not it changed since the last session.

### Hooks that act outside AID projects

The phase rules apply only in AID projects, but four of AID's hooks are not limited to them
once the plugin is installed (on the clone route only linked projects run AID hooks, so a
folder that is not linked has none of them):

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
  [SECURITY-MODEL.md](SECURITY-MODEL.md#human-confirmation-ask)). It also asks in every
  folder before the pipeline's `gate.mjs --resolve` runs, in its exact form
  (`node "<plugin>/skills/pipeline-orchestrator/gate.mjs" --resolve "<what was decided>"`);
  a non-exact spelling is not caught outside AID projects (see
  [SECURITY-MODEL.md](SECURITY-MODEL.md#what-aid-does-not-promise)). A direct call of
  either script (`"<plugin>/hooks/aid_session.py" approve`,
  `env "<plugin>/hooks/aid_session.py" reset`,
  `"<plugin>/skills/pipeline-orchestrator/gate.mjs" --resolve ok`) is judged like the
  `python` / `node` call (T17, F1), so "other spellings are denied" holds for it as written.
  A `--resolve` argument built at run time (`f=--re; ${f}solve`) is an accepted, not-caught
  obfuscation (A1).
- **The Write and Bash gates (PreToolUse)** refuse a write to a project `.aid/state.json`
  in every folder, AID project or not: from the Write, Edit, MultiEdit and NotebookEdit
  tools and from Bash and PowerShell commands that name it. Only `aid_session.py` writes
  it. Outside AID projects a name built at run time, or a write reached through a change of
  folder, a shell `-c` body or interpreter code, is not caught (see
  [SECURITY-MODEL.md](SECURITY-MODEL.md#what-aid-does-not-promise)).
- **Every-folder false denials.** A few harmless commands are refused in every folder, AID
  project or not, because the gate cannot tell them from a confirmed call or a state write:
  an interpreter whose script operand is built at run time (`python "$SCRIPT" "$INPUT"`) and
  archiving `.aid/state.json` (`tar czf b.tgz .aid/state.json`). Write the script path out,
  back the file up with `cp`, or run the command yourself with `!` (see
  [SECURITY-MODEL.md](SECURITY-MODEL.md#what-aid-does-not-promise)).

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

More limits and rules (details in
[SECURITY-MODEL.md](SECURITY-MODEL.md#what-aid-does-not-promise)):

- **The plugin's reviewers win (F4).** Reviewers are spawned as `aid:<name>`; the plugin's
  review criteria and standards always apply, and project files may only add criteria,
  never replace the plugin's agents or criteria. The T10 A3 accepted risk is gone; the
  pipeline skill marks this rule "F4 (2026-11-20)".
- **git add and commit before Phase 4** are on the allow-list, but your own git hooks
  (`pre-commit`, `core.hooksPath`) still run when you commit (N-5). The gate's message
  before Phase 4 says so ("git add/commit are allowed; your own git hooks ... still run
  when you commit", T17-7).
- **The UI-evidence (`.ui-verified`) and pipeline-state gates are self-attested**: the
  agent can create the evidence they check.
- **`.aid/pipeline/config.json`** (the pipeline's pass thresholds) is protected in layer C:
  the Write and Edit tools ask you before changing it, and a Bash write is refused (T16-4).
- **`find` over user config folders** naming agents or control files
  (`find ~/.claude -path '*agents*' -name x.md`) is refused in AID projects, because `find`
  can delete and run commands: an accepted, safe-direction false denial. Use `ls`.
- **Some reads of a linked install's control folders** (`less`, `find`, PowerShell
  `Get-Content`, `git -C <root> fetch`, `python -m pytest <root>/hooks`) are refused from a
  linked project: an accepted, safe-direction false denial (see the next bullet). Use
  `cat`, `head` or `grep`.
- **AID's recommendation queue** (`$AID_HOME/recommendations/`) and, for a project linked
  to an AID install outside it, that install's `hooks/`, `.claude-plugin/`, `agents/` and
  `skills/reflection/criteria/` are control files in every phase (T17). Writes to them are
  refused (the Write tools, `cp`, `mv`, `tee`, redirects, `sed -i`, `perl -i` and the other
  in-place commands). Reading them with `cat`, `head`, `grep` or `git log`/`status`/`diff`,
  and running a script there (`python "<plugin>/hooks/aid_session.py" status`), stays
  allowed (within the phase rules). Other commands that name the live-root folders from a
  linked project (`less`, `find`, PowerShell `Get-Content`, `git -C <root>` with a non-read
  subcommand such as `fetch`, `python -m pytest <root>/hooks`) are refused: an accepted,
  safe-direction false denial, as for the plugin cache copies. Only `aid_session.py
  memory-queue` / `memory-apply` write the recommendation queue.

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
