# Context Schema Reference

Full JSON schema for `.aid/context.json` with validation rules.

---

## Complete Schema

```typescript
interface AIDContext {
  // Metadata
  last_updated: string;      // ISO 8601 timestamp
  session_id: string;        // Format: YYYY-MM-DD-period

  // Phase Information (synced with state.json)
  phase: PhaseInfo;

  // Project Information
  project: ProjectInfo;

  // Task Tracking (previous → current → next)
  tasks: TaskChain;

  // Step Tracking within Current Task
  current_task_steps: StepChain;

  // Session Activity Log
  session_log: LogEntry[];

  // Feedback System Integration
  feedback: FeedbackStatus;
}
```

---

## Phase Information

```typescript
interface PhaseInfo {
  current: 1 | 2 | 3 | 4 | 5;
  name: 'prd' | 'tech-spec' | 'implementation-plan' | 'development' | 'qa-ship';
  started_at: string;        // ISO 8601 timestamp
}
```

### Phase Names Mapping

```javascript
const PHASE_NAMES = {
  1: 'prd',
  2: 'tech-spec',
  3: 'implementation-plan',
  4: 'development',
  5: 'qa-ship'
};
```

---

## Project Information

```typescript
interface ProjectInfo {
  name: string;              // Feature/project name (kebab-case)
  documents: {
    prd: string | null;              // docs/prd/YYYY-MM-DD-[name].md
    tech_spec: string | null;        // docs/tech-spec/YYYY-MM-DD-[name].md
    implementation_plan: string | null; // docs/implementation-plan/YYYY-MM-DD-[name].md
  };
}
```

### Document Path Validation

```javascript
const DOCUMENT_PATH_REGEX = /^docs\/(prd|tech-spec|implementation-plan)\/\d{4}-\d{2}-\d{2}-[\w-]+\.md$/;

function validateDocumentPath(path) {
  return DOCUMENT_PATH_REGEX.test(path);
}
```

---

## Task Chain

```typescript
interface TaskChain {
  previous: Task | null;
  current: Task | null;
  next: Task | null;
}

interface Task {
  key: string;               // Jira key: PROJ-123
  title: string;             // Task title
  status: 'todo' | 'in_progress' | 'done' | 'blocked';
  type?: 'feature' | 'bug' | 'task' | 'qa';
  started_at?: string;       // ISO 8601 timestamp
  completed_at?: string;     // ISO 8601 timestamp
  jira_url?: string;         // Full Jira URL
  notes?: string;            // Additional notes
}
```

### Task Status Transitions

```
todo ────► in_progress ────► done
              │
              ▼
           blocked ────► in_progress
```

---

## Step Chain

```typescript
interface StepChain {
  previous: Step | null;
  current: Step | null;
  next: Step | null;
}

interface Step {
  name: string;              // Step name
  status: 'pending' | 'in_progress' | 'done' | 'skipped';
  order?: number;            // Step order in template
  started_at?: string;       // ISO 8601 timestamp
  completed_at?: string;     // ISO 8601 timestamp
  progress?: string;         // e.g., "50%", "3/8 tests"
  notes?: string;            // Progress notes
}
```

### Step Status Transitions

```
pending ────► in_progress ────► done
                  │
                  ▼
               skipped
```

---

## Session Log

```typescript
interface LogEntry {
  timestamp: string;         // ISO 8601 timestamp
  action: LogAction;
  details: string;
  metadata?: Record<string, any>;
}

type LogAction =
  | 'session_started'
  | 'session_ended'
  | 'task_started'
  | 'task_completed'
  | 'step_started'
  | 'step_completed'
  | 'progress_update'
  | 'blocker_noted'
  | 'phase_changed'
  | 'feedback_collected'
  | 'context_saved';
```

### Log Entry Examples

```json
[
  {
    "timestamp": "2024-12-11T09:00:00Z",
    "action": "session_started",
    "details": "Morning session, loaded context for PROJ-124",
    "metadata": { "session_id": "2024-12-11-morning" }
  },
  {
    "timestamp": "2024-12-11T10:30:00Z",
    "action": "step_completed",
    "details": "Unit tests complete: 12 tests passing",
    "metadata": { "step": "Write tests (TDD)", "duration_minutes": 90 }
  },
  {
    "timestamp": "2024-12-11T12:00:00Z",
    "action": "blocker_noted",
    "details": "Waiting for API spec clarification from backend team"
  }
]
```

---

## Feedback Status

```typescript
interface FeedbackStatus {
  pending_for_phase: boolean;           // True if phase complete, feedback needed
  last_feedback_at: string | null;      // ISO 8601 timestamp
  sessions_since_feedback: number;      // Counter
  tasks_completed_since_feedback: number; // Counter
  reminder_shown: boolean;              // Prevent duplicate reminders
}
```

### Feedback Thresholds

```javascript
const FEEDBACK_THRESHOLDS = {
  sessions: 3,        // Remind after 3 sessions without feedback
  tasks: 5,           // Remind after 5 tasks completed
  phase_end: true     // Always require feedback at phase end
};
```

---

## Validation Functions

### Full Context Validation

```typescript
function validateContext(context: unknown): context is AIDContext {
  if (!context || typeof context !== 'object') return false;

  const ctx = context as AIDContext;

  // Required fields
  if (!ctx.last_updated || !isValidISODate(ctx.last_updated)) return false;
  if (!ctx.session_id || !isValidSessionId(ctx.session_id)) return false;

  // Phase validation
  if (!ctx.phase || !isValidPhase(ctx.phase)) return false;

  // Task chain validation
  if (!ctx.tasks) return false;

  // Step chain validation
  if (!ctx.current_task_steps) return false;

  // Log validation
  if (!Array.isArray(ctx.session_log)) return false;

  // Feedback validation
  if (!ctx.feedback) return false;

  return true;
}

function isValidISODate(str: string): boolean {
  const date = new Date(str);
  return !isNaN(date.getTime());
}

function isValidSessionId(str: string): boolean {
  return /^\d{4}-\d{2}-\d{2}-(morning|afternoon|evening|night)$/.test(str);
}

function isValidPhase(phase: PhaseInfo): boolean {
  return phase.current >= 1 && phase.current <= 5;
}
```

---

## Default Context Template

```json
{
  "last_updated": null,
  "session_id": null,

  "phase": {
    "current": 1,
    "name": "prd",
    "started_at": null
  },

  "project": {
    "name": null,
    "documents": {
      "prd": null,
      "tech_spec": null,
      "implementation_plan": null
    }
  },

  "tasks": {
    "previous": null,
    "current": null,
    "next": null
  },

  "current_task_steps": {
    "previous": null,
    "current": null,
    "next": null
  },

  "session_log": [],

  "feedback": {
    "pending_for_phase": false,
    "last_feedback_at": null,
    "sessions_since_feedback": 0,
    "tasks_completed_since_feedback": 0,
    "reminder_shown": false
  }
}
```

---

## Migration Notes

### From v1 (Simple Context)

Old format:
```json
{
  "tasks": { "previous": {}, "current": {}, "next": {} },
  "current_task_steps": { "previous": {}, "current": {}, "next": {} },
  "session_log": []
}
```

Migration adds:
- `phase` block (sync from state.json)
- `project` block (extract from current feature)
- `feedback` block (initialize with defaults)

### Migration Script

```javascript
function migrateContext(oldContext) {
  const state = readState('.aid/state.json');

  return {
    ...oldContext,
    phase: {
      current: state.current_phase || 1,
      name: PHASE_NAMES[state.current_phase || 1],
      started_at: state.started_at || new Date().toISOString()
    },
    project: {
      name: state.feature_name || 'unknown',
      documents: state.documents || { prd: null, tech_spec: null, implementation_plan: null }
    },
    feedback: {
      pending_for_phase: false,
      last_feedback_at: null,
      sessions_since_feedback: 0,
      tasks_completed_since_feedback: 0,
      reminder_shown: false
    }
  };
}
```
