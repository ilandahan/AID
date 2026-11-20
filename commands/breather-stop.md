---
description: "Stop breather - snooze offers, skip today, or uninstall completely"
disable-model-invocation: true
---

# /breather-stop — Pause or Remove Breather

Three levels of "stop". Ask the user which one they want if the request is
ambiguous (default to the lightest that matches their words):

Snooze and skip run breather's `mark.mjs` under `~/.claude/hooks/`. In an AID project the
phase gate refuses that command to Claude in every phase (it runs a file under
`~/.claude/hooks`, a control path), and that rule stays. So do not run these two yourself:
show the user the line and ask them to type it, with the leading `!`.

## 1. Snooze — quiet for N minutes

The user types:

```
! node ~/.claude/hooks/breather/mark.mjs snooze 90
```

No offers for the given minutes. Presence tracking continues.

## 2. Skip today — no more offers until tomorrow

The user types:

```
! node ~/.claude/hooks/breather/mark.mjs skip
```

Day plan questions and offers stop for the rest of the day.

## 3. Uninstall — remove breather entirely

```bash
node "${CLAUDE_PLUGIN_ROOT}/integrations/breather/install.mjs" --uninstall
```

Claude Code asks the user before the installer runs (AID's gate answers "ask" for this exact
command in every folder; in `-p` or dontAsk sessions it is denied). Under
`--dangerously-skip-permissions` Claude Code does not document that a hook's "ask" still
prompts, so do not count on a prompt in that mode.

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
