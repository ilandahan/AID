#!/bin/bash

#============================================
# AID - Link Project Script
# Creates symbolic links from project to AID
# Usage: ./link-project.sh [path] [--force|-f]
# NOTE: Symbolic links auto-update when AID changes
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

# Parse arguments
FORCE_MODE=0
TARGET_PATH=""

for arg in "$@"; do
    case "$arg" in
        --force|-f)
            FORCE_MODE=1
            ;;
        *)
            if [ -z "$TARGET_PATH" ]; then
                TARGET_PATH="$arg"
            fi
            ;;
    esac
done

# Get target project path if not provided
if [ -z "$TARGET_PATH" ]; then
    read -p "Enter project path to link: " TARGET_PATH
fi

# Remove trailing slash if present
TARGET_PATH="${TARGET_PATH%/}"

# Expand ~ to home directory
TARGET_PATH="${TARGET_PATH/#\~/$HOME}"

echo "Target Project:   $TARGET_PATH"
if [ "$FORCE_MODE" -eq 1 ]; then
    echo "Mode:             FORCE (will recreate links)"
fi
echo ""

# Verify target exists
if [ ! -d "$TARGET_PATH" ]; then
    echo "[ERROR] Target folder does not exist: $TARGET_PATH"
    exit 1
fi

# Check for existing links and ask to update
if [ "$FORCE_MODE" -eq 0 ] && [ -e "$TARGET_PATH/.claude" ]; then
    echo "Existing .claude folder detected."
    echo "  [Y] Yes, recreate symbolic links"
    echo "  [N] No, keep existing"
    echo ""
    read -p "Your choice (Y/N): " UPDATE_CHOICE
    if [[ "$UPDATE_CHOICE" =~ ^[Yy]$ ]]; then
        FORCE_MODE=1
    fi
    echo ""
fi

#============================================
# Create .claude directory
#============================================
echo "Creating .claude directory..."
mkdir -p "$TARGET_PATH/.claude"

#============================================
# Create symbolic links for shared content
#============================================
echo ""
echo "Creating symbolic links to AID..."
echo "(Changes in AID will automatically apply to this project)"
echo ""

# Function to create symlink for a directory
create_dir_symlink() {
    local name="$1"
    local source="$AID_PATH/.claude/$name"
    local target="$TARGET_PATH/.claude/$name"

    # Remove old if force mode
    if [ "$FORCE_MODE" -eq 1 ] && [ -e "$target" ]; then
        rm -rf "$target"
    fi

    # Create symlink if doesn't exist
    if [ ! -e "$target" ]; then
        if ln -s "$source" "$target" 2>/dev/null; then
            echo "  [LINK] .claude/$name -> AID"
        else
            echo "  [ERROR] Failed to create symlink for $name"
        fi
    else
        echo "  [SKIP] $name already exists"
    fi
}

# Create symlinks for directories
create_dir_symlink "commands"
create_dir_symlink "skills"
create_dir_symlink "agents"
create_dir_symlink "references"
create_dir_symlink "rules"

#============================================
# Create symlink for CLAUDE.md
#============================================
echo ""
echo "Creating CLAUDE.md symlink..."
if [ "$FORCE_MODE" -eq 1 ] && [ -e "$TARGET_PATH/CLAUDE.md" ]; then
    rm -f "$TARGET_PATH/CLAUDE.md"
fi

if [ ! -e "$TARGET_PATH/CLAUDE.md" ]; then
    if ln -s "$AID_PATH/CLAUDE.md" "$TARGET_PATH/CLAUDE.md" 2>/dev/null; then
        echo "  [LINK] CLAUDE.md -> AID"
    else
        echo "  [ERROR] Failed to create symlink for CLAUDE.md"
    fi
else
    echo "  [SKIP] CLAUDE.md already exists"
fi

#============================================
# Copy project-specific files (not linked)
#============================================
echo ""
echo "Copying project-specific files..."

# Copy settings.json template (project may customize)
if [ ! -f "$TARGET_PATH/.claude/settings.json" ]; then
    if [ -f "$AID_PATH/.claude/settings.json" ]; then
        cp "$AID_PATH/.claude/settings.json" "$TARGET_PATH/.claude/settings.json"
        echo "  [COPY] .claude/settings.json (customize as needed)"
    fi
else
    echo "  [SKIP] settings.json already exists"
fi

#============================================
# Create .aid directory structure
#============================================
echo ""
echo "Creating project state directory..."
mkdir -p "$TARGET_PATH/.aid"
mkdir -p "$TARGET_PATH/.aid/qa"

CURRENT_DATE=$(date '+%Y-%m-%d %H:%M:%S')

# Create state.json if doesn't exist
if [ ! -f "$TARGET_PATH/.aid/state.json" ]; then
    cat > "$TARGET_PATH/.aid/state.json" << EOF
{
  "\$schema": "aid-state-v1",
  "version": "1.0",
  "initialized_at": "$CURRENT_DATE",
  "last_updated": "$CURRENT_DATE",
  "current_phase": 0,
  "phase_name": "Discovery",
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
    echo "  [OK] state.json created"
else
    echo "  [SKIP] state.json already exists"
fi

# Create context.json if doesn't exist
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
    echo "  [OK] context.json created"
else
    echo "  [SKIP] context.json already exists"
fi

#============================================
# Create docs directory structure
#============================================
echo ""
echo "Creating docs directories (phase outputs)..."
mkdir -p "$TARGET_PATH/docs/research"
mkdir -p "$TARGET_PATH/docs/prd"
mkdir -p "$TARGET_PATH/docs/tech-spec"
mkdir -p "$TARGET_PATH/docs/implementation-plan"
echo "  [OK] docs/ structure created"

#============================================
# Copy .mcp.json template
#============================================
echo ""
echo "Copying MCP configuration..."
if [ ! -f "$TARGET_PATH/.mcp.json" ]; then
    if [ -f "$AID_PATH/.mcp.json.mac" ]; then
        cp "$AID_PATH/.mcp.json.mac" "$TARGET_PATH/.mcp.json"
        echo "  [COPY] .mcp.json (edit with your API tokens)"
    else
        echo "  [ERROR] .mcp.json.mac template not found"
    fi
else
    echo "  [SKIP] .mcp.json already exists (preserving your tokens)"
fi

#============================================
# Summary
#============================================
echo ""
echo "========================================"
echo "   Project Linked Successfully"
echo "========================================"
echo ""
echo "Target: $TARGET_PATH"
echo ""
echo "Symbolic links (auto-update from AID):"
echo "  .claude/commands/   -> AID"
echo "  .claude/skills/     -> AID"
echo "  .claude/agents/     -> AID"
echo "  .claude/references/ -> AID"
echo "  .claude/rules/      -> AID"
echo "  CLAUDE.md           -> AID"
echo ""
echo "Project-specific (copied):"
echo "  .claude/settings.json - Permissions"
echo "  .aid/state.json       - Phase tracking"
echo "  .aid/context.json     - Work context"
echo "  .mcp.json             - MCP config (your tokens)"
echo "  docs/                 - Phase outputs"
echo ""
echo "Next steps:"
echo ""
echo "1. Edit \"$TARGET_PATH/.mcp.json\" with your API tokens"
echo ""
echo "2. Open Claude Code in the project:"
echo "   cd \"$TARGET_PATH\""
echo "   claude"
echo ""
echo "3. Run /aid-start to begin working"
echo ""
echo "========================================"
echo ""
