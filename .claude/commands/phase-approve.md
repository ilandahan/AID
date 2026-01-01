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
- **Mandatory feedback is collected** for the learning system
- Explicit approval is given before proceeding

## Flow

1. **Check Current Phase**: Read `.aid/state.json`
2. **Display Phase Summary**: Show what was accomplished
3. **Show Checklist**: Display deliverables for this phase
4. **Collect Mandatory Feedback** (REQUIRED before approval):
   - Ask for rating (1-5)
   - Ask what worked well
   - Ask what could improve
   - Save feedback to `~/.aid/feedback/pending/{timestamp}.json`
5. **Request Approval**: Ask human to confirm
6. **Update State**: Set `phase_approved: true` and `feedback_provided: true`

## MANDATORY: Feedback Collection

**Phase approval CANNOT proceed without feedback.**

Before showing the approval prompt, Claude MUST:

1. **Ask for Rating**:
   ```
   Before approving this phase, please provide feedback.

   How would you rate this phase? (1-5)

   1 = Poor - Many issues, significant rework needed
   2 = Below average - Some problems encountered
   3 = Average - Met basic expectations
   4 = Good - Exceeded expectations
   5 = Excellent - Outstanding results
   ```

2. **Ask What Worked**:
   ```
   What worked well in this phase?
   (Examples: clear requirements, good collaboration, efficient process)
   ```

3. **Ask What Could Improve**:
   ```
   What could be improved for future phases?
   (Examples: more detail needed, different approach, better communication)
   ```

4. **Save Feedback** to `~/.aid/feedback/pending/{timestamp}.json`:
   ```json
   {
     "timestamp": "2024-01-15T12:20:00Z",
     "phase": "PRD",
     "phase_number": 1,
     "rating": 4,
     "worked_well": "Clear requirements, good user story format",
     "to_improve": "Could include more technical constraints",
     "type": "phase_approval"
   }
   ```

5. **Only AFTER feedback is saved**, proceed to approval prompt

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

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MANDATORY FEEDBACK (required before approval)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

How would you rate this phase? (1-5)
> 4

What worked well?
> Clear requirements format, good collaboration

What could be improved?
> More technical constraints upfront

✅ Feedback saved to ~/.aid/feedback/pending/

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Type 'approve' to approve this phase and allow advancement.
Type 'reject' to continue working on this phase.
```

## After Approval

Once approved:
- `phase_approved` is set to `true` in `.aid/state.json`
- `feedback_provided` is set to `true` in `.aid/state.json`
- Feedback is saved to learning system
- Run `/phase-advance` to move to the next phase
- Or continue working in current phase if needed

## Implementation

When this command is invoked:

1. Read `.aid/state.json` to get current phase
2. Display phase-specific checklist
3. **MANDATORY: Collect feedback** (rating, worked well, to improve)
4. Save feedback to `~/.aid/feedback/pending/{timestamp}.json`
5. Update `.aid/state.json` with `feedback_provided: true`
6. Ask for human confirmation
7. If confirmed:
   - Set `phase_approved: true`
   - Update `last_updated` timestamp
   - Save to `.aid/state.json`
8. Display next steps

## Error: Missing Feedback

If user tries to skip feedback:
```
⚠️ Feedback is REQUIRED before phase approval.

Please provide:
1. Rating (1-5)
2. What worked well
3. What could improve

This feedback helps improve the AID methodology.
```
