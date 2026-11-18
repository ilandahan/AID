---
description: "Complete guided AID setup, step by step, for new users"
disable-model-invocation: true
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
   - Create `.aid/` directory with `context.json` (`state.json` is created in step 3 by
     `aid_session.py`, never written directly)
   - Create `.aid/qa/` directory for acceptance criteria
   - Verify `skills/` and `agents/` are populated

3. **Configure project**
   - Ask user for project name and description
   - Ask for primary role (PM, Developer, Tech Lead, QA, Data Scientist)
   - Set initial phase (typically Phase 0: Discovery)
   - Create `.aid/state.json` by running ONE Bash call (it works only when no
     `state.json` exists yet):

     ```bash
     python "${CLAUDE_PLUGIN_ROOT}/hooks/aid_session.py" init <role> <phase>
     ```

     Claude Code will ask the user to confirm this call; if the user declines, nothing
     changes. `<role>`: pm | lead | developer | qa | data-scientist | other; `<phase>`: 0-5. Run it
     exactly in this shape: one simple command, lowercase `python`, single spaces, no `;`,
     `&&`, pipes, redirects, `$( )` or loops. If `${CLAUDE_PLUGIN_ROOT}` was not
     replaced by a real path, this is not a plugin install: AID's phase commands need the
     plugin (`claude plugin install aid@AID`). Do not substitute another path. The user can
     also run the command themselves by typing it with a leading `!`. Show the
     script's output; if it refuses (non-zero exit), show its reason verbatim. Never write
     `.aid/state.json` yourself: `aid_session.py` is its only writer.

4. **Offer breather** (optional: session boundaries). Ask the user first and install only on
   an explicit yes; the default is No. Tell them this before they answer:
   breather is optional and installs into `~/.claude`, so once installed it is active in **every** project on the machine. In the first session of each day, and again on each prompt until you answer or skip its day-plan question, its instructions tell Claude to fetch **today's calendar events** automatically, before answering and without asking you, through any connector available in the session. It names Google Calendar / Gmail and Microsoft 365 / Outlook as examples: it asks only for today's events, but a Gmail or Outlook connector may also have access to your mail. The events go into the conversation (and so to the model and through that connector), and the meeting start times are saved under `~/.claude/state/breather/`. It also adds hooks and a status line to `~/.claude/settings.json`; see [integrations/breather/README.md](../integrations/breather/README.md) for everything it does. To keep this off, do not install breather, or remove it with `/breather-stop` (uninstall).

   If the user says yes:
   - Run `node integrations/breather/install.mjs` only from the root of the user's own AID
     checkout (the one `/setup` is installing), never from another project's folder
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
