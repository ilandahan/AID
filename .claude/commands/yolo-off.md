# YOLO Mode - Disable Full Automation

To disable YOLO mode and restore permission prompts:

```
/permissions
```

Then remove these patterns:
- `Bash(*)`
- `Edit(*)`
- `Write(*)`
- `Read(*)`

Or edit `.claude/settings.json` and remove the allowed tools, then restart Claude Code.

## Safe Mode Restored

After disabling, you will be asked for confirmation before:
- Running bash commands
- Editing files
- Writing new files
