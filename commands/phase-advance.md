---
description: "Advance to the next AID phase"
---

# /phase-advance Command

Advance to the next phase in the AID workflow after phase approval.

## Usage

```
/phase-advance
```

## Flow

1. **Check Current Phase**: Read `.aid/state.json` to get current phase
2. **Check Sub-Agent Review**: Read `subagent_review.phase_N.status`. `"passed"` is the
   expected value; `"partial"` or `"failed"` is shown to the user, who decides (see below)
3. **Verify Approval**: Ensure current phase is approved (read `phase_approved: true`)
4. **Verify Feedback**: Ensure feedback was provided (read `feedback_provided: true`)
5. **Advance Phase**: Run `aid_session.py advance` (see Implementation). It moves to the
   next phase and resets the approval for the new phase. Claude Code asks the user to
   confirm the call; if the user declines, nothing changes.
6. **Confirm**: Display new phase information

Reading `.aid/state.json` is fine. Writing it is not: only `aid_session.py` writes it, and
the phase gates refuse any direct edit.

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

- **Sub-agent review must have run** and its result is shown; `"passed"` is expected, and
  advancing past `"partial"` or `"failed"` is the user's decision
- Current phase must be approved via `/phase-approve`
- **Feedback must be provided** (collected by `/phase-approve`, which records it with the approval)
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

**If no sub-agent review is recorded:**
```
Cannot advance phase yet.

No sub-agent review is recorded for Phase 0 (Discovery).

Before advancing, Claude MUST:
1. Spawn review sub-agent using Task tool
2. Review all Phase 0 deliverables
3. Record the result (/gate-check runs `aid_session.py review`)
```

**If the review is "partial" or "failed":**
```
Sub-agent review for Phase 0 (Discovery): PARTIAL
Issues: [from the review note]

Advancing anyway is your decision. You already approved this phase at /phase-approve.
If you go ahead, Claude Code will ask you to confirm the advance command.
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
Run /phase-approve: it collects the feedback and records it with the approval.

Feedback is MANDATORY for all phase transitions.
```

**If already at final phase:**
```
Already at final phase (QA & Ship).
Project workflow complete!
```

## Implementation

When this command is invoked:

1. Read `.aid/state.json` (read only)
2. Check `subagent_review.phase_N.status` (written by `/gate-check` or `/aid-end` through
   `aid_session.py review`)
   - Missing: show the "no review recorded" error and exit; the review must be run first
   - `"passed"`: continue
   - `"partial"` or `"failed"`: show it to the user and say that advancing is their
     decision. Continue only if the user says to; `advance` itself only requires the
     approval, which the user already gave at `/phase-approve`
3. Check if `phase_approved` is true
   - If not approved, show error and exit
4. Check if `feedback_provided` is true
   - If no feedback, show error and exit
5. If all requirements met, run ONE Bash call:

   ```bash
   python "${CLAUDE_PLUGIN_ROOT}/hooks/aid_session.py" advance
   ```

   - Run it exactly in this shape: one simple command, lowercase `python`, single spaces,
     no `;`, `&&`, pipes, redirects, `$( )` or loops.
   - If `${CLAUDE_PLUGIN_ROOT}` was not replaced by a real path, this is not a plugin
     install: AID's phase commands need the plugin (`claude plugin install aid@AID`). Do not
     substitute another path. The user can also run the command themselves by typing it
     with a leading `!`.
   - Claude Code will ask the user to confirm this call. If the user declines, nothing
     changes and the project stays in the current phase.
   - The script refuses unless the current phase is approved. On success it moves to the
     next phase (max 5) and resets the approval. It prints what it did; show that output.
   - If it refuses (non-zero exit), show its reason to the user verbatim. Never retry in
     another spelling, never work around it, and never edit `.aid/state.json` yourself.
6. Display success message with next steps
