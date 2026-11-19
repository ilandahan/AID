#!/usr/bin/env python3
"""
QA Gate Enforcement Hook (Stop Hook)

This hook runs when Claude tries to stop/complete a task.
It blocks completion until QA sub-agent review has passed.

ENFORCEMENT FLOW:
1. Claude finishes coding task
2. Claude tries to move to next task or stop
3. This hook fires
4. Checks state.json qa_passed[<task>] (written only by the user-confirmed
   `aid_session.py qa-pass`) against the sha256 of .aid/qa/<task>.yaml (T15, D3)
5. If missing → BLOCKS with "QA required"
6. Claude MUST spawn QA sub-agent
7. After QA passes and the user confirms qa-pass → allows proceeding
In an AID root the gate fails closed: unreadable inputs block (T15-16).
"""

import hashlib
import json
import re
import sys
import os
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent

# T7-7 (A-36, A-24): every path below is under the AID project root, resolved the same way
# as the phase gates (INV-2). Relative to the cwd, a Stop in a subfolder read the wrong
# project and left stray .aid/qa/ folders. Set by main(); None = AID not in use here.
ROOT = None


def aid(*parts):
    return os.path.join(str(ROOT), ".aid", *parts)


def project_root(input_data):
    """The gates' AID project root for this call, or None when AID is not in use."""
    sys.path.insert(0, str(HERE))
    import aid_hooks                      # noqa: E402  (bundled beside this file)
    root = aid_hooks.resolve_project_root(input_data)
    return root if aid_hooks.is_aid_root(root) else None


def log_debug(msg):
    """Write debug info to log file (best effort: a log failure never decides the gate)."""
    try:
        log_file = aid("qa", "enforcement.log")
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().isoformat()}] {msg}\n")
    except OSError:
        pass


class GateError(Exception):
    """T15-16 (A-16): an input the gate cannot trust. In an AID root it BLOCKS (fail closed)."""


# T15 I-2: the same task-id rule aid_session.py qa-pass enforces.
TASK_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")


def read_object(path, what, fix):
    """The JSON object in path, None when the file is missing; GateError when it exists
    but cannot be read or is not a JSON object."""
    if not os.path.lexists(path):
        return None
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError) as e:
        raise GateError(f"cannot read {path} ({e}). {fix}")
    if not isinstance(data, dict):
        raise GateError(f"{path} is not a JSON object. {fix}")
    return data


def read_state():
    return read_object(aid("state.json"), "state",
                       "Ask the user to repair it with `init --repair` (`aid_session.py init <role> "
                       "<phase> --repair`, which the user confirms); do not edit the file.")


def get_current_task():
    """T15 I-3: the first non-empty string of current_task.id, .key, .jira_key, or None.
    T3-6 (A-17, D-06): /context-update writes "id" (older files "key", Jira flows
    "jira_key"); the installers seed "current_task": null."""
    context = read_object(aid("context.json"), "context",
                          "Fix it with /context-update (it rewrites .aid/context.json).")
    if context is None:
        return None
    task = context.get("current_task")
    if task is None:
        return None
    if not isinstance(task, dict):
        raise GateError(f"{aid('context.json')}: current_task is not an object. "
                        "Fix it with /context-update.")
    for field in ("id", "key", "jira_key"):
        value = task.get(field)
        if isinstance(value, str) and value.strip():
            return value
    return None


def criteria_sha256(task_id):
    """sha256 hex of .aid/qa/<task_id>.yaml, None when it does not exist."""
    path = aid("qa", f"{task_id}.yaml")
    if not os.path.isfile(path):
        return None
    try:
        with open(path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except OSError as e:
        raise GateError(f"cannot read the QA criteria file {path} ({e}).")


def check_qa_passed(state, task_id, digest):
    """T15 I-3 (D3, R-07): ONLY a state.json qa_passed record whose criteria_sha256 matches
    the current criteria file passes. The record is written by `aid_session.py qa-pass`,
    which the user confirms; .qa-passed files, *-review*.json files and the legacy
    current_task_qa key are agent-writable and are ignored."""
    passed = state.get("qa_passed")
    record = passed.get(task_id) if isinstance(passed, dict) else None
    return isinstance(record, dict) and record.get("criteria_sha256") == digest


def is_in_development_phase(state):
    """Check if currently in development phase (Phase 4)"""
    return state.get("current_phase") in [4, "4", "development", "Development"]


def qa_pass_command(task_id):
    """T15 I-7: the exact ask-confirmed call, with this plugin's absolute script path."""
    script = (HERE / "aid_session.py").as_posix()
    return f'python "{script}" qa-pass {task_id} --note "<short summary>"'


def block(reason):
    # Stop hook block schema: {"decision": "block", "reason": ...}. The reason is fed
    # back to Claude as the instruction for what to do next.
    print(json.dumps({"decision": "block", "reason": reason}))
    sys.exit(0)


def evaluate():
    """The gate decision for an AID root; returns to allow, calls block() to block."""
    state = read_state()
    if state is None:
        log_debug("No state.json, allowing stop")
        return

    # Only enforce in development phase
    if not is_in_development_phase(state):
        log_debug("Not in development phase, allowing stop")
        return  # allow: silent exit 0 is how a Stop hook approves

    task_id = get_current_task()
    log_debug(f"Current task: {task_id!r}")
    if not task_id:
        log_debug("No task ID found, allowing stop")
        return

    if not TASK_ID_RE.match(task_id) or ".." in task_id:
        raise GateError(f"the current task id {task_id!r} in {aid('context.json')} is not a valid "
                        "task id (letters, digits, . _ -; max 64; no ..). Fix it with /context-update.")

    # Check if this task has QA criteria (if not, no gate needed)
    digest = criteria_sha256(task_id)
    if digest is None:
        log_debug(f"No QA criteria file for {task_id}, allowing stop")
        return

    if check_qa_passed(state, task_id, digest):
        log_debug(f"QA PASSED for {task_id}, allowing stop")
        return

    log_debug(f"QA NOT PASSED for {task_id}, BLOCKING stop")
    block(f"""QA Gate BLOCKED: task {task_id} requires QA validation before you stop.

ACTION REQUIRED:
1. Spawn the QA validator sub-agent:

   Task(
     subagent_type="qa-validator-agent",
     prompt="Validate task {task_id}. Criteria: .aid/qa/{task_id}.yaml",
     description="QA validation for {task_id}"
   )

2. If it returns FAIL, fix the issues and re-run it.
3. Once it returns PASS, record the pass with this exact command (Claude Code asks the
   user to confirm it):

   {qa_pass_command(task_id)}

   Replace <short summary> (brackets included) with a short note using ONLY letters,
   digits, spaces and . _ : - (no commas, slashes, quotes or brackets), for example:
   --note "QA PASS all criteria met". Any other character makes the call non-canonical
   and it is denied.

   Only that confirmed record lets this gate through. If the criteria file changes
   afterwards, QA must pass again.

QA criteria file: .aid/qa/{task_id}.yaml
""")


def main():
    try:
        # Read hook input from stdin
        input_data = json.load(sys.stdin)
    except (OSError, ValueError):
        input_data = {}
    if not isinstance(input_data, dict):
        input_data = {}

    global ROOT
    ROOT = project_root(input_data)
    if ROOT is None:
        sys.exit(0)  # AID not in use here: allow, and create nothing (T7-7)

    log_debug(f"Stop hook triggered. Input keys: {list(input_data.keys())}")

    # Loop guard: Claude Code sets stop_hook_active when it is already continuing
    # because THIS hook blocked. Blocking again would loop forever.
    if input_data.get("stop_hook_active"):
        log_debug("stop_hook_active set, allowing stop to avoid a block loop")
        sys.exit(0)

    # T15-16 (A-16): in an AID root the gate fails CLOSED. An input it cannot trust, or an
    # unexpected error, blocks with a reason instead of silently letting the stop through.
    try:
        evaluate()
    except GateError as e:
        log_debug(f"QA gate input problem, BLOCKING stop: {e}")
        block(f"QA Gate BLOCKED: {e}")
    except Exception as e:  # noqa: BLE001  (fail closed on anything unexpected)
        log_debug(f"QA gate error, BLOCKING stop: {e!r}")
        block(f"QA Gate BLOCKED: the QA gate could not check this stop ({type(e).__name__}: {e}). "
              "Check .aid/state.json and .aid/context.json.")

if __name__ == "__main__":
    main()
