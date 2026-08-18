# AID Memory System - Error Handling Reference

> Implementation patterns for graceful error handling throughout the system.

---

## Error Handling Philosophy

1. **Never crash** - Always provide user feedback and graceful degradation
2. **Preserve data** - Never lose user feedback or learnings
3. **Be transparent** - Tell user what went wrong and how to fix
4. **Auto-recover** - When possible, fix issues automatically
5. **Log everything** - Keep audit trail for debugging

---

## Error Categories

### Category 1: Initialization Errors

#### E1.1: Directory Creation Failed

```
WHEN: mkdir ~/.aid fails
IMPACT: System cannot start
SEVERITY: Critical

HANDLING:
1. Check permissions
2. Suggest manual creation
3. Provide exact commands

MESSAGE:
"❌ Cannot create system directory.
Check permissions or create manually:
mkdir -p ~/.aid/{skills,feedback,metrics}"
```

#### E1.2: Missing Starter Files

```
WHEN: Default files not found during init
IMPACT: Partial initialization
SEVERITY: Medium

HANDLING:
1. Create minimal defaults in-memory
2. Write defaults to disk
3. Continue with initialization

MESSAGE:
"⚠️ Default files missing. Creating minimal files..."
```

#### E1.3: Claude Memory API Unavailable

```
WHEN: memory_user_edits fails
IMPACT: Cannot add starter entries
SEVERITY: Medium (non-blocking)

HANDLING:
1. Log the error
2. Mark memory as "pending sync"
3. Continue without memory initialization
4. Retry on next session start

MESSAGE:
"⚠️ Cannot access Claude Memory right now.
System will continue and retry next session."
```

---

### Category 2: File I/O Errors

#### E2.1: JSON Parse Error

```
WHEN: JSON.parse fails on any config/state file
IMPACT: File data unavailable
SEVERITY: High

HANDLING:
1. Backup corrupted file to .corrupted/
2. Create fresh default
3. Warn user about data loss
4. Continue with defaults

CODE:
try:
    data = json.loads(file_content)
except JSONDecodeError as e:
    backup_corrupted_file(filepath)
    data = get_default_for_file(filepath)
    warn_user_corruption(filepath)

MESSAGE:
"⚠️ File {filename} is corrupted.
Backup saved to .corrupted/
Created new file with defaults."
```

#### E2.2: File Write Failed

```
WHEN: write operation fails (permissions, disk full)
IMPACT: Data not persisted
SEVERITY: High

HANDLING:
1. Retry once
2. Try alternative location (/tmp)
3. Keep data in memory
4. Alert user prominently

MESSAGE:
"❌ Cannot save {filename}.
Data kept temporarily in memory.
Check permissions and try: /aid sync"
```

#### E2.3: File Not Found

```
WHEN: expected file doesn't exist
IMPACT: Missing configuration/data
SEVERITY: Medium

HANDLING:
1. Check if init needed
2. Create default if appropriate
3. Continue with sensible defaults
```

---

### Category 3: State Management Errors

#### E3.1: Invalid State Transition

```
WHEN: attempting impossible state change (e.g., end without start)
IMPACT: State confusion
SEVERITY: Low

HANDLING:
1. Log warning
2. Correct state automatically
3. Continue

MESSAGE:
"ℹ️ No active session to end.
Start a new session with /aid start"
```

#### E3.2: Concurrent State Modification

```
WHEN: state.json modified by another process
IMPACT: State overwrite
SEVERITY: Medium

HANDLING:
1. Use last_updated timestamp for conflict detection
2. Merge non-conflicting changes
3. Warn on actual conflicts
```

---

### Category 4: Feedback Collection Errors

#### E4.1: Missing Required Rating

```
WHEN: user tries to skip rating
IMPACT: Incomplete feedback
SEVERITY: Medium

HANDLING:
1. Insist on rating (required)
2. Explain why it matters
3. Offer to skip entire feedback if user insists

MESSAGE:
"Rating is required - it's the primary signal for pattern detection.
Rate 1-5 or type 'skip' to cancel feedback entirely."
```

#### E4.2: Feedback Save Failed

```
WHEN: cannot write feedback file
IMPACT: Feedback lost
SEVERITY: High

HANDLING:
1. Retry with different filename
2. Save to alternative location
3. Keep in session for manual save
4. Never silently lose feedback

MESSAGE:
"❌ Cannot save feedback file.
Data displayed below for manual backup.
[feedback content]"
```

#### E4.3: Anonymization Failure

```
WHEN: feedback contains identifiable info that should be removed
IMPACT: Privacy concern
SEVERITY: High

HANDLING:
1. Apply strict filtering
2. When in doubt, remove more
3. Log what was removed (without the actual content)
```

---

### Category 5: Improvement Flow Errors

#### E5.1: Not Enough Feedback

```
WHEN: <3 feedback items for analysis
IMPACT: Cannot detect patterns
SEVERITY: Low (expected case)

HANDLING:
1. Explain minimum requirements
2. Show current count
3. Offer to continue anyway (with warning)

MESSAGE:
"📊 Only {count} feedback items (minimum: 3)

For reliable pattern detection, more samples are needed.
Continue anyway? Results may be inaccurate.

[Continue anyway] [Wait for more]"
```

#### E5.2: Sub-Agent Analysis Failed

```
WHEN: pattern detection throws error
IMPACT: No suggestions generated
SEVERITY: Medium

HANDLING:
1. Log detailed error for debugging
2. Preserve feedback for retry
3. Suggest retry or skip

MESSAGE:
"⚠️ Error analyzing feedback.

Feedback saved and will retry later.
[Retry now] [Skip for now]"
```

#### E5.3: Skill Update Failed

```
WHEN: cannot write to cumulative.md
IMPACT: Suggestion not applied
SEVERITY: Medium

HANDLING:
1. Log failure
2. Show manual update instructions
3. Continue with other suggestions
4. Mark suggestion as "pending manual"

MESSAGE:
"⚠️ Cannot update {skill_file}

Manual update:
Open {skill_file}
Add:
{content}

[Continue to next]"
```

---

### Category 6: Claude Memory Errors

#### E6.1: Memory Add Failed

```
WHEN: memory_user_edits(add) fails
IMPACT: Entry not added to memory
SEVERITY: Medium

HANDLING:
1. Retry once
2. Log to pending promotions
3. Suggest manual add
4. Continue improvement flow

MESSAGE:
"⚠️ Cannot add to Claude Memory now.

Entry saved for retry:
{entry}

For manual add:
memory_user_edits(command='add', control='{entry}')"
```

#### E6.2: Memory Full

```
WHEN: trying to add but all slots used
IMPACT: Cannot promote new patterns
SEVERITY: Low

HANDLING:
1. Calculate lowest scoring entry
2. If new scores higher, offer replacement
3. If not, explain and keep in cumulative.md

MESSAGE:
"📊 Claude Memory full (30/30 slots)

New entry (score: {new_score}):
{new_entry}

Lowest existing (score: {low_score}):
{low_entry}

{IF new > low}
Replace? [Yes] [No]
{ELSE}
New entry doesn't score high enough.
Kept in cumulative.md for future consideration.
{ENDIF}"
```

#### E6.3: Memory Out of Sync

```
WHEN: tracking file doesn't match actual memory
IMPACT: Wrong slot allocation
SEVERITY: Medium

HANDLING:
1. Fetch actual memory state
2. Rebuild tracking from actual
3. Report discrepancies

MESSAGE:
"🔄 Syncing tracking with Claude Memory

Found {missing} missing entries
Found {extra} untracked entries

Tracking updated."
```

---

## Auto-Recovery Matrix

| Error | Auto-Recovery | Manual Required |
|-------|---------------|-----------------|
| E1.1 Directory | ❌ | mkdir command |
| E1.2 Missing files | ✅ | - |
| E1.3 Memory API | ✅ (retry later) | - |
| E2.1 JSON corrupt | ✅ (default) | Review backup |
| E2.2 Write failed | ✅ (alt location) | Fix permissions |
| E2.3 File not found | ✅ (create) | - |
| E3.1 Invalid state | ✅ (correct) | - |
| E3.2 Concurrent | ✅ (merge) | Conflict review |
| E4.1 Missing rating | ❌ | User input |
| E4.2 Save failed | ✅ (backup) | Copy from backup |
| E4.3 Anonymization | ✅ (strict filter) | - |
| E5.1 Not enough | ❌ | Wait for more |
| E5.2 Analysis failed | ✅ (retry) | - |
| E5.3 Skill update | ❌ | Manual edit |
| E6.1 Memory add | ✅ (retry) | Manual add |
| E6.2 Memory full | ❌ | User decision |
| E6.3 Out of sync | ✅ (rebuild) | - |

---

## Error Logging

### Log Format

```json
{
  "timestamp": "2025-01-15T10:30:00Z",
  "level": "ERROR",
  "category": "E2.1",
  "message": "JSON parse failed",
  "context": {
    "file": "state.json",
    "operation": "load"
  },
  "resolution": "Created default state",
  "user_notified": true
}
```

### Log Location

```
~/.aid/logs/
├── current.log      # Current session
├── error.log        # Errors only
└── archive/         # Rotated logs
```
