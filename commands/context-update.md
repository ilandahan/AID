---
description: "Update the current work context manually"
---

# Context Update - Manual Context Update

Manually update the work context in `.aid/context.json`.

## Usage

`/context-update` - Interactive context update

## Steps to Execute

### 1. Read Current Context

Read `.aid/context.json` and display current state.

### 2. Ask What to Update

```
========================================
  CONTEXT UPDATE
========================================

What would you like to update?

[1] Current task (change to different task)
[2] Current step (change step within task)
[3] Progress (steps completed / pending)
[4] Mark step complete (advance to next)
[5] Mark task complete (advance to next task)
[6] Add blocker
[7] Add session note
[8] Full reset (start fresh)

Your choice: ___
```

### 3. Handle Each Update Type

#### [1] Update Current Task
```
Current task: {current_task}

New task:
  Task key, saved as current_task.id (or 'none'): ___
  Title: ___

Updating...
```

#### [2] Update Current Step
```
Current step: {current_step}

New step name: ___

Updating...
```

#### [3] Update Progress
```
Completed steps: {progress.steps_completed}
Pending steps:   {progress.steps_pending}

Steps to add to completed / pending: ___
Note (optional, saved to session_notes): ___

Updating...
```

#### [4] Mark Step Complete
```
Completing: {current_step}

Notes for this step: ___

Moving to next step: {next_step}
```

#### [5] Mark Task Complete
```
Completing: {current_task}

Moving to next task: {next_task}

Consider running /aid-end if this was a significant milestone.
```

#### [6] Add Blocker
```
Describe the blocker: ___
Severity (low/medium/high): ___

Blocker added as {"description": ..., "severity": ...}. This will be shown in /context and /good-morning.
```

#### [7] Add Session Note
```
Note: ___

Added to session log.
```

#### [8] Full Reset
```
⚠️ This will clear current context.

Are you sure? (yes/no): ___

What's your new current task?
  Jira key: ___
  Title: ___
  First step: ___
```

### 4. Save and Confirm

Write `.aid/context.json` in the one `aid-context-v1` shape
(`skills/context-tracking/references/context-schema.md`), changing only the fields this
command owns: `current_task`, `current_step`, `progress`, `session_notes`, `blockers` and
`last_updated`. Keep every other key as it is. The task key goes in `current_task.id` (the
QA gate reads `id`, then `key`, then `jira_key`); `jira_key` is optional. The step is the
top-level `current_step` string, never a field of `current_task`. Use `null` for
`current_task` and `current_step` when there is none.

```json
{
  "$schema": "aid-context-v1",
  "version": "1.0",
  "last_updated": "2026-11-20T10:00:00Z",
  "current_task": {"id": "PROJ-123", "title": "Add login form", "jira_key": "PROJ-123"},
  "current_step": "Implement validation",
  "progress": {"steps_completed": ["Design form"], "steps_pending": ["Write tests"]},
  "session_notes": ["Decided to reuse the auth hook"],
  "blockers": [{"description": "Waiting for API keys", "severity": "medium"}]
}
```

The task id must match `^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$` (letters, digits, `.`, `_`,
`-`; no `/` and no `..`), the same rule `aid_session.py qa-pass` uses.

After any update:
```
✅ Context updated

{show brief summary of new state}

Last updated: {timestamp}
```

## Phase Changes

This command changes only `.aid/context.json`. It never touches `.aid/state.json`, which
only `aid_session.py` writes. To change the phase, use `/phase-approve` then
`/phase-advance`, or `/aid-start` (a forward move uses `jump`, which the user confirms).
