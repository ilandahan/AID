// Tests for the scored-step gate. Run: node --test
//
// The case that matters most is "7.9 at cap": this workspace's own step_history contains
// CODE_REVIEW logged PASS at 7.9 and 7.6 against a threshold of 9.5, with nothing escalated. That
// happened because the gate was prose an agent was expected to follow. These tests are the reason it
// cannot happen again.
import { test } from "node:test";
import assert from "node:assert/strict";
import { mkdtempSync, mkdirSync, writeFileSync, rmSync, existsSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { tmpdir } from "node:os";
import { decide, openEscalation, recordDecision, hasCriticalSecurity } from "./gate.mjs";

const CONFIG = {
  max_iterations: { code_review: 5, test_review: 5, phase_gate_reexamine: 5, visual_qa: 5 },
  thresholds: { code_review_pass: 9.5, test_review_pass: 9.5, visual_qa_pass: 9.5, auto_fail_on_critical_security: true },
};

test("the historical bug: 7.9 with iterations exhausted ESCALATES, it is not a PASS", () => {
  const d = decide({ step: "CODE_REVIEW", scores: { overall: 7.9 }, config: CONFIG, iterationsUsed: 5 });
  assert.equal(d.result, "ESCALATE");
  assert.equal(d.exit, 2);
  assert.match(d.why, /NOT a pass/);
});

test("below threshold with rounds left is FIX, and says how many remain", () => {
  const d = decide({ step: "CODE_REVIEW", scores: { overall: 7.9 }, config: CONFIG, iterationsUsed: 2 });
  assert.equal(d.result, "FIX");
  assert.equal(d.exit, 1);
  assert.match(d.why, /3 fix cycle\(s\) left/);
});

test("at or above threshold passes", () => {
  assert.equal(decide({ step: "CODE_REVIEW", scores: { overall: 9.5 }, config: CONFIG }).result, "PASS");
  assert.equal(decide({ step: "CODE_REVIEW", scores: { overall: 9.6 }, config: CONFIG }).result, "PASS");
});

test("9.49 does not pass a 9.5 bar — no rounding into a pass", () => {
  const d = decide({ step: "CODE_REVIEW", scores: { overall: 9.49 }, config: CONFIG, iterationsUsed: 0 });
  assert.equal(d.result, "FIX");
});

test("a critical security finding escalates even with a passing composite", () => {
  const d = decide({ step: "CODE_REVIEW", scores: { overall: 9.9, critical_security: true }, config: CONFIG });
  assert.equal(d.result, "ESCALATE");
  assert.match(d.why, /critical security/);
});

test("a missing or non-numeric score is an ERROR, never a pass", () => {
  // null is the one that caught a real bug: Number(null) is 0, finite, so it reported FIX (a phantom
  // zero) instead of ERROR. A numeric STRING must also fail rather than be coerced.
  for (const scores of [{}, { overall: null }, { overall: undefined }, { overall: "abc" }, { overall: "9.6" }, { overall: NaN }]) {
    const d = decide({ step: "CODE_REVIEW", scores, config: CONFIG });
    assert.equal(d.result, "ERROR", `scores=${JSON.stringify(scores)} must not pass`);
    assert.equal(d.exit, 3);
  }
});

test("a missing cap or threshold is an ERROR, not an implicit pass", () => {
  assert.equal(decide({ step: "CODE_REVIEW", scores: { overall: 9.9 }, config: { thresholds: CONFIG.thresholds } }).result, "ERROR");
  assert.equal(decide({ step: "CODE_REVIEW", scores: { overall: 9.9 }, config: { max_iterations: CONFIG.max_iterations } }).result, "ERROR");
});

test("an unknown step errors rather than guessing a gate", () => {
  assert.equal(decide({ step: "DEVELOP", scores: { overall: 10 }, config: CONFIG }).result, "ERROR");
});

test("PHASE_GATE is boolean, and exhausting re-examine rounds escalates", () => {
  assert.equal(decide({ step: "PHASE_GATE", scores: { passed: true }, config: CONFIG }).result, "PASS");
  assert.equal(decide({ step: "PHASE_GATE", scores: { passed: false }, config: CONFIG, iterationsUsed: 1 }).result, "FIX");
  assert.equal(decide({ step: "PHASE_GATE", scores: { passed: false }, config: CONFIG, iterationsUsed: 5 }).result, "ESCALATE");
});

test("PHASE_GATE accepts the spellings the validators actually emit, not just `passed`", () => {
  // The inversion this prevents: nothing in this skill writes `passed`. SKILL.md's contract is
  // `verdict: "PASS"` and SKILL.extended.md's is `can_proceed: true`, so a PASSING phase gate used to
  // come back FIX and push the work back to DEVELOP.
  assert.equal(decide({ step: "PHASE_GATE", scores: { verdict: "PASS" }, config: CONFIG }).result, "PASS");
  assert.equal(decide({ step: "PHASE_GATE", scores: { can_proceed: true }, config: CONFIG }).result, "PASS");
  // and a real failure in either spelling still fails
  assert.equal(decide({ step: "PHASE_GATE", scores: { verdict: "FAIL" }, config: CONFIG, iterationsUsed: 1 }).result, "FIX");
  assert.equal(decide({ step: "PHASE_GATE", scores: { can_proceed: false }, config: CONFIG, iterationsUsed: 1 }).result, "FIX");
  // a truthy-but-wrong verdict must NOT pass: only the exact contract value counts
  assert.equal(decide({ step: "PHASE_GATE", scores: { verdict: "PASS_WITH_NITS" }, config: CONFIG, iterationsUsed: 1 }).result, "FIX");
});

test("TEST_REVIEW and VISUAL_QA use their own thresholds and counters", () => {
  const cfg = {
    max_iterations: { test_review: 1, visual_qa: 5 },
    thresholds: { test_review_pass: 9.5, visual_qa_pass: 7 },
  };
  assert.equal(decide({ step: "TEST_REVIEW", scores: { overall: 9.4 }, config: cfg, iterationsUsed: 1 }).result, "ESCALATE");
  assert.equal(decide({ step: "VISUAL_QA", scores: { overall: 7.2 }, config: cfg }).result, "PASS");
});

test("an open escalation is detected, a resolved one is not, and a corrupt one counts as open", () => {
  const dir = mkdtempSync(join(tmpdir(), "gate-esc-"));
  try {
    mkdirSync(join(dir, ".aid/pipeline"), { recursive: true });
    const p = join(dir, ".aid/pipeline/ESCALATION.json");

    assert.equal(openEscalation(dir), null, "no file = nothing open");

    writeFileSync(p, JSON.stringify({ status: "open", step: "CODE_REVIEW", why: "7.9 < 9.5" }));
    assert.equal(openEscalation(dir)?.step, "CODE_REVIEW");

    writeFileSync(p, JSON.stringify({ status: "resolved", step: "CODE_REVIEW" }));
    assert.equal(openEscalation(dir), null, "resolved must clear the block");

    // failing open here would let a parse error dismiss a quality escalation
    writeFileSync(p, "{ not json");
    assert.equal(openEscalation(dir)?.status, "open");
    assert.equal(openEscalation(dir)?.corrupt, true);
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});

test("the gate owns the counter: two consecutive FIX decisions consume two of the five cycles", () => {
  // WHY: in demo/saas iterations.code_review stayed at 1 across two FIX verdicts because incrementing
  // was left to the agent. With the gate writing state.json, round 2 must see one fewer cycle left.
  const root = mkdtempSync(join(tmpdir(), "gate-counter-"));
  try {
    mkdirSync(join(root, ".aid/pipeline"), { recursive: true });
    writeFileSync(join(root, ".aid/pipeline/state.json"), JSON.stringify({ current_task_id: "t1", iterations: { code_review: 0 } }));
    const read = () => JSON.parse(readFileSync(join(root, ".aid/pipeline/state.json"), "utf8"));

    const d1 = decide({ step: "CODE_REVIEW", scores: { overall: 6.0 }, config: CONFIG, iterationsUsed: read().iterations.code_review });
    recordDecision(root, { step: "CODE_REVIEW", decision: d1, scores: { overall: 6.0 } });
    assert.equal(read().iterations.code_review, 1);
    assert.match(d1.why, /5 fix cycle\(s\) left/);

    const d2 = decide({ step: "CODE_REVIEW", scores: { overall: 6.0 }, config: CONFIG, iterationsUsed: read().iterations.code_review });
    recordDecision(root, { step: "CODE_REVIEW", decision: d2, scores: { overall: 6.0 } });
    assert.equal(read().iterations.code_review, 2);
    assert.match(d2.why, /4 fix cycle\(s\) left/);

    const pass = decide({ step: "CODE_REVIEW", scores: { overall: 9.6 }, config: CONFIG, iterationsUsed: read().iterations.code_review });
    recordDecision(root, { step: "CODE_REVIEW", decision: pass, scores: { overall: 9.6 } });
    const s = read();
    assert.equal(s.iterations.code_review, 2, "a PASS must not consume a fix cycle");
    assert.equal(s.step_history.length, 3);
    assert.deepEqual(s.step_history.map((h) => h.result), ["FIX", "FIX", "PASS"]);
    assert.equal(s.step_history[1].iteration, 2);
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
});

// ---------------------------------------------------------------------------
// critical_security is DERIVED (2026-09-04). The reviewer agents never emit the
// `critical_security` key, so the auto-fail branch above was dead code from the day it shipped.
// These cases pin the derivation from the findings reviewers DO emit; without them the branch can
// silently return to being decorative.

test("a CRITICAL security finding in the reviewer's own output escalates, with no critical_security key", () => {
  const scores = {
    overall: 9.9,
    issues: [
      { severity: "MINOR", category: "documentation", note: "missing jsdoc" },
      { severity: "CRITICAL", category: "security", note: "token logged in plaintext" },
    ],
  };
  assert.equal(hasCriticalSecurity(scores), true, "derivation must find the finding");
  const d = decide({ step: "CODE_REVIEW", scores, config: CONFIG });
  assert.equal(d.result, "ESCALATE", "9.9 composite must not buy a critical security finding");
  assert.equal(d.exit, 2);
  assert.match(d.why, /critical security/);
});

test("the nested categories.security shape the response format uses is read too", () => {
  const scores = { overall: 9.8, categories: { security: { issues: [{ severity: "critical", note: "auth bypass" }] } } };
  assert.equal(hasCriticalSecurity(scores), true);
  assert.equal(decide({ step: "CODE_REVIEW", scores, config: CONFIG }).result, "ESCALATE");
});

test("a CRITICAL finding OUTSIDE security does not trip the security auto-fail", () => {
  // The step function already caps a CRITICAL at 4, so this review fails on its composite anyway.
  // What must not happen is it escalating as a SECURITY event and skipping its remaining fix cycles.
  const scores = { overall: 4, issues: [{ severity: "CRITICAL", category: "code_quality", note: "data loss on retry" }] };
  assert.equal(hasCriticalSecurity(scores), false);
  assert.equal(decide({ step: "CODE_REVIEW", scores, config: CONFIG }).result, "FIX");
});

test("an explicit critical_security boolean still wins, in both directions", () => {
  assert.equal(hasCriticalSecurity({ critical_security: true }), true);
  // false must not be overridden by a derivation, or a caller that deliberately cleared the flag
  // after review would be unable to.
  assert.equal(hasCriticalSecurity({ critical_security: false, issues: [{ severity: "CRITICAL", category: "security" }] }), false);
});

test("a clean review derives false rather than throwing on any shape", () => {
  for (const scores of [{ overall: 9.6 }, { overall: 9.6, issues: [] }, { overall: 9.6, issues: null },
                        { overall: 9.6, categories: {} }, {}, null, undefined]) {
    assert.equal(hasCriticalSecurity(scores), false, `shape ${JSON.stringify(scores)} must derive false`);
  }
  assert.equal(decide({ step: "CODE_REVIEW", scores: { overall: 9.6 }, config: CONFIG }).result, "PASS");
});

test("the auto-fail respects its config switch: unset means the composite decides", () => {
  const scores = { overall: 9.9, issues: [{ severity: "CRITICAL", category: "security" }] };
  const off = { ...CONFIG, thresholds: { ...CONFIG.thresholds, auto_fail_on_critical_security: false } };
  assert.equal(decide({ step: "CODE_REVIEW", scores, config: off }).result, "PASS");
});

// ---------------------------------------------------------------------------
// A dead agent must leave a record (2026-09-04). ERROR used to exit before recordDecision ran, so
// a reviewer that produced nothing was absent from step_history entirely and the round got charged
// to the next FIX_CODE. These pin both halves: the ERROR verdict, and the row it must leave behind.

test("a review that produced no scores is ERROR, and still records exactly one row", () => {
  const root = mkdtempSync(join(tmpdir(), "gate-error-"));
  try {
    mkdirSync(join(root, ".aid/pipeline"), { recursive: true });
    writeFileSync(join(root, ".aid/pipeline/state.json"), JSON.stringify({ current_task_id: "t1", iterations: { code_review: 2 } }));
    const read = () => JSON.parse(readFileSync(join(root, ".aid/pipeline/state.json"), "utf8"));

    const d = decide({ step: "CODE_REVIEW", scores: {}, config: CONFIG, iterationsUsed: 2 });
    assert.equal(d.result, "ERROR");
    assert.equal(d.exit, 3);

    recordDecision(root, { step: "CODE_REVIEW", decision: d, scores: {} });
    const s = read();
    assert.equal(s.step_history.length, 1, "a dead agent must be visible in the record");
    assert.equal(s.step_history[0].result, "ERROR");
    assert.equal(s.iterations.code_review, 2, "an ERROR is not a fix cycle — it must not consume one");
    assert.equal(s.step_history[0].scores.overall, undefined,
      "no overall key, so the dashboard's pickScore yields NULL and this row cannot pollute a score average");
    assert.match(s.step_history[0].note, /^gate\.mjs: /);
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
});

test("an ERROR row never lands in the score series alongside real rounds", () => {
  const root = mkdtempSync(join(tmpdir(), "gate-error-mix-"));
  try {
    mkdirSync(join(root, ".aid/pipeline"), { recursive: true });
    writeFileSync(join(root, ".aid/pipeline/state.json"), JSON.stringify({ current_task_id: "t1", iterations: { code_review: 0 } }));
    const read = () => JSON.parse(readFileSync(join(root, ".aid/pipeline/state.json"), "utf8"));

    const fix = decide({ step: "CODE_REVIEW", scores: { overall: 6.0 }, config: CONFIG, iterationsUsed: 0 });
    recordDecision(root, { step: "CODE_REVIEW", decision: fix, scores: { overall: 6.0 } });
    const dead = decide({ step: "CODE_REVIEW", scores: {}, config: CONFIG, iterationsUsed: read().iterations.code_review });
    recordDecision(root, { step: "CODE_REVIEW", decision: dead, scores: {} });

    const s = read();
    assert.deepEqual(s.step_history.map((h) => h.result), ["FIX", "ERROR"]);
    assert.equal(s.iterations.code_review, 1, "the dead round cost no cycle; only the real FIX did");
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
});
