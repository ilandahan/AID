# Work Context Tracker

## Overview

The `.aid/context.json` file maintains real-time tracking of:
- **Task level**: Previous → Current → Next Jira task
- **Step level**: Previous → Current → Next step within current task

This file is updated automatically before/after each step for seamless continuity.

---

## File Structure

### `.aid/context.json`

```json
{
  "last_updated": "2025-12-10T09:30:00Z",
  "session_id": "2025-12-10-morning",
  
  "tasks": {
    "previous": {
      "key": "PROJ-123",
      "title": "Create Button atom",
      "status": "done",
      "completed_at": "2025-12-09T16:45:00Z"
    },
    "current": {
      "key": "PROJ-124",
      "title": "Create FormField molecule",
      "status": "in_progress",
      "started_at": "2025-12-09T17:00:00Z",
      "jira_url": "https://yourcompany.atlassian.net/browse/PROJ-124"
    },
    "next": {
      "key": "PROJ-125",
      "title": "Create Card molecule",
      "status": "todo",
      "priority": "high"
    }
  },
  
  "current_task_steps": {
    "previous": {
      "name": "Write tests",
      "status": "done",
      "completed_at": "2025-12-09T17:30:00Z",
      "notes": "All 8 test cases passing"
    },
    "current": {
      "name": "Implement component",
      "status": "in_progress",
      "started_at": "2025-12-09T17:35:00Z",
      "progress": "50%",
      "notes": "Label and input done, error handling next"
    },
    "next": {
      "name": "Style with tokens",
      "status": "pending"
    }
  },
  
  "session_log": [
    {
      "timestamp": "2025-12-09T17:00:00Z",
      "action": "task_started",
      "details": "Started PROJ-124"
    },
    {
      "timestamp": "2025-12-09T17:30:00Z", 
      "action": "step_completed",
      "details": "Tests written and passing"
    },
    {
      "timestamp": "2025-12-09T17:35:00Z",
      "action": "step_started",
      "details": "Beginning implementation"
    }
  ]
}
```

---

## Update Triggers

Claude MUST update `.aid/context.json` when:

| Event | What to Update |
|-------|----------------|
| Starting new task | Move current→previous, set new current, identify next |
| Completing task | Mark current as done, shift all tasks |
| Starting step | Move current_step→previous, set new current |
| Completing step | Mark step done, update notes |
| End of session | Add session summary to log |
| Beginning of session | Create new session_id |

---

## Update Commands

### Automatic (Claude does this)
- Before starting any work
- After completing any step
- When switching tasks
- At end of significant work blocks

### Manual Override
```
/context-update          # Force update current context
/context-show            # Display current context
/context-note "message"  # Add note to current step
```

---

## Integration with /good-morning

When `/good-morning` runs, it reads `.aid/context.json` and displays:

```
═══════════════════════════════════════════════════════
📍 WHERE YOU LEFT OFF
═══════════════════════════════════════════════════════

TASKS:
  ✅ Previous: PROJ-123 "Create Button atom"
  🔄 Current:  PROJ-124 "Create FormField molecule"
  ⏳ Next:     PROJ-125 "Create Card molecule"

CURRENT TASK PROGRESS:
  ✅ Step 1: Write tests - DONE
  🔄 Step 2: Implement component - 50%
     └─ "Label and input done, error handling next"
  ⏳ Step 3: Style with tokens

Last activity: 2025-12-09 17:35 (yesterday)
═══════════════════════════════════════════════════════
```

---

## Step Types by Phase

### Phase 4 (Development) - Typical Steps per Task

```
1. Load task context from Jira
2. Read related Tech Spec section
3. Write tests (TDD)
4. Implement feature
5. Run tests / fix failures
6. Style / polish
7. Self code review
8. Update Jira status
9. Commit
```

### Phase 5 (QA) - Typical Steps per Task

```
1. Run full test suite
2. Check coverage
3. Review against checklist
4. Fix issues found
5. Final verification
6. Update documentation
7. Prepare for merge/deploy
```

---

## Context Preservation Rules

1. **Never lose context** - Always write before doing work
2. **Always have a "next"** - If no next task, flag it
3. **Notes are critical** - Capture WHY not just WHAT
4. **Timestamps everything** - For session reconstruction
5. **Session log is append-only** - Never delete history

---

## Example: Full Work Session

### Morning Start
```json
{
  "session_id": "2025-12-10-morning",
  "tasks": {
    "previous": { "key": "PROJ-123", "status": "done" },
    "current": { "key": "PROJ-124", "status": "in_progress" },
    "next": { "key": "PROJ-125", "status": "todo" }
  },
  "current_task_steps": {
    "previous": { "name": "Write tests", "status": "done" },
    "current": { "name": "Implement component", "status": "in_progress", "progress": "50%" },
    "next": { "name": "Style with tokens", "status": "pending" }
  }
}
```

### After Completing Implementation
```json
{
  "current_task_steps": {
    "previous": { "name": "Implement component", "status": "done" },
    "current": { "name": "Style with tokens", "status": "in_progress" },
    "next": { "name": "Self code review", "status": "pending" }
  },
  "session_log": [
    { "timestamp": "...", "action": "step_completed", "details": "Implementation done, all tests pass" },
    { "timestamp": "...", "action": "step_started", "details": "Starting styling" }
  ]
}
```

### After Completing Task
```json
{
  "tasks": {
    "previous": { "key": "PROJ-124", "status": "done" },
    "current": { "key": "PROJ-125", "status": "in_progress" },
    "next": { "key": "PROJ-126", "status": "todo" }
  },
  "current_task_steps": {
    "previous": null,
    "current": { "name": "Load task context", "status": "in_progress" },
    "next": { "name": "Read Tech Spec section", "status": "pending" }
  }
}
```
