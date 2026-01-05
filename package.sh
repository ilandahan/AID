#!/bin/bash

#============================================
# AID - Package for Distribution
# Creates a clean copy ready for sharing
# For macOS/Linux
#============================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[OK]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

echo ""
echo "========================================"
echo "   AID Distribution Packager"
echo "========================================"
echo ""

# Get source path (where this script is located)
SOURCE_PATH="$(cd "$(dirname "$0")" && pwd)"

echo "Source: $SOURCE_PATH"
echo ""

# Get destination path
if [ -z "$1" ]; then
    read -p "Enter destination folder: " DEST_PATH
else
    DEST_PATH="$1"
fi

# Expand ~ to home directory
DEST_PATH="${DEST_PATH/#\~/$HOME}"

# Remove trailing slash if present
DEST_PATH="${DEST_PATH%/}"

# Create package name with timestamp
TIMESTAMP=$(date +%Y%m%d)
PACKAGE_NAME="aid-package-$TIMESTAMP"
FULL_DEST="$DEST_PATH/$PACKAGE_NAME"

echo ""
echo "Destination: $FULL_DEST"
echo ""

# Check if destination already exists
if [ -d "$FULL_DEST" ]; then
    log_error "Destination already exists: $FULL_DEST"
    echo "        Please remove it or choose a different location."
    exit 1
fi

# Create destination directory
mkdir -p "$FULL_DEST"

echo "[STEP 1/4] Copying core files..."
echo ""

# Use rsync with exclusions (more reliable than cp for complex exclusions)
if command -v rsync &> /dev/null; then
    rsync -av --progress \
        --exclude='node_modules' \
        --exclude='.aid' \
        --exclude='__pycache__' \
        --exclude='.git' \
        --exclude='.vscode' \
        --exclude='.idea' \
        --exclude='.env' \
        --exclude='.mcp.json' \
        --exclude='*.pyc' \
        --exclude='*.egg-info' \
        --exclude='.DS_Store' \
        --exclude='Thumbs.db' \
        "$SOURCE_PATH/" "$FULL_DEST/"
else
    # Fallback to cp if rsync not available
    log_warning "rsync not found, using cp (less precise exclusions)"
    cp -R "$SOURCE_PATH" "$FULL_DEST"

    # Manual cleanup
    rm -rf "$FULL_DEST/node_modules" 2>/dev/null || true
    rm -rf "$FULL_DEST/.aid" 2>/dev/null || true
    rm -rf "$FULL_DEST/.git" 2>/dev/null || true
    rm -f "$FULL_DEST/.env" 2>/dev/null || true
    rm -f "$FULL_DEST/.mcp.json" 2>/dev/null || true
    find "$FULL_DEST" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find "$FULL_DEST" -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
    find "$FULL_DEST" -name ".DS_Store" -delete 2>/dev/null || true
    find "$FULL_DEST" -name "*.pyc" -delete 2>/dev/null || true
fi

echo ""
echo "[STEP 2/4] Cleaning up Python cache..."

# Remove any __pycache__ that might have slipped through
find "$FULL_DEST" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find "$FULL_DEST" -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true

log_success "Python cache cleaned"

echo ""
echo "[STEP 3/4] Verifying essential files..."

MISSING=0

# Check for essential files
check_file() {
    if [ ! -e "$FULL_DEST/$1" ]; then
        echo "  [MISSING] $1"
        MISSING=1
    fi
}

check_file "install.bat"
check_file "install.sh"
check_file ".mcp.json.windows"
check_file ".mcp.json.mac"
check_file ".env.example"
check_file "CLAUDE.md"
check_file "memory-system/pyproject.toml"
check_file "memory-system/memory_system/__init__.py"
check_file "skills"

if [ "$MISSING" -eq 0 ]; then
    log_success "All essential files present"
else
    echo ""
    log_warning "Some files are missing - package may be incomplete"
fi

echo ""
echo "[STEP 4/4] Calculating package size..."

# Count files and size
FILE_COUNT=$(find "$FULL_DEST" -type f | wc -l | tr -d ' ')
SIZE=$(du -sh "$FULL_DEST" | cut -f1)

echo ""
echo "========================================"
echo "   Package Created Successfully!"
echo "========================================"
echo ""
echo "Location: $FULL_DEST"
echo "Files:    $FILE_COUNT"
echo "Size:     $SIZE"
echo ""
echo "Package contents:"
echo "  - install.bat / install.sh (installers)"
echo "  - link-project.bat / link-project.sh (project linkers)"
echo "  - .mcp.json.windows / .mcp.json.mac (MCP templates)"
echo "  - .env.example (environment template)"
echo "  - skills/ (20 AID skills)"
echo "  - memory-system/ (learning system)"
echo "  - CLAUDE.md (project instructions)"
echo ""
echo "----------------------------------------"
echo ""
echo "To use on another machine:"
echo ""
echo "  1. Copy $PACKAGE_NAME folder to target machine"
echo "  2. Open terminal in that folder"
echo "  3. Run: ./install.sh (Mac) or install.bat (Windows)"
echo "  4. Edit .mcp.json with your API tokens"
echo "  5. Run: claude"
echo "  6. Type: /aid-start"
echo ""
echo "========================================"
echo ""
