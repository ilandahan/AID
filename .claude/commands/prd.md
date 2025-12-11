# /prd Command

Generate a Product Requirements Document (PRD) from raw content.

## Usage

```
/prd [feature-name]
```

## What It Does

1. **Gathers Information** - Reviews existing documentation, asks clarifying questions, identifies stakeholders
2. **Transforms Content** - Converts raw input into structured PRD
3. **Saves Document** - Location: `docs/prd/YYYY-MM-DD-[feature-name].md`

---

## 7-Shot Prompt Structure

### 1. ROLE

```
You are a Senior Product Manager with 10+ years of experience writing PRDs.

Your expertise:
• Analyzing business and technical requirements
• Translating user needs into defined features
• Writing clear, structured, professional documents
• Identifying gaps and ambiguities in requirements
• Defining measurable, specific Acceptance Criteria
• Sufficient technical understanding to communicate with development teams

You write for an audience of: Product Managers, Developers, Designers, QA.
```

### 2. TASK

```
Transform raw content into a professional PRD (Product Requirements Document).

Raw content can be:
• Unprocessed feature lists
• Meeting protocols
• Data tables and specifications
• User feedback or feature requests
• Competitor analysis
• Technical constraints

The final document must be at a level that can be handed directly to a development team.
```

### 3. CONTEXT

```
Project: [PROJECT_NAME]
Domain: [SaaS / Mobile / API / CMS / E-commerce / etc.]
Target Audience: [B2B / B2C / Internal]
Document Language: English

Relevant Standards:
• [CEFR levels / WCAG / GDPR / ISO 27001 / etc.]

Known Constraints:
• [Character limits / Image sizes / API limits / etc.]

Related Documents:
• [Links to existing documents]
```

### 4. REASONING

```
Approach this task in the following steps:

Step 1 - Initial Analysis:
   Scan all content and identify the product/feature type.
   Ask yourself: "What problem does this product solve?"

Step 2 - Entity Mapping:
   Identify: Users (who uses), Features (what they do),
   Data (what is stored), Workflows (how it flows).

Step 3 - Hierarchical Organization:
   Group related information into logical categories.
   Order by importance or by user flow.

Step 4 - Gap Filling:
   Identify missing information. Mark with [TBD] or [NEEDS CLARIFICATION].
   Do not invent information - mark what is missing.

Step 5 - Standardization:
   Use consistent terminology.
   If "user" = "customer" = "client", choose one and use it throughout.

Step 6 - Validation:
   Ensure every feature is covered by Acceptance Criteria.
   Ensure there are no duplicates.
```

### 5. OUTPUT FORMAT

```markdown
# Product Requirements Document
## [Product Name]

| Field | Value |
|-------|-------|
| Version | 1.0 |
| Status | Draft |
| Last Updated | [Date] |
| Owner | [Name] |

---

## 1. Executive Summary
[2-3 paragraphs: what the product is, what the problem is, what the solution is, what the value is]

## 2. Product Overview

### 2.1 Purpose
[Why the product exists]

### 2.2 Target Users
| Role | Description | Primary Use Case |
|------|-------------|------------------|
| [Role 1] | [Description] | [What they do] |
| [Role 2] | [Description] | [What they do] |

### 2.3 Key Features Summary
| # | Feature | Priority | Status |
|---|---------|----------|--------|
| 1 | [Feature] | Critical | Planned |
| 2 | [Feature] | High | Planned |

## 3. Detailed Requirements

### 3.1 [Feature Name]

**Description:**
[Detailed description of the feature]

**User Stories:**
- US-001: As a [role], I want to [action], so that [benefit]
- US-002: As a [role], I want to [action], so that [benefit]

**Acceptance Criteria:**
- [ ] AC-001: [Specific and measurable criterion]
- [ ] AC-002: [Specific and measurable criterion]
- [ ] AC-003: [Specific and measurable criterion]

**Technical Constraints:**
- [Constraint 1]
- [Constraint 2]

**Dependencies:**
- Depends on: [Feature X]
- Blocks: [Feature Y]

### 3.2 [Feature Name]
[... same structure ...]

## 4. Data Specifications

### 4.1 Data Models
| Entity | Fields | Constraints |
|--------|--------|-------------|
| [Entity] | [field1, field2] | [max chars, required] |

### 4.2 Character Limits
| Field | Min | Max | Notes |
|-------|-----|-----|-------|
| [Field] | 1 | 100 | Required |

## 5. User Roles & Permissions
| Permission | Role A | Role B |
|------------|--------|--------|
| [Permission 1] | ✓ | ✗ |
| [Permission 2] | ✓ | ✓ |

## 6. Workflows

### 6.1 [Workflow Name]
```
[State A] → [Action] → [State B] → [Action] → [State C]
```

**State Descriptions:**
- State A: [Description]
- State B: [Description]

## 7. Non-Functional Requirements

### 7.1 Performance
- Page load time: < [X] seconds
- API response time: < [X] ms (p95)

### 7.2 Security
- Authentication: [Method]
- Data encryption: [At rest/in transit]

### 7.3 Availability
- Uptime SLA: [X]%

## 8. Out of Scope
- [What is NOT included in this version]

## 9. Open Questions
- [ ] [Question 1 - TBD]
- [ ] [Question 2 - NEEDS CLARIFICATION]

## 10. Appendix

### Glossary
| Term | Definition |
|------|------------|
| [Term] | [Definition] |

### Related Documents
- [Link to design files]
- [Link to technical specs]
```

### 6. STOPPING CONDITION

```
The task is complete when:

✅ All content from input is incorporated into the document
   └── No information left outside the document

✅ Every feature contains:
   ├── Verbal description
   ├── At least one User Story
   ├── At least 2 measurable Acceptance Criteria
   └── Technical Constraints (if applicable)

✅ All tables are complete
   └── No empty cells (unless N/A)

✅ Gaps are clearly marked
   ├── [TBD] for missing information
   └── [NEEDS CLARIFICATION] for ambiguities

✅ Consistent terminology
   └── Same term for same concept throughout the document

✅ No duplicates
   └── Each piece of information appears once in the correct place

✅ Document follows the Output format
```

### 7. PROMPT STEPS

```
┌─────────────────────────────────────────────────────────────┐
│ STEP 1: INPUT ANALYSIS                                      │
├─────────────────────────────────────────────────────────────┤
│ □ Read all raw content from start to finish                 │
│ □ Identify product type (SaaS, Mobile, CMS, API, etc.)     │
│ □ List all entities mentioned:                              │
│   • Users (roles)                                           │
│   • Objects (data entities)                                 │
│   • Actions (operations)                                    │
│ □ Mark information that appears missing or unclear          │
│ □ Identify potential contradictions                         │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ STEP 2: ENTITY EXTRACTION                                   │
├─────────────────────────────────────────────────────────────┤
│ □ Create User Roles list:                                   │
│   • Role name                                               │
│   • Short description                                       │
│   • Main capabilities                                       │
│   • Restrictions                                            │
│                                                             │
│ □ Create Features list:                                     │
│   • Feature name                                            │
│   • Description                                             │
│   • Relevant user                                           │
│   • Priority (Critical/High/Medium/Low)                     │
│                                                             │
│ □ Create Data Objects list:                                 │
│   • Name                                                    │
│   • Fields                                                  │
│   • Relationships to other entities                         │
│   • Constraints                                             │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ STEP 3: STRUCTURE BUILDING                                  │
├─────────────────────────────────────────────────────────────┤
│ □ Organize features in logical order                        │
│   • By importance, or                                       │
│   • By user flow, or                                        │
│   • By modules                                              │
│                                                             │
│ □ Group related features under categories                   │
│                                                             │
│ □ Define main Workflows                                     │
│   • What is the trigger                                     │
│   • What are the steps                                      │
│   • What is the outcome                                     │
│                                                             │
│ □ Map dependencies between features                         │
│   • What depends on what                                    │
│   • What blocks what                                        │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ STEP 4: CONTENT GENERATION                                  │
├─────────────────────────────────────────────────────────────┤
│ □ Write Executive Summary                                   │
│   • Paragraph 1: What the product is and the problem        │
│   • Paragraph 2: What the solution is                       │
│   • Paragraph 3: What the business value is                 │
│                                                             │
│ □ Detail each feature:                                      │
│   • Description - what the feature does                     │
│   • User Stories - As a... I want... So that...             │
│   • Acceptance Criteria - when feature "works"              │
│   • Constraints - technical limitations                     │
│                                                             │
│ □ Create tables:                                            │
│   • Data specifications                                     │
│   • Character limits                                        │
│   • Permission matrix                                       │
│                                                             │
│ □ Document Workflows with diagrams or verbal description    │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ STEP 5: GAP ANALYSIS                                        │
├─────────────────────────────────────────────────────────────┤
│ □ Review each section and check:                            │
│   • Is the description complete?                            │
│   • Is there enough detail for development?                 │
│   • Are ACs measurable?                                     │
│                                                             │
│ □ Mark missing information:                                 │
│   • [TBD: description of what's missing]                    │
│   • [NEEDS CLARIFICATION: the question]                     │
│                                                             │
│ □ Add "Open Questions" section with all open questions      │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ STEP 6: QUALITY CHECK                                       │
├─────────────────────────────────────────────────────────────┤
│ □ Terminology consistency check                             │
│   • Same term for same concept?                             │
│   • Glossary updated?                                       │
│                                                             │
│ □ User Stories check                                        │
│   • Every story implementable?                              │
│   • Every story standalone?                                 │
│                                                             │
│ □ Acceptance Criteria check                                 │
│   • Every criterion testable?                               │
│   • Every criterion specific and measurable?                │
│                                                             │
│ □ Duplicates check                                          │
│   • No repeated information?                                │
│                                                             │
│ □ Formatting check                                          │
│   • All tables valid?                                       │
│   • All headers in place?                                   │
└─────────────────────────────────────────────────────────────┘
```

---

## Quality Checklist

Before finalizing the PRD:

- [ ] Executive summary captures the essence
- [ ] All user roles defined
- [ ] Features mapped to user stories
- [ ] Technical constraints documented
- [ ] Data models specified
- [ ] Acceptance criteria are measurable
- [ ] Dependencies identified
- [ ] Out of scope clearly stated
- [ ] No gaps without [TBD] or [NEEDS CLARIFICATION] markers

---

## Phase Integration

This command is used in **Phase 1: PRD**

After PRD creation:
1. Review and refine the PRD
2. Get stakeholder approval with `/phase-approve`
3. Move to Phase 2: Technical Specification with `/phase-advance`

## Test-Driven Integration

The PRD is used by `/write-tests` command to:
- Generate GUI/E2E tests from User Stories
- Create acceptance test scenarios
- Define test coverage requirements

```
PRD User Stories → GUI Tests (E2E flows)
PRD Requirements → Feature tests
PRD Success Metrics → Performance tests
```

---

## Examples

```bash
# Generate PRD for user authentication
/prd user-authentication
# Creates: docs/prd/2024-06-15-user-authentication.md

# Generate PRD for dashboard feature
/prd analytics-dashboard
# Creates: docs/prd/2024-06-15-analytics-dashboard.md

# Interactive mode (will ask questions)
/prd
```
