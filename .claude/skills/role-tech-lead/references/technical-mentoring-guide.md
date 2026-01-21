# Technical Mentoring Guide

## Mentoring Principles

### 1. Guide, Don't Dictate
- Ask questions that lead to discovery
- Let them find the answer when possible
- Explain the WHY behind decisions
- Share your thought process

### 2. Meet Them Where They Are
- Assess current skill level
- Adapt explanation complexity
- Build on existing knowledge
- Progress incrementally

### 3. Create Safety
- It's okay to not know
- Mistakes are learning opportunities
- No question is stupid
- Celebrate growth

## Mentoring Techniques

### Socratic Method
Ask questions to guide understanding:

```
Developer: "Should I use REST or GraphQL?"

Instead of: "Use REST because X"

Ask:
- "What are the client's data needs?"
- "How many roundtrips does the current design require?"
- "What's the team's experience with each?"
- "What are the trade-offs you see?"
```

### Pair Programming
Side-by-side coding sessions:

```markdown
## Roles

### Navigator (Mentor)
- Think strategically
- Suggest direction
- Ask guiding questions
- Watch for issues

### Driver (Mentee)
- Write the code
- Think tactically
- Ask for clarification
- Make decisions

## Rotate roles every 25-30 minutes
```

### Code Walkthroughs
Developer explains their code:

```markdown
## Format (30 min)

1. Developer presents (15 min)
   - Context and problem
   - Solution approach
   - Code walkthrough
   - Open questions

2. Discussion (10 min)
   - Questions from mentor
   - Alternative approaches
   - Best practices

3. Action items (5 min)
   - Improvements to make
   - Topics to study
   - Next review date
```

### Rubber Duck Debugging
Help them articulate the problem:

```
Developer: "It's not working"

Mentor:
- "Walk me through what you expect to happen"
- "Now walk me through what actually happens"
- "At what point do they diverge?"
- "What have you tried so far?"
- "What do you think might be causing it?"
```

## Skill Development Areas

### Junior Developer Focus
- Clean code fundamentals
- Testing basics
- Debugging techniques
- Git workflow
- Code review etiquette
- Reading documentation

### Mid-Level Developer Focus
- Design patterns
- System design basics
- Performance optimization
- Security awareness
- Technical communication
- Ownership and initiative

### Senior Developer Focus
- Architecture decisions
- Technical leadership
- Mentoring others
- Cross-team collaboration
- Strategic thinking
- Handling ambiguity

## Growth Conversations

### Weekly 1:1 Template
```markdown
## 1:1 Notes - [Date]

### Current Work
- What are you working on?
- Any blockers?
- What went well this week?
- What was challenging?

### Growth
- What did you learn this week?
- What skill do you want to develop?
- How can I help?

### Feedback
- [Specific feedback on recent work]
- [Recognition for good work]

### Action Items
- [ ] [Action for mentee]
- [ ] [Action for mentor]
```

### Career Development Template
```markdown
## Career Development - [Name]

### Current State
- Role: [Current role]
- Strengths: [List]
- Growth areas: [List]

### Goals (Next 6-12 months)
1. [Goal 1]
2. [Goal 2]
3. [Goal 3]

### Development Plan
| Skill | Current | Target | How | Timeline |
|-------|---------|--------|-----|----------|
| [Skill] | 2/5 | 4/5 | [Activity] | [Date] |

### Projects for Growth
- [Project that stretches them]
- [Project that builds new skill]

### Check-in Dates
- [ ] Month 1: [Date]
- [ ] Month 3: [Date]
- [ ] Month 6: [Date]
```

## Handling Common Situations

### Developer is Stuck
```markdown
1. Let them explain what they've tried
2. Ask: "What do you think the problem is?"
3. Guide with questions, not answers
4. If still stuck after 15 min, give a hint
5. If still stuck after 30 min, pair on it
6. After solving, debrief: "What did we learn?"
```

### Developer Made a Mistake
```markdown
1. Don't shame or blame
2. Focus on the learning
3. "What happened?"
4. "What would you do differently?"
5. "How can we prevent this in the future?"
6. Help them fix it, don't fix it for them
```

### Developer Wants to Use New Technology
```markdown
1. "What problem does this solve?"
2. "What are the trade-offs?"
3. "What's the team's experience?"
4. "Have you built a prototype?"
5. If reasonable: "Let's spike it"
6. If not: Explain why, suggest alternative
```

### Developer Disagrees with Your Decision
```markdown
1. Listen to their reasoning
2. "Help me understand your concern"
3. Explain your reasoning
4. Find common ground
5. If still disagree:
   - Small decision: "Let's try your way"
   - Big decision: "I hear you, but we'll go with X because..."
   - Document reasoning for future reference
```

## Recognition & Feedback

### Effective Praise
```markdown
✅ Specific: "The way you handled the edge cases in the payment flow was thorough"
✅ Timely: Right after the good work
✅ Public: In team channels when appropriate

❌ Generic: "Good job"
❌ Delayed: Weeks later
❌ Always private: Others don't see recognition
```

### Constructive Feedback
```markdown
## SBI Model

**Situation**: "In yesterday's code review..."
**Behavior**: "...you dismissed the junior dev's suggestion without explaining why..."
**Impact**: "...which made them hesitant to contribute ideas."

## Follow-up
"What do you think?" (Let them reflect)
"How could we handle it differently next time?"
```

## Resources to Share

### Books
- Clean Code (Robert Martin)
- The Pragmatic Programmer
- Designing Data-Intensive Applications
- System Design Interview

### Practices
- Daily coding challenges
- Open source contributions
- Tech blog reading
- Conference talks
- Side projects
