---
description: "Disable full automation mode - restore confirmation prompts"
disable-model-invocation: true
---

# YOLO Mode - Restore Permission Prompts

To remove allow rules you added with `/yolo`, use the built-in command:

```
/permissions
```

Then delete the rules you no longer want, for example `Bash(npm test)` or `Edit(src/**)`. If
you ever added broad rules such as `Bash(*)`, `Edit(*)` or `Write(*)`, remove those too.

If you started Claude Code with `--dangerously-skip-permissions`, restart it without that flag.
**Warning:** that flag skips Claude Code's permission prompts for normal tools. AID's ask rules
for phase changes and memory writes still prompt in every permission mode, and its deny rules
and phase gates still apply. See `docs/SECURITY-MODEL.md`.

## Safe Mode Restored

After this, Claude Code asks before any tool call that no remaining allow rule covers.
