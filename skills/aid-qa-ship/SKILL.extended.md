---
name: aid-qa-ship
description: AID Phase 5 - QA and Release phase guidance. Use this skill when validating implementations, running acceptance tests, preparing releases, deploying to production, or ensuring operational readiness. Final quality gate before shipping to users.
---

# QA & Ship Phase Skill

## Phase Overview

**Purpose**: Validate the implementation meets requirements, ensure production readiness, and ship with confidence.

**Entry Criteria**:
- Development phase completed and approved
- All developer tests passing
- Code reviewed
- Deployment environment available

**Exit Criteria**:
- All acceptance criteria verified
- No blocking bugs
- Production deployment successful
- Stakeholders informed

## Deliverables

### 1. Test Results
- **Description**: Comprehensive QA validation results
- **Format**: Test report with pass/fail status
- **Quality bar**: All acceptance criteria covered, realistic scenarios

### 2. Release Certification
- **Description**: Sign-off that system is ready for production
- **Format**: Checklist completion, stakeholder approvals
- **Quality bar**: All critical items verified

### 3. Release Notes
- **Description**: User-facing summary of changes
- **Format**: Structured changelog
- **Quality bar**: Clear, accurate, complete

### 4. Deployment
- **Description**: Production release
- **Format**: Deployed, verified application
- **Quality bar**: Smoke tests passing, monitoring active

## Role-Specific Guidance

### For Product Managers
- Perform acceptance testing
- Verify user experience
- Approve for release
- Communicate to stakeholders

### For Developers
- Fix reported bugs
- Support deployment
- Monitor initial release
- Address production issues

### For QA Engineers
- Execute test plan
- Report and verify bugs
- Validate fixes
- Sign off on quality

### For Tech Leads
- Verify operational readiness
- Approve deployment
- Ensure monitoring/alerting
- Lead incident response if needed

## Common Pitfalls

| Pitfall | Problem | Fix |
|---------|---------|-----|
| Rushing to ship | Quality gates bypassed | Respect the checklist |
| Testing in production | Users see bugs | Use staging/preview environments |
| Missing rollback plan | Stuck with broken release | Always have a way back |
| No monitoring | Can't detect problems | Set up monitoring first |
| Poor communication | Stakeholders surprised | Keep everyone informed |

## Cucumber Acceptance Verification

In Phase 5, QA validates that all acceptance criteria (Gherkin scenarios) pass before release.

### Verification Commands

| Step | Command | Expected Result | If Fails |
|------|---------|-----------------|----------|
| 1 | `npm run cucumber:dry` | No undefined steps | Implement missing step definitions |
| 2 | `npm run cucumber` | All scenarios pass | Debug failing scenarios |
| 3 | `npm run test:critical` | @critical scenarios pass | BLOCKER - must fix |
| 4 | `npm run test:bdd` | HTML report generated | Review `reports/cucumber-report.html` |

### Interpreting Results

**Passing Test Output:**
```
50 scenarios (50 passed)
150 steps (150 passed)
0m15.234s
```

**Failing Test Output:**
```
50 scenarios (48 passed, 2 failed)
150 steps (145 passed, 3 failed, 2 skipped)

Failures:
1) Scenario: User login with invalid credentials
   Step: Then I should see error "Invalid credentials"
   Error: Expected "Invalid credentials" but got "Login failed"
```

### What to Check in HTML Report

1. **Scenario Pass Rate** - Should be 100% for release
2. **Failed Scenarios** - Click to see step-by-step failure
3. **Pending Steps** - Yellow = not implemented (blocker)
4. **Duration** - Flag unusually slow scenarios
5. **Tags** - Verify no @wip or @skip in release

---

## Cucumber Verification Procedures

### Failure Investigation Workflow

1. **Identify failing scenario**
   ```bash
   npm run cucumber 2>&1 | grep -A 5 "failed"
   ```

2. **Run single scenario for debugging**
   ```bash
   npx --no-install cucumber-js features/auth/login.feature:15  # Line number
   ```

3. **Check step definition**
   - Is the step implemented?
   - Does it match the Gherkin exactly?
   - Are assertions correct?

4. **Check test data**
   - Is database in expected state?
   - Are test fixtures correct?
   - Is cleanup happening between scenarios?

### Flaky Test Detection

```bash
# Run 3 times to detect flaky tests
npm run cucumber && npm run cucumber && npm run cucumber

# Run with retry to identify flaky
npx --no-install cucumber-js --retry 2 --retryTagFilter @flaky
```

**If test is flaky:**
1. Tag with @flaky temporarily
2. Create bug ticket
3. Investigate timing/state issues
4. Remove @flaky when fixed

### Evidence Collection for Release

1. **Generate comprehensive report**
   ```bash
   npm run test:bdd
   ```

2. **Archive report**
   ```bash
   cp reports/cucumber-report.html docs/qa/release-v1.0.0-cucumber.html
   ```

3. **Screenshot key results**
   - Overall pass rate
   - Critical scenario results
   - Duration metrics

### Check for Forbidden Tags

```bash
# Must return no matches for release
grep -r "@wip\|@skip" features/ && echo "BLOCKED: Remove @wip/@skip tags"
```

### Release Certification Template

```markdown
## Cucumber Acceptance Test Results

**Release:** v1.0.0
**Date:** YYYY-MM-DD
**QA Engineer:** [Name]

### Results Summary
- Total Scenarios: XX
- Passed: XX (100%)
- Failed: 0
- Pending: 0

### Critical Scenarios (@critical)
- [ ] User login: PASS
- [ ] Payment processing: PASS
- [ ] Order creation: PASS

### Report Location
`docs/qa/release-v1.0.0-cucumber.html`

### Sign-off
[x] All acceptance criteria verified
[x] No blocking issues
[x] Approved for release
```

---

## Phase Gate Checklist

Before requesting approval to ship:

### Cucumber Acceptance Gates (MUST PASS) ⭐
- [ ] `npm run cucumber` exits with code 0
- [ ] `npm run test:critical` passes (all @critical scenarios)
- [ ] No undefined or pending step definitions
- [ ] HTML report generated and reviewed
- [ ] No @wip or @skip tags in release scenarios

### Quality Gates
- [ ] All acceptance criteria verified
- [ ] No blocking bugs open
- [ ] Performance validated
- [ ] Security review completed (if applicable)
- [ ] Rollback plan documented
- [ ] Monitoring and alerting configured
- [ ] Release notes prepared
- [ ] Stakeholder approval obtained
- [ ] Deployment instructions verified

### Agentic Release Gates (scaled by §1.5 level)
- [ ] Eval release gate passed on the held-out split (§7A.6 threshold, red-team, never-do)
- [ ] Shadow stage live
- [ ] Kill switch tested, including that the human queue can absorb 100% of the volume (or a throttle)
- [ ] Stage criteria agreed (§7A.8); later promotions are recorded 7A.8 owner decisions, outside the gate
- [ ] Monitoring live: quality drift, cost per successful task, escalation rate and response time, §1.4 guardrail metrics

## QA Testing Checklist

### Functional Testing
- [ ] All user stories verified
- [ ] All acceptance criteria tested
- [ ] Edge cases covered
- [ ] Error handling tested
- [ ] Cross-browser/device tested (if applicable)

### Non-Functional Testing
- [ ] Performance meets requirements
- [ ] Security scan passed
- [ ] Accessibility compliance checked
- [ ] Load testing completed (if applicable)

### Integration Testing
- [ ] All integrations verified
- [ ] API contracts honored
- [ ] Data flows correctly end-to-end
- [ ] Third-party dependencies working

## Release Process

### Pre-Release
1. Complete QA checklist
2. Get stakeholder sign-off
3. Prepare release notes
4. Verify rollback procedure
5. Schedule deployment window

### Deployment
1. Deploy to staging (final verification)
2. Run smoke tests
3. Deploy to production
4. Verify production smoke tests
5. Enable monitoring/alerting

### Post-Release
1. Monitor error rates and performance
2. Gather user feedback
3. Address critical issues immediately
4. Document lessons learned
5. Close out project artifacts

## Agentic Release (Eval Gate, Rollout, Monitoring)

WHY: an LLM component can pass every acceptance test and still drift, overspend or cross a red line
on live traffic. The eval gate proves it is good enough to start; the staged rollout earns autonomy
with evidence; monitoring catches decay; the kill switch limits the damage when something slips through.

Sources in the PRD: §1.4 Success Metrics (North Star, supporting, guardrail), §1.5 Solution Shape,
§7A.1 Charter, §7A.2 Tools & Permissions, §7A.4 Failure Modes & Guardrails, §7A.6 Eval Plan,
§7A.7 Telemetry & Traces, §7A.8 Rollout & Kill Switch.

### Scaling by level (never "N/A")

| Level | Release gate | Rollout | Stop mechanism | Monitoring |
|-------|--------------|---------|----------------|------------|
| 0 Process change | Process acceptance checks | Pilot with one team, then all | Revert to the old process | Process metrics + §1.4 guardrail |
| 1 Deterministic automation | Acceptance tests (Cucumber) | Staged release (canary or % rollout) | Tested rollback plan / feature flag | Errors, latency, §1.4 metrics |
| 2 Single LLM call | Eval gate on the call | Shadow → human approval (if output reaches users) → autonomous | Kill switch to a non-LLM fallback | Plus quality drift, cost |
| 3 Workflow | Eval gate per step + end-to-end | Shadow → human approval → autonomous | Kill switch per workflow | Plus per-step failure rates |
| 4 Agent | Plus tool-choice, never-do and red-team | Full three stages; shadow uses stubbed write tools; write tools approval-gated first | Kill switch revokes tool access | Plus escalation rate, tool-error rate |
| 5 Multi-agent | Plus hand-off evals | Stage each agent; the riskiest last | One switch stops all agents | Plus per-agent metrics |

### Eval release gate

Run on the exact versions that will ship (prompt, tool definitions, model, retrieval config).
QA owns the gate. **The release gate runs on the held-out split, which developers never tune on.**

Timing (A9, no relay): the seed eval cases were written in Phase 1 (`docs/prd/SEED-EVALS-<feature>.md`);
QA grew the golden set and its held-out split IN PARALLEL with Phases 2-4 (without blocking the tech spec);
this gate is the first point where they must be complete. The data scientist calibrated the judge in
Phase 4, when it was introduced.

- [ ] **Golden set:** complete (size and source per §7A.6), and ≥ the PRD's threshold, on the held-out split
- [ ] Score not lower than the last released version beyond the noise margin
- [ ] **Red-team:** 0 critical/high failures, plus an overall pass rate ≥ the PRD's target, including
      prompt-injection cases built from untrusted inputs (web pages, tickets, documents, tool results;
      see `rules/general/untrusted-content.md`)
- [ ] **Never-do:** enforced in code (policy, default-deny); evals verify the enforcement at 100%.
      Repeated runs cannot prove a low breach rate: proving a rate below p at 95% confidence takes
      n ≈ ln(0.05)/ln(1−p) clean runs (about 59 for 5%)
- [ ] **LLM judge,** if used: Cohen's kappa (or Krippendorff's alpha) ≥ 0.7 against adjudicated human
      labels on ≥ 50 stratified cases, including failures. Percent agreement is reported alongside, never alone
- [ ] The judge never grades the outputs of its own prompt or model, and the rubric is not visible to the system under test
- [ ] Eval report attached to the release certification, with versions and cost per successful task

A failed gate is a blocker, like a failed @critical scenario. The threshold is never lowered at
release time to make a build pass; changing it is a PRD change.

### Staged rollout (§7A.8 Rollout & Kill Switch)

| Stage | What it does | Entry criteria | Exit criteria |
|-------|--------------|----------------|---------------|
| 1. Shadow | Runs on real inputs; its actions are logged, not executed (at level 4, write tools are stubbed) | Eval gate passed; traces on (§7A.7); dashboards live | Agreement with human decisions at the agreement target in the §7A.8 agreement-target column, over the agreed volume; zero never-do breaches; cost and latency within budget (§1.5 Q5 / Section 9.7) |
| 2. Human approval | Proposes actions; a human approves each (or each write/irreversible one per §7A.2) | Shadow exit met; kill switch tested in this environment; approvers trained | Approval rate, override reasons, escalation rate and cost within §7A.8 targets for the agreed period; a blind audit of a sample of approved items finds no rubber-stamping; no unresolved guardrail breach |
| 3. Autonomous | Acts within §7A.2 permissions; escalates per §7A.1 | Approval exit met; kill switch tested again; on-call owner named; rollback rehearsed | No exit: stays under monitoring; any guardrail-metric breach triggers the kill switch or a step back to stage 2 |

Rules:
- **Phase 5 exit:** the eval release gate passed, shadow stage live, kill switch tested, and the stage
  criteria agreed. Each later promotion (human approval → autonomous) is a recorded decision by the
  7A.8 owner, outside the phase gate, with the evidence (numbers, trace samples).
- Human approval stage: run a blind audit of a sample of approved items (a second reviewer grades
  them without seeing the approver's decision) to catch approvers who approve without checking.
- Irreversible or high-risk tools (§7A.2) stay human-approved longer, or permanently, if §7A.8 says so.
- Stepping back a stage is normal, not a failure.

### Kill switch test (before autonomy)

- [ ] The switch exists as described in §7A.8 and the tech spec (flag, config, or permission revoke)
- [ ] Triggered in a test: the agent stops acting within the agreed time
- [ ] The fallback works (human queue, previous version or non-LLM path); no work is lost
- [ ] The human queue can absorb 100% of the volume, or a throttle limits intake to what it can absorb
- [ ] In-flight runs end safely (no half-done irreversible action)
- [ ] The on-call owner can trigger it without a deploy, and knows when to
- [ ] Test date, who ran it and the result are recorded in the release certification

### Production monitoring

| Signal | How | Alert when |
|--------|-----|------------|
| Quality drift | Run the eval rubric or judge on a sample of live traces; compare with the release score | Below the §7A.6 threshold or a sustained drop |
| Cost | Cost per *successful* task (total spend / tasks with `outcome: success`) and per day, from traces | Above the budget in §1.5 Q5 / Section 9.7 |
| Latency | P50/P95 from traces | Above budget (§1.5 Q5 / Section 9.7) |
| Escalation rate | Escalations per run (§7A.1) | Outside the expected band, up or down (too few can mean missed escalations) |
| Escalation response time | Time from escalation to human pick-up | Above the §7A.1 escalation SLA |
| Guardrail metrics (§1.4) | As defined in the PRD | Breach: kill switch or step back a stage |
| Never-do breaches | Rule checks on traces | Any breach: kill switch, incident |
| Injection attempts | Flags from guardrails (§7A.4) | Spike |

**Offline vs online evals.** Offline evals run the golden set and red-team suite before release.
Online evals score live traces; name each online label source and its lag (for example: judge on
sampled traces, minutes; human review of escalations, about a day; customer complaints or
chargebacks, weeks). Alert on the fast sources; confirm with the slow ones.

Every alert has an owner and a runbook. New failure modes found in production become new golden-set
or red-team cases (feeding the §7A.6 Eval Plan; QA merges them) before the fix ships.

### Level 0-1 checklist (classic form)

- [ ] Acceptance tests pass (the eval gate)
- [ ] Staged release (pilot, canary or % rollout) with go/no-go criteria per step
- [ ] Rollback plan written and tested
- [ ] Monitoring for errors, latency and the §1.4 metrics, including at least one guardrail metric

## Release Notes Template

```markdown
# Release Notes - [Feature Name]
**Date**: YYYY-MM-DD
**Version**: X.Y.Z

## What's New
- [Feature 1]: [Brief description]
- [Feature 2]: [Brief description]

## Improvements
- [Improvement 1]
- [Improvement 2]

## Bug Fixes
- [Fix 1]: [What was fixed]
- [Fix 2]: [What was fixed]

## Known Issues
- [Issue 1]: [Workaround if any]

## Notes
[Any important information for users]
```

## Post-Ship Activities

After deployment:
- Monitor error rates and performance
- Gather user feedback
- Document lessons learned
- Update documentation if needed
- Close out project artifacts
- Collect feedback via `/aid-end`

---

## Learning Mode Integration

### Decision Transparency Triggers
- **Test coverage decisions**: Show reasoning for coverage targets
- **Release timing**: Explain why releasing now vs waiting
- **Bug severity classification**: Show why bugs are blocking/non-blocking
- **Rollback decisions**: Document criteria for rollback

### Debate Invitations
- **Test strategy**: When coverage trade-offs have significant impact
- **Release scope**: When partial release is an option
- **Bug triage**: When severity classification is unclear

### Feedback Requests
- After test execution: Validate coverage completeness
- Before release: Confirm stakeholder readiness
- After deployment: Overall release quality rating (1-5)

### Example Transparency Block
```markdown
<decision-transparency>
**Decision:** Proceeding with release despite 2 minor UI bugs

**Reasoning:**
- **User impact**: Bugs are cosmetic, don't affect core functionality
- **Business timing**: Marketing campaign starts Monday
- **Fix timeline**: Bugs can be fixed in patch release this week

**Alternatives Considered:**
1. Delay release - Rejected: Minor bugs don't justify missing campaign
2. Disable affected features - Rejected: Features work, just minor visual issues

**Confidence:** High - Clear separation between blocking and non-blocking issues

**Open to Debate:** Yes - If stakeholders prefer waiting, we can discuss
</decision-transparency>
```

### Example Debate Invitation
```markdown
<debate-invitation>
**Topic:** Test strategy for checkout flow

**Option A: Heavy E2E Coverage**
- ✅ Pros: Tests what users actually do, highest confidence
- ❌ Cons: Slow CI, more brittle, expensive to maintain

**Option B: Testing Trophy (Balanced)**
- ✅ Pros: Fast CI, comprehensive, maintainable
- ❌ Cons: E2E gaps possible

**My Lean:** Option B - 40% unit, 40% integration, 20% E2E critical paths

**Your Input Needed:** What's acceptable CI pipeline time? How critical is checkout?
</debate-invitation>
```
