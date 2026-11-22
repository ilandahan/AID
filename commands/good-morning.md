---
description: "Start the day by checking systems, loading context, and preparing to continue work"
---

# Good Morning - Daily Startup Routine

Start the day by checking systems, loading context, and preparing to continue work.

## Steps to Execute

### 1. Check Project State

Read `.aid/state.json` and `.aid/context.json` to understand:
- Current phase (from `state.json` only; `context.json` holds no phase)
- Last session info
- The current task, step, progress and blockers

`.aid/context.json` follows the one `aid-context-v1` schema
(`skills/context-tracking/references/context-schema.md`). Read it field by field: the task
id is `current_task.id` (else `key`, else `jira_key`); `current_step` is a string; skip any
field of another type instead of stopping.

### 2. Display Status Summary

```
========================================
  GOOD MORNING - AID Daily Startup
========================================

Phase: {current_phase} - {phase_name}
Last Session: {last_session_date}

CURRENT TASK:
  {current_task.id}: {current_task.title}
  Step: {current_step}
  Done: {progress.steps_completed}
  Next: {progress.steps_pending}

BLOCKERS:
  - [{severity}] {description}

========================================
```

### 3. System Checks (if available)

- Check if Docker is running (for database)
- Check MCP connections (Jira, GitHub)
- Report any issues

### 4. Ask User

```
How would you like to proceed?

[1] Continue current task ({current_task})
[2] Start the next pending step
[3] Update context manually
[4] Show full context details
```

### 5. Update Context

Update `.aid/context.json`, changing only these fields and keeping every other key:
- Add a `session_started` entry to `session_log`
- Update the `last_updated` timestamp
- Set a new `session_id`

Take every timestamp ONLY from the AID hook line `Current time (UTC): ...` in this session's
context (the SessionStart and UserPromptSubmit hooks print it), and build the `session_id`
from the date in that line (for example `2026-11-20-morning`). Never invent a time or a
session id. If that line is absent, write `null` rather than a guess.

If a system check finds a blocker (for example Docker is not running), add it to `blockers`
only as a `{"description": "<text>", "severity": "low"|"medium"|"high"}` object, never as a
plain string.

## Error Handling

### No .aid/context.json
```
No context found. Let's set it up:
1. What feature are you working on?
2. What task are you on? (Jira key or description)

Run /aid-init if project not initialized.
```

### Stale Context (>24h)
```
Context is stale (last updated {hours} hours ago).

Last state:
- Task: {task}
- Step: {step}

Is this still accurate?
  [1] Yes, continue
  [2] Update needed
  [3] Start fresh
```

## Integration

After startup, user can:
- `/phase` - Check phase requirements
- `/context` - View detailed context
- `/aid-start` - Formally start a session with role selection
