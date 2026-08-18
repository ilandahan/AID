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
[3] Progress (update percentage/notes)
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
  Jira key (or 'none'): ___
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
Current: {step_name} ({progress}%)

New progress (0-100): ___
Notes (optional): ___

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

Blocker added. This will be shown in /context and /good-morning.
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

After any update:
```
✅ Context updated

{show brief summary of new state}

Last updated: {timestamp}
```

## Auto-sync

After update, sync with `.aid/state.json` if phase info changed.
