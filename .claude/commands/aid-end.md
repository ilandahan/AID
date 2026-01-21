# /aid end

End current phase and collect feedback.

## Purpose

Complete the current phase with mandatory sub-agent review, then collect user feedback for the learning system.

## Flow

### Step 1: Sub-Agent Review (MANDATORY)

```
┌─────────────────────────────────────────────────────────────────┐
│  ⚠️  MANDATORY SUB-AGENT REVIEW BEFORE PHASE TRANSITION         │
│                                                                 │
│  Claude MUST spawn a review sub-agent before proceeding.        │
│  This step CANNOT be skipped.                                   │
└─────────────────────────────────────────────────────────────────┘
```

**Claude must:**
1. Identify current phase from `~/.aid/state.json`
2. Use Task tool to spawn review sub-agent with appropriate review prompt
3. Wait for review result (PASS/PARTIAL/FAIL)
4. If FAIL: Stop and address issues before retrying
5. If PARTIAL: Show issues, allow override with reason
6. If PASS: Proceed to feedback collection

**Sub-Agent Invocation:**
```
Task tool:
- subagent_type: "general-purpose"
- description: "Phase [N] gate review"
- prompt: [Phase-specific review checklist from phase-enforcement skill]
```

### Step 2: Review Result Handling

**On PASS:**
```
✅ SUB-AGENT REVIEW PASSED

Phase: [N] [Phase Name]
Result: PASS - All requirements verified

Proceeding to feedback collection...
```

**On PARTIAL:**
```
⚠️ SUB-AGENT REVIEW: PARTIAL PASS

Phase: [N] [Phase Name]
Issues found:
1. [Issue with location]
2. [Issue with location]

Options:
1. Fix issues and re-run /aid end
2. Override with reason: "override: [your reason]"
```

**On FAIL:**
```
❌ SUB-AGENT REVIEW FAILED

Phase: [N] [Phase Name]
Critical issues:
1. [Critical issue with location]
2. [Critical issue with location]

These MUST be fixed before phase transition.
Cannot proceed. Fix issues and re-run /aid end.
```

### Step 3: Summarize Work (after review passes)

```
Phase Summary: Development

Work completed:
- Implemented user authentication
- Added API endpoints for login/logout
- Created unit tests (85% coverage)

Duration: 3h 20m
Sub-Agent Review: PASSED
```

### Step 4: Ask for Rating

```
How would you rate this session? (1-5)

1 = Poor - Many issues
2 = Below average - Some problems
3 = Average - Met basic expectations
4 = Good - Exceeded expectations
5 = Excellent - Outstanding results
```

### Step 5: Ask What Worked

```
What worked well in this session?
(Examples: clear explanations, good code structure, helpful suggestions)
```

### Step 6: Ask What Could Improve

```
What could be improved?
(Examples: more detail needed, different approach, missing context)
```

### Step 7: Save Feedback

Save to `~/.aid/feedback/pending/{timestamp}.json`:
```json
{
  "timestamp": "2024-01-15T12:20:00Z",
  "role": "developer",
  "phase": "development",
  "rating": 4,
  "worked_well": "Clear code structure, good test coverage",
  "to_improve": "Could explain architectural decisions more",
  "duration_minutes": 200,
  "subagent_review": {
    "status": "passed",
    "timestamp": "2024-01-15T12:15:00Z"
  }
}
```

### Step 8: Update State

Update `~/.aid/state.json` with review status:
```json
{
  "subagent_review": {
    "phase_[N]": {
      "status": "passed",
      "timestamp": "2024-01-15T12:15:00Z"
    }
  }
}
```

### Step 9: Confirm & Next

```
✅ Phase Complete

Sub-Agent Review: PASSED
Feedback: Saved

Options:
1. Continue to next phase ([Current] → [Next])
2. Start new session with different role/phase
3. End for now
```

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

- Sub-agent review is MANDATORY - cannot be skipped
- Feedback is stored locally, never sent externally
- Need 3+ feedback items before `/aid improve` works
- Feedback is anonymized before any analysis
- See `phase-enforcement` skill for review checklists
- See `memory-system/docs/AGENT.md#phase-gate` for details
