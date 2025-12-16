# AID Installation Guide

<div align="center">

**מדריך התקנה מלא - מתאים לכל רמות הניסיון**

*Complete Installation Guide - For All Skill Levels*

</div>

---

## Quick Navigation

- [For Beginners (No Technical Knowledge)](#for-beginners-no-technical-knowledge)
- [For Developers](#for-developers)
- [Linking to Existing Projects](#linking-to-existing-projects)
- [MCP Integrations Setup](#mcp-integrations-setup)
- [Troubleshooting](#troubleshooting)

---

## For Beginners (No Technical Knowledge)

### What You Need

1. **Claude Code** - The AI assistant (choose one option):
   - [Claude Code Desktop App](https://claude.ai/download) - Easiest, just download and install
   - Claude Code Terminal - For those comfortable with command line

2. **This AID folder** - Download from GitHub

### Step-by-Step Installation

#### Step 1: Download Claude Code Desktop

1. Go to [claude.ai/download](https://claude.ai/download)
2. Click "Download for Windows" or "Download for Mac"
3. Install like any other app:
   - **Windows**: Double-click the installer, click "Next" until done
   - **Mac**: Drag to Applications folder

#### Step 2: Download AID

1. On this GitHub page, click the green **"Code"** button
2. Click **"Download ZIP"**
3. Find the downloaded ZIP file (usually in Downloads folder)
4. Extract/Unzip it:
   - **Windows**: Right-click → "Extract All"
   - **Mac**: Double-click the ZIP file
5. Move the folder somewhere you'll remember (e.g., Documents/AID)

#### Step 3: Open AID in Claude Code

1. Open Claude Code Desktop
2. Click **"Open Folder"** (or drag the AID folder into Claude Code)
3. Navigate to where you put AID and select it
4. You should see files in the sidebar

#### Step 4: Run Setup

1. In the chat area, type: `/setup`
2. Press Enter
3. Follow Claude's instructions!

### What Happens During Setup?

```
┌─────────────────────────────────────────────────────────────┐
│  /setup will:                                                │
│                                                              │
│  ✅ Check what's installed on your computer                 │
│  ✅ Offer to install missing tools (you decide yes/no)      │
│  ✅ Install required packages                               │
│  ✅ Help set up API tokens (optional, with instructions)    │
│  ✅ Run tests to make sure everything works                 │
│  ✅ Give you a summary of what to do next                   │
│                                                              │
│  Time: About 5-10 minutes                                    │
└─────────────────────────────────────────────────────────────┘
```

### After Setup - Your Daily Workflow

```
Every morning:
  Type: /good-morning
  → Claude checks all systems
  → Shows where you left off
  → Asks what to work on

During work:
  Type: /phase
  → See current phase status

When stuck:
  Just describe your problem to Claude
  → Paste any error messages
  → Claude will help fix it
```

---

## For Developers

### Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Node.js | 18+ | Package management, scripts |
| Python | 3.11+ | Memory system, scripts |
| Docker | Latest | Database, services |
| Claude Code CLI | Latest | AI assistance |

### Quick Install

```bash
# Clone repository
git clone https://github.com/ilandahan/AID.git
cd AID

# Run automated install
./install.sh

# Or use make
make install
```

### Manual Installation

```bash
# 1. Install npm dependencies
npm install

# 2. Copy environment template
cp .env.example .env

# 3. Start Docker services (optional)
docker-compose up -d postgres pgadmin

# 4. Initialize AID
# Open Claude Code and type: /aid-init
```

### Post-Installation (Required!)

After installation, **restart Claude Code** to load MCP servers:

```bash
# Close Claude Code, then:
cd AID
claude

# Verify MCP servers are loaded:
claude mcp list
```

---

## Linking to Existing Projects

### Recommended Structure

```
📁 workspace/
├── 📁 AID/                    ← This repository
│   ├── .claude/commands/
│   ├── skills/
│   └── CLAUDE.md
│
└── 📁 my-project/             ← Your project (separate folder)
    ├── .claude → ../AID/.claude        ← Symbolic link
    ├── CLAUDE.md → ../AID/CLAUDE.md    ← Symbolic link
    └── .aid/                           ← Your project state
```

### Creating Symbolic Links

#### Mac / Linux

```bash
cd my-project

# Create links
ln -s ../AID/.claude .claude
ln -s ../AID/CLAUDE.md CLAUDE.md
ln -s ../AID/skills skills
```

#### Windows (PowerShell as Administrator)

```powershell
cd my-project

# Create links
New-Item -ItemType SymbolicLink -Path ".claude" -Target "..\AID\.claude"
New-Item -ItemType SymbolicLink -Path "CLAUDE.md" -Target "..\AID\CLAUDE.md"
New-Item -ItemType SymbolicLink -Path "skills" -Target "..\AID\skills"
```

#### Windows (Command Prompt as Administrator)

```cmd
cd my-project

mklink /D .claude ..\AID\.claude
mklink CLAUDE.md ..\AID\CLAUDE.md
mklink /D skills ..\AID\skills
```

### Initialize Your Project

```bash
# Open Claude Code in your project
cd my-project
claude

# Initialize AID phases
/aid-init
```

### Verify Setup

```bash
# Check symbolic links work
ls -la .claude        # Should show link to ../AID/.claude
cat CLAUDE.md         # Should display AID instructions

# In Claude Code
/phase               # Should show "Phase 1: PRD"
/good-morning        # Should run startup routine
```

### Benefits

| Benefit | Description |
|---------|-------------|
| **Clean separation** | AID tools separate from your code |
| **Easy updates** | `git pull` in AID folder updates all projects |
| **Multiple projects** | Same AID serves many projects |
| **Git-friendly** | Your project has its own Git history |

### Updating AID

```bash
cd ~/workspace/AID
git pull origin main
# All linked projects automatically get the update!
```

---

## MCP Integrations Setup

MCP (Model Context Protocol) connects Claude to external tools.

### Configuration File

MCP servers are configured in `.mcp.json`:

```json
{
  "mcpServers": {
    "jira": { ... },
    "github": { ... },
    "figma": { ... },
    "chrome-devtools": { ... }
  }
}
```

### Environment Variables

Copy `.env.example` to `.env` and fill in your values:

```bash
# Copy template
cp .env.example .env

# Edit with your values
nano .env  # or open in any text editor
```

### Jira / Atlassian Setup

1. Go to [id.atlassian.com/manage-profile/security/api-tokens](https://id.atlassian.com/manage-profile/security/api-tokens)
2. Click "Create API token"
3. Copy the token

```bash
# In .env file:
ATLASSIAN_SITE_URL=https://your-domain.atlassian.net
ATLASSIAN_USER_EMAIL=your-email@company.com
ATLASSIAN_API_TOKEN=your-api-token
```

### GitHub Setup

1. Go to [github.com/settings/tokens](https://github.com/settings/tokens)
2. Click "Generate new token (classic)"
3. Select scopes: `repo`, `read:org`
4. Copy the token

```bash
# In .env file:
GITHUB_PERSONAL_ACCESS_TOKEN=ghp_xxxxxxxxxxxx
```

### Figma Setup

**Option A: API Token**

1. Open Figma → Settings → Account
2. Scroll to "Personal access tokens"
3. Generate new token

```bash
# In .env file:
FIGMA_API_KEY=figd_xxxxxxxxxxxx
```

**Option B: Dev Mode (Recommended for design tokens)**

1. Open Figma Desktop app
2. Press Shift+D to enter Dev Mode
3. In the inspect panel, enable "MCP Server"
4. Server runs at `http://127.0.0.1:3845/mcp`

### Chrome DevTools Setup

```bash
# Start Chrome with debug port
# Mac:
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222

# Windows:
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222

# Test connection
curl http://localhost:9222/json
```

---

## Troubleshooting

### Common Issues

#### "Symbolic links not working"

**Windows:**
- Run PowerShell/Command Prompt as Administrator
- Or enable Developer Mode:
  - Settings → Update & Security → For Developers → Developer Mode

**Mac/Linux:**
- Check path is correct: `ls -la .claude`
- Make sure you're in the right directory

#### "Claude Code doesn't see commands"

1. Restart Claude Code after creating links
2. Verify links exist: `ls .claude/commands/`
3. Check CLAUDE.md is readable: `cat CLAUDE.md`

#### "Docker not running"

```bash
# Mac
open -a Docker

# Windows
# Start Docker Desktop from Start Menu

# Check status
docker ps
```

#### "Figma MCP not connecting"

1. Make sure Figma Desktop is open (not web)
2. Enter Dev Mode (Shift+D)
3. Enable MCP in inspect panel
4. Test: `curl http://127.0.0.1:3845/mcp`

#### "Phase gate violation"

This means you're trying to do work from a later phase.

```bash
# Check current phase
/phase

# See what's needed
/gate-check

# Complete current phase first!
```

#### "API token not working"

1. Check token is in `.env` file
2. Check no extra spaces or quotes
3. Check token hasn't expired
4. Restart Claude Code after changing `.env`

### Getting Help

1. **Describe the problem to Claude** - It can help diagnose issues
2. **Paste error messages** - Full error text is helpful
3. **Check the logs** - Claude Code shows connection status

### Reset Everything

If you need to start fresh:

```bash
# Reset AID state
/aid reset --confirm

# Or manually delete
rm -rf .aid/
rm -rf ~/.aid/
```

---

## Quick Reference

### First Time
```
/setup              → Complete guided installation
```

### Every Day
```
/good-morning       → Check systems, load context
/phase              → See current phase
```

### Phase Flow
```
/aid-init           → Initialize phases
/gate-check         → Check requirements
/phase-approve      → Human sign-off
/phase-advance      → Move to next phase
```

### When Working
```
/context            → Where am I?
/context-update     → Update progress
```

### Learning
```
/aid-start          → Start session with role
/aid-end            → End phase, give feedback
/aid-improve        → Run learning cycle
```

---

## Support

If something doesn't work:
1. Describe the problem to Claude
2. Paste any error messages you see
3. Claude will help you fix it

For bugs or feature requests: [GitHub Issues](https://github.com/ilandahan/AID/issues)

---

*[Back to README](README.md)*
