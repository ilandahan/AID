# Work Context Tracker

The AID context tracker maintains session continuity by tracking the current task, step, progress, and blockers in `.aid/context.json`.

## Purpose

When a session ends or context is lost, the tracker ensures work can resume seamlessly. Claude reads the context file at the start of every session to understand where work left off.

## Context File Location

`.aid/context.json` — automatically updated during work sessions.

## Schema

One schema, `aid-context-v1`, documented in one place:
[skills/context-tracking/references/context-schema.md](../skills/context-tracking/references/context-schema.md)
(the example, the field types, which command writes which field, and how the hooks read it).
In short: `current_task` is `null` or `{id, title, jira_key?}`, `current_step` is `null` or
a string, `progress` holds `steps_completed` and `steps_pending` string arrays,
`session_notes` is a string array, and `blockers` holds `{description, severity}` objects.

## When Context Updates

Claude updates `.aid/context.json` when:
- Starting a new task
- Completing a step
- Significant progress is made
- A blocker is identified or resolved
- Session ends

## Commands

| Command | Purpose |
|---------|---------|
| `/context` | Show current work context |
| `/context-update` | Manually update context |
| `/good-morning` | Load context and resume work |

## Related

- Skill: `.claude/skills/context-tracking/SKILL.md`
- State file: `.aid/state.json` (phase tracking, complements context)
