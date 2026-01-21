# Session Management Reference

Session tracking, recovery, and continuity patterns.

---

## Overview

```
┌─────────────────────────────────────────────────────────────────┐
│  SESSION LIFECYCLE                                              │
│                                                                 │
│  /good-morning ──▶ Work Session ──▶ /aid end                    │
│       │                │                │                       │
│       ▼                ▼                ▼                       │
│    Load             Update            Save                      │
│   Context          Context          Feedback                    │
│                                                                 │
│  Session ID: 2024-12-11-morning                                 │
│  Period: morning | afternoon | evening | night                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Session ID Format

```
YYYY-MM-DD-period

Periods:
- morning:   06:00 - 12:00
- afternoon: 12:00 - 17:00
- evening:   17:00 - 21:00
- night:     21:00 - 06:00
```

### Session ID Generation

```javascript
function generateSessionId() {
  const now = new Date();
  const date = now.toISOString().split('T')[0];
  const hour = now.getHours();

  let period;
  if (hour >= 6 && hour < 12) period = 'morning';
  else if (hour >= 12 && hour < 17) period = 'afternoon';
  else if (hour >= 17 && hour < 21) period = 'evening';
  else period = 'night';

  return `${date}-${period}`;
}
```

---

## Session Start Flow

### /good-morning Command

```
┌──────────────────────────────────────────────────────────────┐
│                  SESSION START FLOW                          │
│                                                              │
│  1. Check Infrastructure                                     │
│     ├── Docker status                                        │
│     ├── MCP connections (Jira, Figma, GitHub)                │
│     └── Database connectivity                                │
│                                                              │
│  2. Load Context                                             │
│     ├── Read .aid/context.json                               │
│     ├── Sync with .aid/state.json                            │
│     └── Check staleness                                      │
│                                                              │
│  3. Display Status                                           │
│     ├── Project phase                                        │
│     ├── Current task and step                                │
│     └── Last activity timestamp                              │
│                                                              │
│  4. Prompt Continuation                                      │
│     ├── Continue current step                                │
│     ├── Move to next step/task                               │
│     └── Update context (offline work)                        │
└──────────────────────────────────────────────────────────────┘
```

### Session Start Code

```python
def start_session():
    session_id = generate_session_id()

    # Load context
    context = load_context_or_create()
    context.session_id = session_id

    # Sync with phase state
    state = load_state()
    if context.phase.current != state.current_phase:
        context.phase.current = state.current_phase
        context.phase.name = PHASE_NAMES[state.current_phase]

    # Check staleness
    hours_stale = hours_since(context.last_updated)
    if hours_stale > 24:
        prompt_stale_context_recovery()

    # Log session start
    context.session_log.append({
        "timestamp": now(),
        "action": "session_started",
        "details": f"Session {session_id}, task: {context.tasks.current.key}"
    })

    save_context(context)
    display_context(context)

    return context
```

---

## Session Continuity

### Context Recovery Options

When context is stale (>24h) or missing:

```
⚠️ Context Recovery Needed

Last updated: 36 hours ago
Last state: PROJ-124 "Create AuthService" - Implement (60%)

Options:
  [1] Continue from here (context is accurate)
  [2] I completed some work offline
  [3] Start fresh with different task
  [4] Sync from Jira (if connected)

> _
```

### Offline Work Update

```
You selected: I completed some work offline

What did you do?
  [1] Completed current step
  [2] Completed current task
  [3] Completed multiple tasks
  [4] Worked on different task
  [5] Custom update

> 2

Updating context:
- PROJ-124 → DONE
- Moving to: PROJ-125 "Create SessionManager"

Any notes about the completed work?
> Finished auth service, all tests passing

Context updated.
```

---

## Session Activity Tracking

### Automatic Logging

Events automatically logged to `session_log`:

| Event | Trigger | Log Entry |
|-------|---------|-----------|
| Session start | /good-morning | `session_started` |
| Task started | Starting new Jira task | `task_started` |
| Step started | Moving to next step | `step_started` |
| Progress update | Significant milestone | `progress_update` |
| Step completed | Finishing a step | `step_completed` |
| Task completed | Finishing a task | `task_completed` |
| Blocker noted | Encountering blocker | `blocker_noted` |
| Phase changed | Phase transition | `phase_changed` |
| Session ended | /aid end | `session_ended` |

### Log Size Management

```javascript
const MAX_LOG_ENTRIES = 50;

function trimSessionLog(log) {
  if (log.length > MAX_LOG_ENTRIES) {
    // Keep recent entries, archive old ones
    const archived = log.slice(0, log.length - MAX_LOG_ENTRIES);
    const kept = log.slice(-MAX_LOG_ENTRIES);

    saveArchivedLog(archived);
    return kept;
  }
  return log;
}
```

---

## Session End Flow

### /aid end Command

```
┌──────────────────────────────────────────────────────────────┐
│                   SESSION END FLOW                           │
│                                                              │
│  1. Summarize Work                                           │
│     ├── Tasks completed                                      │
│     ├── Steps completed                                      │
│     └── Time spent                                           │
│                                                              │
│  2. Collect Feedback                                         │
│     ├── Rating (1-5)                                         │
│     ├── What worked well                                     │
│     └── What to improve                                      │
│                                                              │
│  3. Save Context                                             │
│     ├── Update context.json                                  │
│     ├── Save feedback to ~/.aid/feedback/pending/            │
│     └── Log session_ended                                    │
│                                                              │
│  4. Prompt Next                                              │
│     ├── Continue to next phase                               │
│     ├── Start new session                                    │
│     └── End for now                                          │
└──────────────────────────────────────────────────────────────┘
```

### Session End Code

```python
def end_session(rating, worked_well, to_improve):
    # Calculate duration
    session_start = find_session_start_log()
    duration_minutes = minutes_since(session_start.timestamp)

    # Save feedback
    feedback = {
        "timestamp": now(),
        "session_id": context.session_id,
        "phase": context.phase.current,
        "phase_name": context.phase.name,
        "rating": rating,
        "worked_well": worked_well,
        "to_improve": to_improve,
        "duration_minutes": duration_minutes,
        "tasks_completed": count_completed_tasks()
    }
    save_feedback(feedback)

    # Update context feedback tracking
    context.feedback.last_feedback_at = now()
    context.feedback.sessions_since_feedback = 0
    context.feedback.tasks_completed_since_feedback = 0
    context.feedback.pending_for_phase = False

    # Log session end
    context.session_log.append({
        "timestamp": now(),
        "action": "session_ended",
        "details": f"Duration: {duration_minutes}m, Rating: {rating}"
    })

    save_context(context)
```

---

## Session Interruption Recovery

### Unexpected Session End

If session ends without /aid end (crash, timeout, etc.):

```
┌──────────────────────────────────────────────────────────────┐
│  NEXT SESSION RECOVERY                                       │
│                                                              │
│  Detected: Previous session ended unexpectedly               │
│                                                              │
│  Last saved state:                                           │
│  - Task: PROJ-124 (in_progress)                              │
│  - Step: Implement component (60%)                           │
│  - Time: 16:45 (2 hours ago)                                 │
│                                                              │
│  Would you like to:                                          │
│  [1] Resume from saved state                                 │
│  [2] Provide feedback for previous session                   │
│  [3] Start fresh                                             │
└──────────────────────────────────────────────────────────────┘
```

### Recovery Logic

```javascript
function checkSessionRecovery() {
  const context = loadContext();
  const lastLog = context.session_log[context.session_log.length - 1];

  // Check if last session ended properly
  if (lastLog && lastLog.action !== 'session_ended') {
    const lastSessionStart = findLastSessionStart(context.session_log);

    if (lastSessionStart && differentSession(lastSessionStart.timestamp, now())) {
      return {
        needsRecovery: true,
        lastSession: {
          id: context.session_id,
          task: context.tasks.current,
          step: context.current_task_steps.current,
          lastActivity: context.last_updated
        }
      };
    }
  }

  return { needsRecovery: false };
}
```

---

## Multi-Session Tracking

### Session History

Track across sessions for patterns:

```json
{
  "session_history": [
    {
      "session_id": "2024-12-11-morning",
      "duration_minutes": 180,
      "tasks_completed": 2,
      "rating": 4
    },
    {
      "session_id": "2024-12-11-afternoon",
      "duration_minutes": 120,
      "tasks_completed": 1,
      "rating": 3
    }
  ]
}
```

### Session Metrics

```javascript
function calculateSessionMetrics(history) {
  return {
    total_sessions: history.length,
    avg_duration: average(history.map(s => s.duration_minutes)),
    avg_tasks_per_session: average(history.map(s => s.tasks_completed)),
    avg_rating: average(history.map(s => s.rating)),
    most_productive_period: findMostProductivePeriod(history)
  };
}
```

---

## Session Commands

| Command | Description |
|---------|-------------|
| `/good-morning` | Start new session with full context load |
| `/context` | Show current session state |
| `/aid end` | End session with feedback |
| `/session log` | Show session log entries |
| `/session history` | Show recent session history |

---

## Best Practices

### Session Start
1. Always run `/good-morning` at start of work
2. Verify context is accurate before proceeding
3. Update context if offline work was done

### During Session
1. Let context update automatically via operations
2. Use `/context` to verify state if unsure
3. Note blockers with `blocker_noted` entries

### Session End
1. Always run `/aid end` before stopping work
2. Provide honest feedback (helps improve methodology)
3. Note what worked and what didn't

### Recovery
1. Check recovery prompts carefully
2. Provide feedback even for interrupted sessions
3. Keep context accurate for future sessions
