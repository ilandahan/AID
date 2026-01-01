# Context - Show Current Work Context

Display the current work context from `.aid/context.json`.

## Usage

- `/context` - Show full context summary
- `/context tasks` - Show task progression only
- `/context steps` - Show current task steps only
- `/context log` - Show session log

## Steps to Execute

### 1. Read Context File

Read `.aid/context.json` and `.aid/state.json`

### 2. Display Context Summary

```
========================================
  CURRENT WORK CONTEXT
========================================

PHASE: {phase_number} - {phase_name}
SESSION: {session_id}
LAST UPDATED: {last_updated}

----------------------------------------
TASKS
----------------------------------------
Previous: [{prev_key}] {prev_title} ✓
Current:  [{curr_key}] {curr_title} ◄── YOU ARE HERE
Next:     [{next_key}] {next_title}

----------------------------------------
CURRENT TASK STEPS
----------------------------------------
Previous: {prev_step} ✓
Current:  {curr_step} ({progress}%) ◄── IN PROGRESS
Next:     {next_step}

Notes: {current_step_notes}

----------------------------------------
SESSION LOG (Last 5)
----------------------------------------
{timestamp} | {action} | {details}
...

========================================
```

### 3. Sync Check

If context.phase doesn't match state.current_phase:
```
⚠️ Context-State mismatch detected!
Context: Phase {context_phase}
State:   Phase {state_phase}

Syncing to Phase {state_phase}...
```

## Error Handling

### No context.json
```
No .aid/context.json found.

Run /good-morning or /aid-init to set up context tracking.
```

### Empty context
```
Context exists but has no active task.

To start tracking:
1. What task are you working on?
2. What's the first step?

Or run /context-update to set manually.
```
