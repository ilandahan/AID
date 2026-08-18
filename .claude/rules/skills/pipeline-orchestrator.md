# Pipeline Orchestrator Rules

Auto-load rules for the pipeline orchestrator. Active when in Phase 4 or Phase 5.

---

## When to Load

Load `.claude/skills/pipeline-orchestrator/SKILL.md` when:

1. User invokes `/pipeline` or `/pipeline-status`
2. Current phase is 4 (Development) or 5 (QA & Ship) AND `.aid/pipeline/state.json` exists with `pipeline_status: "running"`
3. Project loads with an active pipeline (auto-resume)

---

## Auto-Resume Rule

On project load or `/good-morning`:

1. Check if `.aid/pipeline/state.json` exists
2. If `pipeline_status: "running"` or `pipeline_status: "paused"`:
   - Display: "Active pipeline detected for task [task_id] at step [current_step]"
   - Ask: "Resume pipeline? (y/n)"
3. If `pipeline_status: "escalated"`:
   - Display escalation summary with options (resume/override/reset/abort)

---

## Pipeline Augments Existing Skills

When the pipeline is active:

- `aid-development` (Phase 4) defers step sequencing to the pipeline
- `aid-qa-ship` (Phase 5) defers test sequencing to the pipeline
- The pipeline calls the same sub-agents and enforces the same quality gates
- If the pipeline is NOT active, existing manual flows work as before

---

## Sub-Agent Isolation

All sub-agents spawned by the pipeline follow the standard isolation rules:

- **PASS:** Task context, changed files, standards reference
- **DO NOT PASS:** Conversation history, reasoning, previous attempts

See `rules/agents/sub-agents.md` and `rules/agents/reflection-agent.md` for isolation rules.

---

## State File Management

| File | Git-tracked | Purpose |
|------|------------|---------|
| `.aid/pipeline/config.json` | Yes | Pipeline settings (shared) |
| `.aid/pipeline/state.json` | No (gitignored) | Runtime state (per-session) |
| `.aid/pipeline/history.json` | No (gitignored) | Completed run archive |
