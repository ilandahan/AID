# /context-update

Manually update work context.

## Usage

```
/context-update                      # Interactive update
/context-update step done            # Mark current step done
/context-update step "Step name"     # Set current step
/context-update task PROJ-125        # Switch to new task
/context-update note "message"       # Add note to current step
/context-update progress 75%         # Update progress percentage
```

---

## Interactive Mode

When run without arguments:

```
═══════════════════════════════════════════════════════
              ✏️  UPDATE CONTEXT
═══════════════════════════════════════════════════════

Current:
  Task: PROJ-124 "Create FormField molecule"
  Step: Implement component (50%)

What would you like to update?

  [1] Mark current step DONE
  [2] Update step progress
  [3] Add note to current step
  [4] Switch to different task
  [5] Mark task DONE and move to next

>
```

---

## Actions

### Mark Step Done

```
/context-update step done
```

Triggers:
1. Move current step → previous (mark done)
2. Move next step → current
3. Determine new next step
4. Add to session log
5. Save context

Output:
```
✅ Step completed: "Implement component"
🔄 Now on: "Style with tokens"
⏳ Next: "Self code review"

Context saved.
```

### Set Current Step

```
/context-update step "Apply responsive styles"
```

Output:
```
🔄 Current step set to: "Apply responsive styles"
Context saved.
```

### Switch Task

```
/context-update task PROJ-125
```

Triggers:
1. Mark current task as done (if not already)
2. Shift task progression
3. Load new task details from Jira (if connected)
4. Reset steps
5. Log transition

Output:
```
✅ Completed: PROJ-124
🔄 Now on: PROJ-125 "Create Card molecule"
⏳ Next: PROJ-126

Context saved.
```

### Add Note

```
/context-update note "Hit a blocker with CSS grid, need to research"
```

Output:
```
📝 Note added to current step.

Current: Implement component (50%)
Note: "Hit a blocker with CSS grid, need to research"

Context saved.
```

### Update Progress

```
/context-update progress 75%
```

Output:
```
📊 Progress updated: 50% → 75%

Current: Implement component (75%)

Context saved.
```

---

## Auto-Detection

Claude should also update context automatically when:
- User says "done with this step"
- User says "let's move to the next step"
- User says "task complete"
- User starts working on something that implies step change
- Significant work is completed

Claude says:
```
📝 Context auto-updated:
   Step "Implement component" marked DONE
   Now on: "Style with tokens"
```
