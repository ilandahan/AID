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

### Step 5: Save Feedback + State (ONE Bash call)

```bash
# Locate the script: this AID repo → project mirror → installed plugin (newest version)
f=; for c in hooks/aid_session.py .claude/hooks/aid_session.py "$(ls -d "$HOME"/.claude/plugins/cache/AID/aid/*/ 2>/dev/null | sort -V | tail -1)hooks/aid_session.py"; do [ -f "$c" ] && f=$c && break; done
python "$f" end \
  --rating <1-5> --worked "<answer 2>" --improve "<answer 3>" \
  --review <passed|partial|failed> [--review-note "<one-line issue summary>"]
```

Writes `~/.aid/feedback/pending/<timestamp>.json` (read by `/aid-improve`) and updates
project-local `.aid/state.json`: `status: ended`, `subagent_review.phase_[N]`. Show its
output verbatim, then:

```
Options:
1. Continue to next phase ([Current] → [Next])   ← only if review PASSED (or overridden with reason)
2. Start new session with different role/phase
3. End for now
```

Option 1 with PARTIAL/FAIL: refuse, point at the issues. `override: <reason>` records
the reason in `--review-note` and allows it.

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
- Feedback is stored locally, never sent externally
- Need 3+ feedback items before `/aid improve` works
- Feedback is anonymized before any analysis
- See `phase-enforcement` skill for review checklists
- See `memory-system/docs/AGENT.md#phase-gate` for details
