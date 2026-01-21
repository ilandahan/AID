---
paths:
  - ".claude/skills/**/*"
  - "skills/**/*"
---

# Skill Structure Rules

Rules for creating and modifying skills in the AID methodology.

---

## Skill Directory Structure

Each skill MUST follow this structure:

```
.claude/skills/{skill-name}/
├── SKILL.md              # Required - Core skill definition
├── SKILL.extended.md     # Optional - Detailed documentation
├── references/           # Optional - Supporting materials
│   ├── patterns.md
│   └── examples.md
├── templates/            # Optional - Reusable templates
│   └── output-template.md
└── scripts/              # Optional - Helper scripts
    └── helper.sh
```

---

## SKILL.md Required Format

```markdown
---
name: skill-name
description: Brief description of when to use this skill.
---

# Skill Name

## Core Responsibilities
- Responsibility 1
- Responsibility 2

## Phase Focus (if phase-specific)
| Phase | Focus | Output |
|-------|-------|--------|

## Key Patterns
[Skill-specific patterns and examples]

## Anti-Patterns
| Anti-Pattern | Fix |
|--------------|-----|

## Handoff Checklist
- [ ] Deliverable 1
- [ ] Deliverable 2

## References
| File | When to Read |
|------|--------------|
```

---

## YAML Frontmatter Requirements

```yaml
---
name: skill-name          # Required - lowercase, hyphenated
description: >            # Required - Multi-line description
  When this skill should be used.
  What triggers it.
---
```

---

## Skill Naming Conventions

| Type | Pattern | Example |
|------|---------|---------|
| Phase skills | `aid-{phase}` | `aid-discovery`, `aid-prd` |
| Role skills | `role-{role}` | `role-developer`, `role-qa-engineer` |
| Feature skills | `{feature-name}` | `atomic-design`, `code-review` |
| Sub-agents | `{name}-agent` | `reflection-agent`, `qa-validator` |

---

## Skill Responsibilities

Each skill MUST:

1. **Be focused** - One primary responsibility
2. **Be self-contained** - Include all needed patterns and examples
3. **Reference phase** - Indicate which phases it applies to
4. **Include anti-patterns** - What NOT to do
5. **Have handoff checklist** - Clear definition of done

---

## Extended Documentation

Use `SKILL.extended.md` for:

- Detailed examples
- Edge case handling
- Integration patterns
- Comprehensive reference material

Keep `SKILL.md` concise (<200 lines).

---

## References Folder

Store supporting materials in `references/`:

- Pattern libraries
- Example collections
- Checklists and templates
- External documentation links

---

## Skill Integration

Skills are loaded based on:

1. **Phase** - Defined in `.aid/state.json`
2. **Role** - Selected via `/aid-start`
3. **Command** - Invoked via slash commands
4. **Path** - Matched via YAML `paths:` frontmatter

---

## Skill Loading Order

```
1. Foundational skills (why-driven-decision, reflection)
2. Phase-enforcement skill
3. Current phase skill (aid-{phase})
4. Role skill (role-{role})
5. Feature skills as needed
```

---

## Checklist for New Skills

- [ ] SKILL.md follows required format
- [ ] YAML frontmatter complete
- [ ] Name follows conventions
- [ ] Single focused responsibility
- [ ] Anti-patterns documented
- [ ] Handoff checklist included
- [ ] References organized (if needed)
- [ ] Added to skill loading map (if phase-specific)
