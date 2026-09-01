# breather (vendored)

Session-boundary tool for Claude Code: tracks presence across sessions, offers
breaks at safe moments, writes handoffs so leaving is cheap. Installed
automatically as step 10 of `install.sh` / `install.bat`, and by `/setup`.

- Source: https://github.com/ilandahan/breather
- `install.mjs` is the upstream self-contained installer, copied verbatim
  (payload embedded — no other files needed).
- Installs user-scope to `~/.claude` (skills/breather, hooks/breather,
  settings.json hooks + statusLine), so it is active in every project on the
  machine, not just AID ones.
- Safe to re-run. An existing custom statusLine is left untouched unless
  `--force` is passed.
- Uninstall: `node install.mjs --uninstall`
- Slash commands: `/breather-start` (enable), `/breather-stop` (snooze / skip
  today / uninstall)

To update: copy the latest `install.mjs` from the upstream repo over this one.
