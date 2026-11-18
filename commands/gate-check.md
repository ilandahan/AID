---
description: "Check whether the current phase is ready to advance"
---

# /gate-check Command

Check if the current phase is ready to advance to the next phase.

## Usage

```
/gate-check
```

## Purpose

Performs a diagnostic check to determine if all requirements for the current phase have been met. This is informational only - use `/phase-approve` to actually approve the phase.

## Flow

1. **Read State**: Load `.aid/state.json`
2. **Identify Phase**: Determine current phase (0-5)
3. **Check Deliverables**: Verify expected files/artifacts exist
4. **Check Sub-Agent Review**: Verify review status
5. **Report Status**: Show what's complete and what's missing

## Phase Gates

### Phase 0: Discovery
| Check | File/Artifact |
|-------|---------------|
| Research Folder | `docs/research/YYYY-MM-DD-[project]/` |
| Research Report | `research-report.md` with problem statement |
| Stakeholders | Stakeholders identified and mapped |
| Competitive | Competitive analysis documented |
| Traceability | `traceability-matrix.md` created |
| Go/No-Go | Decision documented with justification |
| Sub-Agent Review | Discovery review PASSED |
| Feedback | `/aid end` completed |

### Phase 1: PRD
| Check | File/Artifact |
|-------|---------------|
| PRD Document | `docs/prd/PRD-<feature>.md` |
| User Stories | PRD contains user stories |
| Acceptance Criteria | Each story has AC |
| Research Links | Requirements link to research IDs (RES-XXX) |
| Solution Shape | §1.5 present with the line `Signed level: [n] - by [tech lead], [date], ADR link` filled (not PROPOSED) |
| Agentic Design | §7A.1-7A.8 all present, scaled to the signed level, none "N/A" |
| WHY + Shape Brief | `docs/prd/WHY-SHAPE-BRIEF-<feature>.md` |
| Seed Evals | `docs/prd/SEED-EVALS-<feature>.md`: 20-30 cases, or `INSUFFICIENT_EXAMPLES` resolved (real examples, SME cases tagged `source: SME:<role>`, or a recorded PM + tech lead decision) |
| Level ADR | `docs/prd/ADR-SHAPE-<feature>.md`, its level matching the §1.5 "Signed level" line |
| Sub-Agent Review | PRD review PASSED |
| Feedback | `/aid end` completed |

### Phase 2: Tech Spec
| Check | File/Artifact |
|-------|---------------|
| Tech Spec | `docs/tech-spec/YYYY-MM-DD-[feature].md` |
| Architecture | Architecture diagram (Mermaid/image) |
| API | API contracts documented |
| Security | Security assessment complete |
| Sub-Agent Review | Tech Spec review PASSED |
| Feedback | `/aid end` completed |

### Phase 3: Implementation Plan
| Check | File/Artifact |
|-------|---------------|
| Plan Document | `docs/implementation-plan/YYYY-MM-DD-[feature].md` |
| Tasks | Tasks < 4 hours each |
| Dependencies | Dependencies identified |
| Test Strategy | Test strategy defined |
| Sub-Agent Review | Implementation Plan review PASSED |
| Feedback | `/aid end` completed |

### Phase 4: Development
| Check | File/Artifact |
|-------|---------------|
| Implementation | Source files created |
| Tests | Test files exist |
| Tests Pass | `npm test` passes |
| Coverage | >= 70% coverage |
| Sub-Agent Review | Development review PASSED |
| Feedback | `/aid end` completed |

### Phase 5: QA & Ship
| Check | File/Artifact |
|-------|---------------|
| QA Complete | Acceptance tests pass |
| Build | `npm run build` passes |
| Deploy Ready | All checks pass |

## Example Output

**Phase 0 (Discovery) Gate Check:**
```
Gate Check: Phase 0 (Discovery)

Status: READY TO ADVANCE

Checks:
  [x] docs/research/2024-12-21-user-auth/ exists
  [x] research-report.md present
  [x] Problem statement in SCQ format
  [x] Stakeholders identified
  [x] Competitive analysis documented
  [x] traceability-matrix.md created
  [x] Go/No-Go decision documented
  [x] Sub-agent review PASSED
  [x] Feedback collected via /aid end

Phase Approval: NOT YET APPROVED

Next steps:
- Run /phase-approve to approve this phase
- Then run /phase-advance to move to Phase 1 (PRD)
```

**If not ready:**
```
Gate Check: Phase 0 (Discovery)

Status: NOT READY

Checks:
  [x] docs/research/2024-12-21-user-auth/ exists
  [x] research-report.md present
  [ ] Problem statement missing (need SCQ format)
  [x] Stakeholders identified
  [ ] Competitive analysis not found
  [x] traceability-matrix.md created
  [ ] Go/No-Go decision not documented
  [ ] Sub-agent review PENDING
  [ ] Feedback not collected

Missing items must be completed before phase can be approved.

To complete Discovery:
1. Add problem statement in SCQ format (Situation, Complication, Question)
2. Document competitive analysis
3. Add Go/No-Go decision with justification
4. Run sub-agent review
5. Complete phase with /aid end
```

## Sub-Agent Review Status

The gate check includes the status of the mandatory sub-agent review:

| Status | Meaning |
|--------|---------|
| PENDING | Review not yet run |
| PASSED | Review completed successfully |
| FAILED | Review found critical issues |
| PARTIAL | Review found minor issues |

## Implementation

When this command is invoked:

1. Read `.aid/state.json` to get current phase
2. For each phase, check specific criteria:
   - File existence checks (docs/research/, docs/prd/, etc.)
   - Content validation (sections present)
   - Sub-agent review status
   - Feedback collection status
3. Display checklist with pass/fail for each item
4. Show overall status (READY / NOT READY)
5. Show approval status
6. Provide next steps guidance

## Sub-Agent Review Integration

**MANDATORY**: Before advancing, Claude MUST run the phase review sub-agent.

### Triggering the Review

If review status is PENDING, Claude will:

1. Gather all phase deliverables (files)
2. Pick the checklist for phase {N} (the criteria above)
3. Do not read or paste `agents/phase-review-agent.md`: the named agent brings its own prompt
   and its read-only `tools:` list
4. Spawn the phase-review-agent by name with the Task tool:
   ```
   Task(
     subagent_type: "aid:phase-review-agent",   (fallback: "phase-review-agent")
     prompt: [phase {N} and its name, the deliverable paths, the checklist],
     description: "Phase {N} review"
   )
   ```
5. Process result (PASS/PARTIAL/FAIL)
6. Record the review status with ONE Bash call (no confirmation prompt):

   ```bash
   python "${CLAUDE_PLUGIN_ROOT}/hooks/aid_session.py" review <N> <PASS|PARTIAL|FAIL> --note "<one-line issue summary>"
   ```

   - Run it exactly in this shape: one simple command, lowercase `python`, single spaces,
     no `;`, `&&`, pipes, redirects, `$( )` or loops. `--note` is optional; its text may
     contain only letters, digits, spaces and `. _ : -` (no commas, apostrophes, slashes or
     parentheses). Leave the flag out entirely when its text would be empty (an empty `""`
     is refused).
   - If `${CLAUDE_PLUGIN_ROOT}` was not replaced by a real path, this is not a plugin
     install: AID's phase commands need the plugin (`claude plugin install aid@AID`). Do not
     substitute another path. The user can also run the command themselves by typing it
     with a leading `!`.
   - The script stores the result under `subagent_review.phase_<N>`, the same key
     `/phase-advance` reads. It prints what it did; if it refuses (non-zero exit), show its
     reason to the user verbatim.
   - Never edit `.aid/state.json` yourself: `aid_session.py` is its only writer.

### Review Cannot Be Skipped

The sub-agent review is **mandatory** and **cannot be bypassed**. This ensures:
- Fresh, unbiased evaluation of deliverables
- Consistent quality gates across all phases
- Objective checklist validation without context bias

See: `agents/phase-review-agent.md` for full details.

## Related Commands

| Command | Purpose |
|---------|---------|
| `/phase` | Show current phase overview |
| `/phase-approve` | Approve current phase |
| `/phase-advance` | Move to next phase |
| `/aid end` | Complete phase with feedback |
