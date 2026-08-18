# AID Memory System - Migration Guide

> How to add the Memory System to an existing AID methodology installation.

---

## Overview

This guide covers:
1. Adding Memory System to existing AID repo
2. Migrating existing learnings to the new format
3. Updating workflows to include feedback collection
4. Integrating with existing Claude Memory entries

---

## Prerequisites

Before migrating:
- [ ] Existing AID methodology installation
- [ ] Access to Claude Code with Claude Memory enabled
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
/aid init
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
# Backup existing skills
cp -r ~/.aid/skills ~/.aid/skills.backup

# Run init
/aid init

# Merge your customizations back
# Especially check cumulative.md files
```

---

## Step 3: Migrate Existing Claude Memory

### Check Current Entries

```
memory_user_edits(command="view")
```

Look for any existing AID-related entries.

### Add Starter Entries

If you don't have AID:* entries yet:

```
/aid init
```

This adds 20 starter entries if they don't exist.

### Preserve Custom Entries

If you have custom entries you want to keep:

1. Note their line numbers
2. Run `/aid init`
3. Verify they weren't overwritten
4. Update `~/.aid/metrics/memory-tracking.json` to include them

---

## Step 4: Update Your Workflow

### AID Project Workflow Integration

Add Memory System to your standard workflow:

```markdown
## Updated AID Workflow

### Phase Start
1. `/aid start [role] [phase]`
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
- Every ~10 sessions: `/aid improve`
- Review and approve pattern suggestions
- Skills automatically updated
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
1. Run `/aid improve`
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
- Role-specific → `skills/roles/{role}/SKILL.md`
- Phase-specific → `skills/phases/{phase}/SKILL.md`
- Learnings → `skills/*/cumulative.md`

**Option B: Keep Both**
The Memory System can work alongside existing skills:
- Memory System skills in `~/.aid/skills/`
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

## Step 6: Set Up Claude Memory Slots

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
/aid init
```

### Shared Skill Repository

For teams sharing skill improvements:

1. **Central Repo**: Keep SKILL.md files in git
2. **Local Cumulative**: Each user's cumulative.md is personal
3. **Sync Command**: `/aid skill sync` pulls SKILL.md updates

### Migration Checklist for Teams

- [ ] Each member runs `/aid init`
- [ ] Verify Claude Memory has 20 AID:* entries
- [ ] Test feedback collection with a sample session
- [ ] Run first `/aid improve` cycle
- [ ] Update team documentation

---

## Compatibility Notes

### Claude Code Version

Memory System requires:
- Claude Code with file system access
- Claude Memory (memory_user_edits tool)
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

# Remove Claude Memory entries (optional)
# Use memory_user_edits to remove AID:* entries

# Restore backup
cp -r ~/.aid.backup ~/.aid/
```

### Partial Rollback

Keep Memory System but restore specific files:
```bash
# Restore just skills
cp -r ~/.aid/skills.backup/* ~/.aid/skills/

# Restore just state
cp ~/.aid/state.json.backup ~/.aid/state.json
```

---

## Migration Verification

### Test Session Flow

1. Start a test session:
   ```
   /aid start pm discovery
   ```

2. Verify skills loaded:
   - Should see role-specific guidance
   - Should see phase-specific deliverables

3. End session with feedback:
   ```
   /aid end
   ```

4. Verify feedback created:
   ```bash
   ls ~/.aid/feedback/pending/
   # Should see FB-*.json file
   ```

### Test Improvement Flow

1. Create 3+ test feedback files (or work through 3 sessions)

2. Run improvement:
   ```
   /aid improve
   ```

3. Verify analysis runs and suggestions appear

### Test Memory Integration

1. Check Claude Memory:
   ```
   /aid memory list
   ```

2. Verify 20 AID:* entries exist

3. Test memory stats:
   ```
   /aid memory stats
   ```
