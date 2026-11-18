---
description: "Initialize this project with AID phases and the memory system"
---

# /aid init

Initialize the AID Memory System.

## Purpose

First-time setup of the memory system. Creates runtime directories and copies templates.

## What It Does

1. Creates `~/.aid/` directory structure:
   ```
   ~/.aid/
   ├── state.json
   ├── config.yaml
   ├── feedback/
   │   ├── pending/
   │   └── processed/
   ├── skills/
   ├── metrics/
   └── logs/
   ```

2. Initializes configuration files from `memory-system/templates/`

3. AID's local memory starts empty; entries are added only by `/aid-improve` (`memory-sync`, which you confirm).

## Usage

```
/aid init
```

## Output

```
✅ AID Memory System initialized

Created:
- ~/.aid/state.json
- ~/.aid/config.yaml
- ~/.aid/feedback/pending/
- ~/.aid/feedback/processed/
- ~/.aid/skills/ (copied from repo)
- ~/.aid/metrics/

AID local memory: empty (entries are added only by /aid-improve, after you confirm)

Ready! Use /aid start to begin a session.
```

## Notes

- Safe to run multiple times (won't overwrite existing data)
- Use `/aid reset` to start fresh
- See `memory-system/docs/COMMANDS.md` for details
