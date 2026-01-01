# GitHub MCP Integration

Connect Claude Code to GitHub for repository management and code operations.

## Prerequisites

- GitHub account
- Personal Access Token (PAT) with appropriate scopes
- Node.js 18+

## Creating a GitHub Token

1. Go to [GitHub Settings → Developer Settings → Personal Access Tokens](https://github.com/settings/tokens)
2. Click "Generate new token (classic)"
3. Select scopes:
   - `repo` - Full control of private repositories
   - `workflow` - Update GitHub Action workflows
   - `read:org` - Read org membership (if needed)
4. Generate and copy token

## Configuration

### 1. Environment Variables

Add to your `.env` file:

```bash
GITHUB_PERSONAL_ACCESS_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx
```

### 2. MCP Configuration

Add to your `.mcp.json`:

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_PERSONAL_ACCESS_TOKEN}"
      }
    }
  }
}
```

## Installation

The MCP server is installed automatically via npx when Claude Code connects.

Manual test:
```bash
npx -y @modelcontextprotocol/server-github
```

## Available Tools

| Tool | Description |
|------|-------------|
| `get_file_contents` | Read file from repository |
| `search_code` | Search code across repos |
| `search_repositories` | Find repositories |
| `create_repository` | Create new repository |
| `create_pull_request` | Create PR |
| `create_issue` | Create GitHub issue |
| `list_issues` | List repository issues |
| `create_branch` | Create new branch |
| `push_files` | Push file changes |
| `fork_repository` | Fork a repository |

## Usage Examples

### Search Code

```
"Find all TypeScript files in my-org that import React"
```

### Create Pull Request

```
"Create a PR from feature/auth to main with title 'Add user authentication' and description explaining the changes"
```

### Read Repository Structure

```
"Show me the directory structure of my-org/my-repo"
```

### Create Issue from Bug

```
"Create a GitHub issue for the login bug we discussed, assign it to me, and add the 'bug' label"
```

## Search Syntax

```
# Search code
language:typescript "import React"
repo:my-org/my-repo path:src extension:ts

# Search repositories
org:my-org language:typescript stars:>10

# Search issues
repo:my-org/my-repo is:issue is:open label:bug
```

## Branch Naming Conventions

```
feature/[ticket-id]-short-description
bugfix/[ticket-id]-short-description
hotfix/critical-fix-description
release/v1.2.3
```

## PR Template

When creating PRs, Claude will use this structure:

```markdown
## Description
[Brief description of changes]

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No new warnings
```

## Workflow Integration

### Create Feature Branch → Implement → PR

```
1. "Create a branch called feature/JIRA-123-user-auth"
2. [Implement changes]
3. "Create a PR with the authentication changes, linking to JIRA-123"
```

### Review and Merge

```
"Review the open PRs in my-repo and summarize the changes"
```

## Troubleshooting

### Authentication Failed
- Verify GITHUB_TOKEN is set correctly
- Check token hasn't expired
- Ensure token has required scopes

### Repository Not Found
- Verify repository name and owner
- Check you have access to private repos
- Token needs `repo` scope for private repos

### Rate Limited
- GitHub API: 5,000 requests/hour with token
- Search API: 30 requests/minute
- Wait or use authenticated requests
