# AID Memory System - Main Agent Behavior

> This file defines how Claude should behave when working within the AID Memory System.
> Load this at the start of any AID-enabled session.

---

## Quick Reference

### Commands
| Command | Description |
|---------|-------------|
| `/aid-init` | Initialize AID system (first time setup) |
| `/aid-start [role] [phase]` | Start a session |
| `/aid-status` | Show current session state |
| `/aid-end` | Complete phase gate, collect feedback |
| `/aid-improve` | Run improvement analysis (sub-agent) |

### Roles
- `product-manager` (pm)
- `developer` (dev)
- `qa-engineer` (qa)
- `tech-lead` (lead)

### Phases
- `discovery`
- `prd`
- `tech-spec`
- `development`
- `qa-ship`

---

## 1. Session Start Flow

When user starts a conversation or says `/aid-start`:

### Step 1: Check AID Directory
```
IF ~/.aid/ does not exist:
  → Run /aid-init flow
  → Create directory structure
  → Initialize with defaults
  → Display: "🚀 AID Memory System initialized!"
```

### Step 2: Load State
```python
# Read state.json
state = load("~/.aid/state.json")

# Check improvement suggestion conditions
pending = state.statistics.pending_feedback_count
sessions = state.statistics.sessions_since_last_improvement
last_run = state.statistics.last_improvement_run
```

### Step 3: Check Improvement Suggestion
```
IF state.notifications.improvement_suggested == true:
  
  Display:
  """
  📊 I have {pending} feedback items waiting for analysis.
  It's been {days} days / {sessions} sessions since last improvement.
  
  Would you like to review insights and improve skills?
  
  [Yes, let's improve] [No, continue working] [Remind me later]
  """
  
  IF user chooses "Yes":
    → Go to /aid-improve flow
  ELSE:
    → Continue to Step 4
```

### Step 4: Determine Role & Phase
```
IF /aid-start <role> <phase> provided:
  → Use provided values
ELIF state.last_session exists:
  → Suggest: "Continue as {last_role} in {last_phase}?"
ELSE:
  → Ask: "What's your role today? (pm/dev/qa/lead)"
  → Ask: "What phase are we in? (discovery/prd/tech-spec/development/qa-ship)"
```

### Step 5: Load Skills
```
Load and internalize:
1. skills/memory-system/references/roles/{role}/QUICK-REFERENCE.md
2. skills/memory-system/references/roles/{role}/cumulative.md
3. skills/memory-system/references/phases/{phase}/QUICK-REFERENCE.md
4. skills/memory-system/references/phases/{phase}/cumulative.md

AID's local memory (AID:* entries in `$AID_HOME/memory/slots.json`) is read when present
```

### Step 6: Update State & Begin
```python
# Do NOT edit state.json. `aid_session.py start <role> <phase>` (and `/aid-end`,
# `aid_session.py end`) is the only writer of `.aid/state.json`: it sets
# current_session (active, role, phase, started) itself. The file is protected and a
# direct Edit/Write to it is denied.
run("aid_session.py start {role} {phase}")

# Greet user
print(f"Good morning! I'm ready to work with you as {role_display} in {phase_display}.")
print("What are we working on today?")
```

---

## 2. Session Work Flow

### Apply Skills
During work, actively apply guidance from:
- Role SKILL.md (how this role operates)
- Role cumulative.md (learned patterns)
- Phase SKILL.md (phase requirements)
- Phase cumulative.md (phase learnings)
- AID:* entries in AID's local memory

### Track Revisions (Internal Counter)
```python
revision_triggers = [
  "fix", "change", "update", "wrong", "missing", "add",
  "incorrect", "error", "should be", "not right", "revise",
  "that's not", "actually", "instead"
]

# On each user message:
IF message contains any revision trigger:
  revision_count += 1
  # Note what needed fixing (for feedback)
  what_didnt_notes.append(brief_description)
```

### Note Patterns (Internal)
```python
# Track what's working well
positive_triggers = ["great", "perfect", "exactly", "good", "excellent",
                     "nice", "well done", "that's right"]

IF message contains positive trigger:
  what_worked_notes.append(context)
```

### Detect Phase Gate
```python
phase_complete_triggers = [
  "done", "approved", "next phase", "complete",
  "finished", "move on", "all good", "looks good",
  "ship it", "let's proceed"
]

IF message contains phase_complete trigger OR user says /aid-end:
  → Go to Phase Gate Flow
```

---

## 3. Phase Gate Flow (Feedback Collection)

When phase completion is detected:

### Step 1: Display Summary
```
Display:
"""
📋 Phase Summary: {phase_display_name}

Completed deliverables:
• {deliverable_1}
• {deliverable_2}

Revisions made: {revision_count}
"""
```

### Step 2: Request Rating (MANDATORY)
```
Display:
"""
📊 Quality Rating (1-5):

1 ⭐ - Poor, needs significant improvement
2 ⭐⭐ - Below average, missing important elements  
3 ⭐⭐⭐ - Acceptable, worked but room for improvement
4 ⭐⭐⭐⭐ - Good, almost perfect
5 ⭐⭐⭐⭐⭐ - Excellent, exactly what I needed

Your rating: ___
"""

# MUST get rating before proceeding
WHILE rating not received OR rating not in [1,2,3,4,5]:
  → Request rating again
```

### Step 3: Request Qualitative Feedback (Optional)
```
Display:
"""
What worked well? (optional)
{pre_fill: what_worked_notes if any}

What could be improved? (optional)
{pre_fill: what_didnt_notes if any}

Additional notes? (optional): ___
"""

# User can skip by saying "none" or pressing enter
```

### Step 4: Save Feedback
Do not write a feedback JSON file yourself. Run `/aid-end`, which saves feedback with ONE
call: `python "${CLAUDE_PLUGIN_ROOT}/hooks/aid_session.py" end --rating <1-5> --worked "..." --improve "..."`.
It writes `$AID_HOME/feedback/pending/<timestamp>.json` (default `~/.aid/feedback/pending/`)
and redacts the text (best effort) before writing. `/phase-approve` (`aid_session.py approve`)
is the only other writer: it stores its rating as a pending entry too.

### Step 5: Update State
```python
state = load("~/.aid/state.json")

# Update statistics
state.statistics.total_sessions += 1
state.statistics.total_feedback_collected += 1
state.statistics.pending_feedback_count += 1
state.statistics.sessions_since_last_improvement += 1

# End current session
state.current_session.active = false
state.last_session = {
  "role": current_role,
  "phase": current_phase,
  "completed_at": now_iso()
}

# Check improvement trigger
config = load("~/.aid/config.yaml")
if (state.statistics.pending_feedback_count >= config.improvement.auto_prompt_after_sessions
    or state.statistics.sessions_since_last_improvement >= config.improvement.auto_prompt_after_sessions):
  state.notifications.improvement_suggested = true
  state.notifications.reason = f"{state.statistics.pending_feedback_count} feedbacks pending"

save(state)
```

### Step 6: Confirm & Offer Next Steps
```
Display:
"""
Thanks for the feedback! 🙏

{IF pending >= threshold:}
I now have {pending} feedback items for analysis.
When you're ready, run `/aid-improve` to enhance skills.

Continue to next phase? [Yes] [No, done for today]
"""
```

---

## 4. Status Command (/aid-status)

```
Display:
"""
📊 AID Memory System Status

Current Session:
• Active: {active}
• Role: {role}
• Phase: {phase}
• Revisions so far: {revision_count}

Statistics:
• Total sessions: {total_sessions}
• Pending feedback: {pending_feedback_count}
• Sessions since last improvement: {sessions_since_last_improvement}

{IF improvement_suggested:}
💡 Recommended: Run /aid-improve
"""
```

---

## 5. Feedback Privacy (redaction is best effort)

Feedback text is redacted before it is written and again whenever it is read. Redaction
replaces e-mails, URLs, absolute paths, `file.ext:line` references, common secret tokens, the
project's own names (folder names, git remote owner and repo) and the OS user name with
placeholders (`[email]`, `[url]`, `[path]`, `[file-ref]`, `[token]`, `[project]`, `[user]`). It does not
catch a person's or company's name written as plain words unless it is one of those project
names. So when you condense the user's answers, still leave these out.

### NEVER include in feedback:
- ❌ Project name or identifier
- ❌ Company name
- ❌ Domain-specific terms (e.g., "employee time tracking")
- ❌ Technical implementation details
- ❌ Code snippets
- ❌ File paths from project
- ❌ User names or identifiers
- ❌ Business logic specifics

### ALWAYS include in feedback:
- ✅ Role (product-manager, developer, etc.)
- ✅ Phase (discovery, prd, etc.)
- ✅ Rating (1-5)
- ✅ Revision count
- ✅ Generic what worked/didn't (methodology level)
- ✅ Duration metrics

### Example - What to capture:
```
# User says: "You missed the IT stakeholder in the attendance system project"
# Capture as: "Missed stakeholder in first draft"

# User says: "The SCQ format was excellent for describing the data entry problem"  
# Capture as: "SCQ format worked well"
```

---

## 6. Language Handling

- **Default**: English
- **Prompts**: Display in user's preferred language (config.yaml)
- **Feedback**: Store in whatever language user provides
- **Technical terms**: Keep in English (e.g., "stakeholder", "PRD")

---

## 7. Error Handling

### Missing ~/.aid/ directory
```
→ Run /aid-init automatically
→ "🚀 AID Memory System initialized! Let's begin."
```

### Missing skill files
```
→ Use default behavior
→ Log warning: "skill file not found: {path}"
→ Continue working
```

### Corrupted state.json
```
→ Backup corrupted file
→ Create fresh state.json
→ Warn user: "⚠️ State file was reset. Previous session data lost."
```

### User refuses to give rating
```
→ Gently insist: "The rating helps me learn and improve. Can you give a score from 1 to 5?"
→ After 3 attempts: "Okay, saving feedback without rating (flagged for review)"
→ Save with rating: null, flag: "rating_skipped"
```
