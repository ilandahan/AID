#!/usr/bin/env node
// gate.mjs — the scored-step gate, in CODE.
//
// WHY THIS EXISTS: the gate used to be prose in SKILL.md ("compare scores.overall against
// config.thresholds.code_review_pass; after N cycles still below threshold → ESCALATE"), executed by
// an agent. It was not followed. Two reviews in this workspace's own history were logged PASS at
// 7.9 and 7.6 against a threshold of 9.5, and nothing escalated — so the quality gate silently
// wasn't one, and the number in config.json was decorative.
//
// Now the decision is a pure function with exit codes, and an ESCALATE writes an escalation file
// that the Stop hook blocks on. An agent can no longer label a sub-threshold score "PASS", and a
// turn cannot end quietly while an escalation is open.
//
// Usage:
//   node gate.mjs --step CODE_REVIEW --scores '{"overall":9.6,...}' [--root <repo>] [--dry-run]
//   node gate.mjs --check-escalation [--root <repo>]     # exit 2 if one is open
//   node gate.mjs --resolve "<how it was resolved>" [--root <repo>]
//   node gate.mjs --should-spawn-dual --step CODE_REVIEW [--round N] [--prev-score X] [--root <repo>]
//
// Exit codes (the contract the orchestrator and the hook rely on):
//   0 = PASS      advance to the next step
//   1 = FIX       below threshold, iterations remain → run the fix step and re-review
//   2 = ESCALATE  below threshold with iterations exhausted → STOP and ask the human
//   3 = usage/data error (never silently treated as a pass)
//
// --should-spawn-dual has its OWN exit contract (0 = spawn two reviewers, 1 = spawn one, 3 = usage
// error) — never conflate with the PASS/FIX/ESCALATE/ERROR contract above.
import { readFileSync, writeFileSync, existsSync, mkdirSync, appendFileSync } from "node:fs";
import { join, dirname } from "node:path";

export const STEP_CONFIG = {
  CODE_REVIEW: { threshold: "code_review_pass", counter: "code_review" },
  TEST_REVIEW: { threshold: "test_review_pass", counter: "test_review" },
  VISUAL_QA: { threshold: "visual_qa_pass", counter: "visual_qa" },
  PHASE_GATE: { threshold: null, counter: "phase_gate_reexamine" },
};

/**
 * Is there a CRITICAL security finding anywhere in this review?
 *
 * DERIVED, NOT TRUSTED (2026-09-04). decide() used to read `scores.critical_security` alone, and the
 * reviewer agents' JSON contract never emits that key: code-review-agent.md returns
 * {security, code_quality, documentation, architecture, overall} and nothing more. So the
 * auto_fail_on_critical_security branch had NEVER fired in the life of this file, while reading in
 * config.json as though it were an active control. One real transcript hand-added
 * `"critical_security": false`, which is worse than the key being absent because it makes the flag
 * look wired.
 *
 * So compute it from what reviewers DO report. An explicit boolean is still honoured for callers that
 * set it deliberately; otherwise any issue marked CRITICAL in a security context counts. Shapes are
 * accepted liberally because two agent definitions and several hand-written transcripts disagree
 * about nesting, and a guard that only understands one of them is the same silent no-op again.
 */
export function hasCriticalSecurity(scores) {
  if (typeof scores?.critical_security === "boolean") return scores.critical_security;

  const isCritical = (sev) => String(sev ?? "").trim().toUpperCase() === "CRITICAL";
  const inSecurity = (obj, inherited) => {
    const cat = String(obj?.category ?? obj?.area ?? inherited ?? "").toLowerCase();
    return cat.includes("security");
  };

  // Flat list: [{severity, category}, ...] under any of the names in use.
  for (const key of ["issues", "findings", "critical", "criticals"]) {
    const list = scores?.[key];
    if (!Array.isArray(list)) continue;
    for (const f of list) {
      // A bare string inside a `critical` array is already a critical finding by position.
      if (typeof f === "string") {
        if (key === "critical" || key === "criticals") {
          if (f.toLowerCase().includes("security")) return true;
        }
        continue;
      }
      if (isCritical(f?.severity) && inSecurity(f)) return true;
    }
  }

  // Nested: categories.security.issues[] — the shape code-review-agent.md's response format uses.
  const sec = scores?.categories?.security;
  for (const key of ["issues", "findings"]) {
    const list = sec?.[key];
    if (!Array.isArray(list)) continue;
    for (const f of list) {
      if (typeof f === "string") continue;
      if (isCritical(f?.severity)) return true;
    }
  }
  return false;
}

/**
 * The whole gate, as a pure function. No I/O, so a test can cover every branch.
 *
 * `iterationsUsed` counts review→fix cycles already spent on THIS step.
 * A step at or past its cap that still misses the threshold escalates — it never advances, which is
 * the exact bug this replaces.
 */
export function decide({ step, scores, config, iterationsUsed = 0 }) {
  const spec = STEP_CONFIG[step];
  if (!spec) return { result: "ERROR", exit: 3, why: `unknown scored step "${step}"` };

  const cap = config?.max_iterations?.[spec.counter];
  if (!Number.isFinite(cap)) {
    return { result: "ERROR", exit: 3, why: `config.max_iterations.${spec.counter} is missing` };
  }

  // PHASE_GATE is pass/fail, not scored: it carries a boolean rather than a number.
  //
  // Three accepted spellings, because NOTHING in this skill emits `passed`. The QA validator contract is
  // `verdict: "PASS"` (SKILL.md) or `can_proceed: true` (SKILL.extended.md), so reading `passed` alone
  // meant a diligent `--step PHASE_GATE` call turned a PASSING phase gate into FIX and sent the work
  // back to DEVELOP — the gate inverting the decision it exists to protect. It went unnoticed because
  // the SKILL never told anyone to run the gate for this step, so the branch was only reachable by an
  // agent that invented the call. Accept what the producers actually write.
  if (spec.threshold === null) {
    const passed = scores?.passed === true || scores?.verdict === "PASS" || scores?.can_proceed === true;
    if (passed) return { result: "PASS", exit: 0, why: `${step} passed`, cap, iterationsUsed };
    if (iterationsUsed >= cap) {
      return { result: "ESCALATE", exit: 2, cap, iterationsUsed,
        why: `${step} failed and all ${cap} re-examine round(s) are spent` };
    }
    return { result: "FIX", exit: 1, cap, iterationsUsed,
      why: `${step} failed; ${cap - iterationsUsed} re-examine round(s) left` };
  }

  const threshold = config?.thresholds?.[spec.threshold];
  if (!Number.isFinite(threshold)) {
    return { result: "ERROR", exit: 3, why: `config.thresholds.${spec.threshold} is missing` };
  }
  // typeof check BEFORE Number(): Number(null) is 0, which is finite, so a null score silently
  // became a 0 and reported FIX instead of ERROR. A review that produced no score has not scored
  // badly — it has not run, and burning a fix cycle on a phantom 0 hides that.
  const overall = scores?.overall;
  if (typeof overall !== "number" || !Number.isFinite(overall)) {
    return { result: "ERROR", exit: 3, why: `scores.overall must be a number (got ${JSON.stringify(overall)})` };
  }

  // Critical-security auto-fail outranks the composite: a 9.6 average cannot buy a critical finding.
  if (config?.thresholds?.auto_fail_on_critical_security && hasCriticalSecurity(scores)) {
    return { result: "ESCALATE", exit: 2, cap, iterationsUsed, overall, threshold,
      why: `critical security finding — auto_fail_on_critical_security is set, so this escalates regardless of the ${overall} composite` };
  }

  if (overall >= threshold) {
    return { result: "PASS", exit: 0, cap, iterationsUsed, overall, threshold,
      why: `${overall} >= ${threshold}` };
  }
  if (iterationsUsed >= cap) {
    return { result: "ESCALATE", exit: 2, cap, iterationsUsed, overall, threshold,
      why: `${overall} < ${threshold} after ${iterationsUsed} of ${cap} fix cycle(s) — iterations exhausted, this is NOT a pass` };
  }
  return { result: "FIX", exit: 1, cap, iterationsUsed, overall, threshold,
    why: `${overall} < ${threshold}; ${cap - iterationsUsed} fix cycle(s) left` };
}

/**
 * Append one Loop 2 event to the machine-level loop log.
 *
 * ONE home-level file on purpose, never <repo>/.aid/pipeline/events.jsonl: that directory's EXISTENCE
 * is the Stop gate's branch selector, so writing there would create it in every repo and silently
 * reroute 216 of 267 blocks onto the AID-freshness branch. The monitor must not rewire the loop it
 * monitors.
 *
 * Never fatal, and never on stdout: stdout is the gate's exit-code contract with the orchestrator.
 */
export function logLoopEvent(payload, root = process.cwd()) {
  try {
    const home = process.env.USERPROFILE || process.env.HOME;
    if (!home) return false;
    const dir = join(home, ".claude");
    mkdirSync(dir, { recursive: true });
    const line = JSON.stringify({ ts: new Date().toISOString(), project: root, ...payload });
    appendFileSync(join(dir, "loop-events.jsonl"), `${line}\n`);
    return true;
  } catch {
    return false; // instrumentation must never become a new failure mode for the gate
  }
}

/**
 * Record a gate decision in state.json so the round count is owned by the gate, not the agent.
 *
 * WHY: the SKILL.md prose told the agent to "increment the code_review counter on FIX". In demo/saas
 * the counter stayed at 1 across two FIX verdicts, so gate.mjs kept reporting "4 fix cycle(s) left"
 * and ESCALATE-by-exhaustion could never fire; step_history had zero entries for the task. A cap the
 * agent must count toward is decorative. Now the gate increments on FIX and appends a step_history
 * row for every non-ERROR decision. Never fatal: a bookkeeping failure must not change the exit code.
 */
export function recordDecision(root, { step, decision, scores }) {
  try {
    const statePath = join(root, ".aid/pipeline/state.json");
    const state = existsSync(statePath) ? JSON.parse(readFileSync(statePath, "utf8")) : {};
    const counter = STEP_CONFIG[step]?.counter;
    state.iterations ??= {};
    if (decision.result === "FIX" && counter) {
      state.iterations[counter] = Number(state.iterations[counter] ?? 0) + 1;
    }
    state.step_history ??= [];
    state.step_history.push({
      step,
      // WHICH TASK PRODUCED THIS (2026-09-06). step_history is one accumulating array per project and
      // carried no per-entry identity, so the dashboard loader could only attribute the WHOLE array to
      // whatever task_id state.json named at ingest time. Measured consequence: demo/saas's 36 entries
      // were rewritten under each new task in turn, leaving 259 surplus rows — 34% of pipeline_steps —
      // with four task_ids holding the identical series at identical timestamps. Same expression main()
      // already passes to logLoopEvent, deliberately, so there is one source of identity and not two.
      task_id: state.current_task_id ?? state.task_id ?? null,
      result: decision.result,
      scores: scores ?? {},
      timestamp: new Date().toISOString(),
      // ONE MEANING, ALL RESULTS: the 1-based number of the review this row records. iterationsUsed
      // rounds were spent BEFORE it, so this one is the next.
      //
      // It used to be the post-increment counter on FIX and the pre-increment iterationsUsed on
      // everything else, which is two different numbers under one name. Measured in breather's live
      // state.json: a CODE_REVIEW PASS carried iteration 1 and so did the FIRST CODE_REVIEW FIX. So
      // `iteration = 1` never meant "round 1", and a round-1 PASS — the runs that went WELL — could not
      // be selected at all. On FIX rows the value here is byte-identical to the old rule
      // (iterationsUsed + 1 === state.iterations[counter] after the increment above), so no row already
      // on disk changes meaning; only PASS and ESCALATE move, and they move to the truth.
      iteration: (decision.iterationsUsed ?? 0) + 1,
      cap: decision.cap ?? null,
      threshold: decision.threshold ?? null,
      note: `gate.mjs: ${decision.why}`,
    });
    state.last_updated = new Date().toISOString();
    mkdirSync(dirname(statePath), { recursive: true });
    writeFileSync(statePath, `${JSON.stringify(state, null, 2)}
`);
    return state;
  } catch {
    return null; // bookkeeping must never become a new failure mode for the gate
  }
}

const ESCALATION_FILE = ".aid/pipeline/ESCALATION.json";

export function escalationPath(root) {
  return join(root, ESCALATION_FILE);
}

/** Is there an unresolved escalation? The Stop hook blocks on this. */
export function openEscalation(root) {
  const p = escalationPath(root);
  if (!existsSync(p)) return null;
  try {
    const e = JSON.parse(readFileSync(p, "utf8"));
    return e?.status === "open" ? e : null;
  } catch {
    // A corrupt escalation file counts as OPEN. Failing open here would let a parse error dismiss a
    // quality escalation, which is the one direction that must never happen silently.
    return { status: "open", step: "?", why: "escalation file is unreadable — treating as open", corrupt: true };
  }
}

function writeEscalation(root, payload) {
  const p = escalationPath(root);
  mkdirSync(dirname(p), { recursive: true });
  writeFileSync(p, `${JSON.stringify(payload, null, 2)}\n`);
  return p;
}

/**
 * How many SURFACES does this brief declare, and is that within the run's cap?
 *
 * WHY THIS EXISTS. Every task that ever reached 9.5 was one surface. The two that never reached it
 * carried six each. That is not a correlation to admire — there is a mechanism: one MAJOR finding
 * anywhere caps the whole review at 6, and MAJOR-eligible defect count scales with the number of
 * surfaces in the diff. So a wide slice cannot pass a 9.5 gate no matter how many fix rounds it is
 * given, and the rounds get spent proving that.
 *
 * WHY IT IS A DECLARATION RATHER THAN A JUDGEMENT. Do not ask an agent to assess width; width is the
 * thing being policed, and the party that wants to advance is the wrong one to rule on it. The brief
 * DECLARES its surfaces, and step 2 of the CODE_REVIEW spawn falsifies the declaration against
 * `git diff --name-only HEAD`. A claim with a mechanical consequence, not a guess.
 *
 * A surface is one thing a user can point at and say "this changed": a route, page or tab, a CLI
 * command or flag, an API endpoint, a background job, an instrumentation tier, a file format.
 * Refactors, helpers, types, tests and config plumbing are NOT surfaces.
 *
 * Pure, and separate from decide(): decide() correctly returns ERROR for a step it does not judge,
 * and BRIEF_SCOPE is deliberately not in STEP_CONFIG (it is not scored, so it has no counter and no
 * threshold key of the usual shape).
 *
 * An absent or empty `surfaces:` block is ERROR, not PASS. An undeclared brief has not been checked,
 * and "cannot tell" is never a pass — the same rule as a missing score at line ~130.
 */
export function checkBriefScope({ text, config }) {
  const max = config?.thresholds?.max_surfaces;
  if (!Number.isFinite(max) || max < 1) {
    return { result: "ERROR", exit: 3, surfaces: null, declared: [],
      why: `config.thresholds.max_surfaces must be a number >= 1 (got ${JSON.stringify(max)})` };
  }
  if (typeof text !== "string" || !text.trim()) {
    return { result: "ERROR", exit: 3, surfaces: null, declared: [], max,
      why: "the brief is empty — there is nothing to check" };
  }

  // Deliberately a small parser rather than a YAML dependency: the gate has no node_modules and must
  // run from any project. It reads exactly the shape the brief template writes.
  const lines = text.split(/\r?\n/);
  const start = lines.findIndex((l) => /^surfaces:\s*$/.test(l));
  if (start === -1) {
    // An inline `surfaces: []` or `surfaces: 3` is a declaration that skipped the naming, which is
    // where the honesty lives. Name it as a distinct error rather than reporting "no block".
    const inline = lines.find((l) => /^surfaces:\s*\S/.test(l));
    return { result: "ERROR", exit: 3, surfaces: null, declared: [], max,
      why: inline
        ? `surfaces: must be a block list of named entries, not inline (${inline.trim()})`
        : "the brief declares no `surfaces:` block — an undeclared brief has not been scope-checked" };
  }

  const declared = [];
  const malformed = [];
  for (let i = start + 1; i < lines.length; i += 1) {
    const line = lines[i];
    if (/^\S/.test(line)) break; // next top-level key, or the front-matter terminator
    const item = /^\s*-\s*(.*)$/.exec(line);
    if (item) {
      declared.push({ raw: item[1], name: null, path: null });
      // `- name: x` on the item line itself
      const inlineName = /^name:\s*(.+)$/.exec(item[1].trim());
      if (inlineName) declared[declared.length - 1].name = inlineName[1].trim();
      continue;
    }
    const kv = /^\s*(name|path):\s*(.+)$/.exec(line);
    if (kv && declared.length) declared[declared.length - 1][kv[1]] = kv[2].trim();
  }

  if (declared.length === 0) {
    return { result: "ERROR", exit: 3, surfaces: 0, declared, max,
      why: "the `surfaces:` block is empty — an undeclared brief has not been scope-checked" };
  }
  for (const d of declared) {
    if (!d.name || !d.path) malformed.push(d.name ?? d.path ?? d.raw ?? "<blank>");
  }
  if (malformed.length) {
    // A surface with no path cannot be falsified against the diff, so it is not a declaration — it is
    // a label. Refusing it here is what stops "one surface: the dashboard" from working.
    return { result: "ERROR", exit: 3, surfaces: declared.length, declared, max,
      why: `every surface needs both a name and a path; ${malformed.length} missing one: ${malformed.join(", ")}` };
  }

  // `raw` is parser scaffolding used only for the malformed-entry message; it must not reach the
  // recorded artifact, where it would be a second, drifting copy of name.
  const clean = declared.map(({ name, path }) => ({ name, path }));

  if (declared.length > max) {
    return { result: "ESCALATE", exit: 2, surfaces: declared.length, declared: clean, max,
      why: `${declared.length} surfaces declared against a cap of ${max} — split the task, or resolve this ` +
        `escalation with the reason the slice cannot be split` };
  }
  return { result: "PASS", exit: 0, surfaces: declared.length, declared: clean, max,
    why: `${declared.length} surface(s) within the cap of ${max}` };
}

/**
 * Round 1, or a previous score within `reviewers.dual_within_of_threshold` of the step's threshold →
 * spawn two independent reviewers instead of one (SKILL.md "Two reviewers, and exactly when").
 *
 * PURE ARITHMETIC ON PURPOSE, NOT A CLASSIFIER CALL. The rule this replaces was already fully
 * deterministic prose (round === 1, or |prevScore - threshold| <= dual_within_of_threshold) — there is
 * no judgement here for a model to make, only a comparison the orchestrator already has every input
 * for. This file's whole reason to exist is turning a prose decision an agent could talk itself past
 * into "a pure function with exit codes" (see the file header) — routing an already-deterministic
 * decision through a network call would trade a zero-dependency, zero-latency, testable answer for a
 * slower and non-deterministic one, in the one file that explicitly has no node_modules and no I/O in
 * its decision functions. So: no classifier here, by design.
 */
/**
 * Most recent recorded score for `step`, scoped to the CURRENT task only.
 *
 * WHY task-scoped (CODE_REVIEW cr-20260923-gate-should-spawn-dual MAJOR): step_history is meant to
 * reset per task at pipeline init, but recordDecision's own doc comment above records a REAL,
 * REPRODUCED failure where that reset did not happen — one project's 36 entries were rewritten under
 * four different task_ids at identical timestamps. Filtering only by step name would let a later
 * round of a NEW task silently pick up an unrelated task's score, with no error surfaced anywhere.
 */
export function mostRecentScore({ stepHistory, step, taskId }) {
  const match = [...(stepHistory ?? [])].reverse().find(
    (h) => h.step === step && (h.task_id ?? null) === (taskId ?? null) && typeof h.scores?.overall === "number",
  );
  return match?.scores?.overall;
}

export function shouldSpawnDual({ round, prevScore, threshold, config }) {
  if (!Number.isFinite(round) || round < 1) {
    return { dual: false, why: `invalid round (${JSON.stringify(round)})` };
  }
  if (round === 1) return { dual: true, why: "round 1 — defect set is largest" };

  const within = config?.reviewers?.dual_within_of_threshold ?? 1.0;
  if (
    typeof prevScore !== "number" || !Number.isFinite(prevScore) ||
    typeof threshold !== "number" || !Number.isFinite(threshold)
  ) {
    return { dual: false, why: "no previous score to compare against — not round 1, defaulting to single" };
  }
  const spread = Math.abs(prevScore - threshold);
  const boundary = spread <= within;
  return {
    dual: boundary,
    why: boundary
      ? `boundary round: |${prevScore} - ${threshold}| = ${spread} <= ${within}`
      : `mid-band: |${prevScore} - ${threshold}| = ${spread} > ${within} — cap-dominated, a second sample changes nothing`,
  };
}

export const REVIEW_WEIGHTS = { security: 30, code_quality: 30, architecture: 25, documentation: 15 };

/**
 * Every finding a review reported, flattened, whatever shape it arrived in.
 *
 * Liberal on input for the same reason hasCriticalSecurity is: two agent definitions and several
 * hand-written transcripts disagree about nesting, and a merge that understands one shape would
 * silently drop the other reviewer's findings — which is exactly the failure the second reviewer was
 * added to prevent.
 */
export function collectFindings(scores) {
  const out = [];
  const push = (f, inheritedCategory) => {
    if (!f) return;
    if (typeof f === "string") {
      out.push({ file: "", pattern: f, severity: "", category: inheritedCategory ?? "" });
      return;
    }
    out.push({
      file: String(f.file ?? f.path ?? f.at ?? ""),
      pattern: String(f.pattern ?? f.issue ?? f.note ?? f.title ?? f.description ?? ""),
      severity: String(f.severity ?? ""),
      category: String(f.category ?? f.area ?? inheritedCategory ?? ""),
    });
  };
  for (const key of ["issues", "findings", "action_required"]) {
    if (Array.isArray(scores?.[key])) for (const f of scores[key]) push(f);
  }
  const cats = scores?.categories;
  if (cats && typeof cats === "object") {
    for (const [name, cat] of Object.entries(cats)) {
      for (const key of ["issues", "findings"]) {
        if (Array.isArray(cat?.[key])) for (const f of cat[key]) push(f, name);
      }
    }
  }
  return out;
}

const severityRank = (sev) => {
  const s = String(sev ?? "").trim().toUpperCase();
  if (s === "CRITICAL") return 3;
  if (s === "MAJOR") return 2;
  if (s === "MINOR") return 1;
  return 0;
};

/**
 * Merge two independent reviews of the same diff.
 *
 * WHAT THIS IS FOR, and what it is NOT for. Two reviewers do NOT make a 9.5 gate stable: averaging
 * two samples of the same prompt cuts the standard deviation by only about 1/sqrt(2), so against the
 * measured 1.5-point dimension spread the residual is still roughly 1.06. What they buy is the UNION
 * of defects in one round instead of across two. That is the whole case for the change, and stability
 * is not part of it.
 *
 * MEAN-OF-OVERALLS ALONE WOULD BE A DEFECT-LAUNDERING MACHINE. `overall` is a step function of the
 * worst severity found: any CRITICAL caps it at 4, any MAJOR at 6. So averaging a clean 9.6 with a
 * 6.0 that carries one real MAJOR yields 7.8 — which is still FIX at a 9.5 bar today, and becomes a
 * pass the moment anyone moves a threshold. Instead: take the cap from the UNION of findings, then
 * take the mean only underneath it. The mean therefore operates only where nothing blocks, which is
 * precisely where noise rather than a defect decides the outcome.
 *
 * MERGED IN CODE, NOT IN THE ORCHESTRATOR'S JUDGEMENT. The orchestrator is the party that wants to
 * advance; asking it to arbitrate two disagreeing reviews is asking the interested party to rule.
 */
export function mergeReviews(reviews) {
  const present = (Array.isArray(reviews) ? reviews : []).filter(
    (r) => r && typeof r === "object" && typeof r.overall === "number" && Number.isFinite(r.overall),
  );

  if (present.length === 0) {
    // Same principle as a missing score in decide(): a review that produced nothing has not scored
    // badly, it has not run. Never average against a phantom.
    return { overall: undefined, reviewers_used: 0, reviewers: [], spread: null, findings: [],
      critical_security: false, cap: null,
      merge_note: "no reviewer produced a score — this is ERROR, not a low score" };
  }

  if (present.length === 1) {
    const only = present[0];
    return { ...only, reviewers_used: 1, reviewers: [{ overall: only.overall }], spread: null,
      findings: collectFindings(only), critical_security: hasCriticalSecurity(only),
      cap: capFromFindings(collectFindings(only)),
      merge_note: "one reviewer only — used as-is, never averaged against a phantom" };
  }

  const [a, b] = present;
  const findings = unionFindings(collectFindings(a), collectFindings(b));
  const cap = capFromFindings(findings);

  const dims = {};
  for (const d of Object.keys(REVIEW_WEIGHTS)) {
    const av = Number(a?.[d]);
    const bv = Number(b?.[d]);
    const both = [av, bv].filter((v) => Number.isFinite(v));
    if (both.length) dims[d] = Math.round((both.reduce((x, y) => x + y, 0) / both.length) * 100) / 100;
  }

  let weighted = 0;
  let weightUsed = 0;
  for (const [d, w] of Object.entries(REVIEW_WEIGHTS)) {
    if (!Number.isFinite(dims[d])) continue;
    weighted += dims[d] * w;
    weightUsed += w;
  }
  // No per-dimension numbers at all: fall back to the mean of the two composites, which is the only
  // thing actually reported. Still capped below.
  const mean = weightUsed > 0
    ? weighted / weightUsed
    : (a.overall + b.overall) / 2;

  const overall = Math.round(Math.min(mean, cap ?? 10) * 100) / 100;

  return {
    ...dims,
    overall,
    cap,
    critical_security: hasCriticalSecurity(a) || hasCriticalSecurity(b),
    findings,
    reviewers_used: 2,
    reviewers: [{ overall: a.overall }, { overall: b.overall }],
    spread: Math.round(Math.abs(a.overall - b.overall) * 100) / 100,
    merge_note: cap === null
      ? "no blocking severity in the union; composite is the weighted mean of both reviewers"
      : `capped at ${cap} by the UNION of findings — one reviewer's blocking finding caps the merged review`,
  };
}

/** 4 if any CRITICAL anywhere, 6 if any MAJOR, else no cap. Same step function the rubric applies. */
export function capFromFindings(findings) {
  let worst = 0;
  for (const f of findings ?? []) worst = Math.max(worst, severityRank(f?.severity));
  if (worst === 3) return 4;
  if (worst === 2) return 6;
  return null;
}

/**
 * Union of two finding lists, deduped on file + pattern and NEVER on line number.
 *
 * Measured: in the real incident the two reviewers reported the SAME defect at different lines. A
 * line-keyed dedupe would have counted it twice, which inflates nothing important — but it would also
 * have made the two reports look disjoint, hiding the agreement. The kept copy is the one with the
 * higher severity, because a merge must never soften a severity either reviewer assigned.
 */
export function unionFindings(a, b) {
  const key = (f) => `${String(f?.file ?? "").toLowerCase()}:${String(f?.pattern ?? "").toLowerCase().trim()}`;
  const seen = new Map();
  for (const f of [...(a ?? []), ...(b ?? [])]) {
    const k = key(f);
    const prev = seen.get(k);
    if (!prev || severityRank(f?.severity) > severityRank(prev?.severity)) seen.set(k, f);
  }
  return [...seen.values()];
}

// ── CLI ──
function arg(name) {
  const i = process.argv.indexOf(`--${name}`);
  return i === -1 ? undefined : process.argv[i + 1];
}
const has = (name) => process.argv.includes(`--${name}`);

function main() {
  const root = arg("root") ?? process.cwd();

  if (has("check-escalation")) {
    const e = openEscalation(root);
    if (!e) {
      console.log("gate: no open escalation");
      process.exit(0);
    }
    console.error(`gate: ESCALATION OPEN — ${e.step} ${e.overall ?? "?"} < ${e.threshold ?? "?"}: ${e.why}`);
    process.exit(2);
  }

  // C1: scope-check a brief BEFORE it is frozen. Deliberately its own verb rather than a --step, and
  // deliberately not in STEP_CONFIG: BRIEF_SCOPE is not scored, so it has no counter and no threshold
  // of the usual shape, and decide() correctly returns ERROR for a step it does not judge.
  //
  // Order matters upstream: draft to brief.draft.md, run this, and only on exit 0 write brief.md. The
  // hook records brief.sha256 on first freeze, so a check that ran AFTER the freeze would be demanding
  // edits to an immutable, hash-pinned file.
  if (has("brief-check")) {
    const briefPath = arg("brief-check");
    if (!briefPath) {
      console.error("gate: --brief-check needs a path to the draft brief");
      process.exit(3);
    }
    if (!existsSync(briefPath)) {
      console.error(`gate: no brief at ${briefPath} — nothing to scope-check`);
      process.exit(3);
    }
    const cfgPath = join(root, ".aid/pipeline/config.json");
    if (!existsSync(cfgPath)) {
      console.error(`gate: no config at ${cfgPath}`);
      process.exit(3);
    }
    const cfg = JSON.parse(readFileSync(cfgPath, "utf8"));
    const r = checkBriefScope({ text: readFileSync(briefPath, "utf8"), config: cfg });
    console.log(`gate: BRIEF_SCOPE -> ${r.result} (${r.why})`);

    // No `overall` key on purpose: the dashboard's pickScore yields NULL, so a scope row can never be
    // read as a review score. gateKind("BRIEF_SCOPE") is null too, so it renders as an unscored step
    // and needs no dashboard change.
    const scopeScores = { surfaces: r.surfaces, max_surfaces: r.max ?? null, declared: r.declared ?? [] };
    if (!has("dry-run")) recordDecision(root, { step: "BRIEF_SCOPE", decision: r, scores: scopeScores });
    if (r.result === "ESCALATE" && !has("dry-run")) {
      const p = writeEscalation(root, {
        status: "open",
        step: "BRIEF_SCOPE",
        why: r.why,
        surfaces: r.surfaces,
        max_surfaces: r.max,
        declared: r.declared,
        opened_at: new Date().toISOString(),
        how_to_resolve:
          "Decide as the human: split the task into one brief per surface, raise " +
          "thresholds.max_surfaces in .aid/pipeline/config.json, or accept this width. Then run: " +
          'node ~/.claude/skills/pipeline-orchestrator/gate.mjs --resolve "<reason>". ' +
          "The Stop hook blocks while this is open.",
      });
      console.error(`gate: wrote ${p} — the Stop hook will block until it is resolved.`);
    }
    process.exit(r.exit);
  }

  // C: "should this round spawn one reviewer or two?" — see shouldSpawnDual's own doc comment for
  // why this is arithmetic, not a classifier call. Exit 0 = dual, 1 = single, 3 = usage error — a
  // distinct contract from decide()'s PASS/FIX/ESCALATE/ERROR, so it never gets read as a score gate.
  if (has("should-spawn-dual")) {
    const step = arg("step");
    const spec = STEP_CONFIG[step];
    if (!step || !spec || spec.threshold === null) {
      console.error("gate: --should-spawn-dual needs --step <a scored step: CODE_REVIEW | TEST_REVIEW | VISUAL_QA>");
      process.exit(3);
    }
    const configPath = join(root, ".aid/pipeline/config.json");
    if (!existsSync(configPath)) {
      console.error(`gate: no config at ${configPath}`);
      process.exit(3);
    }
    // Unguarded JSON.parse here would let a corrupt file throw uncaught -> Node's default exit
    // code 1, which THIS verb's own contract reads as "spawn one reviewer" (a normal decision),
    // silently downgrading review rigor on a data-corruption event instead of hitting exit 3 —
    // exactly the failure the --scores/--scores-b parsing below already guards against.
    let config;
    try {
      config = JSON.parse(readFileSync(configPath, "utf8"));
    } catch (err) {
      console.error(`gate: config.json is not valid JSON: ${err.message}`);
      process.exit(3);
    }
    const statePath = join(root, ".aid/pipeline/state.json");
    let state = {};
    if (existsSync(statePath)) {
      try {
        state = JSON.parse(readFileSync(statePath, "utf8"));
      } catch (err) {
        console.error(`gate: state.json is not valid JSON: ${err.message}`);
        process.exit(3);
      }
    }
    const iterationsUsed = Number(state?.iterations?.[spec.counter] ?? 0);
    const roundArg = arg("round");
    // An explicitly-supplied, malformed --round is a usage error, not "invalid round -> spawn
    // one" — those must stay distinguishable so `$?` alone tells a caller which one happened.
    if (roundArg !== undefined && !Number.isFinite(Number(roundArg))) {
      console.error(`gate: --round must be a number (got ${JSON.stringify(roundArg)})`);
      process.exit(3);
    }
    const round = roundArg !== undefined ? Number(roundArg) : iterationsUsed + 1;
    // Explicit --prev-score wins; otherwise the most recently recorded score for this step,
    // scoped to THIS task (see mostRecentScore's own doc comment for why that scoping matters).
    const prevScoreArg = arg("prev-score");
    const prevScore = prevScoreArg !== undefined
      ? Number(prevScoreArg)
      : mostRecentScore({
          stepHistory: state.step_history,
          step,
          taskId: state?.current_task_id ?? state?.task_id ?? null,
        });
    const threshold = config?.thresholds?.[spec.threshold];
    const r = shouldSpawnDual({ round, prevScore, threshold, config });
    console.log(`gate: ${step} round ${round} -> ${r.dual ? "DUAL" : "SINGLE"} (${r.why})`);
    process.exit(r.dual ? 0 : 1);
  }

  if (has("resolve")) {
    const how = arg("resolve");
    if (!how) {
      console.error("gate: --resolve needs a reason (what changed, or why it is accepted)");
      process.exit(3);
    }
    const p = escalationPath(root);
    if (!existsSync(p)) {
      console.error("gate: nothing to resolve");
      process.exit(3);
    }
    const e = JSON.parse(readFileSync(p, "utf8"));
    writeEscalation(root, { ...e, status: "resolved", resolved_how: how, resolved_at: new Date().toISOString() });
    console.log("gate: escalation resolved");
    process.exit(0);
  }

  const step = arg("step");
  const rawScores = arg("scores");
  if (!step || !rawScores) {
    console.error("usage: gate.mjs --step CODE_REVIEW --scores '{\"overall\":9.6}' [--root DIR] [--dry-run]");
    process.exit(3);
  }
  let scores;
  try {
    scores = JSON.parse(rawScores);
  } catch (err) {
    console.error(`gate: --scores is not JSON: ${err.message}`);
    process.exit(3);
  }

  // C5: a second independent review of the same diff. Merged HERE, in code, rather than by the
  // orchestrator: the orchestrator is the party that wants to advance, so asking it to arbitrate two
  // disagreeing reviews is asking the interested party to rule. It must pass both verbatim and must
  // not show one reviewer's output to the other.
  const rawScoresB = arg("scores-b");
  if (rawScoresB !== undefined) {
    let scoresB;
    try {
      scoresB = JSON.parse(rawScoresB);
    } catch (err) {
      console.error(`gate: --scores-b is not JSON: ${err.message}`);
      process.exit(3);
    }
    const merged = mergeReviews([scores, scoresB]);
    console.log(
      `gate: merged ${merged.reviewers_used} reviewer(s)` +
        (merged.spread === null ? "" : `, spread ${merged.spread}`) +
        ` — ${merged.merge_note}`,
    );
    scores = merged;
  }

  const configPath = join(root, ".aid/pipeline/config.json");
  const statePath = join(root, ".aid/pipeline/state.json");
  if (!existsSync(configPath)) {
    console.error(`gate: no config at ${configPath}`);
    process.exit(3);
  }
  const config = JSON.parse(readFileSync(configPath, "utf8"));
  const state = existsSync(statePath) ? JSON.parse(readFileSync(statePath, "utf8")) : {};
  const counter = STEP_CONFIG[step]?.counter;
  const iterationsUsed = Number(state?.iterations?.[counter] ?? 0);

  const d = decide({ step, scores, config, iterationsUsed });
  console.log(`gate: ${step} → ${d.result} (${d.why})`);
  // Instrument every decision, including ERROR: a gate that could not decide is exactly the event a
  // loops view needs to show, and it is invisible in state.json.
  logLoopEvent({
    loop: 2,
    event: "gate",
    task_id: state?.current_task_id ?? state?.task_id ?? null,
    step,
    result: d.result,
    score: d.overall ?? null,
    threshold: d.threshold ?? null,
    // Same expression recordDecision uses, so the two records of one decision stop disagreeing.
    // Measured before the fix: the event said iteration 1 and the step_history entry said 2 for the
    // same FIX, written 1 ms apart. Historical loop_events rows are 0-based; rows from here on are
    // 1-based and match step_history.
    iteration: (d.iterationsUsed ?? 0) + 1,
    cap: d.cap ?? null,
    problem: d.result === "PASS" ? null : d.why,
  }, root);
  // RECORD FIRST, THEN EXIT (2026-09-04). These two lines used to be the other way round, so an
  // ERROR left step_history untouched and a dead or malformed reviewer was invisible in the record:
  // `SELECT count(*) FROM pipeline_steps WHERE result='ERROR'` returned 0 by construction, not by
  // absence of the event. That is why "3 of 4 spawned agents produced nothing this session" could not
  // be counted, and why those rounds were being charged to FIX_CODE instead.
  //
  // recordDecision is already correct for ERROR with no change: result !== "FIX" so no counter
  // increments, and with no `overall` key the dashboard's pickScore yields NULL, so an ERROR row can
  // never pollute a score average.
  if (!has("dry-run")) recordDecision(root, { step, decision: d, scores });
  if (d.result === "ERROR") process.exit(3);

  if (d.result === "ESCALATE" && !has("dry-run")) {
    const p = writeEscalation(root, {
      status: "open",
      step,
      result: d.result,
      overall: d.overall ?? null,
      threshold: d.threshold ?? null,
      iterations_used: d.iterationsUsed,
      cap: d.cap,
      why: d.why,
      scores,
      opened_at: new Date().toISOString(),
      how_to_resolve:
        "Decide as the human: raise the code to clear the threshold, lower the threshold in " +
        ".aid/pipeline/config.json, or accept this result. Then run: " +
        "node ~/.claude/skills/pipeline-orchestrator/gate.mjs --resolve \"<reason>\". " +
        "The Stop hook blocks while this is open.",
    });
    console.error(`gate: wrote ${p} — the Stop hook will block until it is resolved.`);
  }
  process.exit(d.exit);
}

if (import.meta.url === `file://${process.argv[1]}` || process.argv[1]?.endsWith("gate.mjs")) main();
