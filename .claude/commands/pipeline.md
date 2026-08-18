# /pipeline — Start Automated Development Pipeline

Initialize and start the automated development pipeline for the current task. The pipeline enforces a deterministic sequence: DEVELOP > CODE_REVIEW > TDD > TEST_REVIEW > PHASE_GATE > API_TESTS > E2E_TESTS > CERTIFICATION.

## Prerequisites

- Current phase must be 4 (Development) or 5 (QA & Ship)
- A task must be active in `.aid/context.json`

## Behavior

1. **Check prerequisites** — verify phase and task context
2. **Load config** — read `.aid/pipeline/config.json` (create with defaults if missing)
3. **Check existing state** — if pipeline already running, offer resume/restart
4. **Initialize state** — create `.aid/pipeline/state.json` with `current_step: "DEVELOP"`
5. **Start pipeline** — begin executing the state machine

## Sub-Commands

| Command | Action |
|---------|--------|
| `/pipeline` | Start or resume pipeline |
| `/pipeline resume` | Resume from escalation, reset current step counter |
| `/pipeline override [reason]` | Skip escalated step with justification |
| `/pipeline reset` | Reset all counters, restart from DEVELOP |
| `/pipeline abort` | Stop pipeline entirely |

## What Happens

The pipeline drives automated code review and test validation through sub-agents:

- **code-review-agent** reviews changed code for security, quality, docs, architecture
- **test-review-agent** reviews tests for assertion strength, coverage, independence
- **qa-validator-agent** validates acceptance criteria from `.aid/qa/` files

Each gate has max retry iterations. If exceeded, the pipeline escalates to you for a decision.

## Configuration

Edit `.aid/pipeline/config.json` to customize:
- Max iterations per step
- Test commands (unit, integration, e2e, cucumber)
- Quality thresholds (review pass score, coverage %)

## Load Skills

Load the pipeline-orchestrator skill from `.claude/skills/pipeline-orchestrator/SKILL.md`.
