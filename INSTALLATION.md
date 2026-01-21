# AI.D Installation Guide

Complete Installation Guide - For All Skill Levels

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

2. **This AI.D folder** - Download from GitHub

### Step-by-Step Installation

#### Step 1: Download Claude Code Desktop

1. Go to [claude.ai/download](https://claude.ai/download)
2. Click "Download for Windows" or "Download for Mac"
3. Install like any other app:
   - **Windows**: Double-click the installer, click "Next" until done
   - **Mac**: Drag to Applications folder

#### Step 2: Download AI.D

1. On this GitHub page, click the green **"Code"** button
2. Click **"Download ZIP"**
3. Find the downloaded ZIP file (usually in Downloads folder)
4. Extract/Unzip it:
   - **Windows**: Right-click → "Extract All"
   - **Mac**: Double-click the ZIP file
5. Move the folder somewhere you'll remember (e.g., Documents/AI.D)

#### Step 3: Open AI.D in Claude Code

1. Open Claude Code Desktop
2. Click **"Open Folder"** (or drag the AI.D folder into Claude Code)
3. Navigate to where you put AI.D and select it
4. You should see files in the sidebar

#### Step 4: Initialize AI.D

1. In the chat area, type: `/aid-init`
2. Press Enter
3. Follow Claude's instructions!

### After Installation

You're ready to go! See the [README.md](README.md) for your daily workflow and available commands.

---

## For Developers

### Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Node.js | 18+ | MCP servers, Storybook |
| Claude Code CLI | Latest | AI assistance |

### Quick Install

```bash
# Clone repository
git clone https://github.com/ilandahan/AID.git
cd AID

# Run automated install
./install.sh      # Mac/Linux
install.bat       # Windows
```

### Manual Installation

```bash
# 1. Install npm dependencies
npm install

# 2. Copy MCP template for your OS
cp .mcp.json.mac .mcp.json      # Mac
cp .mcp.json.windows .mcp.json  # Windows

# 3. Edit .mcp.json and add your API tokens

# 4. Initialize AI.D
# Open Claude Code and type: /aid-init
```

### Post-Installation

After installation, **restart Claude Code** to load MCP servers:

```bash
# Close Claude Code, then reopen in AI.D folder
cd AID
claude

# Verify MCP servers are loaded:
claude mcp list
```

---

## Linking to Existing Projects

AI.D works best when linked to your existing projects via **symbolic links**. Changes in AI.D automatically apply to all linked projects.

### How It Works

```
workspace/
├── AI.D/                      ← This repository (source)
│   ├── .claude/
│   │   ├── agents/
│   │   ├── skills/
│   │   ├── commands/
│   │   └── ...
│   └── CLAUDE.md
│
└── my-project/                ← Your project (linked)
    ├── .claude/
    │   ├── agents/    ───────→ AI.D/.claude/agents/    (symlink)
    │   ├── skills/    ───────→ AI.D/.claude/skills/    (symlink)
    │   ├── commands/  ───────→ AI.D/.claude/commands/  (symlink)
    │   ├── rules/     ───────→ AI.D/.claude/rules/     (symlink)
    │   ├── references/───────→ AI.D/.claude/references/(symlink)
    │   └── settings.json      (project copy)
    ├── CLAUDE.md      ───────→ AI.D/CLAUDE.md          (symlink)
    ├── .mcp.json              (project copy - your tokens)
    └── .aid/                  (project state)
```

### Using Link Scripts (Recommended)

#### Mac / Linux

```bash
cd AI.D
./link-project.sh /path/to/my-project
```

#### Windows (Run as Administrator or enable Developer Mode)

```cmd
cd AI.D
link-project.bat C:\path\to\my-project
```

**Note**: Windows requires Administrator privileges or Developer Mode enabled for symbolic links.

### What Gets Linked vs Copied

| Linked (Auto-Update) | Copied (Project-Specific) |
|----------------------|---------------------------|
| `.claude/commands/` | `.claude/settings.json` |
| `.claude/skills/` | `.aid/state.json` |
| `.claude/agents/` | `.aid/context.json` |
| `.claude/references/` | `.mcp.json` |
| `.claude/rules/` | `docs/` |
| `CLAUDE.md` | |

### Manual Linking (Alternative)

If you prefer copying instead of symlinks:

#### Mac / Linux

```bash
cd my-project

# Copy AI.D content
cp -r ../AI.D/.claude .claude
cp ../AI.D/CLAUDE.md CLAUDE.md
```

#### Windows

```cmd
cd my-project

# Copy AI.D content
xcopy /E /I "..\AI.D\.claude" ".claude"
copy "..\AI.D\CLAUDE.md" "CLAUDE.md"
```

### Initialize Your Project

```bash
# Open Claude Code in your project
cd my-project
claude

# Initialize AI.D phases
/aid-init
```

### Verify Setup

```bash
# Check symlinks exist
ls -la .claude/          # Should show -> AI.D/.claude/...
ls -la CLAUDE.md         # Should show -> AI.D/CLAUDE.md

# In Claude Code
/phase               # Should show "Phase 0: Discovery"
/good-morning        # Should run startup routine
```

### Benefits

| Benefit | Description |
|---------|-------------|
| **Auto-update** | Changes in AI.D instantly apply to all linked projects |
| **Clean separation** | AI.D tools separate from your code |
| **Multiple projects** | Same AI.D serves many projects |
| **Git-friendly** | Your project has its own Git history |
| **No re-linking** | Just `git pull` in AI.D - all projects update |

### Updating AI.D

With symbolic links, updating is simple:

```bash
cd ~/workspace/AI.D
git pull origin main

# That's it! All linked projects now use the updated AI.D
```

No need to re-run link scripts - symbolic links automatically point to the updated content.

---

## MCP Integrations Setup

MCP (Model Context Protocol) connects Claude to external tools.

### Configuration File

1. Copy the template for your OS:
   - **Windows**: Copy `.mcp.json.windows` to `.mcp.json`
   - **Mac**: Copy `.mcp.json.mac` to `.mcp.json`

2. Edit `.mcp.json` and add your API tokens

### Jira / Atlassian Setup

1. Go to [id.atlassian.com/manage-profile/security/api-tokens](https://id.atlassian.com/manage-profile/security/api-tokens)
2. Click "Create API token"
3. Copy the token
4. In `.mcp.json`, find the `jira` and `confluence` sections and update:

```json
"env": {
  "ATLASSIAN_SITE_URL": "https://your-domain.atlassian.net",
  "ATLASSIAN_USER_EMAIL": "your-email@company.com",
  "ATLASSIAN_API_TOKEN": "your-api-token"
}
```

### GitHub Setup

1. Go to [github.com/settings/tokens](https://github.com/settings/tokens)
2. Click "Generate new token (classic)"
3. Select scopes: `repo`, `read:org`
4. Copy the token
5. In `.mcp.json`, find the `github` section and update:

```json
"env": {
  "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_xxxxxxxxxxxx"
}
```

### Figma Setup

1. Open Figma → Settings → Account
2. Scroll to "Personal access tokens"
3. Generate new token
4. In `.mcp.json`, find the `figma` section and update:

```json
"env": {
  "FIGMA_API_KEY": "figd_xxxxxxxxxxxx"
}
```

### Chrome DevTools Setup

Start Chrome with debug port before using:

```bash
# Mac:
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222

# Windows:
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222
```

---

## Troubleshooting

### Common Issues

#### "Claude Code doesn't see commands"

1. Restart Claude Code after linking
2. Verify files exist: `ls .claude/commands/`
3. Check CLAUDE.md is readable: `cat CLAUDE.md`

#### "MCP server not connecting"

1. Check `.mcp.json` has correct tokens in the `env` sections
2. Check no extra spaces or quotes in token values
3. Restart Claude Code after changing `.mcp.json`
4. Run `claude mcp list` to see loaded servers

#### "Figma MCP not connecting"

1. Make sure Figma Desktop is open (not web)
2. Test: `curl http://127.0.0.1:3845/mcp`

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

1. Check token is in `.mcp.json` (in the correct server's `env` section)
2. Check no extra spaces or quotes
3. Check token hasn't expired
4. Restart Claude Code after changing `.mcp.json`

### Getting Help

1. **Describe the problem to Claude** - It can help diagnose issues
2. **Paste error messages** - Full error text is helpful
3. **Check the logs** - Claude Code shows connection status

### Reset Everything

If you need to start fresh:

```bash
# Reset AI.D state
/aid-reset

# Or manually delete
rm -rf .aid/
```

---

## Quick Reference

### Every Day
```
/good-morning       → Check systems, load context
/phase              → See current phase
```

### Phase Flow
```
/gate-check         → Check requirements
/phase-approve      → Human sign-off
/phase-advance      → Move to next phase
```

### When Working
```
/context            → Where am I?
/context-update     → Update progress
```

### Session Management
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
