# Quality Feedback Reference

Detailed guide for the quality feedback collection and improvement system integrated with phase enforcement.

---

## Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                 QUALITY FEEDBACK CYCLE                          │
│                                                                 │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐      │
│  │  Work   │───▶│ /aid    │───▶│ Feedback│───▶│ /aid    │      │
│  │  Done   │    │  end    │    │ Stored  │    │ improve │      │
│  └─────────┘    └─────────┘    └─────────┘    └────┬────┘      │
│                                                     │           │
│                      ┌──────────────────────────────┘           │
│                      ▼                                          │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                 SKILL IMPROVEMENTS                       │   │
│  │  - Pattern analysis                                      │   │
│  │  - Skill updates                                         │   │
│  │  - Memory promotion                                      │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Feedback Collection (/aid end)

### Purpose
Collect structured feedback at the end of each phase to enable continuous improvement of skills and methodology.

### Flow

```
┌──────────────────────────────────────────────────────────────┐
│                   /aid end FLOW                              │
│                                                              │
│  1. Summarize Work                                           │
│     └── What was accomplished in this phase                  │
│                                                              │
│  2. Request Rating (1-5)                                     │
│     └── 1=Poor, 2=Below avg, 3=Average, 4=Good, 5=Excellent │
│                                                              │
│  3. Ask What Worked                                          │
│     └── Specific positives from this session                 │
│                                                              │
│  4. Ask What to Improve                                      │
│     └── Specific areas needing enhancement                   │
│                                                              │
│  5. Save Feedback                                            │
│     └── ~/.aid/feedback/pending/{timestamp}.json             │
│                                                              │
│  6. Confirm & Options                                        │
│     └── Continue, new session, or end                        │
└──────────────────────────────────────────────────────────────┘
```

### Feedback Schema

```typescript
interface PhaseFeedback {
  // Identification
  timestamp: string;          // ISO 8601 format
  session_id: string;         // UUID for session tracking

  // Phase Context
  phase: number;              // 1-5
  phase_name: string;         // "prd", "tech-spec", etc.
  feature_name: string;       // Feature being worked on

  // Deliverables
  document_path?: string;     // Path to created document
  artifacts?: string[];       // List of files created/modified

  // Quality Assessment
  rating: 1 | 2 | 3 | 4 | 5;  // User rating
  worked_well: string;        // What went well
  to_improve: string;         // What needs improvement

  // Metrics
  duration_minutes: number;   // Time spent on phase
  iterations: number;         // Revisions needed

  // Skill Reference
  skills_used?: string[];     // Skills invoked during phase
}
```

### Example Feedback

```json
{
  "timestamp": "2024-12-11T15:30:00Z",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "phase": 2,
  "phase_name": "tech-spec",
  "feature_name": "user-authentication",
  "document_path": "docs/tech-spec/2024-12-11-user-authentication.md",
  "artifacts": [
    "docs/tech-spec/2024-12-11-user-authentication.md",
    "diagrams/auth-flow.mermaid"
  ],
  "rating": 4,
  "worked_well": "Security architecture was comprehensive, API contracts were clear",
  "to_improve": "Could include more error handling scenarios",
  "duration_minutes": 145,
  "iterations": 2,
  "skills_used": ["system-architect"]
}
```

---

## Rating Scale

| Rating | Label | Description |
|--------|-------|-------------|
| 1 | Poor | Many issues, didn't meet expectations |
| 2 | Below Average | Some problems, partially met expectations |
| 3 | Average | Met basic expectations |
| 4 | Good | Exceeded expectations |
| 5 | Excellent | Outstanding results |

### Rating Prompts by Phase

**Phase 1 (PRD):**
```
How would you rate the PRD quality? (1-5)
Consider: Clarity, completeness, user stories, acceptance criteria
```

**Phase 2 (Tech Spec):**
```
How would you rate the Tech Spec quality? (1-5)
Consider: Architecture clarity, security coverage, API design
```

**Phase 3 (Implementation Plan):**
```
How would you rate the Implementation Plan? (1-5)
Consider: Task breakdown, estimates, test strategy, dependencies
```

**Phase 4 (Development):**
```
How would you rate the Development phase? (1-5)
Consider: Code quality, test coverage, documentation
```

**Phase 5 (QA & Ship):**
```
How would you rate the QA & Ship phase? (1-5)
Consider: Test thoroughness, deployment smoothness, documentation
```

---

## Feedback Analysis (/aid improve)

### Purpose
Analyze collected feedback to identify patterns and suggest improvements to skills and methodology.

### Requirements
- Minimum 3 feedback items in `~/.aid/feedback/pending/`
- Or use `--force` flag (will warn about limited data)

### Analysis Flow

```
┌──────────────────────────────────────────────────────────────┐
│                /aid improve FLOW                             │
│                                                              │
│  1. GATHER DATA                                              │
│     ├── Load ~/.aid/feedback/pending/*.json                  │
│     ├── Load current skills from skills/                     │
│     └── Load trends from ~/.aid/metrics/trends.json          │
│                                                              │
│  2. ANALYZE (Sub-Agent)                                      │
│     ├── Cluster feedback by role/phase                       │
│     ├── Identify recurring patterns                          │
│     ├── Detect common improvement requests                   │
│     └── Score confidence for each suggestion                 │
│                                                              │
│  3. PRESENT SUGGESTIONS                                      │
│     ├── Skill updates with confidence scores                 │
│     ├── Memory candidates for promotion                      │
│     └── Process improvements                                 │
│                                                              │
│  4. APPLY CHANGES (User Approved)                            │
│     ├── Update skill files                                   │
│     ├── Promote memory entries                               │
│     └── Archive processed feedback                           │
│                                                              │
│  5. SUMMARY                                                  │
│     └── Changes applied, feedback archived                   │
└──────────────────────────────────────────────────────────────┘
```

### Pattern Detection

The analysis sub-agent looks for these patterns:

```
┌──────────────────────────────────────────────────────────────┐
│              PATTERN DETECTION RULES                         │
│                                                              │
│  SKILL IMPROVEMENT PATTERNS:                                 │
│  - Same feedback mentioned in 3+ sessions                    │
│  - Rating < 3 with consistent reason                         │
│  - "to_improve" contains similar keywords                    │
│                                                              │
│  MEMORY PROMOTION PATTERNS:                                  │
│  - Insight mentioned in "worked_well" 3+ times               │
│  - High-rating sessions (4-5) with common practices          │
│  - Phase-specific best practices                             │
│                                                              │
│  PROCESS IMPROVEMENT PATTERNS:                               │
│  - Gate failures with common reasons                         │
│  - Override usage patterns                                   │
│  - Duration outliers (too long/short)                        │
└──────────────────────────────────────────────────────────────┘
```

### Suggestion Format

```
SKILL UPDATES SUGGESTED:

1. [system-architect Skill] Add error handling section
   Confidence: 85%
   Reason: 4/5 sessions mentioned need for error handling
   Impact: Phase 2 (Tech Spec)

   Suggested Addition:
   ---
   ### Error Handling Requirements
   - Define error codes for each API endpoint
   - Specify retry policies
   - Document fallback behaviors
   ---

   [Approve] [Edit] [Reject]

2. [phase-enforcement Skill] Add security checklist to Gate 2
   Confidence: 72%
   Reason: Security concerns raised in 3 sessions
   Impact: Gate 2 (Tech Spec → Impl Plan)

   [Approve] [Edit] [Reject]

MEMORY CANDIDATES:

1. "Always document error codes in Tech Spec before implementation"
   Category: system-architect
   Phase: 2 (Tech Spec)
   Confidence: 80%

   [Promote to Memory] [Skip]
```

---

## Feedback Storage

### Directory Structure

```
~/.aid/
├── feedback/
│   ├── pending/           # Unprocessed feedback
│   │   ├── 2024-12-11T10-00-00.json
│   │   └── 2024-12-11T15-30-00.json
│   └── processed/         # Archived after /aid improve
│       └── batch-2024-12-11.json
├── metrics/
│   └── trends.json        # Aggregated metrics
└── improvements/
    └── history.json       # Log of applied improvements
```

### Trends File

```json
{
  "total_sessions": 15,
  "average_rating": 3.8,
  "by_phase": {
    "1": { "count": 5, "avg_rating": 4.0, "avg_duration": 60 },
    "2": { "count": 4, "avg_rating": 3.5, "avg_duration": 120 },
    "3": { "count": 3, "avg_rating": 4.0, "avg_duration": 45 },
    "4": { "count": 2, "avg_rating": 3.5, "avg_duration": 240 },
    "5": { "count": 1, "avg_rating": 4.0, "avg_duration": 60 }
  },
  "common_improvements": [
    { "text": "error handling", "count": 4 },
    { "text": "more examples", "count": 3 }
  ],
  "common_positives": [
    { "text": "clear structure", "count": 5 },
    { "text": "security coverage", "count": 4 }
  ],
  "last_updated": "2024-12-11T16:00:00Z"
}
```

---

## Memory Promotion Format

When insights are promoted to Claude Memory:

```
AID:{SKILL}:{PHASE}:{TYPE} {insight}

Examples:
AID:system-architect:2:PATTERN Always include error codes in API specs
AID:phase-enforcement:3:GATE Check test strategy before advancing
AID:code-review:4:PRACTICE Review security before functionality
```

### Memory Categories

| Category | Description | Example |
|----------|-------------|---------|
| `PATTERN` | Recurring best practice | "Always validate inputs at API boundary" |
| `GATE` | Gate-specific requirement | "Security assessment required for Phase 2" |
| `PRACTICE` | Development practice | "Commit after each test passes" |
| `AVOID` | Anti-pattern to avoid | "Don't skip error handling in POCs" |

---

## Phase-Feedback Integration

Feedback collection is MANDATORY at each phase gate:

```
┌──────────────────────────────────────────────────────────────┐
│           PHASE-FEEDBACK ENFORCEMENT                         │
│                                                              │
│  Phase N Complete?                                           │
│       │                                                      │
│       ▼                                                      │
│  Gate Requirements Met?                                      │
│       │                                                      │
│       ├── No ──▶ Show missing requirements                   │
│       │                                                      │
│       ▼                                                      │
│  Feedback Collected?                                         │
│       │                                                      │
│       ├── No ──▶ Prompt: "Run /aid end before advancing"     │
│       │                                                      │
│       ▼                                                      │
│  ✅ Advance to Phase N+1                                     │
└──────────────────────────────────────────────────────────────┘
```

### State Tracking

```json
{
  "feedback_collected": {
    "phase_1": true,
    "phase_2": false,
    "phase_3": false,
    "phase_4": false,
    "phase_5": false
  },
  "feedback_pending_count": 5,
  "last_improvement_run": "2024-12-10T10:00:00Z"
}
```

---

## Commands

| Command | Description |
|---------|-------------|
| `/aid end` | Collect feedback for current phase |
| `/aid improve` | Run improvement analysis (3+ feedback) |
| `/aid improve --force` | Run with fewer than 3 feedback items |
| `/aid status` | Show feedback collection status |
