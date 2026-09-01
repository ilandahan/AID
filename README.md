# AID - AI Development Methodology

<div align="center">

**Transform raw requirements into production-ready software using Claude Code**

[![Claude Code](https://img.shields.io/badge/Claude-Code-orange)](https://claude.ai)
[![License](https://img.shields.io/badge/License-AID%20Community%20v1.0-blue.svg)](LICENSE)
[![MCP Integrations](https://img.shields.io/badge/MCP-6%20Integrations-green)](#mcp-integrations)
[![Skills](https://img.shields.io/badge/Skills-28%20Specialized-purple)](#skills-system)
[![Sub-Agents](https://img.shields.io/badge/Sub--Agents-39-teal)](#sub-agents)
[![Tests](https://img.shields.io/badge/Tests-228-brightgreen)](#testing)
[![Plugin](https://img.shields.io/badge/Claude%20Code-Plugin-blueviolet)](#install-as-a-plugin)

*A complete AI-powered software development lifecycle framework*

*Created by Ilan Dahan*

</div>

---

## Table of Contents

- [What's New](#whats-new)
- [What is AID?](#what-is-aid)
- [Research & Methodology](#research--methodology)
- [Key Features](#key-features)
- [Phase Gate System](#phase-gate-system)
- [Sub-Agents](#sub-agents)
- [MCP Integrations](#mcp-integrations)
- [Nano Banana Pro (Visual AI)](#nano-banana-pro-visual-ai)
- [Skills System (28 Skills)](#skills-system)
- [Commands Reference (45 Commands)](#commands-reference)
- [Quick Start](#quick-start)
- [Tech Stack](#tech-stack)
- [Testing](#testing)
- [Project Structure](#project-structure)
- [Documentation](#documentation)

---

## What's New

### New capabilities

| Feature | What it gives you |
|---------|-------------------|
| **Data Science / ML track** | A full `role-data-scientist` skill plus 6 phase-specific rule sets — EDA, feasibility, experiment planning, ML architecture, development, production. Covers data pipelines, RAG/CAG, prompt engineering, bias auditing, model cards and monitoring. Phases are relabelled for the role (Phase 0 becomes *EDA — Data Gathering & Analysis*). |
| **Cucumber / BDD** | `cucumber-bdd` skill with step-definition guides for **JS, Python, Java, Ruby and Go**. Phase 1 acceptance criteria are written as Gherkin, so the PRD and the test suite are the same artifact. Runs via `npm run cucumber`. |
| **Automated dev pipeline** | `pipeline-orchestrator` drives a 12-step state machine: DEVELOP → CODE_REVIEW → AR_DESIGN → TDD → AR_FUNCTION → VISUAL_QA → TEST_REVIEW → PHASE_GATE → AR_ACCEPTANCE → API_TESTS → E2E_TESTS → CERTIFICATION, with hard iteration caps and escalation instead of infinite retry loops. All scored review gates (code review, test review, autoresearch KPI) are unified at 9.5/10, and the E2E step pre-checks that E2E tests actually exist before claiming a pass — if none do, it asks you to create or explicitly skip them. |
| **Autoresearch runner** | `autoresearch` performs bounded keep/revert improvement: snapshot → one focused edit → score → keep **only if strictly better**, else revert. Every edit is reversible and the loop always terminates. |
| **39 registered sub-agents** | Independent, context-free specialists: 8 reviewers (code, tests, visual QA, phase gates, QA validation, reflection, feedback analysis), 2 builders (developer, test-engineer) and 29 phase specialists covering Phase 0 discovery, Phase 2 architecture, Phase 3 breakdown, Phase 4 sprint work, Phase 5 release and the PRD pipeline. All invocable by name. |
| **Quality Check on every output** | The `reflection` skill scores WHY alignment, phase compliance, correctness, security and completeness before you see the result. |
| **WHY-first foundation** | `why-driven-decision` loads before everything else — no implementation without an articulated purpose. |
| **Learning system** | `memory-system` collects session feedback and turns recurring patterns into concrete skill improvements, with a Python CLI for analysis and dashboards. |
| **Enforcement hooks** | A QA gate that blocks task completion until acceptance criteria pass, a language-check gate that blocks a turn ending on code that does not compile, and automatic pipeline initialization when a plan is approved. |
| **Figma design review** | `figma-design-review` audits components *before* extraction, so bad structure never reaches your codebase. |

### Reliability fixes in this release

| Area | Fix |
|------|-----|
| **`link-project` data loss** | Pointing the linker at the AID install itself deleted its own skills, agents and commands — and on Windows the fallback recreated the folders *empty* while reporting success. Both installers now refuse a self-target or a home-directory target, and never delete before confirming a source exists. |
| **Sub-agents were not invocable** | Agents shipped as prompt folders with no definition files, so `subagent_type` could never resolve them. All 39 now have registered definitions - and because Claude Code registers every `.md` under `agents/` recursively, asset folders were moved out of it so no prompt fragment registers as an agent. |
| **QA gate never fired** | The hook emitted a response shape Claude Code does not read, so it could not block, and it was only ever registered in a personal local settings file. Now it blocks correctly, is registered in `.claude/settings.json`, and carries a loop guard. |
| **Hooks missing in linked projects** | `settings.json` was copied into linked projects while `hooks/` was not, leaving hooks pointing at absent scripts. `hooks/` is now linked. |
| **Least-privilege permissions** | The shipped settings no longer pre-approve a bare `Bash`, which auto-approved *any* shell command. See [Permissions](INSTALLATION.md#permissions) to widen it deliberately. |
| **Cross-platform line endings** | `.gitattributes` pins `.sh` to LF and `.bat` to CRLF, so a clone on either OS gets working scripts. |
| **Silent installer** | 50 copy commands ran against a directory removed in v2.1, each suppressing its own failure while reporting "Skills installed". Replaced with a real verification. |
| **Dead references** | 22 documentation links pointed at files that did not exist. All fixed, and the missing `memory-system` package and `scripts/init-project.sh` were restored. |
| **Ships as a plugin** | `claude plugin marketplace add ilandahan/AID` then `claude plugin install aid@AID`. No cloning, no symlinks, no Developer Mode on Windows, and `claude plugin update aid` moves every project at once. The clone + `link-project` route still works unchanged. |
| **Phase-gate hooks that actually block** | The enforcement dispatcher emitted `decision`/`reason` without `hookEventName`, a shape Claude Code discards - so every gate was read as an allow and never stopped a write. Fixed, and pinned by tests that execute the hook and assert the payload. |
| **Test suite** | 228 tests cover destructive-guard behaviour, hook block/allow payload schemas, agent registration, the plugin layout and repository integrity. |

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

AID enforces **6 mandatory phases** (0-5) with quality gates between each. No phase can be skipped.

```
Phase 0 ──► Gate ──► Phase 1 ──► Gate ──► Phase 2 ──► Gate ──► Phase 3 ──► Gate ──► Phase 4 ──► Gate ──► Phase 5
Discovery    ✓        PRD        ✓      Tech Spec     ✓      Impl Plan     ✓        Dev          ✓      QA & Ship
```

### Phase Details

| Phase | Name | What Happens | Output |
|-------|------|--------------|--------|
| **0** | Discovery | Research, stakeholder mapping, competitive analysis, Go/No-Go | `docs/research/YYYY-MM-DD-[project]/` |
| **1** | PRD | Define requirements, user stories, scope (linked to research) | `docs/prd/*.md` |
| **2** | Tech Spec | Architecture, database design, APIs, security | `docs/tech-spec/*.md` |
| **3** | Impl Plan | Implementation plan, Jira tasks (< 4 hours each) | `docs/implementation-plan/*.md` |
| **4** | Development | TDD implementation, code review | `src/`, `testing/` |
| **5** | QA & Ship | Validation, testing, deployment | Production release |

### Phase Permissions

| Phase | Allowed | Blocked |
|-------|---------|---------|
| 0 Discovery | Research, stakeholders, competitive analysis | PRD, architecture, code |
| 1 PRD | + Requirements, scope, user stories | Architecture, code, Jira |
| 2 Tech Spec | + Architecture, schemas, APIs | Code, Jira issues |
| 3 Impl Plan | + Jira epics, stories, tasks | Production code |
| 4 Development | + Code, tests, components | Deployment |
| 5 QA & Ship | Everything | - |

### Phase 0: Discovery (NEW)

Start every project with research:

```bash
/discovery my-project    # Creates research folder structure
```

**Key Activities:**
- Problem Analysis (5 Whys, Problem Severity)
- Stakeholder Research (Interviews, Power/Interest Matrix)
- Competitive Analysis (JTBD, Market Research)
- Root Cause Investigation
- Go/No-Go Decision

**Exit Criteria:**
- Research report with problem statement (SCQ format)
- Traceability matrix linking research to requirements
- Go/No-Go decision documented

### Sub-Agent Review (Mandatory)

Before each phase transition, a **sub-agent must review** all deliverables:
- Results: **PASS** / **PARTIAL** / **FAIL**
- PASS: Proceed to feedback collection
- PARTIAL: Fix minor issues and re-run
- FAIL: Cannot advance without fixing critical issues

---

## Sub-Agents

AID ships **39 registered sub-agents**: 8 reviewers (below), 2 builders (`developer`,
`test-engineer` - spawned by the pipeline DEVELOP and TDD steps) and 29 phase specialists
(`phase0-*` discovery, `phase2-*` architecture, `phase3-*` breakdown, `phase4-*` sprint
work, `phase5-*` release, and the `prd-*` pipeline) invocable by name for isolated
clean-room work. Each runs with **no knowledge of the conversation
that produced the work** - that isolation is the point. An agent with no attachment to the
code being good is the only one that reliably finds what is wrong with it.

| Agent | Reviews | Triggered by |
|-------|---------|--------------|
| `reflection-agent` | Any output: WHY alignment, phase compliance, correctness, security, completeness | Automatic Quality Check; `/reflect` |
| `code-review-agent` | A diff or file set: security, quality, documentation, architecture | Pipeline CODE_REVIEW; `/code-review` |
| `test-review-agent` | Test quality: coverage, over-mocking, weak assertions, independence | Pipeline TEST_REVIEW; `/test-review` |
| `visual-qa-agent` | A **running** app in a real browser - never the source | Pipeline VISUAL_QA |
| `qa-validator-agent` | Completed work against `.aid/qa/<task>.yaml` acceptance criteria | QA gate Stop hook |
| `phase-review-agent` | Whether a phase's deliverables justify advancing | `/gate-check` |
| `memory-analysis-agent` | Session feedback → concrete skill improvements | `/aid-improve` |
| `aid-test-agent` | The AID methodology itself, end to end | `/aid-test` |

Reviewer agents are **read-only by design** - a reviewer that can edit the code is no
longer independent.

Each agent is one self-contained definition file (`agents/<name>.md`) with its prompt
inlined - that file is what makes it invocable by name. Calibration examples and response
templates live in `agent-assets/`; see `agent-assets/AGENT-STANDARD.md` to add your own.

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
| Phase 0: Discovery | Stakeholder maps, competitive landscape | Power/interest matrix, market positioning |
| Phase 1: PRD | User flows, journey maps | Checkout process flow diagram |
| Phase 2: Tech Spec | Architecture diagrams, ERDs | Microservices system diagram |
| Phase 4: Development | Screen mockups | Dashboard with design tokens applied |

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

AID uses **28 specialized skills** - domain expertise organized by role and phase.

Each skill ships as a pair: `SKILL.md` is the compact version the model loads, and
`SKILL.extended.md` is the human-readable companion. Keeping them separate means the model
spends its context on instructions rather than on formatting.

### Core Skills (Always Active)

| Skill | Purpose |
|-------|---------|
| `why-driven-decision` | **Foundational** - loads first. No work without an articulated WHY |
| `reflection` | Quality Check scoring on every significant output |
| `phase-enforcement` | Enforce phase gates, refuse out-of-phase work |
| `context-tracking` | Track tasks, steps, progress across sessions |
| `learning-mode` | Decision transparency, feedback collection |
| `memory-system` | Feedback analysis, pattern detection, skill improvement |

### Phase Skills

| Skill | Phase | Purpose |
|-------|-------|---------|
| `pre-prd-research` | 0 | Business analysis, competitive research, problem validation |
| `aid-discovery` | 0-1 | Stakeholder identification, success metrics |
| `aid-prd` | 1 | User stories, acceptance criteria, scope definition |
| `aid-tech-spec` | 2 | Architecture, API contracts, security design |
| `aid-impl-plan` | 3 | Contradiction resolution, task breakdown, Jira population |
| `aid-development` | 4 | Implementation guidance, TDD practices |
| `aid-qa-ship` | 5 | Validation, release preparation, deployment |

### Role Skills

| Skill | Focus Areas |
|-------|-------------|
| `role-product-manager` | Requirements, user stories, scope, stakeholder alignment |
| `role-developer` | Code quality, TDD, technical feasibility |
| `role-qa-engineer` | Test strategy, bug reporting, acceptance testing |
| `role-tech-lead` | Architecture review, code review, technical direction |
| `role-data-scientist` | Data pipelines, ML models, RAG/CAG, prompt engineering, analytics, observability, governance, responsible AI |

### Development Skills

| Skill | Purpose |
|-------|---------|
| `atomic-design` | Figma-to-code component system (atoms, molecules, organisms) |
| `atomic-page-builder` | Compose pages from existing components only |
| `figma-design-review` | Audit Figma components **before** extraction, with a scoring rubric |
| `system-architect` | Security-first architecture (ISO 27001, OWASP Top 10) |
| `test-driven` | TDD methodology, test patterns, coverage requirements |
| `cucumber-bdd` | Gherkin acceptance criteria + step definitions for JS, Python, Java, Ruby, Go |
| `code-review` | Quality review, security audit, production readiness |
| `nano-banana-visual` | AI-powered visual artifact generation (optional) |

### Automation Skills

| Skill | Purpose |
|-------|---------|
| `pipeline-orchestrator` | Drives the Phase 4-5 dev pipeline state machine with sub-agent review gates and hard iteration caps |
| `autoresearch` | Bounded keep/revert improvement loop - one edit at a time, kept only if it strictly improves the score |

### Data Science / ML Track

`role-data-scientist` carries its own 6-phase rule set under `.claude/rules/skills/`, so the
lifecycle maps onto ML work instead of forcing it into a web-app shape:

| Phase | Data Science framing | Rules |
|-------|---------------------|-------|
| 0 | EDA - data gathering & analysis | `phase-1-eda.md` |
| 1 | Feasibility assessment | `phase-2-feasibility.md` |
| 2 | Experiment planning | `phase-3-experiment-planning.md` |
| 3 | ML architecture & pipeline design | `phase-4-ml-architecture.md` |
| 4 | Development & validation | `phase-5-development.md` |
| 5 | Deploy to production & monitoring | `phase-6-production.md` |

Supporting references include an ML pipeline checklist, RAG architecture guide, prompt
testing patterns, model card template, bias audit checklist and monitoring setup guide.

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

AID provides **47 slash commands** organized by workflow.

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
| `/discovery` | Start Phase 0 - research and validation |
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
| `/design-review` | figma-design-review | Review Figma components before extraction |
| `/build-page` | atomic-page-builder | Compose pages from components |
| `/storybook` | atomic-design | Manage Storybook component previews |
| `/architecture` | system-architect | System architecture design |
| `/write-tests` | test-driven | Write tests (TDD methodology) |
| `/test-review` | test-driven | Review test quality |
| `/code-review` | code-review | Review code quality |
| `/qa-ship` | aid-qa-ship | QA validation and release |

### Pipeline & Automation

| Command | Description |
|---------|-------------|
| `/pipeline` | Start or resume the automated 12-step dev pipeline |
| `/pipeline-status` | Show current pipeline state and step history |
| `/reflect` | Detailed breakdown of the last Quality Check (`--history`, `--strict`, `--explain`) |
| `/yolo` | Enable full automation (skip confirmations) |
| `/yolo-off` | Disable full automation (restore confirmations) |
| `/breather-start` | Enable breather (break offers, presence tracking, status line) |
| `/breather-stop` | Snooze breather offers, skip today, or uninstall |

### Figma Integration

| Command | Description |
|---------|-------------|
| `/aid-pair` | Pair with the Figma plugin (auth code) |
| `/figma-relay` | Process Figma plugin server requests |

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
| `/aid-test` | Run the methodology test (Phases 0-4; `--phase N`, `--quick`, `--verbose`) |
| `/test-all-agents` | Run every agent test in sequence |
| `/test-reflection` | Test reflection-agent isolation and scoring |
| `/test-qa-validator` | Test QA validator criteria checking |
| `/test-phase-review` | Test phase gate validation |

---

## Testing

Two independent layers, because they answer different questions.

### The repository's own test suite

**228 pytest tests** under `testing/e2e/` verify that *AID itself* works - not that
your application works. Run them after cloning, and after any change to a hook,
installer or link script:

```bash
pip install pytest pyyaml
npm run test:all              # or: python -m pytest testing/e2e/ -v
```

Narrower runs: `npm run test:install`, `npm run test:mcp`, `npm run test:memory`.

11 of the 228 skip unless `node` and `typescript` are reachable from the shell that runs
hooks - run `npm install` first to exercise them. They **skip**, they do not silently pass.

| Suite | What it proves |
|-------|----------------|
| `test_repo_integrity.py` | Every path the docs promise exists and runs - `python -m memory_system`, `scripts/init-project.sh`, the autoresearch assets, no skill without a `SKILL.md` |
| `test_agents_and_hooks.py` | All 8 agents are registered with valid frontmatter; every hook in `settings.json` exists and parses; no bare `Bash` in the allow list |
| `test_link_project_guards.py` | Linking refuses to run against the AID install itself, and refuses to link a source directory that is missing |
| `test_pipeline_hooks.py` | The Stop hook blocks in the schema Claude Code actually reads, respects `stop_hook_active`, and does not claim a `tsc` pass it never ran |
| `test_installation.py` | A fresh install produces a working tree |
| `test_mcp_sanity.py` | MCP templates are valid JSON and carry no real tokens |

Every assertion here corresponds to a defect that shipped silently, and each one
was verified by **removing the fix and watching the test fail**. A test that has
never been red is an unverified claim - see the docstring at the top of
`test_repo_integrity.py` for the specific defect behind each check.

### Your project's tests

Written by you (or by Phase 4 with `/write-tests`), and enforced by the pipeline:

```bash
npm run cucumber        # executable Gherkin acceptance criteria
npm run cucumber:dry    # validate feature files without running them
npm run test:bdd        # Cucumber + HTML report in reports/
npm run test:smoke      # @smoke-tagged scenarios only
npm run test:critical   # @critical-tagged scenarios only
```

The `TEST_REVIEW` pipeline step hands these to `test-review-agent`, which looks for
over-mocking, weak assertions and coverage that measures nothing.

---

## Quick Start

### Install as a plugin

**Recommended.** AID ships as a Claude Code plugin: two commands, no cloning, no
symlinks, and no Developer Mode on Windows.

```bash
claude plugin marketplace add ilandahan/AID
claude plugin install aid@AID
```

Restart Claude Code, then run `/aid-init` in any project. Every project gets the same 45
commands, 28 skills and 39 sub-agents, and one command moves them all forward:

```bash
claude plugin update aid
```

Useful checks: `claude plugin list`, `claude plugin details aid` (component inventory and
projected token cost), `claude plugin disable aid`.

### For Non-Technical Users

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
├── .aid/                       # Per-project runtime state (created by /aid-init)
│   ├── state.json              # Current phase state
│   ├── context.json            # Work context tracking
│   ├── qa/                     # Acceptance criteria the QA gate enforces
│   └── pipeline/               # Pipeline config (tracked) + run state (ignored)
├── .claude-plugin/             # Plugin manifests
│   ├── plugin.json             # Name, version, and the hooks AID registers
│   └── marketplace.json        # Lets the repo host itself as a marketplace
├── commands/                   # 47 slash commands
│   ├── good-morning.md
│   ├── phase.md
│   └── ... (43 more)
├── skills/                     # 28 specialized skills
│   ├── why-driven-decision/    # Foundational - loads first
│   ├── reflection/             # Quality Check + phase criteria
│   ├── pipeline-orchestrator/  # 12-step machine + gate.mjs
│   ├── autoresearch/           # Bounded keep/revert improvement loop
│   ├── cucumber-bdd/           # Gherkin across 5 languages
│   └── ... (23 more)
├── agents/                     # 39 sub-agents - FLAT, one .md each, prompt inlined
│   ├── reflection-agent.md
│   ├── phase0-problem-validator.md
│   └── ... (36 more)
├── agent-assets/               # Calibration examples + AGENT-STANDARD.md (not scanned)
├── rules/                      # 23 rule files, incl. the Data Science / ML track
├── references/                 # Shared lookup data (role/phase terminology)
├── hooks/                      # Phase gate, QA gate, pipeline enforcement
├── .claude/
│   └── settings.json           # Permissions + hooks for PROJECT mode (copied on link)
├── testing/e2e/                # 228 tests covering AID itself
├── docs/
│   ├── prd/                    # Phase 1 outputs
│   ├── tech-spec/              # Phase 2 outputs
│   ├── implementation-plan/    # Phase 3 outputs
│   ├── research/               # Phase 0 outputs
│   ├── PHASE-GATES.md
│   └── MORNING-STARTUP.md
├── memory-system/              # Learning & improvement
│   ├── memory_system/          # Python package: python -m memory_system
│   └── docs/
├── storybook-preview/          # Component preview workspace
├── integrations/               # MCP setup guides (jira, figma, github, chrome-devtools)
│   └── figma-plugin/           # Figma plugin for /aid-pair
├── scripts/init-project.sh     # New-project scaffolding
├── install.sh / install.bat    # Installers
├── link-project.sh / .bat      # Link an existing project (one source of truth)
├── .mcp.json.mac / .windows    # MCP templates - copy to .mcp.json, add your tokens
├── .gitattributes              # LF for .sh, CRLF for .bat
└── CLAUDE.md                   # Critical instructions Claude loads every session
```

### Why components sit at the root

Claude Code reads a **plugin's** components from the plugin root, and a **project's**
components from `.claude/`. AID has to satisfy both from one copy of the files, so the
tracked files live at the root and `install.sh` mirrors them into `.claude/` as symlinks
(macOS/Linux) or junctions (Windows, no admin needed).

Those mirrors are gitignored on purpose. `core.symlinks` defaults to false on Windows, so
a committed symlink checks out as a *text file containing a path* — a directory that isn't
one, which git reports as perfectly clean.

Three things here are load-bearing and easy to get wrong:

- **`agents/` is flat.** Claude Code registers every `.md` under `agents/` as an agent,
  recursively. Asset folders there produced ~71 agents, most of them prompt fragments and
  calibration examples. Each agent is now one self-contained file with its prompt inlined,
  because an agent's working directory is the *user's project* — an external asset path
  resolves against their code, not the plugin.
- **`.claude/settings.json` stays put.** It is project configuration, not a component, and
  it is what `link-project` copies into a target. It names hooks as `.claude/hooks/*`,
  which is correct in a linked project, where `.claude/hooks` points at AID's `hooks/`.
- **Hook commands use `"${CLAUDE_PLUGIN_ROOT}"`, always quoted.** The likely install path
  contains a space; unquoted, the hook splits into two arguments and dies.

**Upgrading from a pre-3.0 clone:** run `./install.sh` once. It recreates `.claude/*`, so
projects already linked to `.claude/<name>` keep working with no re-linking.

---

## Documentation

| Document | Description |
|----------|-------------|
| [INSTALLATION.md](INSTALLATION.md) | Complete setup guide for all skill levels |
| [CLAUDE.md](CLAUDE.md) | Critical instructions for Claude (phase gates, commands) |
| [docs/PHASE-GATES.md](docs/PHASE-GATES.md) | Phase system details |
| [docs/MORNING-STARTUP.md](docs/MORNING-STARTUP.md) | Daily workflow guide |
| [docs/WORK-CONTEXT-TRACKER.md](docs/WORK-CONTEXT-TRACKER.md) | Context tracking details |
| [memory-system/docs/](memory-system/docs/) | Learning system documentation |
| [agent-assets/AGENT-STANDARD.md](agent-assets/AGENT-STANDARD.md) | How to write a sub-agent |
| [rules/](rules/) | Code standards, and the Data Science / ML phase rules |

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
