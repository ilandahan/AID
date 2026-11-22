---
description: "Display the current state of the automated development pipeline"
---

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
   - Last review result summary, from `last_review_result`
     (`{step, result, overall, threshold, round, timestamp}`)
   - Cost so far, from `cost` (`total_input_tokens`, `total_output_tokens`,
     `estimated_cost_usd`, and `per_step[<step>]` with `input_tokens`, `output_tokens`,
     `cost_usd`, `timestamp`, `estimated`)

Both are recorded in code by `gate.mjs --step` (from the `--usage` token counts of each
review, or the documented 4000 input / 2000 output estimate when none was passed). Mark every
`per_step` entry with `estimated: true` as an estimate, and say the total includes estimates
when any entry does. If `cost` or `last_review_result` is missing (no review has been scored
yet), show "none recorded yet".

The $ brake does not read `cost` alone: `gate.mjs` escalates at `cost_limits.max_per_run_usd`
from `max(cost ledger, cost.estimated_cost_usd)` (T21; the ledger is `.git/aid/<project key>/cost-ledger.json`
in a git repo, else `.aid/pipeline/cost-ledger.json`). Show that running
total against the limit; when the ledger is higher than `cost`, say so.

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

Last Review: [last_review_result.step] > [result] ([overall]/[threshold], round [round])

Cost: [cost.total_input_tokens] in / [cost.total_output_tokens] out tokens,
      ~$[cost.estimated_cost_usd] (includes estimates)
  CODE_REVIEW:  [input_tokens] in / [output_tokens] out, $[cost_usd]
  TEST_REVIEW:  [input_tokens] in / [output_tokens] out, $[cost_usd] (estimated)
```

## Load Skills

Read `.aid/pipeline/state.json` and `.aid/pipeline/config.json`. Display formatted output.
