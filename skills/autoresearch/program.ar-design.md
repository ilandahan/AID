# program.ar-design.md — Autoresearch Pass AR-1 (DESIGN, pre-TDD)

> Karpathy autoresearch loop, specialized for **design/structural quality** of freshly
> developed production source. Instead of editing `train.py` to minimize `val_bpb`, you
> edit one task's source set to maximize a reflection-agent **design quality** score —
> while the public surface stays frozen so the next stage (TDD) has a stable target.
> The agent is the runner. You read this file and follow it. Loop until a stop fires.

---

## MODE

**design** — runs **AFTER** `CODE_REVIEW`, **BEFORE** `TDD`.

**No tests exist yet.** There is no running test suite to score against, so the harness
is reflection-quality ONLY. This is exactly why AR-1 is a separate pass from AR-2: it
must polish structure/clarity *without* moving the public surface, so TDD is not written
against a moving target.

---

## Goal

Iteratively improve the production source changed in task `{{TASK_ID}}` to maximize the
reflection-agent's **Phase-4a Code-Design weighted score**, using
`~/.claude/skills/autoresearch/criteria/phase-4a-code-design.yaml` (user-level bundle default; a project may override at `{{WORKSPACE}}/.claude/skills/autoresearch/criteria/`).

KPIs (each must reach **≥ {{KPI_TARGET}}**):

- **Structural health** — cohesion, function/module size, dead code, duplication, layering.
- **Loudness of failures** — errors surface; no silent swallowing; fail-fast on bad state.
- **Naming clarity** — names reveal intent; no misleading or placeholder identifiers.
- **Docs & traceability** — public surface documented; non-obvious decisions explained;
  changes traceable to the task.

The composite for keep/revert is the reflection-agent's weighted overall (0.0–10.0).

**Stop only when a human interrupts you, or a stop condition below fires.**

---

## Mutable surface (the "train.py")

You may edit ONLY:

- The **production source files changed in this task** — i.e. the set from
  `git diff --name-only` + untracked files introduced by this task, restricted to source
  (no config, no `.aid/`, no generated artifacts). If a definitive changed-set is recorded
  in `{{WORKSPACE}}/.aid/context.json`, use that; otherwise derive it from the diff once at
  setup and treat THAT frozen list as the editable set for the whole pass.
- `{{RECORD_FILE}}` — the experiment log (`results.tsv`).

Snapshots are written ONLY under
`{{WORKSPACE}}/.aid/pipeline/autoresearch/{{TASK_ID}}/snapshots/` via the `cp` commands below.

Do not create, rename, move, or delete any other file.

---

## Fixed harness (the "prepare.py" — DO NOT TOUCH)

Treat as read-only — modifying any of these makes the score meaningless:

- the `reflection-agent` (its prompt/templates) — the scorer. **Resolve project→user:** load `../../agents/reflection-agent.md` from `{{WORKSPACE}}/.claude/…` if present, else `~/.claude/…` (the engine ships user-level).
- `~/.claude/skills/autoresearch/criteria/phase-4a-code-design.yaml` (user-level bundle default; a project may override at `{{WORKSPACE}}/.claude/skills/autoresearch/criteria/`) — the criteria
- the reflection `SKILL.md` scoring methodology
- `{{WORKSPACE}}/.aid/context.json`, `{{WORKSPACE}}/.aid/state.json`, `config.json` — read-only metadata
- any test files (none should exist yet — if any do, they are OUT of the editable set)

---

## HARD CONSTRAINT — the whole reason AR-1 is separate

**NO public-surface changes.** Within the editable set you MUST NOT change any of:

- exported / public **function or method signatures** (name, parameter list, order,
  defaults, return type)
- exported **class / type / interface / enum shapes**
- public **module exports** (what is exported, and under what name)
- **data shapes** crossing a boundary — request/response objects, serialized payloads,
  DB row shapes, public constants/enums consumed elsewhere

Allowed: internal refactors, renaming **local** (non-exported) identifiers, extracting
private helpers, replacing silent fallbacks with loud failures, adding/clarifying docs &
comments, removing dead code, de-duplicating internals — all behind an unchanged surface.

If improving a KPI seems to *require* a signature/shape change, **do not make it**: record
the idea as `skipped (surface-locked)` in `{{RECORD_FILE}}` and pick a different target.
Surface evolution is TDD/AR-2/AR-3 territory, not AR-1.

Other non-negotiables:
- **NEVER auto-commit and NEVER run destructive git** (no `reset --hard`, `clean -f`,
  `checkout -- `, `push`, `rebase`). Validation only; the human commits.
- **No new dependencies**, no framework migration, no plaintext secrets.
- **One focused edit per iteration.** Edit only files in the frozen editable set.
- **Never downgrade a loud failure to silent.** Introduce **zero** new silent-failure paths
  in `{{CRITICALITY_PROFILE}}`-critical paths — no new `catch` that swallows, no
  `|| DEFAULT`, no `?? DEFAULT`, no `.catch` without rethrow.
- **No scope reduction to game the score** — do not delete features, validation, or guards
  just to raise structural numbers.

---

## Setup phase (run ONCE per pass, then never again)

1. Resolve the frozen **editable set** (see Mutable surface). Record the file list and each
   file's line count. If the set is empty, log a no-op baseline row and STOP.
2. Ensure the snapshot dir exists:
   ```bash
   mkdir -p "{{WORKSPACE}}/.aid/pipeline/autoresearch/{{TASK_ID}}/snapshots"
   ```
3. Read `{{RECORD_FILE}}`. If it already has scored rows for this pass, do NOT re-baseline —
   resume from the next iteration number. If empty/header-only, proceed to baseline.
4. **Snapshot the baseline** of the whole editable set:
   ```bash
   TS="$(date -u +%Y%m%dT%H%M%SZ)"
   mkdir -p "{{WORKSPACE}}/.aid/pipeline/autoresearch/{{TASK_ID}}/snapshots/000-baseline-$TS"
   # copy every file in the editable set into that dir, preserving relative paths
   ```
5. **Score the baseline** by spawning the subagent named `reflection-agent`:
   - Tool: `Task`, `subagent_type: general-purpose`, `model: opus`, loading the
     reflection-agent prompt from
     `{{WORKSPACE}}/.claude/agents/reflection-agent.md`.
   - Provide:
     - `ORIGINAL_REQUEST`: verbatim from `{{WORKSPACE}}/.aid/context.json`.
     - `STATED_WHY`: exact WHY from `{{WORKSPACE}}/.aid/context.json`.
     - `PHASE_NUMBER`: 4, `PHASE_NAME`: "Code Design (AR-1)".
     - `PHASE_CRITERIA`: full contents of `phase-4a-code-design.yaml`.
     - `OUTPUT_TO_EVALUATE`: full current contents of every file in the editable set.
     - `FILES_TO_VERIFY`: the editable set paths.
6. Parse the weighted overall (float 0.0–10.0) → `best_score`. Also capture the per-KPI
   sub-scores → `best_kpis`.
7. Append the header (if the file is empty) then the baseline row (tab-separated) to
   `{{RECORD_FILE}}`. AR-1 uses the SKILL.md common schema with its four AR-1 dimension
   columns (`structural_health loudness_of_failures naming_clarity docs_traceability`)
   between `delta` and `status` — use these exact criterion ids as the column names:
   ```
   iter	composite	delta	structural_health	loudness_of_failures	naming_clarity	docs_traceability	status	snapshot	utc
   0	<best_score>	0.00	<sh>	<lof>	<nc>	<dt>	baseline	000-baseline-<TS>	<UTC-iso>
   ```
   where `<sh>/<lof>/<nc>/<dt>` are the four baseline per-KPI sub-scores from `best_kpis`.

---

## Experimentation loop (Waze loop shape)

Counter `N` = next iteration number from `{{RECORD_FILE}}`. Each iteration:

### 1. EVALUATE
Re-read the current editable set and the most recent reflection breakdown. Note `best_score`
(max `score` where `status='kept'`, else baseline) and `best_kpis`. Skim recent
`reverted` / `skipped` ideas — **do not repeat them**.

### 2. SCORE — one line of `file:line` evidence per KPI
For each of the 4 KPIs, write ONE concrete evidence line, e.g.:
```
structural_health   src/auth/token.ts:88  120-line function mixes parse + validate + persist
loudness_of_failures src/auth/token.ts:142 `catch {}` swallows refresh error → silent expiry
naming_clarity      src/auth/util.ts:12   `function doIt(x)` — intent unclear
docs_traceability   src/auth/token.ts:1   exported `rotate()` has no doc; no task ref
```

### 3. RANK — top 5
List the top 5 candidate edits by expected KPI lift × low risk. Each must respect the
surface-lock. Drop any that need a signature/shape change (log them `skipped`).

### 4. PROPOSE
Pick the single highest-ranked candidate. State: target file:line, the KPI it lifts, the
exact change, and an explicit assertion that it does **not** touch the public surface and
introduces **no** new silent-failure path.
- If the proposed edit touches a `{{SAFETY_CRITICAL_FLOWS}}` flow → **ASK the user before
  editing.** Apply pure structural/doc edits (rename local, extract private helper, add
  comment/doc, remove dead code) directly without asking.

### 5. SNAPSHOT
Before editing, snapshot the current editable set (the rollback target):
```bash
SLUG="<short-kebab-of-idea>"; TS="$(date -u +%Y%m%dT%H%M%SZ)"
SNAP="{{WORKSPACE}}/.aid/pipeline/autoresearch/{{TASK_ID}}/snapshots/$(printf '%03d' $N)-pre-${SLUG}-${TS}"
mkdir -p "$SNAP"   # copy every editable file into $SNAP preserving relative paths
```

### 6. IMPLEMENT — one edit
Apply exactly ONE focused edit, only within the editable set. No "while I'm here" extras.

### 7. RE-SCORE
Spawn the reflection-agent again (identical setup, `OUTPUT_TO_EVALUATE` = the edited set).
Parse the weighted overall → `official_score`, and per-KPI → `official_kpis`.

### 8. keep / revert
- **Keep** iff `official_score` **strictly improves** (`official_score > best_score`) AND
  no KPI regressed below its baseline AND the surface-lock + no-new-silent-failure
  invariants still hold:
  - `status = kept`; `best_score = official_score`; `best_kpis = official_kpis`; leave edit on disk.
- **Else revert** by restoring the editable set from the step-5 snapshot:
  - `status = reverted`; `best_score` / `best_kpis` unchanged.

### 9. LOG
Append to `{{RECORD_FILE}}` (tab-separated), matching the SKILL.md common schema with the
four AR-1 dimension columns between `delta` and `status`:
```
iter	composite	delta	structural_health	loudness_of_failures	naming_clarity	docs_traceability	status	snapshot	utc
<N>	<official_score>	<official_score - prior best_score>	<sh>	<lof>	<nc>	<dt>	<status>	<snapshot dir>	<UTC-iso>
```
where `<sh>/<lof>/<nc>/<dt>` are this iteration's per-KPI sub-scores from `official_kpis`.
The one-line idea is NOT a TSV column — keep it in the human chat line only.

### 10. Increment `N`, loop.

---

## STOP conditions

Stop when ANY fires:

- A human interrupts or sends a new prompt.
- **All 4 KPIs ≥ {{KPI_TARGET}}** (design target met).
- **{{AR1_MAX_REVERTS}} consecutive `reverted` iterations** (plateau).
- **{{AR1_MAX_ITERS}} total iterations** reached.
- Cost brake: `config.json` `cost_limits.max_per_run_usd` reached.

> Config bindings: `{{AR1_MAX_ITERS}}` = `config.autoresearch.ar_design.max_iterations`;
> `{{AR1_MAX_REVERTS}}` = `config.autoresearch.ar_design.max_consecutive_reverts`.
> A pass may never be bounded by the cost brake alone.

On stop, in this exact order:
1. **FIRST restore** the editable set to the best-kept version (`cp` from the snapshot of
   the kept state if the last on-disk write was a revert/restore or a crash). This is itself
   a source mutation that bumps the source mtime to NOW.
2. **THEN write `{{WORKSPACE}}/.aid/pipeline/state.json` UNCONDITIONALLY as the FINAL
   action** — after the last source mutation of ANY kind (kept edit, revert/restore `cp`, or
   crash restore). Record final per-KPI scores into `step_history` and update the step's
   completion. Because a rollback `cp` sets the source mtime to NOW and the plateau stop can
   fire right after a run of reverts, state.json MUST be the last thing written so its mtime
   ≥ newest source mtime; otherwise the dev-pipeline-gate Stop hook re-blocks. Then hand off
   to TDD.
3. **Safety contract — follow `autoresearch/SKILL.md`'s loop spine; this file does NOT restate
   it in full.** Restore with `cp -p` and check the exit status of EVERY restore (`test -r` the
   target before any baseline fallback; on any failure HALT with status `restore-failed`). After
   writing `state.json`, verify exit status + re-read/parse + mtime ≥ newest source (on failure
   HALT with status `state-write-failed`). And re-verify the rubric fingerprint before each
   official score (HALT `rubric-tampered` on mismatch). The ordering note above is necessary but
   NOT the whole contract — the SKILL.md loop spine is authoritative for these checks.

Summarize: starting score, final `best_score`, final per-KPI, `kept` vs `reverted` counts,
top 3 kept changes by delta, and confirmation that the public surface is unchanged.

---

## Output expectations to the user

Be quiet. After each iteration print ONE line:
```
AR-1 iter <N> | <kept|reverted|skipped> | <official_score> (Δ <delta>) | KPIs S<..> L<..> N<..> D<..> | <idea>
```
Do not narrate reasoning or dump the full reflection breakdown (the user can ask). The TSV
is the source of truth.
