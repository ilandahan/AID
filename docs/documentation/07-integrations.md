# Integrations

AID uses the **Model Context Protocol (MCP)** to connect Claude to your external tools. This integration allows the AI to read tickets, check code, and verify designs directly without you copy-pasting information.

## Overview

All integrations are defined in the `.mcp.json` file in the root of your project.

```json
{
  "mcpServers": {
    "jira": { ... },
    "github": { ... },
    "figma": { ... },
    "chrome-devtools": { ... }
  }
}
```

## Supported Tools

### 1. Jira (Atlassian)
**Purpose:** Project management and task tracking.
-   **Capabilities:** Create tickets, update status, read acceptance criteria.
-   **Setup:** Requires `ATLASSIAN_API_TOKEN` and `ATLASSIAN_SITE_URL`.
-   **Key Workflow:** The `jira-breakdown` skill uses this to convert Tech Specs into Jira Epics.

### 2. GitHub
**Purpose:** Version control and code review.
-   **Capabilities:** Read PRs, comment on code, search repository history.
-   **Setup:** Requires `GITHUB_PERSONAL_ACCESS_TOKEN`.
-   **Key Workflow:** The `code-review` skill uses this to analyze Pull Requests.

### 3. Figma
**Purpose:** Design Source of Truth.
-   **Capabilities:** Read component metadata, extract API tokens (colors, spacing).
-   **Setup:** Requires `FIGMA_API_KEY`.
-   **Key Workflow:** The `atomic-design` skill uses this to validate that your React components match the Figma design exactly.

### 4. Chrome DevTools
**Purpose:** End-to-End Testing and Validation.
-   **Capabilities:** Control browser, take screenshots, read console logs.
-   **Setup:** Requires running Chrome with `--remote-debugging-port=9222`.
-   **Key Workflow:** The `qa-ship` skill uses this to visually verify that the app is running correctly before release.

## Configuration

To enable an integration:
1.  Ensure the server is listed in `.mcp.json`.
2.  Add the required keys to your `.env` file.
3.  Restart Claude Code to load the new context.

## Troubleshooting

-   **Connection Failed**: Run `/good-morning` to check status.
-   **Auth Errors**: Verify your API tokens are valid and have the correct scopes (e.g., Jira needs 'write' access).
