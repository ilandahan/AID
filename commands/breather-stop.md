---
description: "Stop breather - snooze offers, skip today, or uninstall completely"
disable-model-invocation: true
---

# /breather-stop — Pause or Remove Breather

Three levels of "stop". Ask the user which one they want if the request is
ambiguous (default to the lightest that matches their words):

## 1. Snooze — quiet for N minutes

```bash
node ~/.claude/hooks/breather/mark.mjs snooze 90
```

No offers for the given minutes. Presence tracking continues.

## 2. Skip today — no more offers until tomorrow

```bash
node ~/.claude/hooks/breather/mark.mjs skip
```

Day plan questions and offers stop for the rest of the day.

## 3. Uninstall — remove breather entirely

```bash
node <installer-path> --uninstall
```

Installer path (first match wins):
- `${CLAUDE_PLUGIN_ROOT}/integrations/breather/install.mjs` only (plugin install). Never run an
  `install.mjs` from the current folder; outside a plugin install, ask the user to run it
  themselves with a leading `!` from their own AID checkout.

Removes `~/.claude/skills/breather`, `~/.claude/hooks/breather`, and the
breather entries in `settings.json` (hooks + statusLine). Confirm with the
user before uninstalling — it affects every project on this machine, not
just this one. Tell them to restart Claude Code afterwards.

## Related

- `/breather-start` — re-enable after an uninstall
