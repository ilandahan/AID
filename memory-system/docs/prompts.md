# AID Memory System - Prompt Templates

> All UI prompts and messages displayed to users.

---

## Improvement Suggestion (Session Start)

```
📊 I have {pending_count} feedback items waiting for analysis.
It's been {days} days / {sessions} sessions since last improvement.

Would you like to review insights and improve skills?

[Yes, let's improve] [No, continue working] [Remind me later]
```

---

## Role Selection

```
What's your role today?

• pm - Product Manager
• dev - Developer  
• qa - QA Engineer
• lead - Tech Lead
```

---

## Phase Selection

```
What phase are we in?

• discovery - Problem discovery and definition
• prd - Requirements definition
• tech-spec - Technical specification
• development - Development
• qa-ship - Testing and release
```

---

## Session Start Greeting

### New Session
```
Good morning! I'm ready to work with you as {role_display} in {phase_display}.
What are we working on today?
```

### Returning Session
```
Good morning! Last time we worked as {last_role} in {last_phase}.
Continue with that? [Yes] [No, something different]
```

---

## Phase Gate Flow

### Phase Summary
```
📋 Phase Summary: {phase_name}

Completed deliverables:
{deliverables_list}

Revisions made: {revision_count}
```

### Rating Request
```
📊 Quality Rating (1-5):

1 ⭐ - Poor, needs significant improvement
2 ⭐⭐ - Below average, missing important elements
3 ⭐⭐⭐ - Acceptable, worked but room for improvement
4 ⭐⭐⭐⭐ - Good, almost perfect
5 ⭐⭐⭐⭐⭐ - Excellent, exactly what I needed

Your rating: ___
```

### Qualitative Feedback
```
What worked well? (optional)
{pre_fill_what_worked}

What could be improved? (optional)
{pre_fill_what_didnt}

Additional notes? (optional): ___
```

### Feedback Confirmation
```
Thanks for the feedback! 🙏

{IF pending >= threshold:}
I now have {pending_count} feedback items for analysis.
When ready, run `/aid improve` to enhance skills.

Continue to next phase? [Yes] [No, done for today]
```

---

## Status Display

```
📊 AID Memory System Status

Current Session:
• Active: {active}
• Role: {role}
• Phase: {phase}
• Revisions so far: {revision_count}

Statistics:
• Total sessions: {total_sessions}
• Pending feedback: {pending_count}
• Sessions since last improvement: {sessions_since_improvement}

{IF improvement_suggested:}
💡 Recommended: Run /aid improve
```

---

## Improvement Flow

### Analysis Summary
```
📊 Feedback Analysis Summary

Analyzed: {feedback_count} feedback items
Period: {date_range}

Averages:
• Rating: {avg_rating} ({trend_indicator} from previous)
• Revisions: {avg_revisions} ({trend_indicator} from previous)

By Role/Phase:
{role_phase_breakdown}

Found:
• {positive_count} positive patterns to reinforce ✅
• {negative_count} negative patterns to address ⚠️
• {skill_suggestions_count} skill update recommendations
• {memory_candidates_count} Claude Memory candidates

Review recommendations one by one? [Yes] [Just summary]
```

### Skill Update Suggestion
```
📌 Recommendation {current}/{total}: Skill Update

Type: Update cumulative.md
Target: skills/roles/product-manager/cumulative.md
Section: High-Confidence Patterns
Confidence: {confidence}%

What was found:
{pattern_description}

Evidence:
• {occurrence_count} occurrences in feedback
• Average rating when applied: {avg_rating}
• Average revisions: {avg_revisions}
• Quotes:
  - "{quote_1}"
  - "{quote_2}"

Proposed change:
┌─────────────────────────────────────────────────────────────┐
│ {diff_preview}                                              │
└─────────────────────────────────────────────────────────────┘

[Approve ✓] [Edit 📝] [Reject ✗] [Skip ⏭️]
```

### Improvement Complete
```
✅ Improvement Complete!

Summary of changes:
• {skill_updates_count} skill file updates
• {memory_updates_count} Claude Memory updates

Feedback processed: {feedback_count}
Patterns identified: {patterns_count}

Changes will take effect in next session. 🚀

Start a new session? [/aid start]
```

---

## Error Messages

### No Pending Feedback
```
📭 No feedback items waiting for analysis.

Feedback is collected automatically at the end of each phase (/aid end).
Continue working and we'll improve when there's enough data!
```

### Not Enough Feedback
```
📊 Only {feedback_count} feedback items available.

For reliable pattern detection, at least 3 items are needed.
Continue anyway? [Yes] [No, wait for more]
```

### Analysis Error
```
⚠️ Error analyzing feedback.

Feedback saved in pending and will retry next time.
Error details: {error_message}
```

### Save Error
```
⚠️ Error saving {filename}

This change was not applied. Other changes will continue.
Error details: {error_message}
```

---

## Memory Commands

### Memory List Header
```
📝 AID Claude Memory Entries ({used}/{total} used)

Universal:
{universal_entries}

By Role:
{role_entries}

Phase-specific:
{phase_entries}
```

### Memory Stats
```
📊 Claude Memory Statistics

Slot Allocation:
• Universal: {universal_used}/{universal_max}
• Product Manager: {pm_used}/{pm_max}
• Developer: {dev_used}/{dev_max}
• QA Engineer: {qa_used}/{qa_max}
• Tech Lead: {lead_used}/{lead_max}
• Phase-specific: {phase_used}/{phase_max}
• Learned: {learned_used}/{learned_max}

Top Performers (by usage × rating):
{top_entries}

Promotion Candidates:
{candidates}
```

---

## Initialization

### Init Success
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

### Already Initialized
```
✅ AID Memory System already initialized.

Run /aid status to see current state.
Run /aid start to begin a session.
```

---

## Confirmation Prompts

### Reset Confirmation
```
⚠️ This will delete all feedback and reset statistics.
Skill files and Claude Memory will be preserved.

Type 'RESET' to confirm: ___
```

### Memory Replacement
```
📊 Memory slot full. Replace lowest-scoring entry?

Current entry (score: {current_score}):
{current_entry}

New entry (score: {new_score}):
{new_entry}

[Replace] [Keep current] [Cancel]
```
