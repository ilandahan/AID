# AID Memory System - Commands Reference

> Complete reference for all AID Memory System commands.

---

## Quick Reference

| Command | Description |
|---------|-------------|
| `/aid init` | Initialize system (first time) |
| `/aid start [role] [phase]` | Start a work session |
| `/aid status` | Show current state |
| `/aid end` | Complete phase, collect feedback |
| `/aid improve` | Run improvement analysis |
| `/aid memory list` | Show Claude Memory entries |
| `/aid memory stats` | Show memory statistics |
| `/aid skill view [type]` | View skill content |
| `/aid skill edit [type]` | Edit skill file |
| `/aid skill sync` | Sync skills from repo |
| `/aid export` | Export backup |
| `/aid reset --confirm` | Reset all data |

---

## Initialization

### `/aid init`

Initializes the AID Memory System for first-time use.

**What it does:**
1. Creates `~/.aid/` directory structure
2. Copies default configuration files
3. Initializes skill files for all roles and phases
4. Creates empty feedback directories
5. Sets up metrics tracking files
6. Adds 20 starter entries to Claude Memory

**Output:**
```
🚀 AID Memory System initialized!

Created:
• ~/.aid/config.yaml - Settings
• ~/.aid/state.json - System state
• ~/.aid/skills/ - Skill files (4 roles × 5 phases)
• ~/.aid/feedback/ - Feedback directories
• ~/.aid/metrics/ - Metrics files

Let's begin! Run /aid start [role] [phase]
```

**If already initialized:**
```
✅ AID Memory System already initialized.

Run /aid status to see current state.
Run /aid start to begin a session.
```

---

## Session Commands

### `/aid start [role] [phase]`

Starts a new work session.

**Arguments:**
- `role` (optional): pm, dev, qa, lead
- `phase` (optional): discovery, prd, tech-spec, development, qa-ship

**Examples:**
```
/aid start                    # Interactive - asks for role & phase
/aid start pm                 # Starts as PM, asks for phase
/aid start pm discovery       # Starts as PM in Discovery phase
/aid start dev development    # Starts as Developer in Development phase
```

**Behavior:**
1. Checks if improvement is suggested
2. Loads relevant skill files
3. Initializes session state
4. Begins tracking revisions

---

### `/aid status`

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

💡 Recommended: Run /aid improve
```

---

### `/aid end`

Completes the current phase and collects feedback.

**Flow:**
1. Display phase summary (deliverables, revision count)
2. Request quality rating (1-5) - **required**
3. Request qualitative feedback (optional)
4. Save anonymized feedback file
5. Update statistics
6. Suggest next steps

**Rating is mandatory** - system will prompt until received.

---

## Improvement Commands

### `/aid improve`

Runs the improvement analysis sub-agent.

**Requirements:**
- At least 3 pending feedback items recommended
- No active session (run `/aid end` first)

**Flow:**
1. Gather all pending feedback
2. Run pattern analysis (sub-agent)
3. Present suggestions one by one
4. User approves/rejects each suggestion
5. Apply approved changes
6. Archive processed feedback

**User actions for each suggestion:**
- **Approve** ✓ - Apply the change
- **Edit** 📝 - Modify before applying
- **Reject** ✗ - Don't apply
- **Skip** ⏭️ - Decide later

---

## Memory Commands

### `/aid memory list`

Shows all AID:* entries in Claude Memory.

**Output:**
```
📝 AID Claude Memory Entries (12/30 used)

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

### `/aid memory stats`

Shows memory slot allocation and usage statistics.

**Output:**
```
📊 Claude Memory Statistics

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

## Skill Commands

### `/aid skill view [type]`

Views skill file content.

**Arguments:**
- `type`: Role name or phase name

**Examples:**
```
/aid skill view pm              # View PM role skill
/aid skill view developer       # View Developer role skill
/aid skill view discovery       # View Discovery phase skill
/aid skill view tech-spec       # View Tech Spec phase skill
```

---

### `/aid skill edit [type]`

Opens skill file for editing.

**Arguments:**
- `type`: Role name or phase name

**Editable files:**
- `~/.aid/skills/roles/{role}/SKILL.md`
- `~/.aid/skills/roles/{role}/cumulative.md`
- `~/.aid/skills/phases/{phase}/SKILL.md`
- `~/.aid/skills/phases/{phase}/cumulative.md`

---

### `/aid skill sync`

Synchronizes skill files from the AID repository.

**What it does:**
1. Pulls latest SKILL.md files from repo
2. Preserves local cumulative.md (learned patterns)
3. Reports any conflicts

---

## Admin Commands

### `/aid export`

Creates a backup of all AID data.

**Output location:** `~/.aid/export/aid-backup-{date}.zip`

**Contents:**
- All feedback files (pending and processed)
- All skill files
- Configuration files
- Metrics and tracking files

---

### `/aid reset --confirm`

Resets the AID Memory System.

**Warning:** This deletes all feedback and statistics!

**What is deleted:**
- All feedback files (pending and processed)
- Statistics in state.json
- Trends data

**What is preserved:**
- Skill files (including cumulative.md learnings)
- Claude Memory entries
- Configuration preferences

**Confirmation required:**
```
⚠️ This will delete all feedback and reset statistics.
Skill files and Claude Memory will be preserved.

Type 'RESET' to confirm: ___
```

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

## Command Aliases

| Full Command | Aliases |
|--------------|---------|
| `/aid start` | `/aid s`, `/aid begin` |
| `/aid status` | `/aid st`, `/aid info` |
| `/aid end` | `/aid done`, `/aid finish` |
| `/aid improve` | `/aid i`, `/aid learn` |
| `/aid memory list` | `/aid mem`, `/aid m list` |
| `/aid memory stats` | `/aid m stats` |
