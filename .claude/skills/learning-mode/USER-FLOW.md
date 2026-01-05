# Learning Mode - User Flow

## Master Flow

```
User Request -> Analyze Decision Type
  -> Simple: Execute directly
  -> Significant: Check alternatives
    -> Single Clear: Decision Transparency
    -> Multiple Viable: Debate Invitation
    -> User vs Best Practice: Respectful Counter-point
-> Execute Work
-> Work Complete?
  -> Minor: Continue
  -> Major Milestone: Request Feedback
    -> Positive: Continue
    -> Correction: Capture Learning
```

## Flow 1: Decision Transparency

```
Significant Decision -> Transparent?
  -> Yes (Arch/Tech/Trade-offs/Scope): Create Transparency Block
  -> No (Syntax/Standard/No alternatives): Execute without ceremony
-> Assess Confidence
  -> High: Execute
  -> Medium: Execute + note concern
  -> Low: Invite debate
  -> Uncertain: Ask clarifying question
```

## Flow 2: Feedback Collection

```
Trigger (Phase Gate / Major Deliverable / Session End)
-> Create Feedback Request Block
-> User Response
  -> Rating 4-5: Acknowledge, continue
  -> Rating 3: Ask for improvement suggestions
  -> Rating 1-2: Request specific corrections
-> Capture Learning if needed
-> Continue Work
```

## Flow 3: Debate Invitation

```
Multiple Options -> Evaluate Viability
  -> One clear winner (>70%): Use Decision Transparency
  -> Multiple viable (<70%): Create Debate Invitation
-> User Response
  -> Picks Option A/B: Execute + Document why
  -> Wants more info: Provide deeper analysis
-> Capture learning about preference
```

## Flow 4: Phase Gate Learning

```
Phase Work Complete
-> Prepare Phase Summary
-> Create Feedback Request (deliverables, seeking feedback, questions, rating)
-> User Response
  -> Approved (>=3): Capture notes, advance phase
  -> Needs Revision (<3): List items, return to phase work
```

## Flow 5: Learning Capture

```
User Provides Correction/Preference
-> Identify Category (Process/Technical/Style/Domain)
-> Create Learning Capture Block
-> Store in Session Memory
-> Apply to Future Work
```

## Integration Points

- Phase Enforcement: Request feedback at gate
- Code Review: Debate on significant findings
- System Architect: Transparency on all architecture decisions
