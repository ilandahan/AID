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
│  3. READ phase state (.aid/state.json, read-only)               │
│  4. INTEGRATE with feedback system (/aid-end)                   │
│  5. SAVE context at conversation end                            │
└─────────────────────────────────────────────────────────────────┘
```

## Context Update Triggers

| Moment | Action | Updates |
|--------|--------|---------|
| Session start | Read context | Load current task and step |
| Starting new task | Set `current_task` | Reset `current_step` and `progress`, log entry |
| Starting new step | Set `current_step` | Add to session log |
| Completing step | Move to `steps_completed` | Note, timestamp |
| Completing task | Clear `current_task` | Prompt feedback |
| Progress milestone | Add a session note | Timestamp |
| Phase change | Re-read `.aid/state.json` | Nothing in context.json (it holds no phase) |
| End of conversation | Final save | All pending changes |

## Context Structure

### `.aid/context.json`

The one schema, `aid-context-v1`; field types, writers and readers are in
`references/context-schema.md`. `session_id` and `session_log` are optional extra keys.

```json
{
  "$schema": "aid-context-v1",
  "version": "1.0",
  "last_updated": "2026-11-20T15:30:00Z",
  "session_id": "2026-11-20-afternoon",
  "current_task": {"id": "PROJ-124", "title": "Create AuthService", "jira_key": "PROJ-124"},
  "current_step": "Implement service",
  "progress": {"steps_completed": ["Write unit tests"], "steps_pending": ["Integration tests"]},
  "session_notes": ["Login and logout done, token refresh next"],
  "blockers": [],
  "session_log": [
    {"timestamp": "2026-11-20T14:15:00Z", "action": "task_started", "details": "Started PROJ-124: Create AuthService"},
    {"timestamp": "2026-11-20T15:00:00Z", "action": "step_completed", "details": "Unit tests complete: 8 tests passing"}
  ]
}
```

## PRIORITY 2: Phase Integration

`context.json` holds no phase. The phase, the phase documents and the feedback record live in
`.aid/state.json`, which only `aid_session.py` writes. Read it whenever the phase matters;
never copy it into `context.json`.

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

### Phase 1-3: Research, PRD & Document Creation

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
| `feedback_collected` | /aid-end completed | Rating |
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
│       ├── Yes ──▶ Prompt: "/aid-end for phase feedback"         │
│       │                                                         │
│       ▼                                                         │
│  Check: Sessions since feedback >= 3?                           │
│       │                                                         │
│       ├── Yes ──▶ Remind: "Consider /aid-end for feedback"      │
│       │                                                         │
│       ▼                                                         │
│  Continue to next task                                          │
└─────────────────────────────────────────────────────────────────┘
```

### Feedback Reminders

| Condition | Reminder |
|-----------|----------|
| Phase ending | "Run /aid-end before advancing to next phase" |
| 3+ sessions without feedback | "Consider /aid-end to share what worked" |
| 5+ tasks completed | "Good time for /aid-end checkpoint" |

## Integration with Commands

| Command | Context Action |
|---------|----------------|
| `/good-morning` | Read context, display status, prompt continuation |
| `/context` | Display current context state |
| `/context update` | Manual context update |
| `/phase` | Read the phase from state.json (context.json holds no phase) |
| `/aid-end` | Update feedback tracking, save context |
| `/aid-improve` | Reset feedback counters |

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
- Step: Implement service

Is this still accurate?
  [1] Yes, continue from here
  [2] No, I completed some work offline
  [3] Start fresh with new task
```

### Phase

`context.json` holds no phase, so it cannot disagree with `.aid/state.json`. After a phase
change, check that `current_task` and `current_step` still fit the new phase.

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

## PRIORITY 4: Development Interaction Tracking

During Phase 4 (Development), track significant interactions to trigger periodic quality checks.

### What Counts as an Interaction

```
┌─────────────────────────────────────────────────────────────────┐
│  INTERACTION COUNTER INCREMENTS WHEN:                           │
│                                                                 │
│  ✓ Component/function implementation completed                  │
│  ✓ Test file written and saved                                  │
│  ✓ git commit executed                                          │
│  ✓ Code review checklist completed                              │
│  ✓ Bug fix verified                                             │
│                                                                 │
│  DOES NOT INCREMENT FOR:                                        │
│  ✗ Questions and discussions                                    │
│  ✗ File reads without changes                                   │
│  ✗ Context lookups                                              │
│  ✗ Planning/thinking                                            │
└─────────────────────────────────────────────────────────────────┘
```

### Quality Check Flow

```
┌─────────────────────────────────────────────────────────────────┐
│  DEVELOPMENT QUALITY CHECK FLOW                                 │
│                                                                 │
│  Interaction happens                                            │
│       │                                                         │
│       ▼                                                         │
│  Is Phase 4 (Development)?                                      │
│       │                                                         │
│       ├── No ──▶ Skip                                           │
│       │                                                         │
│       ▼                                                         │
│  Increment the interaction count (kept in the conversation)     │
│       │                                                         │
│       ▼                                                         │
│  interaction_count >= quality_check_threshold?                  │
│       │                                                         │
│       ├── No ──▶ Continue working                               │
│       │                                                         │
│       ▼                                                         │
│  Trigger Quality Check Prompt                                   │
│       │                                                         │
│       ▼                                                         │
│  User rates (1-5) or skips                                      │
│       │                                                         │
│       ▼                                                         │
│  If rated: keep it for the next /aid-end (aid_session.py end    │
│  is the only writer; never write feedback/pending/ by hand)     │
│  Reset interaction_count to 0                                   │
│  Update last_quality_check timestamp                            │
│  Continue working                                               │
└─────────────────────────────────────────────────────────────────┘
```

### Quality Check Prompt

When threshold reached, Claude displays:

```
═══════════════════════════════════════════════════════════════════
📊 QUICK QUALITY CHECK

You've completed ~{count} significant interactions. Quick checkpoint:

How's the session going? (1-5 or 'skip')
  1 = Struggling   2 = Below avg   3 = On track   4 = Good   5 = Great

Your rating (or 'skip'): ___

Brief note (optional): ___
═══════════════════════════════════════════════════════════════════
```

### Configuration

Default threshold: 10 interactions
Can be overridden in `~/.aid/config.yaml`:

```yaml
development:
  quality_check_interval: 10
  quality_check_enabled: true
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
