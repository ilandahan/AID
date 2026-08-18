# Context Isolation Rules

## Why Isolation Matters

The reflection agent exists because **inline self-reflection is biased**. When Claude evaluates its own work with full conversation context, it naturally:
- Agrees with its own reasoning
- Justifies its decisions
- Gives high scores (trending to 10/10)

**True quality assessment requires isolation** - evaluating output without access to the reasoning that produced it.

## The Isolation Principle

```
┌─────────────────────────────────────────────────────────────┐
│  MAIN AGENT (Has full context)                              │
│  ├── Conversation history                                   │
│  ├── User interactions                                      │
│  ├── Reasoning and decisions                                │
│  ├── Previous attempts                                      │
│  └── Justifications                                         │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      │  PASSES ONLY:
                      │  • Original request (verbatim)
                      │  • Stated WHY
                      │  • Output to evaluate
                      │  • Source files
                      │  • Phase criteria
                      ▼
┌─────────────────────────────────────────────────────────────┐
│  REFLECTION AGENT (Isolated)                                │
│  ├── ✅ Original request                                    │
│  ├── ✅ Stated WHY                                          │
│  ├── ✅ Output to evaluate                                  │
│  ├── ✅ Source files for verification                       │
│  ├── ✅ Phase criteria                                      │
│  ├── ❌ NO conversation history                             │
│  ├── ❌ NO reasoning/justifications                         │
│  └── ❌ NO knowledge of previous attempts                   │
└─────────────────────────────────────────────────────────────┘
```

## Enforcement Rules

### MUST DO

1. **Extract original request verbatim**
   - Find the first user message that initiated the task
   - Copy it exactly - do not summarize
   - Include all details, even if they seem minor

2. **Capture stated WHY exactly**
   - From WHY analysis phase
   - The actual text, not a paraphrase
   - If no WHY was established, note that as a finding

3. **Include all relevant source files**
   - Files that the output references or modifies
   - Files needed to verify claims
   - Do not cherry-pick - include all touched files

4. **Load phase criteria from file**
   - Use `criteria/phase-{N}-{name}.yaml`
   - Pass the full YAML content

### MUST NOT DO

1. **❌ Summarize the request**
   - "User wanted a login form" loses detail
   - Pass: "Add user authentication with email/password, include password reset flow"

2. **❌ Explain decisions**
   - "We chose bcrypt because..." is context leak
   - Just pass the output - agent will verify bcrypt is there

3. **❌ Include conversation history**
   - Even "helpful" context biases the review
   - If context is needed, it should be in the output itself

4. **❌ Pre-filter files**
   - Don't decide which files are "relevant"
   - Include all modified files, let agent determine relevance

5. **❌ Mention previous attempts**
   - "This is revision 2 because..." biases toward leniency
   - Each evaluation is independent

## Variable Extraction Guide

### {{ORIGINAL_REQUEST}}

```python
# Find first task-initiating user message
for message in conversation:
    if message.role == "user" and is_task_request(message):
        return message.content  # Verbatim, full text
```

**Example:**
```
Good: "I need to add a user profile page that shows the user's name, email,
      avatar, and a list of their recent orders. It should load data from
      the existing /api/user endpoint."

Bad:  "Add user profile page"  (summarized - loses detail)
```

### {{STATED_WHY}}

```python
# Find WHY analysis from conversation
why_pattern = r"WHY:?\s*(.+?)(?=\n\n|WHAT:|$)"
# or look for "The purpose is..." "This is needed because..."
```

**Example:**
```
Good: "Users need to verify their account information and track order history
      without contacting support. This reduces support tickets and increases
      user self-service."

Bad:  "User wants profile page"  (restates WHAT, not WHY)
```

### {{FILES_TO_VERIFY}}

```python
# Include content of all files that:
# 1. Output claims to modify
# 2. Output references
# 3. Are in the same module/component

files = []
for file_path in get_modified_files(output):
    files.append({
        "path": file_path,
        "content": read_file(file_path)
    })
```

**Format:**
```
--- File: src/components/UserProfile.tsx ---
[full file content]

--- File: src/api/user.ts ---
[full file content]
```

## Bias Detection

Signs the main agent is leaking context:

| Signal | Problem | Fix |
|--------|---------|-----|
| "We decided to..." | Includes reasoning | Remove, just show output |
| "Based on earlier discussion..." | References history | Remove reference |
| "The user clarified that..." | Additional context | Include in original request if critical |
| "This is attempt 3..." | Reveals iteration | Remove, evaluate fresh |
| "I used X because Y..." | Justification | Let agent discover X, ignore Y |

## Testing Isolation

To verify isolation is working:

1. **Same output, different context**: Run evaluation on same output with different (fake) original requests. Scores should differ based on request alignment.

2. **Check for context references**: Agent response should never mention things only in conversation history.

3. **Score distribution**: If scores are consistently 9-10, isolation may be broken.
