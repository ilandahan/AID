# /link-project

Link an existing project folder to AID via symbolic links.

## Purpose

Connect any existing project to the AID methodology by creating symbolic links from the project to AID resources (skills, commands, templates).

## Usage

```
/link-project [path-to-project]
```

If no path provided, use current working directory.

## What It Does

1. **Verify Target Project**: Check the target folder exists and is a valid project (has package.json, .git, etc.)

2. **Create Symbolic Links** in the target project:
   ```
   target-project/
   ├── .claude/
   │   ├── commands/ -> [AID]/.claude/commands/
   │   └── skills/   -> [AID]/.claude/skills/
   ├── .aid/         -> (created, not linked)
   │   ├── state.json
   │   └── context.json
   └── .mcp.json     -> (copied from template)
   ```

3. **On Windows**, use `mklink /D` for directory symlinks:
   ```batch
   mklink /D ".claude\commands" "[AID-PATH]\.claude\commands"
   mklink /D ".claude\skills" "[AID-PATH]\.claude\skills"
   ```

4. **On Mac/Linux**, use `ln -s`:
   ```bash
   ln -s "[AID-PATH]/.claude/commands" ".claude/commands"
   ln -s "[AID-PATH]/.claude/skills" ".claude/skills"
   ```

5. **Create Project-Specific Files** (not linked):
   - `.aid/state.json` - project state
   - `.aid/context.json` - work context
   - `.mcp.json` - copy from AID template (user edits with their tokens)

## Flow

1. Ask user for target project path (or use current directory)
2. Verify target is a valid project folder
3. Check if .claude folder already exists (warn if overwriting)
4. Create .claude directory in target
5. Create symbolic links to AID commands and skills
6. Create .aid directory with fresh state files
7. Copy .mcp.json.example to target as .mcp.json
8. Show success message with next steps

## Example

```
> /link-project C:\Projects\my-app

Linking project: C:\Projects\my-app

Creating symbolic links...
  .claude/commands -> C:\AID\.claude\commands
  .claude/skills   -> C:\AID\.claude\skills

Creating project files...
  .aid/state.json
  .aid/context.json
  .mcp.json (from template)

Project linked successfully!

Next steps:
1. Edit .mcp.json with your API tokens
2. Open Claude Code in C:\Projects\my-app
3. Run /aid-start to begin working
```

## Notes

- Requires administrator privileges on Windows for symlinks (or Developer Mode enabled)
- If symlinks fail, falls back to copying files
- Safe to run multiple times (won't overwrite existing .aid/ files)
- Use /aid-status in the linked project to verify
