# AID - AI Development Methodology

## ⚠️ CRITICAL: Phase Gate Enforcement

Before doing ANY work, Claude MUST:
1. Read `.aid/state.json` to determine current phase
2. Read `.aid/context.json` to understand current task/step
3. Verify requested work is allowed in current phase
4. **REFUSE work that belongs to a later phase**

### Phase Permissions

| Phase | Allowed | Blocked |
|-------|---------|---------|
| 1 PRD | Requirements, scope, user stories | Code, architecture, Jira |
| 2 Tech Spec | + Architecture, schemas, APIs | Code, Jira issues |
| 3 Breakdown | + Jira epics, stories, tasks | Production code |
| 4 Development | + Code, tests, components | Deployment |
| 5 QA & Ship | Everything | - |

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

### Testing
| Command | Purpose |
|---------|---------|
| `/aid-test` | Run full methodology test suite with simulated approvals |

### Phase Management ⭐
| Command | Purpose |
|---------|---------|
| `/aid-init` | Initialize project with AID phases + memory system |
| `/aid-start` | Start work session - select role & phase |
| `/aid-status` | Show current state (phase + session) |
| `/aid-end` | End phase and provide feedback |
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
| 2 | `skills/system-architect/` |
| 4 | `skills/atomic-design/`, `skills/atomic-page-builder/` |
| 4-5 | `skills/code-review/`, `skills/test-driven/` |
| All | `skills/phase-enforcement/`, `skills/context-tracking/` |

---

## Key Files

```
.aid/state.json      - Phase state (which phase we're in)
.aid/context.json    - Work context (current task, step, progress)
docs/PRD.md          - Product requirements
docs/TECH-SPEC.md    - Technical specification
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
2. **Start**: `/aid-start` → Select role (PM/Dev/QA/Lead) → Select phase → Skills loaded
3. **Work**: Claude applies loaded skills automatically
4. **End**: `/aid-end` → Rate session (1-5) → Describe what worked/didn't
5. **Learn**: `/aid-improve` → Analyze feedback → Update skills

### Skills Location

**Primary Skills** (Source of truth):
- `.claude/skills/` - All skill definitions and prompts

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
