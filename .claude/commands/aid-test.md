# /aid-test

Run the complete AID methodology test suite with simulated human approvals.

---

## What This Command Does

1. Creates a test project directory
2. Initializes AID phases
3. Tests phase gate enforcement (tries blocked actions)
4. Simulates human approval at each gate
5. Progresses through all 5 phases
6. Tests context tracking
7. Reports results

---

## Test Execution Flow

When user runs `/aid-test`, Claude executes:

```
═══════════════════════════════════════════════════════════════════════
                    🧪 AID METHODOLOGY TEST SUITE
═══════════════════════════════════════════════════════════════════════

Starting test run...
Test project: /tmp/aid-test-{timestamp}

───────────────────────────────────────────────────────────────────────
SUITE 1: INSTALLATION & SETUP
───────────────────────────────────────────────────────────────────────

TEST 1.1: Verify file structure
  Checking .claude/commands/... ✓ (8 files)
  Checking skills/... ✓ (7 folders)
  Checking docs/... ✓ (6 files)
  Checking templates/.aid/... ✓ (2 files)
  RESULT: ✓ PASSED

TEST 1.2: Initialize project (/aid-init)
  Creating .aid/state.json... ✓
  Creating .aid/context.json... ✓
  Setting phase to 1... ✓
  RESULT: ✓ PASSED

───────────────────────────────────────────────────────────────────────
SUITE 2: PHASE GATE ENFORCEMENT
───────────────────────────────────────────────────────────────────────

TEST 2.1: Block code request in Phase 1
  Current phase: 1 (PRD)
  Requesting: "Create a React Button component"
  Expected: BLOCKED
  Actual: BLOCKED ✓
  Error message includes "Phase 4": ✓
  RESULT: ✓ PASSED

TEST 2.2: Block architecture in Phase 1
  Requesting: "Design database schema"
  Expected: BLOCKED
  Actual: BLOCKED ✓
  RESULT: ✓ PASSED

TEST 2.3: Block Jira in Phase 1
  Requesting: "Create Jira epics"
  Expected: BLOCKED
  Actual: BLOCKED ✓
  RESULT: ✓ PASSED

TEST 2.4: Allow PRD work in Phase 1
  Requesting: "Create PRD for todo app"
  Expected: ALLOWED
  Actual: ALLOWED ✓
  PRD content generated: ✓
  RESULT: ✓ PASSED

───────────────────────────────────────────────────────────────────────
SUITE 3: PHASE PROGRESSION
───────────────────────────────────────────────────────────────────────

TEST 3.1: Gate check before PRD complete
  Running /gate-check...
  Expected: NOT READY
  Actual: NOT READY ✓
  Missing items listed: ✓
  RESULT: ✓ PASSED

TEST 3.2: Gate check after PRD complete
  [Simulating PRD creation]
  Running /gate-check...
  Expected: READY
  Actual: READY ✓
  RESULT: ✓ PASSED

TEST 3.3: Advance without approval
  Running /phase-advance...
  Expected: BLOCKED
  Actual: BLOCKED ✓
  Message mentions approval needed: ✓
  RESULT: ✓ PASSED

TEST 3.4: Human approval simulation
  Running /phase-approve...
  🤖 SIMULATING HUMAN: Typing "approve"
  Expected: Approval recorded
  Actual: .aid/approvals/phase-1-approved.md created ✓
  RESULT: ✓ PASSED

TEST 3.5: Advance after approval
  Running /phase-advance...
  Expected: Move to Phase 2
  Actual: Phase 2 (Tech Spec) ✓
  state.json updated: ✓
  RESULT: ✓ PASSED

───────────────────────────────────────────────────────────────────────
SUITE 4: PHASE 2 TESTS
───────────────────────────────────────────────────────────────────────

TEST 4.1: Block code in Phase 2
  Requesting: "Implement login API"
  Expected: BLOCKED
  Actual: BLOCKED ✓
  RESULT: ✓ PASSED

TEST 4.2: Allow architecture in Phase 2
  Requesting: "Design system architecture"
  Expected: ALLOWED
  Actual: ALLOWED ✓
  RESULT: ✓ PASSED

TEST 4.3: Complete Phase 2 cycle
  Creating tech spec... ✓
  /gate-check... READY ✓
  🤖 SIMULATING HUMAN: /phase-approve → "approve"
  /phase-advance... Phase 3 ✓
  RESULT: ✓ PASSED

───────────────────────────────────────────────────────────────────────
SUITE 5: PHASE 3 TESTS
───────────────────────────────────────────────────────────────────────

TEST 5.1: Block code in Phase 3
  Requesting: "Write user model code"
  Expected: BLOCKED
  Actual: BLOCKED ✓
  RESULT: ✓ PASSED

TEST 5.2: Allow Jira work in Phase 3
  Requesting: "Create Jira breakdown"
  Expected: ALLOWED
  Actual: ALLOWED ✓
  RESULT: ✓ PASSED

TEST 5.3: Complete Phase 3 cycle
  Creating breakdown... ✓
  🤖 SIMULATING HUMAN: approve
  Advancing... Phase 4 ✓
  RESULT: ✓ PASSED

───────────────────────────────────────────────────────────────────────
SUITE 6: PHASE 4 TESTS (DEVELOPMENT)
───────────────────────────────────────────────────────────────────────

TEST 6.1: Allow code in Phase 4
  Requesting: "Create TodoItem component"
  Expected: ALLOWED
  Actual: ALLOWED ✓
  Code generated: ✓
  RESULT: ✓ PASSED

TEST 6.2: Block deployment in Phase 4
  Requesting: "Deploy to production"
  Expected: BLOCKED
  Actual: BLOCKED ✓
  RESULT: ✓ PASSED

───────────────────────────────────────────────────────────────────────
SUITE 7: CONTEXT TRACKING
───────────────────────────────────────────────────────────────────────

TEST 7.1: View empty context
  Running /context...
  Shows "no current task": ✓
  RESULT: ✓ PASSED

TEST 7.2: Set task
  Running /context-update task TEST-001...
  context.json updated: ✓
  current.key = "TEST-001": ✓
  RESULT: ✓ PASSED

TEST 7.3: Update progress
  Running /context-update progress 75%...
  progress = "75%": ✓
  RESULT: ✓ PASSED

TEST 7.4: Complete step
  Running /context-update step done...
  Previous step marked done: ✓
  Steps shifted: ✓
  Session log updated: ✓
  RESULT: ✓ PASSED

───────────────────────────────────────────────────────────────────────
SUITE 8: MORNING STARTUP
───────────────────────────────────────────────────────────────────────

TEST 8.1: Good morning with context
  Running /good-morning...
  Shows task progression: ✓
  Shows step progression: ✓
  Shows continue options: ✓
  RESULT: ✓ PASSED

───────────────────────────────────────────────────────────────────────
SUITE 9: PHASE 5 & COMPLETION
───────────────────────────────────────────────────────────────────────

TEST 9.1: Complete Phase 4 cycle
  🤖 SIMULATING HUMAN: approve
  Advancing... Phase 5 ✓
  RESULT: ✓ PASSED

TEST 9.2: Allow deployment in Phase 5
  Requesting: "Deploy to production"
  Expected: ALLOWED
  Actual: ALLOWED ✓
  RESULT: ✓ PASSED

TEST 9.3: Full workflow complete
  All 5 phases completed: ✓
  All gates passed: ✓
  Context tracked throughout: ✓
  RESULT: ✓ PASSED

═══════════════════════════════════════════════════════════════════════
                         📊 TEST RESULTS
═══════════════════════════════════════════════════════════════════════

Total Tests:  25
Passed:       25 ✓
Failed:       0 ✗
Skipped:      0

Duration: 2m 34s

───────────────────────────────────────────────────────────────────────
                    ✅ ALL TESTS PASSED
───────────────────────────────────────────────────────────────────────

Phase Gate Summary:
  Phase 1 → 2: ✓ Blocked code, allowed PRD, approved, advanced
  Phase 2 → 3: ✓ Blocked code, allowed arch, approved, advanced
  Phase 3 → 4: ✓ Blocked code, allowed Jira, approved, advanced
  Phase 4 → 5: ✓ Allowed code, blocked deploy, approved, advanced
  Phase 5:    ✓ All actions allowed

Context Tracking: ✓ Working
Morning Startup: ✓ Working

🎉 AID METHODOLOGY VALIDATED SUCCESSFULLY

═══════════════════════════════════════════════════════════════════════
```

---

## Human Approval Simulation

When the test needs human approval, it automatically:

1. Calls `/phase-approve`
2. Simulates typing "approve"
3. Logs the simulation:
   ```
   🤖 SIMULATING HUMAN: Typing "approve"
   ```
4. Continues with the test

---

## Test Modes

### Standard Mode (default)
```
/aid-test
```
- Full test suite with simulated approvals
- Takes ~2-3 minutes
- Outputs detailed report

### Quick Mode
```
/aid-test quick
```
- Critical path only
- Phase gates + one full cycle
- Takes ~30 seconds

### Verbose Mode
```
/aid-test verbose
```
- Shows all internal state changes
- Dumps JSON files
- Debug output

---

## Implementation Notes

Claude executes this test by:

1. Creating temporary directory structure
2. Simulating .aid/state.json and .aid/context.json
3. For each test:
   - Set up preconditions
   - Execute action
   - Check result matches expected
   - Log result
4. Aggregate and report

The key insight is that Claude "tests itself" - it classifies work requests and checks if its own phase enforcement logic responds correctly.
