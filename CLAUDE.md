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

### Daily Workflow ⭐
| Command | Purpose |
|---------|---------|
| `/good-morning` | Morning startup - check systems, load context, continue |
| `/context` | Show current work context (tasks + steps) |
| `/context-update` | Update context manually |

### Phase Management ⭐
| Command | Purpose |
|---------|---------|
| `/aid-init` | Initialize project with AID phases |
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

```bash
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
