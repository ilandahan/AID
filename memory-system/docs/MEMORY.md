# AID Memory System - Claude Memory Management

> Guide for managing Claude Memory entries within the AID Memory System.

---

## Entry Format

All AID Memory entries follow this format:

```
AID:{ROLE}:{PHASE}:{TYPE} {insight}
```

### Components

| Component | Values | Description |
|-----------|--------|-------------|
| ROLE | PM, DEV, QA, LEAD, ALL | Target role |
| PHASE | DISC, PRD, SPEC, DEV, QA, ALL | Target phase |
| TYPE | DO, DONT, ASK, CHECK | Action type |

### Constraints

- Maximum **200 characters** total
- Must be **actionable** (start with verb)
- Must be **context-independent** (no project references)

---

## Slot Allocation

Total Claude Memory slots: **30**

| Category | Max Slots | Description |
|----------|-----------|-------------|
| Universal | 5 | AID:ALL:ALL:* entries |
| Product Manager | 5 | AID:PM:* entries |
| Developer | 5 | AID:DEV:* entries |
| QA Engineer | 5 | AID:QA:* entries |
| Tech Lead | 3 | AID:LEAD:* entries |
| Phase-specific | 5 | AID:*:{phase}:* entries |
| Learned | 10 | Patterns promoted from feedback |

---

## 20 Starter Entries

### Universal (5)

```
AID:ALL:ALL:DO Confirm understanding before producing deliverable
AID:ALL:ALL:CHECK Verify scope hasn't crept since last checkpoint
AID:ALL:ALL:DO Break large outputs into reviewable chunks
AID:ALL:ALL:DONT Never skip phase gate human approval
AID:ALL:ALL:ASK "What does success look like?" before starting
```

### Product Manager (5)

```
AID:PM:DISC:ASK "Who else touches this data?" for stakeholders
AID:PM:DISC:DO Use SCQ format for problem statements
AID:PM:PRD:DO User stories: As [who] I want [what] so that [why]
AID:PM:PRD:DONT No implementation details in requirements
AID:PM:PRD:CHECK All acceptance criteria are testable
```

### Developer (5)

```
AID:DEV:SPEC:DO Include error handling for every endpoint
AID:DEV:SPEC:DO Define API contracts before implementation
AID:DEV:DEV:DO Write test first, then implement (TDD)
AID:DEV:DEV:DONT No test-specific logic in implementation
AID:DEV:DEV:CHECK Run all tests before marking complete
```

### QA Engineer (5)

```
AID:QA:QA:DO Test with realistic data (unicode, long strings)
AID:QA:QA:DO Cover happy path, edge cases, AND error conditions
AID:QA:QA:DONT Don't weaken tests to make them pass
AID:QA:QA:CHECK Integration tests exist for critical paths
AID:QA:QA:DO Use real DB/Redis in tests, minimize mocking
```

---

## Promotion Criteria

Patterns from feedback analysis can be promoted to Claude Memory when **ALL** criteria are met:

| Criterion | Threshold | Description |
|-----------|-----------|-------------|
| Occurrences | ≥5 sessions | Pattern appeared in 5+ sessions |
| Avg Rating | ≥4.0 | When pattern was applied |
| Avg Revisions | ≤2.0 | When pattern was applied |
| Human Approved | Yes | User approved during /aid improve |
| Fits Limit | ≤200 chars | Entry fits character limit |
| Not Duplicate | Unique | Not already in memory |
| Context-Free | Yes | No project-specific references |

---

## Replacement Policy

When a slot category is full and a new entry qualifies:

### Step 1: Calculate Value Score

```
value_score = (times_used × avg_rating) / sqrt(age_in_days)
```

### Step 2: Compare

New entry competes **only within its category**:
- New PM entry competes with existing PM entries
- Universal competes with universal
- Learned competes with learned

### Step 3: Present to User

```
📊 Memory slot full. Replace lowest-scoring entry?

Current entry (score: 3.2):
AID:PM:DISC:DO Use stakeholder template for mapping

New entry (score: 4.5):
AID:PM:DISC:ASK "Who approves the budget?" early

[Replace] [Keep current] [Cancel]
```

### Step 4: Archive

Replaced entries are logged in `memory-tracking.json` under `retirement_history`.

---

## Memory Commands

### View All Entries

```
/aid memory list
```

Output:
```
📝 AID Claude Memory Entries (20/30 used)

Universal (5/5):
  1. AID:ALL:ALL:DO Confirm understanding before producing deliverable
  2. AID:ALL:ALL:CHECK Verify scope hasn't crept since last checkpoint
  ...

Product Manager (5/5):
  6. AID:PM:DISC:ASK "Who else touches this data?" for stakeholders
  ...

Developer (5/5):
  ...

QA Engineer (5/5):
  ...

Learned (0/10):
  (none yet)
```

### View Statistics

```
/aid memory stats
```

Output:
```
📊 Claude Memory Statistics

Slot Allocation:
• Universal: 5/5 (100%)
• Product Manager: 5/5 (100%)
• Developer: 5/5 (100%)
• QA Engineer: 5/5 (100%)
• Tech Lead: 0/3 (0%)
• Phase-specific: 0/5 (0%)
• Learned: 0/10 (0%)

Top Performers (by usage × rating):
1. AID:DEV:DEV:DO Write test first... (score: 4.8)
2. AID:PM:DISC:ASK Who else touches... (score: 4.5)

Promotion Candidates:
• "Check API contracts before..." (5 uses, 4.2 avg rating)
```

---

## Memory Tracking File

Location: `~/.aid/metrics/memory-tracking.json`

Structure:
```json
{
  "version": "1.0",
  "last_sync": "2025-01-15T10:30:00Z",
  "slot_allocation": {
    "universal": {
      "max_slots": 5,
      "entries": [
        {
          "line_number": 1,
          "entry": "AID:ALL:ALL:DO Confirm understanding...",
          "added_date": "2025-01-01",
          "source": "starter",
          "times_used": 12,
          "avg_rating_when_relevant": 4.2
        }
      ]
    }
  },
  "promotion_history": [],
  "retirement_history": [],
  "usage_tracking": []
}
```

---

## Manual Memory Management

### Add Entry

```python
memory_user_edits(command="add", control="AID:DEV:DEV:DO New pattern here")
```

### Remove Entry

```python
memory_user_edits(command="remove", line_number=15)
```

### Replace Entry

```python
memory_user_edits(
    command="replace",
    line_number=15,
    replacement="AID:DEV:DEV:DO Updated pattern here"
)
```

### View Current

```python
memory_user_edits(command="view")
```

---

## Best Practices

### Writing Good Entries

**DO:**
- Start with an action verb
- Be specific and actionable
- Include brief context when helpful
- Keep under 200 characters

**DON'T:**
- Reference specific projects
- Be too vague ("do good work")
- Include implementation details
- Exceed character limit

### Examples

| Good ✅ | Bad ❌ |
|---------|--------|
| `AID:PM:DISC:ASK "Who else touches this data?"` | `Remember stakeholders` |
| `AID:DEV:DEV:DO Write test first (TDD)` | `Testing is important` |
| `AID:QA:QA:DONT Never weaken tests to pass` | `Don't do bad things` |

---

## Sync and Recovery

### Check Sync Status

At session start, the system compares `memory-tracking.json` with actual Claude Memory. If discrepancies are found:

```
⚠️ Memory tracking out of sync.

Found in tracking but not in memory: 2 entries
Found in memory but not tracked: 1 entry

Rebuilding tracking file...
✅ Sync complete.
```

### Force Sync

```
/aid memory sync
```

This rebuilds `memory-tracking.json` from actual Claude Memory state.
