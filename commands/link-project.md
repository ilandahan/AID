---
description: "Link an existing project to AID so it shares one source of truth"
disable-model-invocation: true
---

# /link-project

Link an external project to AID methodology via symbolic links.

## Purpose

Enable the full AID methodology in any project by creating symbolic links to AID's commands, skills, and configuration. The linked project gains access to all AID features while maintaining its own state.

## Usage

```
/link-project [path-to-project]
```

If no path provided, asks for the project path.

## Directory Structure Expected

```
Parent Folder/
├── AID-main/           <- This AID installation
│   ├── .claude/
│   │   ├── commands/
│   │   └── skills/
│   ├── .mcp.json.mac / .mcp.json.windows / .mcp.json.example
│   └── ...
│
└── my-project/         <- Project to link
    └── (your code)
```

## What Gets Created in Target Project

```
my-project/
├── .claude/
│   ├── commands/  -> SYMLINK to AID-main/.claude/commands/
│   └── skills/    -> SYMLINK to AID-main/.claude/skills/
├── .aid/
│   ├── state.json      (project-specific, not linked)
│   └── context.json    (project-specific, not linked)
├── .mcp.json           (copied from template, gitignored, tokens via ${VAR})
└── CLAUDE.md           -> SYMLINK to AID-main/CLAUDE.md
```

## Flow

1. **Get AID Path**: Determine current AID-main installation path
2. **Get Target Path**: Ask user or use provided path
3. **Validate**: Ensure target exists and is not inside AID-main
4. **Create .claude Directory** in target project
5. **Create Symbolic Links**:
   - Windows: `mklink /D` (requires Admin or Developer Mode)
   - Mac/Linux: `ln -s`
6. **Create .aid Directory** with a fresh `context.json`. Do not write `.aid/state.json`:
   only `aid_session.py` writes it. It is created when the user runs `/aid-start` in the
   linked project: with no `state.json` it runs `init`, which the user confirms.
7. **Create `.mcp.json`** in the target: the link scripts copy `.mcp.json.mac` (macOS/Linux)
   or `.mcp.json.windows` (Windows); for the minimal set, copy `.mcp.json.example` by hand
   instead (see "MCP Configuration" below)
8. **Link CLAUDE.md** for methodology instructions
9. **Show Success** with next steps

## MCP Configuration

`.mcp.json.example` at the AID root holds the MCP servers the integration guides
document, with the same names, commands and pinned versions:

| Server | How it runs | Environment variables | Guide |
|--------|-------------|-----------------------|-------|
| `github` | HTTP, `https://api.githubcopilot.com/mcp/` | `GITHUB_PERSONAL_ACCESS_TOKEN` | `integrations/github/README.md` |
| `jira` | `npx -y @aashari/mcp-server-atlassian-jira@3.3.0` | `ATLASSIAN_SITE_URL`, `ATLASSIAN_USER_EMAIL`, `ATLASSIAN_API_TOKEN` | `integrations/jira/README.md` |
| `chrome-devtools` | `npx -y chrome-devtools-mcp@1.12.0` | none | `integrations/chrome-devtools/README.md` |

Every secret in the file is a placeholder such as `"${ATLASSIAN_API_TOKEN:-}"`, which
Claude Code expands from your environment when it starts the server. **Provide your
tokens through environment variables, never in the file.** Keep them in your OS keystore
(macOS Keychain, Windows Credential Manager, Linux libsecret) and export them into the
shell you start `claude` from; see the integration guides for the exact commands. Never
replace a placeholder with a real token: `.mcp.json` is gitignored, but a token in a file
can still leak through backups, copies or a mistaken `git add -f`.

The `link-project.sh` / `link-project.bat` scripts copy the per-OS templates
`.mcp.json.mac` / `.mcp.json.windows` instead. Those contain the same three servers plus
`filesystem` and `confluence`, and use the same environment-variable placeholders.

## Windows Commands (Run as Admin or with Developer Mode)

```batch
cd "C:\Projects\my-project"
mkdir .claude
mklink /D ".claude\commands" "C:\path\to\AID-main\.claude\commands"
mklink /D ".claude\skills" "C:\path\to\AID-main\.claude\skills"
mklink "CLAUDE.md" "C:\path\to\AID-main\CLAUDE.md"
mkdir .aid
copy "C:\path\to\AID-main\.mcp.json.example" ".mcp.json"
```

## Mac/Linux Commands

```bash
cd ~/Projects/my-project
mkdir -p .claude
ln -s ~/path/to/AID-main/.claude/commands .claude/commands
ln -s ~/path/to/AID-main/.claude/skills .claude/skills
ln -s ~/path/to/AID-main/CLAUDE.md CLAUDE.md
mkdir -p .aid
cp ~/path/to/AID-main/.mcp.json.example .mcp.json
```

## Example Output

```
/link-project C:\Projects\my-app

AID Project Linker
==================

AID Installation: C:\Tools\AID
Target Project:   C:\Projects\my-app

Creating symbolic links...
  [OK] .claude/commands -> AID commands
  [OK] .claude/skills   -> AID skills
  [OK] CLAUDE.md        -> AID methodology

Creating project-specific files...
  [OK] .aid/context.json
  [--] .aid/state.json (created by /aid-start)
  [OK] .mcp.json (reads tokens from environment variables)
  [OK] .mcp.json added to .gitignore

===========================================
Project linked successfully!
===========================================

Next steps:
1. Export your API tokens from the OS keystore (see INSTALLATION.md); .mcp.json reads them
2. Open Claude Code in C:\Projects\my-app
3. Run /aid-start to begin working

All AID commands are now available:
  /aid-start, /aid-status, /prd, /tech-spec,
  /design-system, /code-review, /write-tests, etc.
```

## What the Linked Project Gets

| Feature | Description |
|---------|-------------|
| All Commands | /aid-start, /prd, /tech-spec, /code-review, etc. |
| All Skills | atomic-design, system-architect, test-driven, etc. |
| Phase Enforcement | PRD -> Tech Spec -> Development -> QA flow |
| Context Tracking | Automatic progress tracking |
| MCP Servers | Jira, GitHub integration (after token setup) |

## Troubleshooting

### Windows: "You do not have sufficient privilege"
Enable Developer Mode: Settings > Update & Security > For Developers > Developer Mode

### Symlinks not working
Fall back to copying instead of linking (run install.bat in the target folder)

## Notes

- Symbolic links mean updates to AID-main automatically apply to all linked projects
- Each project maintains its own .aid/state.json (phase progress is per-project)
- .mcp.json is copied per project and added to its .gitignore; tokens come from environment variables, never the file
- Run from within AID-main folder, pointing to the target project
