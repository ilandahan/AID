---
description: "Record human sign-off for the current phase"
disable-model-invocation: true
---

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

**MANDATORY OUTPUT FIRST. Before any Bash call, print `## Phase N Summary` and
`## Phase N Checklist`** (N = the current phase from `.aid/state.json`). You MUST show both
sections to the user, as headings in your reply, before you ask for feedback and before the
`aid_session.py approve` call. The user signs off on what they saw; an approval without the
summary and checklist on screen is not a sign-off. Never skip them, even when the user asks
to approve quickly.

1. **Check Current Phase**: Read `.aid/state.json` (the Read tool, not Bash)
2. **Display Phase Summary (MANDATORY)**: Print `## Phase N Summary`: what was accomplished
3. **Show Checklist (MANDATORY)**: Print `## Phase N Checklist`: the deliverables for this
   phase (see Phase Checklists below), each marked done or not done
4. **Collect Mandatory Feedback** (REQUIRED before approval):
   - Ask for rating (1-5)
   - Ask what worked well
   - Ask what could improve
   - Do NOT write a feedback file yourself: the feedback travels in the `approve --note`
5. **Request Approval**: Ask human to confirm
6. **Record Approval**: Run `aid_session.py approve` (see Implementation). It sets
   `phase_approved` and `feedback_provided` for the current phase. Claude Code asks the
   user to confirm the call; if the user declines, nothing changes.

`.aid/state.json` is written only by `aid_session.py`. Never edit it directly: the phase
gates refuse any agent write to it.

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

4. **Condense the feedback into the approval note.** Do not write any feedback file
   yourself (the phase gates refuse `~/.aid/feedback/` before Phase 4). Instead, put the
   rating and a short summary into the `approve --note` text, using only letters, digits,
   spaces and `. _ : -`, for example:
   ```
   rating 4 clear scope - more technical constraints next time
   ```
   The script stores it in `.aid/state.json` as `phase_approval_note`.

5. **Only AFTER all three answers are collected**, proceed to approval prompt

## Phase Checklists

### Phase 1: PRD
- [ ] Requirements documented in `docs/prd/`
- [ ] User stories defined
- [ ] Acceptance criteria specified
- [ ] Scope agreed upon

### Phase 2: Tech Spec
- [ ] Technical specification in `docs/tech-spec/`
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

## Phase 1 Summary
PRD for user authentication written and reviewed (docs/prd/2026-11-19-user-auth.md).

## Phase 1 Checklist
[x] Requirements documented in docs/prd/
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

Feedback note: rating 4 clear requirements format - more technical constraints upfront

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Type 'approve' to approve this phase and allow advancement.
Type 'reject' to continue working on this phase.
> approve

Recording approval with aid_session.py approve.
Claude Code will ask you to confirm this command. If you decline, nothing changes.

[script output, shown verbatim]

Next steps:
- Run /phase-advance to move to Phase 2 (Tech Spec)
```

## After Approval

Once approved (the user typed `approve` AND confirmed the `aid_session.py approve` prompt):
- `aid_session.py` has set `phase_approved` and `feedback_provided` in `.aid/state.json`
- The feedback note is stored as `phase_approval_note`
- Run `/phase-advance` to move to the next phase
- Or continue working in current phase if needed

## Implementation

When this command is invoked:

1. Read `.aid/state.json` to get current phase
2. Print `## Phase N Summary` and `## Phase N Checklist` (MANDATORY, before any Bash call)
3. **MANDATORY: Collect feedback** (rating, worked well, to improve)
4. Condense the feedback into one note (rating plus short summary, allowed characters only)
5. Ask for human confirmation (`approve` / `reject`)
6. If the user typed `approve`, run ONE Bash call:

   ```bash
   python "${CLAUDE_PLUGIN_ROOT}/hooks/aid_session.py" approve --note "rating <1-5> <short summary>"
   ```

   - Run it exactly in this shape: one simple command, lowercase `python`, single spaces,
     no `;`, `&&`, pipes, redirects, `$( )` or loops.
   - Always pass `--note`, never empty: it carries at least the rating, for example
     `--note "rating 4 clear scope"`. Its text may contain only letters, digits, spaces and
     `. _ : -` (no commas, apostrophes, slashes or parentheses).
   - If `${CLAUDE_PLUGIN_ROOT}` was not replaced by a real path, this is not a plugin
     install: AID's phase commands need the plugin (`claude plugin install aid@AID`). Do not
     substitute another path. The user can also run the command themselves by typing it
     with a leading `!`.
   - Claude Code will ask the user to confirm this call. That prompt is the real human
     sign-off. If the user declines, nothing changes and the phase stays unapproved.
   - The script sets `phase_approved` and `feedback_provided` and prints what it did. Show
     that output. It also stores the rating from `--note` as a redacted pending feedback
     entry in `$AID_HOME/feedback/pending/`. If it refuses (non-zero exit), show its reason to the user verbatim.
   - Never retry in another spelling, never work around a refusal or a declined prompt, and
     never edit `.aid/state.json` yourself.
7. Display next steps

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
