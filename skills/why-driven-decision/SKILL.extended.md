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
