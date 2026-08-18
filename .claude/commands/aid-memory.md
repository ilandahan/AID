# /aid memory

Manage Claude Memory entries for AID.

## Subcommands

### /aid memory list

Show all AID-related entries in Claude Memory.

```
AID Memory Entries
==================

Universal (5/5 slots):
  1. AID:ALL:ALL:WORKFLOW Always complete current phase before starting next
  2. AID:ALL:ALL:CONTEXT Start each session by reading work_context.json
  3. AID:ALL:ALL:DOCS Update documentation in real-time not at end
  4. AID:ALL:ALL:HUMAN Get explicit approval before major decisions
  5. AID:ALL:ALL:QUALITY Verify every artifact against requirements

Developer (4/5 slots):
  1. AID:DEV:TECH:DECISIONS Document why not just what for tech choices
  2. AID:DEV:DEV:TDD Write test first then implement
  3. AID:DEV:DEV:ATOMIC One logical change per commit
  4. AID:DEV:ALL:DEBT Mark shortcuts with TODO-DEBT and track

PM (5/5 slots):
  [...]

Learned (3/10 slots):
  1. AID:DEV:DEV:LEARNED When implementing auth start with session management
  2. AID:QA:QA:LEARNED Edge cases in date handling need timezone tests
  3. AID:PM:PRD:LEARNED Stakeholder availability affects timeline estimates
```

### /aid memory stats

Show memory usage statistics.

```
AID Memory Statistics
=====================

Slot Usage:
  Universal:  5/5  [█████████████████████] 100%
  PM:         5/5  [█████████████████████] 100%
  Developer:  4/5  [████████████████░░░░░]  80%
  QA:         5/5  [█████████████████████] 100%
  Lead:       2/3  [██████████████░░░░░░░]  67%
  Phase:      3/5  [████████████░░░░░░░░░]  60%
  Learned:    3/10 [██████░░░░░░░░░░░░░░░]  30%
  
  Total: 27/38 slots used (71%)

Last Updated: 3 days ago
Entries from feedback: 3
```

## Usage

```
/aid memory list
/aid memory stats
```

## Notes

- AID entries use prefix `AID:` for easy identification
- Learned entries can be promoted via `/aid improve`
- Manual management available via Claude Memory interface
- See `memory-system/docs/MEMORY.md` for slot allocation details
