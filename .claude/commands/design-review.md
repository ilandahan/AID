# Figma Design Review Command

Review a Figma component design before code extraction.

## Usage

Run this command after selecting a component in Figma with Dev Mode enabled.

## Prerequisites

1. Figma Desktop app running with Dev Mode enabled (Shift+D)
2. MCP server enabled in Figma inspect panel
3. Component selected in Figma

## Process

I will:
1. Connect to Figma MCP at `http://127.0.0.1:3845/mcp`
2. Get the selected component data using `mcp__figma__get_figma_data`
3. Load the `figma-design-review` skill from `.claude/skills/`
4. Audit the component against SKILL.md validation rules
5. Generate improvement suggestions
6. Produce a quality report

## Skill Reference

Load: `.claude/skills/figma-design-review/SKILL.md`

## Output

- Quality scores (0-100) for: naming, structure, visual, accessibility, metadata
- Issues with severity levels (error/warning/info)
- Improvement suggestions
- Export readiness status (requires score >= 90)
- Generated metadata in YAML format ready to paste into Figma

---

When this command is invoked, use the Figma MCP tools to:

1. First, call `mcp__figma__get_figma_data` with the file key to get component information
2. Apply the validation rules from the figma-design-review skill
3. Score each category according to the penalty tables
4. Generate actionable improvement suggestions
5. If score >= 90, mark as export-ready
