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
import argparse
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Project root = where .aid/ lives. Hooks are invoked with cwd = project root.
PROJECT_ROOT = Path.cwd()
STATE_FILE = PROJECT_ROOT / ".aid" / "state.json"
CONTEXT_FILE = PROJECT_ROOT / ".aid" / "context.json"
HOOKS_CONFIG_FILE = PROJECT_ROOT / ".aid" / "hooks" / "config.json"
AUDIT_DIR = PROJECT_ROOT / ".aid" / "audit"
AUDIT_FILE = AUDIT_DIR / "tool-usage.jsonl"
ERROR_LOG = AUDIT_DIR / "errors.log"
MARKERS_DIR = PROJECT_ROOT / ".aid" / "markers"
REFLECTION_MARKER = MARKERS_DIR / "reflection-ran.marker"

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
    "allowed_bash_commands_all_phases": [
        "git", "ls", "cat", "head", "tail", "find", "grep", "rg",
        "npm install", "pip install", "echo", "pwd", "date", "wc",
        "mkdir", "cp", "mv", "touch", "dir", "type", "where",
    ],
    "blocked_bash_patterns_pre_phase4": [
        "npm run", "npm start", "npm test", "node ", "python ",
        "python3 ", "npx ", "tsx ", "ts-node ", "jest ", "vitest ",
        "playwright ", "cucumber",
    ],
}

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
    config = load_json(HOOKS_CONFIG_FILE) or {}
    enforcement = dict(DEFAULT_ENFORCEMENT)
    enforcement.update(config.get("enforcement", {}))
    rules = dict(DEFAULT_PHASE_RULES)
    rules.update(config.get("phase_gate_rules", {}))
    return {"enforcement": enforcement, "phase_gate_rules": rules}


def get_enforcement_level(config, hook_name):
    """Get severity level for a hook: 'log', 'warn', or 'block'."""
    level = config["enforcement"].get(hook_name, "log")
    if level not in ("log", "warn", "block"):
        return "log"
    return level


def now_iso():
    """Current UTC timestamp in ISO format."""
    return datetime.now(timezone.utc).isoformat()

# ---------------------------------------------------------------------------
# Utility: Audit logging
# ---------------------------------------------------------------------------

def audit_log_entry(entry):
    """Append a JSONL entry to the audit log."""
    try:
        AUDIT_DIR.mkdir(parents=True, exist_ok=True)
        entry["timestamp"] = now_iso()
        with open(AUDIT_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, default=str) + "\n")
    except OSError:
        pass  # Non-critical -- never block on audit failure


def log_error(msg):
    """Log an error for debugging."""
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
        # Path is not under project root or can't be resolved --
        # return as-is with forward slashes
        return file_path.replace("\\", "/")

# ---------------------------------------------------------------------------
# Utility: Marker files
# ---------------------------------------------------------------------------

def write_marker(name):
    """Write a marker file with a timestamp."""
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
    clear_markers()

    state = load_state()
    context = load_context()

    audit_log_entry({
        "event": "SessionStart",
        "source": input_data.get("source", "unknown"),
        "phase": state.get("current_phase") if state else None,
        "role": state.get("current_session", {}).get("role") if state else None,
    })

    if not state:
        output_allow(
            "NOTE: No AID state found (.aid/state.json missing). "
            "Run /aid-start to initialize your AID session with role and phase selection."
        )
        return

    session = state.get("current_session", {})
    if not session.get("active"):
        output_allow(
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
    output_allow("\n".join(lines))


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
# Handler: PreToolUse (Write|Edit) -> Phase Gate for Code Writes
# ---------------------------------------------------------------------------

def handle_phase_gate_write(input_data, config):
    """
    Block source code writes in phases before code_write_min_phase.
    Allow writes to docs/, .aid/, .claude/, features/, testing/.
    """
    state = load_state()
    if not state:
        output_allow()  # AID not initialized -- don't block
        return

    phase = state.get("current_phase")
    if phase is None:
        output_allow()
        return

    # Coerce to int (state.json may store as string)
    try:
        phase = int(phase)
    except (ValueError, TypeError):
        output_allow()
        return

    rules = config["phase_gate_rules"]
    min_phase = rules.get("code_write_min_phase", 4)

    if phase >= min_phase:
        output_allow()  # In coding phase -- allow everything
        return

    # Phase < min_phase -- check if this is an allowed path
    file_path = input_data.get("tool_input", {}).get("file_path", "")
    rel_path = normalize_path(file_path)

    allowed_prefixes = rules.get("allowed_write_prefixes", [])
    for prefix in allowed_prefixes:
        if rel_path.startswith(prefix):
            output_allow()  # Writing to allowed path
            return

    # Also allow the plan file (Claude Code creates these in ~/.claude/plans/)
    if ".claude/plans/" in file_path.replace("\\", "/"):
        output_allow()
        return

    # VIOLATION: writing source code in a pre-coding phase
    level = get_enforcement_level(config, "phase_gate_write")
    tool_name = input_data.get("tool_name", "Write")
    message = (
        "Phase gate violation. Cannot {} '{}' in "
        "Phase {} ({}). "
        "Source code changes require Phase {} (Development). "
        "Allowed paths: {}. "
        "Use /gate-check to verify readiness, then /phase-advance.".format(
            tool_name.lower(), rel_path,
            phase, state.get("phase_name", "?"),
            min_phase, ", ".join(allowed_prefixes)))

    enforce(level, message, {
        "event": "PreToolUse",
        "hook": "phase_gate_write",
        "tool": tool_name,
        "file": rel_path,
        "phase": phase,
        "violation": True,
    })


# ---------------------------------------------------------------------------
# Handler: PreToolUse (Bash) -> Phase Gate for Code Execution
# ---------------------------------------------------------------------------

def handle_phase_gate_bash(input_data, config):
    """
    Block code execution commands in phases before code_execute_min_phase.
    Always allow read-only commands (git, ls, etc.) and package installation.

    Edge cases:
    - Piped commands: "cat file.ts | node" -> caught by "node " pattern
    - Chained commands: "echo hi && npm run dev" -> caught by "npm run" pattern
    - Quoted args: 'python "script.py"' -> caught by "python " pattern
    - Empty command: "" -> allowed (no-op)
    """
    state = load_state()
    if not state:
        output_allow()
        return

    phase = state.get("current_phase")
    try:
        phase = int(phase)
    except (ValueError, TypeError):
        output_allow()
        return

    rules = config["phase_gate_rules"]
    min_phase = rules.get("code_execute_min_phase", 4)

    if phase >= min_phase:
        output_allow()
        return

    command = input_data.get("tool_input", {}).get("command", "")
    if not command.strip():
        output_allow()
        return

    # Normalize: lowercase for matching, strip leading whitespace
    cmd_lower = command.strip().lower()

    # Check allowed commands first (fail-open pattern)
    allowed = rules.get("allowed_bash_commands_all_phases", [])
    for allowed_cmd in allowed:
        # Match if command starts with allowed command
        # e.g., "git status" starts with "git"
        if cmd_lower.startswith(allowed_cmd.lower()):
            output_allow()
            return

    # Check blocked patterns (substring match catches piped/chained commands)
    blocked = rules.get("blocked_bash_patterns_pre_phase4", [])
    for pattern in blocked:
        if pattern.lower() in cmd_lower:
            # VIOLATION: executing code in a pre-coding phase
            level = get_enforcement_level(config, "phase_gate_bash")
            # Truncate command for display (may be very long)
            cmd_display = command[:100] + ("..." if len(command) > 100 else "")
            message = (
                "Phase gate violation. Cannot execute '{}' in "
                "Phase {} ({}). "
                "Code execution requires Phase {} (Development). "
                "Allowed: {}... "
                "Use /gate-check to verify readiness.".format(
                    cmd_display,
                    phase, state.get("phase_name", "?"),
                    min_phase,
                    ", ".join(allowed[:8])))

            enforce(level, message, {
                "event": "PreToolUse",
                "hook": "phase_gate_bash",
                "command": command[:200],
                "blocked_pattern": pattern,
                "phase": phase,
                "violation": True,
            })
            return  # enforce() calls sys.exit, but being explicit

    # Unrecognized command -- fail-open (allow)
    output_allow()


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
    global EVENT
    EVENT = args.event

    # Read stdin (hook input data)
    try:
        input_data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        input_data = {}

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
        # Catch-all: never crash -- log and allow. Allowing is silence + exit 0; a hook
        # that fails must not become a hook that blocks the user's work.
        log_error("Unhandled exception: {}: {}".format(type(e).__name__, e))
        sys.exit(0)
