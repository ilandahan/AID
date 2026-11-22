---
description: "Manage AID's local memory entries"
---

# /aid-memory

Manage AID's local memory entries. "Claude Memory" in AID means a LOCAL file,
`$AID_HOME/memory/slots.json` (default `~/.aid/memory/`). Nothing is sent to Claude's
built-in memory.

## Subcommands

### /aid-memory list

Show all AID-related entries in AID's local memory.

Get the list ONLY from the output of `python -m memory_system --memories` run from the
plugin's `memory-system/` folder: it redacts secrets, paths and project names on display.
Never Read `slots.json` directly to build this list (older entries may hold unredacted text).

```
AID Memory Entries
==================

user_preferences (<used>/5 slots):
  1. AID:ALL:ALL:WORKFLOW Always complete current phase before starting next
  2. AID:ALL:ALL:HUMAN Get explicit approval before major decisions

decision_patterns (<used>/8 slots):
  1. AID:DEV:TECH:DECISIONS Document why not just what for tech choices

feedback_trends (<used>/5 slots):
  [...]

skill_adjustments (<used>/7 slots):
  1. AID:DEV:DEV:TDD Write test first then implement

context (<used>/5 slots):
  [...]
```

The categories and their slot counts are the memory system's slot allocation
(`SLOT_ALLOCATION` in `memory-system/memory_system/analysis/memory_sync.py`): 5 + 8 + 5 + 7 +
5 = 30 slots. Show the counts the memory system reports, never numbers from this page.

### /aid-memory stats

Show memory usage statistics.

```
AID Memory Statistics
=====================

Slot Usage:
  user_preferences:   <used>/5
  decision_patterns:  <used>/8
  feedback_trends:    <used>/5
  skill_adjustments:  <used>/7
  context:            <used>/5

  Total: <memory.used>/<memory.total> slots used
```

Take the total from `memory.used` and `memory.total` in the output of exactly
`python "${CLAUDE_PLUGIN_ROOT}/hooks/aid_session.py" status --format json` (one plain
command, read-only, not asked). The total is the sum of the slot allocation (30 today); an
empty memory shows `0/30`. A value the command does not return is shown as `unknown`.

## Usage

```
/aid-memory list
/aid-memory stats
```

## Notes

- AID entries use prefix `AID:` for easy identification
- Learned entries can be added via `/aid-improve`, which runs exactly
  `python "${CLAUDE_PLUGIN_ROOT}/hooks/aid_session.py" memory-sync` (one plain command) to
  write them; Claude Code asks the user to confirm
- Do not edit `slots.json` by hand
- See `memory-system/docs/MEMORY.md` for slot allocation details
