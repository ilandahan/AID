# Morning Startup Routine

The `/good-morning` command runs a daily startup sequence to load context, check systems, and resume work.

## What It Does

1. **Load context** — Read `.aid/context.json` to understand current task and progress
2. **Check phase** — Read `.aid/state.json` to verify current phase
3. **Check pipeline** — If `.aid/pipeline/state.json` exists with `running` status, offer to resume
4. **Check blockers** — Display any open blockers from context
5. **Show status** — Display a summary of where work left off
6. **Resume** — Offer to continue from the last step

## Usage

```
/good-morning
```

## Output

```
Good Morning! Loading context...

Project Phase: [X] - [Phase Name]
Current Task: [task_id] - [title]
Current Step: [step description]
Progress: [N] steps done, [M] remaining

Blockers: [none | list]
Pipeline: [not active | active at step X]

Ready to continue from: [last step]
Shall I proceed? (y/n)
```

## When to Use

- Start of every work session
- After a long break
- When switching between projects
- After context window compression (to reload state)

## Related Commands

- `/context` — Show context without the full startup sequence
- `/aid-status` — Show AID system status (role, phase, session)
- `/pipeline-status` — Check pipeline state specifically
