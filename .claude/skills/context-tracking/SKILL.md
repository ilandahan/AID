---
name: context-tracking
description: Real-time work context tracking for seamless session continuity. Use this skill to maintain task/step state across sessions, track progress on current work, manage session logs, and integrate with phase enforcement. Essential for multi-session projects and team handoffs.
---

# Context Tracking Skill

Maintain real-time work context in `.aid/context.json` for seamless session continuity, integrated with phase enforcement and quality feedback systems.

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
    }
  ],

  "feedback": {
    "pending_for_phase": false,
    "last_feedback_at": "2024-12-10T18:00:00Z",
    "sessions_since_feedback": 2
  }
}
```

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

### Feedback Reminders

| Condition | Reminder |
|-----------|----------|
| Phase ending | "Run /aid end before advancing to next phase" |
| 3+ sessions without feedback | "Consider /aid end to share what worked" |
| 5+ tasks completed | "Good time for /aid end checkpoint" |

## Integration with Commands

| Command | Context Action |
|---------|----------------|
| `/good-morning` | Read context, display status, prompt continuation |
| `/context` | Display current context state |
| `/context update` | Manual context update |
| `/phase` | Sync phase between context and state |
| `/aid end` | Update feedback tracking, save context |
| `/aid improve` | Reset feedback counters |

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

## Commands Reference

| Command | Purpose |
|---------|---------|
| `/context` | Show current context |
| `/context tasks` | Show task progression only |
| `/context steps` | Show current task steps only |
| `/context log` | Show session log |
| `/context update` | Manual context update |
| `/good-morning` | Full startup routine with context |
