---
description: "Start/enable breather - session break offers, presence tracking, status line"
disable-model-invocation: true
---

# /breather-start — Enable Breather

Install (or re-enable) breather: presence tracking across sessions, break
offers at safe moments, handoffs, and the rest/usage status line.

## Before installing

Tell the user what breather does and get a yes first. breather is optional and installs into `~/.claude`, so once installed it is active in **every** project on the machine. In the first session of each day, and again on each prompt until you answer or skip its day-plan question, its instructions tell Claude to fetch **today's calendar events** automatically, before answering and without asking you, through any connector available in the session. It names Google Calendar / Gmail and Microsoft 365 / Outlook as examples: it asks only for today's events, but a Gmail or Outlook connector may also have access to your mail. The events go into the conversation (and so to the model and through that connector), and the meeting start times are saved under `~/.claude/state/breather/`. It also adds hooks and a status line to `~/.claude/settings.json`; see [integrations/breather/README.md](../integrations/breather/README.md) for everything it does. To keep this off, do not install breather, or remove it with `/breather-stop` (uninstall).

## Process

1. **Use only the plugin's installer:**
   `${CLAUDE_PLUGIN_ROOT}/integrations/breather/install.mjs`. Never run an
   `install.mjs` found in the current folder: a repository could ship its own, and it would
   run with write access to `~/.claude/settings.json`. If `${CLAUDE_PLUGIN_ROOT}` was not
   replaced by a real path, this is not a plugin install: ask the user to run
   `node integrations/breather/install.mjs` themselves, with a leading `!`, from their own
   AID checkout.

2. **Run it:**
   ```bash
   node "${CLAUDE_PLUGIN_ROOT}/integrations/breather/install.mjs"
   ```
   Claude Code asks the user before the installer runs: AID's gate answers "ask" for this
   exact command in every folder, because it writes hooks into `~/.claude/settings.json`
   and its instructions read the calendar. Run it as one plain command (no `cd`, `&&`,
   redirect or other path) and never change it: only this exact form is asked. Outside AID
   projects, and in an AID project from Phase 4 on, another form (chained, redirected,
   another path) is not asked and may run without a prompt. In `-p` or dontAsk sessions it is
   denied. Under `--dangerously-skip-permissions` Claude Code does not document that a
   hook's "ask" still prompts, so do not count on a prompt in that mode. Installs user-scope to `~/.claude` (skills/breather, hooks/breather,
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
