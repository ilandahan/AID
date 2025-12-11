# /link-project

Link an existing project to the AID methodology using symbolic links.

## Usage

```
/link-project [project-path]
```

## What It Does

1. Creates symbolic links from your project to AID
2. Initializes `.aid/` folder with state and context
3. Sets up the project to use AID commands and skills

## Prerequisites

- AID repository cloned/downloaded
- An existing project folder (parallel to AID)

## Expected Structure

Before:
```
workspace/
├── AID/                    ← This repository
│   ├── .claude/commands/
│   ├── skills/
│   ├── CLAUDE.md
│   └── ...
│
└── my-project/             ← Your existing project
    ├── src/
    ├── package.json
    └── ...
```

After running `/link-project`:
```
workspace/
├── AID/
│   └── ...
│
└── my-project/
    ├── .claude → ../AID/.claude         ← Symbolic link
    ├── CLAUDE.md → ../AID/CLAUDE.md     ← Symbolic link
    ├── skills → ../AID/skills           ← Symbolic link
    ├── .aid/                            ← Created
    │   ├── state.json
    │   └── context.json
    ├── src/
    └── ...
```

---

## Step-by-Step Process

### Step 1: Verify Locations

```
═══════════════════════════════════════════════════════════════════
                    LINK PROJECT TO AID
═══════════════════════════════════════════════════════════════════

Let's connect your project to AID.

First, I need to know:
  1. Where is your project folder?
  2. Where is the AID folder?

Current directory: /path/to/current

Is your project in a folder parallel to AID? (y/n)
```

### Step 2: Detect AID Location

If in AID folder:
```
I'm currently in the AID folder.

Where is your project?
  Example: ../my-project

Enter project path:
```

If in project folder:
```
I'm currently in what looks like a project folder.

Where is AID?
  Example: ../AID

Enter AID path:
```

### Step 3: Create Symbolic Links

**Mac / Linux:**
```bash
cd /path/to/my-project

# Create symbolic links
ln -s ../AID/.claude .claude
ln -s ../AID/CLAUDE.md CLAUDE.md
ln -s ../AID/skills skills

echo "Symbolic links created"
```

**Windows (requires admin or developer mode):**
```cmd
cd \path\to\my-project

mklink /D .claude ..\AID\.claude
mklink CLAUDE.md ..\AID\CLAUDE.md
mklink /D skills ..\AID\skills

echo Symbolic links created
```

### Step 4: Initialize .aid/ Folder

```bash
mkdir -p .aid/approvals
```

Create `.aid/state.json`:
```json
{
  "current_phase": 1,
  "phase_name": "PRD",
  "project_name": "my-project",
  "initialized_at": "2025-12-10T12:00:00Z",
  "phases": {
    "1": { "name": "PRD", "status": "in_progress" },
    "2": { "name": "Tech Spec", "status": "locked" },
    "3": { "name": "Breakdown", "status": "locked" },
    "4": { "name": "Development", "status": "locked" },
    "5": { "name": "QA & Ship", "status": "locked" }
  }
}
```

Create `.aid/context.json`:
```json
{
  "last_updated": "2025-12-10T12:00:00Z",
  "tasks": {
    "previous": null,
    "current": null,
    "next": null
  },
  "current_task_steps": {
    "previous": null,
    "current": null,
    "next": null
  },
  "notes": "Project linked to AID. Start with /prd to create requirements."
}
```

### Step 5: Ask About Current State

```
═══════════════════════════════════════════════════════════════════

Project linked successfully!

One more thing - what phase is your project in?

  [1] Just starting - no PRD yet (Phase 1)
  [2] Have PRD, need Tech Spec (Phase 2)
  [3] Have Tech Spec, need task breakdown (Phase 3)
  [4] Ready for development (Phase 4)
  [5] In QA/shipping (Phase 5)

>
```

Update `state.json` based on response.

### Step 6: Completion

```
═══════════════════════════════════════════════════════════════════
                    PROJECT LINKED SUCCESSFULLY
═══════════════════════════════════════════════════════════════════

Your project is now connected to AID!

Created:
  .claude → ../AID/.claude
  CLAUDE.md → ../AID/CLAUDE.md
  skills → ../AID/skills
  .aid/state.json
  .aid/context.json

Current Phase: [X] - [Phase Name]

═══════════════════════════════════════════════════════════════════

Next steps:

  1. Open your project in Claude Code:
     cd my-project
     claude

  2. Verify the link:
     /phase

  3. Start working:
     /good-morning

═══════════════════════════════════════════════════════════════════

Benefits of linking:
  - Updates to AID automatically apply to your project
  - All AID commands available (/phase, /prd, etc.)
  - Phase gates enforced
  - Context tracking enabled

═══════════════════════════════════════════════════════════════════
```

---

## Troubleshooting

### Symbolic Links Failed (Windows)

```
Symbolic links require either:
  1. Administrator privileges, OR
  2. Developer Mode enabled

To enable Developer Mode:
  1. Open Settings
  2. Go to: Update & Security → For developers
  3. Enable "Developer Mode"

Or run as Administrator.

Alternative: Copy files instead of linking?
  (You'll need to manually update when AID changes)

  [1] Try again with admin
  [2] Copy files instead
  [3] Cancel

>
```

### AID Folder Not Found

```
Could not find AID folder at: ../AID

Please check:
  1. AID is downloaded/cloned
  2. It's in the correct location
  3. The folder is named "AID" (or provide full path)

Enter correct path to AID (or 'cancel'):
```

### Project Already Linked

```
This project already has AID links:
  .claude exists
  CLAUDE.md exists
  skills exists

What would you like to do?
  [1] Re-link (recreate symbolic links)
  [2] Just initialize .aid/ folder
  [3] Cancel

>
```

---

## Examples

### Link from AID folder
```bash
# You're in the AID folder
claude
> /link-project ../my-app
```

### Link from project folder
```bash
# You're in your project folder
claude
> /link-project
# Claude will detect you're in a project and ask for AID location
```

### Link with absolute paths
```bash
claude
> /link-project /Users/me/projects/my-app
# Provide AID path when asked: /Users/me/tools/AID
```

---

## Unlinking

To remove the link (keep project, just disconnect from AID):

```bash
cd my-project

# Remove symbolic links
rm .claude      # or rmdir on Windows
rm CLAUDE.md
rm skills       # or rmdir on Windows

# Optionally keep .aid/ for state, or remove it too
# rm -rf .aid
```

---

## Notes

- Symbolic links are the recommended approach
- If symlinks fail, falling back to copy is possible but requires manual updates
- The `.aid/` folder is always created fresh in your project (not linked)
- Your project code is never modified
