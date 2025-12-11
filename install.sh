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

# Detect OS
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    elif [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        echo "windows"
    else
        echo "unknown"
    fi
}

# Install Node.js 18+
install_nodejs() {
    local os_type=$(detect_os)

    log_info "Attempting to install Node.js 18+..."

    case $os_type in
        "macos")
            if command -v brew &> /dev/null; then
                log_info "Installing Node.js via Homebrew..."
                brew install node@18
                export PATH="/opt/homebrew/opt/node@18/bin:$PATH"
                export PATH="/usr/local/opt/node@18/bin:$PATH"
                log_success "Node.js installed via Homebrew"
            else
                log_info "Installing Node.js via nvm..."
                curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
                export NVM_DIR="$HOME/.nvm"
                [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
                nvm install 18
                nvm use 18
                log_success "Node.js installed via nvm"
            fi
            ;;
        "linux")
            if command -v apt-get &> /dev/null; then
                log_info "Installing Node.js via NodeSource..."
                curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
                sudo apt-get install -y nodejs
                log_success "Node.js installed via apt"
            elif command -v dnf &> /dev/null; then
                log_info "Installing Node.js via dnf..."
                sudo dnf install -y nodejs
                log_success "Node.js installed via dnf"
            elif command -v pacman &> /dev/null; then
                log_info "Installing Node.js via pacman..."
                sudo pacman -S --noconfirm nodejs npm
                log_success "Node.js installed via pacman"
            else
                log_info "Installing Node.js via nvm..."
                curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
                export NVM_DIR="$HOME/.nvm"
                [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
                nvm install 18
                nvm use 18
                log_success "Node.js installed via nvm"
            fi
            ;;
        "windows")
            if command -v winget &> /dev/null; then
                log_info "Installing Node.js via winget..."
                winget install -e --id OpenJS.NodeJS.LTS --accept-source-agreements --accept-package-agreements
                log_success "Node.js installed via winget"
                log_warning "Please restart your terminal to use Node.js"
            elif command -v choco &> /dev/null; then
                log_info "Installing Node.js via Chocolatey..."
                choco install nodejs-lts -y
                log_success "Node.js installed via Chocolatey"
                log_warning "Please restart your terminal to use Node.js"
            else
                log_error "No package manager found. Please install Node.js manually:"
                echo "  Download from: https://nodejs.org/"
                return 1
            fi
            ;;
        *)
            log_error "Unsupported operating system: $os_type"
            echo "Please install Node.js manually from: https://nodejs.org/"
            return 1
            ;;
    esac

    return 0
}

# Install Git
install_git() {
    local os_type=$(detect_os)

    log_info "Attempting to install Git..."

    case $os_type in
        "macos")
            if command -v brew &> /dev/null; then
                log_info "Installing Git via Homebrew..."
                brew install git
                log_success "Git installed via Homebrew"
            else
                log_info "Installing Xcode Command Line Tools (includes Git)..."
                xcode-select --install 2>/dev/null || true
                log_success "Git installed via Xcode CLT"
            fi
            ;;
        "linux")
            if command -v apt-get &> /dev/null; then
                log_info "Installing Git via apt..."
                sudo apt-get update
                sudo apt-get install -y git
                log_success "Git installed via apt"
            elif command -v dnf &> /dev/null; then
                log_info "Installing Git via dnf..."
                sudo dnf install -y git
                log_success "Git installed via dnf"
            elif command -v yum &> /dev/null; then
                log_info "Installing Git via yum..."
                sudo yum install -y git
                log_success "Git installed via yum"
            elif command -v pacman &> /dev/null; then
                log_info "Installing Git via pacman..."
                sudo pacman -S --noconfirm git
                log_success "Git installed via pacman"
            else
                log_error "No supported package manager found"
                return 1
            fi
            ;;
        "windows")
            if command -v winget &> /dev/null; then
                log_info "Installing Git via winget..."
                winget install -e --id Git.Git --accept-source-agreements --accept-package-agreements
                log_success "Git installed via winget"
                log_warning "Please restart your terminal to use Git"
            elif command -v choco &> /dev/null; then
                log_info "Installing Git via Chocolatey..."
                choco install git -y
                log_success "Git installed via Chocolatey"
                log_warning "Please restart your terminal to use Git"
            else
                log_error "No package manager found. Please install Git manually:"
                echo "  Download from: https://git-scm.com/downloads"
                return 1
            fi
            ;;
        *)
            log_error "Unsupported operating system: $os_type"
            return 1
            ;;
    esac

    return 0
}

# Install Docker
install_docker() {
    local os_type=$(detect_os)

    log_info "Attempting to install Docker..."

    case $os_type in
        "macos")
            if command -v brew &> /dev/null; then
                log_info "Installing Docker Desktop via Homebrew..."
                brew install --cask docker
                log_success "Docker Desktop installed"
                log_warning "Please open Docker Desktop to complete setup"
            else
                log_error "Please install Docker Desktop manually:"
                echo "  Download from: https://www.docker.com/products/docker-desktop/"
                return 1
            fi
            ;;
        "linux")
            if command -v apt-get &> /dev/null; then
                log_info "Installing Docker via apt..."
                sudo apt-get update
                sudo apt-get install -y ca-certificates curl gnupg
                sudo install -m 0755 -d /etc/apt/keyrings
                curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
                sudo chmod a+r /etc/apt/keyrings/docker.gpg
                echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
                sudo apt-get update
                sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
                sudo usermod -aG docker $USER
                log_success "Docker installed via apt"
                log_warning "Please log out and back in to use Docker without sudo"
            elif command -v dnf &> /dev/null; then
                log_info "Installing Docker via dnf..."
                sudo dnf -y install dnf-plugins-core
                sudo dnf config-manager --add-repo https://download.docker.com/linux/fedora/docker-ce.repo
                sudo dnf install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
                sudo systemctl start docker
                sudo systemctl enable docker
                sudo usermod -aG docker $USER
                log_success "Docker installed via dnf"
            elif command -v pacman &> /dev/null; then
                log_info "Installing Docker via pacman..."
                sudo pacman -S --noconfirm docker docker-compose
                sudo systemctl start docker
                sudo systemctl enable docker
                sudo usermod -aG docker $USER
                log_success "Docker installed via pacman"
            else
                log_error "No supported package manager found"
                return 1
            fi
            ;;
        "windows")
            if command -v winget &> /dev/null; then
                log_info "Installing Docker Desktop via winget..."
                winget install -e --id Docker.DockerDesktop --accept-source-agreements --accept-package-agreements
                log_success "Docker Desktop installed via winget"
                log_warning "Please restart and open Docker Desktop to complete setup"
            elif command -v choco &> /dev/null; then
                log_info "Installing Docker Desktop via Chocolatey..."
                choco install docker-desktop -y
                log_success "Docker Desktop installed via Chocolatey"
                log_warning "Please restart and open Docker Desktop to complete setup"
            else
                log_error "Please install Docker Desktop manually:"
                echo "  Download from: https://www.docker.com/products/docker-desktop/"
                return 1
            fi
            ;;
        *)
            log_error "Unsupported operating system: $os_type"
            return 1
            ;;
    esac

    return 0
}

# Install Python 3.11
install_python() {
    local os_type=$(detect_os)

    log_info "Attempting to install Python 3.11..."

    case $os_type in
        "macos")
            if command -v brew &> /dev/null; then
                log_info "Installing Python 3.11 via Homebrew..."
                brew install python@3.11
                # Add to PATH for current session
                export PATH="/opt/homebrew/opt/python@3.11/bin:$PATH"
                export PATH="/usr/local/opt/python@3.11/bin:$PATH"
                log_success "Python 3.11 installed via Homebrew"
            else
                log_error "Homebrew not found. Please install Homebrew first:"
                echo "  /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
                return 1
            fi
            ;;
        "linux")
            if command -v apt-get &> /dev/null; then
                log_info "Installing Python 3.11 via apt..."
                sudo apt-get update
                sudo apt-get install -y software-properties-common
                sudo add-apt-repository -y ppa:deadsnakes/ppa
                sudo apt-get update
                sudo apt-get install -y python3.11 python3.11-venv python3.11-dev python3-pip
                # Update alternatives
                sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1
                log_success "Python 3.11 installed via apt"
            elif command -v dnf &> /dev/null; then
                log_info "Installing Python 3.11 via dnf..."
                sudo dnf install -y python3.11 python3.11-pip
                log_success "Python 3.11 installed via dnf"
            elif command -v yum &> /dev/null; then
                log_info "Installing Python 3.11 via yum..."
                sudo yum install -y python3.11 python3.11-pip
                log_success "Python 3.11 installed via yum"
            elif command -v pacman &> /dev/null; then
                log_info "Installing Python 3.11 via pacman..."
                sudo pacman -S --noconfirm python
                log_success "Python installed via pacman"
            else
                log_error "No supported package manager found (apt, dnf, yum, pacman)"
                return 1
            fi
            ;;
        "windows")
            if command -v winget &> /dev/null; then
                log_info "Installing Python 3.11 via winget..."
                winget install -e --id Python.Python.3.11 --accept-source-agreements --accept-package-agreements
                log_success "Python 3.11 installed via winget"
                log_warning "Please restart your terminal to use Python 3.11"
            elif command -v choco &> /dev/null; then
                log_info "Installing Python 3.11 via Chocolatey..."
                choco install python311 -y
                log_success "Python 3.11 installed via Chocolatey"
                log_warning "Please restart your terminal to use Python 3.11"
            else
                log_error "No package manager found. Please install Python 3.11 manually:"
                echo "  Download from: https://www.python.org/downloads/"
                echo "  Or install winget/chocolatey first"
                return 1
            fi
            ;;
        *)
            log_error "Unsupported operating system: $os_type"
            echo "Please install Python 3.11 manually from: https://www.python.org/downloads/"
            return 1
            ;;
    esac

    return 0
}

# Banner
print_banner() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════════╗"
    echo "║     AI Full Stack Development Methodology - Installation         ║"
    echo "╚══════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Helper function to offer installation
offer_install() {
    local name=$1
    local install_func=$2

    echo ""
    read -p "Would you like to install $name automatically? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if $install_func; then
            return 0
        else
            return 1
        fi
    else
        return 1
    fi
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."

    local missing=()
    local need_restart=false

    # Check Node.js
    local need_node=false
    if ! command -v node &> /dev/null; then
        need_node=true
        log_warning "Node.js not found"
    else
        NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
        if [ "$NODE_VERSION" -lt 18 ]; then
            need_node=true
            log_warning "Node.js version too old (current: $(node -v), required: v18+)"
        fi
    fi

    # Offer to install Node.js if needed
    if [ "$need_node" = true ]; then
        if offer_install "Node.js 18+" install_nodejs; then
            log_success "Node.js installed"
            need_restart=true
        else
            missing+=("Node.js v18+")
        fi
    fi

    # Check Git (before other tools that might need it)
    if ! command -v git &> /dev/null; then
        log_warning "Git not found"
        if offer_install "Git" install_git; then
            log_success "Git installed"
            need_restart=true
        else
            missing+=("Git")
        fi
    fi

    # Check Python
    local need_python=false
    if ! command -v python3 &> /dev/null; then
        need_python=true
        log_warning "Python not found"
    else
        PYTHON_MINOR=$(python3 -c 'import sys; print(sys.version_info.minor)')
        if [ "$PYTHON_MINOR" -lt 11 ]; then
            PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
            need_python=true
            log_warning "Python version too old (current: $PYTHON_VERSION, required: 3.11+)"
        fi
    fi

    # Offer to install Python if needed
    if [ "$need_python" = true ]; then
        if offer_install "Python 3.11" install_python; then
            log_success "Python 3.11 installed"
            need_restart=true
        else
            missing+=("Python 3.11+")
        fi
    fi

    # Check pip (usually comes with Python)
    if ! command -v pip3 &> /dev/null && ! command -v pip &> /dev/null; then
        log_warning "pip not found (usually installed with Python)"
        missing+=("pip3")
    fi

    # Check Docker (optional but recommended)
    if ! command -v docker &> /dev/null; then
        log_warning "Docker not found (optional, recommended for database)"
        echo ""
        read -p "Would you like to install Docker? (y/n) " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            if install_docker; then
                log_success "Docker installed"
                need_restart=true
            else
                log_warning "Docker installation failed - you can install it later"
            fi
        else
            log_info "Skipping Docker installation (you can use local PostgreSQL instead)"
        fi
    else
        log_info "Docker found: $(docker --version 2>/dev/null | head -1)"
    fi

    # Show restart warning if needed
    if [ "$need_restart" = true ]; then
        echo ""
        log_warning "Some tools were installed. You may need to restart your terminal."
        echo ""
        read -p "Press Enter to continue or Ctrl+C to exit and restart terminal..." -r
        echo ""
    fi

    # Final check for required tools
    if [ ${#missing[@]} -ne 0 ]; then
        log_error "Missing required prerequisites:"
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
