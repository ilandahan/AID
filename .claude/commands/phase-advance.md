# /phase-advance

Move to the next phase (if gate criteria are met).

## What It Does

1. Run gate check for current phase
2. If PASS: advance to next phase
3. If FAIL: show what's missing

## Output

### Gate FAILS

```
═══════════════════════════════════════════════════════
⛔ CANNOT ADVANCE

Missing for Phase 2:
  [✗] API endpoints not documented
  [✗] Human approval required

Complete these, then run /phase-advance again.
═══════════════════════════════════════════════════════
```

### Gate PASSES

```
═══════════════════════════════════════════════════════
✅ GATE CHECK PASSED

Advancing: Phase 2 → Phase 3

Updating .aid/state.json...

═══════════════════════════════════════════════════════
       🎉 NOW IN PHASE 3: IMPLEMENTATION PLAN
═══════════════════════════════════════════════════════

Objectives:
  1. Create Implementation Plan from PRD + Tech Spec
  2. Define phases with test requirements
  3. Plan rollout/rollback strategy
  4. Run /implementation-plan [feature]

Document Path:
  → docs/implementation-plan/YYYY-MM-DD-[feature].md

Allowed:
  ✅ Create implementation plan
  ✅ Define test phases
  ✅ Plan rollout strategy

Blocked:
  ❌ Writing production code (Phase 4)

Run /phase for full status
═══════════════════════════════════════════════════════
```

### Already at Final Phase

```
═══════════════════════════════════════════════════════
🏁 You are in Phase 5 (QA & Ship) - final phase

Complete QA and ship when ready.
═══════════════════════════════════════════════════════
```

## State Update

Update `.aid/state.json`:
```json
{
  "current_phase": 3,
  "phase_name": "Task Breakdown",
  "phases": {
    "2": { "status": "complete", "completed_at": "..." },
    "3": { "status": "in_progress", "started_at": "..." }
  }
}
```
