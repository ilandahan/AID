---
name: context-tracking
description: Real-time work context tracking for session continuity. Maintains task/step state across sessions, tracks progress, manages logs, integrates with phase enforcement.
---

# Context Tracking

Applies: every session, whenever work starts, a step/task changes, phase changes, or a conversation ends. Maintain `.aid/context.json`.

## Core Rule

1. READ context before starting work
2. UPDATE on every significant change
3. READ phase state from `.aid/state.json` (read-only: only `aid_session.py` writes it)
4. INTEGRATE with feedback (`/aid-end`)
5. SAVE at conversation end

## Update Triggers

| Moment | Action |
|---|---|
| Session start | Read context |
| New task | Update current_task, reset current_step and progress |
| New step | Update current_step, add session note |
| Step complete | Move step to steps_completed, update current_step |
| Task complete | Clear current_task, prompt feedback |
| Phase change | Re-read phase from state.json (never write it) |
| End conversation | Final save with timestamp |

## Context Structure

The one schema, `aid-context-v1` (field types, writers and readers:
`references/context-schema.md`):

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

## Phase-Aware Context

| Phase | Task Types | Step Templates |
|---|---|---|
| 1 PRD | Requirements | User stories, acceptance |
| 2 Tech Spec | Architecture | Design, API, security |
| 3 Impl Plan | Planning | Task breakdown |
| 4 Development | Coding | TDD cycle, impl |
| 5 QA | QA | Testing, deploy |

## Standard Step Templates

More templates: `references/step-templates.md`.

Component Development (Phase 4)
1. Load task context
2. Read Tech Spec
3. Write tests (TDD)
4. Implement
5. Run tests
6. Self review
7. Commit

Bug Fix (Phase 4)
1. Load context
2. Reproduce issue
3. Write failing test
4. Implement fix
5. Verify
6. Commit

## Session Notes

Append to `session_notes` at these moments:

| When | Note Content |
|---|---|
| Session start | "Session started - resuming [task title]" |
| Task started | "Started task: [key] - [title]" |
| Task completed | "Completed task: [key]" |
| Step completed | "Completed step: [step name]" |
| Progress milestone | "Progress: [description of milestone]" |
| Phase changed | "Phase transition: [old] -> [new]" |
| Blocker added/resolved | "Blocker [added/resolved]: [description]" |

## Blocker Management

Track blockers in the `blockers` array as `{"description": <text>, "severity": "low"|"medium"|"high"}` objects. Remove a blocker from the array when resolved and add a session note documenting the resolution.

## Error Handling

No context.json:
```
No .aid/context.json found
Creating context:
1. What feature?
2. What phase?
3. What task?
```

Stale context (>24h):
```
Context stale (36h old)
Last: PROJ-124 "AuthService" (60%)
Still accurate?
[1] Yes, continue
[2] No, completed offline
[3] Start fresh
```

Phase: `context.json` holds no phase. Always read the phase from `.aid/state.json`.

## File Locations

```
.aid/
  state.json     # Phase state
  context.json   # Task/step context

~/.aid/
  feedback/pending/
  feedback/processed/
```

Session lifecycle detail: `references/session-management.md`.

## Commands

| Command | Purpose |
|---|---|
| /context | Show current |
| /context tasks | Task progression |
| /context steps | Current steps |
| /context log | Session log |
| /context update | Manual update |
| /good-morning | Full startup |
