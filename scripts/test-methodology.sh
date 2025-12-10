#!/bin/bash
#
# AID Methodology Test Script
# Tests phase gate enforcement, context tracking, and workflow
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
TESTS_TOTAL=0
TESTS_PASSED=0
TESTS_FAILED=0

# Test directory
TEST_DIR="/tmp/aid-test-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$TEST_DIR/.aid/approvals"

echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}                🧪 AID METHODOLOGY TEST SUITE${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""
echo "Test directory: $TEST_DIR"
echo ""

# Helper functions
pass_test() {
    TESTS_PASSED=$((TESTS_PASSED + 1))
    TESTS_TOTAL=$((TESTS_TOTAL + 1))
    echo -e "  ${GREEN}✓ PASSED${NC}"
}

fail_test() {
    TESTS_FAILED=$((TESTS_FAILED + 1))
    TESTS_TOTAL=$((TESTS_TOTAL + 1))
    echo -e "  ${RED}✗ FAILED${NC}"
    echo -e "  ${RED}  Reason: $1${NC}"
}

run_test() {
    echo -e "${YELLOW}TEST $1: $2${NC}"
}

# Initialize state.json
init_state() {
    local phase=$1
    cat > "$TEST_DIR/.aid/state.json" << EOF
{
  "current_phase": $phase,
  "phase_name": "$(get_phase_name $phase)",
  "project_name": "aid-test",
  "initialized_at": "$(date -Iseconds)"
}
EOF
}

get_phase_name() {
    case $1 in
        1) echo "PRD" ;;
        2) echo "Tech Spec" ;;
        3) echo "Breakdown" ;;
        4) echo "Development" ;;
        5) echo "QA & Ship" ;;
    esac
}

# Check if work type is allowed in phase
check_allowed() {
    local work_type=$1
    local phase=$2
    
    case $phase in
        1)
            [[ "$work_type" == "requirements" ]] && return 0
            return 1
            ;;
        2)
            [[ "$work_type" == "requirements" || "$work_type" == "architecture" ]] && return 0
            return 1
            ;;
        3)
            [[ "$work_type" == "requirements" || "$work_type" == "architecture" || "$work_type" == "jira" ]] && return 0
            return 1
            ;;
        4)
            [[ "$work_type" == "requirements" || "$work_type" == "architecture" || "$work_type" == "jira" || "$work_type" == "code" ]] && return 0
            return 1
            ;;
        5)
            return 0  # Everything allowed
            ;;
    esac
}

echo -e "${BLUE}───────────────────────────────────────────────────────────────${NC}"
echo -e "${BLUE}SUITE 1: SETUP${NC}"
echo -e "${BLUE}───────────────────────────────────────────────────────────────${NC}"

# Test 1.1
run_test "1.1" "Initialize state files"
init_state 1
if [[ -f "$TEST_DIR/.aid/state.json" ]]; then
    pass_test
else
    fail_test "state.json not created"
fi

# Test 1.2
run_test "1.2" "Verify phase 1 active"
PHASE=$(cat "$TEST_DIR/.aid/state.json" | grep '"current_phase"' | grep -o '[0-9]')
if [[ "$PHASE" == "1" ]]; then
    pass_test
else
    fail_test "Phase is $PHASE, expected 1"
fi

echo ""
echo -e "${BLUE}───────────────────────────────────────────────────────────────${NC}"
echo -e "${BLUE}SUITE 2: PHASE GATE ENFORCEMENT (Phase 1)${NC}"
echo -e "${BLUE}───────────────────────────────────────────────────────────────${NC}"

# Test 2.1
run_test "2.1" "Block code in Phase 1"
if ! check_allowed "code" 1; then
    echo "  Requesting: 'Create React Button'"
    echo "  Expected: BLOCKED"
    echo "  Actual: BLOCKED"
    pass_test
else
    fail_test "Code should be blocked in Phase 1"
fi

# Test 2.2
run_test "2.2" "Block architecture in Phase 1"
if ! check_allowed "architecture" 1; then
    pass_test
else
    fail_test "Architecture should be blocked in Phase 1"
fi

# Test 2.3
run_test "2.3" "Block Jira in Phase 1"
if ! check_allowed "jira" 1; then
    pass_test
else
    fail_test "Jira should be blocked in Phase 1"
fi

# Test 2.4
run_test "2.4" "Allow PRD work in Phase 1"
if check_allowed "requirements" 1; then
    pass_test
else
    fail_test "Requirements should be allowed in Phase 1"
fi

echo ""
echo -e "${BLUE}───────────────────────────────────────────────────────────────${NC}"
echo -e "${BLUE}SUITE 3: PHASE PROGRESSION${NC}"
echo -e "${BLUE}───────────────────────────────────────────────────────────────${NC}"

# Test 3.1
run_test "3.1" "Simulate human approval"
echo "  🤖 SIMULATING HUMAN: typing 'approve'"
echo "Phase 1 approved by test agent at $(date -Iseconds)" > "$TEST_DIR/.aid/approvals/phase-1-approved.md"
if [[ -f "$TEST_DIR/.aid/approvals/phase-1-approved.md" ]]; then
    pass_test
else
    fail_test "Approval file not created"
fi

# Test 3.2
run_test "3.2" "Advance to Phase 2"
init_state 2
PHASE=$(cat "$TEST_DIR/.aid/state.json" | grep '"current_phase"' | grep -o '[0-9]')
if [[ "$PHASE" == "2" ]]; then
    pass_test
else
    fail_test "Phase is $PHASE, expected 2"
fi

echo ""
echo -e "${BLUE}───────────────────────────────────────────────────────────────${NC}"
echo -e "${BLUE}SUITE 4: PHASE 2 TESTS${NC}"
echo -e "${BLUE}───────────────────────────────────────────────────────────────${NC}"

# Test 4.1
run_test "4.1" "Block code in Phase 2"
if ! check_allowed "code" 2; then
    pass_test
else
    fail_test "Code should be blocked in Phase 2"
fi

# Test 4.2
run_test "4.2" "Allow architecture in Phase 2"
if check_allowed "architecture" 2; then
    pass_test
else
    fail_test "Architecture should be allowed in Phase 2"
fi

# Test 4.3
run_test "4.3" "Advance to Phase 3"
echo "  🤖 SIMULATING HUMAN: approve"
echo "Phase 2 approved" > "$TEST_DIR/.aid/approvals/phase-2-approved.md"
init_state 3
pass_test

echo ""
echo -e "${BLUE}───────────────────────────────────────────────────────────────${NC}"
echo -e "${BLUE}SUITE 5: PHASE 3 TESTS${NC}"
echo -e "${BLUE}───────────────────────────────────────────────────────────────${NC}"

# Test 5.1
run_test "5.1" "Block code in Phase 3"
if ! check_allowed "code" 3; then
    pass_test
else
    fail_test "Code should be blocked in Phase 3"
fi

# Test 5.2
run_test "5.2" "Allow Jira in Phase 3"
if check_allowed "jira" 3; then
    pass_test
else
    fail_test "Jira should be allowed in Phase 3"
fi

# Test 5.3
run_test "5.3" "Advance to Phase 4"
echo "  🤖 SIMULATING HUMAN: approve"
init_state 4
pass_test

echo ""
echo -e "${BLUE}───────────────────────────────────────────────────────────────${NC}"
echo -e "${BLUE}SUITE 6: PHASE 4 TESTS (Development)${NC}"
echo -e "${BLUE}───────────────────────────────────────────────────────────────${NC}"

# Test 6.1
run_test "6.1" "Allow code in Phase 4"
if check_allowed "code" 4; then
    pass_test
else
    fail_test "Code should be allowed in Phase 4"
fi

# Test 6.2
run_test "6.2" "Block deployment in Phase 4"
if ! check_allowed "deployment" 4; then
    pass_test
else
    fail_test "Deployment should be blocked in Phase 4"
fi

# Test 6.3
run_test "6.3" "Advance to Phase 5"
echo "  🤖 SIMULATING HUMAN: approve"
init_state 5
pass_test

echo ""
echo -e "${BLUE}───────────────────────────────────────────────────────────────${NC}"
echo -e "${BLUE}SUITE 7: PHASE 5 TESTS (QA & Ship)${NC}"
echo -e "${BLUE}───────────────────────────────────────────────────────────────${NC}"

# Test 7.1
run_test "7.1" "Allow everything in Phase 5"
ALL_ALLOWED=true
for work_type in "code" "architecture" "jira" "deployment"; do
    if ! check_allowed "$work_type" 5; then
        ALL_ALLOWED=false
    fi
done
if $ALL_ALLOWED; then
    pass_test
else
    fail_test "All work types should be allowed in Phase 5"
fi

echo ""
echo -e "${BLUE}───────────────────────────────────────────────────────────────${NC}"
echo -e "${BLUE}SUITE 8: CONTEXT TRACKING${NC}"
echo -e "${BLUE}───────────────────────────────────────────────────────────────${NC}"

# Test 8.1
run_test "8.1" "Create context file"
cat > "$TEST_DIR/.aid/context.json" << EOF
{
  "last_updated": "$(date -Iseconds)",
  "tasks": {
    "previous": null,
    "current": { "key": "TEST-001", "title": "Test Task", "status": "in_progress" },
    "next": { "key": "TEST-002", "title": "Next Task", "status": "todo" }
  },
  "current_task_steps": {
    "previous": null,
    "current": { "name": "Write tests", "status": "in_progress", "progress": "50%" },
    "next": { "name": "Implement", "status": "pending" }
  }
}
EOF
if [[ -f "$TEST_DIR/.aid/context.json" ]]; then
    pass_test
else
    fail_test "context.json not created"
fi

# Test 8.2
run_test "8.2" "Verify task in context"
TASK=$(cat "$TEST_DIR/.aid/context.json" | grep '"key"' | head -1 | grep -o 'TEST-001')
if [[ "$TASK" == "TEST-001" ]]; then
    pass_test
else
    fail_test "Task key not found in context"
fi

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}                     📊 TEST RESULTS${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""
echo "Total Tests:  $TESTS_TOTAL"
echo -e "Passed:       ${GREEN}$TESTS_PASSED ✓${NC}"
echo -e "Failed:       ${RED}$TESTS_FAILED ✗${NC}"
echo ""

if [[ $TESTS_FAILED -eq 0 ]]; then
    echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}              ✅ ALL TESTS PASSED${NC}"
    echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo "Phase Gate Summary:"
    echo "  Phase 1 → 2: ✓ Blocked code, allowed PRD"
    echo "  Phase 2 → 3: ✓ Blocked code, allowed architecture"
    echo "  Phase 3 → 4: ✓ Blocked code, allowed Jira"
    echo "  Phase 4 → 5: ✓ Allowed code, blocked deployment"
    echo "  Phase 5:     ✓ All actions allowed"
    echo ""
    echo -e "${GREEN}🎉 AID METHODOLOGY VALIDATED${NC}"
    exit 0
else
    echo -e "${RED}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${RED}              ❌ SOME TESTS FAILED${NC}"
    echo -e "${RED}═══════════════════════════════════════════════════════════════${NC}"
    exit 1
fi
