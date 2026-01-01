# Core Concepts

AID is built upon three foundational pillars that ensure consistency, context awareness, and continuous improvement.

## 1. Phase Gate System

The Phase Gate System is the primary mechanism for quality control. It divides the software development lifecycle into 6 distinct phases, requiring specific criteria to be met before moving to the next.

### The 6 Phases

| Phase | Name | Focus | Output |
|-------|------|-------|--------|
| **0** | **Discovery** | Research & Feasibility | `docs/research/` |
| **1** | **PRD** | Requirements & Scope | `docs/PRD.md` |
| **2** | **Tech Spec** | Architecture & Design | `docs/TECH-SPEC.md` |
| **3** | **Breakdown** | Task Planning | Jira Epics / `docs/BREAKDOWN.md` |
| **4** | **Development** | Implementation | Source Code, Tests |
| **5** | **QA & Ship** | Validation | Release |

### Rules of the Road
-   **No Skipping**: You cannot start Development (Phase 4) without an approved Tech Spec (Phase 2).
-   **Blocked Actions**: Using `write_to_file` on source code is **technically blocked** by the `phase-enforcement` skill if you are in Phase 1 or 2.
-   **Gate Checks**: Before advancing, run `/gate-check` to verify you have met all "Exit Criteria".

## 2. Context Tracking

One of the biggest challenges in AI-assisted coding is "amnesia"—the AI forgetting what it was doing between sessions. AID solves this with the **Context Tracking System**.

### How It Works
AID maintains a file at `.aid/context.json` that acts as a persistent memory of your current progress.

```json
{
  "tasks": {
    "current": { "key": "PROJ-124", "title": "Create FormField", "status": "in_progress" }
  },
  "current_task_steps": {
    "current": { "name": "Implement component", "progress": "50%" }
  }
}
```

### Context Persistence
-   **Automatic Updates**: When you complete a step or task, Claude updates this file.
-   **Session Restoration**: When you start a new session (`/good-morning`), Claude reads this file to instantly restore context.
-   **Granularity**: Tracks work at both the **Task** level (high level) and **Step** level (granular actions).

## 3. Memory & Learning System

AID gets smarter the more you use it. The Memory System collects feedback and optimizes the AI's instructions (skills) over time.

### The Learning Loop
1.  **Work Session**: You collaborate with Claude on a task.
2.  **Feedback**: At the end (`/aid-end`), you rate the session (1-5) and provide comments.
3.  **Analysis**: The `/aid-improve` command (ran weekly) analyzes all feedback.
4.  **Optimization**: The system updates the prompts in the `skills/` directory and promotes high-value insights to Claude's persistent memory.

### Storage
-   **Local Feedback**: Stored in `~/.aid/feedback/`.
-   **Learned Skills**: Optimizations are applied to your local `skills/` folder.
-   **Claude Memory**: Key insights are stored in Claude's long-term memory slots (if supported).
