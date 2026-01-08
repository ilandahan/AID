# Phase 3: Implementation Planning Methodology

## ⚠️ GOLDEN RULES (Memorize These)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                          │
│   GOLDEN RULE #1: NO WORD LEFT BEHIND                                   │
│   ──────────────────────────────────                                    │
│   Every word in PRD → appears in Epic or Story                          │
│   Every word in Tech Spec → appears in Task                             │
│   If it's not in Jira, it won't get built.                             │
│                                                                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   GOLDEN RULE #2: SMALL TASKS, BIG DOCUMENTS                            │
│   ──────────────────────────────────────────                            │
│   The larger the source docs, the smaller the tasks.                    │
│   100-page spec = 100+ small tasks (not 10 big ones)                   │
│   Small tasks = more checkboxes = nothing lost.                        │
│                                                                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   GOLDEN RULE #3: PROCESS IN CHUNKS, WRITE IMMEDIATELY                  │
│   ────────────────────────────────────────────────────                  │
│   Read section → Write to file → Next section                          │
│   Don't hold it in memory. Write as you go.                            │
│                                                                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   GOLDEN RULE #4: VERIFY BEFORE PROCEEDING                              │
│   ────────────────────────────────────────                              │
│   100% PRD coverage or NO PROCEED                                       │
│   100% Tech Spec coverage or NO PROCEED                                │
│   Run verification agents. No exceptions.                               │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Overview

Phase 3 transforms PRD (Phase 1) and Tech Spec (Phase 2) into actionable, developer-ready Jira tickets.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         PHASE 3 WORKFLOW                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  Phase 1 (PRD)          Phase 2 (Tech Spec)                             │
│       │                        │                                         │
│       ▼                        ▼                                         │
│  ┌─────────────────────────────────────────┐                            │
│  │     3a. CONSOLIDATION                    │                            │
│  │     - Resolve contradictions             │                            │
│  │     - Align terminology                  │                            │
│  │     - Create master reference            │                            │
│  └─────────────────────────────────────────┘                            │
│                      │                                                   │
│                      ▼                                                   │
│  ┌─────────────────────────────────────────┐                            │
│  │     3b. BREAKDOWN                        │                            │
│  │     - Create Epic structure              │                            │
│  │     - Define Stories per Epic            │                            │
│  │     - Break Stories into Tasks           │                            │
│  └─────────────────────────────────────────┘                            │
│                      │                                                   │
│                      ▼                                                   │
│  ┌─────────────────────────────────────────┐                            │
│  │     3c. ENRICHMENT                       │                            │
│  │     - Write full descriptions            │                            │
│  │     - Add technical details              │                            │
│  │     - Verify completeness                │                            │
│  └─────────────────────────────────────────┘                            │
│                      │                                                   │
│                      ▼                                                   │
│  ┌─────────────────────────────────────────┐                            │
│  │     3d. JIRA POPULATION                  │                            │
│  │     - Create hierarchy in Jira           │                            │
│  │     - Upload enriched content            │                            │
│  │     - Link dependencies                  │                            │
│  └─────────────────────────────────────────┘                            │
│                      │                                                   │
│                      ▼                                                   │
│  ┌─────────────────────────────────────────┐                            │
│  │     3e. VERIFICATION                     │                            │
│  │     - PRD coverage check                 │                            │
│  │     - Tech Spec coverage check           │                            │
│  │     - Gap remediation                    │                            │
│  └─────────────────────────────────────────┘                            │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Stage 3a: Contradiction Resolution & Consolidation

### Purpose
Find and resolve ALL contradictions BEFORE consolidating into a single document.

### CRITICAL: The Right Order

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                          │
│   ✅ CONTRADICTIONS FIRST → THEN CONSOLIDATE                            │
│                                                                          │
│   Step 1: Map ─► Step 2: Compare ─► Step 3: Log ─► Step 4: Fix ─► Step 5│
│   Sections      Section by         Contradictions   Source      Consolidate│
│                 Section                             Documents   (Safe!)   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Why This Order?

When you consolidate first, you make **unconscious decisions**:
- "These are basically the same, I'll pick one"
- "This wording is clearer, I'll use it"

These micro-decisions **hide contradictions** in vague wording.

By finding contradictions FIRST:
- Every conflict is **explicitly identified**
- Resolution is **consciously chosen**
- Rationale is **documented**
- Source documents are **fixed** (not just the consolidated doc)

### Process

#### Step 1: Section Mapping

Map which sections in each document cover similar topics:

```markdown
| PRD Section | Tech Spec Section | Topic |
|-------------|-------------------|-------|
| 8.1 Security | 4.1 Authentication | Auth implementation |
| 5.2 API Requirements | 3.1 API Design | API contracts |
| 6.1 Data Model | 2.3 Database | Data structure |
```

#### Step 2: Section-by-Section Comparison

For each mapped pair:
1. Read PRD section completely
2. Read Tech Spec section completely
3. Compare EVERY claim, number, name, behavior
4. Log ANY discrepancy

#### Step 3: Create Contradiction Log

Use template: `references/templates/contradiction-log-template.md`

```markdown
### C-01: Token Expiry

**PRD Section 8.1 Says:**
> "JWT tokens expire after 1 hour"

**Tech Spec Section 4.2 Says:**
> "Access tokens: 15 minutes. Refresh tokens: 7 days."

**Resolution:** Use Tech Spec
**Authority:** Tech Spec overrides PRD on security implementation
**Rationale:** 15-min access tokens are security best practice
**Action:** Update PRD Section 8.1
```

#### Step 4: Fix Source Documents

**CRITICAL: Fix the SOURCE, not just the consolidated doc.**

Why? If you only fix the consolidated doc:
- Original PRD still has wrong info
- Future readers get confused
- The contradiction still exists in source

Update PRD and/or Tech Spec based on each resolution.

#### Step 5: NOW Consolidate (Safe!)

With all contradictions resolved in source docs:
- Merge is now safe
- No hidden conflicts
- Clear authority for every statement
- Audit trail explains all decisions

Create: `docs/implementation-plan/00-consolidated-spec.md`

### Authority Hierarchy

```
Research Report (data-driven)
       │
       ▼ overrides
     PRD (business requirements)
       │
       ▼ overrides
   Tech Spec (implementation)
```

**Exception:** Tech Spec overrides PRD on:
- Technical feasibility
- Security implementation details
- Performance constraints

### Output Artifacts
- `docs/implementation-plan/contradiction-log.md` - All contradictions with resolutions
- Fixed PRD (original file updated)
- Fixed Tech Spec (original file updated)
- `docs/implementation-plan/00-consolidated-spec.md` - Clean merged document

---

## Stage 3b: Breakdown

### Purpose
Create the Epic → Story → Task hierarchy.

### Hierarchy Rules

```
EPIC (Domain)
├── Contains: 3-8 Stories
├── Duration: 1-3 weeks
├── Owner: Tech Lead / Architect
│
└── STORY (User Capability)
    ├── Contains: 2-6 Tasks
    ├── Duration: 1-5 days
    ├── Owner: Senior Developer
    │
    └── TASK (Implementation Unit)
        ├── Duration: 2-16 hours
        ├── Owner: Any Developer
        └── Fully self-contained
```

### Epic Identification Process

1. **Group by Domain** (from Tech Spec architecture)
   ```
   Infrastructure → Auth → Core Domains → Frontend
   ```

2. **Order by Dependency**
   ```
   EPIC-1: Infrastructure (no dependencies)
   EPIC-2: Auth (depends on EPIC-1)
   EPIC-3: Projects (depends on EPIC-1, EPIC-2)
   ...
   EPIC-N: Frontend (depends on all backend)
   ```

3. **Verify Coverage**
   - Every PRD user story maps to an Epic
   - Every Tech Spec component maps to an Epic

### Story Identification Process

1. **Extract from PRD User Stories**
   ```
   PRD: "As a user, I want to register..."
   PRD: "As a user, I want to log in..."
   PRD: "As a user, I want to reset my password..."

   → Story 2.1: User Registration
   → Story 2.2: User Login
   → Story 2.3: Password Reset
   ```

2. **Group by User Capability**
   - NOT by technical layer
   - One story = one user-facing capability

3. **Apply INVEST Criteria**
   - Independent, Negotiable, Valuable, Estimable, Small, Testable

### Task Identification Process

1. **Decompose Story into Implementation Steps**
   ```
   Story: User Registration

   → Task: Create signup API endpoint
   → Task: Implement password hashing
   → Task: Create signup form component
   → Task: Add email validation
   → Task: Write registration tests
   ```

2. **Ensure Task Independence**
   - One developer can complete in 1-2 days
   - Clear start and end points
   - Testable in isolation

### Output
- `docs/implementation-plan/01-task-breakdown.md`
- Epic/Story/Task hierarchy diagram

---

## Stage 3c: Enrichment

### Purpose
Add full implementation details to each Epic/Story/Task.

### Process

1. **Create Enriched Files** (Staging before Jira)
   ```
   docs/implementation-plan/enriched-jiras/
   ├── EPIC-1-enriched.md
   ├── EPIC-2-enriched.md
   └── EPIC-N-enriched.md
   ```

2. **Apply Templates**
   - Use `templates/epic-template.md`
   - Use `templates/story-template.md`
   - Use `templates/task-template.md`

3. **Content Mapping** (See detailed rules below)

### Content Mapping Matrix

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    CONTENT MAPPING MATRIX                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  SOURCE DOCUMENT              TARGET LEVEL                               │
│  ─────────────────           ─────────────                               │
│                                                                          │
│  PRD                                                                     │
│  ├── Product Goals ─────────► Epic: Business Value                      │
│  ├── User Personas ─────────► Epic: User Impact                         │
│  ├── Success Metrics ───────► Epic: Success Criteria                    │
│  ├── User Stories ──────────► Story: User Story                         │
│  ├── Acceptance Criteria ───► Story: Acceptance Criteria (Gherkin)      │
│  ├── UI Requirements ───────► Story: Design References                  │
│  └── Out of Scope ──────────► Story: Out of Scope                       │
│                                                                          │
│  TECH SPEC                                                               │
│  ├── Architecture ──────────► Epic: Technical Context                   │
│  ├── Technology Stack ──────► Epic: Primary Technology                  │
│  ├── Security Reqs ─────────► Story: Non-Functional Requirements        │
│  ├── API Endpoints ─────────► Story: API Endpoints table                │
│  └── Error Handling ────────► Story: Error scenarios in AC              │
│                                                                          │
│  OPENAPI                                                                 │
│  ├── Path + Method ─────────► Task: API Contract                        │
│  ├── Request Schema ────────► Task: Code Pattern                        │
│  ├── Response Schema ───────► Task: Acceptance Criteria                 │
│  ├── Error Responses ───────► Task: Error Handling table                │
│  └── Security Scheme ───────► Task: Technical Details                   │
│                                                                          │
│  PRISMA SCHEMA                                                           │
│  ├── Model Definition ──────► Task: Database Changes                    │
│  ├── Relations ─────────────► Task: Dependencies                        │
│  └── Validations ───────────► Task: Acceptance Criteria                 │
│                                                                          │
│  IMPLEMENTATION PLAN                                                     │
│  ├── File Paths ────────────► Task: Files to create/modify              │
│  ├── Code Examples ─────────► Task: Code Pattern                        │
│  ├── Task Dependencies ─────► Task: Dependencies                        │
│  └── Size Estimates ────────► Task: Size Estimate                       │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Enrichment Checklist

**Epic Enrichment:**
- [ ] Summary (2-3 sentences)
- [ ] Business Value (from PRD goals)
- [ ] User Impact (from PRD personas)
- [ ] Dependencies (blocked by / blocks)
- [ ] Success Criteria (measurable, from PRD)
- [ ] Technical Context (from Tech Spec)
- [ ] PRD References
- [ ] Tech Spec References
- [ ] Estimated Duration

**Story Enrichment:**
- [ ] User Story (As a... I want... So that...)
- [ ] Acceptance Criteria (Gherkin format)
- [ ] API Endpoints table
- [ ] Design References
- [ ] Non-Functional Requirements
- [ ] Out of Scope
- [ ] Definition of Done
- [ ] PRD Traceability
- [ ] Story Points

**Task Enrichment:**
- [ ] Description (what and why)
- [ ] Files to create/modify
- [ ] Implementation approach
- [ ] Code pattern/example
- [ ] API Contract (if applicable)
- [ ] Database changes (if applicable)
- [ ] Dependencies
- [ ] Acceptance Criteria (technical)
- [ ] Error Handling table
- [ ] Testing Requirements
- [ ] Size Estimate
- [ ] Tech Spec References

### Output
- Complete enriched files for all Epics
- Ready for Jira population

---

## Stage 3d: Jira Population

### Purpose
Create and update Jira tickets with enriched content.

### Hierarchy Creation Order

```
1. Create all EPICs first
2. Create all Stories, link to parent Epic
3. Create all Tasks, link to parent Story
4. Link dependencies between tickets
5. Assign initial priorities
```

### Jira API Process

1. **Get Project Key**
   ```bash
   GET /rest/api/3/project
   ```

2. **Create Epics**
   ```bash
   POST /rest/api/3/issue
   {
     "fields": {
       "project": {"key": "AID"},
       "summary": "EPIC-1: Infrastructure & DevOps",
       "issuetype": {"name": "Epic"},
       "description": {ADF content}
     }
   }
   ```

3. **Create Stories with Parent**
   ```bash
   POST /rest/api/3/issue
   {
     "fields": {
       "project": {"key": "AID"},
       "summary": "Story 1.1: GCP Project Setup",
       "issuetype": {"name": "Story"},
       "parent": {"key": "AID-1"},
       "description": {ADF content}
     }
   }
   ```

4. **Create Tasks with Parent**
   ```bash
   POST /rest/api/3/issue
   {
     "fields": {
       "project": {"key": "AID"},
       "summary": "E1-T01: Create GCP Project",
       "issuetype": {"name": "Task"},
       "parent": {"key": "AID-10"},  // Story key
       "description": {ADF content}
     }
   }
   ```

### ADF (Atlassian Document Format)

Convert Markdown to ADF for rich Jira descriptions:

```json
{
  "version": 1,
  "type": "doc",
  "content": [
    {
      "type": "heading",
      "attrs": {"level": 2},
      "content": [{"type": "text", "text": "Description"}]
    },
    {
      "type": "paragraph",
      "content": [{"type": "text", "text": "Content here..."}]
    },
    {
      "type": "bulletList",
      "content": [
        {
          "type": "listItem",
          "content": [
            {"type": "paragraph", "content": [{"type": "text", "text": "Item 1"}]}
          ]
        }
      ]
    }
  ]
}
```

### Output
- All Epics, Stories, Tasks in Jira
- Proper parent-child relationships
- Dependency links

---

## Stage 3e: Verification

### Purpose
Ensure 100% coverage of PRD and Tech Spec.

### Verification Agents

Run 3 parallel verification checks:

1. **PRD Coverage Agent**
   ```
   For each PRD user story:
   - Find corresponding Story in Jira
   - Verify acceptance criteria match
   - Flag gaps
   ```

2. **Tech Spec Coverage Agent**
   ```
   For each Tech Spec component:
   - Find corresponding Tasks in Jira
   - Verify technical details included
   - Flag gaps
   ```

3. **Task Completeness Agent**
   ```
   For each Task:
   - Verify has all required fields
   - Check for orphan tasks (no parent)
   - Check for blocked-by references
   ```

### Gap Remediation

When gaps are found:

1. **Document the Gap**
   ```markdown
   | Gap | EPIC | New Task Needed | Priority |
   |-----|------|-----------------|----------|
   | Rate Limiting | EPIC-1 | E1-T13: Configure Rate Limiting | HIGH |
   ```

2. **Create Missing Tasks**
   - Use templates
   - Add to enriched files
   - Push to Jira

3. **Re-verify**
   - Run coverage check again
   - Confirm 100% coverage

### Coverage Report Template

```markdown
## Phase 3 Verification Report

### PRD Coverage
- User Stories: {X}/{Y} covered ({Z}%)
- Acceptance Criteria: {X}/{Y} covered ({Z}%)
- Gaps: {list or "None"}

### Tech Spec Coverage
- API Endpoints: {X}/{Y} covered ({Z}%)
- Database Models: {X}/{Y} covered ({Z}%)
- Security Requirements: {X}/{Y} covered ({Z}%)
- Gaps: {list or "None"}

### Task Quality
- Total Tasks: {N}
- With full descriptions: {N}
- With code examples: {N}
- With size estimates: {N}

### Gaps Remediated
1. {Gap 1}: Added {Task ID}
2. {Gap 2}: Added {Task ID}

### Final Status
[ ] PRD 100% covered
[ ] Tech Spec 100% covered
[ ] All tasks enriched
[ ] Ready for Phase 4 (Development)
```

---

## Phase 3 Quality Gates

### Entry Criteria (from Phase 2)
- [ ] PRD approved and signed off
- [ ] Tech Spec approved and signed off
- [ ] OpenAPI specification complete
- [ ] Database schema complete
- [ ] No unresolved contradictions

### Exit Criteria (to Phase 4)
- [ ] All Epics created in Jira with full descriptions
- [ ] All Stories created with acceptance criteria
- [ ] All Tasks created with technical details
- [ ] 100% PRD coverage verified
- [ ] 100% Tech Spec coverage verified
- [ ] Dependencies linked
- [ ] Sprint 1 planned
- [ ] Team capacity assigned

---

## Anti-Patterns to Avoid

| Anti-Pattern | Problem | Solution |
|--------------|---------|----------|
| Spec fixes as tasks | Developers shouldn't fix specs | Fix source docs directly |
| Flat hierarchy | Epic → Task loses context | Always use Stories |
| Copy-paste content | Duplicated, goes stale | Reference source docs |
| Vague tasks | Developers ask questions | Use templates, be specific |
| No verification | Gaps discovered in dev | Always run coverage checks |
| Manual Jira entry | Slow, error-prone | Use API, script it |
| Skipping enrichment | Thin descriptions | Stage in .md files first |
