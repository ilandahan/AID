# /prd Command

Generate a Product Requirements Document (PRD) for a feature.

## Usage

```
/prd [feature-name]
```

## What It Does

1. **Gathers Information**
   - Reviews existing documentation
   - Asks clarifying questions
   - Identifies stakeholders

2. **Generates PRD**
   - Problem statement
   - User stories
   - Acceptance criteria
   - Success metrics
   - Out of scope items

3. **Saves Document**
   - Location: `docs/prd/PRD-<feature-name>.md`

## PRD Structure

```markdown
# PRD: [Feature Name]

## Overview
Brief description of the feature

## Problem Statement
What problem does this solve?

## Goals
- Primary goals
- Success metrics

## User Stories
As a [user type], I want to [action] so that [benefit]

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2

## Technical Considerations
High-level technical requirements

## Dependencies
External dependencies and integrations

## Out of Scope
What is NOT included in this feature

## Timeline
Estimated timeline and milestones

## Open Questions
Questions that need answers
```

## Examples

```bash
# Generate PRD for user authentication
/prd user-authentication

# Generate PRD for dashboard feature
/prd analytics-dashboard

# Interactive mode (will ask questions)
/prd
```

## After PRD Creation

1. Review and refine the PRD
2. Get stakeholder approval
3. Move to Phase 3: Technical Specification
   ```
   /tech-spec
   ```

## Tips

- Be specific about user personas
- Define measurable success criteria
- List all assumptions explicitly
- Include edge cases in acceptance criteria
