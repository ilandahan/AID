#!/bin/bash

#==============================================================================
# AID - Project Initialization Script
# Creates a new project with symbolic links to the AID methodology
#==============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Logging
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Get script directory (AID location)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AID_DIR="$(dirname "$SCRIPT_DIR")"

# Usage
usage() {
    echo "Usage: $0 <project-name> [options]"
    echo ""
    echo "Options:"
    echo "  --template <name>   Use specific template (default: fullstack)"
    echo "  --no-git            Skip git initialization"
    echo "  --no-deps           Skip dependency installation"
    echo "  --copy              Copy files instead of symbolic links"
    echo "  --help              Show this help message"
    echo ""
    echo "Templates:"
    echo "  fullstack           Full stack TypeScript project (Next.js)"
    echo "  api                 API-only project"
    echo "  frontend            Frontend-only project"
    echo ""
    echo "Example:"
    echo "  $0 my-awesome-project"
    echo "  $0 my-api --template api"
}

# Parse arguments
PROJECT_NAME=""
TEMPLATE="fullstack"
INIT_GIT=true
INSTALL_DEPS=true
USE_SYMLINKS=true

while [[ $# -gt 0 ]]; do
    case $1 in
        --template)
            TEMPLATE="$2"
            shift 2
            ;;
        --no-git)
            INIT_GIT=false
            shift
            ;;
        --no-deps)
            INSTALL_DEPS=false
            shift
            ;;
        --copy)
            USE_SYMLINKS=false
            shift
            ;;
        --help)
            usage
            exit 0
            ;;
        -*)
            log_error "Unknown option: $1"
            usage
            exit 1
            ;;
        *)
            if [ -z "$PROJECT_NAME" ]; then
                PROJECT_NAME="$1"
            else
                log_error "Unexpected argument: $1"
                usage
                exit 1
            fi
            shift
            ;;
    esac
done

# Validate project name
if [ -z "$PROJECT_NAME" ]; then
    log_error "Project name is required"
    usage
    exit 1
fi

# The name becomes a folder name and is written into JSON and Markdown files.
# Allow only a plain name: letters, digits, dot, underscore, dash.
if ! [[ "$PROJECT_NAME" =~ ^[A-Za-z0-9][A-Za-z0-9._-]{0,99}$ ]] || [[ "$PROJECT_NAME" == *..* ]]; then
    log_error "Invalid project name '$PROJECT_NAME' (use letters, digits, '.', '_' or '-')"
    exit 1
fi

if [ -e "$PROJECT_NAME" ]; then
    log_error "Directory '$PROJECT_NAME' already exists"
    exit 1
fi

# Banner
echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║              AID - New Project Initialization                     ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""
log_info "Creating project: $PROJECT_NAME"
log_info "Template: $TEMPLATE"
log_info "AID location: $AID_DIR"
if [ "$USE_SYMLINKS" = true ]; then
    log_info "Mode: Symbolic links (recommended)"
else
    log_info "Mode: Copy files"
fi
echo ""

# Create project directory
mkdir -p "$PROJECT_NAME"
cd "$PROJECT_NAME"

# Create directory structure
log_info "Creating directory structure..."

mkdir -p src/{components/{atoms,molecules,organisms,templates},app,hooks,utils,types,styles}
mkdir -p tests/{unit,integration,e2e}
mkdir -p docs

# Create .aid directory for work context.
# .aid/state.json is NOT written here: hooks/aid_session.py is its only writer.
# The user creates it with /aid-start (aid_session.py init, which Claude Code asks
# the user to confirm).
log_info "Creating AID work context..."
mkdir -p .aid

# Portable timestamp; no `sed -i` (its flags differ between GNU, BSD and Git Bash).
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Create context.json
cat > .aid/context.json << EOF
{
  "last_updated": "$TIMESTAMP",
  "tasks": {
    "previous": null,
    "current": null,
    "next": null
  },
  "current_task_steps": {
    "previous": null,
    "current": null,
    "next": null
  },
  "notes": "Project created. Run /aid-start to choose your role and phase (0-5)."
}
EOF

log_success "AID work context created (.aid/context.json)"

# The entries linked or copied from AID into the project.
AID_ENTRIES=(.claude CLAUDE.md skills)

# link_entry <name>: create a REAL symbolic link <name> -> AID's <name>.
# Git Bash without native symlinks makes `ln -s` copy instead (and a copy of a tree
# that holds relative mirror links can fail half-way), so anything that is not a real
# link afterwards counts as a failure and is removed.
link_entry() {
    local name="$1"
    local target
    for target in "$RELATIVE_AID/$name" "$AID_DIR/$name"; do
        if ln -s "$target" "$name" 2>/dev/null && [ -L "$name" ] && [ -e "$name" ]; then
            return 0
        fi
        rm -rf -- "./$name"
    done
    return 1
}

# copy_entry <name>: copy AID's <name> into the project, following links.
# `.claude/` in an installed AID holds relative mirror links (agents -> ../agents);
# copied as links they would dangle (and Git Bash refuses to create them, exit 1),
# so they are dereferenced (-L).
copy_entry() {
    local name="$1"
    if [ -e "$AID_DIR/$name" ]; then
        cp -RL "$AID_DIR/$name" "./$name"
        log_info "  Copied: $name"
    fi
}

# Link or copy AID files
if [ "$USE_SYMLINKS" = true ]; then
    log_info "Creating symbolic links to AID..."

    # Create relative path to AID from project
    RELATIVE_AID="../$(basename "$AID_DIR")"

    for entry in "${AID_ENTRIES[@]}"; do
        if ! link_entry "$entry"; then
            log_warning "Symbolic link failed. Copying instead."
            USE_SYMLINKS=false
            break
        fi
    done

    if [ "$USE_SYMLINKS" = true ]; then
        log_success "Symbolic links created"
        for entry in "${AID_ENTRIES[@]}"; do
            log_info "  $entry -> $(readlink "$entry")"
        done
    else
        # Remove the links made before the failure, so the copy starts clean.
        for entry in "${AID_ENTRIES[@]}"; do
            rm -rf -- "./$entry"
        done
    fi
fi

if [ "$USE_SYMLINKS" = false ]; then
    log_info "Copying AID files..."

    for entry in "${AID_ENTRIES[@]}"; do
        copy_entry "$entry"
    done
    # settings.local.json holds the AID install's own machine-local permissions;
    # a new project starts without them.
    rm -f ./.claude/settings.local.json

    log_success "AID files copied"
fi

# Create package.json
log_info "Creating package.json..."

cat > package.json << EOF
{
  "name": "$PROJECT_NAME",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage"
  },
  "dependencies": {
    "next": "^14.0.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  },
  "devDependencies": {
    "@types/node": "^20.0.0",
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "typescript": "^5.0.0",
    "jest": "^29.7.0",
    "@testing-library/react": "^14.0.0",
    "@testing-library/jest-dom": "^6.0.0"
  }
}
EOF

# Create TypeScript config
log_info "Creating TypeScript configuration..."

cat > tsconfig.json << 'EOF'
{
  "compilerOptions": {
    "target": "ES2020",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [{ "name": "next" }],
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"],
      "@/components/*": ["src/components/*"],
      "@/atoms/*": ["src/components/atoms/*"],
      "@/molecules/*": ["src/components/molecules/*"],
      "@/organisms/*": ["src/components/organisms/*"],
      "@/templates/*": ["src/components/templates/*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
EOF

# Create .gitignore
cat > .gitignore << 'EOF'
# Dependencies
node_modules/

# Build
.next/
dist/
build/

# Environment
.env
.env.local
.env.*.local

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db

# Logs
*.log
npm-debug.log*

# Coverage
coverage/

# Cache
.cache/
*.tsbuildinfo
EOF

# Create .env.example: non-secret settings only.
cat > .env.example << 'EOF'
# Non-secret settings only. Never put passwords, tokens or keys in this file
# or in a .env file. Store secrets in your OS keystore (macOS Keychain,
# Windows Credential Manager, Linux libsecret) and export them per shell;
# see AID's INSTALLATION.md, section "MCP Integrations Setup".

# Application
NODE_ENV=development
NEXT_PUBLIC_APP_URL=http://localhost:3000
NEXTAUTH_URL=http://localhost:3000
EOF

# Create basic source files
log_info "Creating source files..."

mkdir -p src/app

cat > src/app/layout.tsx << EOF
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: '$PROJECT_NAME',
  description: 'Built with AID methodology',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
EOF

cat > src/app/page.tsx << EOF
export default function Home() {
  return (
    <main>
      <h1>$PROJECT_NAME</h1>
      <p>Welcome! Start with <code>/prd</code> to create your Product Requirements Document.</p>
    </main>
  );
}
EOF

# Create docs placeholders (the layout AID's commands use: docs/prd/, docs/tech-spec/)
mkdir -p docs/prd docs/tech-spec
cat > docs/prd/PRD.md << 'EOF'
# Product Requirements Document

> Run `/prd` to generate this document.

## Overview
[To be filled]

## Problem Statement
[To be filled]

## Goals
[To be filled]

## User Stories
[To be filled]

## Acceptance Criteria
[To be filled]
EOF

cat > docs/tech-spec/TECH-SPEC.md << 'EOF'
# Technical Specification

> Run `/tech-spec` after PRD is approved to generate this document.

## Overview
[To be filled]

## Architecture
[To be filled]

## Database Schema
[To be filled]

## API Endpoints
[To be filled]
EOF

# Create README
cat > README.md << EOF
# $PROJECT_NAME

Built with [AID (AI Development Methodology)](../AID).

## Getting Started

### Prerequisites
- Node.js 18+
- npm

### Installation
\`\`\`bash
npm install
\`\`\`

### Development
\`\`\`bash
npm run dev
\`\`\`

## AID Workflow

This project uses the AID phase-gated methodology:

Run \`/aid-start\` first: it records your role and phase (0-5).

0. **Phase 0: Discovery** - \`/discovery\` - Research and validation
1. **Phase 1: PRD** - \`/prd\` - Create Product Requirements
2. **Phase 2: Tech Spec** - \`/tech-spec\` - Technical Specification
3. **Phase 3: Breakdown** - \`/jira-breakdown\` - Task Breakdown
4. **Phase 4: Development** - Code implementation
5. **Phase 5: QA & Ship** - Testing and deployment

### Daily Commands
- \`/good-morning\` - Start your day
- \`/phase\` - Check current phase
- \`/context\` - See where you left off

## Project Structure

\`\`\`
$PROJECT_NAME/
├── .aid/                # AID state tracking
│   ├── state.json       # Current phase (created by /aid-start)
│   └── context.json     # Work context
├── .claude/             # Commands (linked to AID)
├── skills/              # Skills (linked to AID)
├── docs/
│   ├── prd/PRD.md       # Product Requirements
│   └── tech-spec/TECH-SPEC.md  # Technical Spec
├── src/
│   ├── app/             # Next.js pages
│   └── components/      # React components
└── tests/               # Test files
\`\`\`
EOF

# Initialize git
if [ "$INIT_GIT" = true ]; then
    log_info "Initializing git repository..."
    git init --quiet
    git add .
    # A machine without a git identity (user.name/user.email) cannot commit;
    # the project is still usable, so warn instead of failing the whole script.
    if git commit -m "Initial commit: Project setup with AID methodology" --quiet; then
        log_success "Git repository initialized"
    else
        log_warning "git commit failed (is user.name/user.email set?). Commit the files yourself."
    fi
fi

# Install dependencies
if [ "$INSTALL_DEPS" = true ]; then
    log_info "Installing dependencies..."
    # Exception to AID's `npm ci` rule: a brand-new project has no package-lock.json
    # yet, so `npm ci` cannot run. `npm install` creates the lockfile; commit it.
    npm install --silent 2>/dev/null || npm install
    log_success "Dependencies installed"
fi

# Print success
echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}                    Project Created Successfully!                    ${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════════════${NC}"
echo ""
echo "Your project is ready at: $(pwd)"
echo ""
echo "Next steps:"
echo ""
echo "  1. Navigate to your project:"
echo "     cd $PROJECT_NAME"
echo ""
echo "  2. Open Claude Code:"
echo "     claude"
echo ""
echo "  3. Start AID (choose your role and phase 0-5; this creates .aid/state.json):"
echo "     /aid-start"
echo ""
if [ "$USE_SYMLINKS" = true ]; then
    echo -e "${BLUE}Note: This project uses symbolic links to AID.${NC}"
    echo "      Updates to AID will automatically apply here."
fi
echo ""
