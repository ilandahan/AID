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
2. **Identify Phase**: Determine current phase
3. **Check Deliverables**: Verify expected files/artifacts exist
4. **Report Status**: Show what's complete and what's missing

## Phase Gates

### Phase 1: PRD
| Check | File/Artifact |
|-------|---------------|
| PRD Document | `docs/PRD.md` |
| Requirements | PRD contains user stories |

### Phase 2: Tech Spec
| Check | File/Artifact |
|-------|---------------|
| Tech Spec | `docs/TECH-SPEC.md` |
| Schema | Database schema defined |
| API | API endpoints documented |

### Phase 3: Breakdown
| Check | File/Artifact |
|-------|---------------|
| Jira Epic | Epic created (check via MCP) |
| Stories | Stories linked to Epic |

### Phase 4: Development
| Check | File/Artifact |
|-------|---------------|
| Implementation | Source files created |
| Tests | Test files exist |
| Tests Pass | `npm test` passes |

### Phase 5: QA & Ship
| Check | File/Artifact |
|-------|---------------|
| QA Complete | Manual testing done |
| Build | `npm run build` passes |
| Deploy Ready | All checks pass |

## Example Output

```
Gate Check: Phase 1 (PRD)

Status: READY TO ADVANCE

Checks:
  [x] docs/PRD.md exists
  [x] PRD contains user stories section
  [x] PRD contains acceptance criteria
  [x] Scope section defined

Phase Approval: NOT YET APPROVED

Next steps:
- Run /phase-approve to approve this phase
- Then run /phase-advance to move to Phase 2
```

Or if not ready:

```
Gate Check: Phase 1 (PRD)

Status: NOT READY

Checks:
  [x] docs/PRD.md exists
  [ ] PRD missing user stories section
  [ ] PRD missing acceptance criteria
  [x] Scope section defined

Missing items must be completed before phase can be approved.
```

## Implementation

When this command is invoked:

1. Read `.aid/state.json` to get current phase
2. For each phase, check specific criteria:
   - File existence checks
   - Content validation (sections present)
   - External checks (Jira via MCP, test results)
3. Display checklist with pass/fail for each item
4. Show overall status (READY / NOT READY)
5. Show approval status
6. Provide next steps guidance
