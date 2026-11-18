---
description: "End the current phase and record session feedback"
---

# /aid end

End current phase and collect feedback.

## Purpose

Complete the current phase with mandatory sub-agent review, then collect user feedback for the learning system.

## Flow

Design rule: the user never waits on the sub-agent. The review starts first, runs in
the background while feedback is collected, and its verdict gates only the phase
transition (option 1 in Step 5). Saving feedback does not wait for it.

### Step 1: Start the Phase Review Sub-Agent (MANDATORY, background)

```
┌─────────────────────────────────────────────────────────────────┐
│  ⚠️  MANDATORY SUB-AGENT REVIEW - STARTED FIRST, RUNS IN BACKGROUND │
│                                                                 │
│  Claude MUST spawn the review before collecting feedback.       │
│  This step CANNOT be skipped. It must not block Steps 2-3.      │
└─────────────────────────────────────────────────────────────────┘
```

1. Read phase from project-local `.aid/state.json` (`current_phase`, `phase_display`).
2. Locate the phase deliverable(s) so the reviewer gets exact paths, not a repo to explore:
   - Phase 0: `docs/research/*.md`
   - Phase 1: `docs/prd/*.md`
   - Phase 2: `docs/tech-spec/*.md`
   - Phase 3: `docs/implementation-plan/*.md`
   - Phase 4-5: `.aid/context.json` current task + files listed there
   (one Glob; if nothing exists, pass "no deliverable found" and let the reviewer say so)
3. Spawn with the Agent tool. Do not wait on it yet.

```
Agent tool:
- subagent_type: "aid:phase-review-agent"   (fallback: "phase-review-agent")
- description: "Phase [N] gate review"
- prompt: "Phase [N] ([Phase Name]) gate review. Deliverables: [exact paths].
           Checklist: [Review Prompt for this phase, below].
           Return PASS | PARTIAL | FAIL, then issues with file:line."
```

Tell the user in one line: `Phase [N] review running in background - meanwhile, a few questions.`

### Step 2: Summarize Work

```
Phase Summary: [Phase Name]

Work completed:
- [from .aid/context.json completed steps / this conversation]

Duration: [from state.json session_start]
```

### Step 3: Collect Feedback (ONE prompt, three answers)

Ask all three together; the user answers in one message:

```
Three quick questions (answer in one message):

1. Rating 1-5?   (1 poor · 3 met expectations · 5 excellent)
2. What worked well?
3. What could be improved?
```

### Step 4: Collect the Review Verdict

By now the sub-agent has usually finished. Take its result (wait for it only if it has
not returned yet).

**On PASS:**
```
✅ SUB-AGENT REVIEW PASSED - Phase [N] [Phase Name]
```

**On PARTIAL:**
```
⚠️ SUB-AGENT REVIEW: PARTIAL PASS - Phase [N] [Phase Name]
Issues found:
1. [Issue with location]
2. [Issue with location]

Phase transition needs: fix and re-run /aid-end, or "override: [reason]".
Ending the session is fine as-is.
```

**On FAIL:**
```
❌ SUB-AGENT REVIEW FAILED - Phase [N] [Phase Name]
Critical issues:
1. [Critical issue with location]

Phase transition blocked until fixed. Ending the session is fine as-is.
```

Record the verdict (ONE Bash call, no confirmation prompt). This is the value
`/phase-advance` reads as `subagent_review.phase_[N]`:

```bash
python "${CLAUDE_PLUGIN_ROOT}/hooks/aid_session.py" review <N> <PASS|PARTIAL|FAIL> --note "<one-line issue summary>"
```

If `${CLAUDE_PLUGIN_ROOT}` was not replaced by a real path, this is not a plugin install:
AID's phase commands need the plugin (`claude plugin install aid@AID`). Do not substitute
another path. The user can also run the command themselves by typing it with a leading `!`.

### Step 5: Save Feedback + State (ONE Bash call)

```bash
python "${CLAUDE_PLUGIN_ROOT}/hooks/aid_session.py" end --rating <1-5> --worked "<answer 2>" --improve "<answer 3>" --review <passed|partial|failed> --review-note "<one-line issue summary>"
```

Run each script call exactly in this shape: ONE simple command on one line, lowercase
`python`, single spaces, no `;`, `&&`, pipes, redirects, `$( )`, loops or line
continuations. Any other shape is refused by the phase gate. Quoted answers may contain only
letters, digits, spaces and `. _ : -` (no commas, apostrophes, slashes or parentheses);
drop other characters. Leave a flag out entirely when its text would be empty (an empty `""`
is refused); `--review-note` and the review `--note` are optional.

Writes `$AID_HOME/feedback/pending/<timestamp>.json` (default `~/.aid/feedback/pending/`,
read by `/aid-improve`). The `--worked`, `--improve` and `--review-note` text is redacted
(best effort) before it is written. Never write a feedback file yourself. The script also updates
project-local `.aid/state.json`: `status: ended`, `subagent_review.phase_[N]`. The script is
the only writer of `.aid/state.json`; never edit that file yourself. If the script refuses
(non-zero exit with a reason), show the reason to the user verbatim; do not retry in another
spelling or work around it. Show its output verbatim, then:

```
Options:
1. Continue to next phase ([Current] → [Next])   ← the user decides at /phase-approve
2. Start new session with different role/phase
3. End for now
```

Option 1 is a phase change, so it goes through the human gates: `/phase-approve` (the
user's sign-off), then `/phase-advance`. Never change the phase any other way.

Option 1 with PARTIAL/FAIL: point at the issues and recommend fixing them first. If the user
says `override: <reason>`, record the reason in `--review-note` (allowed characters only).
An override does not change the recorded verdict: it means the user will decide at
`/phase-approve`, where approving despite a PARTIAL/FAIL review is the user's call.
`/phase-advance` then shows the non-passing review again before the user confirms.

## Usage

```
/aid end
```

## Review Prompts by Phase

### Phase 1 (PRD) Review Prompt
```
Review PRD at docs/prd/[feature].md for:
- Problem statement clarity
- User stories format
- Acceptance criteria completeness
- Non-functional requirements
- Measurable success metrics
- Scope boundaries
- Stakeholder identification
- No implementation details
```

### Phase 2 (Tech Spec) Review Prompt
```
Review Tech Spec at docs/tech-spec/[feature].md for:
- Architecture diagram
- Component definitions
- Data models (TypeScript)
- API contracts
- Database schema
- Security assessment
- Error handling strategy
- PRD traceability
```

### Phase 3 (Implementation Plan) Review Prompt
```
Review Implementation Plan at docs/implementation-plan/[feature].md for:
- Tasks < 4 hours each
- Clear acceptance criteria per task
- Dependencies identified
- Dependency order
- Test strategy (unit/integration/E2E)
- Risk assessment
- Tech Spec mapping
- Step-by-step order explicit
```

### Phase 4 (Development) Review Prompt
```
Review implementation for:
- All tasks complete
- Tests passing
- Coverage >= 70%
- No test-specific production code
- Lint passes
- Build succeeds
- No security vulnerabilities
- Documentation updated
- Code reviewed
```

## Notes

- Sub-agent review is MANDATORY - cannot be skipped; it runs in the background so the user never waits on it
- Review verdict gates the phase transition only, never the feedback save
- Feedback is stored locally in `$AID_HOME`. AID has no collection service of its own. When
  you run `/aid-improve`, the redacted feedback is sent to Claude as part of the
  conversation, for analysis.
- Need 3+ feedback items before `/aid improve` works
- Feedback text is redacted (best effort) before it is written, and again whenever it is read.
  E-mails, URLs, absolute paths, `file.ext:line` references, common secret tokens, the
  project's own names (folder names, git remote owner and repo) and the OS user name are
  replaced with placeholders. A person's or company's name written as plain words is not
  caught unless it is one of those project names, so do not type names you want kept private
- See `phase-enforcement` skill for review checklists
- See `memory-system/docs/AGENT.md#3-phase-gate-flow-feedback-collection` (section "3. Phase Gate Flow") for details
