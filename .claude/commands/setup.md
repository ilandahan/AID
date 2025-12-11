# /setup

Complete guided setup for AID methodology - designed for non-technical users.

## Overview

This command walks you through the entire AID installation process step-by-step, in plain language.

## Instructions for Claude

When the user runs `/setup`, guide them through this process conversationally:

---

### STEP 1: Welcome & Check Current State

First, display this welcome message:

```
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║                    Welcome to AID Setup                          ║
║                                                                  ║
║                 AI Development Methodology                       ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝

I'll guide you through each installation step.
No technical knowledge required - just follow along!
```

Then check what's already installed by running these commands silently:
- `node --version`
- `python3 --version` or `python --version`
- `git --version`
- `docker --version`

Report the status to the user in a friendly way.

---

### STEP 2: Install Missing Prerequisites

For each missing tool, explain what it is and offer to install it:

**If Node.js is missing or old:**
```
Node.js is what runs JavaScript code - we need version 18 or higher.

Want me to install it for you? (y/n)
```

If yes, run the appropriate install command based on OS.

**If Python is missing or old (< 3.11):**
```
Python is a programming language needed for some tools.

Want me to install it? (y/n)
```

**If Git is missing:**
```
Git helps track changes to your code.

Want me to install it? (y/n)
```

**If Docker is missing (optional):**
```
Docker makes it easy to run databases. Optional but recommended.

Want me to install it? (y/n)
```

---

### STEP 3: Install NPM Dependencies

```
Installing Node.js packages...
This might take a few minutes - grab a coffee!
```

Run: `npm install`

Then report success:
```
Packages installed successfully!
```

---

### STEP 4: Setup Environment File

```
Now let's set up your configuration file.
I need a few details from you (if you have them):
```

Check if `.env` exists. If not, copy from `.env.example`:
```bash
cp .env.example .env
```

Then ask the user for each key interactively:

```
GitHub Token (optional)

This lets me work with GitHub for you.

How to get it:
1. Go to: https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Give it a name and select permissions: repo, workflow
4. Copy the token

Paste the token (or press Enter to skip):
```

```
Jira/Atlassian Token (optional)

This lets me create Jira issues.

How to get it:
1. Go to: https://id.atlassian.com/manage-profile/security/api-tokens
2. Click "Create API token"
3. Copy the token

Paste the token (or press Enter to skip):
```

```
Figma Token (optional)

This lets me extract designs from Figma.

How to get it:
1. Open Figma and go to Settings
2. Account → Personal access tokens
3. Create a new token

Paste the token (or press Enter to skip):
```

For each token provided, update the `.env` file.

---

### STEP 5: Install MCP Servers

```
Installing MCP Servers (these connect Claude to external tools)...
```

Run these commands:
```bash
npx -y @modelcontextprotocol/server-github --help
npx -y @modelcontextprotocol/server-atlassian --help
npx -y @modelcontextprotocol/server-postgres --help
npx -y @modelcontextprotocol/server-filesystem --help
npx -y chrome-devtools-mcp@latest --help
```

Report progress for each.

---

### STEP 6: Verify Installation

Run the test script:
```bash
bash scripts/test-methodology.sh
```

If all tests pass:
```
All tests passed!
```

---

### STEP 7: Initialize AID (if new project)

Ask:
```
Want me to initialize the AID methodology now?

This creates the .aid/ folder and starts you at Phase 1 (PRD)

(y/n)
```

If yes, run `/aid-init` flow.

---

### STEP 8: Final Summary

```
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║                      Setup Complete!                             ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝

What was installed:

  ✅ Node.js [version]
  ✅ Python [version]
  ✅ Git [version]
  ✅ npm packages (27 dependencies)
  ✅ MCP Servers (GitHub, Jira, Figma, PostgreSQL)
  [✅/⏭️] Docker
  [✅/⏭️] Environment tokens

═══════════════════════════════════════════════════════════════════

⚠️  IMPORTANT! Please restart Claude Code to load MCP servers

    Close Claude Code completely and reopen it.

═══════════════════════════════════════════════════════════════════

Useful commands:

   /good-morning  - Start your workday (check status + continue)
   /phase         - Show current phase
   /context       - Where did I leave off?
   /aid-test      - Run tests

═══════════════════════════════════════════════════════════════════

Ready to start!

Just tell me what you want to build, and I'll guide you.

═══════════════════════════════════════════════════════════════════
```

---

## Error Handling

If any step fails, explain in simple terms:

```
Something didn't work...

The problem: [simple explanation]

What to do:
[clear steps]

Or just send me the error message and I'll help.
```

---

## Notes

- Be patient and encouraging
- Offer to skip optional steps
- If user seems confused, offer simpler explanations
- Remember: the goal is that ANYONE can set this up
