# Memory System Section for CLAUDE.md

Add this section to your existing CLAUDE.md file.

---

## Memory System

AID includes a learning system that improves Claude's assistance over time by collecting feedback, detecting patterns, and updating skills.

### Quick Commands

| Command | Description |
|---------|-------------|
| `/aid init` | Initialize memory system (first time only) |
| `/aid start` | Start work session - select role & phase |
| `/aid status` | Show current state |
| `/aid end` | End phase and provide feedback |
| `/aid improve` | Run learning cycle (weekly) |
| `/aid memory list` | Show Claude Memory entries |

### Session Flow

1. **Start**: `/aid start` → Select role (PM/Dev/QA/Lead) → Select phase → Skills loaded
2. **Work**: Claude applies loaded skills automatically
3. **End**: `/aid end` → Rate session (1-5) → Describe what worked/didn't
4. **Learn**: `/aid improve` → Analyze feedback → Update skills → Promote to memory

### Skills Location

Claude loads skills based on role and phase:
- Role skills: `memory-system/skills/roles/{role}/SKILL.md`
- Phase skills: `memory-system/skills/phases/{phase}/SKILL.md`

At session start, read both relevant skill files and apply their guidelines.

### Runtime State

Session state stored in `~/.aid/state.json`:
- Current role and phase
- Session start time
- Task and step tracking

### Feedback Collection

At phase end (`/aid end`):
1. Summarize work completed
2. Ask for rating (1-5)
3. Ask: "What worked well?"
4. Ask: "What could be improved?"
5. Save to `~/.aid/feedback/pending/`

### Improvement Cycle

When `/aid improve` is called:
1. Analyze pending feedback (need 3+ items)
2. Detect patterns across sessions
3. Suggest skill updates
4. Promote insights to Claude Memory

### Claude Memory Entries

AID uses Claude Memory for persistent cross-session learning.
Entry format: `AID:{ROLE}:{PHASE}:{TYPE} {insight}`

Categories and slots:
- Universal: 5 slots
- PM/Dev/QA: 5 slots each
- Lead: 3 slots
- Phase-specific: 5 slots
- Learned (dynamic): 10 slots

### Documentation

Full documentation: `memory-system/docs/`
- USER-GUIDE.md - Complete usage guide
- COMMANDS.md - All commands detailed
- TROUBLESHOOTING.md - Common issues

---
