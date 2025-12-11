# Complete Dependencies Overview

Full E2E stack dependencies for AI Full Stack Development Methodology.

## 📋 System Requirements

| Requirement | Version | Purpose |
|-------------|---------|---------|
| Node.js | 18.0.0+ | Runtime environment |
| npm | 8.0.0+ | Package manager |
| Python | 3.11+ | Scripts and backend tools |
| Docker | 20.0.0+ | Optional - containerized deployment |
| Docker Compose | 2.0.0+ | Optional - multi-container orchestration |
| PostgreSQL | 16+ | Database (via Docker or local) |

---

## 🎯 Core Production Dependencies

Required for the application to run:

```json
{
  "next": "^16.0.7",           // React framework with SSR
  "react": "^19.2.1",          // UI library
  "react-dom": "^19.2.1",      // React DOM renderer
  "sass": "^1.94.2",           // CSS preprocessor for styling
  "pg": "^8.16.3",             // PostgreSQL client
  "bcryptjs": "^2.4.3",        // Password hashing
  "jsonwebtoken": "^9.0.2",    // JWT authentication tokens
  "clsx": "^2.1.1",            // Utility for constructing className strings
  "@prisma/client": "^6.1.0"   // Prisma ORM client
}
```

**Total production dependencies: 9 packages**

---

## 🛠️ Development Dependencies

### TypeScript & Type Definitions

```json
{
  "typescript": "^5.9.3",
  "@types/node": "^24.10.1",
  "@types/react": "^19.2.7",
  "@types/react-dom": "^19.2.3",
  "@types/pg": "^8.15.6",
  "@types/bcryptjs": "^2.4.6",
  "@types/jsonwebtoken": "^9.0.7",
  "@types/supertest": "^6.0.3"
}
```

### Testing Framework

```json
{
  "jest": "^29.7.0",
  "jest-environment-jsdom": "^29.7.0",
  "ts-jest": "^29.4.6",
  "@testing-library/jest-dom": "^6.9.1",
  "@testing-library/react": "^16.3.0",
  "@testing-library/user-event": "^14.6.1",
  "supertest": "^7.1.4"
}
```

### Browser Automation

```json
{
  "puppeteer": "^24.32.1"      // Headless browser testing + Chromium
}
```

### Database & Build Tools

```json
{
  "prisma": "^6.1.0",          // Prisma ORM CLI
  "@svgr/webpack": "^8.1.0"    // SVG to React component transformer
}
```

**Total dev dependencies: 18 packages**

---

## 🐘 Database (PostgreSQL)

### Option 1: Docker (Recommended)

```bash
# Start PostgreSQL + pgAdmin
docker-compose up -d postgres pgadmin

# Verify containers
docker ps

# Check health
docker logs app-postgres
```

### Option 2: Local Installation

```bash
# Create database
psql -U postgres
CREATE DATABASE app_db;
CREATE USER app_user WITH PASSWORD 'app_password';
GRANT ALL PRIVILEGES ON DATABASE app_db TO app_user;
```

### Default Configuration

```bash
DB_HOST=localhost
DB_PORT=5432
DB_USER=app_user
DB_PASSWORD=app_password
DB_NAME=app_db
```

---

## 🤖 MCP Server Dependencies

Enable AI-assisted development with Claude:

| MCP Server | Command | Purpose |
|------------|---------|---------|
| Chrome DevTools | `npx chrome-devtools-mcp@latest` | Browser automation |
| Atlassian (Jira) | `npx @modelcontextprotocol/server-atlassian` | Project management |
| GitHub | `npx @modelcontextprotocol/server-github` | Repository operations |
| PostgreSQL | `npx @modelcontextprotocol/server-postgres` | Database queries |
| Filesystem | `npx @modelcontextprotocol/server-filesystem` | File operations |

---

## 📦 Installation Guide

### Step 1: System Prerequisites

```bash
# Check Node.js version (must be 18+)
node --version

# Check npm version
npm --version

# Check Docker (optional)
docker --version
docker-compose --version
```

### Step 2: Install Dependencies

```bash
# Install all npm dependencies
npm install

# This installs:
# - 7 production dependencies
# - 16 development dependencies
# - ~1000+ transitive dependencies
```

### Step 3: Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your configuration
```

### Step 4: Database Setup

```bash
# Using Docker (recommended)
docker-compose up -d postgres pgadmin

# Or local PostgreSQL
createdb app_db
```

### Step 5: Start Development

```bash
npm run dev
# Opens http://localhost:3000
```

---

## 🧪 Testing Setup

```bash
# Run all tests
npm test

# Watch mode
npm run test:watch

# Coverage report
npm run test:coverage
```

### Test Coverage Requirements

| Metric | Target |
|--------|--------|
| Branches | 70% |
| Functions | 70% |
| Lines | 70% |
| Statements | 70% |

---

## 🐳 Docker Deployment

```bash
# Build and start all services
docker-compose up -d --build

# Services:
# - Next.js app (port 3000)
# - PostgreSQL 16 (port 5432)
# - pgAdmin (port 5050)

# View logs
docker-compose logs -f app

# Stop services
docker-compose down

# Stop and remove data
docker-compose down -v
```

---

## 📜 Available Scripts

| Script | Command | Purpose |
|--------|---------|---------|
| `dev` | `npm run dev` | Start dev server (port 3000) |
| `build` | `npm run build` | Build production bundle |
| `start` | `npm run start` | Start production server |
| `lint` | `npm run lint` | Run ESLint |
| `test` | `npm run test` | Run Jest tests |
| `test:watch` | `npm run test:watch` | Tests in watch mode |
| `test:coverage` | `npm run test:coverage` | Generate coverage |
| `db:migrate` | `npm run db:migrate` | Run migrations |
| `generate:keys` | `npm run generate:keys` | Create JWT keys |
| `clean:recordings` | `npm run clean:recordings` | Delete old test recordings |

---

## 🔌 Ports Used

| Service | Port | URL |
|---------|------|-----|
| Next.js Dev | 3000 | http://localhost:3000 |
| PostgreSQL | 5432 | postgresql://localhost:5432 |
| pgAdmin | 5050 | http://localhost:5050 |

---

## 📁 Configuration Files

| File | Purpose |
|------|---------|
| `package.json` | npm dependencies and scripts |
| `tsconfig.json` | TypeScript configuration |
| `jest.config.js` | Jest testing config |
| `docker-compose.yml` | Docker services |
| `Dockerfile` | Application container |
| `.env` | Environment variables |
| `.mcp.json` | MCP server configuration |

---

## 📊 Dependency Statistics

| Category | Count |
|----------|-------|
| Production dependencies | 9 |
| Development dependencies | 18 |
| **Total direct** | **27** |
| Transitive dependencies | ~1000+ |
| node_modules size | ~500-800 MB |

---

## 🔧 Troubleshooting

### Port 3000 already in use

```bash
# Find process
lsof -i :3000  # macOS/Linux

# Use different port
PORT=3001 npm run dev
```

### PostgreSQL connection failed

```bash
# Check if running
docker ps | grep postgres

# Check logs
docker logs app-postgres

# Restart
docker-compose restart postgres
```

### Puppeteer/Chromium issues

```bash
# Install Chromium dependencies (Linux)
apt-get install -y chromium-browser

# Or use existing Chrome
PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true npm install
```
