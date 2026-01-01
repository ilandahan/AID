# MCP Server Configuration Guide

This guide explains how to configure MCP (Model Context Protocol) servers for the AI Full Stack Development methodology.

## Overview

MCP servers enable Claude Code to interact with external services like Jira, GitHub, databases, and more.

**Configuration file:** `.mcp.json` (in project root)

## Configuration Format

```json
{
  "$schema": "https://raw.githubusercontent.com/anthropics/anthropic-quickstarts/main/mcp-config-schema.json",
  "mcpServers": {
    "server-name": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-name"],
      "env": {
        "ENV_VAR": "${ENV_VAR}"
      }
    }
  }
}
```

## Available MCP Servers

### Atlassian (Jira/Confluence)

```json
{
  "jira": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-atlassian"],
    "env": {
      "ATLASSIAN_SITE_URL": "${ATLASSIAN_SITE_URL}",
      "ATLASSIAN_USER_EMAIL": "${ATLASSIAN_USER_EMAIL}",
      "ATLASSIAN_API_TOKEN": "${ATLASSIAN_API_TOKEN}"
    }
  }
}
```

**Environment variables:**
- `ATLASSIAN_SITE_URL` - Your Atlassian URL (e.g., `https://your-domain.atlassian.net`)
- `ATLASSIAN_USER_EMAIL` - Your Atlassian account email
- `ATLASSIAN_API_TOKEN` - [Create API token](https://id.atlassian.com/manage-profile/security/api-tokens)

### GitHub

```json
{
  "github": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-github"],
    "env": {
      "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_PERSONAL_ACCESS_TOKEN}"
    }
  }
}
```

**Environment variables:**
- `GITHUB_PERSONAL_ACCESS_TOKEN` - [Create PAT](https://github.com/settings/tokens) with `repo`, `workflow`, `read:org` scopes

### PostgreSQL

```json
{
  "postgres": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-postgres"],
    "env": {
      "POSTGRES_CONNECTION_STRING": "${POSTGRES_CONNECTION_STRING}"
    }
  }
}
```

**Environment variables:**
- `POSTGRES_CONNECTION_STRING` - Connection string (e.g., `postgresql://user:pass@localhost:5432/db`)

### Filesystem

```json
{
  "filesystem": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-filesystem", "."]
  }
}
```

No environment variables needed. The last argument specifies the root directory.

### Figma

Figma uses a **local MCP server** that runs from Figma Desktop. No `.mcp.json` configuration needed.

**Setup:**
1. Open Figma Desktop
2. Toggle Dev Mode (Shift+D)
3. Enable desktop MCP server in inspect panel
4. Server runs at `http://127.0.0.1:3845/mcp`

### Chrome DevTools

Browser automation, debugging, and performance analysis.

```json
{
  "chrome-devtools": {
    "command": "npx",
    "args": ["-y", "chrome-devtools-mcp@latest"]
  }
}
```

**Dependencies:**

| Package | Type | Purpose |
|---------|------|---------|
| `chrome-devtools-mcp@latest` | MCP Server | Browser automation via Claude |
| `puppeteer` | Dev dependency | Browser automation engine |
| `chromium` | Binary (auto) | Headless browser (~170MB) |

```bash
# Install puppeteer (includes Chromium)
npm install --save-dev puppeteer

# Or from the methodology repo
npm install
```

**Capabilities:**
- Navigate and take screenshots
- Monitor console logs and network requests
- Execute JavaScript in browser context
- Record performance traces
- Automate form filling and clicks

**Optional: Connect to existing Chrome instance:**
```json
{
  "chrome-devtools": {
    "command": "npx",
    "args": ["-y", "chrome-devtools-mcp@latest", "--browser-url=http://127.0.0.1:9222"]
  }
}
```

Launch Chrome with: `chrome --remote-debugging-port=9222`

**Usage in phases:**
- **Phase 5 (Development)**: Live UI verification
- **Phase 6 (Testing)**: E2E screenshots, visual regression
- **Phase 7 (Review)**: Performance audits, Core Web Vitals

**Test Recordings:** All screenshots, videos, and traces are saved to `test-recordings/`:
```
test-recordings/
├── screenshots/   # .png, .jpg files
├── videos/        # .webm, .mp4 recordings
├── traces/        # Performance .json files
└── reports/       # Generated .html reports
```

Cleanup commands:
```bash
npm run clean:recordings      # Delete files older than 7 days
npm run clean:recordings:all  # Delete all recordings
make clean-recordings         # Same via Makefile
```

## Environment Variables

Store sensitive values in `.env`:

```bash
# .env (DO NOT COMMIT)
ATLASSIAN_SITE_URL=https://your-domain.atlassian.net
ATLASSIAN_USER_EMAIL=your-email@company.com
ATLASSIAN_API_TOKEN=your-token

GITHUB_PERSONAL_ACCESS_TOKEN=ghp_xxxxxxxxxxxx

POSTGRES_CONNECTION_STRING=postgresql://user:pass@localhost:5432/mydb
```

Add `.env` to `.gitignore`:
```
.env
.env.local
.env.*.local
```

## Complete Example

`.mcp.json`:
```json
{
  "$schema": "https://raw.githubusercontent.com/anthropics/anthropic-quickstarts/main/mcp-config-schema.json",
  "mcpServers": {
    "jira": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-atlassian"],
      "env": {
        "ATLASSIAN_SITE_URL": "${ATLASSIAN_SITE_URL}",
        "ATLASSIAN_USER_EMAIL": "${ATLASSIAN_USER_EMAIL}",
        "ATLASSIAN_API_TOKEN": "${ATLASSIAN_API_TOKEN}"
      }
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_PERSONAL_ACCESS_TOKEN}"
      }
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "."]
    },
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres"],
      "env": {
        "POSTGRES_CONNECTION_STRING": "${POSTGRES_CONNECTION_STRING}"
      }
    },
    "chrome-devtools": {
      "command": "npx",
      "args": ["-y", "chrome-devtools-mcp@latest"]
    }
  }
}
```

## Troubleshooting

### Server Not Connecting

1. Check environment variables are set in `.env`
2. Verify the server package exists: `npx -y @modelcontextprotocol/server-github --help`
3. Check network connectivity

### Authentication Errors

- **Jira**: Verify API token hasn't expired
- **GitHub**: Check PAT has required scopes
- **Postgres**: Verify connection string and database access

### Server Not Found

```bash
# Pre-install servers for faster startup
npx -y @modelcontextprotocol/server-atlassian --help
npx -y @modelcontextprotocol/server-github --help
npx -y @modelcontextprotocol/server-postgres --help
npx -y chrome-devtools-mcp@latest --help
```

### Chrome DevTools Issues

- **Chrome not found**: Install Google Chrome or specify path with `--executable-path`
- **Sandbox errors**: Use `--no-sandbox` flag in Docker/CI environments
- **Connection refused**: Launch Chrome manually with `--remote-debugging-port=9222`

## Migration from Old Format

If you have MCP config in `.claude/settings.json`, move the `mcpServers` section to `.mcp.json`:

**Old (`.claude/settings.json`):**
```json
{
  "mcpServers": { ... },
  "skills": [ ... ]
}
```

**New:**
- `.mcp.json` - MCP server configuration
- `.claude/settings.json` - Claude-specific settings (skills, hooks, preferences)
