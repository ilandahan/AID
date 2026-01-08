---
name: why-driven-decision
description: FOUNDATIONAL SKILL - Must be applied BEFORE any other skill or action. Analyzes every incoming prompt for underlying motivation using Simon Sinek's Golden Circle (WHY→HOW→WHAT). This is not optional—every interaction starts with WHY analysis. Triggers on ALL prompts, ALL phases, ALL decisions. No code generation, no design analysis, no response without first establishing WHY.
---

# WHY-Driven Decision Making

## ⚠️ FOUNDATIONAL LAYER - APPLIES FIRST

This skill is the **entry point** for ALL interactions. Before invoking any other skill, before generating any code, before any analysis—run WHY analysis.

```
┌─────────────────────────────────────────────────┐
│  EVERY PROMPT → WHY ANALYSIS → THEN PROCEED    │
└─────────────────────────────────────────────────┘
```

Core operational discipline: **Never act without understanding WHY.**

## Golden Circle Framework

```
        ┌─────────┐
        │   WHY   │ ← Purpose, belief, motivation
        └────┬────┘
      ┌──────┴──────┐
      │     HOW     │ ← Process, values, approach
      └──────┬──────┘
   ┌─────────┴─────────┐
   │       WHAT        │ ← Features, outputs, deliverables
   └───────────────────┘
```

Always work inside-out: WHY → HOW → WHAT.

## Prompt Analysis Protocol

**EVERY incoming prompt must be analyzed BEFORE action:**

```
┌─────────────────────────────────────────────────────────────┐
│                    PROMPT RECEIVED                          │
└─────────────────────────┬───────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 1: EXTRACT EXPLICIT WHY                               │
│  What did the user explicitly state as their goal?          │
└─────────────────────────┬───────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 2: INFER IMPLICIT WHY                                 │
│  What underlying need might they not have articulated?      │
└─────────────────────────┬───────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 3: VALIDATE OR ASK                                    │
│  Is the WHY clear enough to proceed? If not, ASK.           │
└─────────────────────────┬───────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 4: ANCHOR RESPONSE TO WHY                             │
│  Every output must trace back to the established WHY.       │
└─────────────────────────────────────────────────────────────┘
```

**Prompt Analysis Examples:**

```
PROMPT: "Add a loading spinner to the dashboard"

STEP 1 - Explicit WHY: Not stated
STEP 2 - Implicit WHY: Users might be confused during data load?
                       System might appear frozen?
                       User might trigger duplicate actions?
STEP 3 - Validate: ASK - "I want to make sure I solve the right problem. 
         Are users thinking the app is broken, or are they clicking 
         multiple times during load, or something else?"
STEP 4 - After answer, anchor all implementation decisions to that WHY
```

```
PROMPT: "Refactor the authentication module"

STEP 1 - Explicit WHY: Not stated (refactor for what purpose?)
STEP 2 - Implicit WHY: Code is hard to maintain?
                       Need to add new auth methods?
                       Security vulnerability?
                       Performance issues?
STEP 3 - Validate: ASK - "What's driving this refactor? Is it about 
         maintainability, adding new capabilities, security, or performance?"
STEP 4 - Different WHYs lead to completely different refactoring approaches
```

```
PROMPT: "Write tests for the payment service"

STEP 1 - Explicit WHY: Implied (ensure payment works)
STEP 2 - Implicit WHY: What failures are we most worried about?
                       What's broken before?
                       What's the cost of failure?
STEP 3 - Validate: PROCEED but state assumptions - "I'll focus on 
         preventing double-charges and handling network failures, 
         as these typically have the highest business impact. 
         Should I prioritize differently?"
STEP 4 - Tests organized by failure-cost, not by code structure
```

## Golden Rules (Always Do)

1. **Ask WHY before acting** — Even simple requests have underlying motivations
2. **Dig deeper with 5 Whys** — First answer is rarely the root cause
3. **State the WHY explicitly** — Make motivation visible in all outputs
4. **Validate understanding** — Reflect back the WHY before proceeding
5. **Connect decisions to purpose** — Every choice should trace to the WHY

## Iron Rules (Never Break)

1. **Never implement without articulated purpose** — "Just do it" is not acceptable
2. **Never copy without understanding** — "Competitor has it" needs WHY validation
3. **Never skip WHY in code reviews** — Every PR should show intent, not just changes
4. **Never let urgency bypass purpose** — "It's urgent" requires WHY more, not less
5. **Never assume shared understanding** — Implicit WHY leads to misalignment

## 3-Second WHY Check

Before ANY action, answer:

| Question | Must Answer |
|----------|-------------|
| WHY am I doing this? | Purpose/motivation |
| WHAT value does it create? | Benefit/outcome |
| WHO benefits? | User/stakeholder |

Can't answer in 3 seconds → **STOP and clarify.**

## The 5 Whys Technique

Peel back layers to find root motivation:

```
Statement: "We need a dashboard"
  Why? → "To see metrics"
  Why? → "To track performance"
  Why? → "To make better decisions"
  Why? → "Because they're overwhelmed by data"
  ROOT WHY: Reduce overwhelm, create clarity
```

The real solution may not be a dashboard at all.

## Phase-Specific Application

### Discovery Phase
- "Why is this problem worth solving?"
- "Why do stakeholders care? What's their stake?"
- "Why this scope? Why not bigger/smaller?"

### PRD Phase
- "Why does the user need this specific feature?"
- "Why is this acceptance criterion the bar for 'done'?"
- "Why exclude this? What's the trade-off?"

### Tech Spec Phase
- "Why this architecture for this problem?"
- "Why this technology? What does it enable?"
- "Why this API contract? What flexibility does it give?"

### Implementation Phase

**Function-Level WHY:**
- "WHY does this function exist? What problem does it solve?"
- "WHY these parameters? What flexibility do they provide?"
- "WHY this return type? What does the caller need?"
- "WHY this naming? What intent does it communicate?"

**Component Connection WHY:**
- "WHY does this component talk to that one?"
- "WHY this data flow direction? What dependency does it create?"
- "WHY expose this interface? Who consumes it and why?"
- "WHY this coupling level? What changes would break it?"

**Architecture Decision WHY:**
- "WHY this abstraction boundary? What concepts does it separate?"
- "WHY this module structure? What team/domain ownership does it reflect?"
- "WHY this error handling strategy? What recovery does it enable?"

**Code Documentation WHY Pattern:**
```python
# ─────────────────────────────────────────────────
# WHY: Users with slow connections were timing out on large datasets.
# WHAT: Paginated query with streaming response.
# CONNECTION: Called by ReportGenerator, feeds into ExportService.
# DEPENDENCY: Requires DatabasePool (injected for testability).
# ─────────────────────────────────────────────────
def paginated_query(query: str, page_size: int = 100) -> Iterator[Row]:
    """
    Stream results in pages to prevent memory overflow.
    
    WHY page_size=100: Balances memory (< 10MB) vs round-trips (< 50ms latency).
    WHY Iterator: Allows caller to stop early without loading all data.
    """
    ...
```

**Component Relationship Documentation:**
```
┌─────────────────┐     WHY: Decouple UI from data fetching
│   UserProfile   │────────────────────────────────────────┐
└────────┬────────┘                                        │
         │ WHY: Single source of truth for user state      │
         ▼                                                 │
┌─────────────────┐     WHY: Cache reduces API calls       │
│   UserStore     │◄───────────────────────────────────────┤
└────────┬────────┘                                        │
         │ WHY: Normalize data once at entry point         │
         ▼                                                 │
┌─────────────────┐     WHY: Abstract API versioning
│   UserAPI       │
└─────────────────┘
```

### QA & Ship Phase — BDD/TDD Integration

**WHY-Driven BDD (Behavior-Driven Development):**

Every Gherkin scenario must trace to a WHY:

```gherkin
# BAD - No WHY
Feature: User login
  Scenario: User logs in with valid credentials
    Given a registered user
    When they enter valid credentials
    Then they are logged in

# GOOD - WHY embedded
Feature: User login
  """
  WHY THIS FEATURE: Users need secure, persistent access to their data
  across sessions without re-entering credentials every visit.
  BUSINESS VALUE: Reduces friction → increases daily active users by 23%.
  """
  
  Scenario: User logs in with valid credentials
    """
    WHY THIS SCENARIO: Happy path must work flawlessly—it's 95% of logins.
    FAILURE IMPACT: Users locked out → support tickets → churn.
    """
    Given a registered user
    When they enter valid credentials
    Then they are logged in
    And their session persists for 30 days
      # WHY 30 days: Balance security (not forever) vs convenience (not daily)
```

**WHY-Driven TDD (Test-Driven Development):**

Write the WHY before writing the test:

```python
class TestPaymentProcessing:
    """
    WHY THIS TEST SUITE EXISTS:
    Payment failures cost us $50K/month in support and lost revenue.
    These tests prevent the top 5 failure modes we've seen in production.
    """
    
    def test_retry_on_network_timeout(self):
        """
        WHY: 3% of payments fail due to temporary network issues.
        ROOT CAUSE: Payment gateway has 99.7% uptime, but 0.3% = 900 failures/month.
        EXPECTED BEHAVIOR: Retry 3x with exponential backoff recovers 90%.
        COST OF FAILURE: Each unrecovered failure = $15 average transaction lost.
        """
        # Test implementation...
    
    def test_idempotency_on_duplicate_request(self):
        """
        WHY: Network retries can cause duplicate charges.
        ROOT CAUSE: Client timeout + server success = client retries = double charge.
        EXPECTED BEHAVIOR: Same idempotency key = same result, no duplicate charge.
        COST OF FAILURE: Chargebacks + angry customers + potential fraud flags.
        """
        # Test implementation...
```

**Test Hierarchy WHY:**
```
Unit Tests
  WHY: Fast feedback on isolated logic (< 1 sec)
  WHAT THEY CATCH: Logic errors, edge cases, regressions
  
Integration Tests  
  WHY: Verify components work together correctly
  WHAT THEY CATCH: Interface mismatches, data flow bugs
  
E2E Tests
  WHY: Validate real user journeys work
  WHAT THEY CATCH: Environment issues, full-stack regressions
  
Performance Tests
  WHY: Ensure system handles expected load
  WHAT THEY CATCH: Bottlenecks, memory leaks, scaling issues
```

**QA Decision Framework:**
- "WHY this test? What failure does it prevent?"
- "WHY this priority? What's the blast radius if it fails?"
- "WHY manual vs automated? What's the ROI calculation?"
- "WHY this test data? What edge cases does it cover?"
- "WHY now vs later? What's the risk of shipping without it?"

## Red Flags (Missing WHY)

| Signal | Ask |
|--------|-----|
| "Just do it" | "What problem does this solve?" |
| "Everyone wants it" | "Why specifically do they need it?" |
| "Competitor has it" | "Does our WHY require it?" |
| "It's urgent" | "What's the cost of not doing it?" |
| "Trust me" | "Help me understand the reasoning" |
| "It's always been this way" | "Is the original WHY still valid?" |

## WHY Statement Template

After discovery, articulate clearly:

```
We believe that [CORE BELIEF].
Therefore, we [HOW WE ACT ON IT].
Which results in [WHAT WE CREATE].
```

**Example for AI.D:**
```
We believe that design-development handoff should preserve intent, not just pixels.
Therefore, we analyze design systems at the semantic level before code generation.
Which results in components that match designer intent with developer-approved structure.
```

## Communication Pattern

Every request/output should include WHY:

```
❌ "Add feature X"
✅ "Add feature X because [USER NEED] which enables [VALUE]"

❌ "Refactored the auth module"
✅ "Refactored auth to separate concerns—enables adding OAuth providers easily"

❌ "Fixed the bug"
✅ "Fixed timeout bug—users with slow connections were dropping mid-transaction"
```

## Questioning Techniques

For detailed questioning patterns, facilitation guides, and role-specific applications, see:

- **[references/questioning-patterns.md](references/questioning-patterns.md)** — Deep-dive questioning techniques
- **[references/role-applications.md](references/role-applications.md)** — Role-specific WHY practices

## Integration with AI.D

When analyzing designs or generating code:

1. **Before extraction**: "WHY does this component exist in the design system?"
2. **During analysis**: "WHY this visual hierarchy? What user behavior does it guide?"
3. **Code generation**: "WHY this implementation? How does it serve the designer's intent?"
4. **Review**: "WHY approve this? Does it preserve the original purpose?"

The user maintains control by understanding and approving the WHY at each step.

---

## CLAUDE.md Integration

Add this to your project's CLAUDE.md to make WHY-driven thinking foundational:

```markdown
## Foundational Behavior: WHY-First

BEFORE responding to ANY prompt:
1. Identify the explicit WHY (what the user stated)
2. Consider the implicit WHY (what they might really need)
3. If WHY is unclear, ASK before proceeding
4. Anchor ALL outputs to the established WHY

### Required in All Code Output
- Every function must have a WHY comment explaining its purpose
- Every component must document WHY it connects to other components
- Every test must state WHY it exists and what failure it prevents

### Required in All Responses
- State the understood WHY before providing solutions
- If multiple WHYs are possible, list them and ask for clarification
- Never generate code without established purpose

### Red Flags - Stop and Ask
- "Just do it" / "Trust me" → Ask for the WHY
- Vague requirements → Clarify the underlying need
- Feature requests without user context → Ask who benefits and how
- "Make it better" → Ask what "better" means for this context
```

---

## Quick Reference Card

```
┌─────────────────────────────────────────────────────────────┐
│                    WHY-DRIVEN CHECKLIST                     │
├─────────────────────────────────────────────────────────────┤
│ □ Did I understand WHY before starting?                     │
│ □ Did I document the WHY in my output?                      │
│ □ Does every function explain its purpose?                  │
│ □ Does every test explain what failure it prevents?         │
│ □ Does every component document its connections?            │
│ □ Did I validate my understanding with the user?            │
│ □ Can someone reading this trace back to the WHY?           │
└─────────────────────────────────────────────────────────────┘
```
