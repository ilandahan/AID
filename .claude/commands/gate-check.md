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
| PRD Document | `docs/prd/YYYY-MM-DD-[feature].md` |
| User Stories | PRD contains user stories |
| Acceptance Criteria | Each story has AC |
| Research Links | Requirements link to research IDs (RES-XXX) |
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

1. Load skill: `.claude/skills/phase-review-agent/SKILL.md`
2. Gather all phase deliverables (files)
3. Load phase-specific checklist: `.claude/skills/phase-review-agent/phase-prompts/phase-{N}.md`
4. Spawn sub-agent using Task tool:
   ```
   Task(
     subagent_type: "general-purpose",
     model: "opus",
     prompt: [AGENT-PROMPT.md with deliverables],
     description: "Phase {N} review"
   )
   ```
5. Process result (PASS/PARTIAL/FAIL)
6. Update `.aid/state.json` with review status

### Review Cannot Be Skipped

The sub-agent review is **mandatory** and **cannot be bypassed**. This ensures:
- Fresh, unbiased evaluation of deliverables
- Consistent quality gates across all phases
- Objective checklist validation without context bias

See: `.claude/skills/phase-review-agent/SKILL.md` for full details.

## Related Commands

| Command | Purpose |
|---------|---------|
| `/phase` | Show current phase overview |
| `/phase-approve` | Approve current phase |
| `/phase-advance` | Move to next phase |
| `/aid end` | Complete phase with feedback |
