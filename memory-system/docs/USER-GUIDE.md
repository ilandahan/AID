# AID Memory System - User Guide

> Complete guide to using the AID Memory System for continuous improvement.

---

## What is AID Memory?

AID Memory is a **learning system** that helps Claude get better at helping you over time. It:

1. **Collects feedback** at the end of each work phase
2. **Identifies patterns** in what works and what doesn't
3. **Updates skills** with proven insights
4. **Promotes top patterns** to permanent Claude Memory

**Result**: Each session benefits from learnings across all your previous sessions.

---

## Quick Start

### First Time Setup

```
/aid init
```

This creates your personal `~/.aid/` directory with:
- Skill files for each role and phase
- Configuration for feedback collection
- 20 starter Claude Memory entries

### Starting a Session

**Option 1: Interactive**
```
/aid start
```
System asks which role and phase you're working in.

**Option 2: Direct**
```
/aid start pm discovery
```
Starts immediately as Product Manager in Discovery phase.

### During Work

Just work normally! The system:
- Applies relevant skills automatically
- Tracks revision requests internally
- Notes positive patterns when you praise outputs

### Ending a Phase

When you complete your work:

```
/aid end
```

Or use natural phrases:
- "done", "approved", "complete this phase"
- "finished", "looks good", "ship it"

The system will:
1. Summarize what was completed
2. Ask for a rating (1-5) - **Required!**
3. Ask for optional feedback
4. Save everything for pattern analysis

---

## Roles & Phases

### Available Roles

| Code | Role | When to Use |
|------|------|-------------|
| `pm` | Product Manager | Requirements, user stories, PRDs |
| `dev` | Developer | Technical specs, implementation |
| `qa` | QA Engineer | Test planning, quality assurance |
| `lead` | Tech Lead | Architecture, code review |

### Available Phases

| Code | Phase | Deliverables |
|------|-------|--------------|
| `discovery` | Discovery | Problem definition, stakeholder map |
| `prd` | PRD | Requirements document |
| `tech-spec` | Tech Spec | Technical design |
| `development` | Development | Code, tests |
| `qa-ship` | QA & Ship | Test results, deployment |

### Examples

```
/aid start pm discovery    # PM doing problem discovery
/aid start dev tech-spec   # Developer writing technical spec
/aid start qa qa-ship      # QA engineer testing before release
```

---

## The Feedback Loop

### Rating Scale

| Rating | Meaning | Typical Revisions |
|--------|---------|-------------------|
| 5 ⭐⭐⭐⭐⭐ | Perfect, no changes needed | 0 |
| 4 ⭐⭐⭐⭐ | Good, minor tweaks only | 1-2 |
| 3 ⭐⭐⭐ | Acceptable, some rework | 2-3 |
| 2 ⭐⭐ | Below expectations, significant rework | 4+ |
| 1 ⭐ | Missed the mark, start over | Many |

### What Makes Good Feedback

**Good feedback (helps improvement):**
- "SCQ format was very clear"
- "Missed stakeholders in first draft"
- "TDD approach reduced bugs"

**Less useful feedback:**
- "It was fine"
- "Good job"
- "Needs improvement"

### Feedback Questions

1. **What worked well?**
   - What should the system keep doing?
   - What patterns led to good results?

2. **What didn't work?**
   - What needed revision?
   - What was missing or wrong?

3. **Additional notes:**
   - Specific tips for the future
   - Context that might help

---

## Improvement Cycles

### When to Run Improvement

The system suggests improvement when:
- 10+ sessions since last improvement, OR
- 50+ pending feedback items

You'll see:
```
💡 Enough feedback for analysis.
   Run /aid improve before we start?
```

### Running Improvement

```
/aid improve
```

**The process:**

1. **Analysis Summary**
   ```
   📊 Feedback Analysis Summary
   
   Analyzed: 12 feedback items
   Period: 2025-01-01 to 2025-01-15
   
   Averages:
   • Rating: 3.8 (↑ from previous)
   • Revisions: 2.1 (↓ from previous)
   
   Found:
   • 3 positive patterns to reinforce ✅
   • 2 negative patterns to address ⚠️
   ```

2. **Review Each Suggestion**
   
   For each pattern found, you decide:
   - **Approve** ✓ - Add to skills
   - **Edit** 📝 - Modify before adding
   - **Reject** ✗ - Don't add
   - **Skip** ⏭️ - Decide later

3. **Apply Changes**
   
   Approved changes update:
   - Skill files (cumulative.md)
   - Claude Memory (if meets promotion criteria)

4. **Summary**
   ```
   ✅ Improvement Complete!
   
   • 2 skill file updates
   • 1 Claude Memory update
   
   Changes take effect next session. 🚀
   ```

---

## Claude Memory Integration

### What Gets Promoted

Patterns are promoted to Claude Memory when:
- Used in **5+ sessions**
- Average rating **≥ 4.0** when used
- Average revisions **≤ 2.0** when used
- You **approve** the promotion

### Memory Entry Format

```
AID:{ROLE}:{PHASE}:{TYPE} {insight}
```

Examples:
```
AID:PM:DISC:ASK "Who else touches this data?" for stakeholders
AID:DEV:DEV:DO Write test first, then implement (TDD)
AID:QA:QA:DONT Never weaken tests to make them pass
```

### Viewing Your Memory

```
/aid memory list
```

Shows all AID:* entries organized by category.

```
/aid memory stats
```

Shows slot allocation and top performers.

---

## Commands Reference

### Session Commands

| Command | Description |
|---------|-------------|
| `/aid init` | Initialize system (first time) |
| `/aid start [role] [phase]` | Start new session |
| `/aid status` | Show current state |
| `/aid end` | Complete phase gate |

### Improvement Commands

| Command | Description |
|---------|-------------|
| `/aid improve` | Run pattern analysis |
| `/aid stats [period]` | Show metrics |

### Skill Commands

| Command | Description |
|---------|-------------|
| `/aid skill view [type]` | View skill content |
| `/aid skill edit [type]` | Edit skill file |
| `/aid skill sync` | Sync with repo |

### Memory Commands

| Command | Description |
|---------|-------------|
| `/aid memory list` | Show all entries |
| `/aid memory stats` | Show allocation |

### Admin Commands

| Command | Description |
|---------|-------------|
| `/aid reset --confirm` | Reset all data |
| `/aid export` | Export backup |

---

## Best Practices

### 1. Rate Honestly

Don't inflate ratings. The system learns from:
- Low ratings → What to avoid
- High ratings → What to repeat

Inflated ratings = wrong lessons learned.

### 2. Be Specific in Feedback

Instead of: "It was good"
Write: "SCQ format made the problem statement very clear"

Instead of: "Needs work"
Write: "Missed the IT department as a stakeholder"

### 3. Run Improvement Regularly

When the system suggests improvement, do it!
- Keeps skills fresh
- Prevents feedback backlog
- Promotes best patterns to memory

### 4. Review Suggestions Carefully

Before approving, ask:
- Is this pattern generalizable?
- Will it help in other projects?
- Is it specific enough to follow?

### 5. Don't Skip Phase Gates

Every phase gate = valuable feedback.
Even quick sessions help the system learn.

---

## File Locations

All data stored under `~/.aid/`:

```
~/.aid/
├── config.yaml           # Your preferences
├── state.json            # Current session state
├── skills/
│   ├── roles/            # Role-specific skills
│   └── phases/           # Phase-specific skills
├── feedback/
│   ├── pending/          # Awaiting analysis
│   └── processed/        # Already analyzed
└── metrics/
    ├── trends.json       # Historical stats
    └── memory-tracking.json  # Memory management
```

---

## Privacy & Data

### What's Collected

- Role and phase (no project names)
- Rating (1-5)
- Revision count
- Generic qualitative feedback

### What's NOT Collected

- Project names
- Company names
- Code snippets
- File paths
- Domain-specific details

### Where Data Lives

- All data stays in `~/.aid/` on your system
- Claude Memory entries are in your Anthropic account
- Nothing is sent externally

### Deleting Data

```
/aid reset --confirm
```

Or manually delete `~/.aid/` directory.

---

## FAQ

**Q: Do I have to rate every session?**
A: Yes, the rating is required. It's the primary signal for pattern detection.

**Q: What if I forget to end a phase?**
A: Run `/aid end` when you remember, or feedback won't be collected.

**Q: Can I edit skill files directly?**
A: Yes! Use `/aid skill edit [type]` or edit files directly in `~/.aid/skills/`.

**Q: How long until I see improvements?**
A: After 10+ sessions and running `/aid improve`, you'll see patterns.

**Q: What if a pattern doesn't apply to my next project?**
A: Patterns should be general. If too specific, don't approve promotion.

**Q: Can I use this with multiple projects?**
A: Yes! The system learns patterns that work across projects.

**Q: Is this only for Claude Code?**
A: Designed for Claude Code, but the skill files work in any Claude interface.
