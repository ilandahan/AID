# Agent Architecture: Reference (Tech Spec Section 9)

> **Purpose**: depth for Section 9 "Agent Architecture" of the tech spec (AID 3.1, the agentic layer).
> Used by `aid-tech-spec`, `system-architect` and `role-tech-lead`.
> The vocabulary is defined once, in the PRD: **§1.5 Solution Shape** (the ladder, levels 0-5) and
> **§7A Agentic Design** (7A.1-7A.8). This file only designs HOW; it never redefines WHAT.

---

## The Rules

1. **Always present.** Every tech spec has Section 9, for every project. It is never "N/A".
2. **Scaled by level.** Depth follows the level chosen in PRD §1.5 Solution Shape. At levels 0-1 each
   heading takes its classic form (see the table below), usually in a few lines.
3. **Traced.** Every item cites the §7A item it implements, e.g. `[PRD 7A.2]`. An item that traces to
   nothing is either missing from the PRD (flag `[PRD GAP]`) or not needed.
4. **Lowest level that works.** The spec builds the level the PRD chose. If design shows a different
   level is needed, raise it as a contradiction; do not silently step up.

### The ladder (from PRD §1.5)

| Level | Shape |
|---|---|
| 0 | Process change (no software) |
| 1 | Deterministic automation |
| 2 | Single LLM call inside a fixed flow |
| 3 | Workflow (several fixed steps, some with LLM calls) |
| 4 | Agent (the model chooses the path and the tools) |
| 5 | Multi-agent |

---

## Scaling by Level: Classic Forms at Levels 0-1

| Section 9 heading | Traces to | Level 0 (process change) | Level 1 (deterministic automation) | Levels 2-5 |
|---|---|---|---|---|
| 9.1 Orchestration Pattern | §1.5, 7A.1 | Process design: steps, RACI, process owner | Service design: components, jobs, rules, data flow | Pattern for the level (below) |
| 9.2 Tool Contracts & Permission Policy | 7A.2, 7A.3 | Who is authorised to do each step | Service permissions: roles, service accounts, scopes | Tool contracts + policy as code |
| 9.3 Guardrails | 7A.4 | Four-eyes checks, limits, sign-offs | Input validation, business rules, rate limits | Input/output/action guardrails |
| 9.4 Trace Schema | 7A.7 | Records kept per case (who, what, when) | Structured logs, audit log, metrics | Per-run trace (schema below) |
| 9.5 Eval Harness | 7A.6, 7A.5 | Acceptance check / dry run of the process | Test harness: unit, integration, acceptance tests | Golden set + runner + judge + gate |
| 9.6 Model Choice & Fallbacks | 7A.4, 7A.6 | None: state why no model is used | None: state why no model is used; dependency fallbacks | Model per step + fallback chain |
| 9.7 Cost & Latency Budgets | §1.5 Q5, 7A.7 | Effort and turnaround per case | NFR latency and infrastructure cost | Per-run token, tool and time budgets |
| 9.8 Kill Switch | 7A.8 | Revert to the old process; who decides | Feature flag + rollback plan | Kill switch + degrade-to level |

---

## 9.1 Orchestration Pattern  `[PRD §1.5, 7A.1]`

| Level | Pattern | Must specify |
|---|---|---|
| 0 | Process (no software) | Steps, owner, hand-offs, where errors are caught |
| 1 | Deterministic service, job or rules engine | Components, triggers, data flow |
| 2 | Fixed flow with one LLM call | The call site, structured output schema, validator, deterministic fallback when the output fails validation |
| 3 | Workflow: a fixed state machine / DAG (chaining, routing, parallel steps) | Each step, which steps call an LLM, checkpoints, retries, where a human approves |
| 4 | Agent loop: plan → call tool → observe → repeat | Tool allowlist, step/turn limit, stop conditions, approval points for irreversible actions, escalation to a human (7A.1) |
| 5 | Multi-agent: orchestrator-workers or hand-off | The ONE justification, each agent's own tools, permissions and context, the hand-off contract, one shared trace id |

**Multi-agent (level 5) is allowed only with one of these four justifications**, written in the spec:
1. separate permission boundaries;
2. contexts that would contaminate each other;
3. genuinely parallel work;
4. ownership by different teams.

"It is cleaner" or "it is more modular" is not a justification: use a workflow or one agent with more tools.

Checklist:
- [ ] Pattern matches the PRD §1.5 level; any change is logged as a contradiction
- [ ] Diagram shows every LLM call, tool call and human approval point
- [ ] Escalation to a human matches 7A.1 (when, to whom, with what context)
- [ ] Level 5: the justification is one of the four, per agent boundary

---

## 9.2 Tool Contracts & Permission Policy  `[PRD 7A.2, 7A.3]`

One contract per tool. The risk tag comes from 7A.2.

| Tool | Input schema | Output schema | Side effect | Risk tag (read/write, reversible?, approval?) | Rate limit | Timeout | Errors | Idempotent? |
|---|---|---|---|---|---|---|---|---|

**Permission policy, as code where possible.** Keep it in the repo, review it like code, and enforce
it outside the model (the model never decides its own permissions). Example:

```yaml
# policy/agent-permissions.yaml  [PRD 7A.2]
agent: refund-assistant
acts_on_behalf_of: customer_support_agent   # 7A.1
default: deny
tools:
  lookup_order:   { access: read,  reversible: true,  approval: none }
  draft_reply:    { access: write, reversible: true,  approval: none }
  issue_refund:   { access: write, reversible: false, approval: human, max_amount_eur: 50 }
  # reversible: false is a property of the action (a refund cannot be recalled), at any amount.
  # max_amount_eur is the one threshold: above 50 EUR the call is blocked (7A.1 never-do).
never:                                        # 7A.1 never-do list, enforced in code
  - delete_customer_record
  - send_email_without_review
data:                                         # 7A.3
  pii_fields_visible: [name, order_id]
  retention_days: 30
```

Checklist:
- [ ] Default deny; each tool is listed with its least-privilege scope
- [ ] Credentials are scoped to the user or role the agent acts for (7A.1), never a broad service key
- [ ] Irreversible writes need human approval until 7A.8 says otherwise
- [ ] Never-do items from 7A.1 are blocked in code, not only in the prompt
- [ ] Data visible to the model matches 7A.3 (PII, financial data, memory, retention)
- [ ] Secrets come from SSO or the OS keystore / secrets manager, never from prompts or files

---

## 9.3 Guardrails  `[PRD 7A.4]`

| Layer | Guardrail | Examples |
|---|---|---|
| Input | Validate and mark untrusted content | Schema checks; tool results and documents are data, not instructions (`rules/general/untrusted-content.md`) |
| Action | Check every tool call against the policy | Allowlist, argument limits, approval gates, never-do blocks |
| Output | Validate before use | Output schema, PII filter, grounding check, refusal handling |
| Run | Bound the run | Step limit, token budget, wall-clock timeout, loop detection |

**Data exfiltration ("lethal trifecta").** Check whether the agent combines all three legs:
private data (7A.3) + untrusted content (documents, web pages, tool results) + an external
channel (outbound tools such as email or HTTP, or URLs/markdown images in the output that the
client fetches). If all three are present, remove one leg or require human approval on
outbound actions.

Checklist:
- [ ] Every 7A.4 failure mode has at least one guardrail and one eval case
- [ ] Lethal trifecta checked: if private data, untrusted content and an external channel are all present, one leg is removed or outbound actions need human approval
- [ ] Prompt-injection exposure is listed per input source, with its mitigation
- [ ] Guardrail hits are recorded in the trace and counted as a metric
- [ ] Red lines fail closed (block and escalate), never fail open

---

## 9.4 Trace Schema  `[PRD 7A.7]`

Trace by default: every run records a trace, from the first release (including shadow mode).

```yaml
trace:
  trace_id: uuid            # shared by every agent and step in the run
  run_started_at: timestamp
  actor: { on_behalf_of: user_or_role, agent: name, agent_version: semver }
  versions: { prompt: id, tools: id, model: id, policy: id }
  input_ref: pointer        # pointer, not raw PII (7A.3)
  plan: [steps]             # the plan or route chosen
  tool_calls:
    - { tool: name, args_redacted: {}, result_summary: str, status: ok|error|blocked, latency_ms: int }
  results: { output_ref: pointer, validation: pass|fail }
  escalations: [{ reason: str, to: role, at: timestamp }]
  guardrail_hits: [{ guardrail: name, action: block|warn }]
  cost: { input_tokens: int, output_tokens: int, tool_cost: float, total_usd: float }
  latency: { total_ms: int, per_step_ms: [int] }
  outcome: success|escalated|failed|killed
```

Checklist:
- [ ] Actor (`actor`, `on_behalf_of`), plan, tool calls, results, escalations, cost, latency and `outcome` are all present
- [ ] PII is redacted or referenced, and secrets and credentials (API keys, tokens, passwords, cookies) never appear in `args_redacted`, `result_summary` or any trace field; retention matches 7A.3
- [ ] Traces feed the 7A.7 metrics (quality, cost, escalation rate, guardrail metrics)
- [ ] A failed production trace can be added to the golden set in one step

---

## 9.5 Eval Harness  `[PRD 7A.6, 7A.5]`

| Part | Design decision |
|---|---|
| Golden set storage | Versioned in the repo: golden set and held-out split in `tests/evals/golden/` (e.g. `*.jsonl`); the dev/targeted suite in `tests/evals/dev/`. Each case: input, expected outcome or rubric, tags (slice, never-do, red-team), source, owner. Why under `tests/`: the phase gate allows `tests/` writes before Phase 4, so QA can grow the set in Phases 2-3. Create and edit these files with the Write/Edit tools, not Bash (Bash is read-only before Phase 4). Every case is de-identified and holds no secrets or credentials, like the seed cases: the files are committed |
| Size and source | From 7A.6 (e.g. real de-identified cases + expert-written edge cases) |
| Timing | Starts from the Phase 1 seed cases (`docs/prd/SEED-EVALS-<feature>.md`). QA grows the golden set and held-out split in parallel with Phases 2-4; this design never waits for it. Complete only for the Phase 5 release gate |
| Golden-set ownership | QA owns the golden set and its held-out split, and is the only one who merges into them. Developers iterate on a separate dev/targeted suite and propose additions through a QA-reviewed PR |
| Adversarial / red-team cases | Generated and hand-written, incl. prompt injection; kept in a separate suite. Gate: 0 critical/high failures, plus an overall pass rate ≥ the PRD's target |
| Never-do checks | One case per 7A.1 never-do item. Never-do is enforced in code (policy, default-deny); evals verify the enforcement at 100%. Repeated runs cannot prove a low breach rate: proving a rate below p at 95% confidence takes n ≈ ln(0.05)/ln(1−p) clean runs (about 59 for 5%) |
| Runner | Runs locally and in CI on every prompt, tool, model or policy change; outputs per-case results and per-slice scores |
| Scorers | Deterministic checks first (schema, exact match, tool-call assertions); LLM-as-judge only where needed |
| Judge and calibration | Judge prompt and model are versioned. Cohen's kappa (or Krippendorff's alpha) ≥ 0.7 against adjudicated human labels on ≥ 50 stratified cases, including failures. Percent agreement is reported alongside, never alone. The judge never grades the outputs of its own prompt or model, and the rubric is not visible to the system under test. Re-calibrated when the judge changes. Calibrated by the data scientist in Phase 4, when the judge is introduced; the tech spec names the judge and the method only |
| Release gate | Golden set ≥ the PRD's threshold, on the held-out split, which developers never tune on; enforced by the runner's exit code in CI |
| Why-Chain link | Each 7A.5 WHY maps to at least one eval case and one production metric |

At levels 0-1 the harness is the classic test harness: acceptance tests from the PRD stories run in CI.

---

## 9.6 Model Choice & Fallbacks  `[PRD 7A.4, 7A.6]`

| Step | Model | Why this model (eval score, cost, latency) | Fallback 1 | Fallback 2 (non-LLM) |
|---|---|---|---|---|

Checklist:
- [ ] Choice is backed by eval results on the golden set, not by preference
- [ ] Smallest model that passes the gate, per step
- [ ] Fallback on timeout, rate limit, provider outage and failed validation
- [ ] Final fallback is deterministic or a human hand-off, never a silent failure
- [ ] Model version is pinned; a model change re-runs the full eval

---

## 9.7 Cost & Latency Budgets  `[PRD §1.5 Q5, 7A.7]`

| Budget | Target | Hard limit (run stops) | Measured from |
|---|---|---|---|
| Cost per run | | | trace `cost.total_usd` |
| Tokens per run | | | trace `cost` |
| Tool calls / steps per run | | | trace `tool_calls` |
| p95 latency | | | trace `latency.total_ms` |
| Monthly spend | | | aggregated traces |

Checklist:
- [ ] Budgets come from §1.5 Q5 (latency and cost budget)
- [ ] Hard limits are enforced in code and end the run with an escalation
- [ ] Alerts fire before the monthly budget is reached

---

## 9.8 Kill Switch  `[PRD 7A.8]`

| Element | Design decision |
|---|---|
| Mechanism | A runtime flag read before every run and every write tool call (not a deploy) |
| Scopes | Global, per tool, per tenant/segment |
| Degrade-to | What runs instead: a lower ladder level, read-only mode, or the human process |
| Who can pull it | The 7A.8 owner on call, plus automatic triggers |
| Automatic triggers | Guardrail-metric breach, cost limit, error or escalation rate spike |
| Rollout stages | Shadow → human approval → autonomous; entry and exit criteria per stage from 7A.8 |
| Tested | The switch is tested in staging and before each move to autonomy, including that the human queue can absorb 100% of the volume (or a throttle) |

At levels 0-1 this is a feature flag plus a tested rollback plan.

---

## Anti-Patterns

| Anti-pattern | Fix |
|---|---|
| Section 9 marked "N/A" | Use the classic form for the level |
| Multi-agent "for modularity" | Use one of the four justifications, or step down |
| Permissions only in the prompt | Enforce the policy in code, default deny |
| Logs instead of traces | Record the full trace schema per run |
| Judge used without calibration | Calibrate against human labels (Phase 4) before the judge gates the release |
| Kill switch needs a deploy | Runtime flag, tested before autonomy |
| Model picked by reputation | Pick by golden-set score, cost and latency |
