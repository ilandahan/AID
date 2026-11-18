# AID Implementation Plan - Extended Guide (Phase 3)

> Detailed guidance for the consolidation-first approach: resolve contradictions, break down tasks, and populate Jira with complete information.

---

## Phase 3a: Consolidation - Detailed Steps

### Step 1: Document Inventory

Before comparing anything, list all source documents:

| Document | Location | Sections | Last Updated |
|----------|----------|----------|--------------|
| Research Report | `docs/research/` | List all | Date |
| PRD | `docs/prd/` | List all | Date |
| Tech Spec | `docs/tech-spec/` | List all | Date |

### Step 2: Section-by-Section Comparison

For each major topic (e.g., authentication, data model, API):

1. **Extract from PRD** - What the product requires (WHY/WHAT)
2. **Extract from Tech Spec** - How it will be built (HOW)
3. **Check alignment** - Does the HOW fully satisfy the WHAT?
4. **Flag gaps** - Requirements without technical coverage, or technical decisions without product justification

### Step 3: Build the Consolidated Spec

Process in dependency order (foundations first):

```
1. Data model / Schema
2. Core business logic
3. API contracts
4. UI / Frontend flows
5. Integrations
6. Non-functional requirements (security, performance)
7. Agentic design: PRD §1.5 Solution Shape, §7A.1-7A.8 and tech spec Section 9 Agent Architecture
```

The consolidated spec carries §1.5 (the level and its justifications), every §7A.1-7A.8 subsection and tech spec Section 9 in full; `references/section-mapping-guide.md` lists where each lands. A level that differs between the PRD and tech spec Section 9.1 (e.g. PRD says level 3, the spec builds a level 4 agent) is a contradiction: log it and resolve it with the tech lead, who decides the level.

For each section, write immediately after processing -- do not batch at the end. This prevents information loss (Golden Rule #3: Process in Chunks, Write Immediately).

---

## Contradiction Resolution Patterns

### Pattern 1: Scope Conflict

**Signal:** PRD says "support X" but Tech Spec scopes it out or implements a subset.

**Resolution:** Check Research Report for original validation. If research supports X, PRD wins. If research is ambiguous, flag for stakeholder decision.

### Pattern 2: Technical Impossibility

**Signal:** PRD requires something the Tech Spec declares infeasible or excessively costly.

**Resolution:** Document the constraint. Propose alternative that satisfies the business intent. Require stakeholder sign-off on the trade-off.

### Pattern 3: Implicit Assumption Mismatch

**Signal:** PRD assumes real-time; Tech Spec designs for batch. Neither states this explicitly.

**Resolution:** Make both assumptions explicit. Align on which is correct based on user need (WHY), not technical convenience.

### Pattern 4: Requirement Gap

**Signal:** Tech Spec implements something not mentioned in PRD, or PRD requires something Tech Spec does not address.

**Resolution:** Gaps from Tech Spec side -- verify if they are infrastructure concerns (acceptable) or scope creep (flag). Gaps from PRD side -- add missing technical coverage or escalate.

### Resolution Hierarchy

When sources conflict and no stakeholder is available:

```
1. Research Report (empirical evidence)
2. PRD (product intent)
3. Tech Spec (technical feasibility)
```

Always document which authority was used and why.

---

## Task Breakdown Methodology

### Sizing Rules

| Complexity Indicator | Target Task Size |
|----------------------|-----------------|
| Single function or component | XS (1-2 hours) |
| Feature slice with tests | S (2-4 hours) |
| Integration between 2 systems | M (4-8 hours) |
| Anything > 8 hours | Must be split further |

### Decomposition Strategy

1. **Identify epics** from PRD feature groups (business-level grouping)
2. **Derive stories** from PRD user stories and acceptance criteria
3. **Extract tasks** from Tech Spec components, APIs, and schemas
4. **Map dependencies** between tasks -- which must complete before others can start
5. **Sequence into sprints** based on dependency order and risk (high-risk first)

### Dependency Mapping

For each task, document:

- **Blocks:** What cannot start until this completes
- **Blocked by:** What must complete before this can start
- **Parallel with:** What can run concurrently

Visualize as a DAG (directed acyclic graph) when complexity exceeds 15 tasks.

### Sprint Assignment

| Sprint | Focus |
|--------|-------|
| Sprint 1 | Foundation: database, auth, core models |
| Sprint 2 | Core features: primary business logic |
| Sprint 3 | Integration: APIs, external services |
| Sprint 4 | Polish: UI, edge cases, performance |

Adjust based on project specifics. Every sprint must produce a testable increment.

---

## Jira Population Guidelines

### Information Completeness Checklist

Every Jira issue MUST have these fields populated before Phase 4:

**Epics:**
- [ ] Summary (business goal in one sentence)
- [ ] Description with business context from PRD
- [ ] Success criteria (how to know the epic is done)
- [ ] Priority and labels

**Stories:**
- [ ] Summary (user story format: As a... I want... So that...)
- [ ] Acceptance criteria (from PRD, testable)
- [ ] Business context linking back to epic goal
- [ ] Story point estimate

**Tasks:**
- [ ] Summary (verb + component: "Implement UserService.authenticate()")
- [ ] Technical implementation details from Tech Spec
- [ ] Files to create or modify
- [ ] API contracts or schema references
- [ ] Error handling approach
- [ ] Hour estimate
- [ ] Dependency links (blocks/blocked-by)
- [ ] Reference to consolidated spec section

### Content Boundary Rules

| Level | Contains | Source | Must NOT Contain |
|-------|----------|--------|-----------------|
| Epic | Business goals, success metrics | Research + PRD | Technical implementation |
| Story | User needs, acceptance criteria | PRD | Code patterns, schemas |
| Task | Technical approach, file paths | Tech Spec | Business justification |

### Two-Pass Population

**Pass 1 - Structure:** Create all epics, stories, tasks with summaries and hierarchy. Verify the tree is complete against source documents.

**Pass 2 - Enrichment:** Add full descriptions, acceptance criteria, technical details, dependencies. This is where the bulk of the content goes.

Never combine both passes. Structure first ensures nothing is missed before investing in detailed descriptions.

Enhancement Template:
```markdown
## Summary
[What this accomplishes]

## Business Context
[From PRD]

## Technical Implementation
[From Tech Spec]

## Acceptance Criteria
- [ ] [Criterion 1]
- [ ] [Criterion 2]

## Dependencies
- Blocks: [keys]
- Blocked By: [keys]

## Reference
📄 Consolidated Spec: [path]
📑 Section: [name]
```

### Traceability Verification

Before declaring Phase 3 complete:

```
For every PRD user story:
  -> Verify a corresponding Jira story exists
  -> Verify acceptance criteria are copied faithfully

For every Tech Spec component:
  -> Verify implementation tasks exist
  -> Verify API contracts are referenced in task descriptions

Coverage target: 100%. Gaps found -> create missing items -> re-verify.
```

---

## Agentic Task Set (AID 3.1, always)

The breakdown ALWAYS carries the eight agentic tasks below, whatever the PRD §1.5 Solution
Shape level. The level sets their depth, in three tiers (levels 0-1, 2-3, 4-5). At levels
2-5 they follow tech spec Section 9 "Agent Architecture" and PRD §7A. At levels 0-1 the
agentic tasks fold into the existing test, logging and release tasks, tagged with their 7A
item (e.g. a "Write acceptance and negative tests" task tagged `7A.6`); no separate task is
needed when an existing one already covers the item.

### The Eight Tasks

Every task obeys the "< 4 hr" rule (Rule #2 and the Sizing Rules above): the "Split into"
column lists the subtasks a typical project needs, each under 4 hours. Split further when a
subtask would exceed 4 hours.

| # | Task | Source | Level 2-5 content | Level 0-1 (folded into existing task) | Split into (each < 4 hr) |
|---|------|--------|-------------------|----------------------------------------|--------------------------|
| 1 | Golden set | PRD 7A.6, tech spec 9.5 | Grow from the Phase 1 seed cases (size and source from 7A.6), tag slices, version in `tests/evals/golden/`, hold out a test split (QA owns it; in parallel, complete before the Phase 5 gate) | Acceptance test data | Collect cases; label and adjudicate; split and version |
| 2 | Eval harness + release gate | PRD 7A.6, 7A.5, tech spec 9.5 | Runner in CI, scorers, LLM judge calibrated (Cohen's kappa >= 0.7 against human labels), threshold as a failing CI check | Acceptance tests wired as a CI gate | Runner; scorers; judge calibration; CI gate |
| 3 | Red-team cases | PRD 7A.4, 7A.1, tech spec 9.3 | Adversarial and prompt-injection cases; one check per never-do item verifying the code enforcement; 0 critical/high failures | Negative / abuse-case tests | Injection cases; never-do checks; abuse cases |
| 4 | Telemetry & traces | PRD 7A.7, tech spec 9.4 | Emit the trace schema, dashboards for quality, cost per successful task, latency, escalation rate, guardrail metrics | Structured logs, metrics, alerts | Trace emission; dashboards; alerts |
| 5 | Rollout stages | PRD 7A.8 | shadow → human approval → autonomous, entry and exit criteria per stage, blind audit of approvals, human-queue capacity check | Staged release plan | Stage criteria; shadow setup; audit sampling |
| 6 | Kill switch | PRD 7A.8, tech spec 9.8 | Runtime flag, scopes, degrade-to path, automatic triggers, test before autonomy, on-call owner | Feature flag + tested rollback | Flag and degrade path; triggers; kill-switch test |
| 7 | Permission policy + guardrails (Section 9.2/9.3) | PRD 7A.2, 7A.4, tech spec 9.2, 9.3 | Policy as code, default deny, per-tool risk tags, never-do items blocked in code, guardrails failing closed, human approval on outbound actions where the lethal trifecta is present | Access-control and validation tasks | Policy as code; tool scopes; guardrails |
| 8 | Data access, redaction, retention (7A.3) | PRD 7A.3, tech spec 9.2 | Data scopes per tool and per agent, redaction before prompts and traces, retention and deletion, model-provider data settings (retention, zero-data-retention, training opt-out, region) | Data-access and retention tasks | Data scopes; redaction; retention and provider settings |

### Dependencies and Ordering
- seed cases + dev/targeted suite -> eval harness -> prompt/tool/agent tasks; QA grows the golden set in parallel; it must be complete before the Phase 5 gate. The golden set is never a precondition for development (eval-driven, like TDD).
- Permission policy + guardrails come before any task that gives the model a write tool
- Red-team cases depend on the guardrails list (tech spec 9.3) and the never-do list (7A.1)
- Data access, redaction and retention come before telemetry stores any trace
- Telemetry & traces come before the first shadow run
- Kill switch is done and tested before the shadow stage goes live (the Phase 5 exit needs it)

### Naming Examples
- `E3-T01: Curate golden set for refund triage`
- `E3-T02: Build eval runner and CI release gate`
- `E3-T03: Write red-team and never-do cases`
- `E3-T04: Emit run traces and quality dashboard`
- `E3-T05: Define rollout stages and exit criteria`
- `E3-T06: Implement and test kill switch`
- `E3-T07: Write permission policy and guardrails as code`
- `E3-T08: Set data scopes, redaction and retention`

### Definition of Done for Agentic Stories
Add to the story template's Definition of Done for any story at level 2-5:
- [ ] Targeted + regression evals at threshold for the slices it touches
- [ ] Red-team and never-do checks for those slices pass
- [ ] Traces recorded for every run (7A.7)
- [ ] Prompt, tool and policy versions recorded
- [ ] Kill switch covers this feature (7A.8)

The "eval release gate" (the full gate on the held-out split) is a Phase 5 check, not a
story's Definition of Done. At levels 0-1, the story's evals are its acceptance tests passing in CI.

### Traceability Check
| §7A item | Must map to at least one task |
|----------|-------------------------------|
| 7A.1 Charter | Task 3 (never-do checks), escalation path in task 5 |
| 7A.2 Tools & Permissions | Task 7 (permission policy + guardrails) |
| 7A.3 Context & Data | Task 8 (data access, redaction, retention) |
| 7A.4 Failure Modes & Guardrails | Task 7 (guardrails) + task 3 (red-team cases) |
| 7A.5 Why-Chain | Task 2 (eval cases and metrics per WHY) |
| 7A.6 Eval Plan | Tasks 1 and 2 (golden set, eval harness + gate) |
| 7A.7 Telemetry & Traces | Task 4 |
| 7A.8 Rollout & Kill Switch | Tasks 5 and 6 |

---

## Phase 3 Exit Checklist

- [ ] Consolidated spec written and stakeholder-approved (3a)
- [ ] All contradictions logged with resolutions (3a)
- [ ] §1.5 level and §7A carried; level contradictions logged (3a)
- [ ] Tasks sized under 4 hours with acceptance criteria (3b)
- [ ] Dependencies mapped and sprint plan created (3b)
- [ ] Agentic task set present and every §7A item traced to a task (3b)
- [ ] Agentic stories carry "targeted + regression evals at threshold for the slices it touches" in their Definition of Done (3b)
- [ ] QA criteria files generated in `.aid/qa/` (3c)
- [ ] Jira populated with full details at every level (3d)
- [ ] Traceability verified: 100% PRD and Tech Spec coverage
