# AID Memory System - Improvement Flow

> Complete implementation guide for the `/aid-improve` command.
>
> The exact commands are in `commands/aid-improve.md`. The pseudo-code below shows the
> logic. AID's own write commands (`memory-sync`, `memory-apply`) run only after you confirm
> them in Claude Code's prompt. `memory-apply` is also used by `/aid-recommendations`.
> Before Phase 4 the phase gate also refuses other writes outside the project. From
> Phase 4 on, AID does not stop other code from editing these files.
> The analysis sub-agent only proposes.

---

## Flow Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     /aid-improve                                │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 1: Gather Data                                             │
│ • aid_session.py memory-feedback: redacted feedback as JSON     │
│ • Optional: skill section headers, trends, memory entries       │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 2: Prepare Sub-Agent Input                                 │
│ • Format feedback batch (redacted, best effort)                 │
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
│ • User: [Apply ✓] [Reject ✗] [Skip ⏭️]                          │
│ • Track decisions                                               │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 6: Apply Approved Changes                                  │
│ • memory-apply <id>: append to cumulative.md (user confirms)    │
│ • memory-reject <id>: drop a proposal                           │
│ • memory-sync: write AID's local memory (user confirms)         │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 7: Archive & Update State                                  │
│ • Not implemented: do not do this by hand                       │
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

One Bash call (writes nothing, no prompt):

```bash
python "${CLAUDE_PLUGIN_ROOT}/hooks/aid_session.py" memory-feedback
```

It prints the feedback as JSON, read through the memory system's one reader and redacted
(best effort), so older files are redacted again when they are read. Never glob or open raw
files in `$AID_HOME/feedback/pending/`. Count the entries; if there are fewer than 3, stop
unless the user passed `--force`.

---

## Step 2: Prepare Sub-Agent Input

- `{{FEEDBACK_DATA}}`: the `memory-feedback` output from Step 1.
- `{{CURRENT_SKILLS}}` (optional, may be empty): section headers from
  `skills/memory-system/references/`.
- `{{TREND_DATA}}` (optional, may be empty).
- `{{MEMORY_ENTRIES}}` (optional, may be empty): the output of
  `python -m memory_system --memories` run from `memory-system/`, or leave it empty.

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
• {memory_candidates_count} AID local memory candidates

Review recommendations one by one? [Yes] [Just summary]
```

---

## Step 5: Review Suggestions One-by-One

For each suggestion, present:

```
📌 Recommendation {current}/{total}: Skill Update

Type: Update cumulative.md
Target: skills/memory-system/references/roles/product-manager/cumulative.md
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

[Apply ✓] [Reject ✗] [Skip ⏭️]
```

### User Actions

```python
def handle_user_action(action, suggestion):
    if action == "apply":
        # aid_session.py memory-apply <id>; Claude Code asks the user to confirm
        apply_suggestion(suggestion)
        return "approved"
    
    elif action == "reject":
        # aid_session.py memory-reject <id>; moves it to rejected.json
        reject_suggestion(suggestion)
        return "rejected"
    
    elif action == "skip":
        defer_suggestion(suggestion)
        return "skipped"
```

---

## Step 6: Apply Approved Changes

### Queue the Proposals

Save the agent's JSON to `.aid/improve/proposals.json` with the Write tool, then run (no
argument, no prompt; it reads that file itself and redacts each proposal):

```bash
python "${CLAUDE_PLUGIN_ROOT}/hooks/aid_session.py" memory-queue
```

### Apply Skill Update

One Bash call per proposal the user picked:

```bash
python "${CLAUDE_PLUGIN_ROOT}/hooks/aid_session.py" memory-apply <id>
```

- Claude Code asks the user to confirm. If the user declines, nothing changes.
- It only APPENDS the proposal's redacted text to
  `skills/memory-system/references/roles/<role>/cumulative.md` or
  `skills/memory-system/references/phases/<phase>/cumulative.md`. Any other target is
  refused.
- It writes the copy of `skills/memory-system/references/...` inside the installed plugin.
  A plugin update can replace that copy.
- The proposal moves from `$AID_HOME/recommendations/queue.json` to `applied.json`.
- Skill-wide recommendations (no learnings file) are shown but cannot be applied by the tool.

### Apply Memory Update

```bash
python "${CLAUDE_PLUGIN_ROOT}/hooks/aid_session.py" memory-sync
```

- Claude Code asks the user to confirm. In `-p`/headless sessions it is denied.
- It writes the entries shown by `memory-preview` to AID's local memory,
  `$AID_HOME/memory/slots.json`. Nothing is sent to Claude's built-in memory.
- Memory entries are built only from redacted text.

---

## Step 7: Archive & Update State

Not implemented: no command archives feedback, writes `processed/` batches, updates
`trends.json` or resets `~/.aid/state.json` counters. Do not do this by hand.

---

## Step 8: Final Summary

```
✅ Improvement Complete!

Summary of changes:
• {skill_updates_count} skill file updates
• {memory_updates_count} AID local memory updates

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

### Apply Refused or Declined

If `memory-apply <id>` exits non-zero, or the user declines the prompt, show the reason
verbatim. The change was not applied and the proposal stays in the queue. Do not retry in
another spelling and do not edit the file another way. Continue with other suggestions.

---

## Output Format from Sub-Agent

See `SUB-AGENT.md` for the complete specification of the analysis output format.

Key fields:
- `analysis_summary`: Overview statistics
- `by_role_phase`: Breakdown by role×phase
- `patterns_found`: Positive and negative patterns
- `suggestions`: Skill updates and memory candidates
- `trends_analysis`: Comparison with previous periods
