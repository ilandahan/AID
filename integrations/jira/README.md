# Jira MCP Integration

Connect Claude Code to Jira for project management automation.

## Prerequisites

- Jira Cloud account
- API token from [Atlassian API tokens](https://id.atlassian.com/manage-profile/security/api-tokens)
- Node.js 18+

## Configuration

### 1. Environment Variables

Add to your `.env` file:

```bash
ATLASSIAN_SITE_URL=https://your-domain.atlassian.net
ATLASSIAN_USER_EMAIL=your-email@company.com
ATLASSIAN_API_TOKEN=your-api-token
```

### 2. MCP Configuration

Add to your `.mcp.json`:

```json
{
  "mcpServers": {
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
}
```

## Installation

The MCP server is installed automatically via npx when Claude Code connects.

Manual test:
```bash
npx -y @modelcontextprotocol/server-atlassian
```

## Available Tools

| Tool | Description |
|------|-------------|
| `create_issue` | Create new Jira issue |
| `search_issues` | Search with JQL |
| `update_issue` | Update existing issue |
| `get_issue` | Get issue details |
| `get_project` | Get project info |
| `list_projects` | List all projects |
| `add_comment` | Add comment to issue |
| `transition_issue` | Change issue status |

## Usage Examples

### Create Epic

```
"Create an epic in PROJECT called 'User Authentication System' with description covering login, registration, and password reset"
```

### Search Issues

```
"Find all open bugs in PROJECT assigned to me"
```

### Create Story with Subtasks

```
"Create a story for login functionality with subtasks for:
- UI component
- API endpoint
- Integration tests
- Documentation"
```

### Generate Sprint Plan

```
"Based on the tech spec, create a complete Jira breakdown with:
- 1 Epic
- 5-7 Stories
- Subtasks for each story
- Time estimates"
```

## JQL Quick Reference

```sql
-- Open issues in project
project = PROJECT AND status != Done

-- My assigned issues
assignee = currentUser() AND status != Done

-- Sprint backlog
project = PROJECT AND sprint in openSprints()

-- Recently updated
project = PROJECT AND updated >= -7d

-- High priority bugs
project = PROJECT AND type = Bug AND priority = High
```

## Issue Type Hierarchy

```
Epic (large feature)
└── Story (user-facing functionality)
    └── Task (technical work)
        └── Sub-task (small piece of work)
```

## Time Estimation Guidelines

| Story Points | Time | Use For |
|-------------|------|---------|
| 1 | 2-4 hours | Simple changes |
| 2 | 0.5-1 day | Small features |
| 3 | 1-2 days | Medium features |
| 5 | 3-5 days | Complex features |
| 8 | 1 week+ | Major features |
| 13 | 2 weeks+ | Epic-sized (split it) |

## Troubleshooting

### Connection Failed
- Verify environment variables are set
- Check API token hasn't expired
- Ensure Jira URL is correct (include https://)

### Permission Denied
- Verify account has project access
- Check API token scopes

### Rate Limited
- Wait 60 seconds between bulk operations
- Use search instead of individual gets
