# Context Tracking Skill

## Purpose

Maintain real-time work context in `.aid/context.json` for seamless session continuity.

---

## Core Rule

**Claude MUST update `.aid/context.json` at these moments:**

| Moment | Action |
|--------|--------|
| Before starting any work | Read current context |
| Starting new task | Shift tasks, reset steps |
| Starting new step | Shift steps, add to log |
| Completing step | Mark done, add notes, shift |
| Completing task | Mark done, shift tasks |
| Any significant progress | Update progress %, notes |
| End of conversation | Final context save |

---

## Context Structure

```json
{
  "last_updated": "ISO timestamp",
  "session_id": "YYYY-MM-DD-period",
  
  "tasks": {
    "previous": { "key": "PROJ-123", "title": "...", "status": "done" },
    "current": { "key": "PROJ-124", "title": "...", "status": "in_progress" },
    "next": { "key": "PROJ-125", "title": "...", "status": "todo" }
  },
  
  "current_task_steps": {
    "previous": { "name": "...", "status": "done" },
    "current": { "name": "...", "status": "in_progress", "progress": "50%", "notes": "..." },
    "next": { "name": "...", "status": "pending" }
  },
  
  "session_log": [
    { "timestamp": "...", "action": "...", "details": "..." }
  ]
}
```

---

## Update Operations

### 1. Start New Task

```python
def start_new_task(new_task):
    context.tasks.previous = context.tasks.current
    context.tasks.current = new_task
    context.tasks.current.status = "in_progress"
    context.tasks.current.started_at = now()
    context.tasks.next = get_next_from_sprint()
    
    # Reset steps for new task
    context.current_task_steps = {
        "previous": None,
        "current": {"name": "Load task context", "status": "in_progress"},
        "next": {"name": "Review requirements", "status": "pending"}
    }
    
    log("task_started", f"Started {new_task.key}")
```

### 2. Complete Step

```python
def complete_step(notes=""):
    context.current_task_steps.previous = context.current_task_steps.current
    context.current_task_steps.previous.status = "done"
    context.current_task_steps.previous.completed_at = now()
    context.current_task_steps.previous.notes = notes
    
    context.current_task_steps.current = context.current_task_steps.next
    context.current_task_steps.current.status = "in_progress"
    context.current_task_steps.current.started_at = now()
    
    context.current_task_steps.next = determine_next_step()
    
    log("step_completed", notes)
```

### 3. Update Progress

```python
def update_progress(progress, notes=""):
    context.current_task_steps.current.progress = progress
    if notes:
        context.current_task_steps.current.notes = notes
    context.last_updated = now()
```

### 4. Complete Task

```python
def complete_task():
    context.tasks.previous = context.tasks.current
    context.tasks.previous.status = "done"
    context.tasks.previous.completed_at = now()
    
    context.tasks.current = context.tasks.next
    context.tasks.next = get_next_from_sprint()
    
    # Reset steps
    context.current_task_steps = {
        "previous": None,
        "current": None,
        "next": None
    }
    
    log("task_completed", f"Completed {context.tasks.previous.key}")
```

---

## Standard Steps by Task Type

### Component Development (Phase 4)
```
1. Load task context
2. Read Tech Spec section  
3. Write tests (TDD)
4. Implement component
5. Run tests / fix
6. Apply styling
7. Self code review
8. Update Jira
9. Commit
```

### Bug Fix
```
1. Load task context
2. Reproduce issue
3. Write failing test
4. Implement fix
5. Verify fix
6. Update Jira
7. Commit
```

### QA Task (Phase 5)
```
1. Load task context
2. Run test suite
3. Check coverage
4. Review checklist
5. Document findings
6. Fix issues
7. Final verification
```

---

## Session Log Actions

| Action | When |
|--------|------|
| `session_started` | /good-morning or first interaction |
| `task_started` | Beginning new Jira task |
| `task_completed` | Finishing Jira task |
| `step_started` | Beginning step within task |
| `step_completed` | Finishing step |
| `progress_update` | Significant progress milestone |
| `blocker_noted` | Hit a blocker |
| `context_saved` | Manual context save |
| `session_ended` | End of work session |

---

## Reading Context (for /good-morning)

```python
def display_context():
    ctx = read_context()
    
    print("📍 WHERE YOU LEFT OFF")
    print("")
    print("TASKS:")
    print(f"  ✅ Previous: {ctx.tasks.previous.key} - {ctx.tasks.previous.title}")
    print(f"  🔄 Current:  {ctx.tasks.current.key} - {ctx.tasks.current.title}")
    print(f"  ⏳ Next:     {ctx.tasks.next.key} - {ctx.tasks.next.title}")
    print("")
    print("CURRENT TASK PROGRESS:")
    for step in [ctx.steps.previous, ctx.steps.current, ctx.steps.next]:
        # Show step with status icon
    print("")
    print(f"Last activity: {ctx.last_updated}")
```

---

## Context File Location

```
.aid/
├── state.json      # Phase-level state
├── context.json    # Task/step-level context (THIS FILE)
└── approvals/
```

---

## Error Handling

### No context.json exists
→ Create from template, ask user about current task

### Context is stale (>24h old)
→ Show warning, ask to verify/update

### Current task doesn't match Jira
→ Sync with Jira, update context

### Next task is null
→ Fetch from sprint backlog or ask user
