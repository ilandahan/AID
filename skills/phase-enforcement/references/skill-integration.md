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
│  Phase 3: Implementation Plan                                   │
│  └── system-architect (planning support)                        │
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
| atomic-design | - | - | - | ✓ | - |
| code-review | - | - | - | ✓ | ✓ |
| test-driven | - | - | - | ✓ | ✓ |
| phase-enforcement | ✓ | ✓ | ✓ | ✓ | ✓ |

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
| system-architect | test-driven | API Contracts | `docs/tech-spec/*.md` |
| system-architect | atomic-design | Data Models | `docs/tech-spec/*.md` |
| Implementation Plan | code-review | Exit Criteria | `docs/implementation-plan/*.md` |

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
