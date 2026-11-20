# breather (vendored, optional)

Session-boundary tool for Claude Code: tracks presence across sessions, offers
breaks at safe moments, writes handoffs so leaving is cheap.

**It is optional.** `install.sh` / `install.bat` (step 10) and `/setup` ask before
installing it, and the default is No (`install.sh --with-breather` /
`install.bat /breather` opt in without the prompt). `/breather-start` installs it on
request.

## What it does on your machine

Checked against the embedded files (`PAYLOAD.lock.json` pins them).

- **Calendar, automatically.** In the first session of each day (`session-open` hook), and
  again on each prompt until you answer or skip its day-plan question (`clock` hook), its
  instructions tell Claude to fetch **today's calendar events** before answering, without
  asking you, through any connector in the session. It names Google Calendar / Gmail and
  Microsoft 365 / Outlook as examples. It asks only for today's events, but a Gmail or
  Outlook connector may also have access to your mail. The events enter the conversation, so
  they go to the model and through that connector. Meeting start times are saved under
  `~/.claude/state/breather/`. If no connector is available, it says so once.
- **Instruction priority.** Its session-start text says "Read this now, before any other
  skill or rule", and its skill text is added to every session.
- **Settings.** The installer adds 4 hooks to `~/.claude/settings.json` (SessionStart,
  UserPromptSubmit, PostToolBatch, SessionEnd) and sets `statusLine` (an existing one is
  kept unless you pass `--force`). It saves `settings.json.bak-<timestamp>` first and leaves
  that backup in place.
- **Local state.** `~/.claude/state/breather/` keeps presence (session ids, working
  directories, times), the day plan and rate-limit readings for the status line. Uninstall
  leaves this folder and the settings backups; delete them by hand for a clean slate.
- **Handoffs.** It writes handoff notes to the project's `.aid/handoff/`, and at session
  start it tells Claude to read the latest one and open with its next step. In a repository
  you do not trust, that file is project-controlled text (see
  `rules/general/untrusted-content.md`).
- **Notifications.** On the day's first prompt or session it shows a desktop notification:
  on Windows by starting a hidden PowerShell with an encoded command, on macOS `osascript`,
  on Linux `notify-send`. Security tools may flag the encoded PowerShell.
- **No network calls** of its own; the calendar fetch goes through Claude's connectors.
- **`mark.mjs` in AID projects: you type it with `!`.** breather's session-start text asks
  Claude to run `mark.mjs` (for example `ack` after it has shown the day's notice). In an AID
  project the phase gate refuses that command to Claude in every phase and level, because it
  runs a file under `~/.claude/hooks` (a control path). So in an AID project type it
  yourself, with the leading `!`: `! node ~/.claude/hooks/breather/mark.mjs ack` (and
  likewise `resumed`, `snooze <minutes>` or `skip`). The vendored payload is unchanged
  (`PAYLOAD.lock.json` still pins it); only this instruction differs in AID projects.

To keep all of this off, do not install breather, or remove it with `/breather-stop`
(uninstall) or `node install.mjs --uninstall`.

## Where it installs

- User-scope to `~/.claude` (skills/breather, hooks/breather, settings.json hooks +
  statusLine), so it is active in every project on the machine, not just AID ones.
- Safe to re-run. An existing custom statusLine is left untouched unless `--force` is
  passed.
- Uninstall: `node install.mjs --uninstall`
- Slash commands: `/breather-start` (enable), `/breather-stop` (snooze / skip today /
  uninstall)

## Known limits of the pinned installer

Both were reproduced against the pinned `install.mjs` (T16-60). The installer is pinned
byte for byte (see Integrity below), so AID does not patch it; the fix belongs upstream,
followed by a re-pin.

- **Uninstall strips by substring.** `--uninstall` (and every re-install, which strips the
  old entries first) removes every hook command in `~/.claude/settings.json` whose text
  contains `breather`, and a status line whose command contains it, not only the entries
  the installer added. A hook of your own such as `node /opt/my-breather-notes.mjs` is
  removed too. The installer writes a `settings.json.bak-<timestamp>` backup first:
  restore your own entries from it if needed.
- **`CLAUDE_HOME` moves the files, not the hook paths.** With `CLAUDE_HOME` set, the files
  go to `$CLAUDE_HOME/.claude/hooks/breather/` and the settings to
  `$CLAUDE_HOME/.claude/settings.json`, but the hook and status-line commands it writes are
  the literal `node ~/.claude/hooks/breather/<file>.mjs`. Unless `$CLAUDE_HOME` is your home
  directory, those commands point at files that do not exist. Install without
  `CLAUDE_HOME`, or fix the paths in that `settings.json` by hand.
- Upstream fix needed (owner action): match only the exact commands the installer writes,
  and write hook commands from the resolved install directory.

## Integrity (pinned)

- Source: https://github.com/ilandahan/breather
- `install.mjs` is the upstream self-contained installer, copied byte for byte. The hook
  and skill files it writes are embedded in it as one base64 JSON payload.
- `PAYLOAD.lock.json` pins it: the upstream commit, the SHA-256 of `install.mjs`, and the
  SHA-256 of every embedded file. `testing/e2e/test_t11_breather.py` decodes the payload
  and checks all of them, so any change fails CI until it is re-pinned on purpose.

To update: copy `install.mjs` from upstream at a chosen commit, decode and review the
diff of the embedded files, then regenerate `PAYLOAD.lock.json` (new commit, new hashes)
and update this README if the behaviour changed.
