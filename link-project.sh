#!/bin/bash

#============================================
# AID - Link Project Script
# Links an external project to AID methodology
# For macOS/Linux
#============================================

echo ""
echo "========================================"
echo "   AID Project Linker (macOS/Linux)"
echo "========================================"
echo ""

# Get AID path (where this script is located)
AID_PATH="$(cd "$(dirname "$0")" && pwd)"

echo "AID Installation: $AID_PATH"
echo ""

# Get target project path
if [ -z "$1" ]; then
    read -p "Enter project path to link: " TARGET_PATH
else
    TARGET_PATH="$1"
fi

# Remove trailing slash if present
TARGET_PATH="${TARGET_PATH%/}"

# Expand ~ to home directory
TARGET_PATH="${TARGET_PATH/#\~/$HOME}"

echo "Target Project:   $TARGET_PATH"
echo ""

# Verify target exists
if [ ! -d "$TARGET_PATH" ]; then
    echo "[ERROR] Target folder does not exist: $TARGET_PATH"
    exit 1
fi

# Create .claude directory
echo "Creating .claude directory..."
mkdir -p "$TARGET_PATH/.claude"

# Create symbolic links
echo ""
echo "Creating symbolic links..."

# Link commands
if [ -e "$TARGET_PATH/.claude/commands" ]; then
    echo "  [SKIP] commands already exists"
else
    if ln -s "$AID_PATH/.claude/commands" "$TARGET_PATH/.claude/commands" 2>/dev/null; then
        echo "  [OK] .claude/commands linked"
    else
        echo "  [FALLBACK] Copying commands instead..."
        cp -r "$AID_PATH/.claude/commands" "$TARGET_PATH/.claude/commands"
        echo "  [OK] .claude/commands copied"
    fi
fi

# Link skills
if [ -e "$TARGET_PATH/.claude/skills" ]; then
    echo "  [SKIP] skills already exists"
else
    if ln -s "$AID_PATH/.claude/skills" "$TARGET_PATH/.claude/skills" 2>/dev/null; then
        echo "  [OK] .claude/skills linked"
    else
        echo "  [FALLBACK] Copying skills instead..."
        cp -r "$AID_PATH/.claude/skills" "$TARGET_PATH/.claude/skills"
        echo "  [OK] .claude/skills copied"
    fi
fi

# Create .aid directory
echo ""
echo "Creating project state directory..."
mkdir -p "$TARGET_PATH/.aid"

CURRENT_DATE=$(date '+%Y-%m-%d %H:%M:%S')

# Create state.json
if [ ! -f "$TARGET_PATH/.aid/state.json" ]; then
    cat > "$TARGET_PATH/.aid/state.json" << EOF
{
  "\$schema": "aid-state-v1",
  "version": "1.0",
  "initialized_at": "$CURRENT_DATE",
  "last_updated": "$CURRENT_DATE",
  "current_phase": 1,
  "phase_name": "PRD",
  "phase_approved": false,
  "current_session": {
    "active": false,
    "role": null,
    "phase": null,
    "started_at": null,
    "revision_count": 0
  },
  "last_session": {
    "role": null,
    "phase": null,
    "completed_at": null
  },
  "statistics": {
    "total_sessions": 0,
    "total_feedback_collected": 0,
    "pending_feedback_count": 0,
    "last_improvement_run": null,
    "sessions_since_last_improvement": 0
  },
  "notifications": {
    "improvement_suggested": false,
    "reason": null
  }
}
EOF
    echo "[OK] state.json created"
else
    echo "[SKIP] state.json already exists"
fi

# Create context.json
if [ ! -f "$TARGET_PATH/.aid/context.json" ]; then
    cat > "$TARGET_PATH/.aid/context.json" << EOF
{
  "\$schema": "aid-context-v1",
  "version": "1.0",
  "last_updated": "$CURRENT_DATE",
  "current_task": null,
  "current_step": null,
  "progress": {
    "steps_completed": [],
    "steps_pending": []
  },
  "session_notes": [],
  "blockers": []
}
EOF
    echo "[OK] context.json created"
else
    echo "[SKIP] context.json already exists"
fi

# Copy .mcp.json (prefer configured one over template)
echo ""
echo "Copying MCP configuration..."
if [ ! -f "$TARGET_PATH/.mcp.json" ]; then
    if [ -f "$AID_PATH/.mcp.json" ]; then
        cp "$AID_PATH/.mcp.json" "$TARGET_PATH/.mcp.json"
        echo "[OK] .mcp.json copied (with your API tokens)"
    elif [ -f "$AID_PATH/.mcp.json.example" ]; then
        cp "$AID_PATH/.mcp.json.example" "$TARGET_PATH/.mcp.json"
        echo "[OK] .mcp.json created (edit with your API tokens)"
    else
        echo "[WARNING] .mcp.json not found"
    fi
else
    echo "[SKIP] .mcp.json already exists"
fi

# Copy CLAUDE.md
echo ""
echo "Copying CLAUDE.md..."
if [ ! -f "$TARGET_PATH/CLAUDE.md" ]; then
    if [ -f "$AID_PATH/CLAUDE.md" ]; then
        cp "$AID_PATH/CLAUDE.md" "$TARGET_PATH/CLAUDE.md"
        echo "[OK] CLAUDE.md copied"
    fi
else
    echo "[SKIP] CLAUDE.md already exists"
fi

echo ""
echo "========================================"
echo "   Project Linked Successfully!"
echo "========================================"
echo ""
echo "Target: $TARGET_PATH"
echo ""
echo "Next steps:"
echo ""
echo "1. Edit $TARGET_PATH/.mcp.json with your API tokens"
echo ""
echo "2. Open Claude Code in the project:"
echo "   cd \"$TARGET_PATH\""
echo "   claude"
echo ""
echo "3. Run /aid-start to begin working"
echo ""
echo "========================================"
echo ""
