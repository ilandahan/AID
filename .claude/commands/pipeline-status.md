# /pipeline-status — Show Pipeline State

Display the current state of the automated development pipeline.

## Behavior

1. Read `.aid/pipeline/state.json`
2. If file doesn't exist: "No active pipeline. Start one with `/pipeline`."
3. Display current state including:
   - Pipeline status (idle/running/paused/escalated/completed)
   - Current phase and step
   - Task ID and description
   - Iteration counts vs. maximums
   - Step history timeline
   - Last review result summary

## Display Format

```
Pipeline Status
Task: [task_id] - [description]
Phase: [current_phase] | Step: [current_step]
Status: [pipeline_status]
Started: [started_at] | Last Updated: [last_updated]

Iterations:
  Code Review: [N]/[max]  Test Fix: [N]/[max]  Test Review: [N]/[max]
  API Fix: [N]/[max]  E2E Fix: [N]/[max]

Step History:
  1. DEVELOP > PASS
  2. CODE_REVIEW > FAIL (1 CRITICAL)
  3. FIX_CODE > done
  4. CODE_REVIEW > PASS
  ...
```

## Load Skills

Read `.aid/pipeline/state.json` and `.aid/pipeline/config.json`. Display formatted output.
