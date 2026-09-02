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
//
// Exit codes (the contract the orchestrator and the hook rely on):
//   0 = PASS      advance to the next step
//   1 = FIX       below threshold, iterations remain → run the fix step and re-review
//   2 = ESCALATE  below threshold with iterations exhausted → STOP and ask the human
//   3 = usage/data error (never silently treated as a pass)
import { readFileSync, writeFileSync, existsSync, mkdirSync, appendFileSync } from "node:fs";
import { join, dirname } from "node:path";

export const STEP_CONFIG = {
  CODE_REVIEW: { threshold: "code_review_pass", counter: "code_review" },
  TEST_REVIEW: { threshold: "test_review_pass", counter: "test_review" },
  VISUAL_QA: { threshold: "visual_qa_pass", counter: "visual_qa" },
  PHASE_GATE: { threshold: null, counter: "phase_gate_reexamine" },
};

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
  if (config?.thresholds?.auto_fail_on_critical_security && scores?.critical_security === true) {
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
      result: decision.result,
      scores: scores ?? {},
      timestamp: new Date().toISOString(),
      iteration: decision.result === "FIX" && counter ? state.iterations[counter] : (decision.iterationsUsed ?? null),
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
    iteration: d.iterationsUsed ?? null,
    cap: d.cap ?? null,
    problem: d.result === "PASS" ? null : d.why,
  }, root);
  if (d.result === "ERROR") process.exit(3);
  if (!has("dry-run")) recordDecision(root, { step, decision: d, scores });

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
