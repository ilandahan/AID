# Technical Architecture

This document outlines the internal architecture of the AID system itself. It is intended for developers who want to understand how AID works "under the hood" or contribute to the framework.

## System Components

### 1. The Core (Claude Code Shim)
AID operates as a set of configuration files and scripts that wrap the standard Claude Code experience.
-   **`CLAUDE.md`**: The "Kernel". This file is loaded by Claude at the start of every session and defines the rules of engagement (Phase Gates).
-   **`.aid/`**: The "State Store". JSON files that track the project's persistent state.

### 2. MCP Server (`server/`)
AID includes a custom MCP server (built with Express.js) specifically for Deep Integrations (like the Figma Plugin).

**Key Modules:**
-   **entry (`index.ts`)**: Handles JSON-RPC 2.0 requests.
-   **auth (`jwt-middleware.ts`)**: Secures communications between the Figma Plugin and the CLI.
-   **tools (`design-review.ts`)**: Implements the logic for checking design deviations.
-   **relay (`relay/`)**: Manages the message queue between the external plugin and the local CLI.

### 3. The Scripts Layer (`scripts/`)
Automates routine tasks to keep the developer experience smooth.

-   **`init-project.sh`**: Scaffolds new projects with the correct directory structure (`src/`, `docs/`, `.aid/`).
-   **`startup-check.sh`**: Verifies prerequisites (Docker, Node, Python) during the `/good-morning` routine.
-   **`generate-keys.js`**: Creating security keys for the JWT auth system.

### 4. Memory System (`memory-system/`)
A Python-based subsystem that runs analysis on feedback.

-   **`subagent.py`**: The logic engine that clusters user feedback and generates prompt optimizations.
-   **`feedback/`**: Local storage for user ratings and comments.

## Data Flow

```
User Command (/aid-start) 
       v
Claude CLI reads CLAUDE.md
       v
Checks .aid/state.json (Is this phase allowed?)
       v
Loads Skills from .claude/skills/ (Symlinked)
       v
Connects to MCP Servers (.mcp.json)
       v
Ready for Work
```

## Security

-   **Local First**: All state and feedback are stored locally in the project or `~/.aid/`.
-   **Auth**: The custom MCP server uses JWT to ensure only authorized plugins can interact with your local development environment.
