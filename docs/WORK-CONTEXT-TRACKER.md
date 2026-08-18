# Work Context Tracker

The AID context tracker maintains session continuity by tracking the current task, step, progress, and blockers in `.aid/context.json`.

## Purpose

When a session ends or context is lost, the tracker ensures work can resume seamlessly. Claude reads the context file at the start of every session to understand where work left off.

## Context File Location

`.aid/context.json` — automatically updated during work sessions.

## Schema

```json
{
  "$schema": "aid-context-v1",
  "version": "1.0",
  "last_updated": "ISO-8601",
  "current_task": {
    "key": "TASK-ID",
    "title": "Task title",
    "description": "What needs to be done",
    "phase": 4,
    "phase_note": "Additional phase context"
  },
  "current_step": {
    "name": "Current step description",
    "progress": 0,
    "notes": "Step-specific notes"
  },
  "progress": {
    "steps_completed": ["Step 1", "Step 2"],
    "steps_pending": ["Step 3", "Step 4"]
  },
  "session_notes": [
    {
      "timestamp": "ISO-8601",
      "note": "What happened"
    }
  ],
  "blockers": [
    {
      "id": "BLOCKER-001",
      "description": "What's blocking",
      "severity": "high|medium|low",
      "resolution": "How to resolve"
    }
  ]
}
```

## When Context Updates

Claude updates `.aid/context.json` when:
- Starting a new task
- Completing a step
- Significant progress is made
- A blocker is identified or resolved
- Session ends

## Commands

| Command | Purpose |
|---------|---------|
| `/context` | Show current work context |
| `/context-update` | Manually update context |
| `/good-morning` | Load context and resume work |

## Related

- Skill: `.claude/skills/context-tracking/SKILL.md`
- State file: `.aid/state.json` (phase tracking, complements context)
