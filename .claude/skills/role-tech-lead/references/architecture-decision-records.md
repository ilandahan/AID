# Architecture Decision Records (ADR) Guide

## What is an ADR?

A short document capturing an important architectural decision and its context. ADRs help teams understand WHY decisions were made, not just what was decided.

## ADR Template

```markdown
# ADR-[NUMBER]: [Title]

## Status
[Proposed | Accepted | Deprecated | Superseded by ADR-XXX]

## Date
[YYYY-MM-DD]

## Context
[What is the issue that we're seeing that is motivating this decision?]
[What are the forces at play?]
[What constraints exist?]

## Decision
[What is the change that we're proposing and/or doing?]
[State the decision clearly and unambiguously.]

## Consequences

### Positive
- [Benefit 1]
- [Benefit 2]

### Negative
- [Drawback 1]
- [Drawback 2]

### Neutral
- [Side effect 1]

## Alternatives Considered

### Alternative 1: [Name]
[Brief description]
**Rejected because**: [Reason]

### Alternative 2: [Name]
[Brief description]
**Rejected because**: [Reason]

## References
- [Link to relevant documentation]
- [Link to spike/POC results]
```

## Example ADRs

### ADR-001: Use PostgreSQL for Primary Database

```markdown
# ADR-001: Use PostgreSQL for Primary Database

## Status
Accepted

## Date
2024-01-15

## Context
We need to select a primary database for our new application.
Requirements:
- ACID compliance for financial transactions
- JSON support for flexible schema sections
- Strong ecosystem and tooling
- Team expertise
- Scalability to millions of records

## Decision
We will use PostgreSQL as our primary database.

## Consequences

### Positive
- Strong ACID compliance
- Excellent JSON/JSONB support
- Team has 5+ years experience
- Rich ecosystem (extensions, tools)
- Proven scalability

### Negative
- Horizontal scaling requires additional tools (Citus, read replicas)
- Higher operational complexity than managed NoSQL

### Neutral
- Will use managed service (RDS/Cloud SQL) to reduce ops burden

## Alternatives Considered

### MongoDB
Flexible schema, horizontal scaling built-in.
**Rejected because**: Team lacks experience, ACID compliance more complex

### MySQL
Similar features, team experience.
**Rejected because**: JSON support less mature, PostgreSQL has more features

## References
- Database evaluation spike: [link]
- Team skills assessment: [link]
```

### ADR-002: Event-Driven Architecture for Order Processing

```markdown
# ADR-002: Event-Driven Architecture for Order Processing

## Status
Accepted

## Date
2024-01-20

## Context
Order processing involves multiple services:
- Inventory check
- Payment processing
- Notification sending
- Analytics tracking

Synchronous processing creates tight coupling and single points of failure.
Peak loads (flash sales) can overwhelm synchronous systems.

## Decision
We will use event-driven architecture with RabbitMQ for order processing.

Order service publishes events:
- order.created
- order.paid
- order.shipped
- order.cancelled

Consumers independently process events.

## Consequences

### Positive
- Services loosely coupled
- Better fault tolerance
- Easier to scale individual services
- Natural audit trail of events

### Negative
- Eventual consistency (not instant)
- More complex debugging
- Need for idempotency
- Message broker is critical infrastructure

### Neutral
- Team needs training on event-driven patterns

## Alternatives Considered

### Direct Service-to-Service Calls
Simple to understand, synchronous.
**Rejected because**: Tight coupling, cascade failures, scaling issues

### Kafka
More scalable, better for high-throughput.
**Rejected because**: Overkill for current scale, higher operational complexity

## References
- Event storming session: [link]
- Message broker comparison: [link]
```

## When to Write an ADR

### Always Write ADR For:
- Database selection
- Framework/language choices
- API design patterns
- Authentication/authorization approach
- Deployment architecture
- Third-party service selection
- Breaking changes to existing systems

### Don't Need ADR For:
- Library version updates
- Bug fixes
- Small refactors
- Code style decisions (use linter)

## ADR Lifecycle

```
┌──────────┐     ┌──────────┐     ┌────────────┐
│ Proposed │────>│ Accepted │────>│ Deprecated │
└──────────┘     └──────────┘     └────────────┘
     │                │                  │
     │                │                  │
     v                v                  v
┌──────────┐     ┌──────────┐     ┌────────────┐
│ Rejected │     │ Superseded│    │  (Keep for │
│          │     │ by ADR-X │     │  history)  │
└──────────┘     └──────────┘     └────────────┘
```

## ADR Review Checklist

- [ ] Context clearly explains the problem
- [ ] Decision is unambiguous
- [ ] Consequences are honest (including negatives)
- [ ] Alternatives show due diligence
- [ ] Status is current
- [ ] Referenced in relevant code/docs

## File Organization

```
docs/
└── architecture/
    └── decisions/
        ├── 0001-use-postgresql.md
        ├── 0002-event-driven-orders.md
        ├── 0003-jwt-authentication.md
        └── README.md  # Index of all ADRs
```
