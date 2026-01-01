# Skills Reference

AID leverages a library of **Skills**—specialized instructions and prompts that are dynamically loaded into Claude based on the current context.

## Core Skills (Always Active)

These skills are loaded in every session to ensure the methodology is followed.

| Skill | Purpose |
|-------|---------|
| **`phase-enforcement`** | The "Supervisor". Prevents you from skipping phases or performing disallowed actions (e.g., coding during Discovery). |
| **`context-tracking`** | The "Secretary". Maintains the `.aid/context.json` file, tracking tasks and steps. |
| **`learning-mode`** | The "Student". Collects feedback and adapts future responses based on established patterns. |

## Phase Skills

These skills activate specific to the project's current lifecycle phase.

| Skill | Phase | Description |
|-------|-------|-------------|
| **`pre-prd-research`** | Phase 0 | Guides research, competitive analysis, and problem validation. |
| **`aid-discovery`** | Phase 0 | Helps identify stakeholders and defining success metrics. |
| **`aid-prd`** | Phase 1 | Focuses on writing clear User Stories and Acceptance Criteria. |
| **`aid-tech-spec`** | Phase 2 | Focuses on System Architecture, DB Schema, and API contracts. |
| **`aid-development`** | Phase 4 | General development guidelines (though mostly handled by Role skills). |
| **`aid-qa-ship`** | Phase 5 | Guides the release process, checklist verification, and regression testing. |

## Development Skills

These skills provide specific technical capabilities, usually available during Phase 4 (Development).

| Skill | Description |
|-------|-------------|
| **`atomic-design`** | **Critical Skill**. Reads Figma tokens and enforces the Atomic Design methodology (Atoms -> Molecules -> Organisms). |
| **`atomic-page-builder`** | strict rule: NEVER build pages from scratch. Only compose them from existing Organisms and Templates. |
| **`system-architect`** | Provides patterns for security, scalability, and code structure. |
| **`test-driven`** | Enforces TDD. Requires writing tests (`.test.ts`) before implementation files. |
| **`code-review`** | Performs automated code reviews looking for anti-patterns and security issues. |

## Optional Skills

| Skill | Description |
|-------|-------------|
| **`nano-banana-visual`** | Generates visual diagrams (charts, flows) using external AI image generation tools (if configured). |

## How Skills Work

Skills are essentially directory-based prompt packages.
-   **Definitions**: Located in `.claude/skills/`.
-   **Loading**: When you run `/aid-start`, the system symlinks the relevant skills into your current session context.
-   **Updates**: The `/aid-improve` command updates the skill files based on your feedback.
