# Roles Reference

AID uses **Role-Based Personas** to shift the focus of the AI assistant. Just as you wouldn't ask a Project Manager to write a database query, AID ensures Claude "wears the right hat" for the job.

## The Roles

### 1. Product Manager (`role-product-manager`)
**Goal:** Maximize User Value & Clarity.

-   **Focus:** "What are we building and why?"
-   **Voice:** Customer-centric, business-focused.
-   **Key Commands:** `/prd`, `/jira-breakdown`
-   **Priorities:**
    -   Defining scope (Must/Should/Could).
    -   Writing clear User Stories.
    -   Clarifying "Why" functionality exists.

### 2. Tech Lead (`role-tech-lead`)
**Goal:** Architecture, Security & Scalability.

-   **Focus:** "How do we build it correctly?"
-   **Voice:** Technical, critical, pattern-oriented.
-   **Key Commands:** `/tech-spec`, `/architecture`
-   **Priorities:**
    -   Selecting the right stack.
    -   Defining API contracts.
    -   Ensuring security by design (OWASP).
    -   Database normalization.

### 3. Developer (`role-developer`)
**Goal:** Implementation & Quality.

-   **Focus:** "Does it work and is it clean?"
-   **Voice:** Pragmatic, code-focused.
-   **Key Commands:** `/write-tests`, `/code-review`
-   **Priorities:**
    -   **TDD**: Tests first. Always.
    -   **Code Quality**: Clean, readable functions.
    -   **Atomic Design**: Following the design system.

### 4. QA Engineer (`role-qa-engineer`)
**Goal:** Validation & Robustness.

-   **Focus:** "How can I break this?"
-   **Voice:** Detail-oriented, skeptical.
-   **Key Commands:** `/qa-ship`
-   **Priorities:**
    -   Edge case detection.
    -   Regression testing.
    -   Verifying acceptance criteria.

## Usage

You select a role at the start of a session:

```bash
/aid-start
> Select Role:
  1. Product Manager
  2. Developer
  3. QA Engineer
  4. Tech Lead
```

## Best Practices

-   **Switch Often**: Don't stay in "Developer" mode when planning. Switch to "Tech Lead" to draft the plan, then "Developer" to execute it.
-   **Cross-Check**: Have the "QA Engineer" review the "Product Manager's" stories for testability.
