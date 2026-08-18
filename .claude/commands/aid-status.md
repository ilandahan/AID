# /aid status

Show current memory system state.

## Purpose

Display current session info, pending feedback count, and system status.

## Output

```
AID Memory System Status
========================

Current Session:
  Role: Developer
  Phase: Development
  Started: 2h 15m ago
  Status: Active

Feedback:
  Pending: 3 items
  Processed: 12 items (all time)
  Last feedback: 2 days ago

Improvements:
  Last run: 5 days ago
  Skills updated: 4 (all time)
  Memory entries: 23/38 slots used

Skills Loaded:
  - developer/SKILL.md (updated 3 days ago)
  - development/SKILL.md (updated 1 week ago)

Recommendations:
  ⚠️ 3 pending feedback items - consider running /aid improve
```

## If No Active Session

```
AID Memory System Status
========================

Current Session: None

Last Session:
  Role: QA
  Phase: QA & Ship
  Ended: Yesterday at 5:30 PM

Feedback:
  Pending: 2 items
  
Use /aid start to begin a new session.
```

## If Not Initialized

```
AID Memory System Status
========================

❌ System not initialized

Run /aid init to set up the memory system.
```

## Usage

```
/aid status
```

## Notes

- Quick way to check system health
- Shows recommendations for next actions
- See `memory-system/docs/COMMANDS.md#status` for details
