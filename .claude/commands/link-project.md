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
│   ├── .mcp.json.example
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
├── .mcp.json           (copied from template, user edits tokens)
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
6. **Create .aid Directory** with fresh state files
7. **Copy .mcp.json.example** to target as `.mcp.json`
8. **Link CLAUDE.md** for methodology instructions
9. **Show Success** with next steps

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

AID Installation: C:\ilans' local files\demo\AID-main
Target Project:   C:\Projects\my-app

Creating symbolic links...
  [OK] .claude/commands -> AID commands
  [OK] .claude/skills   -> AID skills
  [OK] CLAUDE.md        -> AID methodology

Creating project-specific files...
  [OK] .aid/state.json
  [OK] .aid/context.json
  [OK] .mcp.json (edit with your API tokens)

===========================================
Project linked successfully!
===========================================

Next steps:
1. Edit my-app/.mcp.json with your API tokens
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
| MCP Servers | Jira, Figma, GitHub integration (after token setup) |

## Troubleshooting

### Windows: "You do not have sufficient privilege"
Enable Developer Mode: Settings > Update & Security > For Developers > Developer Mode

### Symlinks not working
Fall back to copying instead of linking (run install.bat in the target folder)

## Notes

- Symbolic links mean updates to AID-main automatically apply to all linked projects
- Each project maintains its own .aid/state.json (phase progress is per-project)
- .mcp.json must be configured separately per project (different tokens possible)
- Run from within AID-main folder, pointing to the target project
