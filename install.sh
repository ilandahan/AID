#!/bin/bash

#==============================================================================
# AID - AI Development Methodology Installer
# Cross-Platform (macOS/Linux)
# Updated: 2025-12-31 - Fixed MCP cross-platform compatibility
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
log_success() { echo -e "${GREEN}[OK]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Banner
print_banner() {
    echo ""
    echo "========================================"
    echo "   AID Installation Script"
    echo "   Cross-Platform (macOS/Linux)"
    echo "========================================"
    echo ""
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    echo ""

    # Check Node.js
    if ! command -v node &> /dev/null; then
        log_error "Node.js not found!"
        echo "Please install Node.js 18+ from https://nodejs.org/"
        echo "Or via Homebrew: brew install node"
        exit 1
    fi
    log_success "Node.js found: $(node -v)"

    # Check npm
    if ! command -v npm &> /dev/null; then
        log_error "npm not found!"
        exit 1
    fi
    log_success "npm found: $(npm -v)"

    # Check Git (optional)
    if command -v git &> /dev/null; then
        log_success "Git found: $(git --version | head -1)"
    else
        log_warning "Git not found (optional)"
    fi

    echo ""
}

# Step 1: Install npm dependencies
install_npm_deps() {
    echo ""
    echo "[STEP 1/8] Installing npm dependencies..."
    if npm install; then
        log_success "npm dependencies installed"
    else
        log_warning "npm install had issues, continuing..."
    fi
}

# Step 2: Setup Claude commands and skills
setup_claude_commands_and_skills() {
    echo ""
    echo "[STEP 2/8] Setting up Claude commands and skills..."

    # Create .claude directories (project level)
    mkdir -p ".claude/commands"
    mkdir -p ".claude/skills"
    mkdir -p ".claude/references"

    # Note: Commands are stored in .claude/commands/ (already in git)
    # Do NOT use skills/commands/ - that's not a valid Claude Code pattern
    log_success "Commands installed"

    # Copy skills to .claude/skills (project level)
    echo "Copying skills..."

    # Core methodology skills
    cp -r skills/aid-development .claude/skills/ 2>/dev/null || true
    cp -r skills/aid-discovery .claude/skills/ 2>/dev/null || true
    cp -r skills/aid-prd .claude/skills/ 2>/dev/null || true
    cp -r skills/aid-qa-ship .claude/skills/ 2>/dev/null || true
    cp -r skills/aid-tech-spec .claude/skills/ 2>/dev/null || true

    # Design system skills
    cp -r skills/atomic-design .claude/skills/ 2>/dev/null || true
    cp -r skills/atomic-page-builder .claude/skills/ 2>/dev/null || true

    # Development skills
    cp -r skills/aid-impl-plan .claude/skills/ 2>/dev/null || true
    cp -r skills/code-review .claude/skills/ 2>/dev/null || true
    cp -r skills/context-tracking .claude/skills/ 2>/dev/null || true
    cp -r skills/learning-mode .claude/skills/ 2>/dev/null || true
    cp -r skills/phase-enforcement .claude/skills/ 2>/dev/null || true
    cp -r skills/pre-prd-research .claude/skills/ 2>/dev/null || true
    cp -r skills/system-architect .claude/skills/ 2>/dev/null || true
    cp -r skills/test-driven .claude/skills/ 2>/dev/null || true

    # Role-based skills
    cp -r skills/role-developer .claude/skills/ 2>/dev/null || true
    cp -r skills/role-product-manager .claude/skills/ 2>/dev/null || true
    cp -r skills/role-qa-engineer .claude/skills/ 2>/dev/null || true
    cp -r skills/role-tech-lead .claude/skills/ 2>/dev/null || true

    # Optional skills
    cp -r skills/nano-banana-visual .claude/skills/ 2>/dev/null || true

    # Figma design review skill
    cp -r skills/figma-design-review .claude/skills/ 2>/dev/null || true

    # Foundational skills
    cp -r skills/why-driven-decision .claude/skills/ 2>/dev/null || true
    cp -r skills/reflection .claude/skills/ 2>/dev/null || true
    cp -r skills/aid-test-agent .claude/skills/ 2>/dev/null || true

    log_success "Skills installed (24 skills)"
}

# Step 3: Create project state directory
create_aid_directory() {
    echo ""
    echo "[STEP 3/8] Creating project state directory..."
    mkdir -p ".aid"
    log_success "Project state directory created"
}

# Step 4: Create state files
create_state_files() {
    echo ""
    echo "[STEP 4/8] Creating state files..."

    CURRENT_DATE=$(date '+%Y-%m-%d %H:%M:%S')

    # Create state.json if it doesn't exist
    if [ ! -f ".aid/state.json" ]; then
        cat > ".aid/state.json" << EOF
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
        log_success "State file created"
    else
        log_success "State file already exists"
    fi

    # Create context.json if it doesn't exist
    if [ ! -f ".aid/context.json" ]; then
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
        log_success "Context file created"
    else
        log_success "Context file already exists"
    fi
}


# Step 6: Setup global AID learning system
setup_global_aid() {
    echo ""
    echo "[STEP 5/8] Setting up global AID learning system..."

    AID_HOME="$HOME/.aid"
    mkdir -p "$AID_HOME"
    mkdir -p "$AID_HOME/feedback"
    mkdir -p "$AID_HOME/feedback/pending"
    mkdir -p "$AID_HOME/feedback/processed"
    mkdir -p "$AID_HOME/metrics"
    mkdir -p "$AID_HOME/logs"
    mkdir -p "$AID_HOME/skills"

    log_success "Global learning system initialized at $AID_HOME"
}

# Step 7: Create MCP configuration (Mac template only - no inline defaults)
setup_mcp_and_env() {
    echo ""
    echo "[STEP 6/8] Creating MCP configuration (macOS/Linux)..."

    # Create .mcp.json from Mac template ONLY - no inline defaults
    if [ ! -f ".mcp.json" ]; then
        if [ -f ".mcp.json.mac" ]; then
            cp ".mcp.json.mac" ".mcp.json"
            log_success "MCP configuration created from Mac template"
            echo ""
            echo "  NOTE: Edit .mcp.json to add your API tokens:"
            echo "    - ATLASSIAN_API_TOKEN (for Jira/Confluence)"
            echo "    - FIGMA_API_KEY (for Figma)"
            echo "    - GITHUB_PERSONAL_ACCESS_TOKEN (for GitHub)"
        else
            log_error ".mcp.json.mac template not found!"
            echo ""
            echo "  The Mac MCP template is required for installation."
            echo "  Please ensure .mcp.json.mac exists in the AID folder."
            echo ""
            echo "  You can create it manually or download from the AID repository."
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
    else
        log_success ".env already exists"
    fi
}

# Verify MCP configuration
verify_mcp_config() {
    echo ""
    echo "[STEP 7/8] Verifying MCP configuration..."

    if [ -f ".mcp.json" ]; then
        # Check if it's using the Windows-only format (wrong for Mac)
        if grep -q '"command": "cmd"' ".mcp.json"; then
            log_warning "Your .mcp.json uses Windows format (won't work on Mac)!"
            echo ""
            echo "  To fix: cp .mcp.json.mac .mcp.json"
            echo "  Then add your API tokens to the new file."
        else
            log_success "MCP configuration found"
        fi

        # Check for placeholder tokens
        if grep -q "YOUR_" ".mcp.json"; then
            log_warning "MCP tokens not configured yet"
            echo "  Edit .mcp.json and replace YOUR_* placeholders with real tokens"
        fi
    else
        log_warning "No .mcp.json found - MCP servers won't work"
        echo "  Run: cp .mcp.json.mac .mcp.json"
    fi
}

# Step 8: Setup Storybook preview server
setup_storybook() {
    echo ""
    echo "[STEP 8/8] Setting up Storybook preview server..."

    if [ -d "storybook-preview" ]; then
        log_info "Installing Storybook dependencies (this may take a minute)..."
        cd storybook-preview

        # Install npm dependencies
        if npm install; then
            log_success "Storybook dependencies installed"
        else
            log_warning "Storybook install had issues - try manually: cd storybook-preview && npm install"
        fi

        # Create atomic design component directories
        mkdir -p src/components/atoms
        mkdir -p src/components/molecules
        mkdir -p src/components/organisms
        mkdir -p src/components/templates
        mkdir -p src/components/pages

        cd ..
        log_success "Storybook ready - use /storybook command to preview components"
    else
        log_warning "storybook-preview folder not found, skipping"
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

    echo "  - Confluence server..."
    npm pack @aashari/mcp-server-atlassian-confluence --pack-destination="$TEMP_DIR" >/dev/null 2>&1 || true

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
        node -e "const f=require('./.mcp.json'); Object.keys(f.mcpServers||{}).forEach(s=>console.log('  - '+s))" 2>/dev/null || echo "  (could not list servers)"
    fi
    echo ""
    echo "Next steps:"
    echo ""
    echo "1. Edit .mcp.json with your API tokens:"
    echo "   - ATLASSIAN_API_TOKEN (for Jira/Confluence)"
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
    echo "5. (OPTIONAL) Preview Figma components in Storybook:"
    echo "   - Extract component from Figma plugin"
    echo "   - Tell Claude: 'Add ComponentName to Storybook'"
    echo "   - Or use: /storybook add ./path/to/Component"
    echo "   - View at http://localhost:6006"
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
    # Removed: memory-system now a skill
    setup_global_aid
    setup_mcp_and_env
    verify_mcp_config
    setup_storybook
    preinstall_mcp_servers
    print_next_steps
}

# Run main
main "$@"
