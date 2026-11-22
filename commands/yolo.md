---
description: "Fewer permission prompts - how to add scoped allow rules for commands you trust"
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
normal tools, so commands and edits run without confirmation. AID's gate itself still answers
"ask" for its human-confirmed commands (`aid_session.py` `approve`, `advance`, `jump`, `init`,
`memory-sync`, `memory-apply`, `reset`, `qa-pass`, the breather installer and
`scripts/init-project.sh`) in every folder, and in AID projects its ask rules are a second
layer; its deny rules and phase gates still apply. Claude Code documents that explicit ask
rules (the second layer, AID projects only) still prompt in this mode. It does not document
whether a hook's "ask" does. So outside AID projects, and for the breather installer and
`scripts/init-project.sh` in every folder, do not count on a prompt in this mode. In `-p` or
dontAsk sessions these calls are denied. See `docs/SECURITY-MODEL.md`.

To undo, run `/yolo-off`.
