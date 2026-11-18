# PRD Template Extended Reference

Complete PRD template with all sections, examples, and guidance.

## Full PRD Template

```markdown
# [Feature/Product Name] PRD

**Document Version**: 1.0
**Created**: [Date]
**Last Updated**: [Date]
**Author**: [Name]
**Status**: Draft | In Review | Approved

---

## Document References

| Document | Link |
|----------|------|
| Research Report | [Link to docs/research/YYYY-MM-DD-[project]/research-report.md] |
| Traceability Matrix | [Link to docs/research/YYYY-MM-DD-[project]/traceability-matrix.md] |
| Discovery Phase | [Link if applicable] |
| WHY + Shape Brief | [Link to docs/prd/WHY-SHAPE-BRIEF-<feature>.md] |
| Seed Evals | [Link to docs/prd/SEED-EVALS-<feature>.md] |
| Level ADR | [Link to docs/prd/ADR-SHAPE-<feature>.md] |
| Related PRDs | [Links to related PRDs] |

---

## 1. Executive Summary

### 1.1 Purpose
[One paragraph explaining what this document covers and why it exists]

### 1.2 Problem Statement
**Research Backing**: [PROJECT]-A-INT-XXX, [PROJECT]-A-JTBD-XXX

[Concise description of the problem being solved. Should be user-focused.]

**User Pain Points** (from research):
1. [Pain point 1] - Source: [PROJECT]-A-INT-XXX
2. [Pain point 2] - Source: [PROJECT]-A-INT-XXX
3. [Pain point 3] - Source: [PROJECT]-A-JTBD-XXX

### 1.3 Solution Overview
[Brief description of the proposed solution - high level, not technical]

### 1.4 Success Metrics
**Research Backing**: [PROJECT]-C-OPP-XXX

Every metric set has one North Star, its supporting metrics, and at least one guardrail metric.

| Type | Metric | Current State | Target | Timeline |
|------|--------|--------------|--------|----------|
| North Star | [The one outcome that shows users get value] | [Baseline] | [Goal] | [When] |
| Supporting | [A driver of the North Star] | [Baseline] | [Goal] | [When] |
| Supporting | [Another driver] | [Baseline] | [Goal] | [When] |
| Guardrail | [What must NOT get worse, e.g. error rate, complaints, cost per successful task, wrong actions] | [Baseline] | [Limit not to cross] | [When] |

- **North Star:** one metric only; it moves when users get the value promised in §1.2.
- **Supporting:** the levers that move the North Star; useful for diagnosis.
- **Guardrail (at least one, REQUIRED):** a limit that stops you from "winning" the North Star by causing harm. Crossing it blocks the release or triggers the kill switch (§7A.8).
- **Cost:** state it per *successful* task (total cost ÷ tasks completed correctly), not just per run; retries, escalations and failed runs count against it.

### 1.5 Solution Shape
**Rule:** pick the LOWEST level that works, and justify every step up in one sentence.

**Solution-shape ladder:**

| Level | Shape |
|---|---|
| 0 | Process change (no software) |
| 1 | Deterministic automation |
| 2 | Single LLM call inside a fixed flow |
| 3 | Workflow (several fixed steps, some with LLM calls) |
| 4 | Agent (the model chooses the path and the tools) |
| 5 | Multi-agent |

**Intake questions** (answer all six; the answers recommend a level):

| # | Question | Answer | Points toward |
|---|----------|--------|---------------|
| 1 | Can every path be enumerated in advance? | [Yes/No + example] | Yes → 0-1; No → 3-4 |
| 2 | How much does the problem vary from case to case? | [Low/Medium/High + example] | Low → 0-2; High → 3-4 |
| 3 | What does an error cost, and is it reversible? | [Cost + who pays + reversible?] | High or irreversible → lower level or human approval |
| 4 | Does it need judgement over unstructured input? | [Yes/No + input type] | No → 0-1; Yes → 2+ |
| 5 | What latency and cost budget is there? | [p95 latency, cost per case] | Tight → lower level |
| 6 | Who must approve actions? | [Role, or "none"] | Approval needed → human in the loop (§7A.8) |

**Chosen level:** [0-5] - [Shape name]

Signed level: [n] - by [tech lead], [date], ADR link (`docs/prd/ADR-SHAPE-<feature>.md`)
<!-- The solution-shaper's draft says PROPOSED here; the tech lead signs it after the shaping session. -->

**Justification for each step above level 0** (one sentence each; delete the rows above your level):

| Step | Why the lower level is not enough |
|------|----------------------------------|
| 0 → 1 | [Why a process change alone does not solve it] |
| 1 → 2 | [Why fixed rules cannot handle the input, e.g. free-text judgement] |
| 2 → 3 | [Why one LLM call is not enough, e.g. several dependent steps] |
| 3 → 4 | [Why the path cannot be fixed in advance, so the model must choose steps and tools] |
| 4 → 5 | [ONE of: separate permission boundaries; contexts that would contaminate each other; genuinely parallel work; ownership by different teams] |

Multi-agent (level 5) is justified ONLY by one of those four reasons. "It is cleaner" or "it is more advanced" is not a justification.

**Per part (optional):** a product may use different levels for different parts. List each part with its level, e.g. "proactive alert: level 1; diagnosis: level 4; refund: level 0, human only".

---

## 2. Background & Context

### 2.1 Current State
[Description of how things work today]

### 2.2 User Research Summary
**Sources**: [PROJECT]-A-INT-XXX through XXX

**Key Findings**:
1. [Finding 1]
2. [Finding 2]
3. [Finding 3]

**User Quotes**:
> "[Direct quote from research]" - [Persona type]
> "[Direct quote from research]" - [Persona type]

### 2.3 Competitive Landscape
**Sources**: [PROJECT]-A-COMP-XXX

| Competitor | Strengths | Weaknesses | Our Differentiation |
|------------|-----------|------------|---------------------|
| [Competitor 1] | | | |
| [Competitor 2] | | | |

### 2.4 Business Context
- Strategic alignment: [How this fits company strategy]
- Market opportunity: [Size/impact]
- Timing considerations: [Why now]

---

## 3. User Personas

### 3.1 Primary Persona: [Name]
**Research Backing**: [PROJECT]-A-INT-XXX

| Attribute | Description |
|-----------|-------------|
| Role | [Job title/role] |
| Demographics | [Relevant demographics] |
| Goals | [What they want to achieve] |
| Frustrations | [Current pain points] |
| Tech Savviness | [Low/Medium/High] |
| Usage Frequency | [How often they'd use this] |

**Jobs to be Done**:
- When [situation], I want to [motivation], so I can [outcome]

### 3.2 Secondary Persona: [Name]
**Research Backing**: [PROJECT]-A-INT-XXX

[Same structure as primary]

### 3.3 Anti-Persona: [Who This Is NOT For]
[Description of users explicitly NOT targeted]

---

## 4. User Stories

### 4.1 Epic: [Epic Name]
**Research Backing**: [PROJECT]-C-OPP-XXX

#### US-001: [Title]
**Research Backing**: [PROJECT]-A-INT-XXX, [PROJECT]-B-IDEA-XXX

**As a** [persona]
**I want** [capability]
**So that** [benefit]

**Acceptance Criteria:**
- [ ] Given [context], when [action], then [outcome]
- [ ] Given [context], when [action], then [outcome]
- [ ] Given [error condition], when [action], then [error handling]

**Priority**: Must Have
**Complexity**: M

---

#### US-002: [Title]
**Research Backing**: [PROJECT]-A-XXX OR ASSUMPTION - [rationale]

**As a** [persona]
**I want** [capability]
**So that** [benefit]

**Acceptance Criteria:**
- [ ] Given [context], when [action], then [outcome]

**Priority**: Should Have
**Complexity**: S

---

### 4.2 Epic: [Epic Name]
[Continue with more user stories...]

---

## 5. Scope Definition

### 5.1 In Scope (Phase 1)
| Feature | Description | Research Backing | Priority |
|---------|-------------|------------------|----------|
| [Feature 1] | [Brief description] | [PROJECT]-XXX | Must Have |
| [Feature 2] | [Brief description] | [PROJECT]-XXX | Must Have |
| [Feature 3] | [Brief description] | [PROJECT]-XXX | Should Have |

### 5.2 Out of Scope (Phase 1)
| Feature | Research Backing | Rationale | Future Phase |
|---------|------------------|-----------|--------------|
| [Feature A] | [PROJECT]-XXX | [Why deferred] | Phase 2 |
| [Feature B] | [PROJECT]-XXX | [Why excluded] | TBD |
| [Feature C] | N/A | Stakeholder decision | Phase 2 |

### 5.3 Scope Risks
| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Scope creep from [area] | Medium | High | Strict change control |
| [Risk 2] | | | |

---

## 6. Functional Requirements

### 6.1 [Feature Area 1]

#### FR-001: [Requirement Title]
**Research Backing**: [PROJECT]-XXX

**Description**: [Detailed requirement description]

**Business Rules**:
1. [Rule 1]
2. [Rule 2]

**Data Requirements**:
- Input: [Data inputs needed]
- Output: [Data outputs produced]
- Validation: [Validation rules]

**User Interface**:
- [UI requirement 1]
- [UI requirement 2]

#### FR-002: [Requirement Title]
[Continue pattern...]

---

## 7. Non-Functional Requirements

### 7.1 Performance
| Requirement | Target | Measurement |
|-------------|--------|-------------|
| Page load time | < 2 seconds | P95 latency |
| API response time | < 500ms | P95 latency |
| Concurrent users | 1000+ | Load testing |

### 7.2 Security
- [ ] Authentication: [Requirements]
- [ ] Authorization: [Requirements]
- [ ] Data encryption: [Requirements]
- [ ] Compliance: [GDPR, SOC2, etc.]

### 7.3 Accessibility
- [ ] WCAG 2.1 AA compliance
- [ ] Keyboard navigation
- [ ] Screen reader support

### 7.4 Scalability
- [Scalability requirements]

### 7.5 Reliability
- Uptime target: [99.9%]
- Recovery time objective: [RTO]
- Recovery point objective: [RPO]

### 7.6 Observability
- Logs: [Events and errors recorded]
- Metrics and alerts: [§1.4 metrics, error rate, throughput; who is alerted]

---

## 7A. Agentic Design

Fill EVERY subsection for EVERY project, at a depth scaled to the §1.5 level. No subsection may be "N/A": at levels 0-1 each one takes its classic form (see each "Scaling by level" note).

**Three tiers of depth** (reviewers use these tiers): **levels 0-1** (no LLM: classic form), **levels 2-3** (LLM calls inside a fixed flow or workflow), **levels 4-5** (agent or multi-agent: the full section).

**Levels 0-1 cross-reference.** A section is still never "N/A", but at levels 0-1 it may be one line pointing to where it is already covered (e.g. "7A.6: covered by §4 Gherkin ACs + negative tests"; "7A.7: see §7 NFR observability"). Reviewers score that as fully met.

### 7A.1 Charter

| Item | Answer |
|------|--------|
| Goal | [The outcome it delivers, linked to the §1.4 North Star] |
| On whose behalf it acts | [User / customer / company / team] |
| Who bears the error | [Who pays when it is wrong, and how much] |
| Autonomy level | [§1.5 level, and the current §7A.8 stage: shadow / human approval / autonomous] |
| NEVER do | [Hard list, e.g. move money, delete data, promise refunds, share personal data] |
| Escalates to a human when | [Triggers: low confidence, never-do request, high-value case, angry user, repeated failure] |
| Escalates to | [Role or queue, and the escalation response-time SLA (monitored in §7A.7 and §7A.8)] |

**Scaling by level:**
- **0-1:** the process owner, who bears an error, the steps the process must never skip, and who handles exceptions. Or one line pointing to where it is covered (e.g. "7A.1: see §2.1 process owner and §10 constraints"); scored as fully met.
- **2-3:** as above, plus what the LLM step may and may not decide, and when its output goes to a human.
- **4-5:** the full charter; the never-do list and escalation triggers are binding and are tested in §7A.6.

### 7A.2 Tools & Permissions

| Tool / system | What it does | Read or write | Reversible? | Needs human approval? | Scope (least privilege) |
|---------------|--------------|---------------|-------------|-----------------------|-------------------------|
| [Tool 1] | [Purpose] | Read | n/a | No | [Only fields/records needed] |
| [Tool 2] | [Purpose] | Write | Yes / No | Yes / No | [Limits: amount, rate, records] |

Rule: least privilege. Every irreversible write needs human approval or is on the §7A.1 never-do list.

**Scaling by level:**
- **0-1:** the systems and roles the process touches, with their access rights (who may read, who may change). Or one line pointing to where it is covered (e.g. "7A.2: see §7.2 authorization"); scored as fully met.
- **2-3:** the data each LLM step reads; LLM steps usually get no write tools, and fixed code does the writes.
- **4-5:** every tool the model may call, with a risk tag; per-agent tool lists for level 5.

### 7A.3 Context & Data

| Item | Answer |
|------|--------|
| What it can see | [Sources, documents, records, user input] |
| Personal data | [Which fields, legal basis, masking] |
| Secrets & credentials | [Never placed in prompts, traces, eval sets or seed cases; how they are redacted or referenced] |
| Financial data | [Which fields, limits] |
| Memory | [None / per session / per user / long-term; what is stored] |
| Retention | [How long inputs, outputs and traces are kept; deletion] |
| Untrusted input | [Which inputs come from users or third parties] |
| Model-provider data handling | [Provider retention period, zero-data-retention (yes/no), training opt-out, processing region; the contract or setting that guarantees it] |

**Scaling by level:**
- **0-1:** the data the process uses, who can see it, and how long it is kept. Or one line pointing to where it is covered (e.g. "7A.3: see §7.2 security and §10.3 regulatory"); scored as fully met.
- **2-3:** what goes into each prompt, and what is masked before it is sent to a model.
- **4-5:** everything the agent can retrieve or remember, per-agent context boundaries, and memory rules.

### 7A.4 Failure Modes & Guardrails

| Failure mode | Example | Impact | Guardrail (prevent or detect) |
|--------------|---------|--------|-------------------------------|
| [Wrong answer / hallucination] | [Example] | [Who is hurt, how] | [Grounding check, citation required] |
| [Wrong action] | [Example] | | [Approval, limits, undo] |
| [Prompt injection] | [Instruction hidden in an email, ticket or page] | | [Treat as data, no tool calls from untrusted text] |
| [Loop / runaway cost] | | | [Step and cost caps] |

**Red lines** (stop and escalate immediately): [list; includes the §7A.1 never-do list]

**Prompt-injection exposure:** [Which inputs are untrusted and what they could make it do]. Follow `rules/general/untrusted-content.md`: content from outside is data, never instructions.

**Data-exfiltration "lethal trifecta":** check whether the system has all three of: (1) access to private data; (2) exposure to untrusted content; (3) an external communication channel (outbound tools such as email, HTTP or webhooks, or URLs and markdown images in its output that a client may fetch). [Present / not present, per leg]. If all three are present, remove one leg, or require human approval on every outbound action.

**Scaling by level:**
- **0-1:** classic failure modes (bad input, missed step, system down) and their controls (validation, checklists, alerts). Or one line pointing to where it is covered (e.g. "7A.4: see §11 risks and §4 error scenarios"); scored as fully met.
- **2-3:** add LLM failures (wrong output, format errors, hallucination) and output checks.
- **4-5:** add wrong tool use, loops, prompt injection and cross-agent errors, with guardrails enforced outside the model.

### 7A.5 Why-Chain

Every stated WHY becomes a requirement, an eval that tests it, and a metric that tracks it in production.

| WHY (from research / §1.2) | Requirement | Eval (§7A.6) | Metric (§1.4) |
|----------------------------|-------------|--------------|---------------|
| [WHY 1] - Source: [ID] | [FR-XXX / US-XXX] | [Eval case or set] | [Metric, type] |
| [WHY 2] | | | |

Rule: **a WHY that yields none of the three is an opinion, not a requirement.** Remove it, or turn it into an open question (§12).

**Scaling by level:**
- **0-1:** WHY → requirement → acceptance test → business metric. Or one line pointing to where it is covered (e.g. "7A.5: see §13 traceability summary"); scored as fully met.
- **2-3:** WHY → requirement → eval cases for the LLM steps → quality metric.
- **4-5:** WHY → requirement → eval cases including never-do and adversarial cases → production quality and guardrail metrics.

### 7A.6 Eval Plan

| Item | Answer |
|------|--------|
| Golden set | [Size, source (real cases / experts / synthetic), refresh cadence; QA owns it and its held-out split] |
| Adversarial and red-team cases | [How generated, count; injection, abuse, edge cases; severity per case] |
| Never-do checks | [One check per §7A.1 never-do item; verifies the enforcement in code at 100%] |
| Scoring | [Exact match / rubric / human review / LLM-as-judge] |
| Pass threshold (release gate) | [Golden set >= [X]%; never-do enforcement verified at 100%; red-team 0 critical/high failures and overall pass rate >= [Y]%] |
| LLM-as-judge calibration | [If a judge is used: Cohen's kappa (or Krippendorff's alpha) >= 0.7 against adjudicated human labels on >= 50 stratified cases, including failures; percent agreement reported alongside; re-checked when the judge, rubric or prompt changes] |
| Offline evals | [Golden set, held-out split, red-team, never-do: run pre-release and on every change to prompt, model, tools] |
| Online evals | [In production: a human review sample (rate), user feedback, delayed outcomes (e.g. complaint, reopen, chargeback) with their lag] |
| When it runs | [Every change to prompt, model, tools; before each §7A.8 stage] |

The pass threshold is the release gate: below it, nothing ships or moves to the next rollout stage. The release gate runs on the held-out split, which developers never tune on; developers iterate on a separate dev/targeted suite and propose golden-set additions through a QA-reviewed PR.

**Canonical thresholds:**
- **Never-do:** enforced in code (policy, default-deny); evals verify the enforcement at 100%. Repeated runs cannot prove a low breach rate: proving a rate below p at 95% confidence takes n ≈ ln(0.05)/ln(1−p) clean runs (about 59 for 5%).
- **Red-team:** 0 critical/high failures, plus an overall pass rate ≥ the PRD's target.
- **Golden set:** ≥ the PRD's threshold.
- **LLM judge:** Cohen's kappa (or Krippendorff's alpha) ≥ 0.7 against adjudicated human labels on ≥ 50 stratified cases, including failures. Percent agreement is reported alongside, never alone.
- The judge never grades the outputs of its own prompt or model, and the rubric is not visible to the system under test.

**Offline vs online evals:** offline evals (the golden set, pre-release) decide the release gate; online evals (production: a human review sample, user feedback, delayed outcomes, with their lag) show whether quality holds on live traffic and feed the §7A.8 exit criteria. At level 4, shadow mode uses stubbed write tools that return simulated results, so the agent's full path runs without side effects.

**Scaling by level:**
- **0-1:** acceptance tests (the Gherkin scenarios) plus negative tests for the "never" rules; the gate is "all pass". Or one line, e.g. "7A.6: covered by §4 Gherkin ACs + negative tests"; scored as fully met.
- **2-3:** a golden set for each LLM step, format checks, a few adversarial cases, and a threshold.
- **4-5:** the full plan: golden set, generated red-team cases, never-do checks, judge calibration, offline and online evals, and a gate per rollout stage.

### 7A.7 Telemetry & Traces

Trace by default. Each run records:

| Field | Recorded |
|-------|----------|
| Plan | [The steps it chose or followed] |
| Tool calls | [Tool, inputs, outputs, errors] |
| Results | [Final output, confidence] |
| Escalations | [When, why, to whom] |
| Cost | [Tokens / money per run, and per *successful* task] |
| Latency | [Per step and total] |

Dashboards and alerts: [§1.4 metrics, guardrail metrics, escalation rate, escalation response time against the 7A.1 SLA, cost per successful task]. Retention follows §7A.3. Traces redact personal data and never contain secrets or credentials.

**Scaling by level:**
- **0-1:** logs and metrics: events, errors, throughput, the §1.4 metrics. Or one line, e.g. "7A.7: see §7 NFR observability"; scored as fully met.
- **2-3:** add prompt and model version, input and output, cost and latency per LLM call.
- **4-5:** a full trace per run (plan, every tool call, results, escalations), linked across agents for level 5.

### 7A.8 Rollout & Kill Switch

Stages are exactly "shadow → human approval → autonomous".

| Stage | What happens | Entry criteria | Exit criteria | Agreement target |
|-------|--------------|----------------|---------------|------------------|
| 1. Shadow | Runs on real input; output is logged, not used (level 4: write tools stubbed, returning simulated results) | §7A.6 gate passed | [e.g. N cases, quality >= threshold, no red-line hit] | [Agreement with what humans actually did, e.g. >= X%] |
| 2. Human approval | Proposes; a human approves each action | Shadow exit met | [e.g. agreement target met for N weeks, blind audit passed, guardrails held] | [Share of proposals approved unedited, e.g. >= X%] |
| 3. Autonomous | Acts alone within §7A.2 limits; samples reviewed | Approval exit met + kill switch tested | [Ongoing: guardrails held, online evals hold; else roll back a stage] | [Sampled review agreement >= X%] |

**Against rubber-stamping:** in the human-approval stage, a blind audit re-reviews a sample of approved items ([N] per week, by a reviewer who does not see the original decision); if the audit disagrees with approvals above [X]%, the stage does not exit.

**Phase 5 exit vs rollout:** the Phase 5 exit requires: the eval release gate passed, shadow stage live, kill switch tested, and the stage criteria agreed. Each later promotion (human approval → autonomous) is a recorded decision by the 7A.8 owner, outside the phase gate.

| Item | Answer |
|------|--------|
| Kill switch | [How to turn it off, who may, how fast; what takes over (human queue / previous version)] |
| Rollback trigger | [Guardrail crossed, red line hit, eval regression] |
| Human-queue capacity | [When the kill switch degrades to humans, can the queue absorb 100% of the volume? If not, the throttle or backlog plan] |
| Escalation SLA | [The 7A.1 escalation response time, monitored with an alert when breached] |
| On-call owner | [Name / rotation] |
| Promotion decisions | [Where the 7A.8 owner records each promotion decision, with date and evidence] |

**Scaling by level:**
- **0-1:** a staged release (pilot group, then everyone) plus a tested rollback; the kill switch is a feature flag or reverting to the old process. Or one line pointing to where it is covered (e.g. "7A.8: see §7.5 reliability, release plan and rollback"); scored as fully met.
- **2-3:** shadow → human approval → autonomous for the LLM steps; a flag that falls back to the non-LLM path.
- **4-5:** all three stages with explicit entry and exit criteria, a tested kill switch before autonomy, and an on-call owner.

---

## 8. Dependencies

### 8.1 Internal Dependencies
| Dependency | Owner | Status | Impact if Delayed |
|------------|-------|--------|-------------------|
| [API from Team X] | [Owner] | In Progress | Blocks checkout |
| [Design system] | [Owner] | Complete | - |

### 8.2 External Dependencies
| Dependency | Vendor | Status | Contingency |
|------------|--------|--------|-------------|
| [Payment provider] | [Vendor] | Contracted | [Backup option] |
| [Third-party API] | [Vendor] | Evaluating | [Alternative] |

### 8.3 Technical Dependencies
- [Infrastructure requirement]
- [Platform requirement]

---

## 9. Assumptions Log

| ID | Assumption | Risk if Wrong | Validation Plan | Status |
|----|------------|---------------|-----------------|--------|
| ASSUME-001 | [Assumption] | [Impact] | [How to validate] | Open |
| ASSUME-002 | [Assumption] | [Impact] | [How to validate] | Validated |
| ASSUME-003 | [Assumption] | [Impact] | [How to validate] | Invalid |

---

## 10. Constraints

### 10.1 Business Constraints
- Budget: [Budget limitations]
- Timeline: [Hard deadlines]
- Resources: [Team limitations]

### 10.2 Technical Constraints
- Must use existing [technology/platform]
- Must integrate with [system]
- Cannot change [component]

### 10.3 Regulatory Constraints
- [Compliance requirement 1]
- [Compliance requirement 2]

---

## 11. Risks & Mitigations

| ID | Risk | Likelihood | Impact | Mitigation | Owner |
|----|------|------------|--------|------------|-------|
| RISK-001 | [Risk description] | High/Med/Low | High/Med/Low | [Mitigation plan] | [Name] |
| RISK-002 | [Risk description] | | | | |

---

## 12. Open Questions

| ID | Question | Owner | Due Date | Resolution |
|----|----------|-------|----------|------------|
| Q-001 | [Question] | [Name] | [Date] | [Pending/Resolved: answer] |
| Q-002 | [Question] | [Name] | [Date] | |

---

## 13. Traceability Summary

### 13.1 Research → Requirements Coverage

| Research Type | Total Findings | Used in PRD | Deferred | Excluded |
|---------------|----------------|-------------|----------|----------|
| Interviews (A-INT) | X | X | X | X |
| Competitive (A-COMP) | X | X | X | X |
| JTBD (A-JTBD) | X | X | X | X |
| Ideas (B-IDEA) | X | X | X | X |
| Root Causes (B-ROOT) | X | X | X | X |
| Opportunities (C-OPP) | X | X | X | X |

### 13.2 Requirements → Research Coverage

| Requirement Type | Total | With Research Backing | Assumptions |
|------------------|-------|----------------------|-------------|
| User Stories | X | X | X |
| Acceptance Criteria | X | X | X |
| Functional Requirements | X | X | X |
| Success Metrics | X | X | X |

### 13.3 Traceability Gaps
- [Any findings not yet addressed]
- [Any requirements without backing]

---

## 14. Appendices

### Appendix A: Glossary
| Term | Definition |
|------|------------|
| [Term 1] | [Definition] |
| [Term 2] | [Definition] |

### Appendix B: Related Documents
- [Link to designs]
- [Link to technical spec]
- [Link to research data]

### Appendix C: Revision History
| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | [Date] | [Name] | Initial version |
| 1.1 | [Date] | [Name] | [Changes] |

---

## Approval Sign-off

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Product Manager | | | |
| Tech Lead | | | |
| Design Lead | | | |
| QA Lead | | | |
| Data Scientist | | | |
| Stakeholder | | | |
```

---

## Section-by-Section Guidance

### Executive Summary
- Write last, summarize first
- Keep to one page
- Include key numbers
- Make it scannable

### Success Metrics (§1.4)
- One North Star, a few supporting metrics, at least one guardrail
- Each guardrail has a limit that blocks release or triggers rollback

### Solution Shape (§1.5)
- Answer the six intake questions before choosing a level
- Pick the lowest level that works; one sentence per step up
- Level 5 only with one of the four multi-agent justifications

### Agentic Design (§7A)
- Fill all eight subsections, scaled to the §1.5 level; never "N/A"
- Charter never-do items reappear as §7A.6 never-do checks
- Every Why-Chain row names a requirement, an eval and a metric

### User Stories
- Link every story to research
- Use INVEST criteria
- Include error cases
- Size appropriately (S/M/L)

### Scope Definition
- Be explicit about exclusions
- Document rationale for decisions
- Link to research for both in/out

### Assumptions Log
- Never hide assumptions
- Rate risk impact
- Plan validation before build
- Track status

### Traceability Summary
- Update after each change
- Identify gaps
- Ensure bidirectional links
- No orphan items

---

## Quality Checklist

Before PRD approval:

```
Executive Summary
☐ Problem statement is clear and user-focused
☐ Success metrics are measurable
☐ Solution overview is implementation-agnostic
☐ Metric set has a North Star, supporting metrics and at least one guardrail
☐ §1.5 Solution Shape: six intake questions answered, level chosen, each step up justified

Agentic Design (§7A)
☐ §7A.1-7A.8 all filled at the depth of the chosen level, none "N/A"
☐ Charter names who bears the error, never-do items and escalation
☐ Every WHY in the §7A.5 Why-Chain has a requirement, an eval and a metric
☐ §7A.6 pass threshold set as the release gate
☐ §7A.8 stages have entry/exit criteria, a kill switch and an on-call owner

Research Integration
☐ All key findings referenced
☐ Research IDs linked correctly
☐ Quotes attributed to personas

User Stories
☐ Follow "As a... I want... So that..." format
☐ Each has testable acceptance criteria
☐ Research backing or assumption flag present
☐ Priority and complexity assigned

Scope
☐ In-scope items clearly listed
☐ Out-of-scope items explicitly stated
☐ Rationale provided for exclusions

Dependencies & Risks
☐ All dependencies identified with owners
☐ Risks assessed with mitigations
☐ Open questions tracked

Traceability
☐ Forward trace complete (research → requirements)
☐ Backward trace complete (requirements → research)
☐ No broken links
☐ Coverage summary accurate

Sign-off
☐ All required approvals obtained
☐ Version history updated
☐ Distributed to stakeholders
```
