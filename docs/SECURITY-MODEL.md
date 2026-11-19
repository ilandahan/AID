# AID security model

What AID's phase gates guarantee, what they do not, and how to add a real boundary.

## What AID is

AID's hooks are a **guardrail for a cooperating agent**. They keep Claude inside the phase
process: no source code before Phase 4, and no tampering with AID's own control files.
They are **not a sandbox**. Once code runs (Phase 4 onwards), that code can do whatever your
user account can do. AID does not stop a deliberate attacker who has a shell.

Claude Code's docs make the same point about hooks. Exit code 0 from a PreToolUse hook does
not approve a call; the call still goes through the normal permission flow
([hooks guide](https://code.claude.com/docs/en/hooks-guide.md)). For a hard allow or deny,
use the permission system ([hooks reference](https://code.claude.com/docs/en/hooks.md)).

## Enforcement levels

Since 3.0.8 the two phase gates **block by default** in every AID project. An AID project
is one with `.aid/state.json` or `.aid/hooks/config.json`. The phase rules apply only
there; some hooks also act in other folders (see
[Hooks that act outside AID projects](#hooks-that-act-outside-aid-projects)).

| Level | What happens when Claude breaks a phase rule |
|-------|----------------------------------------------|
| `block` (default) | The tool call is denied, with the reason and a way forward. |
| `warn` | The call is allowed, and Claude gets a warning. |
| `log` | The call is allowed and only recorded in `.aid/audit/`. |

You can lower a gate per project in `.aid/hooks/config.json`. Each gate is set on its own,
levels are case-insensitive, and an unknown value (or a config file that cannot be read)
counts as `block`:

```json
{ "enforcement": { "phase_gate_write": "warn", "phase_gate_bash": "log" } }
```

Lowering a gate relaxes only the **phase rules**: writing source and running code before
Phase 4. That has a cost: at `log` or `warn`, code runs and interpreter one-liners
(`python -c`, `node -e`) are allowed before Phase 4, so project code can do anything your
account can from Phase 0 on. **Writes to AID's control files stay refused at every level and
in every phase.** In an AID project, every PowerShell command whose text names
`aid_session` is also refused at every level and in every phase, except the exact canonical
form of a confirmed subcommand, which gets "ask" (see below). That check reads the command
text, so it is best effort: a PowerShell call whose script name is hidden in a variable
(`python $env:SCRIPT reset`) does not name `aid_session` and runs without a prompt from
Phase 4 on, or from Phase 0 at `log` or `warn`.
Only you should change the config file. Every SessionStart in a project with a gate at
`log` or `warn` states each such gate and its level (for example `phase_gate_bash: log`),
whether or not it changed since the last session.

## Hooks that act outside AID projects

The phase rules apply only in AID projects, but these hooks are not limited to them:

- **dev-pipeline-gate (Stop)** runs in every git repo. When a turn ends with changed
  source files, it may run the repo's own checkers (for example
  `node_modules/typescript/bin/tsc`), which is running that repo's code, and can block the
  turn on errors.
- **plan-execution-pipeline (ExitPlanMode)** runs in every project. When a plan is approved
  it injects the pipeline instructions and writes `~/.claude/.loop1-kickoff/<session_id>`.
- **The Bash gate** answers "ask" for the confirmed `aid_session.py` commands, the breather
  installer and `scripts/init-project.sh` in every folder (next section), from the Bash tool
  and from the PowerShell tool, in the exact forms the next section gives.

## Human confirmation ("ask")

AID's PreToolUse Bash gate itself returns `permissionDecision: "ask"`, in every folder (AID
project or not) and at every gate level, for:

- the human-confirmed `aid_session.py` subcommands: `approve`, `advance`, `jump`, `init`
  (including `init --repair`), `memory-sync`, `memory-apply`, `reset` and `qa-pass`, called
  in their canonical form (`python "<plugin>/hooks/aid_session.py" <subcommand> [args]`, one
  plain command) on the live plugin or another installed copy of it;
- any `aid_session.py` subcommand (confirmed or not) run with the Bash tool from an installed
  copy of the plugin that is not the live one (an older cached version, a directory
  marketplace, another `installed_plugins.json` entry), in the canonical form (one plain
  command, absolute script path);
- the plugin's breather installer (`node "<plugin>/integrations/breather/install.mjs"`) and
  `bash "<plugin>/scripts/init-project.sh"`, in that exact form only. Other spellings of these
  two scripts (chained, redirected, run with `sh`, or through a relative or copied path) are not asked: outside AID projects, and in
  an AID project from Phase 4 on or at `log` or `warn`, they run without a prompt. Before
  Phase 4 at `block`, the Bash allow-list refuses them. The same exact form is asked from
  the PowerShell tool, for every installed copy of the plugin, in every folder, phase and
  level; other PowerShell spellings of the two scripts get the PowerShell rules below (run
  without a prompt outside AID projects and from Phase 4 on or at `log` or `warn`, refused
  before Phase 4 at `block`).

Any other spelling of a confirmed call (upper-case interpreter, quoted subcommand, chained,
redirected, script name or subcommand built at run time) is denied, with the exact form to
use. In AID projects, the ask rules of layer A
below are a second layer for the Bash tool. They are Bash rules, so for the PowerShell tool the
gate's own ask is the only layer. In an AID project a confirmed call is still asked when the gate is
lowered to `log` or `warn`, and when the layer B baseline was recorded at `log` or `warn`: the
ask is a human confirmation, not a phase rule. In `-p`, headless or dontAsk sessions nobody
can answer the prompt, so Claude Code denies these calls: phase changes, QA passes and resets
need an interactive session.

The ask reads the command text only, so its check of run-time-built names is best effort. It
denies the run-time-built spellings it can parse, in every folder and with the exact form to
use: a confirmed call whose script name or subcommand comes from a variable, `$(...)`,
backticks, a glob, `$'...'` quoting or `xargs` with the script path written out
(`echo approve | xargs python "<plugin>/hooks/aid_session.py"`). That includes a call behind `timeout` or
`winpty`, a call whose script name and subcommand both come from variables, a call followed
by a `#` comment, and an `eval` whose quoted text holds the call.

Deliberately obfuscated spellings are an accepted limit of a text gate. These forms are not
caught: an interpreter name the gate does not match (`pythonw`, `pyw`); a wrapper prefix
that takes an option value or that the gate does not know (`exec -a`, `env -u`, `sudo -u`,
`setsid`, `flock`, `chronic`); a call inside a `case` arm; `xargs` fed by a pipe with the
script name in a variable (`echo approve | xargs python "$S"`) or fed by `-a`; an `eval` of a
string built in a variable (`c="python $S approve"; eval "$c"`); and code given to python
through `/dev/stdin`, `/dev/fd/N` or `<( )` (`python /dev/stdin approve < "$S"`). A `<( )`
followed by a confirmed subcommand (`python <(cat "$S") approve`) is denied in every folder;
what is missed is code built inside the `<( )` that runs the script itself (for example with
`runpy`). Outside AID projects these run without a prompt.

In an AID project the result depends on the phase and the level. Before Phase 4 at `block`,
the Bash allow-list refuses all of these forms. From Phase 4 on, or from Phase 0 when
`phase_gate_bash` is at `log` or `warn`, a second text check still refuses one of them only
when the command writes out the `aid_session.py` path and the very next word is `approve`,
`advance`, `jump`, `init`, `memory-sync` or `memory-apply`
(`chronic python "<plugin>/hooks/aid_session.py" approve`). These get through there without
a prompt: the same forms with `reset` or `qa-pass`; a script name held in a variable, even
when the assignment writes out the path (`S="<plugin>/hooks/aid_session.py"; pythonw "$S"
approve`); the script fed to `/dev/stdin`, `/dev/fd/N` or `python -` by a redirect or
a pipe (`python /dev/stdin approve < "<plugin>/hooks/aid_session.py"`); and code built
inside a `<( )`.

What a text gate cannot see at all is indirection that leaves no trace in the command: a copy
of `aid_session.py`, a wrapper script, or an `eval` of a file written by an earlier call. The
layer A ask rules do not match that indirection either. Outside AID projects, and in an AID
project from Phase 4 on (or from Phase 0 when `phase_gate_bash` is lowered to `log` or
`warn`), such a call is neither asked nor denied, and the same holds for the forms above
that get through. Before Phase 4 at `block`, the Bash allow-list refuses it. This is the same best-effort limit as the
other text checks below.

Under `--dangerously-skip-permissions` (bypassPermissions), Claude Code documents that
explicit ask rules (layer A, AID projects only) still prompt. It does not document whether a
hook's "ask" does. So outside AID projects, and for the breather installer and
`init-project.sh` in every folder, do not count on a prompt in that mode.

## The three layers

| Layer | What it does | What it guarantees |
|-------|--------------|--------------------|
| **A. Permission deny rules** | At session start AID adds deny rules for its control files to the project's `.claude/settings.json`: `Edit(/.aid/hooks/**)`, `Edit(/.aid/pipeline/ESCALATION.json)`, `Edit(/.claude/settings.json)`, `Edit(/.claude/settings.local.json)` and `Edit(/.claude/hooks/**)`. `.aid/state.json` is deliberately NOT in this list: Claude Code merges `Edit` deny paths into the sandbox's `denyWrite`, which would stop AID's own `aid_session.py` from writing it. `state.json` is protected instead by layer C (the Write and Bash gates, in every phase and at every level) plus the ask rules. AID also adds **ask** rules for the human-confirmed commands (`aid_session.py approve`, `advance`, `jump`, `init` including `init --repair`, `memory-sync`, `memory-apply`, `reset` and `qa-pass`). These are the second layer: the gate itself already asks for them in every folder (see [Human confirmation](#human-confirmation-ask)), and in AID projects these rules ask again for Bash-tool calls whatever a hook returns, in every permission mode (they are Bash rules and do not cover the PowerShell tool, where the gate's ask is the only layer). In `-p`, headless or dontAsk sessions nobody can answer the prompt, so Claude Code denies these calls: they need an interactive session. | Claude Code applies these rules itself, whatever any hook returns: "PreToolUse hook decisions don't bypass permission rules" ([permissions](https://code.claude.com/docs/en/permissions.md#precedence-among-rules-hooks-and-mods)). They cover the Write and Edit tools, file commands Claude Code recognises in Bash (`cat`, `head`, `tail`, `sed`, `tee`) and redirect targets (`>`, `>>`, `2>`). One caveat from the same page: a Claude Code mod that you install can approve a call that these rules would ask about, so install only mods you trust. |
| **B. Integrity baseline** | At session start AID records the gate configuration and the deny and ask rules (under `~/.aid/integrity/`, or `$AID_HOME/integrity/`). Every gated call compares them with that record. If AID's `.aid` folder disappears mid-session, Claude's writes and commands are refused until the folder is restored, or until you resume the session, run `/clear` or restart Claude Code. | A change made mid-session that would switch a gate off is denied on the next call, at the level the session started with. |
| **C. The Write and Bash gates** | By default, before Phase 4, writes are allowed only under `docs/`, `.aid/`, `.claude/` (not its `skills`, `agents`, `commands`, `output-styles`, `rules` or `hooks` folders), `features/`, `testing/` and `tests/`, Bash is limited to an allow-list of commands that do not run project code (`ls`, `cat`, `grep`, `git status`/`log`/`diff`/`add`/`commit`, `mkdir` and similar), and PowerShell commands are refused, except the exact forms the gate asks about (see below). The project can change these lists in `phase_gate_rules`. In every phase and at every level, writes to the control files (the files above, the project `.aid/state.json`, QA markers under `.aid/qa/` (`*.qa-passed`, `*-review*.json`), your user-level `~/.claude/settings.json`, and Claude Code's `plugins/known_marketplaces.json` and `plugins/installed_plugins.json`) are refused. The only writer of `.aid/state.json` is AID's `aid_session.py`, run as one plain Bash command. | Out-of-phase work by a cooperating agent is refused, with a reason that tells it what to do instead. Claude cannot use the Write tool to rewrite AID's configuration. |

The Write gate sees every file-editing tool: Write, Edit, MultiEdit and NotebookEdit. For
NotebookEdit it checks `notebook_path`, and when a call carries both `file_path` and
`notebook_path` it checks both. The Bash gate also sees the PowerShell tool.

### The PowerShell tool

On Windows with Git Bash and a claude.ai or Console account, Claude Code's PowerShell tool
"is on by default", and "When the tool is enabled, Claude treats PowerShell as the primary
shell" ([tools reference](https://code.claude.com/docs/en/tools-reference.md#powershell-tool)).
On Windows without Git Bash it is enabled automatically and is the only shell. On Linux,
macOS and WSL it is opt-in. Since 3.0.8 AID's command gate handles it with its own rules:

- **By default (`phase_gate_bash` at `block`), no PowerShell command runs before Phase 4
  without a prompt.** Every PowerShell command is refused then, except the canonical call of
  a confirmed `aid_session.py` subcommand and the exact forms of the breather installer and
  `init-project.sh` (next bullet), which are asked: they run only after you confirm them.
  AID's read-only list is defined in bash syntax, and PowerShell reads the same text
  differently. Claude uses the Bash tool for read-only commands, or the Read, Grep and Glob
  tools. On Windows without Git Bash there is no Bash tool
  ([hooks](https://code.claude.com/docs/en/hooks.md#powershell)), so before Phase 4 Claude
  has no shell; you can still run commands yourself with `!`.
- **A PowerShell command that is exactly the canonical call of a confirmed `aid_session.py`
  subcommand** to an installed AID plugin gets "ask" from the gate itself, in any folder.
  So does the exact form of the breather installer
  (`node "<plugin>/integrations/breather/install.mjs" [args]`) and of
  `bash "<plugin>/scripts/init-project.sh" [args]` for an installed AID plugin, in every
  folder, phase and level, as from the Bash tool; other spellings of these two scripts are
  not asked. Claude Code's ask rules are per tool: "a `Bash` rule doesn't restrict the
  PowerShell tool" (same page), so the gate's own ask is what makes Claude Code prompt you
  there.
- **Every other PowerShell command that mentions `aid_session` is refused in an AID
  project, in every phase and at every level** (even one that only reads the file). In a
  folder without AID, a non-canonical confirmed call is refused and other PowerShell
  commands are allowed. Claude runs these commands with the Bash tool, or you type them with
  `!`. This check is best effort. Refused in every folder: a confirmed call whose
  subcommand is built at run time (`$(...)`, `$env:`, `[char]`, a `( )` expression, a
  variable), a script path written out inside a `( )` expression
  (`python ("<plugin>/hooks/aid_session.py") approve`) or joined from quoted parts there
  (`python ('aid_sess'+'ion.py') approve`), and a script name found with `Get-ChildItem` and
  a wildcard. Other run-time-built script names are not always caught. Some
  forms are not caught outside AID projects, for example a script operand that is only a
  variable (`python $env:SCRIPT reset`), a name looked up with `Get-Command`, or the script
  path held in a variable (`$s="<plugin>/hooks/aid_session.py"; python $s approve`). In an
  AID project the rule above refuses the `Get-Command` form, the variable that holds the
  path and any other form whose text names `aid_session`. A name built with `[char]` inside
  a `( )` expression (`python ("<plugin>/hooks/aid_"+[char]115+"ession.py") approve`) does
  not name it: it runs without a prompt outside AID projects, and in an AID project from
  Phase 4 on, or at `log` or `warn`; it is refused only before Phase 4 at `block`, where
  every PowerShell command is. A bare variable operand does not name it: in
  an AID project it is refused only before Phase 4 at `block` (where every PowerShell
  command is), and from Phase 4 on, or at `log` or `warn`, it runs without a prompt.
  What it cannot see at all is indirection that leaves no
  trace in the command, such as a wrapper script or a copy of `aid_session.py`: outside AID
  projects, and in an AID project from Phase 4 on or at `log` or `warn`, such a call runs
  without a prompt.
- **From Phase 4 on**, a PowerShell command whose text names a control file is refused, even
  one that only reads it (Claude can read with the Read tool or Bash). This is best effort,
  as for Bash: a path built at run time is not caught.

### Agents, commands and untrusted content

- **Every AID agent declares its tools.** The 7 reviewers, validators and scorers have only
  Read, Grep and Glob; `visual-qa-agent` adds only the chrome-devtools browser tools.
  `aid-test-agent` is not a reviewer: it is the `/aid-test` test runner and has write tools
  (Read, Write, Edit, Bash, Grep, Glob), as do the builders `developer` and `test-engineer`. An
  agent without a `tools:` line, and the built-in `general-purpose` agent, would have every
  tool ([sub-agents](https://code.claude.com/docs/en/sub-agents.md)).
- **Agents are spawned by name** (`aid:<agent>`, with the bare name as a fallback in a repo
  checkout), so each runs with its own tool list. The autoresearch scorer has no
  fallback: if `aid:reflection-agent` does not resolve, the step stops, because a bare name
  could pick a project's own copy as the judge.
- **Human-only commands.** `/phase-approve`, `/phase-advance`, `/setup`, `/start-project`,
  `/link-project`, `/aid-reset`, `/breather-start`, `/breather-stop`, `/yolo` and
  `/yolo-off` set `disable-model-invocation: true`: Claude cannot run them on its own; you
  type them ([skills](https://code.claude.com/docs/en/skills.md)).
- **Untrusted content.** `rules/general/untrusted-content.md` tells agents that web pages,
  Jira, GitHub and MCP results are data, never instructions. This is guidance for the model,
  not enforcement; the limits above are what holds.

## What AID does not promise

These limits are accepted on purpose. The next section lists what covers them.

- **Code from Phase 4 onwards can do anything.** A script Claude runs (Node, Python, a
  test) opens files itself. Claude Code's deny rules do not apply "to arbitrary
  subprocesses that read or write files indirectly, like a Python or Node script"
  ([permissions](https://code.claude.com/docs/en/permissions.md#read-and-edit)). That
  includes deleting both `.aid/` and the integrity records. AID's Phase 4+ check of Bash
  commands that name a control file is best effort. If you lower `phase_gate_bash` to
  `warn` or `log`, code can run from Phase 0, so this limit applies from then on.
  PowerShell commands have the same limit: from Phase 4, or from Phase 0 if
  `phase_gate_bash` is lowered, AID's check of a PowerShell command that names a control
  file is best effort. The Claude Code docs do not say whether
  `Edit` deny rules or redirect checks apply to PowerShell commands, so AID does not count
  on them there.
- **From Phase 4, a project's `.claude/skills`, `.claude/agents` and `.claude/commands`
  are writable.** Before Phase 4 the Write and Bash gates refuse writes into
  `.claude/{skills,agents,commands,output-styles,rules,hooks}/`. From Phase 4 on they are
  ordinary project folders, so Claude (or project code) can add a skill, agent or command
  that a later session loads. `.claude/hooks/` stays a control file in every phase.
- **Interpreters resolve from `PATH` (accepted).** AID's hooks and confirmed commands start
  `python`, `node` and `bash` by name, so whichever one comes first on `PATH` runs. Whoever
  can change your `PATH` or put a binary ahead of the real one can run code in their place.
  AID does not pin interpreter paths; keep your `PATH` under your own control.
- **QA passes stop a cooperating agent.** In Phase 4 the QA Stop gate keeps a task from
  ending until `aid_session.py qa-pass` (which you confirm) records a pass for the task's
  current criteria file in `.aid/state.json`. QA marker and review files under `.aid/qa/`
  are control files and are ignored by the gate. From Phase 4, project code can still write
  files, so this is a guardrail like the others.
- **A project can change what the reviewers judge against.** The pipeline gives its
  reviewers the plugin's code-review standard and test-review checklist, but a project's
  own `.claude/skills/code-review/` or `test-driven` skill replaces them, and a project
  `.claude/skills/autoresearch` can replace that skill's bundle. This is accepted on
  purpose (projects may set their own standards). The reviewer agents, their tools and the
  autoresearch scorer stay the plugin's.
- **`cp` and `mv` into a protected file.** Claude Code does not document that `Edit` deny
  rules cover these commands, so AID makes no such claim. AID's own Bash gate refuses them
  before Phase 4, and from Phase 4 only as part of the best-effort check.
- **`disableAllHooks`.** A settings file that sets `disableAllHooks: true` turns off user,
  project, local and plugin hooks, AID included, once Claude Code applies it
  ([settings](https://code.claude.com/docs/en/settings-reference.md#disableallhooks)). AID
  checks the project's `.claude/settings.json` and `.claude/settings.local.json` and refuses
  tool calls while such a change is pending there. Layer A stops Claude from writing those
  two files. For the user-level file, and to keep AID running whatever it says, see
  managed settings below.
- **Your user-level `~/.claude/settings.json`.** A deny rule in a project cannot protect a
  file outside that project. AID's Write gate refuses the Write tool there, but a Phase 4+
  script is not stopped. Use the sandbox or managed settings.

## Stronger options (recommended)

### The Claude Code sandbox (macOS, Linux, WSL2)

We recommend turning on Claude Code's sandbox wherever it is available. It confines shell
commands, and the processes they start, at the OS level. Phase 4+ code then cannot write
the paths you deny, unless a command runs outside the sandbox. "The sandbox runs on macOS,
Linux, and WSL2. On native Windows, Claude Code runs commands unsandboxed". On Windows,
run Claude Code inside WSL2 to get it ([sandboxing](https://code.claude.com/docs/en/sandboxing.md)).

The sandbox "covers shell commands only". The Write and Edit tools stay under the
permission rules (layer A), so the two complement each other. Put this in the project's
`.claude/settings.json`:

```json
{
  "sandbox": {
    "enabled": true,
    "allowUnsandboxedCommands": false,
    "filesystem": {
      "denyWrite": [
        "./.aid/hooks",
        "./.aid/pipeline/ESCALATION.json",
        "./.claude/settings.json",
        "./.claude/settings.local.json",
        "./.claude/hooks",
        "~/.aid/integrity",
        "~/.claude/settings.json"
      ]
    }
  }
}
```

- `allowUnsandboxedCommands: false` stops Claude from retrying a refused command outside the
  sandbox.
- To stop commands from running unsandboxed when the sandbox cannot start, also set
  `"sandbox": {"failIfUnavailable": true}`. Put it in your own `~/.claude/settings.json`
  (macOS, Linux, WSL) or in managed settings, **not** in the shared project file. On a
  platform without the sandbox, such as native Windows, Claude Code does not start with
  this key on, so in the project file it would lock out teammates on native Windows.
- Some commands still run outside the sandbox: those you list in `excludedCommands`, and
  those you type yourself at the `!` prompt.
- Do **not** add `.aid/state.json` to `denyWrite`. AID's own `aid_session.py` writes it
  as a Bash command (after you confirm a phase change), so it runs inside the sandbox.
- On Linux and WSL2, a `denyWrite` entry for a path that does not exist yet has no effect,
  so create the paths first.
- Sandbox paths do not use the permission-rule syntax. In project settings, `./` (or no
  prefix) means the project root, `~/` means your home, and `/` or `//` means an absolute
  path ([sandbox path prefixes](https://code.claude.com/docs/en/settings-reference.md#sandbox-path-prefixes)).
- Claude Code also adds the paths from your `Edit(...)` deny rules (layer A) to `denyWrite`,
  and it protects `.claude` settings and hooks by default. The project entries above
  repeat that on purpose. `~/.aid/integrity` is the entry that adds new protection.

### Managed settings (organisations)

Managed settings are the one level that no project or user file can override: "Nothing in
your own settings files or --settings overrides a managed key"
([settings](https://code.claude.com/docs/en/settings.md#settings-precedence)). The file
locations are listed in the
[managed settings docs](https://code.claude.com/docs/en/managed-settings.md):

| OS | File |
|----|------|
| macOS | `/Library/Application Support/ClaudeCode/managed-settings.json` |
| Linux and WSL | `/etc/claude-code/managed-settings.json` |
| Windows | `C:\Program Files\ClaudeCode\managed-settings.json` |

The first two keys below apply when AID is installed as a plugin (`claude plugin install
aid@AID`). With a clone + `link-project` install, AID's hooks come from project settings:
deploy them in managed settings instead, or switch to the plugin.

Recommended keys:
- **Force-enable AID** with managed `enabledPlugins`, for example
  `{"enabledPlugins": {"aid@AID": true}}`. Hooks from a plugin that managed settings
  force-enable keep running even when a user or project file sets `disableAllHooks`
  ([settings](https://code.claude.com/docs/en/settings-reference.md#disableallhooks)).
- **`allowManagedHooksOnly`**: only hooks the organisation deploys run, plus plugins that
  managed settings force-enable
  ([settings](https://code.claude.com/docs/en/settings-reference.md#allowmanagedhooksonly)).
  **Set it only together with the force-enable above.** Otherwise it switches AID's hooks
  off too.
- **Managed `permissions.deny` rules**, for example to protect `~/.claude/settings.json`.
  Managed rules use `~/` or `//` paths, because a `/` path anchors at a directory tied to
  the settings source ([permissions](https://code.claude.com/docs/en/permissions.md#where-a-pattern-anchors)).
- **The sandbox settings above**, so that no project can turn them off.

## Reporting a problem

See [SECURITY.md](../SECURITY.md).
