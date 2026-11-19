# AID Memory System - Troubleshooting Guide

> Solutions for common issues and error recovery procedures.

---

## Quick Diagnostics

Run `/aid status` to check system health:

```
📊 AID Status

System: ✅ OK
Directory: ~/.aid/ exists
State: Valid
Skills: 18/18 loaded
Memory: 20/30 slots used

Current session: PM / Discovery
Pending feedback: 5
Sessions since improvement: 8

💡 Suggestion: Time to run /aid-improve
```

---

## Common Issues

### 1. System Not Initialized

**Symptoms:**
- "~/.aid/ not found" error
- Commands don't work
- Skills not loading

**Solution:**
```
/aid init
```

This creates:
- ~/.aid/ directory structure
- Default config.yaml and state.json
- All skill files
- No memory entries: AID's local memory starts empty; entries are added only by `/aid-improve` (`memory-sync`, which you confirm).

**If init fails:**
```bash
# Manual creation
mkdir -p ~/.aid/{feedback/pending,feedback/processed,metrics}

# Then run init again
/aid init
```

---

### 2. Corrupted state.json

**Symptoms:**
- Strange behavior at session start
- Statistics showing wrong values
- "JSON parse error" messages

**Solution:**

**Option A: Auto-recovery**
```
/aid init --repair
```

**Option B: Manual reset**
```json
// Replace ~/.aid/state.json with:
{
  "version": "1.0",
  "current_session": null,
  "statistics": {
    "total_sessions": 0,
    "sessions_since_last_improvement": 0,
    "pending_feedback_count": 0,
    "last_improvement_run": null
  },
  "notifications": {
    "improvement_suggested": false,
    "reason": null
  },
  "last_updated": null
}
```

**Option C: Full reset (loses history)**
```
/aid reset --confirm
```

---

### 3. Corrupted Feedback Files

**Symptoms:**
- `/aid-improve` fails
- "Invalid feedback file" errors
- Improvement analysis incomplete

**Solution:**

**Check pending feedback:**
```bash
ls ~/.aid/feedback/pending/
```

**Validate each file:**
```bash
# Check if valid JSON (one file at a time)
python -m json.tool ~/.aid/feedback/pending/<file>.json
# Feedback files are named *.json
```

**Remove corrupted files:**
```bash
# Move to backup
mkdir -p ~/.aid/backup/corrupted
mv ~/.aid/feedback/pending/<corrupt-file>.json ~/.aid/backup/corrupted/
```

---

### 4. AID Local Memory Out of Sync

**Symptoms:**
- `/aid memory list` shows different entries than expected
- Entries missing after promotion
- Duplicate entries

**Solution:**

**Step 1: View actual memory**
```bash
cat ~/.aid/memory/slots.json
```

**Step 2: Compare with tracking**
```bash
cat ~/.aid/metrics/memory-tracking.json
```

**Step 3: Rebuild tracking**
```
/aid memory sync
```

---

### 5. Skills Not Loading

**Symptoms:**
- Generic responses (not role/phase specific)
- "Skill file not found" messages
- Wrong guidance being applied

**Solution:**

**Check skill files exist:**
```bash
ls "${CLAUDE_PLUGIN_ROOT}"/skills/memory-system/references/roles/*/QUICK-REFERENCE.md
ls "${CLAUDE_PLUGIN_ROOT}"/skills/memory-system/references/phases/*/QUICK-REFERENCE.md
```

**Resync from repo:**
```
/aid skill sync
```

---

### 6. Improvement Flow Fails

**Symptoms:**
- `/aid-improve` hangs or errors
- "Not enough data" message with plenty of feedback
- Suggestions not being generated

**Solution:**

**Check minimum feedback:**
- Need at least 3 feedback files for pattern detection
- Check: `ls ~/.aid/feedback/pending/ | wc -l`

**Check feedback format:**
All feedback files must have:
- `context.role` and `context.phase`
- `metrics.rating` (1-5)
- `metrics.revisions` (number)

**Force reanalysis:**
```
/aid-improve --force
```

---

### 7. Phase Gate Not Triggering

**Symptoms:**
- Completion phrases ignored
- No feedback collection prompt
- Session doesn't end properly

**Solution:**

**Explicit end:**
```
/aid end
```

**Check trigger phrases:**
The system listens for:
- done, approved, complete this phase, phase gate
- finished, looks good, ship it

**Missed feedback:**
Do not create a feedback file by hand. Run `/aid-end` (it calls `aid_session.py end`, which
redacts the text and writes the file). `/phase-approve` also stores its rating.

---

### 8. Memory Full (All 30 Slots Used)

**Symptoms:**
- "Cannot add entry - memory full" message
- Promotion candidates rejected
- New patterns stuck in cumulative.md

**Solution:**

**Check current allocation:**
```
/aid memory stats
```

**Review lowest-scoring entries:**
The system shows entries by score. Consider:
- Are all 30 entries still relevant?
- Are there duplicates or outdated patterns?

**Cleanup:**
Preview with `aid_session.py memory-preview`. Writes go only through
`aid_session.py memory-sync`, which Claude Code asks you to confirm.

**After removal:**
```
/aid memory sync
```

---

## Error Messages Reference

| Error | Meaning | Solution |
|-------|---------|----------|
| `~/.aid/ not found` | System not initialized | Run `/aid init` |
| `Invalid state.json` | Corrupted state file | Reset or repair state.json |
| `Skill file missing: X` | Skill file deleted/moved | Run `/aid skill sync` |
| `Feedback parse error` | Corrupted feedback file | Remove corrupted file |
| `Memory sync failed` | Could not write `~/.aid/memory/slots.json`, or the prompt was declined | Check the reason shown; re-run `/aid-improve` |
| `Not enough feedback` | <3 feedback items | Wait for more sessions |
| `Promotion rejected` | Entry doesn't meet criteria | Review criteria, try later |
| `Slot allocation full` | Category has no room | Replace lower-scoring entry |
| `Pattern already exists` | Duplicate detection | Pattern already in system |

---

## Recovery Procedures

### Full System Reset

**Warning: This loses all history!**

```
/aid reset --confirm
```

This will:
1. Delete all feedback (pending and processed)
2. Reset state.json to defaults
3. Reset trends.json
4. Keep skill files (including cumulative.md learnings)
5. Keep AID's local memory entries

### Back Up Before Reset

There is no export command. Copy the AID data folder, `$AID_HOME` (default `~/.aid`), e.g.
`cp -R "${AID_HOME:-$HOME/.aid}" "${AID_HOME:-$HOME/.aid}.backup"`.
See `commands/aid-reset.md` for the Windows equivalent.

---

## Diagnostic Commands

### Check System Health
```
/aid status
```

### View Current State
```bash
cat ~/.aid/state.json
```

### View Trends
```bash
cat ~/.aid/metrics/trends.json
```

### Count Feedback Files
```bash
ls ~/.aid/feedback/pending/*.json
```

### Check Memory Entries
```
/aid memory list
```

---

## Getting Help

If issues persist:

1. **Collect diagnostic info:**
   ```
   /aid-status
   ```
   and back up `$AID_HOME` (default `~/.aid`) as described above.

2. **Reset and start fresh:**
   ```
   /aid reset --confirm
   /aid init
   ```

3. **Manual inspection:**
   All data is in plain JSON files under ~/.aid/
   You can always manually edit or fix files
