# program.ar-acceptance.md — AR-3: Post-QA Acceptance Closing Loop

> Adapted from Andrej Karpathy's autoresearch pattern, but applied at the
> **feature** level, not the line-of-code level. Instead of editing one file to
> minimize a loss, you validate the **complete delivered feature** against the
> **original request + STATED_WHY**, and where it falls short you re-enter the
> pipeline to execute the missing work — bounded, never forever.
>
> The agent is the runner. You read this file and follow it.

---

## MODE: acceptance (post-QA)

This pass runs **AFTER `PHASE_GATE`** (i.e. after QA: VISUAL_QA → TEST_REVIEW →
PHASE_GATE have all passed), and **BEFORE Phase 5** (API_TESTS → E2E_TESTS →
CERTIFICATION).

**This is NOT code micro-optimization.** AR-1 (`program.ar-design.md`) and AR-2
(`program.ar-function.md`) already optimized code quality and functional
correctness. Do **not** re-open or re-litigate certified code quality here.

The ONE question this pass answers:

> **Does the delivered feature, as a whole, satisfy the ORIGINAL_REQUEST and the
> STATED_WHY?**

If yes → record and exit to Phase 5. If no → the pipeline did not actually build
the right thing yet; write the gap as concrete work, re-enter `DEVELOP` for ONLY
that gap, and let the pipeline re-validate it. Bounded by a round cap.

---

## Runtime placeholders (filled before this prompt runs)

Filled from `.aid/context.json` + `.aid/pipeline/config.json` (`autoresearch`
block). Do NOT invent values — if a placeholder is empty, say so and stop.

| Placeholder | Source | Meaning |
|---|---|---|
| `{{WORKSPACE}}` | repo root | Absolute path to the project |
| `{{TASK_ID}}` | `.aid/context.json` → `current_task` | The task under acceptance |
| `{{CRITICALITY_PROFILE}}` | `config.json` | Risk profile (informs strictness) |
| `{{KPI_TARGET}}` | `config.autoresearch.kpi_target` (e.g. `8.0`) | Min `why_alignment` score (0–10) |
| `{{PASS_RATE_TARGET}}` | `config.autoresearch.ar_acceptance.pass_rate_target` (e.g. `90`) | Min acceptance-criteria pass-rate (%) |
| `{{MAX_ACCEPTANCE_ROUNDS}}` | `config.autoresearch.ar_acceptance.max_acceptance_rounds` (e.g. `2`) | Hard cap on re-enter-DEVELOP rounds |
| `{{SAFETY_CRITICAL_FLOWS}}` | `.aid/context.json` | Flows that require extra care if re-developed |
| `{{RECORD_FILE}}` | `.aid/pipeline/autoresearch/{{TASK_ID}}/results.tsv` | The per-task experiment log |

---

## Fixed harness (READ-ONLY — DO NOT REINVENT, DO NOT MODIFY)

This pass **orchestrates existing components** into a bounded loop. You do not
build new validators, new criteria, or new scorers. Treat all of the following
as read-only inputs to the evaluation:

1. **`ORIGINAL_REQUEST`** — read VERBATIM from the **frozen Task Brief**
   `{{WORKSPACE}}/.aid/pipeline/{{TASK_ID}}/brief.md` (the `## ORIGINAL_REQUEST`
   section), which the orchestrator froze at pipeline kickoff. This is the
   compaction-proof source — a mid-run compaction may have erased the original
   prompt from conversation, so do NOT trust conversation memory. Fall back to
   `.aid/context.json` `original_request` only if `brief.md` is absent. Do NOT
   summarize or paraphrase, and do NOT validate against `current_task.description`
   (that is a later paraphrase, not the original ask).
2. **`STATED_WHY`** — read EXACT TEXT from the same `brief.md` (`## STATED_WHY`),
   `.aid/context.json` `stated_why` as fallback. The business/user WHY established
   for this feature. Do NOT summarize.
3. **`reflection-agent`** + existing **`phase-5-qa-ship.yaml`**. Its
   `why_alignment` criterion is **weight 3** — that is your "delivers the
   promised value" signal. **Path resolution (project → user):** resolve both the
   criteria file `.claude/skills/reflection/criteria/phase-5-qa-ship.yaml` and the
   agent prompt `.claude/agents/reflection-agent/AGENT-PROMPT.md` from
   `{{WORKSPACE}}/.claude/…` if present, else from the user-level default
   `~/.claude/…` (the engine ships user-level). Spawn the subagent named
   `reflection-agent` (Task, `subagent_type: general-purpose`, `model: opus`,
   AGENT-PROMPT.md with variables filled). Only if `phase-5-qa-ship.yaml` is absent
   in **both** locations do you **ESCALATE** (criteria file is required). Variable contract:
   - `ORIGINAL_REQUEST` / `STATED_WHY` — as above.
   - `PHASE_NUMBER`: 5, `PHASE_NAME`: "QA & Ship".
   - `PHASE_CRITERIA`: contents of `phase-5-qa-ship.yaml`.
   - `OUTPUT_TO_EVALUATE`: a concise description of the delivered feature + the
     acceptance results matrix (below).
   - `FILES_TO_VERIFY`: the production + test files the feature touches.
4. **`phase5-acceptance-validator`** agent → emits an `[AV-XXX]`
   **MET / PARTIAL / NOT_MET** matrix, a `blockers` list, and a `pass_rate`.
5. **`phase4-intent-validator`** agent → emits
   **ALIGNED / PARTIALLY_ALIGNED / MISALIGNED** per user-story / intent.
6. **Acceptance criteria — tiered source** (what "done" means):
   1. `.aid/qa/{{TASK_ID}}.yaml` if present (full AID — the source of truth), else
   2. **brief-derived** — extract acceptance criteria from the frozen `brief.md`
      (its `## DEVELOP PLAN` verification/acceptance section + the `## STATED_WHY`),
      and **note in your output that acceptance ran in brief-derived mode** (no PRD
      qa file), else
   3. if even `brief.md` is absent → **ESCALATE** (no durable acceptance baseline).

### GRACEFUL FALLBACK (some projects only have reflection-agent)

If `phase5-acceptance-validator` and/or `phase4-intent-validator` are **NOT
present** in the current project (e.g. the project ships only the
`reflection-agent`), then:

- Fall back to: **`reflection-agent` + `phase-5-qa-ship.yaml` (resolved project→user
  per item 3) + the tiered acceptance source (item 6).**
- Derive `pass_rate` **directly from the acceptance criteria** (the tiered source —
  `qa/{{TASK_ID}}.yaml` if present, else brief-derived): walk every criterion, mark
  each MET / PARTIAL / NOT_MET against the delivered feature (verifying claims in
  source/test files, not asserting), and compute
  `pass_rate = (MET count) / (total criteria) × 100`. PARTIAL counts as NOT met.
- Derive `why_alignment` from the reflection-agent's `why_alignment` dimension
  score (0–10).
- Derive `blockers` as the list of NOT_MET criteria that are required (non-optional).
- **State explicitly in your output** that you ran in fallback mode and which
  agents were missing, so the human knows the matrix came from
  reflection + criteria rather than the dedicated validators.

If `.aid/qa/{{TASK_ID}}.yaml` is missing, do NOT fabricate criteria — **derive them
from the frozen `brief.md`** per the tiered source (item 6, tier 2). Only if
`brief.md` is ALSO missing do you escalate (no durable acceptance baseline = cannot accept).

> **Note:** the acceptance baseline is tiered — `qa/{{TASK_ID}}.yaml` → brief-derived →
> escalate. AR-3 never validates against a paraphrase, and never runs with no baseline at all.

---

## Setup phase (run ONCE per acceptance pass)

1. Confirm we are post-`PHASE_GATE`: QA steps recorded as passed in
   `.aid/pipeline/state.json`. If QA has not passed, **stop** — AR-3 does not run
   on un-QA'd code.
2. Read `ORIGINAL_REQUEST` and `STATED_WHY` from the frozen Task Brief
   `{{WORKSPACE}}/.aid/pipeline/{{TASK_ID}}/brief.md` (fallback: `.aid/context.json`
   `original_request`/`stated_why`). If `brief.md` is absent AND those context.json
   fields are empty/missing, **escalate to the user** — there is no durable
   acceptance baseline, and validating against a paraphrase would silently accept
   the wrong thing. Do not proceed on conversation memory alone.
3. Resolve the acceptance source per the tiered rule (item 6): `.aid/qa/{{TASK_ID}}.yaml`
   if present, else brief-derived. Detect whether `phase5-acceptance-validator`
   and `phase4-intent-validator` exist (project→user under `.claude/agents/`). Decide
   full-mode vs fallback-mode and note it.
4. Ensure `.aid/pipeline/autoresearch/{{TASK_ID}}/` exists; if not, create it.
   Read `{{RECORD_FILE}}` (`results.tsv`). If it lacks an acceptance header,
   it is fine to append acceptance rows after any AR-1/AR-2 rows. Initialize the
   in-memory round counter `R = 1`.

---

## Bounded acceptance loop (≤ `{{MAX_ACCEPTANCE_ROUNDS}}` rounds)

For each round `R` from 1 to `{{MAX_ACCEPTANCE_ROUNDS}}`:

### 1. Evaluate the COMPLETE feature
- **Full mode:** run `phase5-acceptance-validator` → `[AV-XXX]` matrix +
  `blockers` + `pass_rate`. Run `phase4-intent-validator` →
  ALIGNED/PARTIALLY_ALIGNED/MISALIGNED per intent. Spawn `reflection-agent` with
  `phase-5-qa-ship.yaml` → read the `why_alignment` dimension score.
- **Fallback mode:** derive matrix, `pass_rate`, `blockers`, and `why_alignment`
  as described under GRACEFUL FALLBACK.

Collect: `pass_rate` (%), `blockers` (list), `why_alignment` (0–10),
and any `MISALIGNED` intents.

### 2. DONE check (all three must hold)
DONE when **all** of:
- `pass_rate >= {{PASS_RATE_TARGET}}`, **AND**
- `blockers` is empty (no NOT_MET required criteria, no MISALIGNED intents), **AND**
- `why_alignment >= {{KPI_TARGET}}`.

If DONE → append a DONE round summary to `{{RECORD_FILE}}`, print the one-line
status, and **exit to Phase 5**. Stop the loop.

### 3. Gap → re-enter DEVELOP (only if NOT done and `R < {{MAX_ACCEPTANCE_ROUNDS}}`)
- Compile the gap as **concrete, scoped work**: every `NOT_MET` / `PARTIAL`
  acceptance criterion and every `MISALIGNED` / `PARTIALLY_ALIGNED` intent,
  each phrased as a specific change to make. Reference the `[AV-XXX]` ids (or the
  `qa/{{TASK_ID}}.yaml` criterion ids in fallback mode) so the work is traceable.
- **Re-enter `DEVELOP` for ONLY those gap items.** Do NOT re-implement anything
  already MET. The pipeline then re-runs the inner sequence on the new changes:
  `CODE_REVIEW → AR_DESIGN → TDD → AR_FUNCTION → VISUAL_QA → TEST_REVIEW →
  PHASE_GATE`. Those inner passes carry their own caps and gates.
- If any gap item touches `{{SAFETY_CRITICAL_FLOWS}}`, ASK the user before
  re-entering DEVELOP for that item.
- Append a "round R: re-enter DEVELOP" summary row to `{{RECORD_FILE}}` listing
  the gap items, current `pass_rate`, and `why_alignment`.
- Increment `R`. After the inner pipeline returns, loop back to step 1 to
  re-evaluate.

### 4. Round cap reached with open blockers → ESCALATE
If `R == {{MAX_ACCEPTANCE_ROUNDS}}` and the DONE check still fails:
- **STOP. Do NOT loop the whole pipeline again.**
- **ESCALATE to the user**: present the remaining `blockers`, the latest
  `pass_rate` vs `{{PASS_RATE_TARGET}}`, the `why_alignment` vs `{{KPI_TARGET}}`,
  the `MISALIGNED` intents, and a short recommendation for each. Let the human
  decide (accept-with-known-gaps, extend rounds, or rescope).
- Append a "round R: ESCALATED" summary row to `{{RECORD_FILE}}`.

---

## Termination guarantee

This is an **outer** loop over the pipeline. Termination is guaranteed by the
**conjunction** of:
- the **round cap** `{{MAX_ACCEPTANCE_ROUNDS}}` here (the outer bound), AND
- each inner pass's own caps (CODE_REVIEW ≤ 2, TDD ≤ 2, AR_DESIGN / AR_FUNCTION
  `max_iterations` + `max_consecutive_reverts`), AND
- the existing pipeline cost brake `cost_limits.max_per_run_usd`.

There is no path where AR-3 loops the pipeline unboundedly. If progress stalls,
it escalates; it never silently continues.

---

## Recording

Append round summaries to `{{RECORD_FILE}}`
(`.aid/pipeline/autoresearch/{{TASK_ID}}/results.tsv`), tab-separated, one row per
round, consistent with the AMS results.tsv shape:

```
ar3-r<R>	<pass_rate>	<why_alignment>	<status>	-	<UTC-iso>
```

Where `<status>` ∈ { `done`, `redevelop`, `escalated` }. The trailing three
columns are **exactly** `status`, `snapshot`, `utc` — the `snapshot` column is
`-` (AR-3 does not snapshot files; it re-enters DEVELOP, which is itself governed
by the inner passes' snapshot/revert mechanics). Do **NOT** put the human
one-line gap summary in the TSV row — that would break the right-anchored
positional parse. Keep the one-line gap summary (gap items / DONE / ESCALATED)
in the chat/summary output ONLY (see "Output expectations to the user" below),
exactly as AR-2 does.

This AR-3 row is an **allowed per-pass shape** of the common `results.tsv` schema
defined authoritatively in `SKILL.md`: AR-3 uses a **string `iter` id**
(`ar3-r<R>`) in the `iter` column and `-` in the `snapshot` column. The renderer/
parser reads the common columns positionally from the ends (`iter` … `status
snapshot utc`) and treats whatever lies between as that pass's dimension scores —
for AR-3 those are exactly `pass_rate` and `why_alignment`, occupying the dimension slots
directly between the `iter` column and the trailing `status snapshot utc`. AR-3 has **no
separate `composite`/`delta` columns** (it is gate-based, not score-based), so per `SKILL.md`'s
rule the parser anchors on `iter` (first) and `status snapshot utc` (last three), never on fixed
`composite`/`delta` positions.

---

## Hard constraints (org + pipeline policy — non-negotiable)

- **NEVER auto-commit. NEVER run destructive git.** This pass is
  validation + bounded re-development only; the **human** commits after review.
- **No new dependencies, no framework migration, no plaintext secrets** in any
  re-development triggered here.
- **Do NOT modify the harness**: not `reflection-agent`, not `phase-5-qa-ship.yaml`,
  not the validator agents, not `qa/{{TASK_ID}}.yaml`, not `.aid/context.json`,
  not `.aid/state.json`. They are read-only.
- **Do NOT re-open certified code quality.** AR-3 only opens work for genuine
  acceptance gaps (NOT_MET / MISALIGNED), routed through DEVELOP.
- **Do NOT delete or weaken acceptance criteria to inflate `pass_rate`.** That is
  gaming the harness. Quality of the delivered feature > a green number.
- **Bounded always.** When `{{MAX_ACCEPTANCE_ROUNDS}}` is hit with open blockers,
  escalate — never loop forever.
- **Hook-safety (state.json freshness):** the `dev-pipeline-gate.sh` Stop hook
  re-blocks whenever the newest source mtime is greater than `state.json`'s mtime,
  and any re-development here ultimately routes through inner passes whose last disk
  write may be a revert/restore `cp` (which sets the source mtime to NOW). THEREFORE,
  on stop AR-3 must FIRST ensure the editable set is restored to the best-kept
  version, THEN write `state.json` **UNCONDITIONALLY as its FINAL action** — after
  the last source mutation of ANY kind (kept edit, revert/restore `cp`, or crash
  restore), and after DONE or ESCALATE — so the Stop hook's freshness check stays
  correct. AR-3 itself takes no file snapshots (it re-enters DEVELOP; the inner passes own the
  restore/rubric checks per `autoresearch/SKILL.md`'s loop spine), but AR-3's OWN `state.json`
  write follows the same spine contract: after writing, verify exit status + re-read/parse +
  mtime ≥ newest source, and on failure HALT loudly with status `state-write-failed` rather than
  relying on the downstream Stop gate's generic re-run message.

---

## Output expectations to the user

Be quiet. After each round, print ONE line to chat:

```
ar3 round <R> | <done|redevelop|escalated> | pass_rate <pp>% (target {{PASS_RATE_TARGET}}%) | why_align <X.X> (target {{KPI_TARGET}}) | <gap summary or "all met">
```

On DONE, additionally print the one-line acceptance verdict. On ESCALATE, print
the remaining blockers as a short bulleted list and hand control to the user. The
TSV (`{{RECORD_FILE}}`) is the source of truth for the round history.
