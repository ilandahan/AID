#!/bin/bash

#============================================
# AID - Link Project Script
# Creates symbolic links from project to AID
# Usage: ./link-project.sh [path] [--force|-f] [--role <name|number>]
# NOTE: Symbolic links auto-update when AID changes
# Needs node (registers the AID hooks, T16 I-9) and python (creates the project state
# through hooks/aid_session.py init, T16 I-10).
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
# The role `aid_session.py init` starts the project with (a name or a menu number).
ROLE="1"

while [ $# -gt 0 ]; do
    case "$1" in
        --force|-f)
            FORCE_MODE=1
            ;;
        --role)
            ROLE="$2"
            shift
            ;;
        --role=*)
            ROLE="${1#--role=}"
            ;;
        *)
            if [ -z "$TARGET_PATH" ]; then
                TARGET_PATH="$1"
            fi
            ;;
    esac
    shift
done

# The role is passed to aid_session.py as one argument and printed in a command line:
# accept only a plain name or number.
case "$ROLE" in
    ""|*[!A-Za-z0-9_-]*)
        echo "[ERROR] --role must be a role name or menu number (letters, digits, _ and -)"
        exit 1
        ;;
esac

# Get target project path if not provided
if [ -z "$TARGET_PATH" ]; then
    read -r -p "Enter project path to link: " TARGET_PATH
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

#============================================
# Refuse destructive targets
# WHY: create_dir_symlink() runs `rm -rf "$target"` in force mode. If the target
# resolves to this AID install, target IS source, so AID deletes its own
# skills/agents/commands/references/rules. If it resolves to $HOME, it wipes the
# user's global ~/.claude content. Compare resolved paths, since "." , "~" and
# symlinked parents all reach the same place by different spellings.
#============================================
TARGET_REAL="$(cd "$TARGET_PATH" && pwd -P)"
AID_REAL="$(cd "$AID_PATH" && pwd -P)"
HOME_REAL="$(cd "$HOME" 2>/dev/null && pwd -P)"

if [ "$TARGET_REAL" = "$AID_REAL" ]; then
    echo "[ERROR] Target is the AID installation itself:"
    echo "        $TARGET_REAL"
    echo ""
    echo "        Linking AID to itself deletes its own skills, agents and commands."
    echo "        Pass a different project folder."
    exit 1
fi

if [ -n "$HOME_REAL" ] && [ "$TARGET_REAL" = "$HOME_REAL" ]; then
    echo "[ERROR] Target is your home directory:"
    echo "        $TARGET_REAL"
    echo ""
    echo "        This would replace your global ~/.claude content with links to AID."
    echo "        Pass a specific project folder instead."
    exit 1
fi

#============================================
# node is required (T16 I-9)
# WHY: the hooks registered in the project's .claude/settings.json run `node`. A project
# linked with gates that cannot run would look protected and not be. Stop before
# anything is written.
#============================================
if ! command -v node >/dev/null 2>&1 || ! node -e "" >/dev/null 2>&1; then
    echo "[ERROR] node was not found on PATH."
    echo "        AID's phase gates run with node; install Node.js and run link-project again."
    echo "        Nothing was changed in: $TARGET_PATH"
    exit 1
fi

# Native (C:/...) form of a path for node and python under Git Bash; unchanged elsewhere.
native_path() {
    if command -v cygpath >/dev/null 2>&1; then
        cygpath -m "$1"
    else
        printf '%s\n' "$1"
    fi
}

# Check for existing links and ask to update
if [ "$FORCE_MODE" -eq 0 ] && [ -e "$TARGET_PATH/.claude" ]; then
    echo "Existing .claude folder detected."
    echo "  [Y] Yes, recreate symbolic links"
    echo "  [N] No, keep existing"
    echo ""
    read -r -p "Your choice (Y/N): " UPDATE_CHOICE
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

# T17-40: what was really linked and what was copied, for the summary.
LINKED_ITEMS=""
COPIED_ITEMS=""

# make_link <source> <target> <label>: create a symlink and report what it really is.
# WHY: Git Bash's `ln -s` copies by default (MSYS without winsymlinks) and still exits 0,
# so the old "[LINK]" line was printed for a copy that never sees an AID update. On Git
# Bash a native link is tried first; afterwards `[ -L ]` decides the label.
make_link() {
    local source="$1" target="$2" label="$3"
    case "$(uname -s 2>/dev/null)" in
        MINGW*|MSYS*)
            MSYS="${MSYS:+$MSYS }winsymlinks:nativestrict" ln -s "$source" "$target" 2>/dev/null \
                || ln -s "$source" "$target" 2>/dev/null ;;
        *)
            ln -s "$source" "$target" 2>/dev/null ;;
    esac
    if [ -L "$target" ]; then
        echo "  [LINK] $label -> AID"
        LINKED_ITEMS="$LINKED_ITEMS $label"
    elif [ -e "$target" ]; then
        echo "  [COPY] $label (a copy: AID updates will not reach it; re-run link-project after updating AID)"
        COPIED_ITEMS="$COPIED_ITEMS $label"
    else
        echo "  [ERROR] Failed to create symlink for $label"
    fi
}

# Function to create symlink for a directory
create_dir_symlink() {
    local name="$1"
    # AID's components live at the repository root (commands/, skills/, agents/, ...) so
    # that Claude Code can load this repo as a plugin. The link TARGET is still the
    # project's .claude/<name>, which is where Claude Code looks in a plain project.
    local source="$AID_PATH/$name"
    local target="$TARGET_PATH/.claude/$name"

    # WHY: never delete the target when there is nothing to replace it with.
    # Deleting first and discovering the source is gone is how AID erased its own
    # .claude/skills. Check before destroying, not after.
    if [ ! -d "$source" ]; then
        echo "  [ERROR] Source missing in AID, nothing linked: $name/"
        return 1
    fi

    # Already linked to AID - no work, and no reason to risk a delete.
    if [ -L "$target" ] && [ "$(readlink "$target")" = "$source" ]; then
        echo "  [SKIP] $name already linked to AID"
        LINKED_ITEMS="$LINKED_ITEMS .claude/$name"
        return 0
    fi

    # Remove old if force mode
    if [ "$FORCE_MODE" -eq 1 ] && [ -e "$target" ]; then
        rm -rf "$target"
    fi

    # Create symlink if doesn't exist
    if [ ! -e "$target" ]; then
        make_link "$source" "$target" ".claude/$name"
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
# hooks MUST be linked: the settings.json copied below declares Stop and PostToolUse
# hooks by the path .claude/hooks/*. Without this, a linked project gets a settings
# file pointing at scripts that are not there and every turn end runs a missing file.
create_dir_symlink "hooks"

#============================================
# Create symlink for CLAUDE.md
#============================================
echo ""
echo "Creating CLAUDE.md symlink..."
if [ "$FORCE_MODE" -eq 1 ] && [ -e "$TARGET_PATH/CLAUDE.md" ]; then
    rm -f "$TARGET_PATH/CLAUDE.md"
fi

if [ ! -e "$TARGET_PATH/CLAUDE.md" ]; then
    make_link "$AID_PATH/CLAUDE.md" "$TARGET_PATH/CLAUDE.md" "CLAUDE.md"
else
    echo "  [SKIP] CLAUDE.md already exists"
fi

#============================================
# Copy project-specific files (not linked)
#============================================
echo ""
echo "Copying project-specific files..."

# Register the AID hooks in the project's settings.json (T16 I-9). The ONE generator is
# scripts/link-settings.mjs: it reads .claude-plugin/plugin.json, keeps the user's own keys
# and hooks, and leaves an unparseable file untouched (and fails).
TARGET_NATIVE="$(native_path "$TARGET_REAL")"
AID_NATIVE="$(native_path "$AID_REAL")"
if ! node "$AID_NATIVE/scripts/link-settings.mjs" "$TARGET_NATIVE" "$AID_NATIVE"; then
    echo "  [ERROR] .claude/settings.json was not updated: the AID hooks are NOT registered."
    echo "          Fix the problem above and run link-project again."
    exit 1
fi

#============================================
# Create .aid directory structure
#============================================
echo ""
echo "Creating project state directory..."
mkdir -p "$TARGET_PATH/.aid"
mkdir -p "$TARGET_PATH/.aid/qa"

# The project state is created ONLY by hooks/aid_session.py (T16 I-10, E3): this script
# runs its `init`, with cwd and CLAUDE_PROJECT_DIR = the target, and never writes
# state.json or context.json itself. init also creates .aid/context.json.
INIT_SCRIPT="$AID_NATIVE/hooks/aid_session.py"
if [ -f "$TARGET_PATH/.aid/state.json" ]; then
    echo "  [SKIP] state.json already exists"
else
    PYTHON_CMD=""
    INIT_RC=1
    for cand in python3 python "py -3"; do
        # The Windows Store stub exits 9009 instead of running: only a python that
        # really runs counts. An alias that could not be executed at all (126/127/9009)
        # wrote nothing, so the next candidate is tried.
        $cand -c "import sys" >/dev/null 2>&1 || continue
        PYTHON_CMD="$cand"
        ( cd "$TARGET_PATH" && CLAUDE_PROJECT_DIR="$TARGET_NATIVE" \
              $cand "$INIT_SCRIPT" init "$ROLE" 0 )
        INIT_RC=$?
        case "$INIT_RC" in
            126|127|9009) continue ;;
        esac
        break
    done
    if [ "$INIT_RC" -eq 0 ] && [ -f "$TARGET_PATH/.aid/state.json" ]; then
        echo "  [OK] state.json created by aid_session.py init"
    else
        if [ -z "$PYTHON_CMD" ]; then
            echo "  [WARNING] No working python found (tried python3, python, py -3)."
        else
            echo "  [WARNING] aid_session.py init failed (exit $INIT_RC)."
        fi
        # R1-09: init resolves to the nearest AID root above the target (INV-2) and refuses
        # there, so the printed command would fail the same way. Name that ancestor. A home
        # folder's .aid (the user-level AID_HOME) is not a project and is skipped.
        AID_ANCESTOR=""
        USER_AIDS=" $(native_path "${AID_HOME:-$HOME/.aid}") $(native_path "$HOME/.aid") "
        d="$(dirname "$TARGET_REAL")"
        while :; do
            if [ -f "$d/.aid/state.json" ] || [ -f "$d/.aid/hooks/config.json" ]; then
                d_aid="$(native_path "$d/.aid")"
                case "$USER_AIDS" in
                    *" $d_aid "*) ;;
                    *) AID_ANCESTOR="$(native_path "$d")"; break ;;
                esac
            fi
            p="$(dirname "$d")"
            [ "$p" = "$d" ] && break
            d="$p"
        done
        if [ -n "$AID_ANCESTOR" ]; then
            echo "  [WARNING] The project is inside another AID project: $AID_ANCESTOR"
            echo "  [WARNING] init uses that project's state and refuses; the command below fails"
            echo "            the same way until the project is moved out of $AID_ANCESTOR."
        fi
        echo "  [WARNING] The project state was NOT created. Run this yourself in the project:"
        echo "      cd \"$TARGET_NATIVE\""
        echo "      ${PYTHON_CMD:-python} \"$INIT_SCRIPT\" init $ROLE 0"
    fi
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
        echo "  [COPY] .mcp.json (reads tokens from environment variables)"
    else
        echo "  [ERROR] .mcp.json.mac template not found"
    fi
else
    echo "  [SKIP] .mcp.json already exists (kept; tokens come from environment variables / OS keystore, not this file)"
fi
# .mcp.json is per-user config (keep it out of git even if someone pastes a token into it)
# and .aid/audit/ is the hook audit log. T17 I-26: the one helper, shared with
# link-project.bat, adds a line only when no existing line equals it (a trailing CR, spaces
# and tabs ignored), in the file's own line ending, so any mix of sh/bat runs adds it once.
if ! node "$AID_NATIVE/scripts/ensure-gitignore.mjs" "$TARGET_NATIVE" ".mcp.json" ".aid/audit/"; then
    echo "  [WARNING] .gitignore was not updated: add .mcp.json and .aid/audit/ to it yourself"
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
count_items() { set -- $1; echo $#; }
echo "Symbolic links (auto-update from AID): $(count_items "$LINKED_ITEMS")"
for item in $LINKED_ITEMS; do
    echo "  $item -> AID"
done
if [ -n "$COPIED_ITEMS" ]; then
    echo "Copies (AID updates will NOT reach them; re-run link-project after updating AID): $(count_items "$COPIED_ITEMS")"
    for item in $COPIED_ITEMS; do
        echo "  $item"
    done
    echo "  To get real links on Windows, enable Developer Mode (or run Git Bash as administrator)"
    echo "  and run link-project again, or use link-project.bat (junctions)."
fi
echo ""
echo "Project-specific (not linked):"
echo "  .claude/settings.json - Permissions + AID hooks (phase gates)"
echo "  .aid/state.json       - Phase tracking (aid_session.py init)"
echo "  .aid/context.json     - Work context (aid_session.py init)"
echo "  .mcp.json             - MCP config (tokens come from environment variables / OS keystore, not this file)"
echo "  docs/                 - Phase outputs"
echo ""
echo "Next steps:"
echo ""
echo "1. Export your API tokens as environment variables (see INSTALLATION.md); .mcp.json reads them"
echo ""
echo "2. Open Claude Code in the project:"
echo "   cd \"$TARGET_PATH\""
echo "   claude"
echo ""
echo "3. /aid-start, /aid-status, /phase-approve and /phase-advance need the plugin"
echo "   (claude plugin install aid@AID). Without it, run the session steps yourself"
echo "   (in Claude Code, with a leading !):"
echo "   python \"$AID_PATH/hooks/aid_session.py\" status   (also: start, approve, advance)"
echo ""
echo "========================================"
echo ""
