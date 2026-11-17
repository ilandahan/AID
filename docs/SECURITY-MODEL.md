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
is one with `.aid/state.json` or `.aid/hooks/config.json`. Folders without AID are never
touched.

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
Phase 4. **Writes to AID's control files are refused at every level and in every phase.**
Only you should change the config file. When you lower a gate, the next session warns that
enforcement is weaker than in the previous session.

## The three layers

| Layer | What it does | What it guarantees |
|-------|--------------|--------------------|
| **A. Permission deny rules** | At session start AID adds deny rules for its control files to the project's `.claude/settings.json`: `Edit(/.aid/hooks/**)`, `Edit(/.aid/pipeline/ESCALATION.json)`, `Edit(/.claude/settings.json)`, `Edit(/.claude/settings.local.json)` and `Edit(/.claude/hooks/**)`. | Claude Code applies these rules itself, whatever any hook returns: "PreToolUse hook decisions don't bypass permission rules" ([permissions](https://code.claude.com/docs/en/permissions.md#precedence-among-rules-hooks-and-mods)). They cover the Write and Edit tools, file commands Claude Code recognises in Bash (`cat`, `head`, `tail`, `sed`, `tee`) and redirect targets (`>`, `>>`, `2>`). |
| **B. Integrity baseline** | At session start AID records the gate configuration and the deny rules (under `~/.aid/integrity/`, or `$AID_HOME/integrity/`). Every gated call compares them with that record. If AID's `.aid` folder disappears mid-session, Claude's writes and commands are refused until the folder is restored, or until you resume the session, run `/clear` or restart Claude Code. | A change made mid-session that would switch a gate off is denied on the next call, at the level the session started with. |
| **C. The Write and Bash gates** | By default, before Phase 4, writes are allowed only under `docs/`, `.aid/`, `.claude/`, `features/`, `testing/` and `tests/`, and Bash is limited to an allow-list of commands that do not run project code (`ls`, `cat`, `grep`, `git status`/`log`/`diff`/`add`/`commit`, `mkdir` and similar). The project can change these lists in `phase_gate_rules`. In every phase and at every level, writes to the control files (the files above plus your user-level `~/.claude/settings.json`) are refused. | Out-of-phase work by a cooperating agent is refused, with a reason that tells it what to do instead. Claude cannot use the Write tool to rewrite AID's configuration. |

## What AID does not promise

These limits are accepted on purpose. The next section lists what covers them.

- **Code from Phase 4 onwards can do anything.** A script Claude runs (Node, Python, a
  test) opens files itself. Claude Code's deny rules do not apply "to arbitrary
  subprocesses that read or write files indirectly, like a Python or Node script"
  ([permissions](https://code.claude.com/docs/en/permissions.md#read-and-edit)). That
  includes deleting both `.aid/` and the integrity records. AID's Phase 4+ check of Bash
  commands that name a control file is best effort. If you lower `phase_gate_bash` to
  `warn` or `log`, code can run from Phase 0, so this limit applies from then on.
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
