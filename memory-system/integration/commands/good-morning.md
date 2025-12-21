# Good Morning - Daily Startup Routine

Start the day by checking systems, loading context, and preparing to continue work.

## Steps to Execute

### 1. Check Project State

Read `.aid/state.json` and `.aid/context.json` to understand:
- Current phase
- Last session info
- Current/previous/next tasks

### 2. Display Status Summary

```
========================================
  GOOD MORNING - AID Daily Startup
========================================

Phase: {current_phase} - {phase_name}
Last Session: {last_session_date}

YESTERDAY'S PROGRESS:
  Task: {previous_task}
  Status: {status}

CURRENT TASK:
  {current_task_key}: {current_task_title}
  Step: {current_step} ({progress}%)

NEXT UP:
  {next_task_key}: {next_task_title}

========================================
```

### 3. System Checks (if available)

- Check if Docker is running (for database)
- Check MCP connections (Jira, GitHub, Figma)
- Report any issues

### 4. Ask User

```
How would you like to proceed?

[1] Continue current task ({current_task})
[2] Start fresh with next task
[3] Update context manually
[4] Show full context details
```

### 5. Update Context

Update `.aid/context.json`:
- Add `session_started` to session_log
- Update `last_updated` timestamp
- Set new `session_id`

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
