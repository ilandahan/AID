# /phase-advance Command

Advance to the next phase in the AID workflow after phase approval.

## Usage

```
/phase-advance
```

## Flow

1. **Check Current Phase**: Read `.aid/state.json` to get current phase
2. **Verify Approval**: Ensure current phase is approved (`phase_approved: true`)
3. **Advance Phase**: Increment `current_phase` and update `phase_name`
4. **Reset Approval**: Set `phase_approved: false` for the new phase
5. **Confirm**: Display new phase information

## Phase Progression

| From Phase | To Phase |
|------------|----------|
| 1 PRD | 2 Tech Spec |
| 2 Tech Spec | 3 Breakdown |
| 3 Breakdown | 4 Development |
| 4 Development | 5 QA & Ship |
| 5 QA & Ship | (Complete) |

## Prerequisites

- Current phase must be approved via `/phase-approve`
- All phase deliverables should be complete

## Example Output

```
Phase Advanced!

Previous: Phase 1 (PRD)
Current:  Phase 2 (Tech Spec)

Next steps:
- Run /aid-start to begin a Tech Spec session
- Use /architecture to design the system
- Create docs/TECH-SPEC.md

Use /phase to see current phase details.
```

## Error Cases

**If phase not approved:**
```
Cannot advance phase.

Current phase (PRD) has not been approved.
Run /phase-approve after completing phase deliverables.
```

**If already at final phase:**
```
Already at final phase (QA & Ship).
Project workflow complete!
```

## Implementation

When this command is invoked:

1. Read `.aid/state.json`
2. Check if `phase_approved` is true
3. If not approved, show error and exit
4. If approved:
   - Increment `current_phase` (max 5)
   - Update `phase_name` based on phase number
   - Set `phase_approved` to false
   - Update `last_updated` timestamp
5. Write updated state to `.aid/state.json`
6. Display success message with next steps
