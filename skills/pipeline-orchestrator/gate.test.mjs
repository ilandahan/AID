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
import { decide, openEscalation, recordDecision } from "./gate.mjs";

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
