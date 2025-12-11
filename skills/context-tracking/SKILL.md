# Context Tracking Skill

## Purpose

Maintain real-time work context in `.aid/context.json` for seamless session continuity, integrated with phase enforcement and quality feedback systems.

---

## PRIORITY 1: Context State Management

```
┌─────────────────────────────────────────────────────────────────┐
│  CONTEXT TRACKING CORE RULE                                     │
│                                                                 │
│  Claude MUST maintain context at ALL times:                     │
│                                                                 │
│  1. READ context before starting any work                       │
│  2. UPDATE context on every significant change                  │
│  3. SYNC with phase state (.aid/state.json)                     │
│  4. INTEGRATE with feedback system (/aid end)                   │
│  5. SAVE context at conversation end                            │
└─────────────────────────────────────────────────────────────────┘
```

---

## Context Update Triggers

| Moment | Action | Updates |
|--------|--------|---------|
| Session start | Read context | Load previous/current/next |
| Starting new task | Shift tasks | Reset steps, log entry |
| Starting new step | Shift steps | Add to session log |
| Completing step | Mark done | Notes, timestamp, shift |
| Completing task | Mark done | Shift tasks, prompt feedback |
| Progress milestone | Update % | Notes, timestamp |
| Phase change | Sync state | Update phase in context |
| End of conversation | Final save | All pending changes |

---

## Context Structure

### `.aid/context.json`

```json
{
  "last_updated": "2024-12-11T15:30:00Z",
  "session_id": "2024-12-11-afternoon",

  "phase": {
    "current": 4,
    "name": "development",
    "started_at": "2024-12-10T09:00:00Z"
  },

  "project": {
    "name": "user-authentication",
    "documents": {
      "prd": "docs/prd/2024-12-09-user-authentication.md",
      "tech_spec": "docs/tech-spec/2024-12-10-user-authentication.md",
      "implementation_plan": "docs/implementation-plan/2024-12-10-user-authentication.md"
    }
  },

  "tasks": {
    "previous": {
      "key": "PROJ-123",
      "title": "Create LoginForm component",
      "status": "done",
      "completed_at": "2024-12-11T14:00:00Z"
    },
    "current": {
      "key": "PROJ-124",
      "title": "Create AuthService",
      "status": "in_progress",
      "started_at": "2024-12-11T14:15:00Z",
      "jira_url": "https://company.atlassian.net/browse/PROJ-124"
    },
    "next": {
      "key": "PROJ-125",
      "title": "Create SessionManager",
      "status": "todo"
    }
  },

  "current_task_steps": {
    "previous": {
      "name": "Write unit tests",
      "status": "done",
      "completed_at": "2024-12-11T15:00:00Z",
      "notes": "8 tests passing, covering all auth flows"
    },
    "current": {
      "name": "Implement service",
      "status": "in_progress",
      "started_at": "2024-12-11T15:00:00Z",
      "progress": "60%",
      "notes": "Login and logout done, token refresh next"
    },
    "next": {
      "name": "Integration tests",
      "status": "pending"
    }
  },

  "session_log": [
    {
      "timestamp": "2024-12-11T14:15:00Z",
      "action": "task_started",
      "details": "Started PROJ-124: Create AuthService"
    },
    {
      "timestamp": "2024-12-11T15:00:00Z",
      "action": "step_completed",
      "details": "Unit tests complete: 8 tests passing"
    },
    {
      "timestamp": "2024-12-11T15:30:00Z",
      "action": "progress_update",
      "details": "Implementation at 60%"
    }
  ],

  "feedback": {
    "pending_for_phase": false,
    "last_feedback_at": "2024-12-10T18:00:00Z",
    "sessions_since_feedback": 2
  }
}
```

---

## PRIORITY 2: Phase Integration

```
┌─────────────────────────────────────────────────────────────────┐
│  CONTEXT-PHASE SYNCHRONIZATION                                  │
│                                                                 │
│  context.json              state.json                           │
│  ────────────              ──────────                           │
│  phase.current    ◄────►   current_phase                        │
│  project.documents ◄────►  documents                            │
│  feedback.pending  ◄────►  feedback_collected                   │
│                                                                 │
│  On phase change: sync both files                               │
│  On feedback: update both files                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Phase-Aware Context

| Phase | Task Types | Step Templates |
|-------|------------|----------------|
| 1 - PRD | Requirements | User stories, acceptance criteria |
| 2 - Tech Spec | Architecture | Design, API contracts, security |
| 3 - Impl Plan | Planning | Task breakdown, estimates |
| 4 - Development | Coding | TDD cycle, implementation, review |
| 5 - QA & Ship | QA | Testing, coverage, deployment |

### Document Tracking

Context tracks all phase documents:

```javascript
const documentPaths = {
  1: "docs/prd/YYYY-MM-DD-[feature].md",
  2: "docs/tech-spec/YYYY-MM-DD-[feature].md",
  3: "docs/implementation-plan/YYYY-MM-DD-[feature].md",
};
```

---

## PRIORITY 3: Feedback Integration

```
┌─────────────────────────────────────────────────────────────────┐
│  CONTEXT-FEEDBACK FLOW                                          │
│                                                                 │
│  Task Complete?                                                 │
│       │                                                         │
│       ▼                                                         │
│  Update Context (task → done)                                   │
│       │                                                         │
│       ▼                                                         │
│  Check: Is this phase ending?                                   │
│       │                                                         │
│       ├── Yes ──▶ Prompt: "/aid end for phase feedback"         │
│       │                                                         │
│       ▼                                                         │
│  Check: Sessions since feedback >= 3?                           │
│       │                                                         │
│       ├── Yes ──▶ Remind: "Consider /aid end for feedback"      │
│       │                                                         │
│       ▼                                                         │
│  Continue to next task                                          │
└─────────────────────────────────────────────────────────────────┘
```

### Feedback Tracking in Context

```json
{
  "feedback": {
    "pending_for_phase": true,
    "last_feedback_at": "2024-12-10T18:00:00Z",
    "sessions_since_feedback": 3,
    "tasks_completed_since_feedback": 5,
    "reminder_shown": false
  }
}
```

### Feedback Reminders

| Condition | Reminder |
|-----------|----------|
| Phase ending | "Run /aid end before advancing to next phase" |
| 3+ sessions without feedback | "Consider /aid end to share what worked" |
| 5+ tasks completed | "Good time for /aid end checkpoint" |

---

## Update Operations

### 1. Start Session (Read Context)

```python
def start_session():
    context = read_context(".aid/context.json")
    state = read_state(".aid/state.json")

    # Sync phase
    if context.phase.current != state.current_phase:
        context.phase.current = state.current_phase
        context.phase.name = PHASE_NAMES[state.current_phase]

    # Check staleness
    if hours_since(context.last_updated) > 24:
        show_warning("Context is stale (>24h). Please verify.")

    # Check feedback status
    if context.feedback.sessions_since_feedback >= 3:
        show_reminder("Consider running /aid end for feedback")

    log("session_started", f"Loaded context for {context.tasks.current.key}")
    return context
```

### 2. Start New Task

```python
def start_new_task(new_task):
    # Shift task chain
    context.tasks.previous = context.tasks.current
    context.tasks.current = new_task
    context.tasks.current.status = "in_progress"
    context.tasks.current.started_at = now()
    context.tasks.next = get_next_from_sprint()

    # Reset steps for new task
    context.current_task_steps = get_steps_template(
        task_type=new_task.type,
        phase=context.phase.current
    )

    # Update feedback counter
    context.feedback.tasks_completed_since_feedback += 1

    log("task_started", f"Started {new_task.key}: {new_task.title}")
    save_context()
```

### 3. Complete Step

```python
def complete_step(notes=""):
    # Update previous step
    context.current_task_steps.previous = context.current_task_steps.current
    context.current_task_steps.previous.status = "done"
    context.current_task_steps.previous.completed_at = now()
    context.current_task_steps.previous.notes = notes

    # Shift to next step
    context.current_task_steps.current = context.current_task_steps.next
    if context.current_task_steps.current:
        context.current_task_steps.current.status = "in_progress"
        context.current_task_steps.current.started_at = now()

    # Determine next step
    context.current_task_steps.next = determine_next_step()

    log("step_completed", notes)
    save_context()
```

### 4. Complete Task

```python
def complete_task():
    # Mark task done
    context.tasks.previous = context.tasks.current
    context.tasks.previous.status = "done"
    context.tasks.previous.completed_at = now()

    # Shift to next task
    context.tasks.current = context.tasks.next
    context.tasks.next = get_next_from_sprint()

    # Reset steps
    context.current_task_steps = {
        "previous": None,
        "current": None,
        "next": None
    }

    # Update feedback tracking
    context.feedback.tasks_completed_since_feedback += 1

    # Check if feedback reminder needed
    if context.feedback.tasks_completed_since_feedback >= 5:
        show_reminder("5 tasks completed - good time for /aid end")

    log("task_completed", f"Completed {context.tasks.previous.key}")
    save_context()
```

### 5. Update Progress

```python
def update_progress(progress, notes=""):
    context.current_task_steps.current.progress = progress
    if notes:
        context.current_task_steps.current.notes = notes
    context.last_updated = now()

    log("progress_update", f"{progress} - {notes}")
    save_context()
```

### 6. Phase Transition

```python
def handle_phase_transition(new_phase):
    # Sync with state.json
    state = read_state()
    state.current_phase = new_phase
    save_state(state)

    # Update context
    context.phase.current = new_phase
    context.phase.name = PHASE_NAMES[new_phase]
    context.phase.started_at = now()

    # Mark feedback as required for phase
    context.feedback.pending_for_phase = True

    log("phase_changed", f"Transitioned to Phase {new_phase}")

    # Prompt for feedback
    show_prompt("Run /aid end to provide feedback before continuing")
    save_context()
```

---

## Standard Step Templates by Phase

### Phase 4: Component Development

```json
{
  "steps": [
    { "name": "Load task context", "order": 1 },
    { "name": "Read Tech Spec section", "order": 2 },
    { "name": "Write tests (TDD)", "order": 3 },
    { "name": "Implement component", "order": 4 },
    { "name": "Run tests / fix", "order": 5 },
    { "name": "Apply styling", "order": 6 },
    { "name": "Self code review", "order": 7 },
    { "name": "Update Jira", "order": 8 },
    { "name": "Commit", "order": 9 }
  ]
}
```

### Phase 4: Bug Fix

```json
{
  "steps": [
    { "name": "Load task context", "order": 1 },
    { "name": "Reproduce issue", "order": 2 },
    { "name": "Write failing test", "order": 3 },
    { "name": "Implement fix", "order": 4 },
    { "name": "Verify fix", "order": 5 },
    { "name": "Update Jira", "order": 6 },
    { "name": "Commit", "order": 7 }
  ]
}
```

### Phase 5: QA Task

```json
{
  "steps": [
    { "name": "Load task context", "order": 1 },
    { "name": "Run test suite", "order": 2 },
    { "name": "Check coverage", "order": 3 },
    { "name": "Review checklist", "order": 4 },
    { "name": "Document findings", "order": 5 },
    { "name": "Fix issues", "order": 6 },
    { "name": "Final verification", "order": 7 }
  ]
}
```

### Phase 1-3: Document Creation

```json
{
  "steps": [
    { "name": "Load context", "order": 1 },
    { "name": "Research/gather info", "order": 2 },
    { "name": "Draft document", "order": 3 },
    { "name": "Review/refine", "order": 4 },
    { "name": "Save to docs folder", "order": 5 },
    { "name": "Update context", "order": 6 }
  ]
}
```

---

## Session Log Actions

| Action | When | Details |
|--------|------|---------|
| `session_started` | /good-morning or first interaction | Session ID, loaded context |
| `task_started` | Beginning new Jira task | Task key, title |
| `task_completed` | Finishing Jira task | Task key, duration |
| `step_started` | Beginning step within task | Step name |
| `step_completed` | Finishing step | Notes, duration |
| `progress_update` | Significant progress milestone | Percentage, notes |
| `blocker_noted` | Hit a blocker | Description |
| `phase_changed` | Phase transition | From/to phase |
| `feedback_collected` | /aid end completed | Rating |
| `context_saved` | Manual context save | Reason |
| `session_ended` | End of work session | Summary |

---

## Integration with Commands

| Command | Context Action |
|---------|----------------|
| `/good-morning` | Read context, display status, prompt continuation |
| `/context` | Display current context state |
| `/context update` | Manual context update |
| `/phase` | Sync phase between context and state |
| `/aid end` | Update feedback tracking, save context |
| `/aid improve` | Reset feedback counters |

---

## Jira MCP Integration

When Jira MCP is connected, context syncs automatically:

```
┌─────────────────────────────────────────────────────────────────┐
│  JIRA-CONTEXT SYNC                                              │
│                                                                 │
│  On task_started:                                               │
│    - Fetch task details from Jira                               │
│    - Update context.tasks.current with Jira data                │
│    - Fetch next task from sprint backlog                        │
│                                                                 │
│  On task_completed:                                             │
│    - Update Jira status to "Done"                               │
│    - Log time if duration tracked                               │
│    - Fetch next task for context.tasks.next                     │
│                                                                 │
│  On session_started:                                            │
│    - Verify context.tasks.current matches Jira status           │
│    - Sync any offline changes                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Error Handling

### No context.json exists

```
⚠️ No .aid/context.json found

Setting up context tracking:
1. What feature are you working on?
2. What phase are you in? (Check /phase)
3. What task are you on? (Jira key or description)

[Creates context from answers]
```

### Context is stale (>24h old)

```
⚠️ Context is stale (last updated 36 hours ago)

Last state:
- Task: PROJ-124 "Create AuthService"
- Step: Implement service (60%)

Is this still accurate?
  [1] Yes, continue from here
  [2] No, I completed some work offline
  [3] Start fresh with new task
```

### Context-State mismatch

```
⚠️ Context-State mismatch detected

Context shows: Phase 3 (Implementation Plan)
State shows:  Phase 4 (Development)

Syncing to Phase 4...
[Updates context.phase]

Note: You may need to update your current task steps.
```

### Next task is null

```
⚠️ No next task defined

Options:
  [1] Fetch from Jira sprint backlog
  [2] Enter task key manually
  [3] Skip (will prompt when needed)
```

---

## File Locations

```
.aid/
├── state.json        # Phase-level state (phase-enforcement)
├── context.json      # Task/step-level context (THIS SKILL)
├── approvals/        # Phase approval records
└── overrides.log     # Phase override log

~/.aid/
├── feedback/
│   ├── pending/      # Unprocessed feedback
│   └── processed/    # Archived feedback
└── metrics/
    └── trends.json   # Aggregated metrics
```

---

## Skill Integration

Context tracking coordinates with other skills:

| Skill | Integration |
|-------|-------------|
| `phase-enforcement` | Sync phase, enforce gates |
| `system-architect` | Track Tech Spec document path |
| `atomic-design` | Track component implementation steps |
| `code-review` | Log review step completion |
| `test-driven` | Track TDD cycle steps |

---

## Commands Reference

| Command | Purpose |
|---------|---------|
| `/context` | Show current context |
| `/context tasks` | Show task progression only |
| `/context steps` | Show current task steps only |
| `/context log` | Show session log |
| `/context update` | Manual context update |
| `/good-morning` | Full startup routine with context |

---

## References

See `references/` folder:
- `context-schema.md` - Full JSON schema with validation
- `step-templates.md` - Step templates for all task types
- `session-management.md` - Session tracking and recovery
