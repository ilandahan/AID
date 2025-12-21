# AID - AI Development Methodology

<div align="center">

**Transform raw requirements into production-ready software using Claude Code**

[![Claude Code](https://img.shields.io/badge/Claude-Code-orange)](https://claude.ai)
[![License](https://img.shields.io/badge/License-AID%20Community%20v1.0-blue.svg)](LICENSE)
[![MCP Integrations](https://img.shields.io/badge/MCP-6%20Integrations-green)](#mcp-integrations)
[![Skills](https://img.shields.io/badge/Skills-21%20Specialized-purple)](#skills-system)

*A complete AI-powered software development lifecycle framework*

*Created by Ilan Dahan*

</div>

---

## Table of Contents

- [What is AID?](#what-is-aid)
- [Research & Methodology](#research--methodology)
- [Key Features](#key-features)
- [Phase Gate System](#phase-gate-system)
- [MCP Integrations](#mcp-integrations)
- [Nano Banana Pro (Visual AI)](#nano-banana-pro-visual-ai)
- [Skills System (21 Skills)](#skills-system)
- [Commands Reference (25 Commands)](#commands-reference)
- [Quick Start](#quick-start)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Documentation](#documentation)

---

## What is AID?

AID (AI Development Methodology) is a comprehensive framework that guides you through the **entire software development process** - from a raw idea to production-ready code. It works with Claude Code to provide structure, enforce best practices, and maintain context across sessions.

**No coding experience required** - AID guides you step by step.

### The Problem AID Solves

| Problem | AID Solution |
|---------|--------------|
| AI generates code without context | Phase gates enforce requirements before code |
| Losing track across sessions | Context tracking remembers everything |
| Inconsistent code quality | Enforced TDD and mandatory code review |
| Design-dev mismatch | Figma integration with design tokens |
| No learning from mistakes | Feedback system improves over time |
| Scope creep | Phase gates and approved PRDs prevent expansion |
| Skipping important steps | Mandatory phase transitions with sub-agent review |

---

## Research & Methodology

### The Core Insight

Traditional AI coding assistants generate code reactively without understanding the full context. This leads to:
- Code that doesn't match requirements
- Inconsistent architecture decisions
- Security vulnerabilities from lack of planning
- Wasted effort from scope creep

### AID's Approach

AID enforces a **structured, phase-gated methodology** inspired by proven software engineering practices:

1. **Document-Driven Development**: Every line of code traces back to approved requirements
2. **Phase Gates**: Quality checkpoints prevent premature advancement
3. **Role-Based Guidance**: Different skills for PM, Dev, QA, and Tech Lead perspectives
4. **Continuous Learning**: Feedback loops improve the system over time
5. **Context Preservation**: Never lose your place across sessions

### Key Principles

| Principle | Implementation |
|-----------|----------------|
| **Requirements First** | No code until PRD is approved |
| **Security by Design** | OWASP Top 10 and ISO 27001 built into architecture phase |
| **Test-Driven Development** | Write tests before implementation |
| **Design System Fidelity** | Figma is source of truth - zero deviation |
| **Traceability** | Every decision links to research and requirements |
| **Transparency** | All decisions documented with reasoning |

---

## Key Features

### Context Tracking - Never Lose Your Place

```
═══════════════════════════════════════════════════════
WHERE YOU LEFT OFF
═══════════════════════════════════════════════════════

TASKS:
  [completed] Previous: PROJ-123 "Create Button atom"
  [current]   Current:  PROJ-124 "Create FormField molecule"
  [pending]   Next:     PROJ-125 "Create Card molecule"

CURRENT TASK PROGRESS:
  [completed] Step 1: Write tests - DONE
  [current]   Step 2: Implement component - 50%
     > "Label and input done, error handling next"
  [pending]   Step 3: Style with tokens
═══════════════════════════════════════════════════════
```

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

### Learning & Improvement System

AID gets smarter over time by learning from your feedback:

```
Session Flow:
1. /aid-init     > Initialize project
2. /aid-start    > Select role (PM/Dev/QA/Lead) + phase
3. Work          > Claude applies relevant skills
4. /aid-end      > Rate session (1-5), describe what worked
5. /aid-improve  > System learns and updates skills
```

**Pattern Detection**: After 10+ sessions, AID identifies what works and what doesn't, then updates its recommendations automatically.

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

## Phase Gate System

AID enforces **5 mandatory phases** with quality gates between each. No phase can be skipped.

```
Phase 1 ──► Gate ──► Phase 2 ──► Gate ──► Phase 3 ──► Gate ──► Phase 4 ──► Gate ──► Phase 5
  PRD        ✓      Tech Spec     ✓      Breakdown     ✓        Dev          ✓      QA & Ship
```

### Phase Details

| Phase | Name | What Happens | Output |
|-------|------|--------------|--------|
| **1** | PRD | Define requirements, user stories, scope | `docs/prd/*.md` |
| **2** | Tech Spec | Architecture, database design, APIs, security | `docs/tech-spec/*.md` |
| **3** | Breakdown | Implementation plan, Jira tasks (< 4 hours each) | `docs/implementation-plan/*.md` |
| **4** | Development | TDD implementation, code review | `src/`, `testing/` |
| **5** | QA & Ship | Validation, testing, deployment | Production release |

### Phase Permissions

| Phase | Allowed | Blocked |
|-------|---------|---------|
| 1 PRD | Requirements, scope, user stories | Code, architecture, Jira |
| 2 Tech Spec | + Architecture, schemas, APIs | Code, Jira issues |
| 3 Breakdown | + Jira epics, stories, tasks | Production code |
| 4 Development | + Code, tests, components | Deployment |
| 5 QA & Ship | Everything | - |

### Sub-Agent Review (Mandatory)

Before each phase transition, a **sub-agent must review** all deliverables:
- Results: **PASS** / **PARTIAL** / **FAIL**
- PASS: Proceed to feedback collection
- PARTIAL: Fix minor issues and re-run
- FAIL: Cannot advance without fixing critical issues

---

## MCP Integrations

AID integrates with 6 Model Context Protocol (MCP) servers for seamless tool connectivity:

### Configured MCPs

| MCP | Purpose | Key Capabilities |
|-----|---------|------------------|
| **Filesystem** | File operations | Read/write files, directory operations, search |
| **Chrome DevTools** | Frontend testing | E2E testing, visual testing, performance audits |
| **Jira** | Task management | Create epics/stories/tasks, manage sprints, query issues |
| **Confluence** | Documentation | Create/update pages, manage spaces, organize docs |
| **Figma** | Design system | Extract tokens, component specs, download assets |
| **GitHub** | Source control | Repos, PRs, issues, code search, reviews |

### Environment Variables Required

```env
# Atlassian (Jira & Confluence)
ATLASSIAN_SITE_URL=https://your-org.atlassian.net
ATLASSIAN_USER_EMAIL=your-email@company.com
ATLASSIAN_API_TOKEN=your-api-token

# GitHub
GITHUB_PERSONAL_ACCESS_TOKEN=ghp_...

# Figma
FIGMA_API_KEY=figd_...
```

### MCP Configuration

All MCPs are configured in `.mcp.json`. See [integrations/](integrations/) for detailed setup guides.

---

## Nano Banana Pro (Visual AI)

> **OPTIONAL FEATURE** - AID works fully without this. Enable only if you need AI-generated visuals.

Generate professional visual artifacts using Google's Nano Banana Pro (Gemini 3 Pro Image).

### Capabilities

| AID Phase | Visual Artifact | Example |
|-----------|-----------------|---------|
| Discovery | Stakeholder maps | Org chart with influence levels |
| PRD | User flows, journey maps | Checkout process flow diagram |
| Tech Spec | Architecture diagrams, ERDs | Microservices system diagram |
| Development | Screen mockups | Dashboard with design tokens applied |

### Setup (Environment Variables)

```env
# Enable the feature
ENABLE_NANO_BANANA=true

# Choose ONE provider:

# Option 1: Google AI Studio (Easiest)
NANO_BANANA_PROVIDER=google
GOOGLE_AI_API_KEY=your-key-from-aistudio.google.com

# Option 2: AI/ML API
NANO_BANANA_PROVIDER=aimlapi
AIML_API_KEY=your-key-from-aimlapi.com

# Option 3: Google Vertex AI (Enterprise)
NANO_BANANA_PROVIDER=vertex
VERTEX_PROJECT_ID=your-gcp-project-id
VERTEX_LOCATION=us-central1
```

### Usage

```typescript
import { createNanoBananaClient, isNanoBananaEnabled } from '@/lib/nano-banana-pro';

if (isNanoBananaEnabled()) {
  const client = createNanoBananaClient();
  const result = await client.generateFromText(
    'Create a user flow diagram for checkout process',
    { aspectRatio: '16:9', resolution: '2K' }
  );
}
```

### Features

- **Text-to-Image**: Generate diagrams from descriptions
- **Wireframe-to-UI**: Transform sketches into high-fidelity mockups
- **Design System Integration**: Apply Atomic Design tokens automatically
- **Multiple Formats**: Support for 1:1, 16:9, 9:16, 4:3, and more
- **Resolutions**: 1K, 2K, 4K output

---

## Skills System

AID uses **21 specialized skills** - AI sub-agents with domain expertise organized by role and phase.

### Core Skills (Always Active)

| Skill | Purpose |
|-------|---------|
| `phase-enforcement` | Enforce phase gates, refuse out-of-phase work |
| `context-tracking` | Track tasks, steps, progress across sessions |
| `learning-mode` | Decision transparency, feedback collection |

### Phase Skills

| Skill | Phase | Purpose |
|-------|-------|---------|
| `pre-prd-research` | 0 | Business analysis, competitive research, problem validation |
| `aid-discovery` | 0-1 | Stakeholder identification, success metrics |
| `aid-prd` | 1 | User stories, acceptance criteria, scope definition |
| `aid-tech-spec` | 2 | Architecture, API contracts, security design |
| `aid-development` | 4 | Implementation guidance, TDD practices |
| `aid-qa-ship` | 5 | Validation, release preparation, deployment |

### Role Skills

| Skill | Focus Areas |
|-------|-------------|
| `role-product-manager` | Requirements, user stories, scope, stakeholder alignment |
| `role-developer` | Code quality, TDD, technical feasibility |
| `role-qa-engineer` | Test strategy, bug reporting, acceptance testing |
| `role-tech-lead` | Architecture review, code review, technical direction |

### Development Skills

| Skill | Purpose |
|-------|---------|
| `atomic-design` | Figma-to-code component system (atoms, molecules, organisms) |
| `atomic-page-builder` | Compose pages from existing components only |
| `system-architect` | Security-first architecture (ISO 27001, OWASP Top 10) |
| `test-driven` | TDD methodology, test patterns, coverage requirements |
| `code-review` | Quality review, security audit, production readiness |
| `nano-banana-visual` | AI-powered visual artifact generation (optional) |

### Design System (Atomic Design)

```
Figma (Source of Truth)
    |
    v
Design Tokens (colors, spacing, typography)
    |
    v
Atoms (Button, Input, Label, Icon)
    |
    v
Molecules (FormField, Card, SearchBar)
    |
    v
Organisms (Header, Sidebar, DataTable)
    |
    v
Templates (Page layouts)
    |
    v
Pages (Complete screens)
```

**Critical Rule**: Figma values are source of truth - zero deviation, no "improvements".

---

## Commands Reference

AID provides **25 slash commands** organized by workflow.

### Setup & Initialization

| Command | Description |
|---------|-------------|
| `/setup` | Complete guided setup for new users (recommended) |
| `/aid-init` | Initialize project with AID phases + memory system |
| `/link-project` | Link existing project to AID via symbolic links |
| `/start-project` | Initialize a new project from scratch |

### Daily Workflow

| Command | Description |
|---------|-------------|
| `/good-morning` | Morning startup - check systems, load context, continue |
| `/context` | Show current work context (tasks + steps) |
| `/context-update` | Update context manually |

### Phase Management

| Command | Description |
|---------|-------------|
| `/phase` | Show current phase status |
| `/gate-check` | Check if ready to advance to next phase |
| `/phase-approve` | Human sign-off for current phase |
| `/phase-advance` | Move to next phase |
| `/aid-start` | Start session - select role & phase, load skills |
| `/aid-end` | End phase and provide feedback |
| `/aid-status` | Show current state (phase + session) |

### Development

| Command | Skill | Description |
|---------|-------|-------------|
| `/prd` | aid-prd | Create Product Requirements Document |
| `/tech-spec` | aid-tech-spec | Create Technical Specification |
| `/jira-breakdown` | - | Break spec into Jira issues |
| `/design-system` | atomic-design | Build design system from Figma |
| `/build-page` | atomic-page-builder | Compose pages from components |
| `/architecture` | system-architect | System architecture design |
| `/write-tests` | test-driven | Write tests (TDD methodology) |
| `/test-review` | test-driven | Review test quality |
| `/code-review` | code-review | Review code quality |
| `/qa-ship` | aid-qa-ship | QA validation and release |

### Learning & Improvement

| Command | Description |
|---------|-------------|
| `/aid-improve` | Run learning cycle (requires 3+ feedback) |
| `/aid-memory` | Manage Claude Memory entries |
| `/aid-analyze` | Full quality analysis with metrics |
| `/aid-dashboard` | Generate quality dashboard report |
| `/aid-recommendations` | View/manage skill update recommendations |
| `/aid-reset` | Reset memory system (destructive) |

### Testing

| Command | Description |
|---------|-------------|
| `/aid-test` | Run full methodology test suite |

---

## Quick Start

### For Non-Technical Users (Recommended)

```
1. Open Claude Code in this folder
2. Type: /setup
3. Follow the step-by-step prompts
```

### For Developers

```bash
# Clone the repository
git clone https://github.com/ilandahan/AID.git
cd AID

# Run installation script
./install.sh          # macOS/Linux
./install.bat         # Windows

# Initialize your project
./scripts/init-project.sh my-app
cd my-app

# Every morning
/good-morning
```

### For Teams

```bash
# 1. Clone AID to shared location
git clone https://github.com/ilandahan/AID.git /shared/aid

# 2. From your project folder, link to AID
/link-project

# 3. All team members share the same methodology
# 4. Update AID centrally, all projects get updates
```

---

## Tech Stack

### Supported Technologies

| Layer | Technologies |
|-------|--------------|
| **Frontend** | Next.js, React, TypeScript, SCSS |
| **Backend** | Node.js, Next.js API Routes |
| **Database** | PostgreSQL, Prisma ORM |
| **Testing** | Jest, Testing Library, Supertest, Chrome DevTools MCP |
| **Deployment** | Docker, Docker Compose |

### Testing Pyramid

```
        /\
       /  \
      / E2E \       <- Chrome DevTools MCP
     /--------\
    /Integration\   <- Real DB, APIs
   /--------------\
  /   Unit Tests   \  <- Jest, Vitest (70%+ coverage)
 /------------------\
```

### Security Standards

- **OWASP Top 10** mitigation at architecture level
- **ISO 27001** compliance patterns
- Input validation with Zod
- XSS prevention (React auto-escapes)
- Authentication in httpOnly cookies

---

## Project Structure

```
AID/
├── .aid/
│   ├── state.json              # Current phase state
│   └── context.json            # Work context tracking
├── .claude/
│   ├── commands/               # 25 slash commands
│   │   ├── good-morning.md
│   │   ├── phase.md
│   │   ├── aid-start.md
│   │   └── ... (22 more)
│   └── skills/                 # 21 specialized skills
│       ├── phase-enforcement/
│       ├── context-tracking/
│       ├── atomic-design/
│       ├── test-driven/
│       └── ... (17 more)
├── docs/
│   ├── prd/                    # Phase 1 outputs
│   ├── tech-spec/              # Phase 2 outputs
│   ├── implementation-plan/    # Phase 3 outputs
│   ├── PHASE-GATES.md
│   └── MORNING-STARTUP.md
├── memory-system/              # Learning & improvement
│   ├── docs/
│   └── skills/
├── src/                        # Application code (Phase 4)
│   └── lib/
│       └── nano-banana-pro/    # Visual AI integration
├── integrations/               # MCP setup guides
├── scripts/                    # Automation scripts
├── .mcp.json                   # MCP configuration
├── .env.example                # Environment template
├── CLAUDE.md                   # Critical instructions
└── BEST-PRACTICES.md           # Code standards
```

---

## Documentation

| Document | Description |
|----------|-------------|
| [INSTALLATION.md](INSTALLATION.md) | Complete setup guide for all skill levels |
| [CLAUDE.md](CLAUDE.md) | Critical instructions for Claude (phase gates, commands) |
| [BEST-PRACTICES.md](BEST-PRACTICES.md) | Code standards and patterns |
| [docs/PHASE-GATES.md](docs/PHASE-GATES.md) | Phase system details |
| [docs/MORNING-STARTUP.md](docs/MORNING-STARTUP.md) | Daily workflow guide |
| [docs/WORK-CONTEXT-TRACKER.md](docs/WORK-CONTEXT-TRACKER.md) | Context tracking details |
| [memory-system/docs/](memory-system/docs/) | Learning system documentation |

---

## Example Workflows

### Creating a New Feature (Full Cycle)

```
1. /good-morning              # Load context, check systems
2. /aid-start                 # Select PM role, Phase 1
3. /prd                       # Create requirements document
4. /phase-approve             # Human approval
5. /aid-end                   # Collect feedback
6. /phase-advance             # Move to Phase 2

7. /aid-start                 # Select Tech Lead role, Phase 2
8. /tech-spec                 # Create technical specification
9. /architecture              # Design system architecture
10. /design-system            # Extract Figma tokens
11. /phase-approve            # Human approval
12. /phase-advance            # Move to Phase 3

13. /jira-breakdown           # Create Jira tasks
14. /phase-advance            # Move to Phase 4

15. /aid-start                # Select Developer role, Phase 4
16. /write-tests              # TDD - tests first
17. [implement code]
18. /code-review              # Quality check
19. /phase-advance            # Move to Phase 5

20. /qa-ship                  # Final validation & deploy
21. /aid-end                  # Collect feedback
22. /aid-improve              # Learn from session
```

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

**AID Community License v1.0** - Free to use, adapt, and share. Cannot be sold.

See [LICENSE](LICENSE) for full details.

### Quick Summary:
- **FREE:** Use it in any project (personal, commercial, open source)
- **ADAPT:** Customize for your needs
- **SHARE:** Teach, present, write about it
- **CREDIT:** Attribute to Ilan Dahan / theaid.ai
- **DON'T SELL:** The methodology itself must remain free
