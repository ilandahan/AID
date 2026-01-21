# Phase 2: Tech Spec Checklist

## Checklist Items

### Architecture
- `[CRITICAL]` Architecture diagram present
- `[CRITICAL]` All major components identified
- `[REQUIRED]` Component responsibilities described
- `[REQUIRED]` Data flow documented

### API Design
- `[CRITICAL]` All endpoints documented
- `[REQUIRED]` Request/response formats with examples
- `[REQUIRED]` Auth approach defined
- `[REQUIRED]` Error handling strategy

### Data Model
- `[CRITICAL]` Database schema present
- `[REQUIRED]` Entity relationships documented
- `[REQUIRED]` Key fields and types specified

### Security
- `[CRITICAL]` Security section exists
- `[REQUIRED]` Authentication mechanism
- `[REQUIRED]` Sensitive data handling
- `[RECOMMENDED]` OWASP considerations

### Technical Decisions
- `[REQUIRED]` Tech stack specified
- `[REQUIRED]` Key decisions with rationale (WHY)
- `[RECOMMENDED]` Alternatives considered

### Traceability
- `[REQUIRED]` Links to PRD (REQ-XXX)
- `[REQUIRED]` Technical IDs (TECH-XXX)

## Expected Files

- `docs/tech-spec/*.md` (required)
- Architecture diagrams (required)
- API specification (required)

## Auto-FAIL

- No architecture diagram
- APIs without examples
- No security section
- Missing database schema
- No link to PRD
