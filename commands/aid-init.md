---
description: "Initialize this project with AID phases and the memory system"
---

# /aid-init

Initialize this project with AID phases, and the AID Memory System.

## Purpose

First-time setup of a project: `aid_session.py init` creates the project's `.aid/state.json`
and `.aid/context.json`; this command also sets up the user-level memory system
directories.

## Bootstrap the project (ONE confirmed Bash call)

The project `.aid/state.json` has exactly one writer: `aid_session.py`.
**Never create or edit `.aid/state.json` yourself** (not with the Write, Edit, MultiEdit or
NotebookEdit tools, a Bash redirect, `cp`, `tee` or any other command). The phase gates
refuse that in every folder, AID project or not.

1. Print the role menu and wait for the user's number:

   ```bash
   python "${CLAUDE_PLUGIN_ROOT}/hooks/aid_session.py" roles
   ```

2. Print that role's phase menu and wait for the user's number (a new project usually
   starts at Phase 0):

   ```bash
   python "${CLAUDE_PLUGIN_ROOT}/hooks/aid_session.py" phases <role>
   ```

3. Create the project state with exactly this command:

   ```bash
   python "${CLAUDE_PLUGIN_ROOT}/hooks/aid_session.py" init <role> <phase>
   ```

   - Run each of these exactly in this shape: one simple command, lowercase `python`, single
     spaces, no `;`, `&&`, pipes, redirects, `$( )` or loops.
   - Claude Code asks the user to confirm `init`. If the user declines, nothing changes.
   - `aid_session.py init` writes `.aid/state.json` and, when it is absent,
     `.aid/context.json` (the file `/context` reads). An existing `context.json` is never
     overwritten.
   - If the call is denied (for example in `-p`, headless or dontAsk sessions, where nobody
     can answer the prompt), do not retry in another spelling and do not write the file
     yourself. Give the user this line to run themselves, with a leading `!`:

     ```
     ! python "${CLAUDE_PLUGIN_ROOT}/hooks/aid_session.py" init <role> <phase>
     ```

     with `${CLAUDE_PLUGIN_ROOT}` replaced by the plugin's real path.
   - If `${CLAUDE_PLUGIN_ROOT}` was not replaced by a real path, this is not a plugin
     install: AID's phase commands need the plugin (`claude plugin install aid@AID`). Do not
     substitute another path.
   - If `.aid/state.json` already exists, do not run `init`: use `/aid-start`. For a
     corrupted state file, `init <role> <phase> --repair` (also confirmed) rewrites it.

## Memory system (user level)

1. Creates `~/.aid/` directory structure:
   ```
   ~/.aid/
   ├── config.yaml
   ├── feedback/
   │   ├── pending/
   │   └── processed/
   ├── skills/
   ├── metrics/
   └── logs/
   ```
   Never create `~/.aid/state.json` (or any `state.json` under `~/.aid/`) yourself. No AID
   command needs one, and a `.aid/state.json` in a parent folder can make every folder below
   it (here: everything under your home directory) look like an AID project to tools that
   look for the nearest `.aid/state.json`. `aid_session.py reset` removes a stale one.

2. Initializes configuration files from `memory-system/templates/`

3. AID's local memory starts empty; entries are added only by `/aid-improve` (`memory-sync`, which you confirm).

## Usage

```
/aid-init
```

## Output

```
✅ AID project and Memory System initialized

Created:
- .aid/state.json (by aid_session.py init, after you confirmed)
- .aid/context.json
- ~/.aid/config.yaml
- ~/.aid/feedback/pending/
- ~/.aid/feedback/processed/
- ~/.aid/skills/ (copied from repo)
- ~/.aid/metrics/

AID local memory: empty (entries are added only by /aid-improve, after you confirm)

Ready! Use /aid-start to begin a session.
```

## Notes

- Safe to run multiple times (won't overwrite existing data)
- Use `/aid-reset` to start fresh
- See `memory-system/docs/COMMANDS.md` for details
