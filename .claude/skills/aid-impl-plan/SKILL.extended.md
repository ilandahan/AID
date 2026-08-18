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
```

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

## Phase 3 Exit Checklist

- [ ] Consolidated spec written and stakeholder-approved (3a)
- [ ] All contradictions logged with resolutions (3a)
- [ ] Tasks sized under 4 hours with acceptance criteria (3b)
- [ ] Dependencies mapped and sprint plan created (3b)
- [ ] QA criteria files generated in `.aid/qa/` (3c)
- [ ] Jira populated with full details at every level (3d)
- [ ] Traceability verified: 100% PRD and Tech Spec coverage
