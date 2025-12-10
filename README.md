# AI Full Stack Development Methodology

<div align="center">

**Transform raw requirements into production-ready software using Claude Code**

[![Claude Code](https://img.shields.io/badge/Claude-Code-orange)](https://claude.ai)

*Created by Ilan Dahan*

</div>

---

## 🚀 Easy Setup Guide (No Technical Knowledge Required)

This section is for anyone who wants to use AID - no programming experience needed!

### What is AID?

AID (AI Development Methodology) helps you build software with AI assistance. You describe what you want, and Claude guides you through building it step-by-step.

### What You Need

1. **Claude Code** - The AI assistant that will help you (choose one):
   - [Claude Code Desktop App](https://claude.ai/download) - Easiest option, just download and install
   - Claude Code Terminal - For those comfortable with command line

2. **This AID folder** - Download it from GitHub

### Step-by-Step Installation

#### Option A: Using Claude Code Desktop App (Recommended)

1. **Download Claude Code Desktop**
   - Go to [claude.ai/download](https://claude.ai/download)
   - Download for your system (Windows/Mac)
   - Install it like any other app

2. **Download AID**
   - Click the green "Code" button on this GitHub page
   - Click "Download ZIP"
   - Extract the ZIP file to a folder (e.g., `Documents/AID`)

3. **Open AID in Claude Code**
   - Open Claude Code Desktop
   - Click "Open Folder" or drag the AID folder into Claude Code
   - You should see the files in the sidebar

4. **Run Setup**
   - In the chat, type: `/setup`
   - Press Enter
   - Claude will guide you through everything!

#### Option B: Using Claude Code in Terminal

1. **Install Claude Code CLI**
   ```bash
   npm install -g @anthropic-ai/claude-code
   ```

2. **Download AID**
   ```bash
   git clone https://github.com/ilandahan/AID.git
   cd AID
   ```

3. **Open Claude Code**
   ```bash
   claude
   ```

4. **Run Setup**
   - Type: `/setup`
   - Press Enter
   - Follow the instructions

### What Happens During Setup?

When you type `/setup`, Claude will:

1. ✅ Check what's already installed on your computer
2. ✅ Offer to install any missing tools (you can say yes or no)
3. ✅ Install the required packages
4. ✅ Help you set up your API tokens (optional, with instructions)
5. ✅ Run tests to make sure everything works
6. ✅ Give you a summary of what to do next

**The entire process takes about 5-10 minutes.**

### After Setup

Once setup is complete:
- Type `/good-morning` each day to start working
- Type `/phase` to see where you are in the process
- Just tell Claude what you want to build!

### Need Help?

If something doesn't work:
- Just describe the problem to Claude
- Paste any error messages you see
- Claude will help you fix it

---

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

---

## Technical Installation (For Developers)

### Quick Start

```bash
# Clone and install
git clone https://github.com/ilandahan/AID.git
cd AID
./install.sh

# Or use make
make install
```

> ⚠️ **Important:** After installation, restart Claude Code to load MCP servers.

## Project Setup Guide

### Recommended Structure: AID + Project in Parallel Folders

```
📁 workspace/
├── 📁 AID/                    ← This repository (methodology & tools)
│   ├── .claude/commands/
│   ├── skills/
│   ├── CLAUDE.md
│   └── ...
│
└── 📁 my-project/             ← Your project (separate folder)
    ├── .claude → ../AID/.claude        ← Symbolic link
    ├── CLAUDE.md → ../AID/CLAUDE.md    ← Symbolic link
    ├── .aid/                           ← Your project state
    │   ├── state.json
    │   └── context.json
    ├── src/
    └── ...
```

### Step-by-Step Setup

#### 1. Clone AID Repository

```bash
cd ~/workspace  # or your preferred location
git clone https://github.com/ilandahan/AID.git
```

#### 2. Create Your Project Folder

```bash
mkdir my-project
cd my-project
```

#### 3. Create Symbolic Links to AID

**Mac / Linux:**
```bash
ln -s ../AID/.claude .claude
ln -s ../AID/CLAUDE.md CLAUDE.md
ln -s ../AID/skills skills
```

**Windows (PowerShell as Administrator):**
```powershell
New-Item -ItemType SymbolicLink -Path ".claude" -Target "..\AID\.claude"
New-Item -ItemType SymbolicLink -Path "CLAUDE.md" -Target "..\AID\CLAUDE.md"
New-Item -ItemType SymbolicLink -Path "skills" -Target "..\AID\skills"
```

**Windows (Command Prompt as Administrator):**
```cmd
mklink /D .claude ..\AID\.claude
mklink CLAUDE.md ..\AID\CLAUDE.md
mklink /D skills ..\AID\skills
```

#### 4. Initialize Your Project with AID

```bash
# Open Claude Code in your project
cd my-project
claude

# Initialize AID phases
/aid-init
```

This creates `.aid/state.json` and `.aid/context.json` in your project folder.

#### 5. Verify Setup

```bash
# Check symbolic links work
ls -la .claude        # Should show link to ../AID/.claude
cat CLAUDE.md         # Should display AID instructions

# In Claude Code
/phase               # Should show "Phase 1: PRD"
/good-morning        # Should run startup routine
```

### Benefits of This Structure

| Benefit | Description |
|---------|-------------|
| **Clean separation** | AID tools separate from your code |
| **Easy updates** | `git pull` in AID folder updates all projects |
| **Multiple projects** | Same AID serves many projects |
| **Git-friendly** | Your project has its own Git history |

### Updating AID

When a new version of AID is released:

```bash
cd ~/workspace/AID
git pull origin main
```

That's it! All projects using symbolic links automatically get the update.

### Troubleshooting

**Symbolic links not working?**
- Windows: Run PowerShell/CMD as Administrator
- Mac/Linux: Check path is correct with `ls -la`

**Claude Code doesn't see commands?**
- Restart Claude Code after creating links
- Verify with `ls .claude/commands/`

**Permission denied on Windows?**
- Enable Developer Mode: Settings → Update & Security → For Developers → Developer Mode
- Or run terminal as Administrator

---

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
- Python 3.11+ (Backend, Scripts)
- PostgreSQL 16+ (Database)
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

#### Testing ⭐
| Command | Description |
|---------|-------------|
| `/aid-test` | Run full methodology test suite |

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
