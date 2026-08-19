# Skill Integration Reference

How phase-enforcement coordinates with other skills based on the current phase.

---

## Overview

```
┌─────────────────────────────────────────────────────────────────┐
│               SKILL ACTIVATION BY PHASE                         │
│                                                                 │
│  Phase 1: PRD                                                   │
│  └── No specialized skills (requirements focus)                 │
│                                                                 │
│  Phase 2: Tech Spec                                             │
│  └── system-architect (security, ISO 27001, API design)         │
│                                                                 │
│  Phase 3: Implementation Plan  ⭐ MAJOR UPDATE                   │
│  ├── aid-impl-plan (consolidation, breakdown, enrichment)       │
│  └── Sub-phases: 3a → 3b → 3c → 3d → 3e                        │
│                                                                 │
│  Phase 4: Development                                           │
│  ├── atomic-design (component library)                          │
│  ├── code-review (quality checks)                               │
│  └── test-driven (TDD methodology)                              │
│                                                                 │
│  Phase 5: QA & Ship                                             │
│  ├── code-review (final review)                                 │
│  └── test-driven (coverage verification)                        │
└─────────────────────────────────────────────────────────────────┘
```

---

## Skill Activation Matrix

| Skill | Phase 1 | Phase 2 | Phase 3 | Phase 4 | Phase 5 |
|-------|:-------:|:-------:|:-------:|:-------:|:-------:|
| system-architect | - | ✓ | ✓ | - | - |
| **aid-impl-plan** | - | - | **✓** | - | - |
| atomic-design | - | - | - | ✓ | - |
| code-review | - | - | - | ✓ | ✓ |
| test-driven | - | - | - | ✓ | ✓ |
| phase-enforcement | ✓ | ✓ | ✓ | ✓ | ✓ |

---

## Phase 3: Implementation Plan (Detailed)

Phase 3 is the most complex phase with 5 distinct sub-phases and 4 Golden Rules.

### Phase 3 Golden Rules

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                          │
│   GOLDEN RULE #1: NO WORD LEFT BEHIND                                   │
│   Every word in PRD → appears in Epic or Story                          │
│   Every word in Tech Spec → appears in Task                             │
│   If it's not in Jira, it won't get built.                             │
│                                                                          │
│   GOLDEN RULE #2: SMALL TASKS, BIG DOCUMENTS                            │
│   >100 pages source = XS tasks (1-2 hours each)                        │
│   50-100 pages source = S tasks (2-4 hours each)                       │
│   Small tasks = more checkboxes = nothing lost.                        │
│                                                                          │
│   GOLDEN RULE #3: PROCESS IN CHUNKS, WRITE IMMEDIATELY                  │
│   Read section → Write to enriched file → Next section                  │
│   Don't hold it in memory. Write as you go.                            │
│                                                                          │
│   GOLDEN RULE #4: VERIFY BEFORE PROCEEDING                              │
│   100% PRD coverage or NO PROCEED                                       │
│   100% Tech Spec coverage or NO PROCEED                                │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Phase 3 Sub-Phases

```
┌─────────────────────────────────────────────────────────────────────────┐
│  Phase 3a: CONTRADICTION RESOLUTION & CONSOLIDATION                     │
│  ─────────────────────────────────────────────────                      │
│  • Find contradictions FIRST (before consolidating)                     │
│  • Compare PRD and Tech Spec section-by-section                        │
│  • Log each contradiction with resolution rationale                     │
│  • Fix SOURCE documents (not Jira tasks!)                              │
│  • Then create consolidated spec                                        │
│  Template: contradiction-log-template.md                                │
│  Output: contradiction-log.md, 00-consolidated-spec.md                  │
├─────────────────────────────────────────────────────────────────────────┤
│  Phase 3b: TASK BREAKDOWN                                               │
│  ────────────────────────                                               │
│  • Create Epic → Story → Task hierarchy (NEVER skip Story!)            │
│  • Apply templates from aid-impl-plan/references/templates/            │
│  • Stage in enriched-jiras/*.md files                                  │
│  Templates: epic-template.md, story-template.md, task-template.md       │
│  Output: 01-task-breakdown.md, EPIC-N-enriched.md files                │
├─────────────────────────────────────────────────────────────────────────┤
│  Phase 3c: ENRICHMENT                                                   │
│  ───────────────────                                                    │
│  • Add full content using content-mapping rules                        │
│  • PRD content → Epic description, Story acceptance criteria           │
│  • Tech Spec content → Task technical details                          │
│  • Every Task needs 8 required fields                                  │
│  Reference: content-mapping.md                                          │
│  Output: Fully enriched EPIC-N-enriched.md files                       │
├─────────────────────────────────────────────────────────────────────────┤
│  Phase 3d: JIRA POPULATION                                              │
│  ─────────────────────────                                              │
│  • Push to Jira with proper hierarchy                                  │
│  • Use ADF format for rich descriptions                                │
│  • Link dependencies between issues                                    │
│  Output: All Epics, Stories, Tasks in Jira                             │
├─────────────────────────────────────────────────────────────────────────┤
│  Phase 3e: VERIFICATION                                                 │
│  ──────────────────────                                                 │
│  • Run PRD coverage agent (every user story → Story)                   │
│  • Run Tech Spec coverage agent (every component → Tasks)              │
│  • Gap remediation: add missing, re-verify                             │
│  • 100% coverage required before Phase 4                               │
│  Output: Verification report, 100% coverage                            │
└─────────────────────────────────────────────────────────────────────────┘
```

### Phase 3 Templates (in aid-impl-plan/references/templates/)

| Template | Purpose | When Used |
|----------|---------|-----------|
| `contradiction-log-template.md` | Log PRD/Tech Spec contradictions | Phase 3a |
| `epic-template.md` | Epic format with content mapping | Phase 3b |
| `story-template.md` | Story format with INVEST criteria | Phase 3b |
| `task-template.md` | Task format with 8 required fields | Phase 3b |

### Phase 3 Content Mapping

```
┌─────────────────────────────────────────────────────────────────────────┐
│  SOURCE DOCUMENT              →  TARGET JIRA LEVEL                      │
│  ─────────────────────           ──────────────────                     │
│                                                                          │
│  PRD Product Goals            →  Epic: Business Value                   │
│  PRD User Personas            →  Epic: User Impact                      │
│  PRD Success Metrics          →  Epic: Success Criteria                 │
│  PRD User Stories             →  Story: User Story                      │
│  PRD Acceptance Criteria      →  Story: AC (Gherkin)                    │
│                                                                          │
│  Tech Spec Architecture       →  Epic: Technical Context                │
│  Tech Spec Components         →  Task: Implementation Details           │
│  OpenAPI Endpoints            →  Task: API Contract                     │
│  Prisma Models                →  Task: Database Changes                 │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Task Required Fields (8 Mandatory)

Every task MUST have these 8 fields to be considered complete:

| # | Field | Description |
|---|-------|-------------|
| 1 | Description | What to build and WHY (2-3 sentences) |
| 2 | Files to modify | Exact file paths |
| 3 | Code pattern | Example or snippet to follow |
| 4 | API contract | Method, path, request, response (if API) |
| 5 | Error handling | Table of error cases |
| 6 | Acceptance criteria | Specific, testable outcomes |
| 7 | Size estimate | XS/S/M/L/XL with hours |
| 8 | Tech Spec reference | Section number |

---

## Skill Integration Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    SKILL LOADING SEQUENCE                       │
│                                                                 │
│  1. User Request Received                                       │
│          │                                                      │
│          ▼                                                      │
│  2. phase-enforcement: Check Current Phase                      │
│          │                                                      │
│          ├── Violation? ──▶ BLOCK & Show Violation Template     │
│          │                                                      │
│          ▼                                                      │
│  3. phase-enforcement: Identify Applicable Skills               │
│          │                                                      │
│          ▼                                                      │
│  4. Load Phase-Appropriate Skills                               │
│          │                                                      │
│          ▼                                                      │
│  5. Execute Work with Loaded Skills                             │
│          │                                                      │
│          ▼                                                      │
│  6. Phase Complete? ──▶ Prompt for /aid end                     │
└─────────────────────────────────────────────────────────────────┘
```

---

## Skill Descriptions

### aid-impl-plan (Phase 3)

**Purpose:** Implementation planning with 4 Golden Rules and 5 sub-phases

**Gate Requirement:** Tech Spec approved (Phase 2 complete)

**Capabilities:**
- Contradiction resolution between PRD and Tech Spec
- Epic → Story → Task hierarchy creation
- Content enrichment from source documents
- Jira population with ADF formatting
- Coverage verification (100% required)

**Document Output:**
- `docs/implementation-plan/contradiction-log.md`
- `docs/implementation-plan/00-consolidated-spec.md`
- `docs/implementation-plan/enriched-jiras/*.md`
- All issues in Jira with full details

**Golden Rules:**
```
#1: NO WORD LEFT BEHIND - Every word in source docs appears in Jira
#2: SMALL TASKS, BIG DOCUMENTS - Larger docs = smaller task sizes
#3: PROCESS IN CHUNKS, WRITE IMMEDIATELY - Don't hold in memory
#4: VERIFY BEFORE PROCEEDING - 100% coverage or no Phase 4
```

**Templates:**
```
templates/
├── contradiction-log-template.md  (Phase 3a)
├── epic-template.md               (Phase 3b)
├── story-template.md              (Phase 3b)
└── task-template.md               (Phase 3b - 8 required fields)
```

---

### system-architect (Phase 2+)

**Purpose:** Security-first architecture design with ISO 27001 compliance

**Gate Requirement:** PRD approved (Phase 1 complete)

**Capabilities:**
- Technical specification creation
- Security architecture design
- API contract definition
- Database schema design
- ISO 27001 control mapping

**Document Output:** `docs/tech-spec/YYYY-MM-DD-[feature].md`

**Security Focus:**
```
PRIORITY 1: Security Architecture
- Authentication/Authorization design
- Data classification
- Encryption requirements
- Audit logging

PRIORITY 2: ISO 27001 Compliance
- Control mapping (A.8, A.9, A.10, A.12, A.14, A.18)
- Data handling rules
- Compliance documentation
```

### atomic-design (Phase 4+)

**Purpose:** Build component library following Atomic Design principles

**Gate Requirement:** Tech Spec approved (Phase 2 complete)

**Capabilities:**
- Atom/Molecule/Organism creation
- Design token extraction (via Figma MCP)
- Component documentation
- Storybook integration

**Document Output:** Component files in `src/components/`

**Integration with phase-enforcement:**
```javascript
// Before creating components
if (currentPhase < 4) {
  throw new PhaseViolation(
    "atomic-design requires Phase 4 (Development)",
    "Complete Tech Spec first"
  );
}
```

### code-review (Phase 4+)

**Purpose:** Comprehensive code review for quality assurance

**Gate Requirement:** Implementation Plan approved (Phase 3 complete)

**Capabilities:**
- PR review
- Security vulnerability detection
- Code quality assessment
- Best practice enforcement

**Integration with phase-enforcement:**
```javascript
// Automatic trigger after code changes
if (currentPhase >= 4 && hasCodeChanges()) {
  suggestCodeReview();
}
```

### test-driven (Phase 4+)

**Purpose:** TDD methodology with minimal mocking

**Gate Requirement:** Implementation Plan approved (Phase 3 complete)

**Capabilities:**
- Test-first development
- Coverage analysis
- Fixture patterns
- Integration testing

**Test Output:** Test files in `testing/`

**Integration with phase-enforcement:**
```javascript
// Gate 4 requires passing tests
if (!testsPass()) {
  blockGate4("All tests must pass before QA phase");
}
```

---

## Cross-Skill Communication

Skills can pass information to each other through documents:

```
┌──────────────────────────────────────────────────────────────┐
│              DOCUMENT-BASED COMMUNICATION                    │
│                                                              │
│  Phase 1 (PRD)                                               │
│  └── User Stories ──────────────────────────────────┐        │
│                                                      │        │
│  Phase 2 (Tech Spec) ◀───────────────────────────────┘        │
│  └── API Contracts ─────────────────────────────────┐        │
│  └── Data Models ───────────────────────────────────┤        │
│  └── Security Requirements ─────────────────────────┤        │
│                                                      │        │
│  Phase 3 (Impl Plan) ◀───────────────────────────────┘        │
│  └── Task Breakdown ────────────────────────────────┐        │
│  └── Test Strategy ─────────────────────────────────┤        │
│                                                      │        │
│  Phase 4 (Development) ◀─────────────────────────────┘        │
│  └── Components from atomic-design                           │
│  └── Tests from test-driven                                  │
│  └── Reviews from code-review                                │
└──────────────────────────────────────────────────────────────┘
```

### Information Flow

| From | To | Data | Document |
|------|-----|------|----------|
| PRD | system-architect | User Stories | `docs/prd/*.md` |
| PRD | **aid-impl-plan** | **User Stories, AC** | `docs/prd/*.md` |
| system-architect | **aid-impl-plan** | **API Contracts, Models** | `docs/tech-spec/*.md` |
| system-architect | test-driven | API Contracts | `docs/tech-spec/*.md` |
| system-architect | atomic-design | Data Models | `docs/tech-spec/*.md` |
| **aid-impl-plan** | Jira | **Epics, Stories, Tasks** | `docs/implementation-plan/enriched-jiras/*.md` |
| Implementation Plan | code-review | Exit Criteria | `docs/implementation-plan/*.md` |

### Phase 3 Information Flow (Detailed)

```
┌────────────────────────────────────────────────────────────────────────────┐
│                    PHASE 3 CONTENT FLOW                                    │
│                                                                            │
│  ┌─────────────┐                              ┌─────────────────────────┐  │
│  │    PRD      │────────────────────────────►│        EPIC             │  │
│  │             │    Product Goals            │  Business Value         │  │
│  │ User Stories│    User Personas           │  User Impact            │  │
│  │ Acceptance  │    Success Metrics          │  Success Criteria       │  │
│  │ Criteria    │                             └──────────┬──────────────┘  │
│  └─────────────┘                                        │                 │
│        │                                                ▼                 │
│        │                                     ┌─────────────────────────┐  │
│        └─────────────────────────────────────►        STORY            │  │
│             User Stories                     │  As/I want/So that      │  │
│             Acceptance Criteria              │  Gherkin AC             │  │
│                                              │  Technical Notes        │  │
│                                              └──────────┬──────────────┘  │
│  ┌─────────────┐                                        │                 │
│  │  Tech Spec  │                                        ▼                 │
│  │             │                             ┌─────────────────────────┐  │
│  │ Architecture│──────────────────────────────►       TASK             │  │
│  │ Components  │    Implementation Details   │  8 Required Fields      │  │
│  │ API Defs    │    API Contracts           │  ├─ Description          │  │
│  │ Data Models │    Error Handling          │  ├─ Files to modify      │  │
│  │ Prisma      │                             │  ├─ Code pattern         │  │
│  └─────────────┘                             │  ├─ API contract         │  │
│                                              │  ├─ Error handling       │  │
│                                              │  ├─ Acceptance criteria  │  │
│                                              │  ├─ Size estimate        │  │
│                                              │  └─ Tech Spec reference  │  │
│                                              └─────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## Skill Conflict Resolution

When multiple skills could apply, phase-enforcement determines priority:

```
┌──────────────────────────────────────────────────────────────┐
│              SKILL PRIORITY RULES                            │
│                                                              │
│  1. phase-enforcement ALWAYS runs first                      │
│     └── Validates phase before any work                      │
│                                                              │
│  2. Document-producing skills run before code skills         │
│     └── system-architect before atomic-design                │
│                                                              │
│  3. test-driven runs alongside code skills                   │
│     └── Tests written with or before implementation          │
│                                                              │
│  4. code-review runs after code changes                      │
│     └── Triggered by PR or explicit request                  │
└──────────────────────────────────────────────────────────────┘
```

---

## Feedback Loop

All skills contribute to the feedback system:

```
┌──────────────────────────────────────────────────────────────┐
│           SKILL-SPECIFIC FEEDBACK QUESTIONS                  │
│                                                              │
│  system-architect (Phase 2):                                 │
│  - "How clear was the architecture design?"                  │
│  - "Was security adequately addressed?"                      │
│  - "Were API contracts well-defined?"                        │
│                                                              │
│  aid-impl-plan (Phase 3):                                    │
│  - "Were contradictions identified before consolidation?"    │
│  - "Was the Epic → Story → Task hierarchy correct?"          │
│  - "Did tasks have all 8 required fields?"                   │
│  - "Was 100% PRD/Tech Spec coverage achieved?"               │
│  - "Could a developer work from tasks independently?"        │
│                                                              │
│  atomic-design (Phase 4):                                    │
│  - "How reusable are the components?"                        │
│  - "Was the design token extraction helpful?"                │
│  - "Is the component hierarchy clear?"                       │
│                                                              │
│  code-review (Phase 4-5):                                    │
│  - "Were reviews thorough?"                                  │
│  - "Did reviews catch important issues?"                     │
│  - "Was feedback actionable?"                                │
│                                                              │
│  test-driven (Phase 4-5):                                    │
│  - "Did TDD improve code quality?"                           │
│  - "Were tests comprehensive?"                               │
│  - "Was coverage adequate?"                                  │
└──────────────────────────────────────────────────────────────┘
```

### Skill Improvement Targets

```json
{
  "system-architect": {
    "target_rating": 4.0,
    "current_rating": 3.8,
    "improvement_focus": ["error handling", "more examples"]
  },
  "aid-impl-plan": {
    "target_rating": 4.5,
    "current_rating": 4.5,
    "improvement_focus": ["contradiction detection accuracy"]
  },
  "atomic-design": {
    "target_rating": 4.0,
    "current_rating": 4.2,
    "improvement_focus": ["documentation"]
  },
  "code-review": {
    "target_rating": 4.0,
    "current_rating": 3.5,
    "improvement_focus": ["security checks", "performance review"]
  },
  "test-driven": {
    "target_rating": 4.0,
    "current_rating": 4.0,
    "improvement_focus": []
  }
}
```

---

## Commands

| Command | Description |
|---------|-------------|
| `/skills` | List available skills for current phase |
| `/skills --all` | List all skills with phase requirements |
| `/skill load [name]` | Manually load a skill (phase-checked) |
| `/aid status` | Show skill usage and feedback status |
