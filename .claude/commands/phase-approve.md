# /phase-approve Command

Human sign-off to approve the current phase and allow advancement.

## Usage

```
/phase-approve
```

## Purpose

This command provides a gate check before moving to the next phase. It ensures:
- All phase deliverables are complete
- Human has reviewed the work
- Explicit approval is given before proceeding

## Flow

1. **Check Current Phase**: Read `.aid/state.json`
2. **Display Phase Summary**: Show what was accomplished
3. **Show Checklist**: Display deliverables for this phase
4. **Request Approval**: Ask human to confirm
5. **Update State**: Set `phase_approved: true`

## Phase Checklists

### Phase 1: PRD
- [ ] Requirements documented in `docs/PRD.md`
- [ ] User stories defined
- [ ] Acceptance criteria specified
- [ ] Scope agreed upon

### Phase 2: Tech Spec
- [ ] Technical specification in `docs/TECH-SPEC.md`
- [ ] Database schema designed
- [ ] API endpoints defined
- [ ] Architecture decisions documented

### Phase 3: Breakdown
- [ ] Jira Epic created
- [ ] Stories broken down
- [ ] Tasks estimated
- [ ] Sprint planned

### Phase 4: Development
- [ ] All features implemented
- [ ] Tests passing
- [ ] Code reviewed
- [ ] Documentation updated

### Phase 5: QA & Ship
- [ ] QA testing complete
- [ ] No critical bugs
- [ ] Performance acceptable
- [ ] Ready for deployment

## Example Output

```
Phase Approval: PRD (Phase 1)

Checklist:
[x] Requirements documented in docs/PRD.md
[x] User stories defined
[x] Acceptance criteria specified
[x] Scope agreed upon

Type 'approve' to approve this phase and allow advancement.
Type 'reject' to continue working on this phase.
```

## After Approval

Once approved:
- `phase_approved` is set to `true` in `.aid/state.json`
- Run `/phase-advance` to move to the next phase
- Or continue working in current phase if needed

## Implementation

When this command is invoked:

1. Read `.aid/state.json` to get current phase
2. Display phase-specific checklist
3. Ask for human confirmation
4. If confirmed:
   - Set `phase_approved: true`
   - Update `last_updated` timestamp
   - Save to `.aid/state.json`
5. Display next steps
