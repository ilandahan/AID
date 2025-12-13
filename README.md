# AID - AI Development Methodology

<div align="center">

**Transform raw requirements into production-ready software using Claude Code**

[![Claude Code](https://img.shields.io/badge/Claude-Code-orange)](https://claude.ai)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

*A complete AI-powered software development lifecycle framework*

*Created by Ilan Dahan*

</div>

---

## What is AID?

AID (AI Development Methodology) is a comprehensive framework that guides you through the **entire software development process** - from a raw idea to production-ready code. It works with Claude Code to provide structure, enforce best practices, and maintain context across sessions.

**No coding experience required** - AID guides you step by step.

---

## Key Features

### Phase Gate System
Structured development through 5 enforced phases:

```
Phase 1 ──► Gate ──► Phase 2 ──► Gate ──► Phase 3 ──► Gate ──► Phase 4 ──► Gate ──► Phase 5
  PRD        ✓      Tech Spec     ✓      Breakdown     ✓        Dev          ✓      QA & Ship
```

| Phase | What Happens | Output |
|-------|--------------|--------|
| **1. PRD** | Define requirements, user stories, scope | Product Requirements Doc |
| **2. Tech Spec** | Architecture, database design, APIs | Technical Specification |
| **3. Breakdown** | Jira epics, stories, task estimates | Task Breakdown |
| **4. Development** | TDD, code implementation | Working Code |
| **5. QA & Ship** | Testing, review, deployment | Production Release |

**Phase gates prevent skipping ahead** - you can't write code until requirements are approved.

---

### Context Tracking - Never Lose Your Place
AID remembers exactly where you left off:

```
═══════════════════════════════════════════════════════
📍 WHERE YOU LEFT OFF
═══════════════════════════════════════════════════════

TASKS:
  ✅ Previous: PROJ-123 "Create Button atom"
  🔄 Current:  PROJ-124 "Create FormField molecule"
  ⏳ Next:     PROJ-125 "Create Card molecule"

CURRENT TASK PROGRESS:
  ✅ Step 1: Write tests - DONE
  🔄 Step 2: Implement component - 50%
     └─ "Label and input done, error handling next"
  ⏳ Step 3: Style with tokens
═══════════════════════════════════════════════════════
```

---

### Morning Startup Routine
One command to start your day:

```
/good-morning
```

This automatically:
- Checks all systems (Docker, MCPs, integrations)
- Loads your project state
- Shows yesterday's progress
- Asks where to continue

---

### Learning & Improvement System
AID gets smarter over time by learning from your feedback:

```
Session Flow:
1. /aid-init     → Initialize project
2. /aid-start    → Select role (PM/Dev/QA/Lead) + phase
3. Work          → Claude applies relevant skills
4. /aid-end      → Rate session (1-5), describe what worked
5. /aid-improve  → System learns and updates skills
```

**Pattern Detection**: After 10+ sessions, AID identifies what works and what doesn't, then updates its recommendations.

---

### Role-Based Skills
Different guidance for different roles:

| Role | Focus Areas |
|------|-------------|
| **Product Manager** | Requirements, user stories, scope definition |
| **Developer** | Implementation, code quality, TDD |
| **QA Engineer** | Test strategy, validation, quality gates |
| **Tech Lead** | Architecture, reviews, technical direction |

---

### Design System Automation (Atomic Design)
Build pixel-perfect UIs from Figma designs:

```
Figma → Design Tokens → Components → Pages
```

**Component Hierarchy**:
- **Atoms**: Button, Input, Label, Icon
- **Molecules**: FormField, Card, SearchBar
- **Organisms**: Header, Sidebar, DataTable
- **Templates**: Page layouts
- **Pages**: Complete screens

**Figma MCP Integration**: Extract colors, typography, and spacing directly from Figma files.

---

### Test-Driven Development (TDD)
Write tests first, then implement:

```
1. Write failing test
2. Write minimal code to pass
3. Refactor
4. Repeat
```

**TDD Guidance Includes**:
- Test patterns and anti-patterns
- Minimal mocking strategies
- Integration testing approaches
- Coverage requirements (70%+ default)

---

### Code Review Automation
Comprehensive review checklist:

- Code quality and patterns
- Security vulnerabilities (OWASP Top 10)
- Test coverage verification
- Performance considerations
- Accessibility compliance

---

### Decision Transparency
See the reasoning behind every major decision:

```markdown
**Decision:** Using PostgreSQL with Prisma ORM

**Reasoning:**
- Data relationships: Complex hierarchy benefits from relational model
- ACID compliance: Financial data requires strong guarantees
- Query flexibility: Reporting features need complex joins

**Alternatives Considered:**
1. MongoDB - Rejected: Would require complex denormalization
2. MySQL - Viable but PostgreSQL has better JSON support

**Confidence:** High - Clear fit for requirements
**Open to Debate:** Yes - Could discuss if team prefers different stack
```

---

### MCP Integrations
Built-in connections to your tools:

| Integration | Purpose |
|-------------|---------|
| **Jira** | Task management, epics, stories |
| **GitHub** | Repository, PRs, issues |
| **Figma** | Design tokens, component specs |
| **Chrome DevTools** | UI testing, performance audits |

---

## Available Commands

### Daily Workflow
| Command | Description |
|---------|-------------|
| `/good-morning` | Morning startup - check systems, load context |
| `/context` | Show current work context |
| `/context-update` | Update context manually |

### Phase Management
| Command | Description |
|---------|-------------|
| `/aid-init` | Initialize project with phases |
| `/aid-start` | Start session - select role & phase |
| `/aid-status` | Show current state |
| `/phase` | Show current phase status |
| `/gate-check` | Check if ready to advance |
| `/phase-approve` | Human sign-off for phase |
| `/phase-advance` | Move to next phase |

### Development
| Command | Description |
|---------|-------------|
| `/prd` | Create Product Requirements Document |
| `/tech-spec` | Create Technical Specification |
| `/jira-breakdown` | Break spec into Jira issues |
| `/design-system` | Build design system from Figma |
| `/build-page` | Compose pages from components |
| `/write-tests` | Write tests (TDD methodology) |
| `/code-review` | Review code quality |

### Learning System
| Command | Description |
|---------|-------------|
| `/aid-end` | End phase and provide feedback |
| `/aid-improve` | Run learning cycle |
| `/aid-memory` | Manage Claude Memory entries |
| `/aid-analyze` | Full quality analysis |

---

## Tech Stack Support

| Layer | Technologies |
|-------|--------------|
| **Frontend** | Next.js, React, TypeScript, SCSS |
| **Backend** | Node.js, Next.js API Routes |
| **Database** | PostgreSQL (Docker or local) |
| **Testing** | Jest, Testing Library, Supertest |
| **Deployment** | Docker, Docker Compose |

---

## Skills System

AID uses specialized "skills" - AI sub-agents with domain expertise:

### Core Skills (Always Active)
- `phase-enforcement` - Enforces phase gates
- `context-tracking` - Tracks tasks and progress
- `learning-mode` - Transparent decisions, feedback collection

### Development Skills
- `atomic-design` - Figma-to-code component system
- `atomic-page-builder` - Page composition from components
- `system-architect` - Architecture and API design
- `code-review` - Quality and security review
- `test-driven` - TDD methodology and test quality

### Phase Skills
- `aid-discovery` - Problem validation (Phase 0)
- `aid-prd` - Requirements writing (Phase 1)
- `aid-tech-spec` - Technical specification (Phase 2)
- `aid-development` - Implementation guidance (Phase 4)
- `aid-qa-ship` - QA and release (Phase 5)

---

## Project Structure

```
AID/
├── .claude/
│   ├── commands/          # Slash commands (/good-morning, /phase, etc.)
│   └── skills/            # Skill definitions and references
├── docs/
│   ├── PHASE-GATES.md     # Phase system documentation
│   ├── MORNING-STARTUP.md # Daily workflow guide
│   └── WORK-CONTEXT-TRACKER.md
├── memory-system/         # Learning and improvement system
├── integrations/          # MCP setup guides (Jira, GitHub, Figma)
├── templates/             # PRD and state templates
└── scripts/               # Automation scripts
```

---

## How It Works

### For Non-Technical Users
1. Open Claude Code in this folder
2. Type `/setup` and follow the prompts
3. Describe what you want to build
4. AID guides you through each phase

### For Teams
1. Clone AID repository
2. Create symbolic links from your project
3. All team members share the same methodology
4. Update AID centrally, all projects get updates

---

## Getting Started

**[Installation Guide](INSTALLATION.md)** - Complete setup instructions for all skill levels

Quick start:
```
# Open Claude Code in this folder
/setup
```

---

## Why AID?

| Problem | AID Solution |
|---------|--------------|
| AI generates code without context | Phase gates ensure requirements before code |
| Losing track across sessions | Context tracking remembers everything |
| Inconsistent code quality | Enforced TDD and code review |
| Design-dev mismatch | Figma integration with design tokens |
| No learning from mistakes | Feedback system improves over time |
| Scope creep | Phase gates and approved PRDs |

---

## Documentation

- [Installation Guide](INSTALLATION.md) - Setup for all skill levels
- [Phase Gates](docs/PHASE-GATES.md) - Phase system details
- [Morning Startup](docs/MORNING-STARTUP.md) - Daily workflow
- [Context Tracking](docs/WORK-CONTEXT-TRACKER.md) - How context is maintained
- [Memory System](memory-system/docs/USER-GUIDE.md) - Learning system guide

---

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing`)
3. Write tests first (TDD approach)
4. Commit changes (`git commit -m 'Add amazing feature'`)
5. Push to branch (`git push origin feature/amazing`)
6. Open Pull Request

---

## Author

Created by **Ilan Dahan**

Built with [Claude Code](https://claude.ai) by Anthropic.

---

## License

MIT License - see [LICENSE](LICENSE) for details.
