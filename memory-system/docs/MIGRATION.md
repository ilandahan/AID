# AID Memory System - Migration Guide

> How to add the Memory System to an existing AID methodology installation.
>
> **Note (T8):** "Claude Memory" in AID means a LOCAL file, `$AID_HOME/memory/slots.json`
> (default `~/.aid/memory/`). Nothing is sent to Claude's built-in memory, and AID does not
> call `memory_user_edits`. The `memory_user_edits` examples below describe an earlier design
> and are not used. Entries are written only by `aid_session.py memory-sync`, which Claude
> Code asks the user to confirm. See `MEMORY.md`.

---

## Overview

This guide covers:
1. Adding Memory System to existing AID repo
2. Migrating existing learnings to the new format
3. Updating workflows to include feedback collection
4. Integrating with existing AID's local memory entries

---

## Prerequisites

Before migrating:
- [ ] Existing AID methodology installation
- [ ] Access to Claude Code
- [ ] Backup of any existing customizations

---

## Step 1: Add Memory System Files

### Option A: Copy Directory

```bash
# From the aid-memory-system package
cp -r memory-system/* /path/to/aid-repo/memory-system/
```

### Option B: Git Subtree (for repo integration)

```bash
cd /path/to/aid-repo
git subtree add --prefix=memory-system https://github.com/[aid-memory-repo] main --squash
```

---

## Step 2: Initialize User Directory

Run the initialization command:

```
/aid-init
```

This creates `~/.aid/` if it doesn't exist, or updates missing files if it does.

### What Gets Created

```
~/.aid/
├── config.yaml           # User preferences
├── state.json            # Session tracking
├── skills/               # Skill files
├── feedback/             # Feedback storage
└── metrics/              # Analytics
```

### Preserving Existing Customizations

If you have existing customized skill files:

```bash
# Backup your customized references (they live in the plugin, not in ~/.aid)
cp -r "${CLAUDE_PLUGIN_ROOT}/skills/memory-system/references" ./memory-references.backup

# Run init
/aid-init

# Merge your customizations back
# Especially check cumulative.md files
```

---

## Step 3: Migrate Existing AID's local memory

### Check Current Entries

```
memory_user_edits(command="view")
```

Look for any existing AID-related entries.

### Add Starter Entries

If you don't have AID:* entries yet:

```
/aid-init
```

AID's local memory starts empty; entries are added only by `/aid-improve` (`memory-sync`, which you confirm).

### Preserve Custom Entries

If you have custom entries you want to keep:

1. Note their line numbers
2. Run `/aid-init`
3. Verify they weren't overwritten
4. Update `~/.aid/metrics/memory-tracking.json` to include them

---

## Step 4: Update Your Workflow

### AID Project Workflow Integration

Add Memory System to your standard workflow:

```markdown
## Updated AID Workflow

### Phase Start
1. `/aid-start [role] [phase]`
2. Load relevant skills automatically
3. Begin work

### During Phase
- Skills are applied automatically
- Revisions tracked internally

### Phase End (NEW!)
1. Complete deliverable
2. User approves: "approved" or "done"
3. Rate session (1-5) ← NEW
4. Provide feedback ← NEW
5. Move to next phase

### Improvement Cycle (NEW!)
- Every ~10 sessions: `/aid-improve`
- Review and approve pattern suggestions
- Each approved suggestion is appended to its learnings file only after you confirm it
```

### Updating Team Documentation

Add to your team's AID documentation:

```markdown
## Feedback Collection

After each phase:
1. Rate your experience (1-5)
2. Note what worked well
3. Note what needed revision
4. This helps improve future sessions!

## Running Improvements

When prompted (every ~10 sessions):
1. Run `/aid-improve`
2. Review each suggestion
3. Approve patterns that will help future work
4. Changes apply to next session
```

---

## Step 5: Integrate with Existing Skills

### If You Have Custom Skills

Your existing AID skills likely live in a different structure. Options:

**Option A: Adopt Memory System Structure**
Move your content into the new structure:
- Role-specific → `skills/memory-system/references/roles/{role}/QUICK-REFERENCE.md`
- Phase-specific → `skills/memory-system/references/phases/{phase}/QUICK-REFERENCE.md`
- Learnings → `skills/memory-system/references/*/*/cumulative.md`

**Option B: Keep Both**
The Memory System can work alongside existing skills:
- Memory System references in the plugin's `skills/memory-system/references/`
- Original AID skills in your project

**Option C: Hybrid Approach**
Copy Memory System structure, then merge your content into the SKILL.md files.

### Merging Skill Content

When merging, preserve:
- Your custom guidance and tips
- Project-type-specific content
- Team conventions

Add from Memory System:
- Structured sections (Responsibilities, Deliverables, etc.)
- Anti-patterns section
- Cumulative learning format

---

## Step 6: Set Up AID's local memory Slots

### Review Slot Allocation

Default allocation (30 slots):
- Universal: 5
- Product Manager: 5
- Developer: 5
- QA Engineer: 5
- Tech Lead: 3
- Phase-specific: 5
- Learned: 10

### Customize for Your Team

If your team uses different roles, edit `~/.aid/metrics/memory-tracking.json`:

```json
{
  "slot_allocation": {
    "universal": { "max_slots": 5 },
    "product_manager": { "max_slots": 5 },
    "developer": { "max_slots": 5 },
    // Add custom roles:
    "data_scientist": { "max_slots": 3 },
    "designer": { "max_slots": 3 }
  }
}
```

---

## Step 7: Team Rollout

### Individual Setup

Each team member runs:
```
/aid-init
```

### Shared Skill Repository

For teams sharing skill improvements:

1. **Central Repo**: Keep SKILL.md files in git
2. **Local Cumulative**: Each user's cumulative.md is personal
3. **Updates**: an AID update brings new SKILL.md files (there is no skill sync command)

### Migration Checklist for Teams

- [ ] Each member runs `/aid-init`
- [ ] Note: AID's local memory starts empty; entries are added only by `/aid-improve` (`memory-sync`, which you confirm).
- [ ] Test feedback collection with a sample session
- [ ] Run first `/aid-improve` cycle
- [ ] Update team documentation

---

## Compatibility Notes

### Claude Code Version

Memory System requires:
- Claude Code with file system access
- AID's local memory (`$AID_HOME/memory/slots.json`)
- JSON file read/write capability

### Directory Locations

Default: `~/.aid/`

To change, set environment variable:
```bash
export AID_HOME=/custom/path/.aid
```

### Existing .claude Files

If you have existing `.claude/` or similar directories:
- Memory System uses separate `~/.aid/` directory
- No conflicts with existing Claude configurations
- Can coexist safely

---

## Rollback Procedure

If migration causes issues:

### Full Rollback

```bash
# Remove Memory System
rm -rf ~/.aid/

# Remove AID's local memory entries (optional)
# Use memory_user_edits to remove AID:* entries

# Restore backup
cp -r ~/.aid.backup ~/.aid/
```

### Partial Rollback

Keep Memory System but restore specific files:
```bash
# Restore just the references
cp -r ./memory-references.backup/* "${CLAUDE_PLUGIN_ROOT}/skills/memory-system/references/"

# Restore just state
cp ~/.aid/state.json.backup ~/.aid/state.json
```

---

## Migration Verification

### Test Session Flow

1. Start a test session:
   ```
   /aid-start pm discovery
   ```

2. Verify skills loaded:
   - Should see role-specific guidance
   - Should see phase-specific deliverables

3. End session with feedback:
   ```
   /aid-end
   ```

4. Verify feedback created:
   ```bash
   ls ~/.aid/feedback/pending/
   # Should see a new *.json file
   ```

### Test Improvement Flow

1. Create 3+ test feedback files (or work through 3 sessions)

2. Run improvement:
   ```
   /aid-improve
   ```

3. Verify analysis runs and suggestions appear

### Test Memory Integration

1. Check AID's local memory:
   ```
   /aid-memory list
   ```

2. Verify 20 AID:* entries exist

3. Test memory stats:
   ```
   /aid-memory stats
   ```

---

## Recommendation IDs: legacy SHA-1 sunset (T16-33)

Before T15, a queued recommendation's id was SHA-1 of its content cut to 16 hex
characters. Since T15 it is SHA-256 cut to 32 hex characters.

- Entries queued BEFORE T15 keep their stored 16-hex id. `memory-apply <id>` and
  `memory-reject <id>` still accept that id, but only for the entry that stores it and only
  while its content still hashes to it.
- Every NEW entry gets its SHA-256 id when it is queued, whatever id it came with. A 16-hex
  id is never accepted for a new entry.
- Sunset: the legacy id is read-only support for old queues. Apply or reject the old entries
  (or run `/aid-reset`); once no pre-T15 entry is left in
  `$AID_HOME/recommendations/`, legacy ids are no longer used, and a later release may drop
  the SHA-1 check.
