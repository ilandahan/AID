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
import { decide, openEscalation, recordDecision, hasCriticalSecurity, checkBriefScope, mergeReviews, unionFindings, capFromFindings, collectFindings } from "./gate.mjs";

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

// ---------------------------------------------------------------------------
// C1: the slice cap lives at the brief (2026-09-04). Every task that reached 9.5 was one surface;
// the two that never did carried six each. One MAJOR anywhere caps a review at 6, and MAJOR-eligible
// defect count scales with surface count, so a wide slice cannot pass a 9.5 gate however many rounds
// it is given. These cases pin the cap, and pin that an UNDECLARED brief is an error rather than a pass.

const SCOPE_CONFIG = { thresholds: { max_surfaces: 2 } };
const brief = (surfacesBlock) =>
  ["---", "task_id: t1", "frozen_at: 2026-09-04T00:00:00Z", surfacesBlock, "---", "", "## ORIGINAL_REQUEST", "do the thing", ""].join("\n");
const SURFACE = (name, path) => `  - name: ${name}\n    path: ${path}`;

test("two surfaces are within the cap of two", () => {
  const r = checkBriefScope({ text: brief(["surfaces:", SURFACE("tokens tab", "dashboard/public/app.js"), SURFACE("tokens route", "dashboard/src/tokens.js")].join("\n")), config: SCOPE_CONFIG });
  assert.equal(r.result, "PASS");
  assert.equal(r.exit, 0);
  assert.equal(r.surfaces, 2);
});

test("three surfaces escalate rather than quietly proceeding", () => {
  const r = checkBriefScope({ text: brief(["surfaces:", SURFACE("a", "p1"), SURFACE("b", "p2"), SURFACE("c", "p3")].join("\n")), config: SCOPE_CONFIG });
  assert.equal(r.result, "ESCALATE");
  assert.equal(r.exit, 2);
  assert.equal(r.surfaces, 3);
  assert.match(r.why, /3 surfaces declared against a cap of 2/);
});

test("a brief with no surfaces block is ERROR, never a pass", () => {
  // The whole point: an undeclared brief has not been scope-checked, and "cannot tell" must not
  // advance. If this returned PASS, skipping the declaration would be the cheapest way past the cap.
  const r = checkBriefScope({ text: brief("").trimEnd(), config: SCOPE_CONFIG });
  assert.equal(r.result, "ERROR");
  assert.equal(r.exit, 3);
  assert.match(r.why, /no `surfaces:` block/);
});

test("an empty surfaces block is ERROR too", () => {
  const r = checkBriefScope({ text: brief("surfaces:"), config: SCOPE_CONFIG });
  assert.equal(r.result, "ERROR");
  assert.equal(r.exit, 3);
  assert.match(r.why, /empty/);
});

test("an inline surfaces value is refused, because it names nothing to falsify", () => {
  for (const inline of ["surfaces: []", "surfaces: 2", "surfaces: the dashboard"]) {
    const r = checkBriefScope({ text: brief(inline), config: SCOPE_CONFIG });
    assert.equal(r.result, "ERROR", `${inline} must not pass`);
    assert.match(r.why, /block list of named entries/);
  }
});

test("a surface without a path is a label, not a declaration", () => {
  // This is what stops "one surface: the dashboard" from being the way around the cap: with no path,
  // the CODE_REVIEW diff falsifier has nothing to compare the claim against.
  const r = checkBriefScope({ text: brief(["surfaces:", "  - name: the dashboard"].join("\n")), config: SCOPE_CONFIG });
  assert.equal(r.result, "ERROR");
  assert.equal(r.exit, 3);
  assert.match(r.why, /needs both a name and a path/);
});

test("a missing or nonsensical max_surfaces is ERROR, not an unlimited cap", () => {
  const text = brief(["surfaces:", SURFACE("a", "p1"), SURFACE("b", "p2"), SURFACE("c", "p3")].join("\n"));
  for (const thresholds of [{}, { max_surfaces: 0 }, { max_surfaces: "two" }, { max_surfaces: null }]) {
    const r = checkBriefScope({ text, config: { thresholds } });
    assert.equal(r.result, "ERROR", `${JSON.stringify(thresholds)} must not silently allow 3 surfaces`);
    assert.match(r.why, /max_surfaces/);
  }
});

test("the surfaces block ends at the front-matter terminator, so body text cannot inflate the count", () => {
  const text = ["---", "task_id: t1", "surfaces:", SURFACE("a", "p1"), "---", "", "## DEVELOP PLAN", "- step one", "- step two", "- step three", ""].join("\n");
  const r = checkBriefScope({ text, config: SCOPE_CONFIG });
  assert.equal(r.surfaces, 1, "the plan's bullet list must not be counted as surfaces");
  assert.equal(r.result, "PASS");
});

// ---------------------------------------------------------------------------
// C5: two reviewers, union of findings, mean ONLY inside the clean band (2026-09-04).
// The second test here is the anti-laundering assertion and the reason this change is safe to ship:
// a naive mean-of-overalls would average a real MAJOR away.

const clean = (overall) => ({ overall, security: overall, code_quality: overall, architecture: overall, documentation: overall });

test("two clean reviews merge to the mean and pass", () => {
  const m = mergeReviews([clean(9.6), clean(9.4)]);
  assert.equal(m.overall, 9.5);
  assert.equal(m.cap, null);
  assert.equal(m.reviewers_used, 2);
  assert.equal(m.spread, 0.2);
  assert.equal(decide({ step: "CODE_REVIEW", scores: m, config: CONFIG }).result, "PASS");
});

test("a clean 9.6 merged with a 6.0 carrying a MAJOR yields 6.0, NOT 7.8", () => {
  // THE anti-laundering case. A mean-of-overalls would return 7.8, which is still FIX at 9.5 today
  // and becomes a PASS the moment anyone moves a threshold. The cap comes from the UNION.
  const flawed = { ...clean(6.0), issues: [{ severity: "MAJOR", category: "code_quality", file: "src/a.ts", pattern: "silent catch swallows the error" }] };
  const m = mergeReviews([clean(9.6), flawed]);
  assert.equal(m.cap, 6, "one reviewer's MAJOR must cap the merged review");
  assert.ok(m.overall <= 6, `expected <= 6, got ${m.overall}`);
  assert.notEqual(m.overall, 7.8);
  assert.equal(decide({ step: "CODE_REVIEW", scores: m, config: CONFIG }).result, "FIX");
});

test("a CRITICAL from one reviewer alone escalates regardless of the composite", () => {
  const withCritical = { ...clean(9.7), issues: [{ severity: "CRITICAL", category: "security", file: "src/auth.ts", pattern: "token logged in plaintext" }] };
  const m = mergeReviews([clean(9.8), withCritical]);
  assert.equal(m.cap, 4);
  assert.equal(m.critical_security, true, "critical_security is the OR of both, derived not trusted");
  const d = decide({ step: "CODE_REVIEW", scores: m, config: CONFIG });
  assert.equal(d.result, "ESCALATE");
  assert.match(d.why, /critical security/);
});

test("one missing review uses the survivor unchanged, with reviewers_used 1 and no averaging", () => {
  const survivor = clean(9.6);
  for (const partner of [null, undefined, {}, { overall: "n/a" }, { overall: NaN }]) {
    const m = mergeReviews([survivor, partner]);
    assert.equal(m.reviewers_used, 1, `partner ${JSON.stringify(partner)} must not count as a reviewer`);
    assert.equal(m.overall, 9.6, "the survivor's score must not be diluted");
    assert.equal(m.spread, null, "spread between one reviewer and nothing is not a number");
  }
});

test("zero recoverable reviews is ERROR, never a low score", () => {
  const m = mergeReviews([null, undefined]);
  assert.equal(m.reviewers_used, 0);
  assert.equal(m.overall, undefined);
  assert.equal(decide({ step: "CODE_REVIEW", scores: m, config: CONFIG }).result, "ERROR");
});

test("the union dedupes on file and pattern, never on line number", () => {
  // Measured: the two reviewers reported the SAME defect at different lines. Keying on the line
  // would make two reports of one defect look like two disjoint findings.
  const a = [{ file: "src/a.ts", line: 88, pattern: "Silent catch swallows the error", severity: "MINOR" }];
  const b = [{ file: "src/a.ts", line: 140, pattern: "silent catch swallows the error", severity: "MAJOR" }];
  const u = unionFindings(a, b);
  assert.equal(u.length, 1, "one defect, reported twice");
  assert.equal(u[0].severity, "MAJOR", "the merge must never soften a severity either reviewer assigned");
  assert.equal(capFromFindings(u), 6);
});

test("disjoint findings compose to the union of caps", () => {
  const a = { ...clean(8.0), issues: [{ severity: "MINOR", category: "documentation", file: "x.ts", pattern: "no header" }] };
  const b = { ...clean(8.0), issues: [{ severity: "MAJOR", category: "security", file: "y.ts", pattern: "unparameterised query" }] };
  const m = mergeReviews([a, b]);
  assert.equal(m.findings.length, 2, "neither reviewer's finding may be dropped");
  assert.equal(m.cap, 6);
});

test("findings are collected from every shape the agents actually emit", () => {
  const nested = { overall: 7, categories: { security: { issues: [{ severity: "MAJOR", file: "s.ts", pattern: "leak" }] } } };
  assert.equal(collectFindings(nested).length, 1);
  assert.equal(collectFindings(nested)[0].category, "security", "the nesting must supply the category");
  assert.equal(collectFindings({ overall: 7 }).length, 0);
  assert.equal(collectFindings(null).length, 0);
});

test("per-dimension means are the mean of both, and the cap applies over them", () => {
  const a = { overall: 9.0, security: 10, code_quality: 9, architecture: 8, documentation: 9 };
  const b = { overall: 8.0, security: 8, code_quality: 8, architecture: 8, documentation: 7 };
  const m = mergeReviews([a, b]);
  assert.equal(m.security, 9);
  assert.equal(m.documentation, 8);
  // weighted: 9*30 + 8.5*30 + 8*25 + 8*15 = 270 + 255 + 200 + 120 = 845 / 100 = 8.45
  assert.equal(m.overall, 8.45);
  assert.equal(m.cap, null, "no severities reported, so nothing caps this");
});

test("iteration means the same thing on every result, so round 1 is selectable", () => {
  // WHY: it used to be the post-increment counter on FIX and the pre-increment iterationsUsed on
  // everything else. Measured in breather's live state.json, a CODE_REVIEW PASS carried iteration 1
  // and so did the FIRST FIX — so `iteration = 1` could not distinguish a round-1 PASS from the first
  // fix round, and qa/pipeline-artifacts.mjs's self-review mode was blind to exactly the runs that
  // went well. This pins one meaning: the 1-based number of the review the row records.
  const root = mkdtempSync(join(tmpdir(), "gate-iter-"));
  try {
    mkdirSync(join(root, ".aid/pipeline"), { recursive: true });
    writeFileSync(join(root, ".aid/pipeline/state.json"), JSON.stringify({ current_task_id: "t1", iterations: { code_review: 0 } }));
    const read = () => JSON.parse(readFileSync(join(root, ".aid/pipeline/state.json"), "utf8"));

    for (const overall of [6.0, 6.5]) {
      const d = decide({ step: "CODE_REVIEW", scores: { overall }, config: CONFIG, iterationsUsed: read().iterations.code_review });
      recordDecision(root, { step: "CODE_REVIEW", decision: d, scores: { overall } });
    }
    const pass = decide({ step: "CODE_REVIEW", scores: { overall: 9.6 }, config: CONFIG, iterationsUsed: read().iterations.code_review });
    recordDecision(root, { step: "CODE_REVIEW", decision: pass, scores: { overall: 9.6 } });

    const h = read().step_history;
    assert.deepEqual(h.map((x) => x.result), ["FIX", "FIX", "PASS"]);
    // Consecutive across results. The PASS is round 3, not round 2 (its pre-increment iterationsUsed).
    assert.deepEqual(h.map((x) => x.iteration), [1, 2, 3], "iteration must be a consecutive 1-based round number");
    assert.equal(h[0].task_id, "t1", "every entry names the task that produced it");
    assert.ok(h.every((x) => x.task_id === "t1"));
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
});
