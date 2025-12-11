# /good-morning

Morning startup routine - verify all systems, load context, and continue from where you left off.

## What It Does

1. Check Docker status
2. Start/verify MCPs (Figma, Jira, etc.)
3. Load project phase state
4. Load work context (tasks + steps)
5. Show where you left off
6. Ask what to continue

---

## Step 1: Infrastructure Check

```
═══════════════════════════════════════════════════════
           GOOD MORNING - AID STARTUP
═══════════════════════════════════════════════════════

DOCKER
   Status: Running
   Containers: postgres_dev, redis_dev

MCP CONNECTIONS
   Figma:     Connected (Dev Mode MCP)
   Jira:      Connected (project: PROJ)
   GitHub:    Connected

```

---

## Step 2: Project State

```
═══════════════════════════════════════════════════════

PROJECT STATE
   Phase: [4] DEVELOPMENT
   Sprint Progress: 12/45 tasks (27%)

```

---

## Step 3: Work Context (THE KEY PART)

Read `.aid/context.json` and display:

```
═══════════════════════════════════════════════════════

WHERE YOU LEFT OFF
───────────────────────────────────────────────────────

TASKS:
  Previous: PROJ-123 "Create Button atom"
  Current:  PROJ-124 "Create FormField molecule"
  Next:     PROJ-125 "Create Card molecule"

CURRENT TASK - PROJ-124:
  Write tests ────────────── DONE
  Implement component ────── 50%
     "Label and input done, error handling next"
  Style with tokens
  Self code review
  Update Jira & commit

Last activity: 2025-12-09 17:35 (yesterday, 16 hours ago)

═══════════════════════════════════════════════════════
```

---

## Step 4: Continue Prompt

```
═══════════════════════════════════════════════════════

What would you like to do?

  [1] Continue PROJ-124 step "Implement component"
      (Continuing from 50%, error handling)

  [2] Finished this step, move to next step

  [3] Finished PROJ-124, move to PROJ-125

  [4] Different task from sprint

  [5] Update - I did something offline

>
═══════════════════════════════════════════════════════
```

---

## Response Handling

### User says "1" (continue current step)
```
Claude:
  Great, continuing with PROJ-124.

  Resume point: Implement component (50%)
  Last note: "Label and input done, error handling next"

  Let's start with error handling. What approach did you plan?
```

### User says "2" (step done, next step)
```
Claude:
  Updating: "Implement component" → DONE
  Now: "Style with tokens"

  [Updates .aid/context.json]

  Let's start with styling. Do we have the tokens from Figma?
```

### User says "3" (task done, next task)
```
Claude:
  Updating: PROJ-124 → DONE
  Now: PROJ-125 "Create Card molecule"

  [Updates .aid/context.json - shifts all tasks and resets steps]

  Loading context for PROJ-125...
  [Fetches from Jira if connected]

  Ready to start?
```

### User says "5" (offline update)
```
Claude:
  What did you do since last time?

  (Describe what you completed, and I'll update the context)
```

---

## Complete Output Example

```
═══════════════════════════════════════════════════════
           GOOD MORNING - AID STARTUP
═══════════════════════════════════════════════════════

DOCKER: Running (2 containers)
MCPs:   Figma | Jira | GitHub

═══════════════════════════════════════════════════════

PROJECT: Time Tracking System
   Phase: [4] DEVELOPMENT
   Sprint: 12/45 (27%)

═══════════════════════════════════════════════════════

WHERE YOU LEFT OFF

TASKS:
  PROJ-123 "Button atom" - DONE
  PROJ-124 "FormField molecule" - IN PROGRESS
  PROJ-125 "Card molecule" - PENDING

CURRENT TASK STEPS:
  Write tests - DONE
  Implement component (50%)
     "Label and input done, error handling next"
  Style with tokens - PENDING
  Code review - PENDING
  Commit - PENDING

Last: 2025-12-09 17:35 (16 hours ago)

═══════════════════════════════════════════════════════

What would you like to do?
  [1] Continue current step (Implement - 50%)
  [2] Finished step, next
  [3] Finished task, next
  [4] Different task
  [5] Offline update

>
═══════════════════════════════════════════════════════
```

---

## If No Context Exists

```
═══════════════════════════════════════════════════════

No work context found (.aid/context.json)

Let's set it up:
  What Jira task are you currently working on?
  (Enter task key like PROJ-123, or "none" to skip)

> PROJ-124

Great! What step are you on?
  [1] Just starting - loading context
  [2] Writing tests
  [3] Implementing
  [4] Styling
  [5] Code review
  [6] Other (describe)

> 3

Setting up context...
Context created for PROJ-124, step: Implementing

═══════════════════════════════════════════════════════
```
