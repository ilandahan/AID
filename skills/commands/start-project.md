# /start-project Command

Initialize a new project with the AI Full Stack Development methodology.

## Usage

```
/start-project <project-name> [options]
```

## Options

| Option | Description |
|--------|-------------|
| `--template <type>` | Project template: `fullstack` (default), `api`, `frontend` |
| `--no-git` | Skip git initialization |
| `--no-deps` | Skip npm install |

## Examples

```bash
# Full stack project (default)
/start-project my-awesome-app

# API-only project
/start-project my-api --template api

# Frontend-only project
/start-project my-frontend --template frontend

# Quick setup without dependencies
/start-project my-app --no-deps
```

## What Gets Created

### Directory Structure
```
<project-name>/
├── .claude/
│   └── settings.json       # Claude Code settings
├── .mcp.json               # MCP server configuration
├── docs/
│   ├── prd/                # PRD documents
│   ├── tech-specs/         # Technical specifications
│   └── decisions/          # Architecture decisions
├── skills/                 # AI methodology skills
│   ├── atomic-design/
│   ├── atomic-page-builder/
│   ├── code-review/
│   ├── system-architect/
│   └── test-driven/
├── src/
│   ├── components/
│   │   ├── atoms/
│   │   ├── molecules/
│   │   ├── organisms/
│   │   └── templates/
│   ├── pages/
│   ├── hooks/
│   ├── utils/
│   ├── types/
│   ├── api/
│   └── styles/
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── CLAUDE.md               # Project documentation for Claude
├── package.json
├── tsconfig.json
└── README.md
```

### Included Skills
- **system-architect** - Technical specifications & SaaS patterns
- **atomic-design** - Component design system
- **atomic-page-builder** - Page composition from components
- **code-review** - Code quality review
- **test-driven** - TDD methodology

### Configuration Files
- `.mcp.json` - GitHub & Filesystem MCP servers
- `.claude/settings.json` - Skills, hooks, permissions
- `tsconfig.json` - TypeScript with path aliases
- `vite.config.ts` - Vite bundler configuration
- `vitest.config.ts` - Test configuration

## Execution

When you run this command, Claude will:

1. **Execute the init script:**
   ```bash
   ./scripts/init-project.sh <project-name> [options]
   ```

2. **Copy methodology skills** into the new project

3. **Initialize git** with first commit

4. **Install dependencies** via npm

## After Creation

Navigate to your new project and start the workflow:

```bash
cd <project-name>
npm run dev

# Start with Discovery phase
/phase 1
```

## Next Steps

1. **Phase 1 - Discovery**: Define requirements
   ```
   /phase 1
   ```

2. **Create PRD**: Document product requirements
   ```
   /prd
   ```

3. **Technical Spec**: Generate technical specification
   ```
   /tech-spec
   ```

4. **Development**: Start building
   ```
   /phase 5
   ```

---

## Prompt

```markdown
**Role**: You are a senior developer initializing a new project with the AI Full Stack Development methodology.

**Task**: Create a new project with proper structure, skills, configuration, and documentation.

**Context**:
- Project name: [PROJECT_NAME]
- Template: [fullstack | api | frontend]
- Methodology: AI Full Stack Development with 8 phases
- Skills: system-architect, atomic-design, atomic-page-builder, code-review, test-driven

**Reasoning**:
- Use consistent project structure
- Include all methodology skills
- Configure MCP servers for integrations
- Set up TypeScript with strict mode
- Prepare for TDD workflow

**Output Format**:
1. Run init script: `./scripts/init-project.sh [PROJECT_NAME]`
2. Verify directory structure created
3. Confirm skills installed
4. List next steps for user

**Stopping Condition**:
- Project directory created with full structure
- All skills copied
- Git initialized with first commit
- Dependencies installed (unless --no-deps)
- Clear guidance on next steps

**Steps**:
1. Parse project name and options
2. Execute `./scripts/init-project.sh` with arguments
3. Verify structure created:
   - docs/ (prd, tech-specs, decisions)
   - src/ (components, pages, api, etc.)
   - tests/ (unit, integration, e2e)
   - skills/ (all 5 skills)
4. Verify configs created:
   - .mcp.json
   - .claude/settings.json
   - CLAUDE.md
5. Initialize git
6. Install dependencies
7. Provide next steps guidance

---
Project: [PROJECT_NAME]
Template: [TEMPLATE]
---
```
