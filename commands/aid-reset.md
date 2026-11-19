---
description: "Full system reset - clears AID's runtime data in $AID_HOME"
disable-model-invocation: true
---

# /aid-reset

Full system reset - clears AID's runtime data in `$AID_HOME` (default `~/.aid`).

## Purpose

Start fresh by removing AID's runtime data. Use when troubleshooting or starting over.

## What it deletes

`aid_session.py reset` deletes exactly these runtime entries under `$AID_HOME`
(the command prints each entry it removes):
- `state.json` - session state
- `agent_state.json` - agent state
- `feedback/` - all pending and processed feedback
- `recommendations/` - queued recommendations
- `metrics/` - metrics and trends
- `reports/` - generated reports
- `memory/` - AID's local memory entries, only with `reset --all`

It does not delete `~/.aid/skills/` or `config.yaml`, or anything else not listed above.

## What it keeps

- `memory/` - AID's local memory entries (kept unless the user asks for `--all`)
- `integrity/` - the session integrity baseline (never deleted, not even with `--all`)
- The project's `.aid/` folder (state, context, QA criteria) - never touched
- Repository files in `memory-system/`
- Any other entry in `$AID_HOME`, such as `skills/` and `config.yaml` (printed as "kept")

## Flow

1. **Confirm with the user** what will be deleted (list above), and whether they also want
   AID's local memory (`memory/`) deleted. Offer the backup below first.

2. **Run exactly one Bash command.** Claude Code asks the user to confirm it:
   ```
   python "${CLAUDE_PLUGIN_ROOT}/hooks/aid_session.py" reset
   ```
   Only when the user explicitly asked to delete the memory too:
   ```
   python "${CLAUDE_PLUGIN_ROOT}/hooks/aid_session.py" reset --all
   ```
   Do not delete anything any other way: no manual deletion, no changing into `$AID_HOME`.
   If the command refuses (non-zero exit), show its reason to the user verbatim and stop.

3. **Show the output** (each removed and kept entry), then suggest `/aid-init` to
   reinitialize.

## Usage

```
/aid-reset
```

## Back Up Before Reset

AID has no export command. To keep your feedback and history, copy the AID data folder
(`$AID_HOME`, default `~/.aid`) before you reset:

```bash
# macOS / Linux / Git Bash
cp -R "${AID_HOME:-$HOME/.aid}" "${AID_HOME:-$HOME/.aid}.backup-$(date +%Y%m%d)"
```

```powershell
# Windows PowerShell
$src = if ($env:AID_HOME) { $env:AID_HOME } else { "$env:USERPROFILE\.aid" }
Copy-Item -Recurse $src "$src.backup-$(Get-Date -Format yyyyMMdd)"
```

To restore, copy the backup folder back to `$AID_HOME`.

## Notes

- Claude Code asks the user before `reset` runs; in `-p` or dontAsk sessions it is denied.
  Outside AID projects, under `--dangerously-skip-permissions` Claude Code does not document
  that a hook's "ask" still prompts, so do not count on a prompt in that mode
- Cannot be undone (except from a backup)
- Run `/aid-init` after reset to reinitialize
- See `memory-system/docs/COMMANDS.md#reset` for details
