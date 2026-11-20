---
description: "Show current work context: active task, step and progress"
---

# Context - Show Current Work Context

Display the current work context from `.aid/context.json`.

## Usage

- `/context` - Show full context summary
- `/context tasks` - Show the current task only
- `/context steps` - Show the steps (completed and pending) only
- `/context log` - Show session log

## Steps to Execute

### 1. Read Context File

Read `.aid/context.json` and `.aid/state.json`. `context.json` follows the one
`aid-context-v1` schema (`skills/context-tracking/references/context-schema.md`); the phase
comes from `state.json` only. Read field by field and skip a field of an unexpected type.

### 2. Display Context Summary

```
========================================
  CURRENT WORK CONTEXT
========================================

PHASE: {state.current_phase} - {phase_name}
SESSION: {session_id}
LAST UPDATED: {last_updated}

----------------------------------------
TASK
----------------------------------------
Current:  [{current_task.id}] {current_task.title} ◄── YOU ARE HERE

----------------------------------------
STEPS
----------------------------------------
Done:     {progress.steps_completed} ✓
Current:  {current_step} ◄── IN PROGRESS
Pending:  {progress.steps_pending}

Notes: {session_notes}
Blockers: [{severity}] {description}

----------------------------------------
SESSION LOG (Last 5)
----------------------------------------
{timestamp} | {action} | {details}
...

========================================
```

## Error Handling

### No context.json
```
No .aid/context.json found.

Run /aid-init to set up context tracking: its `aid_session.py init` call creates
.aid/context.json (it never overwrites an existing one). In a project that already has
.aid/state.json, /good-morning shows where you are.
```

### Empty context
```
Context exists but has no active task.

To start tracking:
1. What task are you working on?
2. What's the first step?

Or run /context-update to set manually.
```
