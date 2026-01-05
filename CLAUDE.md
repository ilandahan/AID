# AID - AI Development Methodology

## ⚠️ FOUNDATIONAL LAYER: WHY-First Thinking

> "People don't buy what you do; they buy why you do it." — Simon Sinek

**BEFORE any command, any phase, any action — understand WHY.**

### Prompt Analysis Protocol (Runs First, Always)

```
┌─────────────────────────────────────────────────────────────┐
│  EVERY PROMPT → WHY ANALYSIS → PHASE CHECK → THEN PROCEED  │
└─────────────────────────────────────────────────────────────┘
```

1. **Extract Explicit WHY** — What did the user state as their goal?
2. **Infer Implicit WHY** — What underlying need might they not have articulated?
3. **Validate or Ask** — Is the WHY clear enough? If not, ASK before proceeding.
4. **Anchor to WHY** — Every output must trace back to the established WHY.

### Golden Rules (Always Do)

| Rule | Description |
|------|-------------|
| Ask WHY before acting | Even simple requests have underlying motivations |
| Dig deeper with 5 Whys | First answer is rarely the root cause |
| State the WHY explicitly | Make motivation visible in all outputs |
| Validate understanding | Reflect back the WHY before proceeding |
| Connect to purpose | Every choice traces to the WHY |

### Iron Rules (Never Break)

| Rule | Description |
|------|-------------|
| Never implement without purpose | "Just do it" is not acceptable |
| Never copy without understanding | "Competitor has it" needs WHY validation |
| Never skip WHY in reviews | Every PR shows intent, not just changes |
| Never let urgency bypass purpose | "It's urgent" requires WHY more, not less |
| Never assume shared understanding | Implicit WHY leads to misalignment |

### 3-Second WHY Check

Before ANY action:

| ✓ | Question |
|---|----------|
| □ | WHY am I doing this? |
| □ | WHAT value does it create? |
| □ | WHO benefits? |

Can't answer in 3 seconds → **STOP and clarify.**

### Red Flags — Stop and Ask

| Signal | Ask |
|--------|-----|
| "Just do it" | "What problem does this solve?" |
| "Everyone wants it" | "Why specifically?" |
| "Competitor has it" | "Does our purpose require it?" |
| "It's urgent" | "What's the cost of not doing it?" |
| "Make it better" | "What does 'better' mean here?" |
| "Trust me" | "Help me understand the reasoning" |

---

## ⚠️ CRITICAL: Phase Gate Enforcement

After WHY is established, Claude MUST:
1. Read `.aid/state.json` to determine current phase
2. Read `.aid/context.json` to understand current task/step
3. Verify requested work is allowed in current phase
4. **REFUSE work that belongs to a later phase**

### 6-Phase Lifecycle

```
Phase 0 ──► Phase 1 ──► Phase 2 ──► Phase 3 ──► Phase 4 ──► Phase 5
Discovery     PRD      Tech Spec   Impl Plan     Dev       QA & Ship
```

### Phase-Specific WHY Questions

| Phase | Core WHY Question |
|-------|-------------------|
| 0 Discovery | "WHY is this problem worth solving?" |
| 1 PRD | "WHY does the user need this?" |
| 2 Tech Spec | "WHY this architecture?" |
| 3a Consolidation | "WHY does this contradiction exist? WHY this resolution?" |
| 3b Breakdown | "WHY this task size? WHY these dependencies?" |
| 3c Jira Population | "WHY is this information complete? WHY can dev work from this alone?" |
| 4 Development | "WHY this code? WHY these connections?" |
| 5 QA & Ship | "WHY is this test? WHY is this ready?" |

### Phase Permissions

| Phase | Allowed | Blocked |
|-------|---------|---------|
| 0 Discovery | Research, stakeholders, competitive analysis | PRD, architecture, code |
| 1 PRD | + Requirements, scope, user stories | Architecture, code, Jira |
| 2 Tech Spec | + Architecture, schemas, APIs | Code, Jira issues |
| 3a Consolidation | + Contradiction resolution, consolidate specs | Jira issues, code |
| 3b Breakdown | + Task decomposition, sprint planning | Jira creation, code |
| 3c Jira Population | + Jira epics, stories, tasks with full info | Production code |
| 4 Development | + Code, tests, components | Deployment |
| 5 QA & Ship | Everything | - |

---

## 🔍 Transparent Quality Check (AUTOMATIC)

Every significant output MUST go through self-reflection before being shown to the user.
The Quality Check box is ALWAYS displayed to build trust and ensure consistent quality.

### Core Flow

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   Prompt    │ ───► │   Draft     │ ───► │  Reflect    │ ───► │   Output    │
└─────────────┘      └─────────────┘      └─────────────┘      └─────────────┘
                      (internal)          (score & revise)    (with QC box)
```

### When to Apply

| Apply Quality Check | Skip Quality Check |
|---------------------|-------------------|
| ✅ Code generation | ❌ Simple questions |
| ✅ Architecture decisions | ❌ Status checks |
| ✅ PRD/requirements | ❌ File reading |
| ✅ Technical specs | ❌ Clarifying questions |
| ✅ Test writing | ❌ Command help |

### Quality Check Display Format

**ALWAYS show this box before significant outputs:**

```
╭─────────────────────────────────────────────────────────────╮
│ 🔍 Quality Check                                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  [✅|⚠️|❌] WHY Alignment     X/10   [brief note]           │
│  [✅|⚠️|❌] Phase Compliance  X/10   [brief note]           │
│  [✅|⚠️|❌] Correctness       X/10   [brief note]           │
│  [✅|⚠️|❌] Security          X/10   [brief note]           │
│  [✅|⚠️|❌] Completeness      X/10   [brief note]           │
│                                                             │
│  ══════════════════════════════════════════════════════    │
│  📊 Overall: X.X/10                                         │
│  [STATUS: ✅ PASSED | 🔄 PASSED after N revision(s) | ⚠️]   │
│                                                             │
│  [If revised: 📝 Improvements made: ...]                    │
│                                                             │
╰─────────────────────────────────────────────────────────────╯
```

### Score Icons

| Score | Icon | Action |
|-------|------|--------|
| 8-10 | ✅ | Excellent - show output |
| 6-7.9 | ⚠️ | Acceptable - show with notes |
| 0-5.9 | ❌ | Revise internally (up to 3 times) |

### Criteria (Weight)

1. **WHY Alignment (3)** - Does output serve user's actual need?
2. **Phase Compliance (2)** - Appropriate for current phase?
3. **Correctness (3)** - Accurate, functional, no errors?
4. **Security (2)** - No vulnerabilities or exposed secrets?
5. **Completeness (2)** - All requirements addressed?

### Revision Display

When a score improved due to revision, show:
```
│  ⚠️  Security         5→8/10 Fixed: Added input validation  │
```

### Quality Commands

| Command | Purpose |
|---------|---------|
| `/reflect` | Show detailed breakdown of last quality check |
| `/reflect --history` | Show all quality checks from session |
| `/reflect --strict` | Re-evaluate with threshold 8 |
| `/reflect --explain <criterion>` | Deep dive into specific score |

### Phase-Specific Criteria

Detailed criteria for each phase in:
`.claude/skills/reflection/criteria/phase-{N}-{name}.yaml`

---

## Code Generation Standards (Phase 4+)

### Every Function Must Include WHY:

```python
# ─────────────────────────────────────────────────
# WHY: [Problem this function solves]
# WHAT: [What it does]
# CONNECTION: [What calls it, what it calls]
# ─────────────────────────────────────────────────
def function_name(params):
    """
    Brief description.
    
    WHY param_x: [Why this parameter exists]
    WHY return_type: [Why caller needs this]
    """
```

### Every Component Must Document Connections:

```python
"""
ComponentName

WHY THIS EXISTS:
[Core purpose and problem it solves]

CONNECTIONS:
- CALLED BY: [List callers and WHY they call this]
- CALLS: [List dependencies and WHY we need them]

DESIGN DECISIONS:
- WHY [decision]: [Reasoning]
"""
```

### Component Relationship Pattern:

```
┌─────────────────┐     WHY: Decouple UI from data fetching
│   UserProfile   │────────────────────────────────────────┐
└────────┬────────┘                                        │
         │ WHY: Single source of truth for user state      │
         ▼                                                 │
┌─────────────────┐     WHY: Cache reduces API calls       │
│   UserStore     │◄───────────────────────────────────────┤
└────────┬────────┘                                        │
         │ WHY: Normalize data once at entry point         │
         ▼                                                 │
┌─────────────────┐     WHY: Abstract API versioning
│   UserAPI       │
└─────────────────┘
```

---

## Testing Standards (Phase 4-5) — BDD/TDD Integration

### Every Test Must State WHY:

```python
def test_specific_behavior():
    """
    WHY THIS TEST:
    - PROBLEM: [What failure this prevents]
    - COST OF FAILURE: [Business/user impact]
    - SUCCESS: [What passing means]
    """
```

### BDD - Gherkin with WHY:

```gherkin
Feature: Feature Name
  """
  WHY: [Business value and user need]
  IMPACT: [What happens if this fails]
  """
  
  Scenario: Scenario Name
    """
    WHY: [Why this specific scenario matters]
    """
    Given [context]
    When [action]
    Then [outcome]
```

### Test Organization by WHY (Cost of Failure):

```
tests/
├── critical_failures/      # High cost - test first
├── user_experience/        # Medium cost
└── edge_cases/            # Low frequency
```

---

## Commands

### First Time Setup 🆕
| Command | Purpose |
|---------|---------|
| `/setup` | **Complete guided setup** - walks through entire installation step-by-step |
| `/link-project` | **Link existing project** - connect a project folder to AID via symbolic links |

### Daily Workflow ⭐
| Command | Purpose |
|---------|---------|
| `/good-morning` | Morning startup - check systems, load context, continue |
| `/context` | Show current work context (tasks + steps) |
| `/context-update` | Update context manually |
| `/reflect` | Show detailed breakdown of last quality check |

### Testing
| Command | Purpose |
|---------|---------|
| `/aid-test` | Run full AID test (Phases 0-2) with reflection validation |
| `/aid-test --phase 0` | Test only Phase 0 |
| `/aid-test --quick` | Abbreviated test (1 output per phase) |
| `/aid-test --verbose` | Show all reflection details |

### Phase Management ⭐
| Command | Purpose |
|---------|---------|
| `/aid-init` | Initialize project with AID phases + memory system |
| `/aid-start` | Start work session - select role & phase (0-5) |
| `/aid-status` | Show current state (phase + session) |
| `/aid-end` | End phase and provide feedback |
| `/discovery` | **Start Phase 0** - research and validation |
| `/phase` | Show current phase status |
| `/gate-check` | Check if ready to advance |
| `/phase-approve` | Human sign-off for current phase |
| `/phase-advance` | Move to next phase |

### Development Commands
| Command | Skill | Purpose |
|---------|-------|---------|
| `/design-system` | atomic-design | Build design system from Figma |
| `/build-page` | atomic-page-builder | Compose pages from components |
| `/architecture` | system-architect | System architecture design |
| `/code-review` | code-review | Review code quality |
| `/write-tests` | test-driven | TDD test writing |
| `/test-review` | test-driven | Review test quality |
| `/qa-ship` | aid-qa-ship | QA validation and release |
| `/prd` | - | Create PRD from requirements |
| `/tech-spec` | - | Create technical specification |
| `/jira-breakdown` | - | Break spec into Jira issues |
| `/start-project` | - | Initialize new project |

---

## Context Tracking

Claude MUST update `.aid/context.json` when:
- Starting a new task
- Completing a step  
- Significant progress is made
- Session ends

---

## Skills by Phase

| Phase | Load These Skills |
|-------|-------------------|
| ALL | `skills/why-driven-decision/` **(FOUNDATIONAL - Load First)** |
| ALL | `skills/reflection/` **(Quality Check - Always Active)** |
| 0 | `skills/pre-prd-research/`, `skills/aid-discovery/`, `skills/nano-banana-visual/` |
| 1 | `skills/aid-prd/` |
| 2 | `skills/system-architect/`, `skills/aid-tech-spec/` |
| 3 | `skills/aid-impl-plan/` **(Consolidation → Breakdown → Jira)** |
| 4 | `skills/atomic-design/`, `skills/atomic-page-builder/` |
| 4-5 | `skills/code-review/`, `skills/test-driven/` |
| All | `skills/phase-enforcement/`, `skills/context-tracking/` |

---

## Key Files

```
.aid/state.json      - Phase state (starts at Phase 0: Discovery)
.aid/context.json    - Work context (current task, step, progress)
docs/research/       - Phase 0 outputs (research-report.md, traceability-matrix.md)
docs/prd/            - Phase 1 outputs (Product requirements)
docs/tech-spec/      - Phase 2 outputs (Technical specification)
docs/implementation-plan/ - Phase 3 outputs (Task breakdown)
```

---

## Quick Start

### For Non-Technical Users (Recommended)
```
Just open Claude Code in this folder and type:
/setup
```
This will guide you through everything step-by-step.

### For Technical Users
```bash
# Run install script
./install.sh

# Initialize new project
./scripts/init-project.sh my-app
cd my-app

# Every morning
/good-morning

# Or initialize phases manually
/aid-init
```

---

## Documentation

- Phase system: `docs/PHASE-GATES.md`
- Context tracking: `docs/WORK-CONTEXT-TRACKER.md`
- Daily workflow: `docs/MORNING-STARTUP.md`
- Components: `skills/atomic-design/references/`
- Testing: `skills/test-driven/references/`
- **WHY Framework: `skills/why-driven-decision/`**

---

## Memory & Learning System

AID includes a learning system that improves Claude's assistance over time.

### Learning Mode Commands

| Command | Description |
|---------|-------------|
| `/aid-improve` | Run learning cycle (weekly) |
| `/aid-memory` | Manage Claude Memory entries |
| `/aid-reset` | Reset memory system |
| `/aid-analyze` | Full quality analysis with metrics and patterns |
| `/aid-dashboard` | Generate quality dashboard report |
| `/aid-recommendations` | View/manage skill update recommendations |

### Sub-Agent CLI

```bash
# Run quality analysis
python -m memory_system --analyze

# Generate dashboard
python -m memory_system --dashboard --days 14

# Sync learnings to memory
python -m memory_system --sync-memory

# Show status
python -m memory_system --status
```

### Session Flow

1. **Init**: `/aid-init` → Creates project state + memory system
2. **Start**: `/aid-start` → Select role FIRST → Then select phase with role-specific terminology → Skills loaded
3. **WHY Check**: Before any work, establish WHY (automatic)
4. **Work**: Claude applies loaded skills automatically
5. **End**: `/aid-end` → Rate session (1-5) → Describe what worked/didn't
6. **Learn**: `/aid-improve` → Analyze feedback → Update skills

### Role-Based Phase Terminology

Phases are displayed using **role-specific language** so each persona sees familiar terms:

| Phase | PM | Tech Lead | Developer | QA |
|-------|-----|-----------|-----------|-----|
| 0 | Market & Competitive Research | Technology & Architecture Research | Technical Spike & Research | Test Strategy Research |
| 1 | Product Requirements (PRD) | Technical Requirements Report | Feature Specification | Test Requirements & Coverage Plan |
| 2 | Solution Review | System Architecture Design | Technical Design | Test Architecture & Framework |
| 3 | Roadmap & Prioritization | Sprint Planning & Task Breakdown | Task Breakdown & Estimation | Test Plan & Case Design |
| 4 | Feature Validation & UAT | Code Review & Architecture Oversight | Implementation & Coding | Test Execution & Automation |
| 5 | Launch & Go-to-Market | Release Engineering & Deployment | Bug Fixes & Polish | Release Certification & Sign-off |

Terminology mapping defined in: `.claude/references/role-phase-terminology.json`

### Skills Location

**Primary Skills** (Source of truth):
- `.claude/skills/` - All skill definitions and prompts
- `.claude/skills/why-driven-decision/` - **Foundational WHY skill (loads first)**

**Memory System** (References + learnings):
- `memory-system/skills/roles/{role}/` - Quick reference + cumulative learnings
- `memory-system/skills/phases/{phase}/` - Quick reference + cumulative learnings

Claude loads skills from `.claude/skills/` based on role and phase.

### Runtime State

- Project state: `.aid/state.json` (phase tracking)
- Session state: `~/.aid/state.json` (role, session info)
- Feedback: `~/.aid/feedback/pending/`

### Memory System Documentation

Full documentation: `memory-system/docs/`

---

## Appendix: The 5 Whys Technique

When WHY isn't clear, dig deeper:

```
Statement: "We need a dashboard"
  Why? → "To see metrics"
  Why? → "To track performance"
  Why? → "To make better decisions"
  Why? → "Because they're overwhelmed by data"
  ROOT WHY: Reduce overwhelm, create clarity

→ The real solution may not be a dashboard at all.
```

---

## Appendix: WHY Statement Template

After discovery, articulate clearly:

```
We believe that [CORE BELIEF].
Therefore, we [HOW WE ACT ON IT].
Which results in [WHAT WE CREATE].
```

**AID's WHY:**
```
We believe that great software comes from understanding purpose before writing code.
Therefore, we enforce phase gates and WHY analysis at every step.
Which results in products that solve real problems, not just implement features.
```