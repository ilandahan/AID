# Learning Mode - User Flow Diagrams

Visual flows for decision transparency, feedback collection, and debate invitation.

## Master Flow: Learning Mode Integration

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    LEARNING MODE MASTER FLOW                            │
└─────────────────────────────────────────────────────────────────────────┘

User Request Received
        │
        ▼
┌───────────────────┐
│ Analyze Request   │
│ for Decision Type │
└───────────────────┘
        │
        ├─────────────────────────────────────────────────────────┐
        │                                                          │
        ▼                                                          ▼
┌───────────────────┐                                    ┌───────────────────┐
│ Simple/Obvious    │                                    │ Significant       │
│ Decision          │                                    │ Decision          │
└───────────────────┘                                    └───────────────────┘
        │                                                          │
        ▼                                                          ▼
┌───────────────────┐                                    ┌───────────────────┐
│ Execute directly  │                                    │ Check for         │
│ (no ceremony)     │                                    │ alternatives      │
└───────────────────┘                                    └───────────────────┘
        │                                                          │
        │                              ┌───────────────────────────┼───────────────────────────┐
        │                              │                           │                           │
        │                              ▼                           ▼                           ▼
        │                    ┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
        │                    │ Single Clear    │         │ Multiple Viable │         │ User Preference │
        │                    │ Best Option     │         │ Options         │         │ vs Best Practice│
        │                    └─────────────────┘         └─────────────────┘         └─────────────────┘
        │                              │                           │                           │
        │                              ▼                           ▼                           ▼
        │                    ┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
        │                    │ Show Decision   │         │ Invite Debate   │         │ Respectful      │
        │                    │ Transparency    │         │ Block           │         │ Counter-point   │
        │                    └─────────────────┘         └─────────────────┘         └─────────────────┘
        │                              │                           │                           │
        └──────────────────────────────┴───────────────────────────┴───────────────────────────┘
                                                        │
                                                        ▼
                                              ┌─────────────────┐
                                              │ Execute Work    │
                                              └─────────────────┘
                                                        │
                                                        ▼
                                              ┌─────────────────┐
                                              │ Work Complete?  │
                                              └─────────────────┘
                                                        │
                                       ┌────────────────┴────────────────┐
                                       │                                 │
                                       ▼                                 ▼
                              ┌─────────────────┐               ┌─────────────────┐
                              │ Minor Work      │               │ Major Milestone │
                              │ (continue)      │               │ or Phase Gate   │
                              └─────────────────┘               └─────────────────┘
                                       │                                 │
                                       │                                 ▼
                                       │                        ┌─────────────────┐
                                       │                        │ Request         │
                                       │                        │ Feedback        │
                                       │                        └─────────────────┘
                                       │                                 │
                                       │                                 ▼
                                       │                        ┌─────────────────┐
                                       │                        │ User Response   │
                                       │                        └─────────────────┘
                                       │                                 │
                                       │                    ┌────────────┴────────────┐
                                       │                    │                         │
                                       │                    ▼                         ▼
                                       │           ┌─────────────────┐       ┌─────────────────┐
                                       │           │ Positive/       │       │ Correction/     │
                                       │           │ Neutral         │       │ Improvement     │
                                       │           └─────────────────┘       └─────────────────┘
                                       │                    │                         │
                                       │                    │                         ▼
                                       │                    │                ┌─────────────────┐
                                       │                    │                │ Capture         │
                                       │                    │                │ Learning        │
                                       │                    │                └─────────────────┘
                                       │                    │                         │
                                       └────────────────────┴─────────────────────────┘
                                                            │
                                                            ▼
                                                  ┌─────────────────┐
                                                  │ Continue or     │
                                                  │ End Session     │
                                                  └─────────────────┘
```

---

## Flow 1: Decision Transparency

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    DECISION TRANSPARENCY FLOW                           │
└─────────────────────────────────────────────────────────────────────────┘

Significant Decision Identified
            │
            ▼
┌───────────────────────┐
│ Is this decision      │
│ type transparent?     │
└───────────────────────┘
            │
            ├───────────────────────────────────────────┐
            │                                           │
            ▼                                           ▼
┌───────────────────────┐                    ┌───────────────────────┐
│ YES - Show reasoning: │                    │ NO - Simple choice:   │
│ • Architecture        │                    │ • Obvious syntax      │
│ • Technology choices  │                    │ • Standard patterns   │
│ • Trade-offs          │                    │ • No alternatives     │
│ • Scope decisions     │                    │                       │
└───────────────────────┘                    └───────────────────────┘
            │                                           │
            ▼                                           ▼
┌───────────────────────┐                    ┌───────────────────────┐
│ Create Transparency   │                    │ Execute without       │
│ Block:                │                    │ ceremony              │
│                       │                    │                       │
│ <decision-transparency>                    └───────────────────────┘
│ **Decision:** ...     │
│ **Reasoning:** ...    │
│ **Alternatives:** ... │
│ **Confidence:** ...   │
│ **Open to Debate:** ..│
│ </decision-transparency>
└───────────────────────┘
            │
            ▼
┌───────────────────────┐
│ Assess Confidence     │
│ Level                 │
└───────────────────────┘
            │
    ┌───────┼───────┬───────────────┐
    │       │       │               │
    ▼       ▼       ▼               ▼
┌───────┐ ┌───────┐ ┌───────┐ ┌───────────────┐
│ HIGH  │ │MEDIUM │ │ LOW   │ │ UNCERTAIN     │
│       │ │       │ │       │ │               │
│Execute│ │Execute│ │Invite │ │Ask clarifying │
│       │ │+ note │ │debate │ │question first │
│       │ │concern│ │       │ │               │
└───────┘ └───────┘ └───────┘ └───────────────┘
```

---

## Flow 2: Feedback Collection

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    FEEDBACK COLLECTION FLOW                             │
└─────────────────────────────────────────────────────────────────────────┘

Trigger Event
     │
     ├─────────────────────────────────────────────────────────────┐
     │                           │                                 │
     ▼                           ▼                                 ▼
┌───────────┐            ┌───────────────┐              ┌───────────────┐
│Phase Gate │            │Major          │              │Session        │
│Reached    │            │Deliverable    │              │Ending         │
└───────────┘            └───────────────┘              └───────────────┘
     │                           │                                 │
     └───────────────────────────┴─────────────────────────────────┘
                                 │
                                 ▼
                    ┌───────────────────────┐
                    │ Create Feedback       │
                    │ Request Block         │
                    │                       │
                    │ <feedback-request>    │
                    │ **Context:** ...      │
                    │ **Seeking On:** ...   │
                    │ **Questions:** ...    │
                    │ **Rating:** 1-5       │
                    │ </feedback-request>   │
                    └───────────────────────┘
                                 │
                                 ▼
                    ┌───────────────────────┐
                    │ Wait for User         │
                    │ Response              │
                    └───────────────────────┘
                                 │
            ┌────────────────────┼────────────────────┐
            │                    │                    │
            ▼                    ▼                    ▼
    ┌───────────────┐   ┌───────────────┐   ┌───────────────┐
    │ Rating: 4-5   │   │ Rating: 3     │   │ Rating: 1-2   │
    │ (Positive)    │   │ (Neutral)     │   │ (Needs Work)  │
    └───────────────┘   └───────────────┘   └───────────────┘
            │                    │                    │
            ▼                    ▼                    ▼
    ┌───────────────┐   ┌───────────────┐   ┌───────────────┐
    │ Acknowledge   │   │ Ask for       │   │ Request       │
    │ Continue      │   │ improvement   │   │ specific      │
    │               │   │ suggestions   │   │ corrections   │
    └───────────────┘   └───────────────┘   └───────────────┘
            │                    │                    │
            │                    └─────────┬─────────┘
            │                              │
            │                              ▼
            │                    ┌───────────────────┐
            │                    │ Capture Learning  │
            │                    │                   │
            │                    │ <learning-captured>
            │                    │ **What:** ...     │
            │                    │ **Source:** ...   │
            │                    │ **Applied:** ...  │
            │                    │ </learning-captured>
            │                    └───────────────────┘
            │                              │
            └──────────────────────────────┘
                           │
                           ▼
                 ┌───────────────────┐
                 │ Continue Work     │
                 └───────────────────┘
```

---

## Flow 3: Debate Invitation

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    DEBATE INVITATION FLOW                               │
└─────────────────────────────────────────────────────────────────────────┘

Multiple Options Identified
            │
            ▼
┌───────────────────────┐
│ Evaluate Options      │
│ for Viability         │
└───────────────────────┘
            │
    ┌───────┴───────────────────────────────────┐
    │                                           │
    ▼                                           ▼
┌───────────────────────┐            ┌───────────────────────┐
│ One clear winner      │            │ Multiple viable       │
│ (>70% confidence)     │            │ options (<70%)        │
└───────────────────────┘            └───────────────────────┘
    │                                           │
    ▼                                           ▼
┌───────────────────────┐            ┌───────────────────────┐
│ Use Decision          │            │ Create Debate         │
│ Transparency Flow     │            │ Invitation Block      │
│ (show why)            │            │                       │
└───────────────────────┘            │ <debate-invitation>   │
                                     │ **Topic:** ...        │
                                     │ **Option A:** ...     │
                                     │ **Option B:** ...     │
                                     │ **My Lean:** ...      │
                                     │ **But Consider:** ... │
                                     │ **Your Input:** ...   │
                                     │ </debate-invitation>  │
                                     └───────────────────────┘
                                                │
                                                ▼
                                     ┌───────────────────────┐
                                     │ Wait for User         │
                                     │ Response              │
                                     └───────────────────────┘
                                                │
                          ┌─────────────────────┼─────────────────────┐
                          │                     │                     │
                          ▼                     ▼                     ▼
                  ┌───────────────┐     ┌───────────────┐     ┌───────────────┐
                  │ User picks    │     │ User picks    │     │ User wants    │
                  │ Option A      │     │ Option B      │     │ more info     │
                  └───────────────┘     └───────────────┘     └───────────────┘
                          │                     │                     │
                          ▼                     ▼                     ▼
                  ┌───────────────┐     ┌───────────────┐     ┌───────────────┐
                  │ Execute A     │     │ Execute B     │     │ Provide       │
                  │ + Document    │     │ + Document    │     │ deeper        │
                  │ why           │     │ why           │     │ analysis      │
                  └───────────────┘     └───────────────┘     └───────────────┘
                          │                     │                     │
                          └─────────────────────┴──────────┬──────────┘
                                                           │
                                                           ▼
                                                ┌───────────────────┐
                                                │ Capture learning  │
                                                │ about preference  │
                                                └───────────────────┘
```

---

## Flow 4: Phase Gate Learning

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    PHASE GATE LEARNING FLOW                             │
└─────────────────────────────────────────────────────────────────────────┘

Phase Work Complete
        │
        ▼
┌───────────────────┐
│ Prepare Phase     │
│ Summary           │
└───────────────────┘
        │
        ▼
┌───────────────────────────────────────────────────────────────┐
│ <feedback-request>                                            │
│ **Context:** Phase [N] - [Name] completed                     │
│                                                               │
│ **Phase Deliverables:**                                       │
│ - [Deliverable 1]                                             │
│ - [Deliverable 2]                                             │
│ - [Deliverable 3]                                             │
│                                                               │
│ **Seeking Feedback On:**                                      │
│ 1. Quality of deliverables                                    │
│ 2. Completeness of requirements                               │
│ 3. Readiness for next phase                                   │
│                                                               │
│ **Questions:**                                                │
│ - Did we miss any requirements?                               │
│ - Are the deliverables at the quality level expected?         │
│ - Any concerns before moving to [Next Phase]?                 │
│                                                               │
│ **Rating Request:** 1-5 for this phase                        │
│ **Improvement Ideas Welcome**                                 │
│ </feedback-request>                                           │
└───────────────────────────────────────────────────────────────┘
        │
        ▼
┌───────────────────┐
│ User Responds     │
└───────────────────┘
        │
        ├─────────────────────────────────────────┐
        │                                         │
        ▼                                         ▼
┌───────────────────┐                   ┌───────────────────┐
│ Approved          │                   │ Needs Revision    │
│ (Rating ≥ 3)      │                   │ (Rating < 3)      │
└───────────────────┘                   └───────────────────┘
        │                                         │
        ▼                                         ▼
┌───────────────────┐                   ┌───────────────────┐
│ Capture any       │                   │ List specific     │
│ improvement notes │                   │ items to address  │
└───────────────────┘                   └───────────────────┘
        │                                         │
        ▼                                         ▼
┌───────────────────┐                   ┌───────────────────┐
│ Advance to        │                   │ Return to phase   │
│ next phase        │                   │ work              │
└───────────────────┘                   └───────────────────┘
```

---

## Flow 5: Learning Capture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    LEARNING CAPTURE FLOW                                │
└─────────────────────────────────────────────────────────────────────────┘

User Provides Correction/Preference
                │
                ▼
      ┌───────────────────┐
      │ Identify Learning │
      │ Category          │
      └───────────────────┘
                │
    ┌───────────┼───────────┬───────────────┐
    │           │           │               │
    ▼           ▼           ▼               ▼
┌───────┐  ┌───────────┐ ┌───────────┐ ┌───────────────┐
│Process│  │Technical  │ │Style/     │ │Domain-        │
│Pref.  │  │Preference │ │Format     │ │Specific       │
└───────┘  └───────────┘ └───────────┘ └───────────────┘
    │           │           │               │
    └───────────┴───────────┴───────────────┘
                        │
                        ▼
          ┌───────────────────────┐
          │ Create Learning       │
          │ Capture Block         │
          │                       │
          │ <learning-captured>   │
          │ **What I Learned:**   │
          │ [specific learning]   │
          │                       │
          │ **Source:**           │
          │ - Context: [what]     │
          │ - Date: [when]        │
          │                       │
          │ **Applied To:**       │
          │ [how behavior changes]│
          │                       │
          │ **Verification:**     │
          │ [next application]    │
          │ </learning-captured>  │
          └───────────────────────┘
                        │
                        ▼
          ┌───────────────────────┐
          │ Store in Session      │
          │ Memory                │
          └───────────────────────┘
                        │
                        ▼
          ┌───────────────────────┐
          │ Apply to Future       │
          │ Work in Session       │
          └───────────────────────┘
```

---

## Integration Points

### With Phase Enforcement

```
Phase Gate Check
       │
       ▼
┌────────────────┐     ┌────────────────┐
│ Phase          │────►│ Learning Mode  │
│ Enforcement    │     │ Feedback       │
│ Skill          │◄────│ Request        │
└────────────────┘     └────────────────┘
       │
       ▼
Gate Pass/Fail + Learning Captured
```

### With Code Review

```
Code Review Findings
       │
       ▼
┌────────────────┐     ┌────────────────┐
│ Code Review    │────►│ Learning Mode  │
│ Skill          │     │ Debate         │
│                │◄────│ (if needed)    │
└────────────────┘     └────────────────┘
       │
       ▼
Review Complete + Preferences Learned
```

### With System Architect

```
Architecture Decision
       │
       ▼
┌────────────────┐     ┌────────────────┐
│ System         │────►│ Learning Mode  │
│ Architect      │     │ Transparency   │
│ Skill          │◄────│ Block          │
└────────────────┘     └────────────────┘
       │
       ▼
Decision Documented + Feedback Captured
```
