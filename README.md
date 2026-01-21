# AI.D - AI Development Methodology

<div align="center">

## You own it. We organize it.

**Your API key. Your repos. Your data.**

AI.D is an overlay for Claude Code that gives your whole team — PM, Dev, Tech Lead, QA — a repeatable process from idea to production.

[![Claude Code](https://img.shields.io/badge/Claude-Code-orange)](https://claude.ai)
[![License](https://img.shields.io/badge/License-AI.D%20Community%20v1.0-blue.svg)](LICENSE)
[![Skills](https://img.shields.io/badge/Skills-23%20Specialized-purple)](#skills-system)
[![Agents](https://img.shields.io/badge/Agents-4%20Sub--Agents-green)](#sub-agents)

*Created by Ilan Dahan*

</div>

---

## The Three Pillars

<table>
<tr>
<td align="center" width="33%">

### Humans Lead
**AI accelerates, you decide.**

You approve every phase gate. You own every decision. Claude suggests — you commit.

</td>
<td align="center" width="33%">

### Structure First
**Clarity before code.**

No code until requirements are approved. No deployment until tests pass. Phase gates enforce discipline.

</td>
<td align="center" width="33%">

### Nothing Lost
**Context compounds.**

Every session builds on the last. Context tracking means you never restart from zero.

</td>
</tr>
</table>

---

## Table of Contents

- [What is AI.D?](#what-is-aid)
- [The Three Pillars](#the-three-pillars)
- [Phase Gate System](#phase-gate-system)
- [Sub-Agents (4 Specialized)](#sub-agents)
- [Skills System (23 Skills)](#skills-system)
- [MCP Integrations](#mcp-integrations)
- [Commands Reference](#commands-reference)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [Documentation](#documentation)

---

## What is AI.D?

AI.D (AI Development Methodology) is a **structured overlay** for Claude Code that transforms how teams build software. It's not a framework you install into your code — it's a methodology that guides Claude to work with your team through every phase of development.

### The Problem

| Without AI.D | With AI.D |
|-------------|----------|
| AI generates code without context | Phase gates enforce requirements before code |
| Losing track across sessions | Context tracking remembers everything |
| Each team member works differently | One process: PM → Dev → QA all aligned |
| Scope creep and endless revisions | Approved PRDs lock scope |
| No learning from mistakes | Feedback system improves over time |

### Roles

| Role | Focus |
|------|-------|
| **Product Manager** | Requirements, user stories, DDD (Document Driven Development) |
| **Tech Lead** | Architecture, code review, technical direction |
| **Developer** | Implementation, TDD (Test Driven Development) |
| **QA Engineer** | Test strategy, BDD (Behavior Driven Development) |

---

## Phase Gate System

AI.D enforces **6 mandatory phases** (0-5) with quality gates between each. No phase can be skipped.

```
Phase 0 ──► Gate ──► Phase 1 ──► Gate ──► Phase 2 ──► Gate ──► Phase 3 ──► Gate ──► Phase 4 ──► Gate ──► Phase 5
Discovery    ✓        PRD        ✓      Tech Spec     ✓      Impl Plan     ✓        Dev          ✓      QA & Ship
```

### What Happens in Each Phase

| Phase | Name | What You Do | Output |
|-------|------|-------------|--------|
| **0** | Discovery | Research, stakeholder mapping, Go/No-Go decision | Research report |
| **1** | PRD | Define requirements, user stories, acceptance criteria | Product Requirements |
| **2** | Tech Spec | Architecture, database design, APIs, security | Technical Specification |
| **3** | Impl Plan | Task breakdown, Jira population, sprint planning | Implementation Plan |
| **4** | Development | TDD implementation, code review, component building | Production code |
| **5** | QA & Ship | Validation, acceptance testing, deployment | Release |

### Phase Permissions (Humans Lead)

| Phase | Allowed | Blocked |
|-------|---------|---------|
| 0 Discovery | Research, stakeholders, competitive analysis | PRD, architecture, code |
| 1 PRD | + Requirements, scope, user stories | Architecture, code, Jira |
| 2 Tech Spec | + Architecture, schemas, APIs | Code, Jira issues |
| 3 Impl Plan | + Task decomposition, Jira creation | Production code |
| 4 Development | + Code, tests, components | Deployment |
| 5 QA & Ship | Everything | - |

**You approve each gate.** Claude cannot advance without your `/phase-approve`.

---

## Sub-Agents

AI.D uses **4 specialized sub-agents** — isolated AI processes that provide objective evaluation without bias from the main conversation.

### Why Sub-Agents?

| Main Agent | Sub-Agent |
|------------|-----------|
| Full conversation context | Isolated — sees only what you pass |
| Knows its own reasoning | Evaluates output objectively |
| Might agree with itself | Catches issues the main agent missed |

### Available Agents

| Agent | Purpose | Triggered By |
|-------|---------|--------------|
| **reflection-agent** | Quality evaluation for all significant outputs | Automatic (Quality Check) |
| **phase-review-agent** | Phase gate validation before advancement | `/gate-check` command |
| **qa-validator-agent** | Task completion validation | QA hooks (Phase 4) |
| **memory-analysis-agent** | Analyzes feedback and suggests improvements | `/aid-improve` command |

### Quality Check (Automatic)

Every significant output goes through the reflection-agent:

```
╭─────────────────────────────────────────────────────────────╮
│ 🔍 Quality Check                                            │
├─────────────────────────────────────────────────────────────┤
│  ✅ WHY Alignment     9/10   Addresses stated goal          │
│  ✅ Phase Compliance  10/10  Appropriate for Phase 2        │
│  ✅ Correctness       8/10   Verified against specs         │
│  ✅ Security          9/10   No vulnerabilities found       │
│  ⚠️  Completeness     7/10   Missing error handling         │
│  ══════════════════════════════════════════════════════     │
│  📊 Overall: 8.6/10                                         │
│  STATUS: ✅ PASSED                                          │
╰─────────────────────────────────────────────────────────────╯
```

---

## Skills System

AI.D uses **23 specialized skills** organized by role and phase.

### Core Skills (Always Active)

| Skill | Purpose |
|-------|---------|
| `why-driven-decision` | **Foundational** — understand WHY before any action |
| `reflection` | Quality check system with sub-agent evaluation |
| `phase-enforcement` | Enforce phase gates, refuse out-of-phase work |
| `context-tracking` | Track tasks, steps, progress across sessions |

### Phase Skills

| Skill | Phase | Purpose |
|-------|-------|---------|
| `pre-prd-research` | 0 | Business analysis, competitive research, problem validation |
| `aid-discovery` | 0 | Stakeholder identification, Go/No-Go decision |
| `aid-prd` | 1 | User stories, acceptance criteria, scope definition |
| `aid-tech-spec` | 2 | Architecture, API contracts, security design |
| `aid-impl-plan` | 3 | Task breakdown, Jira population, sprint planning |
| `aid-development` | 4 | Implementation guidance, TDD practices |
| `aid-qa-ship` | 5 | Validation, release preparation, deployment |

### Role Skills

| Skill | Focus Areas |
|-------|-------------|
| `role-product-manager` | Requirements, user stories, scope, stakeholder alignment |
| `role-developer` | Code quality, TDD, debugging, technical feasibility |
| `role-qa-engineer` | Test strategy, BDD/Gherkin, acceptance testing |
| `role-tech-lead` | Architecture review, code review, technical direction |

### Development Skills

| Skill | Purpose |
|-------|---------|
| `atomic-design` | Figma-to-code component system (atoms → pages) |
| `atomic-page-builder` | Compose pages from existing components only |
| `system-architect` | Security-first architecture (ISO 27001, OWASP) |
| `test-driven` | TDD methodology, test patterns, coverage |
| `code-review` | Quality review, security audit, production readiness |

### Support Skills

| Skill | Purpose |
|-------|---------|
| `memory-system` | Session feedback, learning, improvement cycles |
| `learning-mode` | Decision transparency, debate invitations |
| `figma-design-review` | Design system compliance scoring |

---

## MCP Integrations

AI.D integrates with Model Context Protocol (MCP) servers for seamless tool connectivity:

| MCP | Purpose |
|-----|---------|
| **Filesystem** | File operations, directory management |
| **Chrome DevTools** | E2E testing, visual testing, performance |
| **Jira** | Epics, stories, tasks, sprint management |
| **Confluence** | Documentation, knowledge base |
| **Figma** | Design tokens, component specs, assets |
| **GitHub** | Repos, PRs, issues, code review |

> **Setup:** See [INSTALLATION.md](INSTALLATION.md) for MCP configuration and environment variables.

---

## Commands Reference

> **Setup commands:** See [INSTALLATION.md](INSTALLATION.md)

### Session Flow (Daily)

```
┌─────────────────────────────────────────────────────────────┐
│  /aid-start  →  Work  →  /aid-end  →  /aid-improve          │
│     ↑                                       │               │
│     └───────────── Next Session ────────────┘               │
└─────────────────────────────────────────────────────────────┘
```

| Step | Command | What Happens |
|------|---------|--------------|
| 1 | `/aid-start` | Select role (PM/Dev/QA/Lead) + phase → Skills loaded |
| 2 | Work | Claude applies relevant skills, enforces phase gates |
| 3 | `/aid-end` | Rate session (1-5), describe what worked/didn't |
| 4 | `/aid-improve` | System learns and updates skills (optional, weekly) |

### Daily Workflow

| Command | Description |
|---------|-------------|
| `/good-morning` | Morning startup — check systems, load context |
| `/context` | Show current work context |
| `/aid-start` | Start session — select role & phase |
| `/aid-end` | End session and provide feedback |
| `/aid-status` | Show current state |

### Phase Management

| Command | Description |
|---------|-------------|
| `/phase` | Show current phase status |
| `/gate-check` | Check if ready to advance (spawns sub-agent) |
| `/phase-approve` | Human sign-off for current phase |
| `/phase-advance` | Move to next phase |

### Development

| Command | Description |
|---------|-------------|
| `/discovery` | Start Phase 0 research |
| `/prd` | Create Product Requirements Document |
| `/tech-spec` | Create Technical Specification |
| `/jira-breakdown` | Break spec into Jira issues |
| `/design-system` | Build design system from Figma |
| `/build-page` | Compose pages from components |
| `/write-tests` | Write tests (TDD methodology) |
| `/code-review` | Review code quality |
| `/qa-ship` | QA validation and release |

### Improvement

| Command | Description |
|---------|-------------|
| `/aid-improve` | Run learning cycle (spawns sub-agent) |
| `/reflect` | Show detailed quality check breakdown |

---

## Quick Start

> **See [INSTALLATION.md](INSTALLATION.md) for complete setup instructions.**

Once installed, your daily workflow:

```
/good-morning          # Start your day
/aid-start             # Select role + phase
[work]                 # Claude applies skills
/aid-end               # Rate session
```

---

## Project Structure

```
AI.D/
├── .claude/                    # ALL Claude Code content
│   ├── agents/                 # 4 sub-agents
│   ├── skills/                 # 23 specialized skills
│   ├── commands/               # Slash commands
│   ├── hooks/                  # QA gate hooks
│   ├── references/             # Reference documentation
│   ├── rules/                  # Behavioral rules
│   └── templates/              # State file templates
├── docs/                       # AI.D methodology docs
├── integrations/               # MCP setup guides
├── CLAUDE.md                   # Main instructions
├── INSTALLATION.md             # Setup guide
└── README.md                   # This file
```

### Your Project (After Setup)

```
your-project/
├── .aid/                       # Runtime state
│   ├── state.json              # Current phase
│   └── context.json            # Work context
└── .claude/                    # Linked from AI.D
    ├── skills/
    ├── agents/
    └── commands/
```

---

## Documentation

| Document | Description |
|----------|-------------|
| [INSTALLATION.md](INSTALLATION.md) | Complete setup guide |
| [CLAUDE.md](CLAUDE.md) | Critical instructions for Claude |
| [docs/PHASE-GATES.md](docs/PHASE-GATES.md) | Phase system details |
| [docs/MORNING-STARTUP.md](docs/MORNING-STARTUP.md) | Daily workflow guide |

---

## Example Workflow

### Creating a New Feature (Full Cycle)

```
1. /good-morning              # Load context, check systems
2. /aid-start                 # Select PM role, Phase 0
3. /discovery                 # Research and Go/No-Go
4. /phase-approve             # Human approval
5. /phase-advance             # → Phase 1

6. /prd                       # Create requirements
7. /phase-approve             # Human approval
8. /phase-advance             # → Phase 2

9. /tech-spec                 # Create architecture
10. /design-system            # Extract Figma tokens
11. /phase-approve            # Human approval
12. /phase-advance            # → Phase 3

13. /jira-breakdown           # Create Jira tasks
14. /phase-advance            # → Phase 4

15. /aid-start                # Select Developer role
16. /write-tests              # TDD - tests first
17. [implement code]
18. /code-review              # Quality check
19. /phase-advance            # → Phase 5

20. /qa-ship                  # Final validation & deploy
21. /aid-end                  # Collect feedback
22. /aid-improve              # Learn from session
```

---

## Author

Created by **Ilan Dahan**

Built with [Claude Code](https://claude.ai) by Anthropic.

---

## License

**AI.D Community License v1.0** — Free to use, adapt, and share. Cannot be sold.

See [LICENSE](LICENSE) for full details.

| Allowed | Not Allowed |
|---------|-------------|
| Use in any project | Sell the methodology |
| Customize for your needs | Remove attribution |
| Share and teach | |
| Commercial use | |

**Credit:** Ilan Dahan / theaid.ai
