#!/usr/bin/env python3
"""
QA Gate Enforcement Hook (Stop Hook)

This hook runs when Claude tries to stop/complete a task.
It blocks completion until QA sub-agent review has passed.

ENFORCEMENT FLOW:
1. Claude finishes coding task
2. Claude tries to move to next task or stop
3. This hook fires
4. Checks for QA_PASSED marker
5. If missing → BLOCKS with "QA required"
6. Claude MUST spawn QA sub-agent
7. After QA passes → allows proceeding
"""

import json
import sys
import os
from datetime import datetime

def log_debug(msg):
    """Write debug info to log file"""
    log_file = ".aid/qa/enforcement.log"
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    with open(log_file, "a") as f:
        f.write(f"[{datetime.now().isoformat()}] {msg}\n")

def get_current_task():
    """Get current task from .aid/context.json"""
    context_file = ".aid/context.json"
    if os.path.exists(context_file):
        try:
            with open(context_file) as f:
                context = json.load(f)
                return context.get("current_task", {}).get("id")
        except:
            pass
    return None

def check_qa_passed(task_id):
    """Check if QA has passed for the given task"""
    if not task_id:
        return True  # No task tracking, allow

    # Check 1: Look for QA review file with PASS verdict
    review_pattern = f".aid/qa/{task_id}-review"
    qa_dir = ".aid/qa"

    if os.path.exists(qa_dir):
        for filename in os.listdir(qa_dir):
            if filename.startswith(f"{task_id}-review") and filename.endswith(".json"):
                review_file = os.path.join(qa_dir, filename)
                try:
                    with open(review_file) as f:
                        review = json.load(f)
                        if review.get("verdict") == "PASS":
                            return True
                except:
                    pass

    # Check 2: Look for .qa-passed marker file
    marker_file = f".aid/qa/{task_id}.qa-passed"
    if os.path.exists(marker_file):
        return True

    # Check 3: Check state.json for qa_status
    state_file = ".aid/state.json"
    if os.path.exists(state_file):
        try:
            with open(state_file) as f:
                state = json.load(f)
                current_task_qa = state.get("current_task_qa", {})
                if current_task_qa.get("task_id") == task_id:
                    if current_task_qa.get("status") == "passed":
                        return True
        except:
            pass

    return False

def is_in_development_phase():
    """Check if currently in development phase (Phase 4)"""
    state_file = ".aid/state.json"
    if os.path.exists(state_file):
        try:
            with open(state_file) as f:
                state = json.load(f)
                phase = state.get("current_phase")
                if phase in [4, "4", "development", "Development"]:
                    return True
        except:
            pass
    return False

def has_qa_criteria_file(task_id):
    """Check if QA criteria file exists for this task"""
    if not task_id:
        return False
    qa_file = f".aid/qa/{task_id}.yaml"
    return os.path.exists(qa_file)

def main():
    try:
        # Read hook input from stdin
        input_data = json.load(sys.stdin)
    except:
        input_data = {}

    log_debug(f"Stop hook triggered. Input keys: {list(input_data.keys())}")

    # Loop guard: Claude Code sets stop_hook_active when it is already continuing
    # because THIS hook blocked. Blocking again would loop forever.
    if input_data.get("stop_hook_active"):
        log_debug("stop_hook_active set, allowing stop to avoid a block loop")
        sys.exit(0)

    # Only enforce in development phase
    if not is_in_development_phase():
        log_debug("Not in development phase, allowing stop")
        sys.exit(0)  # allow: silent exit 0 is how a Stop hook approves

    # Get current task
    task_id = get_current_task()
    log_debug(f"Current task: {task_id}")

    if not task_id:
        log_debug("No task ID found, allowing stop")
        sys.exit(0)  # allow: silent exit 0 is how a Stop hook approves

    # Check if this task has QA criteria (if not, no gate needed)
    if not has_qa_criteria_file(task_id):
        log_debug(f"No QA criteria file for {task_id}, allowing stop")
        sys.exit(0)  # allow: silent exit 0 is how a Stop hook approves

    # Check if QA has passed
    if check_qa_passed(task_id):
        log_debug(f"QA PASSED for {task_id}, allowing stop")
        sys.exit(0)  # allow: silent exit 0 is how a Stop hook approves

    # QA NOT passed - BLOCK
    log_debug(f"QA NOT PASSED for {task_id}, BLOCKING stop")

    # Stop hook block schema: {"decision": "block", "reason": ...}. The reason is fed
    # back to Claude as the instruction for what to do next.
    output = {
        "decision": "block",
        "reason": f"""QA Gate BLOCKED: task {task_id} requires QA validation before you stop.

ACTION REQUIRED:
1. Spawn the QA validator sub-agent:

   Task(
     subagent_type="qa-validator-agent",
     prompt="Validate task {task_id}. Criteria: .aid/qa/{task_id}.yaml",
     description="QA validation for {task_id}"
   )

2. If it returns FAIL, fix the issues and re-run it.
3. Once it returns PASS, write the verdict to .aid/qa/{task_id}-review.json
   (or .aid/qa/{task_id}.qa-passed) so this gate can see it, then stop.

QA criteria file: .aid/qa/{task_id}.yaml
"""
    }

    print(json.dumps(output))

if __name__ == "__main__":
    main()
