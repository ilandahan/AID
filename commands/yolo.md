---
description: "Enable full automation mode - skip confirmation prompts"
disable-model-invocation: true
---

# YOLO Mode - Fewer Permission Prompts

AID does not add allow rules for you. To be asked less often, add scoped allow rules for the
commands and paths you trust, with the built-in command:

```
/permissions
```

For example:
- `Bash(npm test)`
- `Bash(npm run lint)`
- `Bash(git status)`
- `Bash(git diff *)`
- `Edit(src/**)`

Do not add `Bash(*)`, `Edit(*)` or `Write(*)`. They approve every shell command and every file
change without asking.

## Launch flag (not recommended)

**Warning:** `claude --dangerously-skip-permissions` skips Claude Code's permission prompts for
normal tools, so commands and edits run without confirmation. AID's ask rules for phase changes
and memory writes still prompt in every permission mode, and its deny rules and phase gates
still apply. See `docs/SECURITY-MODEL.md`.

To undo, run `/yolo-off`.
