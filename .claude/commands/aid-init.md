# /aid-init

Initialize AID project with phases and memory system.

## Purpose

First-time setup that creates both the phase management system and the memory/learning system.

## What It Does

### 1. Project Phase System (`.aid/` in project root)

Creates project-level state files:
```
.aid/
├── state.json      # Phase tracking (which phase we're in)
└── context.json    # Work context (current task, step, progress)
```

**state.json** - Initialize with:
```json
{
  "current_phase": 1,
  "phase_name": "PRD",
  "started_at": "<current_timestamp>",
  "phases": {
    "1": { "status": "in_progress" },
    "2": { "status": "locked" },
    "3": { "status": "locked" },
    "4": { "status": "locked" },
    "5": { "status": "locked" }
  },
  "artifacts": {}
}
```

**context.json** - Initialize with:
```json
{
  "last_updated": "<current_timestamp>",
  "session_id": "<generate_uuid>",
  "tasks": { "previous": null, "current": null, "next": null },
  "current_task_steps": { "previous": null, "current": null, "next": null },
  "session_log": []
}
```

### 2. Memory System (`~/.aid/` in user home)

Creates user-level learning system:
```
~/.aid/
├── state.json          # Session state (role, phase, session info)
├── config.yaml         # Configuration
├── feedback/
│   ├── pending/        # Feedback awaiting analysis
│   └── processed/      # Analyzed feedback
├── skills/             # Copied from memory-system/skills/
├── metrics/            # Usage metrics
└── logs/               # Session logs
```

### 3. Claude Memory Initialization

If not already present, initializes 20 starter memory entries:
- Universal guidelines (5 slots)
- Role-specific (PM/Dev/QA - 5 slots each)

## Usage

```
/aid-init
```

## Output

```
✅ AID Initialized Successfully

📁 Project Setup (.aid/):
   ✓ state.json - Phase 1 (PRD) active
   ✓ context.json - Ready for tracking

🧠 Memory System (~/.aid/):
   ✓ Directory structure created
   ✓ Skills copied from memory-system/
   ✓ Feedback collection ready

💾 Claude Memory:
   ✓ 20 starter entries initialized

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Ready to start! Next steps:
1. /aid-start - Begin a work session
2. /phase - Check current phase status
3. /good-morning - Daily startup routine
```

## Notes

- Safe to run multiple times (won't overwrite existing data)
- Use `/aid-reset` to start completely fresh
- Templates located in:
  - `templates/.aid/` - Project state templates
  - `memory-system/templates/` - Memory system templates
- See `docs/PHASE-GATES.md` for phase system details
- See `memory-system/docs/` for memory system details
