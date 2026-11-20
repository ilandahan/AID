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
**Warning:** that flag skips Claude Code's permission prompts for normal tools. AID's gate
itself still answers "ask" for its human-confirmed commands (`aid_session.py` `approve`,
`advance`, `jump`, `init`, `memory-sync`, `memory-apply`, `reset`, `qa-pass`, the breather
installer and `scripts/init-project.sh`) in every folder, and in AID projects its ask rules
are a second layer; its deny rules and phase gates still apply. Claude Code documents that
explicit ask rules (the second layer, AID projects only) still prompt in this mode. It does
not document whether a hook's "ask" does. So outside AID projects, and for the breather
installer and `scripts/init-project.sh` in every folder, do not count on a prompt in this
mode. In `-p` or dontAsk sessions these calls are denied. See `docs/SECURITY-MODEL.md`.

## Safe Mode Restored

After this, Claude Code asks before any tool call that no remaining allow rule covers.
