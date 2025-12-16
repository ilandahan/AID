# Phase Enforcement Skill

## Purpose

Enforces AID phase gates with mandatory quality feedback collection. Claude MUST check current phase before any work, REFUSE work that belongs to a later phase, and collect feedback at phase completion for continuous improvement.

---

## PRIORITY 1: Phase Gate Enforcement

```
┌─────────────────────────────────────────────────────────────────┐
│  BEFORE ANY WORK, CLAUDE MUST:                                  │
│                                                                 │
│  1. Read `.aid/state.json` for current phase                    │
│  2. Classify the requested work                                 │
│  3. Check if work is allowed in current phase                   │
│  4. REFUSE if not allowed (show violation template)             │
│  5. At phase completion: collect feedback via /aid end          │
└─────────────────────────────────────────────────────────────────┘
```

---

## Phase Structure

### 5-Phase Development Lifecycle

| Phase | Name | Document Output | Folder |
|-------|------|-----------------|--------|
| 1 | PRD | Product Requirements | `docs/prd/` |
| 2 | Tech Spec | Technical Specification | `docs/tech-spec/` |
| 3 | Implementation Plan | Task Breakdown | `docs/implementation-plan/` |
| 4 | Development | Code & Tests | `src/`, `testing/` |
| 5 | QA & Ship | Deployment & Release | Production |

### Document Naming Convention

All documents follow: `YYYY-MM-DD-[feature-name].md`

```
docs/
├── prd/
│   └── 2024-12-11-user-authentication.md
├── tech-spec/
│   └── 2024-12-12-user-authentication.md
└── implementation-plan/
    └── 2024-12-13-user-authentication.md
```

---

## Work Classification

| Category | Examples | First Allowed | Gate Document |
|----------|----------|---------------|---------------|
| `requirements` | PRD, user stories, scope | Phase 1 | `docs/prd/` |
| `architecture` | System design, DB schema, APIs | Phase 2 | `docs/tech-spec/` |
| `planning` | Jira issues, task breakdown | Phase 3 | `docs/implementation-plan/` |
| `coding` | Components, features, tests | Phase 4 | Source code |
| `qa` | Testing review, deployment | Phase 5 | Release |

---

## Phase Permissions

```javascript
const PHASE_ALLOWED = {
  1: ["requirements"],
  2: ["requirements", "architecture"],
  3: ["requirements", "architecture", "planning"],
  4: ["requirements", "architecture", "planning", "coding"],
  5: ["requirements", "architecture", "planning", "coding", "qa"],
};

const PHASE_OUTPUT_FOLDERS = {
  1: "docs/prd/",
  2: "docs/tech-spec/",
  3: "docs/implementation-plan/",
  4: "src/",
  5: "deployment/",
};
```

---

## Detection Patterns

### Phase 1 Work (requirements)
- "create PRD", "write requirements", "define scope"
- "user stories", "acceptance criteria", "feature definition"

### Phase 2 Work (architecture)
- "design architecture", "create schema", "define API"
- "tech spec", "data model", "component design", "security architecture"

### Phase 3 Work (planning)
- "create epic", "jira", "break down", "implementation plan"
- "tasks", "estimate", "sprint", "phase breakdown"

### Phase 4 Work (coding)
- "create component", "implement", "write code"
- "build", "create file", "write tests"

### Phase 5 Work (qa)
- "deploy", "release", "ship"
- "review coverage", "performance test", "production"

---

## PRIORITY 2: Quality Feedback Integration

```
┌─────────────────────────────────────────────────────────────────┐
│  MANDATORY FEEDBACK COLLECTION                                  │
│                                                                 │
│  At EVERY phase completion:                                     │
│  1. Run /aid end to collect user feedback                       │
│  2. Rating (1-5) + What worked + What to improve                │
│  3. Save to ~/.aid/feedback/pending/                            │
│  4. Use feedback in /aid improve for skill enhancement          │
└─────────────────────────────────────────────────────────────────┘
```

### Quality Feedback Flow

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Phase N    │────▶│   /aid end   │────▶│   Feedback   │
│  Complete    │     │   (Rating)   │     │    Stored    │
└──────────────┘     └──────────────┘     └──────┬───────┘
                                                  │
                                                  ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│    Skill     │◀────│ /aid improve │◀────│   3+ Items   │
│   Updated    │     │  (Analysis)  │     │   Pending    │
└──────────────┘     └──────────────┘     └──────────────┘
```

### Feedback Schema

```json
{
  "timestamp": "2024-12-11T12:00:00Z",
  "phase": 2,
  "phase_name": "tech-spec",
  "rating": 4,
  "worked_well": "Security architecture well documented",
  "to_improve": "Need more detail on error handling",
  "document_path": "docs/tech-spec/2024-12-11-user-auth.md",
  "duration_minutes": 120
}
```

---

## Gate Check Requirements

### Phase 1 → Phase 2 Gate
- [ ] PRD exists in `docs/prd/YYYY-MM-DD-[feature].md`
- [ ] All user stories defined
- [ ] Acceptance criteria complete
- [ ] **Feedback collected** via `/aid end`

### Phase 2 → Phase 3 Gate
- [ ] Tech Spec exists in `docs/tech-spec/YYYY-MM-DD-[feature].md`
- [ ] Architecture diagram included
- [ ] API contracts defined
- [ ] Security assessment complete
- [ ] **Feedback collected** via `/aid end`

### Phase 3 → Phase 4 Gate
- [ ] Implementation Plan in `docs/implementation-plan/YYYY-MM-DD-[feature].md`
- [ ] Tasks broken down with effort estimates
- [ ] Dependencies identified
- [ ] Test strategy defined
- [ ] **Feedback collected** via `/aid end`

### Phase 4 → Phase 5 Gate
- [ ] All code implemented
- [ ] Tests passing
- [ ] Coverage meets threshold
- [ ] Code reviewed
- [ ] **Feedback collected** via `/aid end`

---

## Violation Template

```
⛔ PHASE GATE VIOLATION

Current Phase: [N] [Phase Name]
Requested: [What user asked for]
Category: [Category]

This work belongs to Phase [X] ([Phase Name]).

Complete these phases first:
[List incomplete phases with their requirements]

Documents required:
- Phase [N]: docs/[folder]/YYYY-MM-DD-[feature].md

Commands:
  /phase        - See current status
  /gate-check   - See what's needed
  /aid end      - Complete current phase with feedback
```

---

## Phase Completion Template

```
✅ PHASE [N] COMPLETE: [Phase Name]

Deliverables:
- [Document/Output created]
- Location: [path]

Before advancing to Phase [N+1], please provide feedback:

Run: /aid end

This helps improve the methodology for future sessions.
```

---

## Exceptions

### Always Allowed
- Reading/viewing files (exploration)
- Documentation updates (non-phase docs)
- Answering questions
- Running `/phase`, `/gate-check`, `/aid end`, `/aid improve`

### With Warning
- Fixing earlier phase artifacts (show warning but allow)
- Updating documents from completed phases

### Override
- User can say "override: [reason]"
- Log override in `.aid/overrides.log`
- Override does NOT skip feedback requirement

---

## Skill Integration

This skill coordinates with other skills based on phase:

| Skill | Available From | Gate Requirement |
|-------|----------------|------------------|
| `system-architect` | Phase 2+ | PRD approved |
| `atomic-design` | Phase 4+ | Tech Spec approved |
| `code-review` | Phase 4+ | Implementation Plan approved |
| `test-driven` | Phase 4+ | Implementation Plan approved |

### Integration Flow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Phase     │     │   Load      │     │   Execute   │
│   Check     │────▶│   Skill     │────▶│   Work      │
└─────────────┘     └─────────────┘     └──────┬──────┘
       │                                        │
       │                                        ▼
       │                               ┌─────────────┐
       │                               │  /aid end   │
       │                               │  (Feedback) │
       │                               └─────────────┘
       │                                        │
       ▼                                        ▼
┌─────────────────────────────────────────────────────┐
│           /aid improve (Skill Enhancement)          │
│   - Analyze feedback patterns                       │
│   - Suggest skill updates                           │
│   - Promote insights to memory                      │
└─────────────────────────────────────────────────────┘
```

---

## State Management

### `.aid/state.json`

```json
{
  "current_phase": 2,
  "phase_name": "tech-spec",
  "feature_name": "user-authentication",
  "started_at": "2024-12-11T10:00:00Z",
  "phases_completed": [1],
  "documents": {
    "prd": "docs/prd/2024-12-11-user-authentication.md",
    "tech_spec": null,
    "implementation_plan": null
  },
  "feedback_collected": {
    "phase_1": true,
    "phase_2": false
  }
}
```

---

## Commands Reference

| Command | Purpose | Phase |
|---------|---------|-------|
| `/phase` | Show current phase status | Any |
| `/gate-check` | Check gate requirements | Any |
| `/phase approve` | Approve phase advancement | End of phase |
| `/aid end` | Complete phase with feedback | End of phase |
| `/aid improve` | Run improvement analysis | Any (3+ feedback) |

---

## References

See `references/` folder:
- `phase-gates.md` - Detailed gate requirements
- `quality-feedback.md` - Feedback collection and analysis
- `skill-integration.md` - How skills coordinate by phase
