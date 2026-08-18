#!/usr/bin/env bash
# =============================================================================
# check-file-size.sh
# 
# Enforce the 300-line rule: Find code files that exceed size limits.
# Use in CI or pre-commit hooks to prevent large files.
#
# @see role-developer.md - Development Constraints section
# =============================================================================

set -e

# Colors
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

# =============================================================================
# CONFIGURATION
# =============================================================================

WARNING_THRESHOLD=${WARNING_THRESHOLD:-200}
ERROR_THRESHOLD=${ERROR_THRESHOLD:-400}
EXTENSIONS=${EXTENSIONS:-"ts,tsx,js,jsx,py,rb,go,java,cs,cpp,c,h"}

# Directories to exclude
EXCLUDE_DIRS="node_modules,dist,build,.git,coverage,vendor,__pycache__"

# =============================================================================
# USAGE
# =============================================================================

usage() {
    echo "Usage: $0 [directory] [options]"
    echo ""
    echo "Arguments:"
    echo "  directory    Directory to scan (default: current directory)"
    echo ""
    echo "Options:"
    echo "  --warn N     Warning threshold (default: 200 lines)"
    echo "  --error N    Error threshold (default: 400 lines)"
    echo "  --ext LIST   Comma-separated extensions (default: ts,tsx,js,jsx,py,rb,go,java)"
    echo "  --ci         Exit with error code if any file exceeds error threshold"
    echo "  --fix        Show suggested splits for large files"
    echo ""
    echo "Examples:"
    echo "  $0 src/"
    echo "  $0 --warn 150 --error 300"
    echo "  $0 src/ --ci"
    echo ""
    exit 1
}

# =============================================================================
# PARSE ARGUMENTS
# =============================================================================

SCAN_DIR="."
CI_MODE=false
SHOW_FIX=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --warn)
            WARNING_THRESHOLD="$2"
            shift 2
            ;;
        --error)
            ERROR_THRESHOLD="$2"
            shift 2
            ;;
        --ext)
            EXTENSIONS="$2"
            shift 2
            ;;
        --ci)
            CI_MODE=true
            shift
            ;;
        --fix)
            SHOW_FIX=true
            shift
            ;;
        --help|-h)
            usage
            ;;
        *)
            SCAN_DIR="$1"
            shift
            ;;
    esac
done

# =============================================================================
# BUILD FIND COMMAND
# =============================================================================

# Convert extensions to find pattern
EXT_PATTERN=""
IFS=',' read -ra EXT_ARRAY <<< "$EXTENSIONS"
for ext in "${EXT_ARRAY[@]}"; do
    if [ -n "$EXT_PATTERN" ]; then
        EXT_PATTERN="$EXT_PATTERN -o"
    fi
    EXT_PATTERN="$EXT_PATTERN -name \"*.$ext\""
done

# Convert exclude dirs to find pattern
EXCLUDE_PATTERN=""
IFS=',' read -ra EXCLUDE_ARRAY <<< "$EXCLUDE_DIRS"
for dir in "${EXCLUDE_ARRAY[@]}"; do
    EXCLUDE_PATTERN="$EXCLUDE_PATTERN -path \"*/$dir/*\" -prune -o"
done

# =============================================================================
# SCAN FILES
# =============================================================================

echo -e "${BLUE}📏 Checking file sizes in: ${SCAN_DIR}${NC}"
echo -e "${BLUE}   Warning threshold: ${WARNING_THRESHOLD} lines${NC}"
echo -e "${BLUE}   Error threshold: ${ERROR_THRESHOLD} lines${NC}"
echo ""

ERRORS=0
WARNINGS=0
TOTAL=0

# Create temporary file for results
RESULTS=$(mktemp)

# Find and analyze files
eval "find \"$SCAN_DIR\" $EXCLUDE_PATTERN \( $EXT_PATTERN \) -print" 2>/dev/null | while read -r file; do
    if [ -f "$file" ]; then
        lines=$(wc -l < "$file" | tr -d ' ')
        TOTAL=$((TOTAL + 1))
        
        if [ "$lines" -gt "$ERROR_THRESHOLD" ]; then
            echo -e "${RED}❌ ERROR${NC}  ${lines} lines: $file" >> "$RESULTS"
            echo "ERROR" >> "${RESULTS}.errors"
        elif [ "$lines" -gt "$WARNING_THRESHOLD" ]; then
            echo -e "${YELLOW}⚠️  WARN${NC}   ${lines} lines: $file" >> "$RESULTS"
            echo "WARN" >> "${RESULTS}.warnings"
        fi
    fi
done

# Display results
if [ -f "$RESULTS" ]; then
    sort -t':' -k2 -rn "$RESULTS" | head -50
    echo ""
fi

# Count issues
ERRORS=0
WARNINGS=0
if [ -f "${RESULTS}.errors" ]; then
    ERRORS=$(wc -l < "${RESULTS}.errors" | tr -d ' ')
fi
if [ -f "${RESULTS}.warnings" ]; then
    WARNINGS=$(wc -l < "${RESULTS}.warnings" | tr -d ' ')
fi

# Cleanup
rm -f "$RESULTS" "${RESULTS}.errors" "${RESULTS}.warnings"

# =============================================================================
# SUMMARY
# =============================================================================

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ "$ERRORS" -gt 0 ]; then
    echo -e "${RED}❌ ${ERRORS} file(s) exceed ${ERROR_THRESHOLD} lines - MUST SPLIT${NC}"
fi

if [ "$WARNINGS" -gt 0 ]; then
    echo -e "${YELLOW}⚠️  ${WARNINGS} file(s) exceed ${WARNING_THRESHOLD} lines - consider splitting${NC}"
fi

if [ "$ERRORS" -eq 0 ] && [ "$WARNINGS" -eq 0 ]; then
    echo -e "${GREEN}✅ All files within size limits${NC}"
fi

# =============================================================================
# FIX SUGGESTIONS
# =============================================================================

if [ "$SHOW_FIX" = true ] && [ "$ERRORS" -gt 0 ]; then
    echo ""
    echo -e "${BLUE}📋 Suggested approach for splitting large files:${NC}"
    echo ""
    echo "1. Identify responsibilities in the file"
    echo "   - Look for class boundaries"
    echo "   - Look for related function groups"
    echo "   - Look for different concerns (validation, logic, data)"
    echo ""
    echo "2. Create focused modules:"
    echo "   feature/"
    echo "   ├── feature.controller.ts   # HTTP layer (thin)"
    echo "   ├── feature.service.ts      # Business logic"
    echo "   ├── feature.repository.ts   # Data access"
    echo "   ├── feature.types.ts        # Types/interfaces"
    echo "   └── feature.validation.ts   # Input validation"
    echo ""
    echo "3. Each module should:"
    echo "   - Have single responsibility"
    echo "   - Be independently testable"
    echo "   - Be under 200 lines ideally"
fi

# =============================================================================
# EXIT CODE
# =============================================================================

if [ "$CI_MODE" = true ] && [ "$ERRORS" -gt 0 ]; then
    echo ""
    echo -e "${RED}CI check failed: ${ERRORS} file(s) exceed size limit${NC}"
    exit 1
fi

exit 0