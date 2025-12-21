# /aid init

Initialize the AID Memory System.

## Purpose

First-time setup of the memory system. Creates runtime directories and copies templates. Projects start at **Phase 0 (Discovery)**.

## What It Does

1. Creates `~/.aid/` directory structure:
   ```
   ~/.aid/
   ├── state.json          # Starts at Phase 0 (Discovery)
   ├── config.yaml
   ├── feedback/
   │   ├── pending/
   │   └── processed/
   ├── skills/
   ├── metrics/
   └── logs/
   ```

2. Creates `.aid/` project directory:
   ```
   .aid/
   ├── state.json          # current_phase: 0, phase_name: "Discovery"
   └── context.json
   ```

3. Creates `docs/research/` folder for Phase 0 outputs

4. Copies skill templates from `memory-system/skills/`

5. Initializes configuration files from `memory-system/templates/`

6. Initializes Claude Memory with 20 starter entries (if not present)

## Usage

```
/aid init
```

## Output

```
✅ AID Memory System initialized

Created:
- .aid/state.json (Phase 0: Discovery)
- .aid/context.json
- ~/.aid/state.json
- ~/.aid/config.yaml
- ~/.aid/feedback/pending/
- ~/.aid/feedback/processed/
- ~/.aid/skills/ (copied from repo)
- ~/.aid/metrics/
- docs/research/ (for Phase 0 outputs)

Claude Memory: 20 starter entries added

Ready!
- Use /discovery to start Phase 0 research
- Use /aid start to begin a tracked session
```

## Initial Phase

Projects start at **Phase 0: Discovery**

```
Phase 0 ──► Phase 1 ──► Phase 2 ──► Phase 3 ──► Phase 4 ──► Phase 5
Discovery     PRD      Tech Spec   Impl Plan     Dev       QA & Ship
```

## Notes

- Safe to run multiple times (won't overwrite existing data)
- Use `/aid reset` to start fresh
- See `memory-system/docs/COMMANDS.md` for details
