---
description: "Start/enable breather - session break offers, presence tracking, status line"
---

# /breather-start — Enable Breather

Install (or re-enable) breather: presence tracking across sessions, break
offers at safe moments, handoffs, and the rest/usage status line.

## Process

1. **Locate the installer** (first match wins):
   - `${CLAUDE_PLUGIN_ROOT}/integrations/breather/install.mjs` (plugin install)
   - `./integrations/breather/install.mjs` (AID repo root)

2. **Run it:**
   ```bash
   node <installer-path>
   ```
   Installs user-scope to `~/.claude` (skills/breather, hooks/breather,
   settings.json hooks + statusLine, with a settings backup). Active in
   every project on this machine.

3. **If a custom statusLine already exists**, the installer leaves it
   untouched and says so. Ask the user before re-running with `--force`.

4. **Tell the user:** restart Claude Code (or run `/hooks` to confirm the
   four breather events are registered). If the status line stays blank,
   accept the workspace trust dialog.

## Notes

- Safe to re-run anytime — it refreshes files and re-patches settings.
- Coming back from a break? `node ~/.claude/hooks/breather/mark.mjs resumed`

## Related

- `/breather-stop` — snooze, skip today, or uninstall
