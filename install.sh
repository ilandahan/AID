#!/bin/bash

#==============================================================================
# AI Full Stack Development Methodology - Installation Script
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
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Banner
print_banner() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════════╗"
    echo "║     AI Full Stack Development Methodology - Installation         ║"
    echo "╚══════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    local missing=()
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        missing+=("Node.js (v18+)")
    else
        NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
        if [ "$NODE_VERSION" -lt 18 ]; then
            missing+=("Node.js v18+ (current: $(node -v))")
        fi
    fi
    
    # Check npm
    if ! command -v npm &> /dev/null; then
        missing+=("npm")
    fi
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        missing+=("Python 3.10+")
    fi
    
    # Check pip
    if ! command -v pip3 &> /dev/null; then
        missing+=("pip3")
    fi
    
    # Check Git
    if ! command -v git &> /dev/null; then
        missing+=("Git")
    fi
    
    if [ ${#missing[@]} -ne 0 ]; then
        log_error "Missing prerequisites:"
        for item in "${missing[@]}"; do
            echo "  - $item"
        done
        echo ""
        echo "Please install the missing prerequisites and run this script again."
        exit 1
    fi
    
    log_success "All prerequisites met"
}

# Setup environment file
setup_environment() {
    log_info "Setting up environment..."
    
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example .env
            log_info "Created .env from .env.example - please edit with your values"
        fi
    else
        log_info ".env file already exists"
    fi
    
    log_success "Environment setup complete"
}

# Install MCP servers (pre-cache for faster startup)
install_mcp_servers() {
    log_info "Pre-installing MCP servers for faster startup..."
    
    # Install npm dependencies (including puppeteer)
    if [ -f "package.json" ]; then
        log_info "Installing npm dependencies (puppeteer + Chromium)..."
        npm install --silent
    fi
    
    # Pre-install common MCP servers
    log_info "Installing Atlassian (Jira) MCP server..."
    npx -y @modelcontextprotocol/server-atlassian --help &>/dev/null || true
    
    log_info "Installing GitHub MCP server..."
    npx -y @modelcontextprotocol/server-github --help &>/dev/null || true
    
    log_info "Installing Filesystem MCP server..."
    npx -y @modelcontextprotocol/server-filesystem --help &>/dev/null || true
    
    log_info "Installing PostgreSQL MCP server..."
    npx -y @modelcontextprotocol/server-postgres --help &>/dev/null || true
    
    log_info "Installing Chrome DevTools MCP server..."
    npx -y chrome-devtools-mcp@latest --help &>/dev/null || true
    
    log_success "MCP servers pre-installed"
}

# Configure Claude Code settings
configure_claude_settings() {
    log_info "Configuring Claude Code settings..."
    
    # Create Claude configuration directory
    CLAUDE_CONFIG_DIR="$HOME/.claude"
    mkdir -p "$CLAUDE_CONFIG_DIR"
    
    # Copy Claude settings (not MCP - that stays in .mcp.json)
    if [ -f ".claude/settings.json" ]; then
        cp .claude/settings.json "$CLAUDE_CONFIG_DIR/settings.local.json"
        log_info "Claude settings template copied to $CLAUDE_CONFIG_DIR/settings.local.json"
    fi
    
    # Note: MCP configuration is in .mcp.json in project root
    # This is the new standard - MCP config stays with the project
    log_info "MCP configuration is in .mcp.json (project-level)"
    
    log_success "Claude Code configured"
}

# Install skills
install_skills() {
    log_info "Installing skills..."
    
    SKILLS_DIR="$HOME/.claude/skills"
    mkdir -p "$SKILLS_DIR"
    
    # Copy each skill
    for skill_dir in skills/*/; do
        skill_name=$(basename "$skill_dir")
        log_info "Installing skill: $skill_name"
        cp -r "$skill_dir" "$SKILLS_DIR/"
    done
    
    log_success "Skills installed to $SKILLS_DIR"
}

# Setup Git hooks
setup_git_hooks() {
    log_info "Setting up Git hooks..."
    
    if [ -d ".git" ]; then
        # Pre-commit hook for type checking
        cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
# AI Full Stack Methodology - Pre-commit hook

echo "Running pre-commit checks..."

# TypeScript type check (if applicable)
if [ -f "tsconfig.json" ]; then
    echo "Running TypeScript type check..."
    npx tsc --noEmit || exit 1
fi

# Run tests
if [ -f "package.json" ] && grep -q '"test"' package.json; then
    echo "Running tests..."
    npm test || exit 1
fi

echo "Pre-commit checks passed!"
EOF
        chmod +x .git/hooks/pre-commit
        log_success "Git hooks installed"
    else
        log_warning "Not a git repository, skipping hooks setup"
    fi
}

# Verify installation
verify_installation() {
    log_info "Verifying installation..."
    
    local errors=0
    
    # Check .mcp.json exists
    if [ -f ".mcp.json" ]; then
        log_info "MCP configuration found (.mcp.json)"
    else
        log_warning "MCP configuration not found"
        ((errors++))
    fi
    
    # Check .env exists
    if [ -f ".env" ]; then
        log_info "Environment file found (.env)"
    else
        log_warning "Environment file not found - copy .env.example to .env"
    fi
    
    # Check skills directory
    if [ -d "$HOME/.claude/skills" ]; then
        skill_count=$(ls -1 "$HOME/.claude/skills" 2>/dev/null | wc -l)
        log_info "Found $skill_count skills installed"
    else
        log_warning "Skills directory not found"
        ((errors++))
    fi
    
    # Check Claude config
    if [ -f "$HOME/.claude/settings.local.json" ]; then
        log_info "Claude settings file exists"
    else
        log_warning "Claude settings not found"
    fi
    
    if [ $errors -eq 0 ]; then
        log_success "Installation verified successfully"
    else
        log_warning "Installation completed with warnings"
    fi
}

# Print next steps
print_next_steps() {
    echo ""
    echo -e "${GREEN}═══════════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}                    Installation Complete!                          ${NC}"
    echo -e "${GREEN}═══════════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "${YELLOW}⚠️  IMPORTANT: Restart Claude Code to load MCP servers!${NC}"
    echo ""
    echo "Next steps:"
    echo ""
    echo "  1. Configure environment variables:"
    echo "     - Copy .env.example to .env"
    echo "     - Fill in your API tokens:"
    echo "       • ATLASSIAN_API_TOKEN (from https://id.atlassian.com/manage-profile/security/api-tokens)"
    echo "       • GITHUB_PERSONAL_ACCESS_TOKEN (from https://github.com/settings/tokens)"
    echo "       • FIGMA_API_KEY (from Figma Settings → Account → Personal access tokens)"
    echo ""
    echo -e "  2. ${YELLOW}Restart Claude Code to load MCP servers:${NC}"
    echo "     - Close Claude Code completely"
    echo "     - Reopen in the project directory:"
    echo "       cd $(pwd)"
    echo "       claude"
    echo "     - Verify with: claude mcp list"
    echo ""
    echo "  3. Optional: Enable Figma Dev Mode MCP (alternative to API)"
    echo "     - Open Figma Desktop"
    echo "     - Toggle Dev Mode (Shift+D)"
    echo "     - Enable desktop MCP server in inspect panel"
    echo ""
    echo "  4. Start a new project:"
    echo "     ./scripts/init-project.sh my-project-name"
    echo ""
    echo "  5. Or use Claude Code commands:"
    echo "     claude \"/start-project my-project\""
    echo ""
    echo "Configuration files:"
    echo "  • MCP Servers: .mcp.json (project-level)"
    echo "  • Claude Settings: ~/.claude/settings.local.json"
    echo "  • Skills: ~/.claude/skills/"
    echo "  • Environment: .env"
    echo ""
}

# Main installation flow
main() {
    print_banner
    
    # Check if we're in the right directory
    if [ ! -f "README.md" ] || [ ! -d "skills" ]; then
        log_error "Please run this script from the ai-fullstack-methodology root directory"
        exit 1
    fi
    
    check_prerequisites
    setup_environment
    install_mcp_servers
    configure_claude_settings
    install_skills
    setup_git_hooks
    verify_installation
    print_next_steps
}

# Run main
main "$@"
