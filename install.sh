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
    echo "[STEP 1/10] Installing npm dependencies..."
    # npm ci: install exactly what package-lock.json pins (no silent upgrades).
    if npm ci; then
        log_success "npm dependencies installed"
    else
        log_warning "npm ci had issues, continuing..."
    fi
}

# Step 2: Setup Claude commands and skills
setup_claude_commands_and_skills() {
    echo ""
    echo "[STEP 2/10] Setting up Claude commands and skills..."

    # Components ship in git at the REPOSITORY ROOT (commands/, skills/, agents/,
    # rules/, references/, hooks/) because that is where Claude Code looks when this
    # repo is loaded as a plugin. There is NO copy step.
    #
    # WHY this is a verification and not an installation: this function used to run 25
    # `cp -r skills/<name> .claude/skills/` lines against a root skills/ directory that
    # v2.1 removed, each ending in `|| true`. Every copy silently did nothing while the
    # step reported "Skills installed (24 skills)" - a count that was hardcoded and also
    # wrong. A step that cannot fail cannot tell you anything.
    missing=0
    for d in commands skills agents rules references hooks; do
        if [ -d "$d" ]; then
            count=$(find "$d" -type f | wc -l | tr -d ' ')
            log_success "$d/ present ($count files)"
        else
            log_warning "$d/ is MISSING - restore it before using AID"
            missing=1
        fi
    done

    skill_count=$(find skills -mindepth 1 -maxdepth 1 -type d 2>/dev/null | wc -l | tr -d ' ')
    agent_count=$(find agents -maxdepth 1 -name '*.md' 2>/dev/null | wc -l | tr -d ' ')

    if [ "$missing" -eq 0 ]; then
        log_success "Verified: $skill_count skills, $agent_count registered agents"
    else
        log_warning "Installation incomplete - see the warnings above"
        return
    fi

    # Mirror the root components into .claude/ as links.
    #
    # WHY: two consumers want them in different places. As a PLUGIN, Claude Code reads
    # commands/, skills/ and agents/ from the plugin root. As a plain PROJECT - which is
    # what this repo is when you open Claude Code in it, and what every already-linked
    # project expects - Claude Code reads .claude/<name>. Links satisfy both from one
    # copy of the files.
    #
    # These links are NOT tracked in git: core.symlinks defaults to false on Windows, so
    # a committed symlink checks out as a text file containing a path. They are created
    # here instead, per machine.
    echo ""
    log_info "Mirroring components into .claude/ (for project-mode and existing links)"
    mkdir -p .claude
    for d in commands skills agents rules references hooks; do
        target=".claude/$d"
        # Already a working link or directory? Leave it alone.
        if [ -e "$target" ] || [ -L "$target" ]; then
            if [ -L "$target" ] || [ -d "$target" ]; then
                log_success ".claude/$d already present"
                continue
            fi
        fi
        if ln -s "../$d" "$target" 2>/dev/null && [ -d "$target" ]; then
            log_success ".claude/$d -> ../$d (symlink)"
        else
            # MSYS/Git-Bash on Windows silently COPIES instead of linking, and plain
            # Windows needs a junction. Fall back to mklink /J, which needs no admin.
            rm -rf "$target" 2>/dev/null
            abs="$(cd "$d" && pwd -W 2>/dev/null || cd "$d" && pwd)"
            if command -v cmd >/dev/null 2>&1 && \
               MSYS_NO_PATHCONV=1 cmd //c mklink /J ".claude\\$d" "$(echo "$abs" | tr '/' '\\')" >/dev/null 2>&1; then
                log_success ".claude/$d -> $d (junction)"
            else
                log_warning ".claude/$d could not be linked - project mode will not see $d/"
            fi
        fi
    done
}

# Step 3: Create project state directory
create_aid_directory() {
    echo ""
    echo "[STEP 3/10] Creating project state directory..."
    mkdir -p ".aid"
    log_success "Project state directory created"
}

# Step 4: Create state files
create_state_files() {
    echo ""
    echo "[STEP 4/10] Creating state files..."

    CURRENT_DATE=$(date '+%Y-%m-%d %H:%M:%S')

    # .aid/state.json is NOT written here (T16-64, E3): hooks/aid_session.py is its only
    # writer. /aid-start runs `aid_session.py init`, which the user confirms.
    if [ -f ".aid/state.json" ]; then
        log_success "State file already exists"
    else
        log_info "State file: created by /aid-start (aid_session.py init), not by the installer"
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
    echo "[STEP 5/10] Setting up global AID learning system..."

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
    echo "[STEP 6/10] Creating MCP configuration (macOS/Linux)..."

    # Create .mcp.json from Mac template ONLY - no inline defaults
    if [ ! -f ".mcp.json" ]; then
        if [ -f ".mcp.json.mac" ]; then
            cp ".mcp.json.mac" ".mcp.json"
            log_success "MCP configuration created from Mac template"
            echo ""
            echo "  NOTE: .mcp.json reads tokens from environment variables. Do NOT paste"
            echo "  tokens into it. Export them from your OS keystore (see INSTALLATION.md):"
            echo "    - ATLASSIAN_SITE_NAME (subdomain only), ATLASSIAN_USER_EMAIL, ATLASSIAN_API_TOKEN (Jira/Confluence)"
            echo "    - GITHUB_PERSONAL_ACCESS_TOKEN (GitHub)"
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

    # No .env is created: tokens never go into a plaintext file.
    # Preference order: SSO/OAuth > OS keystore > environment variable.
    log_info "Tokens: store them in your OS keystore, not in a .env file."
    echo "  See INSTALLATION.md, section \"MCP Integrations Setup\" (OS keystore table)."
}

# Verify MCP configuration
verify_mcp_config() {
    echo ""
    echo "[STEP 7/10] Verifying MCP configuration..."

    if [ -f ".mcp.json" ]; then
        # Check if it's using the Windows-only format (wrong for Mac)
        if grep -q '"command": "cmd"' ".mcp.json"; then
            log_warning "Your .mcp.json uses Windows format (won't work on Mac)!"
            echo ""
            echo "  To fix: cp .mcp.json.mac .mcp.json"
            echo "  Then export your tokens as environment variables (see INSTALLATION.md)."
        else
            log_success "MCP configuration found"
        fi

        # Check for placeholder tokens
        if grep -q "YOUR_" ".mcp.json"; then
            log_warning ".mcp.json is an old template with inline token placeholders"
            echo "  Run: cp .mcp.json.mac .mcp.json  (it reads tokens from environment variables)"
        fi
    else
        log_warning "No .mcp.json found - MCP servers won't work"
        echo "  Run: cp .mcp.json.mac .mcp.json"
    fi
}

# Step 8: Setup Storybook preview server
setup_storybook() {
    echo ""
    echo "[STEP 8/10] Setting up Storybook preview server..."

    if [ -d "storybook-preview" ]; then
        log_info "Installing Storybook dependencies (this may take a minute)..."
        cd storybook-preview

        # Install npm dependencies
        if npm ci; then
            log_success "Storybook dependencies installed"
        else
            log_warning "Storybook install had issues - try manually: cd storybook-preview && npm ci"
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

# Step 9: Setup Cucumber BDD
setup_cucumber() {
    echo ""
    echo "═══════════════════════════════════════════════════════"
    echo "[STEP 9/10] Setting up Cucumber BDD..."
    echo "═══════════════════════════════════════════════════════"

    # Create Cucumber directory structure
    echo "  Creating Cucumber directory structure..."
    mkdir -p features/step-definitions
    mkdir -p features/support
    mkdir -p reports

    if [ -d "features" ]; then
        log_success "Cucumber directories created"
        echo "    ├── features/"
        echo "    │   ├── step-definitions/"
        echo "    │   └── support/"
        echo "    └── reports/"
    else
        log_warning "Failed to create Cucumber directories"
    fi

    # Copy Cucumber configuration template
    echo "  Setting up Cucumber configuration..."
    if [ -f "cucumber.js" ]; then
        log_success "Cucumber configuration already exists (preserved)"
    elif [ -f "cucumber.js.template" ]; then
        cp cucumber.js.template cucumber.js
        log_success "Cucumber configuration created from template"
    else
        log_warning "cucumber.js.template not found - creating minimal config"
        cat > cucumber.js << 'CUCUMBEREOF'
module.exports = {
  default: {
    require: ['features/step-definitions/**/*.ts', 'features/support/**/*.ts'],
    requireModule: ['ts-node/register'],
    format: ['progress-bar', 'html:reports/cucumber-report.html'],
    publishQuiet: true
  }
};
CUCUMBEREOF
        log_success "Minimal Cucumber configuration created"
    fi

    # Create World class template
    echo "  Creating Cucumber World template..."
    if [ -f "features/support/world.ts" ]; then
        log_success "World template already exists (preserved)"
    else
        cat > features/support/world.ts << 'WORLDEOF'
/**
 * Cucumber World - Shared State Between Steps
 *
 * The World is instantiated for each scenario and provides
 * a clean context for step definitions to share data.
 *
 * Add properties here to share between steps:
 *   this.currentUser = await login(email);
 *   this.response = await api.get('/endpoint');
 *
 * Access in steps via 'this':
 *   Given('I am logged in', async function() {
 *     this.currentUser = await login('test@example.com');
 *   });
 */
import { setWorldConstructor, World, IWorldOptions } from '@cucumber/cucumber';

export interface ICustomWorld {
  // Add your shared properties here
  // Example: currentUser?: User;
  // Example: response?: Response;
  // Example: page?: Page;  // for browser automation
}

export class CustomWorld extends World implements ICustomWorld {
  constructor(options: IWorldOptions) {
    super(options);
  }

  // Add helper methods here
  // Example:
  // async login(email: string): Promise<User> { ... }
}

setWorldConstructor(CustomWorld);
WORLDEOF
        log_success "World template created at features/support/world.ts"
    fi

    log_success "Cucumber BDD setup complete"
    echo "  Run 'npm run cucumber' to execute feature files"
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
    npm pack @modelcontextprotocol/server-filesystem@2.1.0 --pack-destination="$TEMP_DIR" >/dev/null 2>&1 || true

    echo "  - Chrome DevTools server..."
    npm pack chrome-devtools-mcp@1.12.0 --pack-destination="$TEMP_DIR" >/dev/null 2>&1 || true

    echo "  - Jira server..."
    npm pack @aashari/mcp-server-atlassian-jira@3.3.0 --pack-destination="$TEMP_DIR" >/dev/null 2>&1 || true

    echo "  - Confluence server..."
    npm pack @aashari/mcp-server-atlassian-confluence@3.3.0 --pack-destination="$TEMP_DIR" >/dev/null 2>&1 || true

    # GitHub uses GitHub's hosted MCP server (type http): nothing to download.

    log_success "MCP servers cached"
}

# Step 10: breather (session boundaries + status line, user-scope). T11: OPT-IN.
# It installs into ~/.claude (every project on this machine), and its session-start
# instructions tell Claude to fetch today's calendar events through any connected calendar
# connector. So it runs only after an explicit yes, or with --with-breather.
WITH_BREATHER=0
for arg in "$@"; do
    [ "$arg" = "--with-breather" ] && WITH_BREATHER=1
done

setup_breather() {
    echo ""
    echo "═══════════════════════════════════════════════════════"
    echo "[STEP 10/10] breather (optional: session break offers)"
    echo "═══════════════════════════════════════════════════════"
    echo "breather installs into ~/.claude for EVERY project on this machine (hooks + status line)."
    echo "At session start it tells Claude to fetch today's calendar events through any connected"
    echo "calendar connector (Google Calendar / Gmail, Microsoft 365 / Outlook) and to record the"
    echo "meeting times locally. See integrations/breather/README.md."

    if [ "$WITH_BREATHER" != "1" ]; then
        if [ -t 0 ]; then
            read -r -p "Install breather? [y/N] " answer || answer=""
        else
            answer=""
            echo "(no terminal to ask: skipping)"
        fi
        case "$answer" in
            [yY]|[yY][eE][sS]) ;;
            *)
                log_info "breather skipped. Install later with /breather-start, or: node integrations/breather/install.mjs"
                return 0
                ;;
        esac
    fi

    if node integrations/breather/install.mjs; then
        log_success "breather installed to ~/.claude (all projects, active after Claude Code restart)"
    else
        log_warning "breather install failed - run manually: node integrations/breather/install.mjs"
    fi
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
    echo "1. Export your API tokens as environment variables (do not edit them into .mcp.json):"
    echo "   - ATLASSIAN_SITE_NAME (subdomain only), ATLASSIAN_USER_EMAIL, ATLASSIAN_API_TOKEN (for Jira/Confluence)"
    echo "   - GITHUB_PERSONAL_ACCESS_TOKEN (for GitHub)"
    echo "   Load them from your OS keystore, e.g.:"
    echo "     export ATLASSIAN_API_TOKEN=\"\$(security find-generic-password -s aid-atlassian -w)\"   # macOS"
    echo "     export ATLASSIAN_API_TOKEN=\"\$(secret-tool lookup service aid-atlassian)\"          # Linux"
    echo ""
    echo "2. Start Claude Code FROM THIS FOLDER:"
    echo "   cd $(pwd)"
    echo "   claude"
    echo ""
    echo "3. Inside Claude Code, verify MCP with: /mcp"
    echo ""
    echo "4. Run /aid-start to begin working!"
    echo ""
    echo "5. Cucumber BDD commands:"
    echo "   npm run cucumber        - Run BDD acceptance tests"
    echo "   npm run cucumber:dry    - Validate feature file syntax"
    echo "   npm run test:bdd        - Run tests and generate HTML report"
    echo "   npm run test:smoke      - Run @smoke tagged tests only"
    echo "   npm run test:critical   - Run @critical tagged tests only"
    echo ""
    echo "6. (OPTIONAL) Preview design spec components in Storybook:"
    echo "   - Implement a component from the approved design specification"
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
    setup_cucumber
    setup_breather
    preinstall_mcp_servers
    print_next_steps
}

# Run main
main "$@"
