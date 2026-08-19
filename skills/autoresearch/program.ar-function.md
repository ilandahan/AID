# program.ar-function.md — Autoresearch AR-2 (FUNCTION pass, post-TDD)

> Adapted from Andrej Karpathy's autoresearch pattern: instead of editing `train.py`
> to minimize `val_bpb`, you edit **production source** to maximize a **composite
> functional+quality KPI**. The harness here is REAL: a running test suite + coverage,
> AND an AID reflection-agent scoring against `phase-4b-code-function.yaml`. You are the
> runner. You read this file and follow it. Loop until a STOP condition fires.
>
> This is **AR-2 / FUNCTION**. It runs **after TDD** (tests now exist and are green) and
> **before VISUAL_QA / TEST_REVIEW (QA)**. Its sibling passes:
> - AR-1 / DESIGN (`program.ar-design.md`) — pre-TDD, judge-only, NO interface changes.
> - AR-3 / ACCEPTANCE (`program.ar-acceptance.md`) — post-QA, feature vs original request+WHY.

---

## MODE

**MODE: function (post-TDD, pre-QA).**

The TDD stage has produced a passing test suite. Those tests are now part of the
**fixed evaluation harness** — they define "functionally correct." Your job is to make
the production source *better* (correctness of defaults, security, loud failures,
structural health) **without breaking a single test and without lowering coverage**, then
hand a hardened implementation to QA.

Placeholders below are filled at runtime from `.aid/context.json` + `.aid/pipeline/config.json`:
`{{WORKSPACE}}`, `{{TASK_ID}}`, `{{CRITICALITY_PROFILE}}`, `{{KPI_TARGET}}`,
`{{TEST_COMMAND}}`, `{{MIN_COVERAGE}}`, `{{SAFETY_CRITICAL_FLOWS}}`, `{{RECORD_FILE}}`,
`{{AR2_MAX_ITERS}}` (= `config.autoresearch.ar_function.max_iterations`),
`{{AR2_MAX_REVERTS}}` (= `config.autoresearch.ar_function.max_consecutive_reverts`),
`{{AR2_INTERNAL_ROUNDS}}` (= `config.autoresearch.ar_function.internal_rounds`, default 2 —
a bounded cap on internal revision attempts per iteration).

---

## Mutable surface (the "train.py")

You may edit ONLY:

- **Production source** changed by this task — the files in `git diff` + untracked files
  introduced for `{{TASK_ID}}`, excluding test files. This is the same surface AR-1
  operated on, now post-TDD.
- The experiment log at `{{RECORD_FILE}}`
  (`.aid/pipeline/autoresearch/{{TASK_ID}}/results.tsv`).

You may create snapshot files ONLY under
`.aid/pipeline/autoresearch/{{TASK_ID}}/snapshots/` and ONLY via the `cp` commands below.

---

## Fixed harness (the "prepare.py" — DO NOT TOUCH)

Treat ALL of the following as **read-only**. If you modify any of them, the score becomes
meaningless and the pass is invalid:

- **The test suite. TESTS ARE FROZEN.** They are the functional harness produced by TDD.
  **Do NOT edit, add, delete, skip, `.only`, weaken, or re-baseline any test** to make the
  bar easier. Changing a test is changing the ruler. If a test is genuinely wrong, that is
  a TDD-stage concern — STOP and escalate to the user; do not "fix" it here.
- `{{TEST_COMMAND}}` + coverage tooling — the deterministic scorer.
- `reflection-agent` (`subagent_type: general-purpose`, `model: opus`) — the quality scorer. **Resolve project→user:** load `../../agents/reflection-agent.md` from `{{WORKSPACE}}/.claude/…` if present, else `~/.claude/…` (the engine ships user-level).
- `~/.claude/skills/autoresearch/criteria/phase-4b-code-function.yaml` (user-level bundle default; project may override at `{{WORKSPACE}}/.claude/skills/autoresearch/criteria/`) — the criteria.
- `.aid/state.json`, `.aid/context.json`, `.aid/pipeline/config.json` — read-only metadata.
- `.mcp.json` and any AID/skill/agent prompt or command file.

---

## Composite KPI (tiered — the Superpharm pattern)

The single comparable score for keep/revert is a **composite**:

```
composite = quality * (all Tier-1 gates pass ? 1 : 0)
```

### Tier-1 — deterministic HARD gates (a multiplier, not an average)

All three must hold or `composite = 0` (the edit is rejected regardless of quality):

1. **Test pass rate = 100%.** Run `{{TEST_COMMAND}}`. Every test passes. **A test going RED
   triggers an immediate, automatic revert** — quality is not even consulted.
2. **Coverage ≥ `{{MIN_COVERAGE}}`%.** Below the threshold forces `composite = 0`, which
   blocks advancing to QA. (Coverage is read from the same `{{TEST_COMMAND}}` run.)
   **Absent / unparseable coverage is itself a Tier-1 FAILURE.** If the test run COMPLETES
   (tests exit 0 and pass) but emits NO parseable coverage value, treat coverage as a gate
   FAILURE → `composite = 0`; **NEVER silently default to 0% and NEVER advance.** Distinguish
   a *measured* `0%` (a real, parsed value below threshold → fail) from *absent/unparseable*
   coverage (no value extracted → also fail, but logged with a loud
   `coverage tooling missing/unparseable` note rather than a numeric `0`). Both fail the gate;
   the cause differs and must be recorded distinctly.
3. **ZERO new silent-failure paths vs. baseline.** Diff the current source against the
   **iteration's pre-edit snapshot** for newly introduced:
   - a new `catch` block that swallows / does not rethrow or surface the error,
   - a new `|| DEFAULT` fallback,
   - a new `?? DEFAULT` fallback,
   - a new `.catch(...)` without a rethrow / propagation.
   For each NEW such site, the **reflection-agent must classify it** as one of
   `loud` (error surfaced/propagated/logged-and-rethrown) /
   `silent` (error swallowed, masked, or a default substituted with no signal) /
   `justified` (documented, intentional, with a stated reason the judge accepts).
   **Any judge-confirmed `silent` site fails Tier-1.** `loud` and `justified` pass.

### Tier-2 — quality (0–10)

The **weighted reflection-agent score** over `phase-4b-code-function.yaml`. Dimensions
(see the YAML for weights/checks):

- **Functional correctness**
- **Correctness of defaults**
- **Security**
- **Loudness of failures**
- **Structural carry-overs** (the structural-health / naming concerns carried over from AR-1)

### Targets

- KPIs target **≥ `{{KPI_TARGET}}`**.
- The coverage gate forces `composite → 0` if coverage is below `{{MIN_COVERAGE}}`% **or if
  no coverage value can be parsed at all** (absent/unparseable coverage = Tier-1 fail, never
  a silent 0% default), which **blocks the pipeline from advancing to QA**. Functional
  correctness (100% green) and zero-new-silent-failures are likewise hard gates.

---

## Setup phase (run ONCE per session, then never again)

1. Read `.aid/context.json` and `.aid/pipeline/config.json`; confirm `{{TASK_ID}}`,
   `{{TEST_COMMAND}}`, `{{MIN_COVERAGE}}`, `{{KPI_TARGET}}`, `{{CRITICALITY_PROFILE}}`,
   and `{{SAFETY_CRITICAL_FLOWS}}`.
2. Compute the **mutable set**: production source touched by `{{TASK_ID}}`
   (`git diff --name-only` + untracked), minus test files. Record this list; it does not
   change mid-session.
3. Ensure `.aid/pipeline/autoresearch/{{TASK_ID}}/snapshots/` exists; if not, `mkdir -p` it.
4. Read `{{RECORD_FILE}}`. If it has only the header (or is missing), proceed to baseline.
   If it already has AR-2 rows, **resume** — do NOT re-baseline.
5. **Snapshot the baseline** of every mutable file:
   ```bash
   TS="$(date -u +%Y%m%dT%H%M%SZ)"
   DST=".aid/pipeline/autoresearch/{{TASK_ID}}/snapshots/000-baseline-${TS}"
   mkdir -p "$DST"
   # copy each file in the mutable set into $DST preserving relative paths
   ```
6. **Score the baseline:**
   a. Run `{{TEST_COMMAND}}` (+ coverage). Record pass rate (must be 100% entering AR-2 —
      TDD just left it green) and coverage %. These define the Tier-1 baseline.
   b. Record the baseline set of silent-failure sites (so later diffs only flag NEW ones).
   c. Spawn the reflection-agent for the Tier-2 quality score:
      - Tool: `Task`, `subagent_type: general-purpose`, `model: opus`. Spawn the subagent
        named `reflection-agent`.
      - Load `{{WORKSPACE}}/.claude/agents/reflection-agent.md`
        and fill its variable contract:
        - `ORIGINAL_REQUEST` — verbatim from `.aid/context.json`.
        - `STATED_WHY` — verbatim from `.aid/context.json`.
        - `PHASE_NUMBER`: 4, `PHASE_NAME`: "Code (function)".
        - `PHASE_CRITERIA` — full contents of
          `~/.claude/skills/autoresearch/criteria/phase-4b-code-function.yaml` (user-level bundle default; project may override at `{{WORKSPACE}}/.claude/skills/autoresearch/criteria/`).
        - `OUTPUT_TO_EVALUATE` — full current contents of the mutable production files.
        - `FILES_TO_VERIFY` — the mutable set + any files they import/reference.
   d. Compute baseline `composite = quality * (all Tier-1 gates pass ? 1 : 0)`.
      Call this `best_composite`.
7. Append the baseline row (row 0) to `{{RECORD_FILE}}` (tab-separated). The header AR-2
   prints (and resumes against) is exactly:
   ```
   iter	composite	delta	quality	pass_rate	coverage	status	snapshot	utc
   ```
   Baseline row:
   ```
   0	<best_composite>	0.00	<quality>	<pass_rate>	<coverage>	baseline	000-baseline-<TS>	<UTC-iso>
   ```
   This follows the SKILL.md common schema — common prefix `iter  composite  delta`, then the
   AR-2 dimension columns `quality  pass_rate  coverage`, then the common suffix
   `status  snapshot  utc`. (No `description` column; the one-line idea lives only in the
   chat output.)

---

## Experimentation loop (run until a STOP condition)

Track an in-memory counter `N` from the next iteration number in `{{RECORD_FILE}}`.
For each iteration:

### 1. EVALUATE / read state
- Re-read the current mutable files.
- Read `{{RECORD_FILE}}`: note `best_composite` (max `composite` where `status='kept'`,
  fallback baseline). Skim recent `reverted` ideas — **do not repeat them**.

### 2. RANK / pick ONE improvement target
A small, single-purpose edit that raises a Tier-2 dimension **without risking a test or a
new silent path**. Cite **file:line evidence** for the target. Examples (not prescriptive):
- "Replace the `?? 0` fallback at `pricing.ts:88` with an explicit validated branch that
  throws on missing input (Correctness of defaults / Loudness)."
- "Tighten the input check at `handler.ts:42` so a malformed payload is rejected loudly
  instead of coerced (Security / Loudness)."
- "Rethrow with context in the `catch` at `repo.ts:130` instead of returning `null`
  (Loudness of failures)."

**One idea per iteration.** No mass rewrites. No "while I'm here" extras. **No test edits.**

### 3. PROPOSE / multi-attempt revision (≤ `{{AR2_INTERNAL_ROUNDS}}` internal rounds)
For attempt in 1..`{{AR2_INTERNAL_ROUNDS}}`:
  a. Apply the focused edit to the production source only.
  b. Run `{{TEST_COMMAND}}` quickly. If any test is RED → this attempt is invalid; revert
     the attempt in memory and refine or try a different angle.
  c. If green, do a fast self-check of the silent-failure diff + a self-estimate of quality.
     If it looks like it clears Tier-1 and improves Tier-2, break and proceed to scoring.
  d. If `{{AR2_INTERNAL_ROUNDS}}` is exhausted without a promising green attempt, proceed
     anyway with the best green attempt — the official scorer decides.

### 4. SNAPSHOT the pre-change state
**Before** official scoring, snapshot the PRE-edit on-disk version of every mutable file
(the rollback target):
```bash
SLUG="<short-kebab-case-of-your-idea>"
TS="$(date -u +%Y%m%dT%H%M%SZ)"
DST=".aid/pipeline/autoresearch/{{TASK_ID}}/snapshots/$(printf '%03d' $N)-pre-${SLUG}-${TS}"
mkdir -p "$DST"
# copy each mutable file's PRE-edit version into $DST
```
Practically: copy the mutable files at the very start of step 3 (before applying the edit).

### 5. IMPLEMENT / RE-SCORE (official)
Run the full fixed harness on the now-edited source:
  a. **Tier-1 gates:**
     - Run `{{TEST_COMMAND}}` (+ coverage). Pass rate must be **100%**; coverage must be
       **≥ `{{MIN_COVERAGE}}`%**. **If any test is RED → automatic revert (skip to step 7
       with `status=reverted-redtest`), quality not consulted.** **If tests COMPLETE/pass
       but no coverage value is parseable → Tier-1 FAIL: force `composite = 0`, do NOT default
       to 0% and do NOT advance; log coverage as `n/a` with a loud
       `coverage tooling missing/unparseable` note (distinct from a measured `0%`, which also
       fails but as a real parsed value).**
     - Diff new silent-failure sites vs. this iteration's pre-edit snapshot; have the
       reflection-agent classify each NEW site `loud`/`silent`/`justified`. Any `silent`
       fails Tier-1.
  b. **Tier-2 quality:** spawn the reflection-agent (same variable contract as baseline,
     with the edited source as `OUTPUT_TO_EVALUATE`) → weighted quality score 0–10.
  c. `composite = quality * (all Tier-1 gates pass ? 1 : 0)`.

### 6. LOG the result
Append to `{{RECORD_FILE}}` (same column order as the header:
`iter  composite  delta  quality  pass_rate  coverage  status  snapshot  utc`):
```
<N>	<composite>	<composite - best_composite>	<quality>	<pass_rate>	<coverage>	<status>	<snapshot dir>	<UTC-iso>
```
The one-line idea + `file:line` evidence goes to the chat line (step "Output expectations"),
not into a TSV column.

### 7. keep / revert
- If `composite > best_composite` (STRICTLY better):
  - `status = kept`; update `best_composite = composite`; leave the edited source in place
    (it becomes the new baseline for the silent-failure diff and quality).
- Else (including `composite = 0` from any failed Tier-1 gate, and any red-test case):
  - `status = reverted` (or `reverted-redtest`); restore every mutable file from this
    iteration's step-4 snapshot; `best_composite` unchanged.
  - **A test going RED ALWAYS forces a revert**, irrespective of quality.
- **Plateau counter:** `reverted`, `reverted-redtest`, and `crash` ALL increment the
  consecutive_reverts counter toward `{{AR2_MAX_REVERTS}}`. A `kept` iteration resets it to 0.

### 8. Increment `N`, loop.

---

## STOP conditions

Stop the loop when ANY of these fires:

- **All KPIs ≥ `{{KPI_TARGET}}`** (quality dimensions and the composite at/above target,
  with all Tier-1 gates green) — the implementation is hardened; hand to QA.
- **`{{AR2_MAX_REVERTS}}` consecutive non-kept iterations** (plateau) — `reverted`,
  `reverted-redtest`, and `crash` all count toward this counter.
- **`{{AR2_MAX_ITERS}}` total iterations** reached.
- **Cost brake:** `cost_limits.max_per_run_usd` (from `config.json`) reached.
- Human sends an interrupt or any new prompt.

**HOOK-SAFETY — order matters.** The `dev-pipeline-gate.sh` Stop hook re-blocks when
`newest_source_mtime > state.json` mtime. A rollback via `cp <snapshot> <file>` sets the
source mtime to NOW, and the plateau stop typically fires right after a run of REVERTS — so
the last disk write is often a revert, not a kept edit. THEREFORE, on stop, in this order:

1. **FIRST**, restore the editable (mutable) set to the **best-kept** version (the source
   that produced `best_composite`). This is the last source mutation of the pass.
2. **THEN write `state.json`/`step_history` UNCONDITIONALLY as the FINAL action** — after
   the last source mutation of ANY kind (a kept edit, a revert/restore `cp`, or a crash
   restore). Writing it unconditionally last guarantees the freshness check sees
   `newest_source_mtime ≤ state_mtime` and does NOT re-block.
3. **Safety contract — follow `autoresearch/SKILL.md`'s loop spine; this file does NOT restate
   it in full.** Restore with `cp -p` and check the exit status of EVERY restore (`test -r` the
   target before any baseline fallback; on any failure HALT with status `restore-failed`). After
   writing `state.json`, verify exit status + re-read/parse + mtime ≥ newest source (on failure
   HALT with status `state-write-failed`). And re-verify the rubric fingerprint before each
   official score (HALT `rubric-tampered` on mismatch). The ordering note above is necessary but
   NOT the whole contract — the SKILL.md loop spine is authoritative for these checks.

Then summarize: baseline composite, final `best_composite`, final pass rate + coverage,
count of `kept` vs `reverted`, and the top 3 most-impactful kept edits by delta (with
file:line).

---

## Constraints (non-negotiable — org + plan policy)

- **TESTS ARE FROZEN.** No edits, additions, deletions, skips, `.only`, or re-baselining of
  any test. The test suite is the harness.
- **No new dependencies. No framework migration. No plaintext secrets.**
- **No scope reduction to game the score** — do not delete behavior, validation, or error
  handling to lift a quality dimension. Quality > brevity.
- **ASK before any edit that touches `{{SAFETY_CRITICAL_FLOWS}}`.** Pause and get explicit
  user confirmation first.
- **One idea per iteration.** Edit only files in the mutable set.
- **Never auto-commit. Never run destructive git.** Validation only — the human commits
  after review. Snapshots are `cp` into the autoresearch snapshots dir; nothing else writes
  to git.
- Edit only the mutable production source and `{{RECORD_FILE}}`; snapshots only under
  `.aid/pipeline/autoresearch/{{TASK_ID}}/snapshots/`.

---

## Output expectations to the user

Be quiet. After each iteration print ONE line to chat:
```
ar-2 iter <N> | <kept|reverted> | composite <composite> (Δ <delta>) | tests <pass_rate> cov <coverage>% | <description>
```
Do not narrate reasoning or dump the reflection-agent's full breakdown (it's in the agent
response; the user can ask). The TSV at `{{RECORD_FILE}}` is the source of truth.
