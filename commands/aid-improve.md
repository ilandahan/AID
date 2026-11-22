---
description: "Run the improvement analysis cycle"
---

# /aid-improve

Run the improvement analysis cycle.

## Purpose

Analyze collected feedback and propose skill learnings and memory entries. AID's own write
commands (`memory-sync`, `memory-apply`) run only after the user confirms them.

## Requirements

- At least 3 feedback entries. Count the entries in the `memory-feedback` output (step 2);
  if there are fewer than 3, stop unless the user passed `--force`.

Feedback text is redacted (best effort) when it is written and again when it is read. See
"Privacy" below.

## Flow

Every step that runs a command is ONE Bash call, in exactly the shape shown:

- lower-case `python`, single spaces, the subcommand bare;
- no `;`, `&&`, pipes, redirects, `$( )` or loops;
- never retry in another spelling, and never work around a refusal or a declined prompt;
- if `${CLAUDE_PLUGIN_ROOT}` was not replaced by a real path, this is not a plugin
  install. Do not substitute another path. The user can run the command themselves by
  typing it with a leading `!`.

1. **Preview** (writes nothing, no prompt):

   ```bash
   python "${CLAUDE_PLUGIN_ROOT}/hooks/aid_session.py" memory-preview
   ```

   It prints the memory entries a sync would add and the current proposal queue. Show
   the output.

2. **Analyze** (sub-agent): get the feedback, redacted (writes nothing, no prompt):

   ```bash
   python "${CLAUDE_PLUGIN_ROOT}/hooks/aid_session.py" memory-feedback
   ```

   Count its entries; if there are fewer than 3, stop unless the user passed `--force`.

   Spawn `aid:memory-analysis-agent` (link-project route only: `memory-analysis-agent`; tools: Read, Grep,
   Glob) and pass it:

   - `{{FEEDBACK_DATA}}`: the `memory-feedback` output. Do not paste raw files from the
     pending folder: files written before redaction existed may still hold unredacted text.
   - `{{CURRENT_SKILLS}}` (optional, may be empty): section headers from
     `skills/memory-system/references/`.
   - `{{TREND_DATA}}` (optional, may be empty).
   - `{{MEMORY_ENTRIES}}` (optional, may be empty): the output of
     `python -m memory_system --memories` run from `memory-system/`, or leave it empty.

   The agent writes no files. It returns JSON with proposals only.

3. **Queue the proposals** (no prompt): save the agent's JSON to
   `.aid/improve/proposals.json` with the Write tool, then run:

   ```bash
   python "${CLAUDE_PLUGIN_ROOT}/hooks/aid_session.py" memory-queue
   ```

   It takes no argument: it reads `<project>/.aid/improve/proposals.json` itself.

   Each proposal is redacted and added to `$AID_HOME/recommendations/queue.json`. A
   proposal whose target is not an allowed learnings file is skipped, and the output says
   so.

4. **Show the queue**: run `memory-preview` again (step 1) and show each proposal with
   its id, target file and proposed text. Ask the user which ones to apply and which to
   drop.

5. **Apply or drop, one proposal at a time**, only for items the user picked:

   ```bash
   python "${CLAUDE_PLUGIN_ROOT}/hooks/aid_session.py" memory-apply <id>
   ```

   - Claude Code asks the user to confirm this call. If the user declines, nothing changes.
   - It only APPENDS the proposal's redacted text to
     `skills/memory-system/references/roles/<role>/cumulative.md` or
     `skills/memory-system/references/phases/<phase>/cumulative.md`. Any other target is
     refused.
   - It writes the copy of `skills/memory-system/references/...` inside the installed
     plugin. A plugin update can replace that copy.
   - An applied proposal moves to `$AID_HOME/recommendations/applied.json`.
   - Skill-wide recommendations (no learnings file) are shown but cannot be applied by
     the tool.

   ```bash
   python "${CLAUDE_PLUGIN_ROOT}/hooks/aid_session.py" memory-reject <id>
   ```

   - No prompt. The proposal moves to `$AID_HOME/recommendations/rejected.json`.

   If a command refuses (non-zero exit), show its reason to the user verbatim.

6. **Write memory entries** (only if the user wants the entries shown in the preview):

   ```bash
   python "${CLAUDE_PLUGIN_ROOT}/hooks/aid_session.py" memory-sync
   ```

   Claude Code asks the user to confirm this call. It writes the entries to AID's local
   memory, `$AID_HOME/memory/slots.json` (default `~/.aid/memory/`). Nothing is sent to
   Claude's built-in memory. In `-p`/headless sessions nobody can answer the prompt, so
   the call is denied.

7. **Summary**: list what was applied, rejected and synced, from the command output.

## Usage

```
/aid-improve
```

Force with limited data:
```
/aid-improve --force
```

## Notes

- Run weekly or after 5+ sessions
- AID's own write commands (`memory-sync`, `memory-apply`) run only after the user confirms them
  in Claude Code's prompt. `memory-apply` is also used by `/aid-recommendations`. Before Phase
  4 the phase gate also refuses other writes outside the project. From Phase 4 on, AID does
  not stop other code from editing these files.
- Memory entries follow format: `AID:{ROLE}:{PHASE}:{TYPE} {insight}`
- See `memory-system/docs/IMPROVEMENT-FLOW.md` for full process

## Privacy

Redaction is best effort. It replaces e-mail addresses, URLs (including git remotes),
absolute paths, `file.ext:line` references, common secret tokens, the project's own
names (cwd and project-root folder names, git remote owner and repo) and the OS user name
with placeholders: `[email]`, `[url]`, `[path]`, `[file-ref]`, `[token]`, `[project]`, `[user]`. It
does not catch a person's or company's name written as plain words unless it is one of
those project names. Very generic folder names (docs, app, src, ...) and project names
shorter than 4 characters are not removed. When files are read later, only the current
project's names are known.

Feedback is stored locally in `$AID_HOME`. AID has no collection service of its own. When
you run `/aid-improve`, the redacted feedback is sent to Claude as part of the conversation,
for analysis.
