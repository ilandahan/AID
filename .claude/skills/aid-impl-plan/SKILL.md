---
name: aid-impl-plan
description: AID Phase 3 - Implementation Planning with consolidation-first approach. Resolves contradictions between PRD and Tech Spec, creates consolidated master document, then breaks down into actionable tasks and populates Jira. Includes sprint planning and risk assessment.
---

# AID Implementation Plan Skill (Phase 3)

## Templates & References

**Templates:**
- `references/templates/epic-template.md`
- `references/templates/story-template.md`
- `references/templates/task-template.md`
- `references/templates/contradiction-log-template.md`

**Methodology:**
- `references/phase3-methodology.md`
- `references/content-mapping.md`
- `references/criteria-generator.md`
- `references/iron-rules.md`

**Key Principle:** PRD Content → Epics & Stories (WHY/WHAT), Tech Spec Content → Tasks (HOW)

---

## Golden Rules of Phase 3

### Rule #1: NO WORD LEFT BEHIND

Every word from source documents MUST appear in Jira:
- PRD content → Epics/Stories
- Tech Spec content → Tasks
- OpenAPI endpoints → Implementation Tasks

**Verification:** Create traceability matrices. 100% coverage required before Phase 4.

### Rule #2: SMALL TASKS, BIG DOCUMENTS

| Source Size | Task Size |
|-------------|-----------|
| < 20 pages | M (4-8 hours) |
| 20-50 pages | S (2-4 hours) |
| 50-100 pages | XS-S (1-4 hours) |
| > 100 pages | XS (1-2 hours) |

### Rule #3: PROCESS IN CHUNKS, WRITE IMMEDIATELY

Wrong: Read all → Think → Write at end (loses info)
Right: Read section → Write to enriched file → Next section (progressive capture)

### Rule #4: VERIFY BEFORE PROCEEDING

Before Phase 4:
- [ ] Every PRD user story → Story in Jira
- [ ] Every Tech Spec component → Tasks
- [ ] Every Task has all required fields
- [ ] Coverage < 100%? Find gaps → Add items → Re-verify

---

## Phase 3 Sub-Phases

```
Phase 3a → Phase 3b → Phase 3c → Phase 3d
Consolidation  Breakdown  Criteria Gen  Jira Population
```

### Phase 3a: Contradiction Resolution & Consolidation

**Purpose:** Find and resolve ALL contradictions between PRD, Tech Spec, and Research BEFORE consolidating.

**Process:**
1. Document Discovery & Section Mapping
2. Create Processing Order (dependency order)
3. Section-by-Section Consolidation
4. Contradiction Analysis (per section)
5. Resolution Hierarchy: Research > PRD > Tech Spec
6. Progressive Document Building

**Contradiction Types:**
| Type | Priority |
|------|----------|
| Scope conflicts | 1 (Critical) |
| Technical conflicts | 1 (Critical) |
| Requirement gaps | 2 (High) |
| Implementation conflicts | 2 (High) |
| Minor inconsistencies | 3 (Low) |

**Resolution Template:**
```markdown
## Contradiction #[N]
**Found In:** [PRD section] vs [Tech Spec section]
**Description:** [What conflicts]
**Resolution:** [How resolved]
**Authority Used:** [Research/PRD/Tech Spec]
**Rationale:** [Why]
```

**Phase 3a Checkpoint:** User approval required before proceeding to 3b.

---

### Phase 3b: Task Breakdown

**Purpose:** Transform consolidated spec into actionable development tasks.

**Component Categories:**
- Backend: API, Database, Business Logic, Integrations
- Frontend: Pages, Components, State, API Integration
- Infrastructure: Database Setup, Config, CI/CD
- Cross-Cutting: Auth, Logging, Error Handling

**Task Decomposition Rules:**
| Rule | Requirement |
|------|-------------|
| Size | < 4 hours (prefer 1-2) |
| Independence | Completable alone (unless dependency) |
| Testability | Clear acceptance criteria |
| Traceability | Links to spec section |

**Estimation:**
| Type | Unit | Range |
|------|------|-------|
| Epic | Sprints | 1-3 |
| Story | Story Points | 1,2,3,5,8,13 |
| Task | Hours | 1-8 |
| Subtask | Minutes/Hours | 15min-4hr |

**Risk Template:**
```markdown
### Risk: [Name]
- **Category:** [Technical/Dependency/Resource/Timeline/Scope]
- **Probability:** [High/Medium/Low]
- **Impact:** [High/Medium/Low]
- **Mitigation:** [Strategy]
- **Contingency:** [Backup plan]
```

---

### Phase 3c: Success Criteria Generation (QA Gate Setup)

**Purpose:** Generate testable acceptance criteria for QA sub-agent validation.

**Information Boundaries:**
| Level | Contains | Source | Forbidden |
|-------|----------|--------|-----------|
| Epic | Business Logic (WHY) | Research+PRD | Tech HOW |
| Story | Product Logic (WHAT) | PRD | Tech HOW |
| Task | Technical Approach (HOW) | Tech Spec | Business WHY |
| Sub-task (QA) | Acceptance Criteria (VERIFY) | Story AC | Tech HOW |

**Output:** `.aid/qa/{task-id}.yaml`

```yaml
schema_version: "1.0"
task_id: "{TASK-ID}"
business_context:
  epic_goal: "{sanitized}"
  user_value: "{sanitized}"
  acceptance_criteria: []
criteria:
  must_achieve: []
  must_not: []
  not_included: []
  best_practices: []
files_to_review: []
review_history: []
```

**Phase 3c Checkpoint:** Human approval required before Jira population.

---

### Phase 3d: Jira Population

**Two-Step Process:**

**Step 1: Create Structure**
1. Create all Epics (summary, priority, labels)
2. Create all Stories under Epics
3. Create all Tasks under Stories
4. Create all Subtasks under Tasks
5. Link all dependencies

**Step 2: Enhance with Full Details**
For each issue, add:
- Full business context (PRD)
- Technical implementation (Tech Spec)
- Acceptance criteria
- Technical notes
- Test strategy
- Reference to consolidated spec

**Enhancement Template:**
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

**Alternative Export:** CSV/JSON for non-Jira users.

---

## Lessons Learned

1. **Stage enriched content** in `docs/implementation-plan/enriched-jiras/` before pushing to Jira
2. **Never skip Story layer** - Epic → Story → Task (not Epic → Task)
3. **Spec fixes are NOT developer work** - fix source documents directly
4. **Content mapping is mandatory** - PRD → Epic/Story, Tech Spec → Task
5. **Verification is mandatory** - run coverage agents before Phase 4
6. **Use ADF for Jira** - Atlassian Document Format for rich descriptions
7. **Task naming:** E{Epic#}-T{Sequential##}: {Verb} {Component}
8. **Every task needs:** Description, Files, Code pattern, API contract, Error handling, AC, Estimate, Spec reference

---

## Output Artifacts

| Artifact | Location |
|----------|----------|
| Consolidated Spec | docs/implementation-plan/consolidated-spec-YYYY-MM-DD-[feature].md |
| Contradiction Log | docs/implementation-plan/contradiction-log-YYYY-MM-DD.md |
| Task Breakdown | docs/implementation-plan/task-breakdown-YYYY-MM-DD-[feature].md |
| Jira Export | docs/implementation-plan/jira-export-YYYY-MM-DD.json |
| Risk Assessment | docs/implementation-plan/risks-YYYY-MM-DD.md |
| Sprint Plan | docs/implementation-plan/sprint-plan-YYYY-MM-DD.yaml |

---

## Exit Criteria (Phase 3 → Phase 4)

- [ ] Phase 3a: Consolidated doc created, user approved
- [ ] Phase 3b: Tasks < 4hr, acceptance criteria, dependencies mapped
- [ ] Phase 3c: QA criteria files generated, human approved
- [ ] Phase 3d: Jira populated, all issues have full descriptions
- [ ] Quality Gates: Sub-agent review PASSED

---

## Commands

| Command | Purpose |
|---------|---------|
| /impl-plan | Start Phase 3 |
| /consolidate | Run Phase 3a |
| /breakdown | Run Phase 3b |
| /populate-jira | Run Phase 3d |

---

## State Tracking

`.aid/state.json`:
```json
{
  "current_phase": 3,
  "sub_phase": "3b",
  "phase_3_state": {
    "3a": {"status": "complete", "user_approved": true},
    "3b": {"status": "in_progress"},
    "3c": {"status": "locked"},
    "3d": {"status": "locked"}
  }
}
```
