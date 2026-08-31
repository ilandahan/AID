---
description: "Complete guided AID setup, step by step, for new users"
---

# /setup — Complete Guided Setup

Walk through the entire AID installation and configuration step-by-step.

## When to Use

- First time using AID in a new environment
- Setting up a fresh project with AID methodology
- Onboarding a new team member

## Process

1. **Check prerequisites**
   - Verify Node.js is installed
   - Verify Claude Code CLI is available
   - Check if `.claude/` directory exists

2. **Initialize AID structure**
   - Create `.aid/` directory with `state.json` and `context.json`
   - Create `.aid/qa/` directory for acceptance criteria
   - Verify `skills/` and `agents/` are populated

3. **Configure project**
   - Ask user for project name and description
   - Ask for primary role (PM, Developer, Tech Lead, QA, Data Scientist)
   - Set initial phase (typically Phase 0: Discovery)
   - Create `.aid/state.json` with initial values

4. **Install breather** (session boundaries)
   - Run `node integrations/breather/install.mjs` (works from the AID repo root;
     in a linked project, run it from the AID install directory)
   - Installs user-scope to `~/.claude`: presence tracking, break offers,
     handoffs, and the rest/usage status line — active in every project
   - Safe to re-run; it never replaces an existing custom statusLine
     without `--force`
   - Tell the user to restart Claude Code (or run `/hooks`) to activate it

5. **Verify installation**
   - Check all skill files are present
   - Check all agent files are present
   - Check all command files are accessible
   - Run a quick sanity check

6. **Show next steps**
   - Recommend `/good-morning` for daily startup
   - Recommend `/aid-start` to begin first session
   - Show available commands for their role

## Output

```
AID Setup Complete

Project: [name]
Role: [selected role]
Phase: 0 - Discovery

Next steps:
  /aid-start    — Begin your first work session
  /good-morning — Use this every morning to load context
  /context      — Check current work context anytime
```

## Related Commands

- `/aid-init` — Initialize phases (subset of setup)
- `/link-project` — Link an existing project to AID
- `/aid-start` — Start a work session
