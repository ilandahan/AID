---
name: context-tracking
description: Real-time work context tracking for session continuity. Maintains task/step state across sessions, tracks progress, manages logs, integrates with phase enforcement.
---

# Context Tracking Skill

Maintain real-time work context in `.aid/context.json`.

## Core Rule

Claude MUST maintain context:
1. READ context before starting work
2. UPDATE on every significant change
3. SYNC with phase state
4. INTEGRATE with feedback (/aid end)
5. SAVE at conversation end

## Context Update Triggers

| Moment | Action |
|--------|--------|
| Session start | Read context |
| New task | Shift tasks, reset steps |
| New step | Shift steps, log |
| Step complete | Mark done, notes |
| Task complete | Shift tasks, prompt feedback |
| Phase change | Sync state |
| End conversation | Final save |

## Context Structure

```json
{
  "last_updated": "2024-12-11T15:30:00Z",
  "session_id": "2024-12-11-afternoon",
  "phase": {
    "current": 4,
    "name": "development"
  },
  "project": {
    "name": "user-auth",
    "documents": {
      "prd": "docs/prd/...",
      "tech_spec": "docs/tech-spec/...",
      "implementation_plan": "docs/implementation-plan/..."
    }
  },
  "tasks": {
    "previous": { "key": "PROJ-123", "status": "done" },
    "current": { "key": "PROJ-124", "status": "in_progress" },
    "next": { "key": "PROJ-125", "status": "todo" }
  },
  "current_task_steps": {
    "previous": { "name": "Write tests", "status": "done" },
    "current": { "name": "Implement", "status": "in_progress", "progress": "60%" },
    "next": { "name": "Integration tests", "status": "pending" }
  },
  "session_log": [
    { "timestamp": "...", "action": "task_started", "details": "..." }
  ],
  "feedback": {
    "pending_for_phase": false,
    "sessions_since_feedback": 2
  }
}
```

## Phase-Aware Context

| Phase | Task Types | Step Templates |
|-------|------------|----------------|
| 1 PRD | Requirements | User stories, acceptance |
| 2 Tech Spec | Architecture | Design, API, security |
| 3 Impl Plan | Planning | Task breakdown |
| 4 Development | Coding | TDD cycle, impl |
| 5 QA | QA | Testing, deploy |

## Standard Step Templates

### Component Development (Phase 4)
1. Load task context
2. Read Tech Spec
3. Write tests (TDD)
4. Implement
5. Run tests
6. Self review
7. Commit

### Bug Fix (Phase 4)
1. Load context
2. Reproduce issue
3. Write failing test
4. Implement fix
5. Verify
6. Commit

## Session Log Actions

| Action | When |
|--------|------|
| session_started | First interaction |
| task_started | New task |
| task_completed | Task done |
| step_started | New step |
| step_completed | Step done |
| progress_update | Milestone |
| phase_changed | Transition |
| feedback_collected | /aid end |

## Feedback Integration

```
Task Complete?
  -> Update Context
  -> Phase ending? Prompt /aid end
  -> 3+ sessions without feedback? Remind
  -> Continue to next task
```

## Error Handling

### No context.json
```
No .aid/context.json found
Creating context:
1. What feature?
2. What phase?
3. What task?
```

### Stale context (>24h)
```
Context stale (36h old)
Last: PROJ-124 "AuthService" (60%)
Still accurate?
[1] Yes, continue
[2] No, completed offline
[3] Start fresh
```

### Context-State mismatch
```
Context: Phase 3
State: Phase 4
Syncing to Phase 4...
```

## File Locations

```
.aid/
  state.json     # Phase state
  context.json   # Task/step context

~/.aid/
  feedback/pending/
  feedback/processed/
```

## Commands

| Command | Purpose |
|---------|---------|
| /context | Show current |
| /context tasks | Task progression |
| /context steps | Current steps |
| /context log | Session log |
| /context update | Manual update |
| /good-morning | Full startup |
