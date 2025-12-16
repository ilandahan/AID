# AID Memory System - Improvement Flow

> Complete implementation guide for the `/aid improve` command.

---

## Flow Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     /aid improve                                │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 1: Gather Data                                             │
│ • Load all feedback from ~/.aid/feedback/pending/               │
│ • Load current skill files                                      │
│ • Load trends.json                                              │
│ • Load memory-tracking.json                                     │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 2: Prepare Sub-Agent Input                                 │
│ • Format feedback batch (anonymized)                            │
│ • Summarize current skills                                      │
│ • List current memory entries                                   │
│ • Include trend data                                            │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 3: Run Sub-Agent Analysis                                  │
│ • Load SUB-AGENT.md system prompt                               │
│ • Process with analysis input                                   │
│ • Get structured output                                         │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 4: Present Summary                                         │
│ • Show analysis overview                                        │
│ • Show pattern counts                                           │
│ • Ask user to proceed or skip                                   │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 5: Review Suggestions One-by-One                           │
│ • Present each suggestion with evidence                         │
│ • User: [Approve ✓] [Edit 📝] [Reject ✗] [Skip ⏭️]              │
│ • Track decisions                                               │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 6: Apply Approved Changes                                  │
│ • Update skill files (cumulative.md)                            │
│ • Update Claude Memory (if approved)                            │
│ • Update memory-tracking.json                                   │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 7: Archive & Update State                                  │
│ • Create batch summary in processed/                            │
│ • Archive or delete pending feedback                            │
│ • Update trends.json                                            │
│ • Reset state counters                                          │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 8: Final Summary                                           │
│ • Report changes made                                           │
│ • Confirm completion                                            │
└─────────────────────────────────────────────────────────────────┘
```

---

## Step 1: Gather Data

```python
def gather_data():
    # Load pending feedback
    feedback_files = glob("~/.aid/feedback/pending/FB-*.json")
    feedback_batch = [load_json(f) for f in feedback_files]
    
    # Load current skills
    skills = {
        "roles": load_all_role_skills(),
        "phases": load_all_phase_skills()
    }
    
    # Load metrics
    trends = load_json("~/.aid/metrics/trends.json")
    memory_tracking = load_json("~/.aid/metrics/memory-tracking.json")
    
    return {
        "feedback": feedback_batch,
        "skills": skills,
        "trends": trends,
        "memory_tracking": memory_tracking
    }
```

---

## Step 2: Prepare Sub-Agent Input

```python
def prepare_subagent_input(data):
    # Simplify feedback for analysis (already anonymized)
    simplified_feedback = [
        {
            "id": fb["id"],
            "role": fb["context"]["role"],
            "phase": fb["context"]["phase"],
            "rating": fb["metrics"]["rating"],
            "revisions": fb["metrics"]["revisions"],
            "what_worked": fb["qualitative"]["what_worked"],
            "what_didnt": fb["qualitative"]["what_didnt"],
            "note": fb["qualitative"]["user_note"]
        }
        for fb in data["feedback"]
    ]
    
    # Summarize current skills (just section headers)
    skills_summary = summarize_skills(data["skills"])
    
    # List current memory entries
    memory_entries = get_aid_memory_entries()
    
    return {
        "feedback_batch": simplified_feedback,
        "current_skills_summary": skills_summary,
        "current_memory_entries": memory_entries,
        "recent_trends": data["trends"]["recent_averages"]
    }
```

---

## Step 3: Run Sub-Agent Analysis

```python
def run_subagent(input_data):
    # Load sub-agent system prompt
    system_prompt = load("~/.aid/SUB-AGENT.md")
    
    # Run analysis
    analysis_output = claude_analyze(
        system=system_prompt,
        input=json.dumps(input_data)
    )
    
    # Parse structured output
    return json.loads(analysis_output)
```

---

## Step 4: Present Summary

Display analysis overview:

```
📊 Feedback Analysis Summary

Analyzed: {feedback_count} feedback items
Period: {date_range}

Averages:
• Rating: {avg_rating} ({trend_indicator} from previous)
• Revisions: {avg_revisions} ({trend_indicator} from previous)

By Role/Phase:
• PM/Discovery: 4 feedbacks, avg 4.2
• Dev/Development: 3 feedbacks, avg 3.8
• ...

Found:
• {positive_count} positive patterns to reinforce ✅
• {negative_count} negative patterns to address ⚠️
• {skill_suggestions_count} skill update recommendations
• {memory_candidates_count} Claude Memory candidates

Review recommendations one by one? [Yes] [Just summary]
```

---

## Step 5: Review Suggestions One-by-One

For each suggestion, present:

```
📌 Recommendation {current}/{total}: Skill Update

Type: Update cumulative.md
Target: skills/roles/product-manager/cumulative.md
Section: High-Confidence Patterns
Confidence: 85%

What was found:
Asking "Who else touches this data?" early in Discovery
prevents stakeholder misses.

Evidence:
• 4 occurrences in feedback
• Average rating when applied: 4.3
• Average revisions: 1.2
• Quotes:
  - "Data flow question helped"
  - "Asking who touches data was useful"

Proposed change:
┌─────────────────────────────────────────────────────────────┐
│ ### Discovery Phase                                         │
│ + - **Ask about data flow early**: "Who else touches this   │
│ +   data?" prevents stakeholder misses                      │
│ +   (Evidence: 4 sessions, 4.3 avg rating)                  │
└─────────────────────────────────────────────────────────────┘

[Approve ✓] [Edit 📝] [Reject ✗] [Skip ⏭️]
```

### User Actions

```python
def handle_user_action(action, suggestion):
    if action == "approve":
        apply_suggestion(suggestion)
        return "approved"
    
    elif action == "edit":
        edited = prompt_for_edit(suggestion)
        apply_suggestion(edited)
        return "approved_with_edits"
    
    elif action == "reject":
        log_rejection(suggestion, reason=prompt_for_reason())
        return "rejected"
    
    elif action == "skip":
        defer_suggestion(suggestion)
        return "skipped"
```

---

## Step 6: Apply Approved Changes

### Apply Skill Update

```python
def apply_skill_update(suggestion):
    filepath = suggestion["target_file"]
    section = suggestion["target_section"]
    content = suggestion["content"]
    
    # Read current file
    skill_file = load(filepath)
    
    # Find section
    section_start = find_section(skill_file, section)
    
    # Insert/modify content
    updated = insert_at_section(skill_file, section_start, content)
    
    # Add metadata
    updated = add_update_metadata(updated, suggestion["evidence"])
    
    # Save
    save(filepath, updated)
```

### Apply Memory Update

```python
def apply_memory_update(suggestion):
    entry = suggestion["entry"]
    action = suggestion["action"]  # "add" or "replace"
    
    if action == "add":
        memory_user_edits(command="add", control=entry)
    
    elif action == "replace":
        line_number = suggestion["replace_line"]
        memory_user_edits(
            command="replace",
            line_number=line_number,
            replacement=entry
        )
    
    # Update tracking
    update_memory_tracking(entry, action)
```

---

## Step 7: Archive & Update State

### Create Batch Summary

```python
def archive_batch(feedback_batch, analysis, decisions):
    batch_summary = {
        "id": f"BATCH-{timestamp}",
        "processed_at": now_iso(),
        "feedback_count": len(feedback_batch),
        "feedback_ids": [fb["id"] for fb in feedback_batch],
        "analysis_summary": {
            "patterns_found": len(analysis["patterns"]),
            "suggestions_made": len(analysis["suggestions"]),
            "approved": sum(1 for d in decisions if d == "approved"),
            "rejected": sum(1 for d in decisions if d == "rejected"),
            "skipped": sum(1 for d in decisions if d == "skipped")
        }
    }
    
    save(f"~/.aid/feedback/processed/BATCH-{timestamp}.json", batch_summary)
```

### Update Trends

```python
def update_trends(feedback_batch, trends):
    # Calculate new averages
    new_avg_rating = average([fb["metrics"]["rating"] for fb in feedback_batch])
    new_avg_revisions = average([fb["metrics"]["revisions"] for fb in feedback_batch])
    
    # Update rolling averages
    trends["recent_averages"]["rating"] = rolling_average(
        trends["recent_averages"]["rating"],
        new_avg_rating
    )
    trends["recent_averages"]["revisions"] = rolling_average(
        trends["recent_averages"]["revisions"],
        new_avg_revisions
    )
    
    # Add to history
    trends["history"].append({
        "date": today(),
        "feedback_count": len(feedback_batch),
        "avg_rating": new_avg_rating,
        "avg_revisions": new_avg_revisions
    })
    
    save("~/.aid/metrics/trends.json", trends)
```

### Reset State Counters

```python
def reset_state_counters():
    state = load("~/.aid/state.json")
    
    state["statistics"]["pending_feedback_count"] = 0
    state["statistics"]["sessions_since_last_improvement"] = 0
    state["statistics"]["last_improvement_run"] = now_iso()
    state["notifications"]["improvement_suggested"] = False
    state["notifications"]["reason"] = None
    
    save("~/.aid/state.json", state)
```

### Delete/Archive Pending Feedback

```python
def cleanup_pending_feedback(feedback_files):
    for filepath in feedback_files:
        # Option A: Delete
        delete(filepath)
        
        # Option B: Move to processed
        # move(filepath, filepath.replace("pending", "processed"))
```

---

## Step 8: Final Summary

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

## Error Handling

### No Pending Feedback

```python
if len(feedback_batch) == 0:
    display("""
    📭 No feedback items waiting for analysis.
    
    Feedback is collected automatically at the end of each phase (/aid end).
    Continue working and we'll improve when there's enough data!
    """)
    return
```

### Not Enough Data

```python
if len(feedback_batch) < 3:
    display(f"""
    📊 Only {len(feedback_batch)} feedback items available.
    
    For reliable pattern detection, at least 3 items are needed.
    Continue anyway? [Yes] [No, wait for more]
    """)
    
    if not user_confirms():
        return
```

### Sub-Agent Failure

```python
try:
    analysis = run_subagent(input_data)
except Exception as e:
    display(f"""
    ⚠️ Error analyzing feedback.
    
    Feedback saved in pending and will retry next time.
    Error details: {str(e)}
    """)
    return
```

### File Write Error

```python
try:
    apply_skill_update(suggestion)
except IOError as e:
    display(f"""
    ⚠️ Error saving {suggestion['target_file']}
    
    This change was not applied. Other changes will continue.
    Error details: {str(e)}
    """)
    continue  # Continue with other suggestions
```

---

## Output Format from Sub-Agent

See `SUB-AGENT.md` for the complete specification of the analysis output format.

Key fields:
- `analysis_summary`: Overview statistics
- `by_role_phase`: Breakdown by role×phase
- `patterns_found`: Positive and negative patterns
- `suggestions`: Skill updates and memory candidates
- `trends_analysis`: Comparison with previous periods
