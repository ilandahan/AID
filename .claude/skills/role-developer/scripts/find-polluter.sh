#!/usr/bin/env bash
# =============================================================================
# find-polluter.sh
# 
# Bisection script to find which test creates unwanted files/state.
# Use when tests pass individually but fail when run together.
#
# @see role-developer.md - Developer Tools section
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# =============================================================================
# USAGE
# =============================================================================

usage() {
    echo "Usage: $0 <file_or_dir_to_check> <test_pattern>"
    echo ""
    echo "Arguments:"
    echo "  file_or_dir_to_check  Path that shouldn't exist (e.g., '.git', 'temp/')"
    echo "  test_pattern          Glob pattern for test files"
    echo ""
    echo "Examples:"
    echo "  $0 '.git' 'src/**/*.test.ts'"
    echo "  $0 'node_modules/.cache' 'tests/*.spec.js'"
    echo "  $0 'coverage' '**/*.test.tsx'"
    echo ""
    echo "What it does:"
    echo "  Runs each test file individually and checks if the pollution"
    echo "  file/directory appears after each test. Reports the first"
    echo "  test that creates the unwanted state."
    exit 1
}

# =============================================================================
# MAIN
# =============================================================================

if [ $# -ne 2 ]; then
    usage
fi

POLLUTION_CHECK="$1"
TEST_PATTERN="$2"

echo -e "${BLUE}🔍 Searching for test that creates: ${POLLUTION_CHECK}${NC}"
echo -e "${BLUE}   Test pattern: ${TEST_PATTERN}${NC}"
echo ""

# Check if pollution already exists
if [ -e "$POLLUTION_CHECK" ]; then
    echo -e "${YELLOW}⚠️  Warning: ${POLLUTION_CHECK} already exists!${NC}"
    echo "   Remove it first to run this script:"
    echo "   rm -rf \"$POLLUTION_CHECK\""
    exit 1
fi

# Get list of test files
TEST_FILES=$(find . -path "$TEST_PATTERN" 2>/dev/null | sort)

if [ -z "$TEST_FILES" ]; then
    echo -e "${RED}❌ No test files found matching: ${TEST_PATTERN}${NC}"
    echo "   Check your pattern and try again."
    exit 1
fi

TOTAL=$(echo "$TEST_FILES" | wc -l | tr -d ' ')
echo -e "${BLUE}Found ${TOTAL} test files${NC}"
echo ""

# =============================================================================
# RUN TESTS
# =============================================================================

COUNT=0
for TEST_FILE in $TEST_FILES; do
    COUNT=$((COUNT + 1))
    
    # Skip if pollution already exists (from previous test)
    if [ -e "$POLLUTION_CHECK" ]; then
        echo -e "${YELLOW}⚠️  Pollution appeared before test ${COUNT}/${TOTAL}${NC}"
        echo "   Previous test was the polluter!"
        break
    fi
    
    # Progress indicator
    printf "[%3d/%3d] Testing: %s" "$COUNT" "$TOTAL" "$TEST_FILE"
    
    # Run the test (suppress output)
    npm test -- "$TEST_FILE" > /dev/null 2>&1 || true
    
    # Check if pollution appeared
    if [ -e "$POLLUTION_CHECK" ]; then
        echo ""
        echo ""
        echo -e "${RED}🎯 FOUND POLLUTER!${NC}"
        echo -e "${RED}   Test: ${TEST_FILE}${NC}"
        echo -e "${RED}   Created: ${POLLUTION_CHECK}${NC}"
        echo ""
        echo "Pollution details:"
        ls -la "$POLLUTION_CHECK"
        echo ""
        echo "To investigate:"
        echo "  npm test -- $TEST_FILE    # Run just this test"
        echo "  cat $TEST_FILE            # Review test code"
        echo ""
        echo "Common causes:"
        echo "  - Missing cleanup in afterEach/afterAll"
        echo "  - Test using real filesystem instead of mock"
        echo "  - Missing test isolation"
        exit 1
    fi
    
    # Clear the line for next test
    printf "\r\033[K"
done

echo ""
echo -e "${GREEN}✅ No polluter found - all ${TOTAL} tests are clean!${NC}"
exit 0