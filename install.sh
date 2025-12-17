#!/bin/bash

#==============================================================================
# AID - AI Development Methodology Installer
# For macOS/Linux
#==============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "[OK] $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Banner
print_banner() {
    echo ""
    echo "========================================"
    echo "   AID Installation Script (macOS/Linux)"
    echo "========================================"
    echo ""
}

# Check prerequisites (simple check like Windows version)
check_prerequisites() {
    # Check Node.js
    if ! command -v node &> /dev/null; then
        log_error "Node.js not found!"
        echo "Please install Node.js 18+ from https://nodejs.org/"
        exit 1
    fi
    log_success "Node.js found"

    # Check npm
    if ! command -v npm &> /dev/null; then
        log_error "npm not found!"
        exit 1
    fi
    log_success "npm found"
}

# Step 1: Install npm dependencies
install_npm_deps() {
    echo ""
    echo "[STEP 1/6] Installing npm dependencies..."
    npm install || log_warning "npm install had issues, continuing..."
}

# Step 2: Setup Claude commands and skills
setup_claude_commands_and_skills() {
    echo ""
    echo "[STEP 2/6] Setting up Claude commands and skills..."

    # Create .claude directories (project level)
    mkdir -p ".claude/commands"
    mkdir -p ".claude/skills"

    # Copy command files
    cp -f memory-system/integration/commands/*.md .claude/commands/ 2>/dev/null || true
    cp -f skills/commands/*.md .claude/commands/ 2>/dev/null || true
    log_success "Commands installed"

    # Copy skills to .claude/skills (project level, like Windows)
    echo "Copying skills..."
    cp -r skills/atomic-design .claude/skills/ 2>/dev/null || true
    cp -r skills/atomic-page-builder .claude/skills/ 2>/dev/null || true
    cp -r skills/code-review .claude/skills/ 2>/dev/null || true
    cp -r skills/context-tracking .claude/skills/ 2>/dev/null || true
    cp -r skills/learning-mode .claude/skills/ 2>/dev/null || true
    cp -r skills/phase-enforcement .claude/skills/ 2>/dev/null || true
    cp -r skills/system-architect .claude/skills/ 2>/dev/null || true
    cp -r skills/test-driven .claude/skills/ 2>/dev/null || true
    log_success "Skills installed"
}

# Step 3: Create project state directory
create_aid_directory() {
    echo ""
    echo "[STEP 3/6] Creating project state directory..."
    mkdir -p ".aid"
}

# Step 4: Create state files
create_state_files() {
    echo "[STEP 4/6] Creating state files..."

    CURRENT_DATE=$(date '+%Y-%m-%d %H:%M:%S')

    # Create state.json
    cat > ".aid/state.json" << EOF
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

    # Create context.json
    cat > ".aid/context.json" << EOF
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

    log_success "State files created"
}

# Step 5: Setup global AID learning system
setup_global_aid() {
    echo ""
    echo "[STEP 5/6] Setting up global AID learning system..."

    AID_HOME="$HOME/.aid"
    mkdir -p "$AID_HOME"
    mkdir -p "$AID_HOME/feedback"
    mkdir -p "$AID_HOME/feedback/pending"
    mkdir -p "$AID_HOME/feedback/processed"
    mkdir -p "$AID_HOME/metrics"
    mkdir -p "$AID_HOME/logs"
    mkdir -p "$AID_HOME/skills"

    # Copy templates to global config
    if [ -f "memory-system/templates/config.yaml" ]; then
        if [ ! -f "$AID_HOME/config.yaml" ]; then
            cp "memory-system/templates/config.yaml" "$AID_HOME/config.yaml"
        fi
    fi
    if [ -f "memory-system/templates/state.json" ]; then
        if [ ! -f "$AID_HOME/state.json" ]; then
            cp "memory-system/templates/state.json" "$AID_HOME/state.json"
        fi
    fi

    log_success "Global learning system initialized at $AID_HOME"
}

# Step 6: Create MCP configuration and .env
setup_mcp_and_env() {
    echo ""
    echo "[STEP 6/6] Creating MCP configuration..."

    # Create .mcp.json if not exists
    if [ ! -f ".mcp.json" ]; then
        if [ -f ".mcp.json.example" ]; then
            cp ".mcp.json.example" ".mcp.json"
            log_success "MCP configuration created from template"
        else
            log_warning ".mcp.json.example not found, skipping MCP config"
        fi
    else
        log_success "MCP configuration already exists"
    fi

    # Create .env if not exists
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            cp ".env.example" ".env"
            log_success "Created .env from template"
        fi
    fi
}

# Bonus: Pre-install MCP servers (optional - for faster startup)
preinstall_mcp_servers() {
    echo ""
    echo "[BONUS] Pre-installing MCP servers (for faster startup)..."
    echo ""
    echo "Downloading MCP server packages..."

    # Create temp directory for npm pack
    TEMP_DIR="${TMPDIR:-/tmp}"

    echo "  - Filesystem server..."
    npm pack @modelcontextprotocol/server-filesystem --pack-destination="$TEMP_DIR" >/dev/null 2>&1 || true

    echo "  - Chrome DevTools server..."
    npm pack chrome-devtools-mcp --pack-destination="$TEMP_DIR" >/dev/null 2>&1 || true

    echo "  - Jira server..."
    npm pack @aashari/mcp-server-atlassian-jira --pack-destination="$TEMP_DIR" >/dev/null 2>&1 || true

    echo "  - Figma server..."
    npm pack figma-developer-mcp --pack-destination="$TEMP_DIR" >/dev/null 2>&1 || true

    echo "  - GitHub server..."
    npm pack @modelcontextprotocol/server-github --pack-destination="$TEMP_DIR" >/dev/null 2>&1 || true

    log_success "MCP servers cached"
}

# Print next steps
print_next_steps() {
    echo ""
    echo "========================================"
    echo "   Installation Complete!"
    echo "========================================"
    echo ""
    echo "MCP servers configured in .mcp.json:"
    if [ -f ".mcp.json" ]; then
        node -e "const f=require('./.mcp.json'); Object.keys(f.mcpServers||{}).forEach(s=>console.log('  - '+s))" 2>/dev/null || true
    fi
    echo ""
    echo "Next steps:"
    echo ""
    echo "1. Edit .mcp.json with your API tokens:"
    echo "   - ATLASSIAN_API_TOKEN (for Jira)"
    echo "   - FIGMA_API_KEY (for Figma)"
    echo "   - GITHUB_PERSONAL_ACCESS_TOKEN (for GitHub)"
    echo ""
    echo "2. Start Claude Code FROM THIS FOLDER:"
    echo "   cd $(pwd)"
    echo "   claude"
    echo ""
    echo "3. Inside Claude Code, verify MCP with: /mcp"
    echo ""
    echo "4. Run /aid-start to begin working!"
    echo ""
    echo "NOTE: MCP servers are PROJECT-SCOPED."
    echo "      They only work when running Claude from this folder."
    echo ""
    echo "========================================"
    echo ""
}

# Main installation flow
main() {
    print_banner
    check_prerequisites
    install_npm_deps
    setup_claude_commands_and_skills
    create_aid_directory
    create_state_files
    setup_global_aid
    setup_mcp_and_env
    preinstall_mcp_servers
    print_next_steps
}

# Run main
main "$@"
