# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security issue, please report it responsibly.

### How to Report

1. **DO NOT** create a public GitHub issue for security vulnerabilities
2. Email security concerns to the repository maintainers directly
3. Include the following in your report:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

### What to Expect

- **Acknowledgment**: Within 48 hours of your report
- **Initial Assessment**: Within 5 business days
- **Resolution Timeline**: Depends on severity
  - Critical: 24-72 hours
  - High: 1-2 weeks
  - Medium: 2-4 weeks
  - Low: Next release cycle

### Responsible Disclosure

We kindly ask that you:
- Give us reasonable time to fix the issue before public disclosure
- Do not access or modify other users' data
- Do not perform actions that could harm the service or other users

## Security Best Practices for Contributors

### Secrets Management

**NEVER commit secrets to the repository:**

```bash
# Bad - hardcoded secrets
ATLASSIAN_API_TOKEN="actual_token_here"

# Good - use environment variables
ATLASSIAN_API_TOKEN="${ATLASSIAN_API_TOKEN}"
```

**Files that should NEVER contain real credentials:**
- `.mcp.json` - Use `.mcp.json.example` as template
- `.env` - Use `.env.example` as template
- Any configuration file in version control

### Pre-commit Hooks

This repository uses pre-commit hooks to prevent accidental secret commits:

```bash
# Install pre-commit hooks
pip install pre-commit
pre-commit install

# Run manually
pre-commit run --all-files
```

### Security Checklist for PRs

Before submitting a PR, verify:

- [ ] No hardcoded credentials, API keys, or tokens
- [ ] No private keys or certificates
- [ ] No internal URLs or IP addresses
- [ ] No personally identifiable information (PII)
- [ ] Dependencies are from trusted sources
- [ ] No `eval()`, `exec()`, or similar dangerous functions
- [ ] Input validation on all user inputs
- [ ] Proper error handling (no stack traces in production)

## Known Security Considerations

### MCP Configuration

The `.mcp.json` file configures external service integrations. This file:
- Is listed in `.gitignore` to prevent accidental commits
- Should be created locally from `.mcp.json.example`
- Contains API tokens that grant access to:
  - Atlassian Jira/Confluence
  - Figma
  - GitHub
  - Local filesystem

**If you accidentally commit credentials:**
1. Immediately rotate all exposed tokens
2. Remove the file from git history using BFG Repo-Cleaner or `git filter-branch`
3. Force push to all branches
4. Check for any unauthorized access using the exposed tokens

### Data Storage

The AID system stores data locally in `~/.aid/`:
- `state.json` - Session state
- `feedback/` - User feedback data
- `memory/` - Claude Memory sync data

This data may contain:
- Project names and descriptions
- User interactions and feedback
- Learning patterns

**Recommendation**: Ensure `~/.aid/` is backed up securely and not shared publicly.

## Security Updates

Security patches are released as soon as possible after a vulnerability is confirmed. To stay updated:

1. Watch this repository for releases
2. Enable GitHub security alerts
3. Run `npm audit` and `pip-audit` regularly

## Contact

For security-related questions, contact the repository maintainers.
