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

    # Check Python (warning only, not required)
    if command -v python3 &> /dev/null; then
        log_success "Python found: $(python3 --version)"
        PYTHON_CMD="python3"
        if command -v pip3 &> /dev/null; then
            PIP_CMD="pip3"
        elif python3 -m pip --version &> /dev/null; then
            PIP_CMD="python3 -m pip"
        else
            PIP_CMD=""
            log_warning "pip not found, memory-system will need manual install"
        fi
    elif command -v python &> /dev/null; then
        PYTHON_VERSION=$(python --version 2>&1)
        if [[ "$PYTHON_VERSION" == *"3."* ]]; then
            log_success "Python found: $PYTHON_VERSION"
            PYTHON_CMD="python"
            if command -v pip &> /dev/null; then
                PIP_CMD="pip"
            else
                PIP_CMD=""
            fi
        else
            log_warning "Python 3 not found, memory-system will need manual install"
            PYTHON_CMD=""
            PIP_CMD=""
        fi
    else
        log_warning "Python not found, memory-system will need manual install"
        PYTHON_CMD=""
        PIP_CMD=""
    fi

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
    echo "[STEP 1/7] Installing npm dependencies..."
    if npm install; then
        log_success "npm dependencies installed"
    else
        log_warning "npm install had issues, continuing..."
    fi
}

# Step 2: Setup Claude commands and skills
setup_claude_commands_and_skills() {
    echo ""
    echo "[STEP 2/7] Setting up Claude commands and skills..."

    # Create .claude directories (project level)
    mkdir -p ".claude/commands"
    mkdir -p ".claude/skills"
    mkdir -p ".claude/references"

    # Copy command files
    if [ -d "memory-system/integration/commands" ]; then
        cp -f memory-system/integration/commands/*.md .claude/commands/ 2>/dev/null || true
    fi
    if [ -d "skills/commands" ]; then
        cp -f skills/commands/*.md .claude/commands/ 2>/dev/null || true
    fi
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

    log_success "Skills installed (20 skills)"
}

# Step 3: Create project state directory
create_aid_directory() {
    echo ""
    echo "[STEP 3/7] Creating project state directory..."
    mkdir -p ".aid"
    log_success "Project state directory created"
}

# Step 4: Create state files
create_state_files() {
    echo ""
    echo "[STEP 4/7] Creating state files..."

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

# Step 5: Install memory-system Python package
install_memory_system() {
    echo ""
    echo "[STEP 5/7] Installing memory-system Python package..."

    if [ -z "$PIP_CMD" ]; then
        log_warning "Python/pip not found, skipping memory-system install"
        echo "         Install Python 3.9+ and run: pip install -e memory-system"
        return
    fi

    if [ -d "memory-system" ]; then
        if $PIP_CMD install -e memory-system 2>/dev/null; then
            log_success "Memory system installed"
        else
            log_warning "Memory system install failed"
            echo "         Try manually: $PIP_CMD install -e memory-system"
        fi
    else
        log_warning "memory-system directory not found, skipping"
    fi
}

# Step 6: Setup global AID learning system
setup_global_aid() {
    echo ""
    echo "[STEP 6/7] Setting up global AID learning system..."

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

# Step 7: Create MCP configuration (CROSS-PLATFORM)
setup_mcp_and_env() {
    echo ""
    echo "[STEP 7/7] Creating MCP configuration..."

    # Create .mcp.json from Mac template if not exists
    if [ ! -f ".mcp.json" ]; then
        if [ -f ".mcp.json.mac" ]; then
            cp ".mcp.json.mac" ".mcp.json"
            log_success "MCP configuration created from Mac template"
        else
            echo "Creating .mcp.json with default configuration..."
            cat > ".mcp.json" << 'MCPEOF'
{
  "mcpServers": {
    "filesystem": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "."]
    },
    "chrome-devtools": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "chrome-devtools-mcp@latest"]
    },
    "jira": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@aashari/mcp-server-atlassian-jira"],
      "env": {
        "ATLASSIAN_SITE_URL": "https://YOUR_SITE.atlassian.net",
        "ATLASSIAN_USER_EMAIL": "your@email.com",
        "ATLASSIAN_API_TOKEN": "YOUR_ATLASSIAN_API_TOKEN"
      }
    },
    "confluence": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@aashari/mcp-server-atlassian-confluence"],
      "env": {
        "ATLASSIAN_SITE_URL": "https://YOUR_SITE.atlassian.net",
        "ATLASSIAN_USER_EMAIL": "your@email.com",
        "ATLASSIAN_API_TOKEN": "YOUR_ATLASSIAN_API_TOKEN"
      }
    },
    "figma": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "figma-developer-mcp", "--stdio"],
      "env": {
        "FIGMA_API_KEY": "YOUR_FIGMA_API_KEY"
      }
    },
    "github": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "YOUR_GITHUB_TOKEN"
      }
    }
  }
}
MCPEOF
            log_success "MCP configuration created with defaults"
        fi
        echo ""
        echo "  NOTE: Edit .mcp.json to add your API tokens:"
        echo "    - ATLASSIAN_API_TOKEN (for Jira/Confluence)"
        echo "    - FIGMA_API_KEY (for Figma)"
        echo "    - GITHUB_PERSONAL_ACCESS_TOKEN (for GitHub)"
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
    echo "[VERIFY] Checking MCP configuration..."
    
    if [ -f ".mcp.json" ]; then
        # Check if it's using the old Windows-only format
        if grep -q '"command": "cmd"' ".mcp.json"; then
            log_warning "Your .mcp.json uses Windows-only format!"
            echo ""
            echo "  To fix: Copy .mcp.json.example to .mcp.json"
            echo "  Command: cp .mcp.json.example .mcp.json"
            echo ""
            echo "  Then add your API tokens to the new file."
        else
            log_success "MCP configuration is cross-platform compatible"
        fi
        
        # Check for placeholder tokens
        if grep -q "YOUR_" ".mcp.json"; then
            log_warning "MCP tokens not configured yet"
            echo "  Edit .mcp.json and replace YOUR_* placeholders with real tokens"
        fi
    else
        log_warning "No .mcp.json found - MCP servers won't work"
        echo "  Run: cp .mcp.json.example .mcp.json"
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
    install_memory_system
    setup_global_aid
    setup_mcp_and_env
    verify_mcp_config
    preinstall_mcp_servers
    print_next_steps
}

# Run main
main "$@"
