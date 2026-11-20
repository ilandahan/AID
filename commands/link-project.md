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

The scripts behind it:

```
./link-project.sh  <path> [--force] [--role <name|number>]     # macOS / Linux / Git Bash
link-project.bat   <path> [--force] [--copy] [--role <name|number>]   # Windows
```

`--role` is the role the project state starts with (default `1`, the first role in the
`/aid-start` menu). Both scripts need `node` (the registered hooks run with it; without
node they stop before writing anything) and `python` (for `aid_session.py init`).

## Directory Structure Expected

```
Parent Folder/
├── AID-main/           <- This AID installation (components at the repo root)
│   ├── commands/  skills/  agents/  references/  rules/  hooks/
│   ├── scripts/link-settings.mjs
│   ├── CLAUDE.md
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
│   ├── commands/   -> link to AID-main/commands/
│   ├── skills/     -> link to AID-main/skills/
│   ├── agents/     -> link to AID-main/agents/
│   ├── references/ -> link to AID-main/references/
│   ├── rules/      -> link to AID-main/rules/
│   ├── hooks/      -> link to AID-main/hooks/
│   └── settings.json   (permissions + the AID hooks, absolute paths to AID-main)
├── .aid/
│   ├── state.json      (written by aid_session.py init, not linked)
│   └── context.json    (written by aid_session.py init, not linked)
├── .mcp.json           (copied from template, gitignored, tokens via ${VAR})
└── CLAUDE.md           -> SYMLINK to AID-main/CLAUDE.md
```

## Flow

1. **Get AID Path**: Determine current AID-main installation path
2. **Get Target Path**: Ask user or use provided path
3. **Validate**: Ensure target exists and is not inside AID-main
4. **Create .claude Directory** in target project
5. **Create Links**: `.claude/commands`, `skills`, `agents`, `references`, `rules` and
   `hooks` in the project point at the folders of the same name at AID-main's root
   - Windows: `mklink /J` directory junctions (no Admin needed); `CLAUDE.md` with `mklink /H`
   - Mac/Linux: `ln -s`
6. **Register the AID hooks**: `node scripts/link-settings.mjs <project> <AID-main>` merges
   the SessionStart, PreToolUse (writes and commands), PostToolUse and Stop hooks of
   `.claude-plugin/plugin.json` into the project's `.claude/settings.json`, with
   `${CLAUDE_PLUGIN_ROOT}` replaced by AID-main's absolute path. The project gets the same
   phase gates as the plugin (`onFailure: block`). Your own keys and hooks are kept; a second
   run changes nothing; a settings file that cannot be parsed is left alone and the link stops.
7. **Create the project state**: the scripts run AID-main's `hooks/aid_session.py` with
   the arguments `init <role> 0`, using python, in the project folder. `aid_session.py` is the only
   writer of `.aid/state.json`; `init` also creates `.aid/context.json`. The scripts never
   write either file themselves. With no working python they print that exact command for
   you to run and finish with a warning.
8. **Create `.mcp.json`** in the target: the link scripts copy `.mcp.json.mac` (macOS/Linux)
   or `.mcp.json.windows` (Windows); for the minimal set, copy `.mcp.json.example` by hand
   instead (see "MCP Configuration" below)
9. **Link CLAUDE.md** for methodology instructions
10. **Show Success** with next steps

## MCP Configuration

`.mcp.json.example` at the AID root holds the MCP servers the integration guides
document, with the same names, commands and pinned versions:

| Server | How it runs | Environment variables | Guide |
|--------|-------------|-----------------------|-------|
| `github` | HTTP, `https://api.githubcopilot.com/mcp/` | `GITHUB_PERSONAL_ACCESS_TOKEN` | `integrations/github/README.md` |
| `jira` | `npx -y @aashari/mcp-server-atlassian-jira@3.3.0` | `ATLASSIAN_SITE_NAME` (subdomain only, e.g. `mycompany`), `ATLASSIAN_USER_EMAIL`, `ATLASSIAN_API_TOKEN` | `integrations/jira/README.md` |
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

## Linking by Hand

Prefer the scripts. If you link by hand, run the commands below for your OS. They link
the same six folders the scripts link (AID-main's `commands`, `skills`, `agents`,
`references`, `rules` and `hooks`, which sit at the repository root, not under
`.claude/`), register the hooks (without them the project has no phase gates), and create
the project state.

The last command creates the state. Run it yourself, in the project folder, from a
terminal or by typing it in Claude Code with a leading `!`:

```
python "<AID-main>/hooks/aid_session.py" init <role> 0
```

`<role>` is a role name or its number in the `/aid-start` menu (`1` is the first). Do not
use `/aid-start` for this step: in a linked project (not a plugin install),
`${CLAUDE_PLUGIN_ROOT}` is not replaced, and `/aid-start` stops.

## Windows Commands (cmd; junctions need no Admin rights)

```batch
cd /d "C:\Projects\my-project"
mkdir .claude
mklink /J ".claude\commands"   "C:\path\to\AID-main\commands"
mklink /J ".claude\skills"     "C:\path\to\AID-main\skills"
mklink /J ".claude\agents"     "C:\path\to\AID-main\agents"
mklink /J ".claude\references" "C:\path\to\AID-main\references"
mklink /J ".claude\rules"      "C:\path\to\AID-main\rules"
mklink /J ".claude\hooks"      "C:\path\to\AID-main\hooks"
mklink /H "CLAUDE.md" "C:\path\to\AID-main\CLAUDE.md"
copy "C:\path\to\AID-main\.mcp.json.windows" ".mcp.json"
node "C:\path\to\AID-main\scripts\link-settings.mjs" "C:\Projects\my-project" "C:\path\to\AID-main"
python "C:\path\to\AID-main\hooks\aid_session.py" init 1 0
```

## Mac/Linux Commands

```bash
cd ~/Projects/my-project
mkdir -p .claude
ln -s ~/path/to/AID-main/commands   .claude/commands
ln -s ~/path/to/AID-main/skills     .claude/skills
ln -s ~/path/to/AID-main/agents     .claude/agents
ln -s ~/path/to/AID-main/references .claude/references
ln -s ~/path/to/AID-main/rules      .claude/rules
ln -s ~/path/to/AID-main/hooks      .claude/hooks
ln -s ~/path/to/AID-main/CLAUDE.md CLAUDE.md
cp ~/path/to/AID-main/.mcp.json.mac .mcp.json
node ~/path/to/AID-main/scripts/link-settings.mjs ~/Projects/my-project ~/path/to/AID-main
python ~/path/to/AID-main/hooks/aid_session.py init 1 0
```

Then add `.mcp.json` to the project's `.gitignore`.

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
  [OK] .claude/settings.json registers the AID hooks (C:/Tools/AID)
  [OK] state.json created by aid_session.py init (also .aid/context.json)
  [OK] .mcp.json (reads tokens from environment variables)
  [OK] .mcp.json added to .gitignore

===========================================
Project linked successfully!
===========================================

Next steps:
1. Export your API tokens from the OS keystore (see INSTALLATION.md); .mcp.json reads them
2. Open Claude Code in C:\Projects\my-app
3. /aid-start, /aid-status, /phase-approve and /phase-advance need the plugin
   (claude plugin install aid@AID). Without it, run the session steps yourself
   (in Claude Code, with a leading !):
   python "C:/Tools/AID/hooks/aid_session.py" status   (also: start, approve, advance)
```

The commands that call `${CLAUDE_PLUGIN_ROOT}` (`/aid-start`, `/aid-status`, `/aid-end`,
`/phase-approve`, `/phase-advance`, `/gate-check` and the other session and memory commands)
stop in a linked project, because only a plugin install replaces that variable. Install the
plugin (`claude plugin install aid@AID`) to use them, or run AID-main's
`hooks/aid_session.py` with `start`, `approve`, `advance` or `status` yourself, as in the
`init` step above.

## What the Linked Project Gets

| Feature | Description |
|---------|-------------|
| Commands | /prd, /tech-spec, /code-review, etc. The session commands (/aid-start, /aid-status, /phase-approve, /phase-advance) need the plugin; without it run `hooks/aid_session.py` yourself |
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
