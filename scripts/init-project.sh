#!/bin/bash

#==============================================================================
# AI Full Stack Development - Project Initialization Script
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

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
METHODOLOGY_DIR="$(dirname "$SCRIPT_DIR")"

# Usage
usage() {
    echo "Usage: $0 <project-name> [options]"
    echo ""
    echo "Options:"
    echo "  --template <name>   Use specific template (default: fullstack)"
    echo "  --no-git            Skip git initialization"
    echo "  --no-deps           Skip dependency installation"
    echo "  --help              Show this help message"
    echo ""
    echo "Templates:"
    echo "  fullstack           Full stack TypeScript project"
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
echo "║          AI Full Stack Development - New Project                  ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""
log_info "Creating project: $PROJECT_NAME"
log_info "Template: $TEMPLATE"
echo ""

# Create project directory
mkdir -p "$PROJECT_NAME"
cd "$PROJECT_NAME"

# Create directory structure
log_info "Creating directory structure..."

mkdir -p src/{components/{atoms,molecules,organisms,templates},pages,hooks,utils,types,api,styles}
mkdir -p tests/{unit,integration,e2e}
mkdir -p docs/{prd,tech-specs,jira,decisions}
mkdir -p .claude
mkdir -p skills

# Copy skills from methodology
log_info "Copying methodology skills..."

if [ -d "$METHODOLOGY_DIR/skills" ]; then
    # Copy each skill directory
    for skill_dir in "$METHODOLOGY_DIR/skills"/*; do
        skill_name=$(basename "$skill_dir")
        if [ -d "$skill_dir" ]; then
            cp -r "$skill_dir" "skills/"
            log_info "  - Copied: $skill_name"
        fi
    done
    log_success "Skills and commands copied successfully"
else
    log_warning "Skills directory not found at $METHODOLOGY_DIR/skills"
fi

# Copy prompts framework
log_info "Copying prompt framework..."

mkdir -p docs/prompts
if [ -f "$METHODOLOGY_DIR/docs/prompts/7-component-framework.md" ]; then
    cp "$METHODOLOGY_DIR/docs/prompts/7-component-framework.md" "docs/prompts/"
    log_success "Prompt framework copied"
else
    log_warning "Prompt framework not found"
fi

# Create package.json
log_info "Creating package.json..."

cat > package.json << EOF
{
  "name": "$PROJECT_NAME",
  "version": "0.1.0",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "test": "vitest",
    "test:coverage": "vitest --coverage",
    "lint": "eslint src --ext ts,tsx --report-unused-disable-directives --max-warnings 0",
    "type-check": "tsc --noEmit",
    "format": "prettier --write src"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "@typescript-eslint/eslint-plugin": "^6.0.0",
    "@typescript-eslint/parser": "^6.0.0",
    "@vitejs/plugin-react": "^4.0.0",
    "eslint": "^8.45.0",
    "eslint-plugin-react-hooks": "^4.6.0",
    "eslint-plugin-react-refresh": "^0.4.0",
    "prettier": "^3.0.0",
    "typescript": "^5.0.0",
    "vite": "^4.4.0",
    "vitest": "^0.34.0",
    "@vitest/coverage-v8": "^0.34.0"
  }
}
EOF

# Create TypeScript config
log_info "Creating TypeScript configuration..."

cat > tsconfig.json << EOF
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"],
      "@/components/*": ["src/components/*"],
      "@/atoms/*": ["src/components/atoms/*"],
      "@/molecules/*": ["src/components/molecules/*"],
      "@/organisms/*": ["src/components/organisms/*"],
      "@/templates/*": ["src/components/templates/*"],
      "@/hooks/*": ["src/hooks/*"],
      "@/utils/*": ["src/utils/*"],
      "@/types/*": ["src/types/*"],
      "@/api/*": ["src/api/*"]
    }
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
EOF

cat > tsconfig.node.json << EOF
{
  "compilerOptions": {
    "composite": true,
    "skipLibCheck": true,
    "module": "ESNext",
    "moduleResolution": "bundler",
    "allowSyntheticDefaultImports": true
  },
  "include": ["vite.config.ts"]
}
EOF

# Create Vite config
log_info "Creating Vite configuration..."

cat > vite.config.ts << EOF
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
});
EOF

# Create Vitest config
cat > vitest.config.ts << EOF
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./tests/setup.ts'],
    coverage: {
      reporter: ['text', 'html'],
      exclude: ['node_modules/', 'tests/'],
    },
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
});
EOF

# Create test setup
mkdir -p tests
cat > tests/setup.ts << EOF
import '@testing-library/jest-dom';
EOF

# Create ESLint config
cat > .eslintrc.cjs << EOF
module.exports = {
  root: true,
  env: { browser: true, es2020: true },
  extends: [
    'eslint:recommended',
    'plugin:@typescript-eslint/recommended',
    'plugin:react-hooks/recommended',
  ],
  ignorePatterns: ['dist', '.eslintrc.cjs'],
  parser: '@typescript-eslint/parser',
  plugins: ['react-refresh'],
  rules: {
    'react-refresh/only-export-components': [
      'warn',
      { allowConstantExport: true },
    ],
  },
};
EOF

# Create Prettier config
cat > .prettierrc << EOF
{
  "semi": true,
  "singleQuote": true,
  "tabWidth": 2,
  "trailingComma": "es5"
}
EOF

# Create .gitignore
cat > .gitignore << EOF
# Dependencies
node_modules/

# Build
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

# Create Claude configuration
log_info "Creating Claude Code configuration..."

# Create .mcp.json (MCP server configuration - project level)
cat > .mcp.json << 'EOF'
{
  "$schema": "https://raw.githubusercontent.com/anthropics/anthropic-quickstarts/main/mcp-config-schema.json",
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_PERSONAL_ACCESS_TOKEN}"
      }
    },
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "."
      ]
    }
  }
}
EOF

# Create .claude/settings.json (Claude-specific settings only)
mkdir -p .claude
cat > .claude/settings.json << 'EOF'
{
  "$schema": "https://schemas.claude.ai/settings.json",
  "skills": {
    "system-architect": {
      "path": "./skills/system-architect/SKILL.md",
      "description": "Technical specifications & SaaS architecture patterns"
    },
    "atomic-design": {
      "path": "./skills/atomic-design/SKILL.md",
      "description": "Atomic design system component development"
    },
    "atomic-page-builder": {
      "path": "./skills/atomic-page-builder/SKILL.md",
      "description": "Page composition using existing components"
    },
    "code-review": {
      "path": "./skills/code-review/SKILL.md",
      "description": "Code quality review and best practices"
    },
    "test-driven": {
      "path": "./skills/test-driven/SKILL.md",
      "description": "TDD methodology and test quality"
    }
  },
  "hooks": {
    "preCommit": {
      "enabled": true,
      "commands": ["npm run type-check", "npm run lint"]
    }
  },
  "permissions": {
    "allow": [
      "Bash(npm run *)",
      "Bash(npx *)",
      "Bash(git *)",
      "Read(*)",
      "Write(src/**)",
      "Write(tests/**)",
      "Write(docs/**)",
      "Write(skills/**)"
    ]
  }
}
EOF

# Create .env.example
cat > .env.example << 'EOF'
# GitHub Integration
# Create a Personal Access Token at: https://github.com/settings/tokens
GITHUB_PERSONAL_ACCESS_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx

# Jira / Atlassian Integration (optional)
# Get your API token from: https://id.atlassian.com/manage-profile/security/api-tokens
# ATLASSIAN_SITE_URL=https://your-domain.atlassian.net
# ATLASSIAN_USER_EMAIL=your-email@company.com
# ATLASSIAN_API_TOKEN=your-api-token-here

# Database (optional)
# POSTGRES_CONNECTION_STRING=postgresql://user:password@localhost:5432/mydb
EOF

# Create minimal CLAUDE.md that points to documentation
cat > CLAUDE.md << 'CLAUDEMD'
# $PROJECT_NAME

AI Full Stack Development methodology project.

## Commands
Read `skills/commands/*.md` for available commands:
- `/phase`, `/prd`, `/tech-spec`, `/jira-breakdown`
- `/test-review`, `/code-review`, `/build-page`

## Skills
Read skill before using: `skills/<name>/SKILL.md`

## Prompts
See `docs/prompts/7-component-framework.md`

## Output Locations
- PRD → `docs/prd/`
- Tech Spec → `docs/tech-specs/`
- Jira → `docs/jira/`
CLAUDEMD

# Replace placeholder with actual project name
sed -i "s/\$PROJECT_NAME/$PROJECT_NAME/g" CLAUDE.md

# Create README
cat > README.md << EOF
# $PROJECT_NAME

## Getting Started

### Prerequisites
- Node.js 18+
- npm or yarn

### Installation
\`\`\`bash
npm install
\`\`\`

### Development
\`\`\`bash
npm run dev
\`\`\`

### Testing
\`\`\`bash
npm run test
\`\`\`

## Project Structure
See [CLAUDE.md](./CLAUDE.md) for detailed project information.

## License
[Add license here]
EOF

# Create basic entry files
log_info "Creating source files..."

cat > src/main.tsx << EOF
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './styles/index.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
EOF

cat > src/App.tsx << EOF
function App() {
  return (
    <div>
      <h1>$PROJECT_NAME</h1>
      <p>Welcome to your new project!</p>
    </div>
  );
}

export default App;
EOF

cat > src/styles/index.css << EOF
:root {
  /* Design tokens will be added here */
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  line-height: 1.5;
}
EOF

cat > index.html << EOF
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>$PROJECT_NAME</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
EOF

# Initialize git
if [ "$INIT_GIT" = true ]; then
    log_info "Initializing git repository..."
    git init --quiet
    git add .
    git commit -m "Initial commit: Project setup with AI Full Stack methodology" --quiet
    log_success "Git repository initialized"
fi

# Install dependencies
if [ "$INSTALL_DEPS" = true ]; then
    log_info "Installing dependencies..."
    npm install --silent
    log_success "Dependencies installed"
fi

# Print success
echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}                    Project Created Successfully!                    ${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════════════${NC}"
echo ""
echo "Next steps:"
echo ""
echo "  1. Navigate to your project:"
echo "     cd $PROJECT_NAME"
echo ""
echo "  2. Start development server:"
echo "     npm run dev"
echo ""
echo "  3. Begin with Discovery phase:"
echo "     claude \"/phase 1\""
echo ""
echo "Documentation: See CLAUDE.md for project details"
echo ""
