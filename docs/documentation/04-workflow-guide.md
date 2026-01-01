# Workflow Guide

This guide details the standard daily workflows for using AID.

## The Morning Startup

Start every workday with the **Morning Startup** routine. This single command prepares your environment and restores your context.

**Command:**
```bash
/good-morning
```

**What it does:**
1.  **System Check**: Verifies Docker containers are running and MCP servers (Jira, Figma) are connected.
2.  **Context Restore**: Reads `.aid/context.json` to remind you of your last active task.
3.  **Action Plan**: Asks you if you want to continue the current task or start a new one.

## standard Development Cycle

A typical task follows this flow:

### 1. Start Work
Establish what you are doing. If starting a new phase or role:
```bash
/aid-start
# Select Role (e.g., Developer) and Phase (e.g., Phase 4)
```

### 2. Check Context
If continuing from before, check where you are:
```bash
/context
```

### 3. Execute (Rules by Phase)
-   **Phase 1 (PRD)**: Focus on `docs/PRD.md`. Use the `/prd` command.
-   **Phase 2 (Tech Spec)**: Focus on `docs/TECH-SPEC.md`. Use `/tech-spec`.
-   **Phase 4 (Dev)**:
    -   **TDD First**: Write tests (`.test.ts` / `.spec.ts`) before code.
    -   **Implement**: Write the source code (`src/`).
    -   **Verify**: Run tests (`npm test`).

### 4. End & Review
When you finish a major chunk of work or a phase:
```bash
/gate-check       # Verify you met all criteria
/phase-approve    # Human approval (typing "Approved")
/phase-advance    # Move system pointer to next phase
```

### 5. Close Session
When taking a break or finishing for the day:
```bash
/aid-end
# Provide 1-5 rating and brief feedback on what went well/poorly.
```

## Command Reference

| Category | Command | Description |
|----------|---------|-------------|
| **Startup** | `/good-morning` | System check and context restore |
| | `/aid-init` | Initialize a new project |
| **Flow** | `/aid-start` | Begin session with specific Role/Phase |
| | `/aid-end` | End session and log feedback |
| **Phase** | `/phase` | Show current phase status |
| | `/gate-check` | Verify phase exit criteria |
| | `/phase-advance` | Move to next phase |
| **Context** | `/context` | Show current task/step |
| | `/context-update` | Manually update progress |
| **Tools** | `/prd` | Generate Product Requirements |
| | `/tech-spec` | Generate Technical Spec |
| | `/code-review` | Run AI code review |
| | `/qa-ship` | Run QA validation suite |

## Troubleshooting

-   **"Blocked" Message**: You are trying to act outside your current phase. Run `/phase-advance` if you are ready to move on.
-   **Context Lost**: Run `/context-update` to manually set your current task status.
-   **MCP Errors**: Run `/good-morning` again to trigger the connection checks.
