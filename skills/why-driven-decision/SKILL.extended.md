> Human-readable companion to SKILL.md. The LLM loads SKILL.md only.

# WHY-Driven Decision Making Skill

## Overview

This is the **foundational skill** of the AID methodology. It runs *before* any other
skill, on every prompt, and its job is a single question: **why are we doing this?**

The rule is deliberately absolute — never act without understanding WHY — because the
most expensive failures in software are not bugs. They are correctly built features that
nobody needed. Understanding purpose first is cheaper than discovering it after delivery.

```
EVERY PROMPT -> WHY ANALYSIS -> THEN PROCEED
```

---

## Core Principle: The Golden Circle

Work from the inside out. Purpose comes first, process second, deliverable last.

```
     WHY   <- Purpose, belief, motivation
     HOW   <- Process, values, approach
    WHAT   <- Features, outputs, deliverables
```

Most requests arrive at the WHAT layer ("add a spinner", "build a dashboard"). The skill's
work is to travel inward to the WHY before travelling back out to a solution — because a
solution chosen at the WHAT layer can only ever be the solution the requester already
imagined, not the one their problem needs.

---

## The Prompt Analysis Protocol

Four steps, run in order, on every prompt:

```
1. EXTRACT EXPLICIT WHY - What did user state as goal?
2. INFER IMPLICIT WHY - What need not articulated?
3. VALIDATE OR ASK - Is WHY clear enough?
4. ANCHOR TO WHY - Every output traces to WHY
```

Step 3 is the gate. If the WHY is not clear enough after steps 1 and 2, the correct move
is to **ask**, not to guess and proceed.

### Worked Example

```
PROMPT: "Add loading spinner to dashboard"

STEP 1: Explicit WHY: Not stated
STEP 2: Implicit WHY: Users confused? App frozen? Duplicate clicks?
STEP 3: ASK: "What problem? Users think broken, or clicking multiple times?"
STEP 4: Anchor all decisions to answer
```

Notice how much the answer changes the WHAT. If users think the app is broken, the fix may
be a progress indicator with an estimate. If they are clicking twice, the fix may be
disabling the button — no spinner at all. Same prompt, two different correct solutions,
separated only by the WHY.

---

## Golden Rules (Always Do)

1. **Ask WHY before acting** — even simple requests have underlying motivations.
2. **Dig deeper with 5 Whys** — the first answer is rarely the root cause.
3. **State WHY explicitly in outputs** — make the motivation visible, not assumed.
4. **Validate understanding** — reflect the WHY back before proceeding.
5. **Connect every decision to purpose** — every choice should trace to the WHY.

## Iron Rules (Never Break)

These have no exceptions. Where a Golden Rule can be satisfied in degrees, an Iron Rule is
a hard stop.

1. **Never implement without purpose** — "just do it" is not an acceptable justification.
2. **Never copy without understanding** — "a competitor has it" needs WHY validation.
3. **Never skip WHY in reviews** — a review shows intent, not only changes.
4. **Never let urgency bypass purpose** — urgency raises the cost of building the wrong
   thing, so it demands *more* WHY, not less.
5. **Never assume shared understanding** — an implicit WHY is how teams end up misaligned
   while believing they agree.

---

## The 3-Second WHY Check

A fast pre-flight check before any action:

| Question | Answer |
|----------|--------|
| WHY am I doing this? | Purpose |
| WHAT value created? | Benefit |
| WHO benefits? | Stakeholder |

If all three cannot be answered in three seconds, that is itself the signal:
**STOP and clarify.** The three-second limit is the point — a WHY that takes a paragraph to
reconstruct was never actually established.

---

## The 5 Whys Technique

When the WHY is not clear, keep asking. Each answer is usually a symptom of the next.

```
"We need a dashboard"
  Why? -> "To see metrics"
  Why? -> "To track performance"
  Why? -> "To make better decisions"
  Why? -> "Because overwhelmed by data"
  ROOT: Reduce overwhelm, create clarity
```

The root cause here — overwhelm — reframes the request entirely. Adding another surface
full of numbers may make the real problem worse. The dashboard was the requester's
hypothesis, not their need.

---

## The Why-Chain Rule

The WHY-first rule extends from "know the WHY" to "prove the WHY". Every stated WHY becomes:

1. **A requirement** - what we build because of it;
2. **An eval** - the acceptance test or eval case that shows the requirement is met;
3. **A metric** - what tracks it in production (North Star, supporting or guardrail).

**A WHY that yields none of the three is an opinion, not a requirement.** Either make it concrete (requirement + eval + metric) or move it to open questions. It never justifies scope on its own.

This is recorded in PRD §7A.5 Why-Chain (`skills/aid-prd/references/prd-template-extended.md`):

| WHY | Requirement | Eval | Metric |
|---|---|---|---|
| Customers contact support 3 times per delayed payment because nobody tells them why | FR-004: state the specific hold reason, citing the ledger record | Golden set of 200 real tickets; the stated reason matches in >= 95% | Contacts per delayed payment; guardrail: wrong-reason rate < 1% |

At levels 0-1 of the solution-shape ladder the eval is an ordinary acceptance test; at levels 2-5 it is an eval case in PRD §7A.6.

---

## The Agentic Lens and the WHY + Shape Brief

At the start of Phase 1, after the WHY / 5 Whys, the conversation ALWAYS continues with the agentic lens. It applies to every project, AI or not: at levels 0-1 the answers are short, never "N/A".

**The 6 shape questions** (PRD §1.5, verbatim):

1. Can every path be enumerated in advance?
2. How much does the problem vary from case to case?
3. What does an error cost, and is it reversible?
4. Does it need judgement over unstructured input?
5. What latency and cost budget is there?
6. Who must approve actions?

**Plus three agentic questions** (who approves actions is Q6, not asked twice):

- On whose behalf does the solution act?
- Who bears the cost of an error?
- What must never happen?

The answers go into the **WHY + shape brief**, saved as `docs/prd/WHY-SHAPE-BRIEF-<feature>.md`. It is the shared input of every Phase 1 agent: `prd-research-aggregator`, `prd-writer`, `aid:phase1-solution-shaper`, `aid:phase1-charter-drafter` and `aid:phase1-eval-planner` (see `aid-prd/SKILL.md`, "Phase 1 Flow").

**The level in the brief starts from the Phase 0 solution-shape hypothesis** (the "Solution Shape Hypothesis" section of the research report); any change from it is recorded in the brief with a reason. **The level in the brief is a HYPOTHESIS.** `phase1-solution-shaper` tests it against the ladder and proposes the lowest level that works; the PM and the tech lead decide it in the shaping session, and the tech lead signs it as an ADR (A1 decision rights).

### WHY + Shape Brief Template

```markdown
# WHY + Shape Brief: <feature>

**Date:** YYYY-MM-DD | **PM:** <name> | **Status:** input to /prd (level is a hypothesis)

## 1. WHY statement
We believe that [CORE BELIEF].
Therefore, we [HOW WE ACT ON IT].
Which results in [WHAT WE CREATE].
Root WHY (5 Whys): [one sentence]

## 2. Why-Chain seeds
| WHY | Requirement (draft) | Eval idea | Metric idea |
|---|---|---|---|
| [stated reason] | [what we build because of it] | [test or eval case that proves it] | [production metric; at least one guardrail] |

## 3. Shape questions (PRD §1.5)
| # | Question | Answer |
|---|---|---|
| 1 | Can every path be enumerated in advance? | |
| 2 | How much does the problem vary from case to case? | |
| 3 | What does an error cost, and is it reversible? | |
| 4 | Does it need judgement over unstructured input? | |
| 5 | What latency and cost budget is there? | |
| 6 | Who must approve actions? | |

## 4. Level HYPOTHESIS
**Phase 0 hypothesis (research report):** [0-5] - [shape name]
**Level:** [0-5] - [shape name]
**Reason (one line):** [why this level and not the one below]
**Change from Phase 0:** [none, or what changed and why]
Hypothesis only: decided in the shaping session; the tech lead signs the level (ADR).

## 5. On whose behalf it acts
[the user, team or organisation the solution acts for]

## 6. Error owner
[who bears the cost of an error, and how much it costs them]

## 7. Never-do list
- [what must never happen, e.g. "never issue a refund above X without approval"]

## 8. Approvals
[the Q6 answer in detail: which actions need approval, and by whom; "none" only with a reason]
```

---

## Phase-Specific WHY Questions

Each phase of the AID lifecycle has its own core WHY question. The question changes as the
work moves from problem space to solution space:

| Phase | Core Question |
|-------|---------------|
| Discovery | "Why is this problem worth solving?" |
| PRD | "Why does user need this feature?" |
| Tech Spec | "Why this architecture?" |
| Development | "Why this code? Why these connections?" |
| QA & Ship | "Why this test? Why ready?" |

---

## Red Flags — Stop and Ask

Certain phrases are reliable signals that a WHY is missing and is being papered over with
social pressure. Each has a matching question:

| Signal | Ask |
|--------|-----|
| "Just do it" | "What problem does this solve?" |
| "Everyone wants it" | "Why specifically?" |
| "Competitor has it" | "Does our WHY require it?" |
| "It's urgent" | "What's cost of not doing it?" |
| "Trust me" | "Help me understand reasoning" |

---

## Carrying WHY into the Code

A WHY that lives only in a conversation is lost by the next maintainer. The skill therefore
requires the WHY to survive into the artifacts themselves.

### Code Documentation Pattern

Three things are documented: the problem (WHY), the mechanism (WHAT), and the place in the
system (CONNECTION). Parameter and return-type choices carry their own reasoning.

```python
# WHY: Users with slow connections timing out on large datasets.
# WHAT: Paginated query with streaming response.
# CONNECTION: Called by ReportGenerator, feeds into ExportService.
def paginated_query(query: str, page_size: int = 100) -> Iterator[Row]:
    """
    WHY page_size=100: Balance memory (<10MB) vs latency (<50ms).
    WHY Iterator: Allows early stop without loading all data.
    """
```

### Test Pattern

A test's WHY is the failure it prevents and what that failure costs. Written this way, a
test is self-justifying: anyone reading it can judge whether it still earns its place.

```python
def test_retry_on_network_timeout(self):
    """
    WHY: 3% of payments fail due to network issues.
    EXPECTED: Retry 3x recovers 90%.
    COST OF FAILURE: $15 avg transaction lost.
    """
```

---

## Checklist

- [ ] Did I understand WHY before starting?
- [ ] Did I document WHY in output?
- [ ] Does every function explain purpose?
- [ ] Does every test explain what failure it prevents?
- [ ] Can someone trace back to WHY?
- [ ] Does every WHY yield a requirement, an eval and a metric (Why-Chain)?

---

## Further Reading

Supporting material lives alongside this file:

- `references/questioning-patterns.md` — question patterns for eliciting the WHY
- `references/role-applications.md` — how the WHY analysis differs by role

---

## Why This Matters

1. **Prevents wasted work** — the wrong feature built well is still wrong.
2. **Surfaces better solutions** — the root WHY often has a cheaper answer than the
   requested WHAT.
3. **Keeps decisions traceable** — a documented WHY lets a future reader judge whether a
   choice still holds.
4. **Removes false agreement** — stating the WHY out loud exposes misalignment early,
   while it is still cheap.
5. **Outlives the conversation** — WHY captured in code and tests survives the people who
   wrote it.
