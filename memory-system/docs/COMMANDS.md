# AID Memory System - Commands Reference

> Complete reference for all AID Memory System commands.

---

## Quick Reference

| Command | Description |
|---------|-------------|
| `/aid-init` | Initialize system (first time) |
| `/aid-start [role] [phase]` | Start a work session |
| `/aid-status` | Show current state |
| `/aid-end` | Complete phase, collect feedback |
| `/aid-improve` | Run improvement analysis |
| `/aid-memory list` | Show AID's local memory entries |
| `/aid-memory stats` | Show memory statistics |
| `/aid-recommendations` | View and apply queued skill-update proposals |
| `/aid-reset` | Reset AID runtime data ([details](#reset)) |

---

## Initialization

### `/aid-init`

Initializes the AID Memory System for first-time use.

**What it does:**
1. Creates `~/.aid/` directory structure
2. Copies default configuration files
3. Initializes skill files for all roles and phases
4. Creates empty feedback directories
5. Sets up metrics tracking files
6. AID's local memory starts empty; entries are added only by `/aid-improve` (`memory-sync`, which you confirm).

**Output:**
```
🚀 AID Memory System initialized!

Created:
• ~/.aid/config.yaml - Settings
• ~/.aid/state.json - System state
• Skill references: skills/memory-system/references/ (in the plugin, not copied)
• ~/.aid/feedback/ - Feedback directories
• ~/.aid/metrics/ - Metrics files

Let's begin! Run /aid-start [role] [phase]
```

**If already initialized:**
```
✅ AID Memory System already initialized.

Run /aid-status to see current state.
Run /aid-start to begin a session.
```

---

## Session Commands

### `/aid-start [role] [phase]`

Starts a new work session.

**Arguments:**
- `role` (optional): pm, dev, qa, lead
- `phase` (optional): discovery, prd, tech-spec, development, qa-ship

**Examples:**
```
/aid-start                    # Interactive - asks for role & phase
/aid-start pm                 # Starts as PM, asks for phase
/aid-start pm discovery       # Starts as PM in Discovery phase
/aid-start dev development    # Starts as Developer in Development phase
```

**Behavior:**
1. Checks if improvement is suggested
2. Loads relevant skill files
3. Initializes session state
4. Begins tracking revisions

---

### `/aid-status`

Shows current session state and statistics.

**Output:**
```
📊 AID Memory System Status

Current Session:
• Active: Yes
• Role: Product Manager
• Phase: Discovery
• Revisions so far: 2

Statistics:
• Total sessions: 47
• Pending feedback: 8
• Sessions since last improvement: 8

💡 Recommended: Run /aid-improve
```

---

### `/aid-end`

Completes the current phase and collects feedback.

**Flow:**
1. Display phase summary (deliverables, revision count)
2. Request quality rating (1-5) - **required**
3. Request qualitative feedback (optional)
4. Save feedback with `aid_session.py end`, which redacts the text (best effort) before
   writing it to `$AID_HOME/feedback/pending/`
5. Update statistics
6. Suggest next steps

**Rating is mandatory** - system will prompt until received.

---

## Improvement Commands

### `/aid-improve`

Runs the improvement analysis sub-agent.

**Requirements:**
- At least 3 pending feedback items recommended
- No active session (run `/aid-end` first)

**Flow:** (see `commands/aid-improve.md` for the exact calls)
1. Preview: `aid_session.py memory-preview` (writes nothing)
2. Get the redacted feedback: `aid_session.py memory-feedback` (JSON, writes nothing)
3. Run pattern analysis (`memory-analysis-agent`, proposals only, writes no files)
4. Save its JSON to `.aid/improve/proposals.json`, then queue it: `aid_session.py memory-queue`
   (no argument; it reads that file itself)
5. Show the queue; the user picks proposals
6. Apply one: `aid_session.py memory-apply <id>` (Claude Code asks the user to confirm;
   it only appends to a role or phase `cumulative.md`), or drop one:
   `aid_session.py memory-reject <id>`
7. Optionally write memory entries: `aid_session.py memory-sync` (Claude Code asks the
   user to confirm)

**User actions for each suggestion:**
- **Apply** ✓ - `memory-apply <id>`, confirmed in the Claude Code prompt
- **Reject** ✗ - `memory-reject <id>`
- **Skip** ⏭️ - Leave it in the queue and decide later

---

## Memory Commands

### `/aid-memory list`

Shows all AID:* entries in AID's local memory (`$AID_HOME/memory/slots.json`).

**Output:**
```
📝 AID Local Memory Entries (12/30 used)

Universal:
  1. AID:ALL:ALL:DO Confirm understanding before producing deliverable
  2. AID:ALL:ALL:CHECK Verify scope hasn't crept since last checkpoint

Product Manager:
  3. AID:PM:DISC:ASK "Who else touches this data?" for stakeholders
  4. AID:PM:DISC:DO Use SCQ format for problem statements

Developer:
  5. AID:DEV:DEV:DO Write test first, then implement (TDD)
  ...
```

---

### `/aid-memory stats`

Shows memory slot allocation and usage statistics.

**Output:**
```
📊 AID Local Memory Statistics

Slot Allocation:
• Universal: 5/5 (100%)
• Product Manager: 4/5 (80%)
• Developer: 5/5 (100%)
• QA Engineer: 4/5 (80%)
• Tech Lead: 2/3 (67%)
• Phase-specific: 3/5 (60%)
• Learned: 2/10 (20%)

Top Performers (by usage × rating):
1. AID:DEV:DEV:DO Write test first... (score: 4.8)
2. AID:PM:DISC:ASK Who else touches... (score: 4.5)

Promotion Candidates:
• "Check API contracts before..." (5 uses, 4.2 avg)
```

---

## Skill Files

There is no skill command. The role and phase skill files are plain files in the plugin;
read or edit them directly:

- `skills/memory-system/references/roles/{role}/QUICK-REFERENCE.md`
- `skills/memory-system/references/roles/{role}/cumulative.md`
- `skills/memory-system/references/phases/{phase}/QUICK-REFERENCE.md`
- `skills/memory-system/references/phases/{phase}/cumulative.md`

Learnings reach `cumulative.md` through `/aid-improve` or `/aid-recommendations`
(`aid_session.py memory-apply <id>`, which Claude Code asks you to confirm). New skill
versions come with an AID update; your `cumulative.md` learnings are in those same files,
so back them up first (see `MIGRATION.md`).

---

## Admin Commands

### Backing up AID data

There is no export command. Copy the AID data folder, `$AID_HOME` (default `~/.aid`), e.g.
`cp -R "${AID_HOME:-$HOME/.aid}" "${AID_HOME:-$HOME/.aid}.backup"`.
See `commands/aid-reset.md` for the Windows equivalent.

The copy holds all feedback (pending and processed), state, metrics and
AID's local memory.

---

<a id="reset"></a>
### Reset

`/aid-reset` (see `commands/aid-reset.md`) runs exactly one command, which Claude Code
asks the user to confirm:

```
python "${CLAUDE_PLUGIN_ROOT}/hooks/aid_session.py" reset          # keeps memory/
python "${CLAUDE_PLUGIN_ROOT}/hooks/aid_session.py" reset --all    # also deletes memory/
```

Use `--all` only when the user explicitly asked to delete AID's local memory too.
Do not delete anything by hand (no `rm`, no changing into `$AID_HOME`): the command is the
only supported way to reset.

**Warning:** This deletes all feedback and statistics. It cannot be undone except from a
backup (see "Backing up AID data" above).

**What is deleted** (the fixed list of runtime entries under `$AID_HOME`, default `~/.aid`):
- `state.json` and `agent_state.json` (session state)
- `feedback/` (pending and processed feedback)
- `recommendations/` (queued, applied and rejected recommendations)
- `metrics/` (statistics and trends)
- `reports/` (dashboard output)
- `memory/` (AID's local memory) - only with `--all`

**What is kept:**
- `memory/` - unless `--all` is given
- `integrity/` - the session integrity baseline, never deleted, not even with `--all`
- The project's `.aid/` folder (state, context, QA criteria) - never touched
- Skill files in the plugin (including cumulative.md learnings)
- Anything else in `$AID_HOME` it does not recognise (printed as "kept")

The command prints each entry it removes and each entry it keeps. It refuses, deleting
nothing, when `$AID_HOME` is (or contains) a user home folder, a filesystem root, the
current project root or the current folder, or is not a plain folder. In `-p` or dontAsk
sessions the confirmation cannot be given, so it is denied. Run `/aid-init` afterwards to
reinitialize.

---

## Natural Language Triggers

The system also responds to natural language phrases:

### Session Start
- "Good morning" / "Let's start"
- Triggers role/phase selection flow

### Phase Completion
- "Done" / "Approved" / "Complete"
- "Let's move on" / "Looks good"
- Triggers feedback collection flow

### During Work
- Revision indicators: "fix", "change", "wrong", "missing"
- Positive indicators: "great", "perfect", "exactly"
- System tracks these internally for feedback

---

## Command Names

Every command is a separate slash command named `/aid-<name>` (one file in `commands/`).
There are no aliases, and the name is always joined with a hyphen.
