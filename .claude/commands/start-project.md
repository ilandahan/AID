# /start-project Command

Initialize a new project with the AID methodology.

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
├── .claude → ../AID/.claude     # Symbolic link to AID commands
├── CLAUDE.md → ../AID/CLAUDE.md # Symbolic link to AID instructions
├── skills → ../AID/skills       # Symbolic link to AID skills
├── .aid/
│   ├── state.json               # Phase state (starts at Phase 1)
│   └── context.json             # Work context tracking
├── docs/
│   ├── prd/                     # Product requirements (Phase 1)
│   │   └── README.md            # Naming: YYYY-MM-DD-[feature].md
│   ├── tech-spec/               # Technical specs (Phase 2)
│   │   └── README.md            # Naming: YYYY-MM-DD-[feature].md
│   └── implementation-plan/     # Implementation plans (Phase 3)
│       └── README.md            # Naming: YYYY-MM-DD-[feature].md
├── src/
│   ├── components/
│   │   ├── atoms/
│   │   ├── molecules/
│   │   ├── organisms/
│   │   └── templates/
│   ├── app/
│   ├── hooks/
│   ├── utils/
│   ├── types/
│   └── styles/
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── .env.example
├── package.json
├── tsconfig.json
└── README.md
```

### Symbolic Links

The project uses symbolic links to connect to AID:
- `.claude` → Commands from AID
- `CLAUDE.md` → Instructions from AID
- `skills` → Skills from AID

This allows:
- Clean separation of AID tools from your code
- Easy updates (just `git pull` in AID folder)
- Multiple projects sharing the same AID

## Execution

When you run this command, Claude will:

1. **Create project structure**
2. **Create symbolic links to AID**
3. **Initialize .aid/ folder** with state.json and context.json
4. **Create docs/ folders** (prd/, tech-spec/, implementation-plan/) with README.md
5. **Initialize git** with first commit
6. **Install dependencies** via npm (unless --no-deps)

## After Creation

Navigate to your new project and start the workflow:

```bash
cd <project-name>

# Verify AID is connected
/phase               # Should show Phase 1: PRD

# Start working
/good-morning        # Daily startup routine
```

## Next Steps

1. **Phase 1 - PRD**: Document product requirements
   ```
   /prd [feature-name]
   ```
   Creates: `docs/prd/YYYY-MM-DD-[feature].md`

2. **Get Approval**: Human sign-off
   ```
   /phase-approve
   ```

3. **Move to Phase 2**: Technical Specification
   ```
   /phase-advance
   /tech-spec [feature-name]
   ```
   Creates: `docs/tech-spec/YYYY-MM-DD-[feature].md`

4. **Move to Phase 3**: Implementation Plan
   ```
   /phase-advance
   /implementation-plan [feature-name]
   ```
   Creates: `docs/implementation-plan/YYYY-MM-DD-[feature].md`

5. **Move to Phase 4**: Development (TDD)
   ```
   /phase-advance
   /write-tests [feature-name]
   ```
   Reads all docs, writes tests FIRST

---

## Prompt

```markdown
**Role**: You are a senior developer initializing a new project with the AID methodology.

**Task**: Create a new project with proper structure and symbolic links to AID.

**Context**:
- Project name: [PROJECT_NAME]
- Template: [fullstack | api | frontend]
- AID folder location: ../AID (relative to project)

**Reasoning**:
- Use symbolic links to connect to AID
- Initialize Phase 1 (PRD) automatically
- Set up standard project structure
- Configure TypeScript with strict mode
- Prepare for TDD workflow

**Output Format**:
1. Create project directory
2. Create symbolic links to AID
3. Initialize .aid/ with state and context
4. Create docs/ structure with subfolders
5. Initialize git with first commit
6. Provide next steps guidance

**Stopping Condition**:
- Project directory created with full structure
- Symbolic links working
- .aid/ initialized at Phase 1
- docs/ folders created (prd/, tech-spec/, implementation-plan/)
- Git initialized
- Clear guidance on next steps

**Steps**:
1. Parse project name and options
2. Create project directory
3. Create symbolic links:
   - .claude → ../AID/.claude
   - CLAUDE.md → ../AID/CLAUDE.md
   - skills → ../AID/skills
4. Create .aid/state.json (Phase 1)
5. Create .aid/context.json
6. Create docs/ subfolders:
   - docs/prd/ with README.md
   - docs/tech-spec/ with README.md
   - docs/implementation-plan/ with README.md
7. Create src/ structure
8. Initialize git
9. Install dependencies (unless --no-deps)
10. Provide next steps guidance

---
Project: [PROJECT_NAME]
Template: [TEMPLATE]
---
```
