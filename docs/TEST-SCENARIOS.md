# AID Test Agent

## Purpose

Automated testing agent that validates the entire AID methodology by simulating a real development workflow, including phase gate enforcement and human approval simulation.

---

## Test Scenarios

### Test Suite 1: Installation & Setup

```
TEST 1.1: Clone and Verify Structure
─────────────────────────────────────
Action: Clone repo, verify all files exist
Expected: 
  ✓ .claude/commands/ (8 files)
  ✓ skills/ (7 folders)
  ✓ docs/ (6+ files)
  ✓ templates/.aid/ (2 files)
  ✓ CLAUDE.md exists
  ✓ README.md exists
```

```
TEST 1.2: Initialize Project
─────────────────────────────────────
Action: Run /aid-init
Expected:
  ✓ .aid/state.json created
  ✓ .aid/context.json created
  ✓ Phase set to 1 (PRD)
  ✓ Status shows "Phase 1: PRD"
```

---

### Test Suite 2: Phase Gate Enforcement (CRITICAL)

```
TEST 2.1: Block Code in Phase 1
─────────────────────────────────────
Current Phase: 1 (PRD)
Action: Request "create a React Button component"
Expected: 
  ✗ BLOCKED
  ✓ Error message mentions "Phase 4"
  ✓ Suggests completing PRD first
```

```
TEST 2.2: Block Architecture in Phase 1
─────────────────────────────────────
Current Phase: 1 (PRD)
Action: Request "design the database schema"
Expected:
  ✗ BLOCKED
  ✓ Error message mentions "Phase 2"
```

```
TEST 2.3: Block Jira in Phase 1
─────────────────────────────────────
Current Phase: 1 (PRD)
Action: Request "create Jira epics for this project"
Expected:
  ✗ BLOCKED
  ✓ Error message mentions "Phase 3"
```

```
TEST 2.4: Allow PRD Work in Phase 1
─────────────────────────────────────
Current Phase: 1 (PRD)
Action: Request "create PRD for user authentication feature"
Expected:
  ✓ ALLOWED
  ✓ PRD content generated
```

---

### Test Suite 3: Phase Progression

```
TEST 3.1: Gate Check - Not Ready
─────────────────────────────────────
Current Phase: 1 (PRD)
State: No PRD created
Action: Run /gate-check
Expected:
  ✗ NOT READY
  ✓ Lists missing: "docs/PRD.md"
```

```
TEST 3.2: Gate Check - Ready
─────────────────────────────────────
Current Phase: 1 (PRD)
State: PRD exists and complete
Action: Run /gate-check
Expected:
  ✓ READY
  ✓ All criteria met
```

```
TEST 3.3: Advance Without Approval
─────────────────────────────────────
Current Phase: 1 (PRD)
State: Gate check passed, NOT approved
Action: Run /phase-advance
Expected:
  ✗ BLOCKED
  ✓ Requires /phase-approve first
```

```
TEST 3.4: Human Approval Simulation
─────────────────────────────────────
Current Phase: 1 (PRD)
Action: Run /phase-approve, type "approve"
Expected:
  ✓ Approval recorded
  ✓ .aid/approvals/phase-1-approved.md created
  ✓ Timestamp recorded
```

```
TEST 3.5: Advance After Approval
─────────────────────────────────────
Current Phase: 1 (PRD)
State: Approved
Action: Run /phase-advance
Expected:
  ✓ Phase updated to 2
  ✓ state.json shows phase: 2
  ✓ Message confirms "Now in Phase 2: Tech Spec"
```

---

### Test Suite 4: Phase 2 (Tech Spec)

```
TEST 4.1: Block Code in Phase 2
─────────────────────────────────────
Current Phase: 2 (Tech Spec)
Action: Request "implement the login API"
Expected:
  ✗ BLOCKED
  ✓ Code not allowed until Phase 4
```

```
TEST 4.2: Allow Architecture in Phase 2
─────────────────────────────────────
Current Phase: 2 (Tech Spec)
Action: Request "design the system architecture"
Expected:
  ✓ ALLOWED
  ✓ Architecture content generated
```

```
TEST 4.3: Complete Phase 2 Cycle
─────────────────────────────────────
Actions:
  1. Create tech spec
  2. /gate-check → READY
  3. /phase-approve → "approve"
  4. /phase-advance → Phase 3
Expected:
  ✓ All steps complete
  ✓ Now in Phase 3
```

---

### Test Suite 5: Phase 3 (Breakdown)

```
TEST 5.1: Block Code in Phase 3
─────────────────────────────────────
Current Phase: 3 (Breakdown)
Action: Request "write the user model"
Expected:
  ✗ BLOCKED
```

```
TEST 5.2: Allow Jira Work in Phase 3
─────────────────────────────────────
Current Phase: 3 (Breakdown)
Action: Request "create Jira epics and stories"
Expected:
  ✓ ALLOWED
```

```
TEST 5.3: Complete Phase 3 Cycle
─────────────────────────────────────
Actions:
  1. Create Jira breakdown
  2. /gate-check → READY
  3. /phase-approve → "approve"  
  4. /phase-advance → Phase 4
Expected:
  ✓ Now in Phase 4 (Development)
```

---

### Test Suite 6: Phase 4 (Development)

```
TEST 6.1: Allow Code in Phase 4
─────────────────────────────────────
Current Phase: 4 (Development)
Action: Request "create Button component"
Expected:
  ✓ ALLOWED
  ✓ Code generated
```

```
TEST 6.2: Block Deployment in Phase 4
─────────────────────────────────────
Current Phase: 4 (Development)
Action: Request "deploy to production"
Expected:
  ✗ BLOCKED
  ✓ Deployment only in Phase 5
```

---

### Test Suite 7: Context Tracking

```
TEST 7.1: Context Initialization
─────────────────────────────────────
Action: Run /context after /aid-init
Expected:
  ✓ Shows empty context
  ✓ Prompts to set current task
```

```
TEST 7.2: Set Current Task
─────────────────────────────────────
Action: /context-update task PROJ-101
Expected:
  ✓ context.json updated
  ✓ current task = PROJ-101
```

```
TEST 7.3: Update Step Progress
─────────────────────────────────────
Action: /context-update progress 50%
Expected:
  ✓ context.json shows progress: "50%"
```

```
TEST 7.4: Complete Step
─────────────────────────────────────
Action: /context-update step done
Expected:
  ✓ Previous step marked done
  ✓ Current step shifted to next
  ✓ Session log updated
```

```
TEST 7.5: Task Completion
─────────────────────────────────────
Action: /context-update task done
Expected:
  ✓ Task marked complete
  ✓ Tasks shifted (current → previous)
  ✓ Next task becomes current
```

---

### Test Suite 8: Morning Startup

```
TEST 8.1: Good Morning - Fresh Start
─────────────────────────────────────
State: No context.json
Action: Run /good-morning
Expected:
  ✓ Infrastructure checks shown
  ✓ Prompts to set up context
```

```
TEST 8.2: Good Morning - With Context
─────────────────────────────────────
State: Existing context with task at 50%
Action: Run /good-morning
Expected:
  ✓ Shows previous/current/next tasks
  ✓ Shows current step progress
  ✓ Shows "where you left off"
  ✓ Prompts to continue
```

---

### Test Suite 9: Full Workflow E2E

```
TEST 9.0: Complete Development Cycle
─────────────────────────────────────
Simulate full project from start to finish:

1. /aid-init
   → Phase 1 active

2. "Create PRD for todo app"
   → PRD generated

3. /gate-check
   → Ready

4. /phase-approve → "approve"
   → Approved

5. /phase-advance
   → Phase 2

6. "Design architecture for todo app"
   → Tech spec generated

7. Try "write the code"
   → BLOCKED ✗

8. /gate-check → /phase-approve → /phase-advance
   → Phase 3

9. "Create Jira breakdown"
   → Issues created

10. Try "implement feature"
    → BLOCKED ✗

11. /gate-check → /phase-approve → /phase-advance
    → Phase 4

12. "Create TodoItem component"
    → ALLOWED ✓
    → Code generated

13. /context-update task PROJ-101
14. /context-update progress 100%
15. /context-update step done

16. /gate-check → /phase-approve → /phase-advance
    → Phase 5

17. "Deploy to production"
    → ALLOWED ✓

RESULT: Full cycle complete
```

---

## Test Execution Script

```bash
#!/bin/bash
# test-aid-methodology.sh

echo "═══════════════════════════════════════════════════════════════"
echo "           AID METHODOLOGY TEST SUITE"
echo "═══════════════════════════════════════════════════════════════"

PROJECT_DIR="/tmp/aid-test-project"
RESULTS_FILE="/tmp/aid-test-results.md"

# Setup
rm -rf "$PROJECT_DIR"
mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"

# Initialize
echo "TEST 1: Initialize project..."
# Run /aid-init equivalent

# Phase 1 Tests
echo "TEST 2: Phase gate enforcement..."
# Try blocked actions

# Continue with all tests...

echo "═══════════════════════════════════════════════════════════════"
echo "           TEST RESULTS"
echo "═══════════════════════════════════════════════════════════════"
cat "$RESULTS_FILE"
```

---

## Expected Test Results Format

```markdown
# AID Test Results

Run: 2025-12-10 10:30:00
Duration: 5 minutes

## Summary
- Total Tests: 25
- Passed: 24 ✓
- Failed: 1 ✗
- Skipped: 0

## Results by Suite

### Suite 1: Installation ✓
- TEST 1.1: Clone and Verify ✓
- TEST 1.2: Initialize Project ✓

### Suite 2: Phase Gates ✓
- TEST 2.1: Block Code in Phase 1 ✓
- TEST 2.2: Block Architecture in Phase 1 ✓
- TEST 2.3: Block Jira in Phase 1 ✓
- TEST 2.4: Allow PRD in Phase 1 ✓

### Suite 3: Phase Progression ✓
- TEST 3.1: Gate Check Not Ready ✓
- TEST 3.2: Gate Check Ready ✓
- TEST 3.3: Advance Without Approval ✓
- TEST 3.4: Human Approval ✓
- TEST 3.5: Advance After Approval ✓

... (etc)

## Failed Tests

### TEST X.X: [Name]
- Expected: ...
- Actual: ...
- Error: ...
```

---

## Running the Tests

### Option 1: Manual (in Claude Code)
```
/aid-test-suite
```

### Option 2: Automated Script
```bash
./scripts/test-methodology.sh
```

### Option 3: CI/CD Integration
```yaml
# .github/workflows/test-aid.yml
name: Test AID Methodology
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run AID Tests
        run: ./scripts/test-methodology.sh
```
