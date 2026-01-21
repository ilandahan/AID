# Questioning Patterns

Deep-dive techniques for uncovering the WHY.

## The 5 Whys (Root Cause Discovery)

Each "why" peels back a layer. Don't stop until you hit bedrock belief.

**Pattern:**
```
Statement: [Surface request]
  Why #1? → [Immediate reason]
  Why #2? → [Underlying goal]
  Why #3? → [Deeper motivation]
  Why #4? → [Core need]
  Why #5? → [ROOT WHY - bedrock belief]
```

**Example:**
```
"We need to add a loading spinner"
  Why? → "Users don't know if data is loading"
  Why? → "They think the app is broken and refresh"
  Why? → "Refreshing loses their input and frustrates them"
  Why? → "Frustrated users abandon tasks and churn"
  ROOT WHY: Trust. Users need confidence the system is responsive.

Insight: This isn't about spinners—it's about building trust through feedback.
```

## Inversion Technique

Sometimes WHY becomes clearer by defining what you're NOT.

**Pattern:**
```
"We're NOT [negative pattern]"
"We're NOT [competitor approach]"
"We're NOT [harmful tradeoff]"
Therefore, we ARE...
```

**Example:**
```
"We're NOT building another tool that overwhelms users with options"
"We're NOT competing on feature count"
"We're NOT sacrificing simplicity for power users"
Therefore, we ARE building opinionated defaults with escape hatches.
```

## Motivation Mapping Questions

### For Business Decisions
- "If this succeeds perfectly, what changes in the world?"
- "What would we never compromise on, even if it cost us?"
- "Why would someone choose us over the easiest alternative?"
- "What story do we want users to tell others about us?"

### For Feature Decisions
- "What problem disappears when this exists?"
- "What does the user feel before and after using this?"
- "Why this solution instead of ten other possibilities?"
- "What behavior change indicates success?"

### For Stakeholder Alignment
- "What's the underlying concern behind this request?"
- "What future are you trying to prevent?"
- "What future are you trying to create?"
- "What would make you feel this was right in 2 years?"

## Discovery Interview Pattern

**Opening (Establish Context):**
```
"Before we discuss what to build, I'd like to understand the deeper 
context. What made this feel important enough to prioritize now?"
```

**Deepening (Follow the Thread):**
```
"You mentioned [X]. What's behind that?"
"When you say 'better,' what does better look like specifically?"
"Who else cares about this, and why do they care?"
```

**Validating (Test the WHY):**
```
"So if I understand correctly, the core belief here is [WHY]. 
If we held that belief but couldn't build [WHAT], what else might we do?"
```

**Closing (Anchor the WHY):**
```
"Let me reflect back what I heard as the WHY: [statement]. 
Does that capture it? What would you adjust?"
```

## Alignment Check Pattern

When stakeholders seem misaligned:

1. Have each stakeholder independently answer: "Why does this matter? In one sentence."
2. Share and compare answers
3. Explore differences: "Person A emphasized [X], Person B emphasized [Y]. What's driving that?"
4. Find shared root: "What's the deeper WHY both perspectives serve?"

## Prioritization Filter

When deciding between options, ask for each:

1. "How directly does this serve our WHY?"
2. "Does this strengthen or dilute our purpose?"
3. "Would someone who deeply understands our WHY choose this?"
4. "What would we have to believe for this to be right?"

## Anti-Patterns to Detect

### The False WHY
- Sounds good but isn't authentic
- Doesn't actually guide decisions
- Everyone nods but behavior doesn't change

**Test:** "Would we still do this if no one was watching?"

### The Too-Broad WHY
- "We want to make the world better"
- Can justify any decision

**Test:** "Does this WHY exclude anything?"

### The Retrofitted WHY
- Invented after the decision to justify it
- Changes to fit whatever's convenient

**Test:** "Did we ask WHY before deciding, or after?"

### The Aspirational-Only WHY
- Beautiful statement, no operational impact
- Lives on the wall, not in decisions

**Test:** "Can a team member explain how their current task serves this WHY?"
