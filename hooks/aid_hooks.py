#!/usr/bin/env python3
"""
AID Hooks Enforcement Dispatcher

Central dispatcher for all AID methodology hooks.
Receives hook event data on stdin, reads AID state files,
applies enforcement rules, and returns JSON decisions.

Usage:
  python aid_hooks.py --event <EventName> [--action <action>]

Events: SessionStart, UserPromptSubmit, PreToolUse, PostToolUse, Stop
Actions: phase_gate_write, phase_gate_bash, audit_log, quality_check
"""

import sys
import json
import os
import re
import argparse
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

sys.path.insert(0, str(Path(__file__).resolve().parent))
import aid_guard  # noqa: E402  (bundled beside this file)


def set_project_root(root):
    """Point every project path at root (the directory that holds .aid/)."""
    global PROJECT_ROOT, STATE_FILE, CONTEXT_FILE, HOOKS_CONFIG_FILE, AUDIT_DIR, AUDIT_FILE
    global ERROR_LOG, MARKERS_DIR, REFLECTION_MARKER
    PROJECT_ROOT = Path(root)
    STATE_FILE = PROJECT_ROOT / ".aid" / "state.json"
    CONTEXT_FILE = PROJECT_ROOT / ".aid" / "context.json"
    HOOKS_CONFIG_FILE = PROJECT_ROOT / ".aid" / "hooks" / "config.json"
    AUDIT_DIR = PROJECT_ROOT / ".aid" / "audit"
    AUDIT_FILE = AUDIT_DIR / "tool-usage.jsonl"
    ERROR_LOG = AUDIT_DIR / "errors.log"
    MARKERS_DIR = PROJECT_ROOT / ".aid" / "markers"
    REFLECTION_MARKER = MARKERS_DIR / "reflection-ran.marker"


def is_aid_root(d):
    """
    AC-27: a directory is an AID project root only if its .aid/ holds state.json or
    hooks/config.json, and that .aid/ is not the user-level AID_HOME (default ~/.aid).
    A stray .aid/ holding only audit/ or qa/ does not make a project an AID project.
    """
    aid = Path(d) / ".aid"
    if not ((aid / "state.json").is_file() or (aid / "hooks" / "config.json").is_file()):
        return False
    # A home directory is never an AID project: its .aid/ is the user-level session dir.
    # Check AID_HOME, $HOME/$USERPROFILE AND the account's real profile, because a moved
    # AID_HOME or a faked HOME would otherwise turn the real ~ into a gated "project" and
    # let SessionStart rewrite ~/.claude/settings.json (review T1-fix1 MAJOR).
    user_aids = [os.environ.get("AID_HOME") or str(Path.home() / ".aid")]
    user_aids += [os.path.join(h, ".aid") for h in (str(Path.home()), _account_home()) if h]
    key = aid_guard._key(os.path.realpath(str(aid)))
    return all(key != aid_guard._key(os.path.realpath(u)) for u in user_aids)


def _account_home():
    """The logged-in account's profile dir, ignoring HOME/USERPROFILE overrides."""
    try:
        if os.name == "nt":
            import ctypes
            import uuid
            guid = (ctypes.c_byte * 16).from_buffer_copy(
                uuid.UUID("{5E6C858F-0E22-4760-9AFE-EA3317B67173}").bytes_le)   # FOLDERID_Profile
            buf = ctypes.c_wchar_p()
            if ctypes.windll.shell32.SHGetKnownFolderPath(ctypes.byref(guid), 0, None, ctypes.byref(buf)):
                return None
            try:
                return buf.value
            finally:
                ctypes.windll.ole32.CoTaskMemFree(buf)
        import pwd
        return pwd.getpwuid(os.getuid()).pw_dir
    except Exception:
        return None


def resolve_project_root(input_data):
    """
    The AID project this call belongs to (audit MAJOR 4: a session that cd'ed into a
    subfolder must still be gated). $CLAUDE_PROJECT_DIR when it is an AID root, else the
    nearest AID-root ancestor of the call's cwd, else the cwd itself (AID not in use).

    AC-43 session latch (the ONE place it lives): an ancestor that is not an AID root but
    holds this session's layer-B baseline written by SessionStart
    (aid_guard.integrity_dir(d)/<session_id>.json with session_start) was the AID root when
    the session began and lost its markers (.aid renamed or deleted mid-session). A
    first-use baseline layer B wrote for a root the session only visited does not latch. It is still this session's root; LATCHED tells layer B to refuse.
    The latch is checked first, over $CLAUDE_PROJECT_DIR and every cwd ancestor, so
    neither a cwd outside the root nor a fresh nearer .aid can step around it.
    """
    global LATCHED
    LATCHED = False
    env_dir = os.environ.get("CLAUDE_PROJECT_DIR")
    data = input_data if isinstance(input_data, dict) else {}
    cwd, sid = data.get("cwd"), data.get("session_id")
    start = Path(cwd) if isinstance(cwd, str) and cwd else Path.cwd()
    walk = [start] + list(start.parents)
    if isinstance(sid, str) and aid_guard._SESSION_ID.fullmatch(sid):
        for d in ([Path(env_dir)] if env_dir else []) + walk:
            if aid_guard.started_at(d, sid) and not is_aid_root(d):
                LATCHED = True
                return d
    if env_dir and is_aid_root(env_dir):
        return Path(env_dir)
    for d in walk:
        if is_aid_root(d):
            return d
    return start


LATCHED = False   # set by resolve_project_root: root lost its AID markers mid-session


set_project_root(Path.cwd())

DEFAULT_ENFORCEMENT = {
    "phase_gate_write": "log",
    "phase_gate_bash": "log",
    "quality_check_verifier": "log",
    "session_reminder": "log",
    "context_injector": "log",
    "audit_logger": "log",
}

DEFAULT_PHASE_RULES = {
    "code_write_min_phase": 4,
    "code_execute_min_phase": 4,
    "allowed_write_prefixes": ["docs/", ".aid/", ".claude/", "features/", "testing/", "tests/"],
    # Bash before Phase 4 (block mode) is a small READ-ONLY allow-list (aid_guard._pre4:
    # aid_guard.READ_ONLY, GIT_OPTIONS, mkdir, cd-to-root, --version). Package installs
    # run code and are NOT on it. The human adds exact commands here, e.g.
    # ["make lint", "npm ci"] (first word = command, rest = leading arguments).
    "extra_allowed_commands": [],
}

# The two PreToolUse gates. They fail CLOSED in block mode (see fail_closed()).
GATES = ("phase_gate_write", "phase_gate_bash")


class GateInputError(Exception):
    """State, config or hook input a gate cannot trust. Fails closed in block mode."""

# ---------------------------------------------------------------------------
# Utility: File I/O helpers
# ---------------------------------------------------------------------------

def load_json(path):
    """Load a JSON file, return None if missing or invalid."""
    try:
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    except (json.JSONDecodeError, OSError, PermissionError):
        pass
    return None


def load_state():
    """Load .aid/state.json. Returns None if AID not initialized."""
    return load_json(STATE_FILE)


def load_context():
    """Load .aid/context.json."""
    return load_json(CONTEXT_FILE)


def load_hooks_config():
    """Load .aid/hooks/config.json with defaults."""
    config = load_json(HOOKS_CONFIG_FILE)
    if config is None and not HOOKS_CONFIG_FILE.exists():
        config = {}
    malformed = not (
        isinstance(config, dict)
        and isinstance(config.get("enforcement", {}), dict)
        and isinstance(config.get("phase_gate_rules", {}), dict))
    enforcement = dict(DEFAULT_ENFORCEMENT)
    rules = dict(DEFAULT_PHASE_RULES)
    if malformed:
        # A config exists but cannot be read: the author meant to configure enforcement,
        # so the gates fail closed instead of silently dropping to the "log" default.
        log_error("Malformed {}: phase gates forced to block".format(HOOKS_CONFIG_FILE))
        for gate in GATES:
            enforcement[gate] = "block"
    else:
        enforcement.update(config.get("enforcement", {}))
        rules.update(config.get("phase_gate_rules", {}))
    for key in ("code_write_min_phase", "code_execute_min_phase"):
        try:
            rules[key] = int(rules[key])
        except (TypeError, ValueError):
            log_error("{} {!r} is not an integer: using 4".format(key, rules[key]))
            rules[key] = 4
    return {"enforcement": enforcement, "phase_gate_rules": rules}


def get_enforcement_level(config, hook_name):
    """Get severity level for a hook: 'log', 'warn', or 'block' (case-insensitive).

    An unknown value fails closed ('block') for the PreToolUse gates and open ('log')
    for every other hook.
    """
    level = str(config["enforcement"].get(hook_name, "log")).strip().lower()
    if level not in ("log", "warn", "block"):
        return "block" if hook_name in GATES else "log"
    return level


def now_iso():
    """Current UTC timestamp in ISO format."""
    return datetime.now(timezone.utc).isoformat()

# ---------------------------------------------------------------------------
# Utility: Audit logging
# ---------------------------------------------------------------------------

def audit_log_entry(entry):
    """Append a JSONL entry to the audit log (never in a non-AID project: AC-27).
    A latched root (AC-43) still logs while its .aid/audit exists, but never recreates it."""
    if not aid_in_use() and not (LATCHED and AUDIT_DIR.is_dir()):
        return
    try:
        AUDIT_DIR.mkdir(parents=True, exist_ok=True)
        entry["timestamp"] = now_iso()
        with open(AUDIT_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, default=str) + "\n")
    except OSError:
        pass  # Non-critical -- never block on audit failure


def log_error(msg):
    """Log an error for debugging (never in a non-AID project: AC-27)."""
    if not aid_in_use():
        return
    try:
        AUDIT_DIR.mkdir(parents=True, exist_ok=True)
        with open(ERROR_LOG, "a", encoding="utf-8") as f:
            f.write(f"[{now_iso()}] {msg}\n")
    except OSError:
        pass

# ---------------------------------------------------------------------------
# Utility: Path normalization (Windows-aware)
# ---------------------------------------------------------------------------

def normalize_path(file_path):
    """
    Convert an absolute file path to a project-relative path using forward slashes.

    Edge cases handled:
    - Windows backslashes -> forward slashes
    - Paths containing spaces or apostrophes (e.g. "C:\\My Projects\\app\\src")
    - Paths already relative
    - Mixed separators
    """
    if not file_path:
        return ""
    # Normalize to Path object then to relative
    try:
        p = Path(file_path).resolve()
        root = PROJECT_ROOT.resolve()
        rel = p.relative_to(root)
        return str(rel).replace("\\", "/")
    except (ValueError, OSError):
        # Not under the project root (or unresolvable): return the RESOLVED absolute path.
        # Returning the raw input let "docs/../../elsewhere/x.ts" match the "docs/" prefix.
        return os.path.realpath(file_path).replace("\\", "/")


# ---------------------------------------------------------------------------
# Utility: Marker files
# ---------------------------------------------------------------------------

def write_marker(name):
    """Write a marker file with a timestamp."""
    if not aid_in_use():
        return
    try:
        MARKERS_DIR.mkdir(parents=True, exist_ok=True)
        marker = MARKERS_DIR / name
        marker.write_text(now_iso(), encoding="utf-8")
    except OSError:
        pass


def check_marker(name):
    """Check if a marker file exists."""
    return (MARKERS_DIR / name).exists()


def clear_markers():
    """Clear all marker files (called on SessionStart)."""
    try:
        if MARKERS_DIR.exists():
            for f in MARKERS_DIR.iterdir():
                if f.is_file() and f.suffix == ".marker":
                    f.unlink()
    except OSError:
        pass

# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------

# The hook event currently being handled. Set once by main(), read by the helpers below.
#
# WHY a module global: Claude Code requires "hookEventName" inside every
# hookSpecificOutput payload and discards the payload without it. output_allow() has 33
# call sites, so threading the event through each one buys nothing over setting it once.
EVENT = ""


def output_allow(additional_context=""):
    """
    Allow the action, optionally injecting context.

    WHY hookEventName: without it Claude Code cannot route hookSpecificOutput and
    silently drops additionalContext -- which made every SessionStart context injection
    and every "warn" enforcement level a no-op.
    """
    if additional_context:
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": EVENT,
                "additionalContext": additional_context
            }
        }))
    # Allowing with nothing to say = stay silent, exit 0. The old {"ok": true} body was
    # not a shape Claude Code reads.
    sys.exit(0)


def output_deny(reason):
    """
    Deny the action with a reason.

    WHY this exact shape: PreToolUse denials are read from
    hookSpecificOutput.permissionDecision / permissionDecisionReason. The previous payload
    used "decision"/"reason" and omitted hookEventName, so every phase-gate block was
    treated as an allow and the gate never stopped anything.
    """
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": EVENT or "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason
        }
    }))
    sys.exit(0)


def output_stop_block(reason):
    """Block the Stop event (continue working)."""
    print(json.dumps({
        "decision": "block",
        "reason": reason
    }))
    sys.exit(0)

# ---------------------------------------------------------------------------
# Enforcement action (central log/warn/block logic)
# ---------------------------------------------------------------------------

def enforce(level, message, audit_entry, is_stop=False):
    """
    Apply the enforcement action based on severity level.

    level: "log" | "warn" | "block"
    message: human-readable enforcement message
    audit_entry: dict to log
    is_stop: True if this is a Stop event (uses stop_block instead of deny)
    """
    audit_entry["enforcement_level"] = level
    audit_entry["enforcement_message"] = message
    audit_log_entry(audit_entry)

    if level == "log":
        output_allow()
    elif level == "warn":
        output_allow(additional_context="⚠️ AID ENFORCEMENT WARNING: " + message)
    elif level == "block":
        if is_stop:
            output_stop_block(message)
        else:
            output_deny("🚫 AID ENFORCEMENT BLOCK: " + message)

# ---------------------------------------------------------------------------
# Handler: SessionStart -> Context Injector
# ---------------------------------------------------------------------------

def handle_session_start(input_data, config):
    """
    Inject current AID phase/role/skills/task into Claude's context.
    Also clears stale marker files from previous sessions.
    """
    # Layer A then layer B (order matters: the baseline must include the deny rules).
    # Nothing at all is touched outside an AID project (AC-27ext): markers included.
    global LATCHED
    notes = []
    if (LATCHED and input_data.get("source") in aid_guard.LATCH_RELEASE_SOURCES
            and aid_guard.release_latch(PROJECT_ROOT, input_data.get("session_id"))):
        LATCHED = False     # now a plain non-AID project: AC-27 applies from here on
        notes.append("NOTE: AID's markers (.aid/state.json, .aid/hooks/config.json) are gone "
                     "from {} since this session last ran, so AID no longer gates it. If the "
                     "user did not remove AID on purpose, restore the .aid folder."
                     .format(PROJECT_ROOT))
    if aid_in_use():
        clear_markers()
        added, err = aid_guard.ensure_permissions(PROJECT_ROOT)   # AC-38ext: config-only roots too
        if added:
            notes.append("AID added {} permission deny rules to .claude/settings.json "
                         "protecting its gate configuration.".format(added))
        if err:
            notes.append("WARNING: AID could not install its permission deny rules: " + err)
        off = aid_guard.hooks_disabled(PROJECT_ROOT)
        if off:
            notes.append("WARNING: {} -- this switches AID's enforcement off once Claude Code "
                         "applies it. Remove it unless the user set it on purpose.".format(off))
        if input_data.get("source") != "compact":   # compact keeps the session's baseline
            aid_guard.write_baseline(PROJECT_ROOT, input_data.get("session_id"), gate_levels(config),
                                     session_start=True)
            weaker = aid_guard.weakened_since_last_session(PROJECT_ROOT, gate_levels(config))
            if weaker:
                notes.append("WARNING: AID enforcement is weaker than in the last session: {}. "
                             "If the user did not make this change, restore "
                             ".aid/hooks/config.json.".format("; ".join(weaker)))
        env_dir = os.environ.get("CLAUDE_PROJECT_DIR")
        if env_dir and (aid_guard._key(os.path.realpath(env_dir))
                        != aid_guard._key(os.path.realpath(str(PROJECT_ROOT)))):
            notes.append("WARNING: Claude Code was started in {} but the AID project is {}; AID's "
                         "permission rules only apply when Claude Code is started in the AID "
                         "project folder.".format(env_dir, PROJECT_ROOT))

    def say(text):
        output_allow("\n".join(notes + [text]))

    state = load_state()
    context = load_context()

    audit_log_entry({
        "event": "SessionStart",
        "source": input_data.get("source", "unknown"),
        "phase": state.get("current_phase") if state else None,
        "role": state.get("current_session", {}).get("role") if state else None,
    })

    if not state:
        say(
            "NOTE: No AID state found (.aid/state.json missing). "
            "Run /aid-start to initialize your AID session with role and phase selection."
        )
        return

    session = state.get("current_session", {})
    if not session.get("active"):
        say(
            "NOTE: No active AID session. Run /aid-start to select your role and phase."
        )
        return

    # Build rich context string
    phase = state.get("current_phase", "?")
    phase_name = state.get("phase_name", "Unknown")
    role = session.get("role_display", session.get("role", "Unknown"))
    phase_display = session.get("phase_display", phase_name)
    skills = session.get("skills_loaded", [])

    lines = [
        "=== AID SESSION CONTEXT ===",
        "Phase: {} ({})".format(phase, phase_name),
        "Role: {}".format(role),
        "Phase Display: {}".format(phase_display),
        "Skills Loaded: {}".format(", ".join(skills) if skills else "none"),
    ]

    # Add task context if available
    if context:
        task = context.get("current_task", {})
        step = context.get("current_step", {})
        blockers = context.get("blockers", [])
        if task:
            lines.append("\nCurrent Task: {} - {}".format(
                task.get("key", "?"), task.get("title", "?")))
        if step:
            lines.append("Current Step: {}".format(step.get("name", "?")))
        if blockers:
            lines.append("Blockers: {}".format(len(blockers)))
            for b in blockers[:3]:  # show max 3
                lines.append("  - [{}] {}".format(
                    b.get("severity", "?"), b.get("description", "?")[:80]))

    # Add enforcement status
    enforcement = config["enforcement"]
    active_enforcements = [
        "{}: {}".format(k, v) for k, v in enforcement.items() if v != "log"
    ]
    if active_enforcements:
        lines.append("\nENFORCEMENT ACTIVE: {}".format(", ".join(active_enforcements)))

    # Add phase restrictions reminder
    min_phase = config["phase_gate_rules"].get("code_write_min_phase", 4)
    try:
        phase_int = int(phase)
    except (ValueError, TypeError):
        phase_int = 0

    if phase_int < min_phase:
        allowed = ", ".join(config["phase_gate_rules"].get("allowed_write_prefixes", []))
        lines.append(
            "\n⚠️ PHASE RESTRICTION: Code writing/execution NOT allowed until Phase {}. "
            "Allowed write paths: {}".format(min_phase, allowed)
        )

    # Check for active pipeline
    pipeline_state = load_json(PROJECT_ROOT / ".aid" / "pipeline" / "state.json")
    if pipeline_state and pipeline_state.get("pipeline_status") in ("running", "paused"):
        lines.append(
            "\nACTIVE PIPELINE: Task {} at step {} (status: {})".format(
                pipeline_state.get("task_id", "?"),
                pipeline_state.get("current_step", "?"),
                pipeline_state.get("pipeline_status")))

    lines.append("=== END AID CONTEXT ===")
    say("\n".join(lines))


# ---------------------------------------------------------------------------
# Handler: UserPromptSubmit -> Session Reminder / Context Reinforcement
# ---------------------------------------------------------------------------

def handle_user_prompt_submit(input_data, config):
    """
    On every user prompt, inject a lightweight context reminder.
    """
    level = get_enforcement_level(config, "session_reminder")
    state = load_state()

    if not state:
        if level != "log":
            output_allow("NOTE: No AID session active. Run /aid-start to begin.")
        else:
            output_allow()
        return

    session = state.get("current_session", {})
    if not session.get("active"):
        if level != "log":
            output_allow("NOTE: AID session inactive. Run /aid-start to resume.")
        else:
            output_allow()
        return

    # Active session -- inject one-line reinforcement
    phase = state.get("current_phase", "?")
    role = session.get("role_display", session.get("role", "?"))

    context = load_context()
    task_key = ""
    if context:
        task = context.get("current_task", {})
        task_key = task.get("key", "")

    tag = "[AID: Phase {} | {}".format(phase, role)
    if task_key:
        tag += " | Task: {}".format(task_key)
    tag += "]"

    output_allow(tag)


# ---------------------------------------------------------------------------
# Phase-gate helpers: state, fail-closed, shell command parsing
# ---------------------------------------------------------------------------

def load_gate_state(config):
    """
    Return (state, phase) for the PreToolUse gates.

    - state.json unreadable / not an object / non-integer phase -> GateInputError
      (fails closed in block mode).
    - No state.json, or current_phase null: phase None (gates only protect control files)
      -- unless a gate is configured to block, then phase 0: deleting or blanking
      state.json must not switch the gates off (design review MAJOR 3).
    """
    state = load_state()
    blocking = any(get_enforcement_level(config, g) == "block" for g in GATES)
    if state is None:
        if STATE_FILE.exists():
            raise GateInputError("{} exists but is not valid JSON".format(STATE_FILE))
        return None, (0 if blocking else None)
    if not isinstance(state, dict):
        raise GateInputError("{} is not a JSON object".format(STATE_FILE))
    phase = state.get("current_phase")
    if phase is None:
        return state, (0 if blocking else None)
    try:
        return state, int(str(phase).strip())
    except (ValueError, TypeError):
        raise GateInputError("current_phase {!r} is not an integer".format(phase))


ACTION = None  # set by main(); read by fail_closed()


def fail_closed(reason):
    """
    A PreToolUse gate could not evaluate the call. In block mode deny it (fail CLOSED);
    in log/warn mode, and for every other hook, log the error and allow.
    """
    log_error(reason)
    if EVENT == "PreToolUse" and ACTION in GATES:
        try:
            level = get_enforcement_level(load_hooks_config(), ACTION)
        except Exception:  # config unreadable while failing: stay closed
            level = "block"
        if level == "block":
            output_deny("🚫 AID ENFORCEMENT BLOCK: the phase gate could not evaluate "
                        "this call ({}), so it is denied.".format(reason))
    sys.exit(0)


# ---------------------------------------------------------------------------
# Gate plumbing shared by both PreToolUse gates (decision logic lives in aid_guard.py)
# ---------------------------------------------------------------------------

def gate_levels(config):
    return {g: get_enforcement_level(config, g) for g in GATES}


def gate_cwd(input_data):
    """The directory the tool call runs in (Bash cwd persists between calls)."""
    cwd = input_data.get("cwd")
    return cwd if isinstance(cwd, str) and cwd else str(PROJECT_ROOT)


def check_integrity_or_deny(input_data, config, hook_name, phase):
    """Layer B: deny (per the BASELINE's level) when the gate config or deny rules changed."""
    reason, base_levels = aid_guard.check_integrity(
        PROJECT_ROOT, input_data.get("session_id"), gate_levels(config), markers_missing=LATCHED)
    if reason:
        level = base_levels.get(hook_name, get_enforcement_level(config, hook_name))
        enforce(level, reason, {"event": "PreToolUse", "hook": hook_name, "integrity": True,
                                "phase": phase, "violation": True})


def aid_in_use():
    return is_aid_root(PROJECT_ROOT)


# Phase 4+ deny footer, shared by both gates: only control files are refused then.
CONTROL_FILE_HINT = ("AID control files are protected in every phase; edit them only if the "
                     "user asks, and let the user make the change.")


# ---------------------------------------------------------------------------
# Handler: PreToolUse (Write|Edit|MultiEdit|NotebookEdit) -> Phase Gate for Code Writes
# ---------------------------------------------------------------------------

def handle_phase_gate_write(input_data, config):
    """
    Refuse writes to AID control files in every phase, and source writes before
    code_write_min_phase. Allowed before then: docs/, .aid/, .claude/, features/,
    testing/, tests/ and Claude Code's own plan files. Rules: aid_guard.write_target_verdict.
    """
    if not aid_in_use() and not LATCHED:
        output_allow()  # AID not used in this project -- stay out of the way
        return
    # INV-3: layer B before the state is read, so a broken state.json cannot skip it.
    check_integrity_or_deny(input_data, config, "phase_gate_write", None)
    state, phase = load_gate_state(config)

    tool_input = input_data["tool_input"]
    file_path = tool_input.get("file_path") or tool_input.get("notebook_path") or ""
    if not isinstance(file_path, str):
        raise GateInputError("file_path is not a string")
    reason = aid_guard.write_target_verdict(
        file_path, gate_cwd(input_data), PROJECT_ROOT, phase, config["phase_gate_rules"], literal=True)
    if not reason:
        output_allow()
        return

    min_phase = config["phase_gate_rules"].get("code_write_min_phase", 4)
    tool_name = input_data.get("tool_name", "Write")
    if phase is not None and phase < min_phase:
        message = (
            "Phase gate: cannot {} — {}. Phase {} ({}); source changes need Phase {} "
            "(Development). Use /gate-check, then /phase-advance.".format(
                tool_name.lower(), reason, phase, (state or {}).get("phase_name", "?"), min_phase))
    else:
        # Phase 4+: only control files are refused; advancing a phase cannot help.
        message = "Phase gate: cannot {} — {}. {}".format(tool_name.lower(), reason, CONTROL_FILE_HINT)
    enforce(get_enforcement_level(config, "phase_gate_write"), message, {
        "event": "PreToolUse",
        "hook": "phase_gate_write",
        "tool": tool_name,
        "file": file_path[:300],
        "phase": phase,
        "violation": True,
    })


# ---------------------------------------------------------------------------
# Handler: PreToolUse (Bash) -> Phase Gate for Code Execution
# ---------------------------------------------------------------------------

def handle_phase_gate_bash(input_data, config):
    """
    Before code_execute_min_phase (block mode), the command must be a flat list of
    read-only commands (aid_guard.evaluate_bash); anything else is denied. From then on
    only a best-effort literal control-file check runs (layers A and B are the real
    protection). The human extends the pre-Phase-4 list with
    phase_gate_rules.extra_allowed_commands in .aid/hooks/config.json (a protected file).
    """
    if not aid_in_use() and not LATCHED:
        output_allow()
        return
    # INV-3: layer B before the state is read, so a broken state.json cannot skip it.
    check_integrity_or_deny(input_data, config, "phase_gate_bash", None)
    state, phase = load_gate_state(config)

    command = input_data["tool_input"].get("command") or ""
    if not isinstance(command, str):
        raise GateInputError("command is not a string")
    if not command.strip():
        output_allow()
        return

    rules = config["phase_gate_rules"]
    extra = [str(e).split() for e in rules.get("extra_allowed_commands", []) if str(e).strip()]
    reason = aid_guard.evaluate_bash(command, gate_cwd(input_data), str(PROJECT_ROOT), phase,
                                     rules, extra)
    if not reason:
        output_allow()
        return

    min_phase = rules.get("code_execute_min_phase", 4)
    cmd_display = command[:100] + ("..." if len(command) > 100 else "")
    if phase is not None and phase < min_phase:
        message = (
            "Phase gate: '{}' — {}. Phase {} ({}); running code needs Phase {} (Development). "
            "Until then Bash runs only read-only commands (ls, cat, grep, git status/log/diff/"
            "add/commit, mkdir in docs/...). To create or change files use the Write tool. "
            "When this phase's work is done, use /gate-check, then /phase-advance. If the "
            "project needs a specific command earlier, ask the user to add it to "
            "phase_gate_rules.extra_allowed_commands in .aid/hooks/config.json.".format(
                cmd_display, reason, phase, (state or {}).get("phase_name", "?"), min_phase))
    else:
        message = "Phase gate: '{}' — {}. {}".format(cmd_display, reason, CONTROL_FILE_HINT)
    enforce(get_enforcement_level(config, "phase_gate_bash"), message, {
        "event": "PreToolUse",
        "hook": "phase_gate_bash",
        "command": command[:200],
        "reason": reason[:200],
        "phase": phase,
        "violation": True,
    })


# ---------------------------------------------------------------------------
# Handler: PostToolUse -> Audit Logger + Reflection Marker
# ---------------------------------------------------------------------------

def handle_audit_log(input_data, config):
    """
    Log tool usage and detect reflection-agent spawns.
    """
    state = load_state()
    tool_name = input_data.get("tool_name", "?")
    tool_input = input_data.get("tool_input", {})

    entry = {
        "event": "PostToolUse",
        "tool": tool_name,
        "phase": state.get("current_phase") if state else None,
        "role": state.get("current_session", {}).get("role") if state else None,
    }

    # Add tool-specific fields (concise, no full content)
    if tool_name in ("Write", "Edit"):
        file_path = tool_input.get("file_path", "")
        entry["file"] = normalize_path(file_path)
    elif tool_name == "Bash":
        command = tool_input.get("command", "")
        entry["command"] = command[:200]  # Truncate for audit
    elif tool_name == "Agent":
        description = tool_input.get("description", "")
        prompt = tool_input.get("prompt", "")
        entry["agent_description"] = description[:200]

        # Detect reflection-agent spawn -> write marker
        reflection_keywords = ["quality", "reflection", "evaluation", "quality check"]
        combined = (description + " " + prompt).lower()
        if any(kw in combined for kw in reflection_keywords):
            write_marker("reflection-ran.marker")
            entry["reflection_detected"] = True

    audit_log_entry(entry)
    output_allow()


# ---------------------------------------------------------------------------
# Handler: Stop -> Quality Check Verifier
# ---------------------------------------------------------------------------

def handle_quality_check(input_data, config):
    """
    Verify that reflection-agent ran on significant outputs.

    Note: The Stop event does NOT include the assistant's response text.
    We rely on marker files to detect reflection-agent usage.

    If the reflection marker is missing and we're in a phase that
    requires quality checks, apply enforcement.
    """
    # Prevent infinite loops: if stop hook already active, allow
    if input_data.get("stop_hook_active"):
        output_allow()
        return

    state = load_state()
    if not state:
        output_allow()
        return

    session = state.get("current_session", {})
    if not session.get("active"):
        output_allow()
        return

    level = get_enforcement_level(config, "quality_check_verifier")
    if level == "log":
        # In log mode, just record whether reflection ran
        ran = check_marker("reflection-ran.marker")
        audit_log_entry({
            "event": "Stop",
            "hook": "quality_check",
            "reflection_ran": ran,
            "phase": state.get("current_phase"),
        })
        output_allow()
        return

    # In warn/block mode, check for reflection marker
    if check_marker("reflection-ran.marker"):
        audit_log_entry({
            "event": "Stop",
            "hook": "quality_check",
            "reflection_ran": True,
            "phase": state.get("current_phase"),
        })
        output_allow()
        return

    # No reflection marker -- enforce
    message = (
        "Quality check not detected. Per AID methodology, significant outputs "
        "should go through the reflection-agent for quality evaluation. "
        "If you produced a significant output (code, spec, PRD, plan), "
        "please spawn the reflection-agent before completing."
    )

    enforce(level, message, {
        "event": "Stop",
        "hook": "quality_check",
        "reflection_ran": False,
        "phase": state.get("current_phase"),
    }, is_stop=True)


# ---------------------------------------------------------------------------
# Main: Argument parsing and dispatch
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="AID Hooks Dispatcher")
    parser.add_argument("--event", required=True,
                        choices=["SessionStart", "UserPromptSubmit",
                                 "PreToolUse", "PostToolUse", "Stop"],
                        help="Hook event name")
    parser.add_argument("--action", default=None,
                        help="Specific action (e.g., phase_gate_write)")
    args = parser.parse_args()

    # Every hookSpecificOutput payload must name its event or Claude Code drops it.
    global EVENT, ACTION
    EVENT = args.event
    ACTION = args.action

    # Read stdin (hook input data)
    try:
        input_data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        input_data = {}
    if not isinstance(input_data, dict):
        input_data = {}
    set_project_root(resolve_project_root(input_data))

    # Load config
    config = load_hooks_config()

    # Dispatch
    handlers = {
        "SessionStart": handle_session_start,
        "UserPromptSubmit": handle_user_prompt_submit,
        "Stop": {
            "quality_check": handle_quality_check,
        },
        "PreToolUse": {
            "phase_gate_write": handle_phase_gate_write,
            "phase_gate_bash": handle_phase_gate_bash,
        },
        "PostToolUse": {
            "audit_log": handle_audit_log,
        },
    }

    handler = handlers.get(args.event)
    if handler is None:
        output_allow()
        return

    # If handler is a dict, dispatch by action
    if isinstance(handler, dict):
        action_handler = handler.get(args.action)
        if action_handler is None:
            output_allow()
            return
        action_handler(input_data, config)
    else:
        handler(input_data, config)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise  # Let sys.exit() through
    except Exception as e:
        # Catch-all: never crash. A phase gate in block mode fails CLOSED (deny with the
        # reason); every other hook, and the gates in log/warn mode, log and allow.
        fail_closed("{}: {}".format(type(e).__name__, e))
