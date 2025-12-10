# AI Full Stack Development Methodology

<div align="center">

**Transform raw requirements into production-ready software using Claude Code**

[![Claude Code](https://img.shields.io/badge/Claude-Code-orange)](https://claude.ai)

*Created by Ilan Dahan*

</div>

## Overview

A comprehensive framework for AI-enhanced software development that systematizes the entire journey from raw content discovery through deployment. This methodology leverages Claude Code with MCP integrations to create repeatable, scalable processes for complex software projects.

## Key Features

- **End-to-End Workflow** - From PRD to production
- **Phase Gates** ⭐ - Enforced phase progression with human approval
- **Context Tracking** ⭐ - Always know where you left off
- **Morning Startup** ⭐ - `/good-morning` routine for daily continuity
- **MCP Integrations** - Jira, GitHub, Figma built-in
- **Atomic Design System** - Figma-to-code automation
- **TDD Methodology** - Comprehensive testing framework
- **One-Command Setup** - Automated installation

## Tech Stack

| Layer | Technologies |
|-------|--------------|
| **Frontend** | Next.js 16, React 19, TypeScript, SCSS |
| **Backend** | Node.js 18+, Next.js API Routes |
| **Database** | PostgreSQL 16+ (Docker or local) |
| **Auth** | bcryptjs, jsonwebtoken (JWT) |
| **Testing** | Jest, Testing Library, Supertest, Puppeteer |
| **Browser Automation** | Chrome DevTools MCP, Puppeteer |
| **Build** | Next.js, TypeScript |
| **Deployment** | Docker, Docker Compose |

See [DEPENDENCIES.md](DEPENDENCIES.md) for complete dependency documentation.

## Quick Start

```bash
# Clone and install
git clone https://github.com/your-org/ai-fullstack-methodology.git
cd ai-fullstack-methodology
./install.sh

# Or manual setup
make install
```

> ⚠️ **Important:** After initial installation, restart Claude Code in the project directory to load all MCP servers. Run `claude` or reopen the project in Claude Code.

## Development Phases (with Phase Gates)

```
Phase 1 ──► Gate ──► Phase 2 ──► Gate ──► Phase 3 ──► Gate ──► Phase 4 ──► Gate ──► Phase 5
  PRD        ✓      Tech Spec     ✓      Breakdown     ✓        Dev          ✓      QA & Ship
```

| Phase | Input | Output | Gate Criteria |
|-------|-------|--------|---------------|
| **1. PRD** | Raw requirements | `docs/PRD.md` | Approved PRD with user stories |
| **2. Tech Spec** | PRD | `docs/TECH-SPEC.md` | Approved architecture & APIs |
| **3. Breakdown** | Tech Spec | Jira issues | Epics, Stories, Tasks created |
| **4. Development** | Tasks | Working code | Tests pass, code reviewed |
| **5. QA & Ship** | Code | Production | Coverage met, deployed |

**⚠️ Phase Gates are enforced - you cannot skip phases or do work out of order.**

See `docs/PHASE-GATES.md` for complete phase system documentation.

## Directory Structure

```
ai-fullstack-methodology/
├── .mcp.json                  # MCP server configuration
├── .env.example               # Environment variables template
├── .gitignore                 # Git ignore rules
├── CLAUDE.md                  # Claude Code instructions
├── package.json               # npm dependencies
├── tsconfig.json              # TypeScript configuration
├── jest.config.js             # Jest testing configuration
├── jest.setup.js              # Jest setup file
├── docker-compose.yml         # Docker services
├── Dockerfile                 # Application container
├── DEPENDENCIES.md            # Complete dependency documentation
│
├── .claude/commands/          # Slash commands ⭐
│   ├── good-morning.md        # /good-morning (daily startup)
│   ├── context.md             # /context (show work context)
│   ├── context-update.md      # /context-update
│   ├── aid-init.md            # /aid-init
│   ├── phase.md               # /phase
│   ├── gate-check.md          # /gate-check
│   ├── phase-approve.md       # /phase-approve
│   └── phase-advance.md       # /phase-advance
│
├── docs/                      # Documentation
│   ├── PHASE-GATES.md         # Phase gate system ⭐
│   ├── MORNING-STARTUP.md     # Daily workflow ⭐
│   ├── WORK-CONTEXT-TRACKER.md # Context tracking ⭐
│   ├── mcp-setup.md           # MCP configuration
│   ├── phases/                # Phase guides
│   └── prompts/               # Prompt templates
│
├── skills/                    # Claude Code skills
│   ├── phase-enforcement/     # Phase gate enforcement ⭐
│   ├── context-tracking/      # Work context tracking ⭐
│   ├── system-architect/      # Architecture & tech specs
│   ├── atomic-design/         # Design system development
│   ├── atomic-page-builder/   # Page composition
│   ├── code-review/           # Code review automation
│   ├── test-driven/           # TDD methodology
│   └── commands/              # Legacy commands
│
├── integrations/              # MCP integration guides
│   ├── jira/                  # Jira setup guide
│   ├── github/                # GitHub setup guide
│   ├── figma/                 # Figma setup guide
│   └── chrome-devtools/       # Chrome DevTools setup guide
│
├── templates/                 # Project templates
│   ├── .aid/                  # AID state templates ⭐
│   │   ├── state.json.template
│   │   └── context.json.template
│   └── prd-template.md        # PRD template
│
├── test-recordings/           # Browser test artifacts
├── scripts/                   # Automation scripts
│   ├── init-project.sh        # Initialize new project
│   └── startup-check.sh       # Infrastructure check ⭐
├── install.sh                 # One-command installation
└── Makefile                   # Build automation
```

## Installation

### Prerequisites

- Node.js 18+ (React, Backend)
- Python 3.10+ (Backend, Scripts)
- PostgreSQL 14+ (Database)
- Docker (optional, for services)
- Claude Code CLI
- Chrome/Chromium (for Chrome DevTools MCP)

### Dependencies

```bash
# Install all dependencies (production + development)
npm install

# Start database (Docker)
docker-compose up -d postgres pgadmin
```

| Category | Packages | Count |
|----------|----------|-------|
| **Production** | next, react, react-dom, sass, pg, bcryptjs, jsonwebtoken | 7 |
| **TypeScript** | typescript, @types/* | 8 |
| **Testing** | jest, testing-library, supertest, puppeteer | 8 |
| **Total** | | **23** |

See [DEPENDENCIES.md](DEPENDENCIES.md) for complete documentation.

### Automated Installation

```bash
./install.sh
```

This will:
1. Install MCP server dependencies
2. Configure Claude Code settings
3. Set up Git hooks
4. Install skill files
5. Verify integrations

### Post-Installation

> ⚠️ **Required:** After installation, you must restart Claude Code to load the MCP servers:
> ```bash
> # Close Claude Code, then reopen in project directory
> cd ai-fullstack-methodology
> claude
> ```
> 
> Verify MCP servers are loaded:
> ```bash
> claude mcp list
> ```

### Manual Installation

See [docs/mcp-setup.md](docs/mcp-setup.md) for detailed MCP configuration.

## Usage

### Start a New Project

```bash
# Initialize with methodology
./scripts/init-project.sh my-new-project

# Or use Claude Code directly
claude "/start-project my-new-project"
```

### Available Commands

Commands are defined in `.claude/commands/` and `skills/commands/`:

#### Daily Workflow ⭐
| Command | Description |
|---------|-------------|
| `/good-morning` | Morning startup - check MCPs, load context, continue |
| `/context` | Show current work context (tasks + steps) |
| `/context-update` | Update context manually |

#### Phase Management ⭐
| Command | Description |
|---------|-------------|
| `/aid-init` | Initialize project with AID phases |
| `/phase` | Show current phase status |
| `/gate-check` | Check if ready to advance to next phase |
| `/phase-approve` | Human sign-off for current phase |
| `/phase-advance` | Move to next phase |

#### Development Commands
| Command | Description | Phase |
|---------|-------------|-------|
| `/start-project [name]` | Initialize new project with methodology | Setup |
| `/prd [feature]` | Generate Product Requirements Document | 1 |
| `/tech-spec [feature]` | Create technical specification | 2 |
| `/jira-breakdown [feature]` | Generate Jira project structure | 3 |
| `/design-system` | Build design system from Figma | 4 |
| `/build-page` | Compose pages from components | 4 |
| `/write-tests` | Write tests (TDD) | 4 |
| `/test-review [path]` | Review test quality | 5 |
| `/code-review [path]` | Review code changes | 5 |

### Example Workflow

```bash
# 1. Create new project
./scripts/init-project.sh my-app
cd my-app

# 2. Initialize AID phases
/aid-init

# 3. Every morning
/good-morning

# This shows:
# - MCP status (Figma, Jira, GitHub)
# - Current phase
# - Where you left off (task + step)
# - Options to continue

# 4. Work through phases
/prd user-auth           # Phase 1: Create PRD
/phase-approve           # Human sign-off
/phase-advance           # Move to Phase 2

/tech-spec user-auth     # Phase 2: Tech Spec
/phase-approve
/phase-advance

/jira-breakdown          # Phase 3: Create Jira issues
/phase-approve
/phase-advance

# Phase 4: Development (now code is allowed)
/context                 # See current task
/write-tests             # TDD
# ... implement ...
/context-update step done

# Phase 5: QA & Ship
/test-review
/code-review
```

## Phases in Detail

### Phase 1: Discovery
Gather raw requirements, stakeholder input, and market research.

### Phase 2: PRD Creation
Transform raw content into structured Product Requirements Document.

### Phase 3: Technical Specification
Convert PRD into technical architecture:
- **Frontend**: React components with TypeScript, SCSS modules
- **Backend**: Node.js/Python APIs with TypeScript interfaces
- **Database**: PostgreSQL schemas with migrations
- **API Design**: RESTful endpoints with OpenAPI specs

### Phase 4: Jira Breakdown
Create detailed project structure with Epics, Stories, Tasks, and time estimates.

### Phase 5: Development
Implement features using TDD methodology:
- React components with atomic design patterns
- Node.js services with TypeScript
- PostgreSQL queries with type-safe ORM
- SCSS styling following design tokens
- **Chrome DevTools**: Live UI verification, console monitoring

### Phase 6: Testing
Comprehensive testing with minimal mocking:
- Vitest/Jest for React components
- Integration tests with real PostgreSQL
- API testing with supertest
- Python tests with pytest
- **Chrome DevTools**: Visual regression, E2E screenshots, performance traces
- **Recordings saved to**: `test-recordings/` directory

### Phase 7: Code Review
Automated review against professional standards:
- Code quality and patterns
- Test coverage verification
- **Chrome DevTools**: Performance audits, Core Web Vitals, network analysis

### Phase 8: Deployment
CI/CD pipeline and production deployment.

## MCP Integrations

MCP servers are configured in `.mcp.json` at the project root.

### Configuration File: `.mcp.json`

```json
{
  "mcpServers": {
    "jira": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-atlassian"],
      "env": {
        "ATLASSIAN_SITE_URL": "${ATLASSIAN_SITE_URL}",
        "ATLASSIAN_USER_EMAIL": "${ATLASSIAN_USER_EMAIL}",
        "ATLASSIAN_API_TOKEN": "${ATLASSIAN_API_TOKEN}"
      }
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_PERSONAL_ACCESS_TOKEN}"
      }
    },
    "figma": {
      "command": "npx",
      "args": ["-y", "figma-developer-mcp"],
      "env": {
        "FIGMA_API_KEY": "${FIGMA_API_KEY}"
      }
    },
    "chrome-devtools": {
      "command": "npx",
      "args": ["-y", "chrome-devtools-mcp@latest"]
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "."]
    }
  }
}
```

> **Note:** Figma also supports a local Dev Mode MCP server - see Figma Integration section below.

### Environment Variables

Copy `.env.example` to `.env` and fill in your values:

```bash
# Jira / Atlassian
ATLASSIAN_SITE_URL=https://your-domain.atlassian.net
ATLASSIAN_USER_EMAIL=your-email@company.com
ATLASSIAN_API_TOKEN=your-api-token

# GitHub
GITHUB_PERSONAL_ACCESS_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx

# Figma (optional - can also use Dev Mode local server)
FIGMA_API_KEY=figd_xxxxxxxxxxxxxxxxxxxx
```

### Figma Integration

Two options for Figma integration:

**Option 1: API-based (configured in `.mcp.json`)**
- Get API key from Figma Settings → Account → Personal access tokens
- Add `FIGMA_API_KEY` to `.env`

**Option 2: Dev Mode Local Server (recommended for design tokens)**
1. Open Figma Desktop
2. Toggle Dev Mode (Shift+D)
3. Enable desktop MCP server in inspect panel
4. Server runs at `http://127.0.0.1:3845/mcp`

See `skills/atomic-design/references/figma-mcp-integration.md` for detailed workflow.

### Chrome DevTools Integration

Browser automation and debugging - configured in `.mcp.json`:
- **Development**: Live UI verification, console monitoring
- **Testing**: Screenshots, E2E flows, visual regression
- **Review**: Performance audits, Core Web Vitals, network analysis

```bash
# Or add via CLI
claude mcp add chrome-devtools npx chrome-devtools-mcp@latest
```

## Skills Overview

| Skill | Description |
|-------|-------------|
| `phase-enforcement` | Phase gate enforcement (blocks work out of order) ⭐ |
| `context-tracking` | Work context tracking (tasks, steps, progress) ⭐ |
| `system-architect` | Architecture design, tech specs, API patterns |
| `atomic-design` | Design system from Figma, tokens extraction |
| `atomic-page-builder` | Page composition from existing components |
| `code-review` | Automated code quality assessment |
| `test-driven` | TDD methodology and test quality |

### Slash Commands

#### Daily Workflow ⭐
| Command | Description |
|---------|-------------|
| `/good-morning` | Morning startup routine |
| `/context` | Show current work context |
| `/context-update` | Update context manually |

#### Phase Management ⭐
| Command | Description |
|---------|-------------|
| `/aid-init` | Initialize AID phases |
| `/phase` | Show current phase |
| `/gate-check` | Check gate criteria |
| `/phase-approve` | Human sign-off |
| `/phase-advance` | Advance to next phase |

#### Development
| Command | Description |
|---------|-------------|
| `/start-project` | Initialize new project |
| `/prd` | Generate PRD |
| `/tech-spec` | Create technical specification |
| `/jira-breakdown` | Generate Jira structure |
| `/design-system` | Build design system from Figma |
| `/build-page` | Compose pages from components |
| `/write-tests` | Write tests (TDD) |
| `/test-review` | Review test quality |
| `/code-review` | Review code changes |

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing`)
5. Open Pull Request

## Author

Created by **Ilan Dahan**

Built with [Claude Code](https://claude.ai) by Anthropic.
