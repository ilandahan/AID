# /context

Show current work context - where you are in tasks and steps.

## What It Does

1. Read `.aid/context.json`
2. Display task progression (previous → current → next)
3. Display step progression within current task
4. Show last activity timestamp

---

## Output Format

```
═══════════════════════════════════════════════════════
              📍 CURRENT WORK CONTEXT
═══════════════════════════════════════════════════════

TASKS:
  ✅ Previous: PROJ-123 "Create Button atom"
     Completed: 2025-12-09 16:45

  🔄 Current:  PROJ-124 "Create FormField molecule"
     Started: 2025-12-09 17:00
     https://yourcompany.atlassian.net/browse/PROJ-124

  ⏳ Next:     PROJ-125 "Create Card molecule"

═══════════════════════════════════════════════════════

CURRENT TASK STEPS:

  ✅ Step 1: Write tests
     └─ "All 8 test cases passing"

  🔄 Step 2: Implement component (50%)
     └─ "Label and input done, error handling next"

  ⏳ Step 3: Style with tokens

  ⏳ Step 4: Self code review

  ⏳ Step 5: Update Jira & commit

═══════════════════════════════════════════════════════

Last updated: 2025-12-09 17:35
Session: 2025-12-09-afternoon

═══════════════════════════════════════════════════════
```

---

## If No Context Exists

```
⚠️ No .aid/context.json found

Would you like to:
  [1] Set up context for current task
  [2] Start fresh with a new task
  [3] Skip context tracking

>
```

---

## Quick Variants

```
/context              # Full display (above)
/context tasks        # Just task progression
/context steps        # Just current task steps
/context log          # Recent session log entries
```
