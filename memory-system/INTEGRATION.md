# Memory System Integration with AID Repository

Files that need to be placed in specific locations in the AID repo.

## Files to Distribute

### 1. CLAUDE.md Addition

Add this section to your existing `CLAUDE.md`:

```markdown
## Memory System

AID includes a learning system that improves over time.

### Quick Commands
- `/aid init` - Initialize memory system
- `/aid start` - Start work session
- `/aid end` - End phase with feedback
- `/aid improve` - Run learning cycle

### How It Works
At session start, Claude loads relevant skills from `memory-system/skills/`.
At phase end, feedback is collected and stored.
Weekly, the `/aid improve` command analyzes patterns and updates skills.

### Files
- Skills: `memory-system/skills/`
- Docs: `memory-system/docs/`
- Runtime: `~/.aid/` (created on init)

See `memory-system/README.md` for full documentation.
```

### 2. Slash Commands

Create/update these in your `slash-commands/` or `commands/` directory:

**`/aid-init.md`**
```markdown
# /aid init

Initialize the AID Memory System.

## What It Does
1. Creates `~/.aid/` directory structure
2. Copies skill templates from repo
3. Initializes state.json and config.yaml
4. Sets up feedback directories

## Implementation
See: `memory-system/docs/COMMANDS.md#init`
```

**`/aid-start.md`**
```markdown
# /aid start

Start a new work session.

## Flow
1. Ask for role (PM/Developer/QA/Lead)
2. Ask for phase (Discovery/PRD/Tech-Spec/Development/QA-Ship)
3. Load relevant skills
4. Update state.json
5. Greet user with context

## Implementation
See: `memory-system/docs/AGENT.md#session-start`
```

**`/aid-end.md`**
```markdown
# /aid end

End current phase and collect feedback.

## Flow
1. Summarize work done
2. Ask for rating (1-5)
3. Ask what worked well
4. Ask what could improve
5. Save feedback to pending/
6. Offer to continue or stop

## Implementation
See: `memory-system/docs/AGENT.md#phase-gate`
```

**`/aid-improve.md`**
```markdown
# /aid improve

Run the improvement analysis cycle.

## Requirements
- At least 3 pending feedback items
- Or manual override with confirmation

## Flow
1. Gather all pending feedback
2. Run sub-agent analysis
3. Present suggestions to user
4. Apply approved changes
5. Archive processed feedback

## Implementation
See: `memory-system/docs/IMPROVEMENT-FLOW.md`
```

**`/aid-status.md`**
```markdown
# /aid status

Show current memory system state.

## Output
- Current role and phase
- Session duration
- Pending feedback count
- Last improvement date
- Skills loaded

## Implementation
See: `memory-system/docs/COMMANDS.md#status`
```

**`/aid-memory.md`**
```markdown
# /aid memory [list|stats]

Manage Claude Memory entries.

## Subcommands
- `list` - Show all AID entries in Claude Memory
- `stats` - Show slot usage by category

## Implementation
See: `memory-system/docs/MEMORY.md`
```

### 3. Skills Integration

If your AID repo already has a `skills/` directory, you have options:

**Option A: Keep Separate**
```
aid-repo/
├── skills/              # Existing skills
└── memory-system/
    └── skills/          # Memory system skills
```

**Option B: Merge**
```
aid-repo/
└── skills/
    ├── existing/        # Your existing skills
    ├── roles/           # From memory-system
    └── phases/          # From memory-system
```

**Option C: Reference**
Keep memory-system skills separate but reference them from CLAUDE.md.

### 4. work_context.json Update

If you use `work_context.json`, add memory system fields:

```json
{
  "project": "...",
  "current_task": "...",
  
  "memory_system": {
    "role": "developer",
    "phase": "development",
    "session_start": "2024-01-15T09:00:00Z",
    "feedback_pending": 2
  }
}
```

## Recommended Repository Structure

```
aid-repo/
├── CLAUDE.md                    # Add memory system section
├── README.md
├── commands/                    # Or slash-commands/
│   ├── aid-init.md             # NEW
│   ├── aid-start.md            # NEW
│   ├── aid-end.md              # NEW
│   ├── aid-improve.md          # NEW
│   ├── aid-status.md           # NEW
│   ├── aid-memory.md           # NEW
│   └── [existing commands]
├── memory-system/               # NEW - entire directory
│   ├── README.md
│   ├── docs/
│   ├── skills/
│   ├── templates/
│   └── samples/
├── [existing directories]
└── work_context.json           # Update schema
```

## Quick Integration Checklist

- [ ] Copy `memory-system/` directory to repo root
- [ ] Add memory system section to `CLAUDE.md`
- [ ] Create slash command files in `commands/`
- [ ] Update `work_context.json` schema (if used)
- [ ] Run `/aid init` to test
- [ ] Commit all changes

## Files Created by This Package

**In repo (version controlled):**
- `memory-system/` - All 36 files

**At runtime (not in repo):**
- `~/.aid/` - Created by `/aid init`
