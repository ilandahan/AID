---
description: "Show current AID state: phase plus session info"
---

# /aid-status

Show current AID state: the project phase, the session and the memory system.

## Purpose

Display current session info, pending feedback count, and system status.

## Data source (ONE Bash call)

Read every value from AID's status command. Do not guess from files, and do not read
`~/.aid/` or `.aid/` by hand to fill the fields in:

```bash
python "${CLAUDE_PLUGIN_ROOT}/hooks/aid_session.py" status --format json
```

- Run it exactly in this shape: one simple command, lowercase `python`, single spaces, no
  `;`, `&&`, pipes, redirects, `$( )` or loops. `status` is read-only (it writes nothing),
  so Claude Code does not ask for it.
- It prints one JSON document with these fields:

  | Field | Holds |
  |-------|-------|
  | `project` | `root`, `initialized`, `phase`, `phase_name` (and `problem` when the state file is unreadable); `null` outside an AID project |
  | `session` | `role`, `role_display`, `phase_display`, `started`, `active`, `status`; `null` when there is no project state |
  | `feedback` | `pending`, `processed`, `newest_pending` (timestamp of the newest pending item, or `null`) |
  | `improvement` | the stats from `$AID_HOME/metrics/improvement.json`: `last_improvement_run`, `runs`, `feedback_processed`, `skills_updated` |
  | `memory` | `used`, `total`: memory slots used and the slot total from the memory system's slot allocation (an empty memory shows `0/30`); `null` when the memory system is not found |
  | `recommendations` | `queued`: the recommendations queue length; `null` when unavailable |

- Show those fields in the layout below. A field the command does not return (or returns as
  `null`) is shown as `unknown`, never estimated. `Last run` is
  `improvement.last_improvement_run` and `Skills updated` is `improvement.skills_updated`;
  `Memory entries` is `memory.used`/`memory.total`, both read from the output, never a
  number written in this file.
- If `${CLAUDE_PLUGIN_ROOT}` was not replaced by a real path, this is not a plugin install:
  AID's phase commands need the plugin (`claude plugin install aid@AID`). Do not substitute
  another path.

## Output

```
AID Memory System Status
========================

Project: /path/to/project (Phase 4)

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
  Memory entries: <memory.used>/<memory.total> slots used

Recommendations:
  Queue: 2 proposals (see /aid-recommendations)
  ⚠️ 3 pending feedback items - consider running /aid-improve
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
  
Use /aid-start to begin a new session.
```

## If Not Initialized

```
AID Memory System Status
========================

❌ System not initialized

Run /aid-init to set up the project and the memory system.
```

## Usage

```
/aid-status
```

## Notes

- Quick way to check system health
- Shows recommendations for next actions
- Every value comes from `aid_session.py status`; nothing is guessed
- See [`memory-system/docs/COMMANDS.md`](../memory-system/docs/COMMANDS.md#aid-status) for details
