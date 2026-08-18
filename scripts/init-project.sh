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

if [ -d "$PROJECT_NAME" ]; then
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

# Create .aid directory for state tracking
log_info "Initializing AID phase tracking..."
mkdir -p .aid/approvals

# Create state.json (Phase 1: PRD)
cat > .aid/state.json << 'EOF'
{
  "current_phase": 1,
  "phase_name": "PRD",
  "project_name": "PROJECT_NAME_PLACEHOLDER",
  "initialized_at": "TIMESTAMP_PLACEHOLDER",
  "phases": {
    "1": { "name": "PRD", "status": "in_progress", "started_at": "TIMESTAMP_PLACEHOLDER" },
    "2": { "name": "Tech Spec", "status": "locked" },
    "3": { "name": "Breakdown", "status": "locked" },
    "4": { "name": "Development", "status": "locked" },
    "5": { "name": "QA & Ship", "status": "locked" }
  }
}
EOF

# Replace placeholders
TIMESTAMP=$(date -Iseconds 2>/dev/null || date +"%Y-%m-%dT%H:%M:%S")
sed -i "s/PROJECT_NAME_PLACEHOLDER/$PROJECT_NAME/g" .aid/state.json 2>/dev/null || \
    sed -i '' "s/PROJECT_NAME_PLACEHOLDER/$PROJECT_NAME/g" .aid/state.json
sed -i "s/TIMESTAMP_PLACEHOLDER/$TIMESTAMP/g" .aid/state.json 2>/dev/null || \
    sed -i '' "s/TIMESTAMP_PLACEHOLDER/$TIMESTAMP/g" .aid/state.json

# Create context.json
cat > .aid/context.json << 'EOF'
{
  "last_updated": "TIMESTAMP_PLACEHOLDER",
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
  "notes": "Project initialized. Start with /prd to create Product Requirements Document."
}
EOF

sed -i "s/TIMESTAMP_PLACEHOLDER/$TIMESTAMP/g" .aid/context.json 2>/dev/null || \
    sed -i '' "s/TIMESTAMP_PLACEHOLDER/$TIMESTAMP/g" .aid/context.json

log_success "AID state initialized at Phase 1 (PRD)"

# Link or copy AID files
if [ "$USE_SYMLINKS" = true ]; then
    log_info "Creating symbolic links to AID..."

    # Create relative path to AID from project
    RELATIVE_AID="../$(basename "$AID_DIR")"

    # Create symbolic links
    ln -s "$RELATIVE_AID/.claude" .claude 2>/dev/null || {
        # Windows or symlink failed - try with full path
        ln -s "$AID_DIR/.claude" .claude 2>/dev/null || {
            log_warning "Symbolic link failed. Copying instead."
            USE_SYMLINKS=false
        }
    }

    if [ "$USE_SYMLINKS" = true ]; then
        ln -s "$RELATIVE_AID/CLAUDE.md" CLAUDE.md 2>/dev/null || ln -s "$AID_DIR/CLAUDE.md" CLAUDE.md
        ln -s "$RELATIVE_AID/skills" skills 2>/dev/null || ln -s "$AID_DIR/skills" skills
        log_success "Symbolic links created"
        log_info "  .claude -> $RELATIVE_AID/.claude"
        log_info "  CLAUDE.md -> $RELATIVE_AID/CLAUDE.md"
        log_info "  skills -> $RELATIVE_AID/skills"
    fi
fi

if [ "$USE_SYMLINKS" = false ]; then
    log_info "Copying AID files..."

    # Copy .claude directory
    if [ -d "$AID_DIR/.claude" ]; then
        cp -r "$AID_DIR/.claude" .claude
        log_info "  Copied: .claude/"
    fi

    # Copy CLAUDE.md
    if [ -f "$AID_DIR/CLAUDE.md" ]; then
        cp "$AID_DIR/CLAUDE.md" CLAUDE.md
        log_info "  Copied: CLAUDE.md"
    fi

    # Copy skills
    if [ -d "$AID_DIR/skills" ]; then
        cp -r "$AID_DIR/skills" skills
        log_info "  Copied: skills/"
    fi

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

# Create .env.example
cat > .env.example << 'EOF'
# Application
NODE_ENV=development
NEXT_PUBLIC_APP_URL=http://localhost:3000

# Database (optional)
DATABASE_URL=postgresql://user:password@localhost:5432/mydb

# Authentication (optional)
NEXTAUTH_SECRET=your-secret-key
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

# Create docs placeholders
cat > docs/PRD.md << 'EOF'
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

cat > docs/TECH-SPEC.md << 'EOF'
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
│   ├── state.json       # Current phase
│   └── context.json     # Work context
├── .claude/             # Commands (linked to AID)
├── skills/              # Skills (linked to AID)
├── docs/
│   ├── PRD.md           # Product Requirements
│   └── TECH-SPEC.md     # Technical Spec
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
    git commit -m "Initial commit: Project setup with AID methodology" --quiet
    log_success "Git repository initialized"
fi

# Install dependencies
if [ "$INSTALL_DEPS" = true ]; then
    log_info "Installing dependencies..."
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
echo -e "${YELLOW}Current Phase: 1 - PRD${NC}"
echo ""
echo "Next steps:"
echo ""
echo "  1. Navigate to your project:"
echo "     cd $PROJECT_NAME"
echo ""
echo "  2. Open Claude Code:"
echo "     claude"
echo ""
echo "  3. Check your phase status:"
echo "     /phase"
echo ""
echo "  4. Start creating your PRD:"
echo "     /prd"
echo ""
if [ "$USE_SYMLINKS" = true ]; then
    echo -e "${BLUE}Note: This project uses symbolic links to AID.${NC}"
    echo "      Updates to AID will automatically apply here."
fi
echo ""
