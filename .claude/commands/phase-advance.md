# /phase-advance Command

Advance to the next phase in the AID workflow after phase approval.

## Usage

```
/phase-advance
```

## Flow

1. **Check Current Phase**: Read `.aid/state.json` to get current phase
2. **Verify Sub-Agent Review**: Ensure sub-agent review passed
3. **Verify Approval**: Ensure current phase is approved (`phase_approved: true`)
4. **Verify Feedback**: Ensure feedback was provided (`feedback_provided: true`)
5. **Advance Phase**: Increment `current_phase` and update `phase_name`
6. **Reset Approval**: Set `phase_approved: false` and `feedback_provided: false` for the new phase
7. **Confirm**: Display new phase information

## Phase Progression

| From Phase | To Phase | Key Transition |
|------------|----------|----------------|
| 0 Discovery | 1 PRD | Research validated, Go/No-Go decided |
| 1 PRD | 2 Tech Spec | Requirements complete |
| 2 Tech Spec | 3 Implementation Plan | Architecture defined |
| 3 Implementation Plan | 4 Development | Tasks broken down |
| 4 Development | 5 QA & Ship | Code complete, tests passing |
| 5 QA & Ship | (Complete) | Deployed to production |

## Phase Name Mapping

```javascript
const PHASE_NAMES = {
  0: "Discovery",
  1: "PRD",
  2: "Tech Spec",
  3: "Implementation Plan",
  4: "Development",
  5: "QA & Ship"
};
```

## Prerequisites

- **Sub-agent review MUST pass** (mandatory, cannot be skipped)
- Current phase must be approved via `/phase-approve`
- **Feedback must be provided** (collected during `/aid end`)
- All phase deliverables should be complete

## Example Output

**Advancing from Phase 0 to Phase 1:**
```
Phase Advanced!

Previous: Phase 0 (Discovery)
Current:  Phase 1 (PRD)

Research deliverables:
- docs/research/2024-12-21-user-auth/research-report.md
- docs/research/2024-12-21-user-auth/traceability-matrix.md

Next steps:
- Run /aid-start to begin a PRD session
- Use /prd to create Product Requirements Document
- Link requirements to research IDs (RES-XXX)

Use /phase to see current phase details.
```

**Advancing from Phase 1 to Phase 2:**
```
Phase Advanced!

Previous: Phase 1 (PRD)
Current:  Phase 2 (Tech Spec)

Next steps:
- Run /aid-start to begin a Tech Spec session
- Use /architecture to design the system
- Create docs/tech-spec/YYYY-MM-DD-[feature].md

Use /phase to see current phase details.
```

## Error Cases

**If sub-agent review not passed:**
```
Cannot advance phase.

Sub-agent review has not passed for Phase 0 (Discovery).

Before advancing, Claude MUST:
1. Spawn review sub-agent using Task tool
2. Review all Phase 0 deliverables
3. Get PASS result

This is MANDATORY and cannot be skipped.
```

**If phase not approved:**
```
Cannot advance phase.

Current phase (Discovery) has not been approved.
Run /phase-approve after completing phase deliverables.
```

**If feedback not provided:**
```
Cannot advance phase.

Feedback has not been provided for the current phase.
Run /aid end to complete the phase with feedback.

Feedback is MANDATORY for all phase transitions.
```

**If already at final phase:**
```
Already at final phase (QA & Ship).
Project workflow complete!
```

## Implementation

When this command is invoked:

1. Read `.aid/state.json`
2. Check if `subagent_review.phase_N.status` is "passed"
   - If not passed, show error and exit (CANNOT BE SKIPPED)
3. Check if `phase_approved` is true
   - If not approved, show error and exit
4. Check if `feedback_provided` is true
   - If no feedback, show error and exit
5. If all requirements met:
   - Increment `current_phase` (max 5)
   - Update `phase_name` based on PHASE_NAMES mapping
   - Set `phase_approved` to false
   - Set `feedback_provided` to false
   - Update `last_updated` timestamp
6. Write updated state to `.aid/state.json`
7. Display success message with next steps
