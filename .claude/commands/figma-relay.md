# Figma Relay - Process Plugin Requests

This command polls the Figma plugin server for pending requests and processes them using AID skills.

## Usage

Run `/figma-relay` to start processing requests from the Figma plugin.

## How It Works

1. Polls `http://localhost:3001/relay/pending` for requests
2. For each pending request:
   - Marks it as processing
   - Loads the appropriate skill (figma-design-review)
   - Processes the component data
   - Returns the result

## Request Types

| Type | Skill Used | Action |
|------|-----------|--------|
| `audit` | figma-design-review | Audit component against SKILL.md rules |
| `analyze` | figma-design-review | Analyze metadata completeness |
| `generate` | figma-design-review | Generate metadata suggestions |
| `report` | figma-design-review | Create quality report |
| `pipeline` | figma-design-review | Run full 4-step pipeline |
| `export` | figma-design-review | Export to AID format |

---

When this command is invoked:

1. Fetch pending requests from `GET http://localhost:3001/relay/pending`
2. For each request in `requests` array:
   a. Call `POST http://localhost:3001/relay/process/{requestId}` to mark processing
   b. Load the figma-design-review skill
   c. Process based on `request.type`:
      - For `audit`: Score component on naming, structure, visual, accessibility, metadata
      - For `analyze`: Check which required fields are present/missing
      - For `generate`: Generate YAML metadata following SKILL.md format
      - For `report`: Combine audit + analysis + suggestions into report
      - For `pipeline`: Run all 4 steps in sequence
      - For `export`: Format output per ENRICHMENT_TEMPLATE.json
   d. Call `POST http://localhost:3001/relay/complete/{requestId}` with result
   e. If error, call `POST http://localhost:3001/relay/fail/{requestId}` with error message

3. Report how many requests were processed
