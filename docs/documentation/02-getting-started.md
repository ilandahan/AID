# Getting Started with AID

This guide covers the installation and setup of the AID framework for your development environment.

## Prerequisites

Before installing AID, ensure you have the following tools installed:

- **Node.js** (v18 or higher) - For package management and running scripts.
- **Python** (v3.11 or higher) - For the memory system and analysis tools.
- **Docker & Docker Compose** - For running local databases and services (optional but recommended).
- **Claude Code** - The command-line interface for Anthropic's Claude.

## Installation

### Quick Install (Mac/Linux)

1. Clone the repository:
   ```bash
   git clone https://github.com/ilandahan/AID.git
   cd AID
   ```

2. Run the installation script:
   ```bash
   ./install.sh
   ```

### Quick Install (Windows)

1. Clone the repository:
   ```bash
   git clone https://github.com/ilandahan/AID.git
   cd AID
   ```

2. Run the installation batch file:
   ```cmd
   install.bat
   ```

### Manual Installation

If you prefer to install manually:

1.  **Install Dependencies**: `npm install`
2.  **Environment Setup**: Copy `.env.example` to `.env` and configure your keys.
3.  **Claude Setup**: Create `.claude` directory and copy contents from `skills/` and `commands/` as per the repository structure.

## Setting Up Your First Project

AID supports two modes: creating a new project from scratch or linking to an existing one.

### Option 1: Create a New Project

Use the built-in script to initialize a new project with the AID structure pre-configured.

```bash
# General usage
./scripts/init-project.sh <project-name>

# Example
./scripts/init-project.sh my-new-app
```

This will:
- Create a directory `my-new-app`.
- Initialize a Next.js / TypeScript template (default).
- Set up the `.aid` folder for phase tracking.
- Link the AID skills and commands to your new project.

### Option 2: Link an Existing Project

If you have an existing repository, you can "enable" AID on it by creating symbolic links.

**Mac/Linux:**
```bash
cd your-existing-project
/path/to/AID/scripts/link-project.sh
```

**Windows:**
```powershell
# From your project directory
New-Item -ItemType SymbolicLink -Path ".claude" -Target "..\AID\.claude"
New-Item -ItemType SymbolicLink -Path "CLAUDE.md" -Target "..\AID\CLAUDE.md"
```
*(Note: Adjust paths accordingly)*

## Integrations Setup (MCP)

AID uses the **Model Context Protocol (MCP)** to connect to external tools. Configuration is handled in `.mcp.json`.

1.  **Edit Configuration**: Open `.mcp.json` in your project root.
2.  **Add API Keys**: Update your `.env` file with necessary keys:
    - `ATLASSIAN_API_TOKEN` (Jira/Confluence)
    - `GITHUB_PERSONAL_ACCESS_TOKEN`
    - `FIGMA_API_KEY`

Refer to the [Integrations Guide](./07-integrations.md) for detailed setup instructions for each tool.

## Morning Routine

Once installed, your daily workflow begins with a single command:

```bash
/good-morning
```

This command will:
1.  Check the health of your environment (Docker, MCPs).
2.  Load the project context from `.aid/context.json`.
3.  Remind you of your last active task.
4.  Ask you what you want to achieve today.
