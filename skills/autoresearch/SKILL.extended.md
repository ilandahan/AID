> Human-readable companion to SKILL.md. The LLM loads SKILL.md only.

# Autoresearch — the bounded keep/revert runner

## What it is

Autoresearch applies the Karpathy autoresearch pattern to code: **one mutable artifact, one
fixed evaluation harness, one comparable score**, looped until it stops improving.

Each iteration does exactly this:

```
snapshot → ONE focused edit → score → keep if strictly better, else revert → log
```

The word doing the work is **strictly**. An edit is kept only when the composite score is
*greater than* the best score so far. Ties revert. That is what stops the loop from
drifting sideways through equally-good rewrites and calling it progress.

## Why it exists

A model asked to "improve this code" will happily produce twenty edits and no way to tell
whether the result is better than where it started. Autoresearch makes improvement
*measurable and reversible*:

- **Measurable** — the harness is frozen before the first edit. The score means the same
  thing on iteration 1 and iteration 15.
- **Reversible** — every edit is snapshotted before it is applied, so a bad edit costs
  nothing but one iteration.
- **Bounded** — the loop always terminates. See *Stop conditions* below.

## The three modes

The pipeline invokes autoresearch at three points, each with its own prompt file and its
own harness. The mode decides what "better" means.

| Mode | Stage | Harness | Rule |
|------|-------|---------|------|
| `design` | AR-1, **before** TDD | reflection-agent judgement only, scored against `phase-4a-code-design.yaml` | Judge-only. **No interface, public-API or data-shape changes** — this pass tidies the inside of the box, never its edges. |
| `function` | AR-2, **after** TDD | the frozen test suite as a HARD Tier-1 gate, multiplied by reflection quality (`phase-4b-code-function.yaml`) | A test going red is an automatic revert. Quality cannot buy back a broken test: `composite = quality × (all gates pass ? 1 : 0)`. |
| `acceptance` | AR-3 | acceptance-criteria validators + reflection | Scored against the frozen Task Brief, not against what the code happens to do. |

Each mode reads its own program file: `program.ar-design.md`, `program.ar-function.md`,
`program.ar-acceptance.md`. Those files are authoritative — the mode's scoring formula,
editable surface and gates all come from there.

## How it gets invoked

**Normally**, the `/pipeline` state machine calls it at the AR_DESIGN, AR_FUNCTION and
AR_ACCEPTANCE steps. Placeholders (`{{TEST_COMMAND}}`, iteration caps, KPI target) are
resolved from `.aid/pipeline/config.json`.

**Standalone**, a human can run one mode directly against a single artifact. You resolve
the placeholders yourself in that case.

## Configuration

All knobs live under `autoresearch` in `.aid/pipeline/config.json`:

| Key | Meaning |
|-----|---------|
| `kpi_target` | Minimum `why_alignment` score (0–10) |
| `ar_design.max_iterations` / `ar_function.max_iterations` | Iteration cap per pass |
| `ar_design.max_consecutive_reverts` / `ar_function.max_consecutive_reverts` | Plateau cap — consecutive failures to improve before stopping |
| `ar_function.internal_rounds` | Internal scoring rounds for AR-2 |
| `ar_acceptance.max_acceptance_rounds` | Hard cap on re-entering DEVELOP |
| `ar_acceptance.pass_rate_target` | Minimum acceptance-criteria pass rate (%) |
| `bundle_dir` | Where this skill lives (`~/.claude/skills/autoresearch`; a project `.claude/skills/autoresearch` overrides) |
| `criticality_profile` | Informs how strict the judging should be |

`config.default.json` in the pipeline-orchestrator skill carries the shipped defaults.

## Stop conditions

The loop is designed so it cannot run forever. It stops on the first of:

- `max_iterations` reached for the pass
- `max_consecutive_reverts` reached — the plateau signal, meaning further edits are not
  finding improvements
- the cost brake trips
- the target score is met

## Safety constraints

These are non-negotiable, and they are the reason this runner is safe to point at
production source:

- **Never auto-commits.** Validation only. It never runs destructive git commands.
- **Every mutable file is snapshotted before it is touched**, and a revert restores from
  that snapshot.
- **No scope reduction to game the score.** Deleting behaviour, criteria or tests to make
  a number go up is explicitly forbidden — that is the obvious exploit for any
  score-maximising loop, and the prompts call it out.
- **Rubric fingerprint (weak).** `verify-run.sh` step 8 recomputes a SHA-256 over the
  criteria YAML and `reflection-agent.md` only, and compares it with a hash the runner
  itself records in `.aid/pipeline/state.json`. That file is runner-writable, so the check
  is self-attested and is not a reliable tamper detector; a missing hash only warns.
- **AR-1 may not change interfaces.** Design cleanup must not ripple into callers.

## Scope of the harness guard

`bin/check-harness-immutable.mjs` is a PreToolUse hook on Write, Edit, MultiEdit and
NotebookEdit. It protects files by role (rubric YAMLs, the three scorer prompts,
`skills/autoresearch/**`, `skills/reflection/**`, `.claude/skills|agents/**`, Claude
settings, `.mcp.json`, `.aid/**/*.json` except runner state, per-task stage records such as
`fix-<n>.json` / `self-review-<n>.json`, the QA-gate verdicts in `.aid/qa/` and the
`~/.aid/feedback/` queue, the acceptance sources `.aid/qa/**/*.yaml|yml` (existing or new), and
an existing `.aid/pipeline/<task>/brief.md` or `config.frozen.json` (creating them once at
kickoff is allowed)), wherever the file lives: project, link target, AID
checkout or plugin cache.

- **It is a guardrail, not a sandbox.** It stops a score-maximising agent from editing its
  own harness with the four file-edit tools.
- **Out of scope and not reliably detected today:** writes through Bash, python/node
  subprocesses, git or MCP file tools. The step-8 fingerprint covers only the criteria YAML
  and `reflection-agent.md`, and its hash is self-attested in runner-writable `state.json`,
  so it does not catch what the guard misses.
- **It stays active for the whole session** after `/autoresearch` (a property of
  skill-frontmatter hooks). Harness edits belong in a new session without an AR pass.
- **AR passes cannot edit `skills/autoresearch/**` or `skills/reflection/**`**, including
  on AID's own tasks that own those trees. Run those tasks without an AR stage.

## Artifacts it leaves behind

| Path | Contents |
|------|----------|
| `.aid/pipeline/autoresearch/<task_id>/results.tsv` | One row per iteration: score, delta, kept/reverted. The audit trail. |
| `.aid/pipeline/autoresearch/<task_id>/snapshots/` | Pre-edit copies used for reverts |

`results.tsv` row 0 is the baseline score of the untouched code, so the value of the whole
pass is readable as one subtraction.

## Verifying a run

```bash
bash verify-run.sh /path/to/your/project
```

Read-only. It inspects the on-disk artifacts of the last run and reports PASS/WARN/FAIL
per expectation — including whether the recorded rubric fingerprint still matches the
active criteria file.

## Files in this skill

| File | Purpose |
|------|---------|
| `SKILL.md` | The runner instructions the LLM loads |
| `program.ar-design.md` | AR-1 pass definition |
| `program.ar-function.md` | AR-2 pass definition |
| `program.ar-acceptance.md` | AR-3 pass definition |
| `verify-run.sh` | Post-run checker (read-only) |
| `bin/check-harness-immutable.mjs` | PreToolUse guard: blocks edits to the frozen harness |

Scoring criteria live with the reflection skill, not here:
`../reflection/criteria/phase-4a-code-design.yaml` and
`phase-4b-code-function.yaml`.
