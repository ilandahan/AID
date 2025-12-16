# AID Memory System - Memory Initialization

> Implementation guide for initializing Claude Memory with starter entries.

---

## Initialization Flow

### Step 1: View Current Memory

```python
def get_current_memory():
    result = memory_user_edits(command="view")
    return parse_memory_entries(result)
```

### Step 2: Identify Missing Entries

```python
def get_missing_starters(current_entries):
    starters = load_starter_entries()  # From MEMORY.md
    current_aid_entries = [e for e in current_entries if e.startswith("AID:")]
    
    missing = []
    for starter in starters:
        if not any(starter in entry for entry in current_aid_entries):
            missing.append(starter)
    
    return missing
```

### Step 3: Add Missing Entries

```python
def add_missing_entries(missing):
    added = []
    for entry in missing:
        try:
            memory_user_edits(command="add", control=entry)
            added.append(entry)
        except Exception as e:
            log_error(f"Failed to add: {entry}", e)
    
    return added
```

### Step 4: Update Tracking

```python
def update_tracking_after_init(added_entries):
    tracking = load_json("~/.aid/metrics/memory-tracking.json")
    
    # Get current line numbers
    current = memory_user_edits(command="view")
    
    for entry in added_entries:
        line_number = find_line_number(current, entry)
        category = categorize_entry(entry)
        
        tracking["slot_allocation"][category]["entries"].append({
            "line_number": line_number,
            "entry": entry,
            "added_date": today(),
            "source": "starter",
            "times_used": 0,
            "avg_rating_when_relevant": None
        })
    
    tracking["last_sync"] = now_iso()
    save_json("~/.aid/metrics/memory-tracking.json", tracking)
```

---

## Starter Entries (20 Total)

### Universal (5 entries)

```
AID:ALL:ALL:DO Confirm understanding before producing deliverable
AID:ALL:ALL:CHECK Verify scope hasn't crept since last checkpoint
AID:ALL:ALL:DO Break large outputs into reviewable chunks
AID:ALL:ALL:DONT Never skip phase gate human approval
AID:ALL:ALL:ASK "What does success look like?" before starting
```

### Product Manager (5 entries)

```
AID:PM:DISC:ASK "Who else touches this data?" for stakeholders
AID:PM:DISC:DO Use SCQ format for problem statements
AID:PM:PRD:DO User stories: As [who] I want [what] so that [why]
AID:PM:PRD:DONT No implementation details in requirements
AID:PM:PRD:CHECK All acceptance criteria are testable
```

### Developer (5 entries)

```
AID:DEV:SPEC:DO Include error handling for every endpoint
AID:DEV:SPEC:DO Define API contracts before implementation
AID:DEV:DEV:DO Write test first, then implement (TDD)
AID:DEV:DEV:DONT No test-specific logic in implementation
AID:DEV:DEV:CHECK Run all tests before marking complete
```

### QA Engineer (5 entries)

```
AID:QA:QA:DO Test with realistic data (unicode, long strings)
AID:QA:QA:DO Cover happy path, edge cases, AND error conditions
AID:QA:QA:DONT Don't weaken tests to make them pass
AID:QA:QA:CHECK Integration tests exist for critical paths
AID:QA:QA:DO Use real DB/Redis in tests, minimize mocking
```

---

## Promotion Implementation

### Check Promotion Criteria

```python
def meets_promotion_criteria(pattern):
    return (
        pattern["occurrences"] >= 5 and
        pattern["avg_rating"] >= 4.0 and
        pattern["avg_revisions"] <= 2.0 and
        len(pattern["entry"]) <= 200 and
        is_context_independent(pattern["entry"]) and
        not is_duplicate(pattern["entry"])
    )
```

### Find Slot for Entry

```python
def find_slot_for_entry(entry, tracking):
    category = categorize_entry(entry)
    cat_data = tracking["slot_allocation"][category]
    
    # Check if room in category
    if len(cat_data["entries"]) < cat_data["max_slots"]:
        return {"action": "add", "category": category}
    
    # Find lowest scoring entry
    lowest = min(
        cat_data["entries"],
        key=lambda e: calculate_value_score(e)
    )
    
    new_score = calculate_value_score(entry)
    if new_score > calculate_value_score(lowest):
        return {
            "action": "replace",
            "category": category,
            "replace_entry": lowest,
            "replace_line": lowest["line_number"]
        }
    
    return {"action": "none", "reason": "New entry doesn't score higher"}
```

### Execute Promotion

```python
def execute_promotion(entry, slot_info, tracking):
    if slot_info["action"] == "add":
        memory_user_edits(command="add", control=entry)
        
    elif slot_info["action"] == "replace":
        memory_user_edits(
            command="replace",
            line_number=slot_info["replace_line"],
            replacement=entry
        )
        
        # Log retirement
        tracking["retirement_history"].append({
            "entry": slot_info["replace_entry"]["entry"],
            "retired_date": today(),
            "reason": "replaced_by_higher_score",
            "replaced_by": entry
        })
    
    # Log promotion
    tracking["promotion_history"].append({
        "entry": entry,
        "promoted_date": today(),
        "category": slot_info["category"],
        "source": "feedback_analysis"
    })
    
    save_tracking(tracking)
```

---

## Category Detection

```python
def categorize_entry(entry):
    # Parse AID:{ROLE}:{PHASE}:{TYPE}
    parts = entry.split(":")
    if len(parts) < 4:
        return "learned"
    
    role = parts[1]
    phase = parts[2]
    
    # Specific role
    role_map = {
        "PM": "product_manager",
        "DEV": "developer",
        "QA": "qa_engineer",
        "LEAD": "tech_lead"
    }
    
    if role in role_map and phase != "ALL":
        return role_map[role]
    
    # Universal
    if role == "ALL" and phase == "ALL":
        return "universal"
    
    # Phase-specific (role is ALL, phase is specific)
    if role == "ALL" and phase != "ALL":
        return "phase_specific"
    
    # Default to learned
    return "learned"
```

---

## Error Handling

### Entry Too Long

```python
if len(entry) > 200:
    # Suggest shortened version
    shortened = shorten_entry(entry)
    display(f"""
    ⚠️ Entry exceeds 200 character limit ({len(entry)} chars).
    
    Original: {entry}
    
    Suggested shortened version:
    {shortened}
    
    Use shortened version? [Yes] [Edit manually] [Cancel]
    """)
```

### Memory Full (No Lower Score)

```python
if slot_info["action"] == "none":
    display(f"""
    📊 Memory category '{category}' is full.
    
    New entry score: {new_score}
    Lowest existing score: {lowest_score}
    
    The new entry doesn't score high enough to replace existing entries.
    It will be kept in cumulative.md for future consideration.
    """)
```

### API Error

```python
try:
    memory_user_edits(command="add", control=entry)
except Exception as e:
    display(f"""
    ⚠️ Failed to add to Claude Memory.
    
    Entry saved to retry queue.
    Error: {str(e)}
    """)
    
    # Save to retry queue
    tracking["pending_adds"].append({
        "entry": entry,
        "failed_at": now_iso(),
        "error": str(e)
    })
```

---

## Sync Check

At each session start:

```python
def check_memory_sync():
    tracking = load_tracking()
    actual = get_current_memory()
    
    # Build expected set from tracking
    expected = set()
    for category in tracking["slot_allocation"].values():
        for entry in category.get("entries", []):
            expected.add(entry["entry"])
    
    # Compare
    actual_aid = {e for e in actual if e.startswith("AID:")}
    
    missing_from_memory = expected - actual_aid
    missing_from_tracking = actual_aid - expected
    
    if missing_from_memory or missing_from_tracking:
        display("⚠️ Memory tracking out of sync. Rebuilding...")
        rebuild_tracking(actual_aid)
        display("✅ Sync complete.")
```

---

## Initialization Script

Complete initialization sequence:

```python
def init_memory_system():
    # 1. Check if already initialized
    tracking = load_tracking()
    if tracking.get("initialized"):
        return "Already initialized"
    
    # 2. Get current memory state
    current = get_current_memory()
    
    # 3. Identify missing starters
    missing = get_missing_starters(current)
    
    # 4. Add missing entries
    if missing:
        display(f"Adding {len(missing)} starter entries to Claude Memory...")
        added = add_missing_entries(missing)
        display(f"✅ Added {len(added)} entries.")
    
    # 5. Update tracking
    update_tracking_after_init(added)
    
    # 6. Mark as initialized
    tracking["initialized"] = True
    tracking["initialized_at"] = now_iso()
    save_tracking(tracking)
    
    return f"Initialized with {len(added)} entries"
```
