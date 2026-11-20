# Context Schema Reference: `aid-context-v1`

This is the ONE schema for `.aid/context.json` (T17, F6). Every other AID document links
here instead of restating a different shape. The phase lives in `.aid/state.json`, never in
`context.json`.

---

## The document

```json
{
  "$schema": "aid-context-v1",
  "version": "1.0",
  "last_updated": "2026-11-20T10:00:00Z",
  "current_task": {"id": "PROJ-123", "title": "Add login form", "jira_key": "PROJ-123"},
  "current_step": "Implement validation",
  "progress": {"steps_completed": ["Design form"], "steps_pending": ["Write tests"]},
  "session_notes": ["Decided to reuse the auth hook"],
  "blockers": [{"description": "Waiting for API keys", "severity": "medium"}]
}
```

---

## Field types

| Field | Type |
|-------|------|
| `$schema` | the string `"aid-context-v1"` |
| `version` | the string `"1.0"` |
| `last_updated` | ISO 8601 timestamp string |
| `current_task` | `null`, or an object with `id` (string matching `^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$`, no `..`), `title` (string) and optionally `jira_key` (string) |
| `current_step` | `null`, or a string (the step name) |
| `progress` | an object with two string arrays: `steps_completed` and `steps_pending` |
| `session_notes` | an array of strings |
| `blockers` | an array of objects `{"description": <string>, "severity": "low" \| "medium" \| "high"}` |

- Writers may keep extra top-level keys, such as `session_id` (for example
  `"2026-11-20-morning"`) and `session_log` (an array of `{timestamp, action, details}`
  objects). Readers ignore keys they do not know.
- Not part of the schema: a step inside `current_task`, a number as `progress`, `key` as the
  task id field, and the older `tasks` / `current_task_steps` / `phase` chain.

---

## Writers

| Writer | What it writes |
|--------|----------------|
| `aid_session.py init` (run by `/aid-init`, `/aid-start`, `/setup`) | Creates the file once, exactly this document with `current_task` and `current_step` set to `null` and empty arrays. It never overwrites an existing file. |
| `/context-update` | Changes only the fields it owns: `current_task`, `current_step`, `progress`, `session_notes`, `blockers`, `last_updated`. |
| `/good-morning` | Changes only `last_updated`, `session_id` and `session_log`, and writes blockers only as `{description, severity}` objects. |

---

## Readers (tolerant)

AID's SessionStart and UserPromptSubmit hooks read the file field by field and never fail on
it:

- the task id is `id`, else `key`, else `jira_key`;
- `current_step` is a string, or the `name` of an object;
- each blocker is an object (`severity`, `description`) or a string (shown as `[?]`);
- a field of any other type is skipped;
- a file that is not a JSON object, invalid JSON, or a file with a UTF-8 BOM gives no
  context lines, and never an error. The AID rules block is always shown.

---

## Optional `session_log` entries (extra key)

`/good-morning` and `/context-update` may append to the optional top-level `session_log`
array. Each entry is `{"timestamp": <ISO 8601>, "action": <string>, "details": <string>}`,
with an optional `metadata` object. Typical actions: `session_started`, `step_completed`,
`blocker_noted`, `context_saved`.

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

## Older shapes

Files written before T17 may hold a `tasks` / `current_task_steps` / `phase` chain, a step
inside `current_task`, or a number as `progress`. The readers skip those fields; they never
fail. `/context-update` rewrites the fields it owns in this shape the next time it runs.
