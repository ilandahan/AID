---
description: "Initialize a brand new project from scratch"
disable-model-invocation: true
---

# /start-project Command

Create a new project folder, set up for the AID methodology, in the current directory.

## Usage

```
/start-project <project-name> [options]
```

`<project-name>` is a plain folder name: letters, digits, `.`, `_` and `-`.

## Options

| Option | Description |
|--------|-------------|
| `--template <type>` | Project template: `fullstack` (default), `api`, `frontend` |
| `--no-git` | Skip git initialization |
| `--no-deps` | Skip `npm install` |
| `--copy` | Copy AID files instead of linking them (used automatically when links fail, e.g. Git Bash on Windows without symlink rights) |

## Examples

```bash
# Full stack project (default)
/start-project my-awesome-app

# API-only project
/start-project my-api --template api

# Quick setup without dependencies or git
/start-project my-app --no-deps --no-git
```

## What Gets Created

```
<project-name>/
├── .aid/
│   └── context.json        # Work context (.aid/state.json is created by /aid-start)
├── .claude/                # Linked to (or copied from) AID's .claude/
├── CLAUDE.md               # Linked to (or copied from) AID's CLAUDE.md
├── skills/                 # Linked to (or copied from) AID's skills/
├── docs/
│   ├── prd/PRD.md          # PRD placeholder
│   └── tech-spec/TECH-SPEC.md
├── src/
│   ├── app/                # layout.tsx, page.tsx
│   ├── components/
│   │   ├── atoms/
│   │   ├── molecules/
│   │   ├── organisms/
│   │   └── templates/
│   ├── hooks/
│   ├── utils/
│   ├── types/
│   └── styles/
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── .env.example            # Non-secret settings only
├── .gitignore
├── package.json
├── tsconfig.json
└── README.md
```

The script never writes `.aid/state.json`. `hooks/aid_session.py` is its only writer;
`/aid-start` creates it after you choose a role and a phase (0-5).

## Execution

Run the init script that ships with the AID plugin, from the folder that should
contain the new project. Use exactly this form, one command, nothing chained:

```bash
bash "${CLAUDE_PLUGIN_ROOT}/scripts/init-project.sh" <project-name> [options]
```

Claude Code asks you to confirm this command before it runs, because it creates a new
project folder. Say no and nothing is created. Under `--dangerously-skip-permissions`
Claude Code does not document that a hook's "ask" still prompts, so do not count on a
prompt in that mode.

The script:
1. Creates the folder tree above.
2. Links AID's `.claude/`, `CLAUDE.md` and `skills/` into the project (or copies them).
3. Runs `git init` and a first commit (unless `--no-git`).
4. Runs `npm install` (unless `--no-deps`). This is the one place AID uses
   `npm install` instead of `npm ci`: a new project has no lockfile yet.

## After Creation

```bash
cd <project-name>
claude
```

Then, in Claude Code:

```
/aid-start
```

`/aid-start` asks for your role and the phase to start in (0-5) and creates
`.aid/state.json`. Claude Code asks you to confirm that step too.

## Next Steps

1. **Phase 0 - Discovery**: research and validation (`/discovery`)
2. **Phase 1 - PRD**: product requirements (`/prd`)
3. **Phase 2 - Tech Spec**: technical specification (`/tech-spec`)
4. **Phase 3 - Implementation Plan**: task breakdown (`/jira-breakdown`)
5. **Phase 4 - Development**: build it
6. **Phase 5 - QA & Ship**: test and release (`/qa-ship`)

Use `/phase` to see the current phase and `/gate-check` before moving on.

---

## Prompt

```markdown
**Role**: You are a senior developer initializing a new project with the AID methodology.

**Task**: Create a new project by running AID's init script, then guide the user to /aid-start.

**Context**:
- Project name: [PROJECT_NAME]
- Template: [fullstack | api | frontend]
- Methodology: AID, phases 0-5

**Steps**:
1. Check the project name: only letters, digits, `.`, `_` and `-`. Otherwise ask for another name.
2. Run exactly: `bash "${CLAUDE_PLUGIN_ROOT}/scripts/init-project.sh" [PROJECT_NAME] [options]`
   (one command; Claude Code asks the user to confirm it).
3. Verify the folder tree from "What Gets Created".
4. Do not create or edit `.aid/state.json`. Tell the user to `cd` into the project,
   start `claude` there and run `/aid-start`.

**Stopping Condition**:
- Project folder created, or the user declined the confirmation
- Clear next step: `/aid-start`

---
Project: [PROJECT_NAME]
Template: [TEMPLATE]
---
```
