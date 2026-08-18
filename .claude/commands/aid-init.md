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

2. Copies skill templates from `memory-system/skills/`

3. Initializes configuration files from `memory-system/templates/`

4. Initializes Claude Memory with 20 starter entries (if not present)

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

Claude Memory: 20 starter entries added

Ready! Use /aid start to begin a session.
```

## Notes

- Safe to run multiple times (won't overwrite existing data)
- Use `/aid reset` to start fresh
- See `memory-system/docs/COMMANDS.md` for details
