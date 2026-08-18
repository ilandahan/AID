# Non-Functional Requirements (NFR) Reference Template


## NFR Specification Format


Every NFR follows this standard format:


```
[NFR-XXX] {Category} -- {Name}

Target:             {Concrete, measurable target}
Measurement Method: {How to verify -- tool, technique, or test}
Priority:           {P1 | P2 | P3}
PRD Trace:          {Link to PRD requirement this NFR supports}
Approach:           {Technical strategy to meet the target}
Cost Implication:   {Infrastructure, engineering effort, or operational cost}
```


### Example

```
[NFR-001] Performance -- Dashboard Page Load

Target:             P50 < 1.2s, P95 < 2.5s, P99 < 4.0s (LCP)
Measurement Method: Lighthouse CI in pipeline + RUM via web-vitals library
Priority:           P1
PRD Trace:          PRD-012 "Users see project status within 3 seconds"
Approach:           SSR critical path, lazy-load below-fold, CDN static assets
Cost Implication:   CDN ~$50/mo at 10K users; SSR adds ~200ms server compute
```


### Category Taxonomy

| Code | Category | Covers |
|------|----------|--------|
| PERF | Performance | Latency, throughput, render time |
| SCAL | Scalability | User growth, data growth, compute scaling |
| AVAIL | Availability | Uptime, redundancy, failover |
| REL | Reliability | Data durability, error rates, recovery |
| SEC | Security | AuthN, AuthZ, encryption, compliance |
| OBS | Observability | Logging, metrics, tracing, alerting |
| MAINT | Maintainability | Code quality, deploy frequency, tech debt |
| USE | Usability | Accessibility, responsiveness, UX performance |
| COST | Cost | Infrastructure spend, cost-per-user, budgets |

---

## 1. Performance Benchmarks -- SaaS Industry Standards

### Page Load Targets (Largest Contentful Paint)

| Percentile | Good | Acceptable | Poor |
|------------|------|------------|------|
| P50 | < 1.2s | 1.2-2.0s | > 2.0s |
| P75 | < 2.0s | 2.0-3.0s | > 3.0s |
| P95 | < 3.0s | 3.0-5.0s | > 5.0s |
| P99 | < 5.0s | 5.0-8.0s | > 8.0s |

**Context**: Google research shows 53% of mobile users abandon pages that take > 3s to load. For B2B SaaS, tolerance is slightly higher (users are invested), but P95 > 5s causes measurable churn.

### API Latency by Operation Type

| Operation | P50 | P95 | P99 | Notes |
|-----------|-----|-----|-----|-------|
| **Simple Read** (GET by ID) | < 50ms | < 150ms | < 300ms | Single row lookup, indexed |
| **List/Filter** (GET collection) | < 100ms | < 300ms | < 600ms | Paginated, max 100 items |
| **Search** (full-text, fuzzy) | < 200ms | < 500ms | < 1000ms | Elasticsearch/pg_trgm |
| **Simple Write** (POST/PUT) | < 100ms | < 300ms | < 500ms | Single table mutation |
| **Complex Write** (transaction) | < 200ms | < 500ms | < 1000ms | Multi-table, side effects |
| **File Upload** | < 500ms | < 2000ms | < 5000ms | Presigned URL pattern preferred |
| **Report Generation** | < 1000ms | < 5000ms | < 10000ms | Async if > 5s; use job queue |
| **AI/LLM Call** | < 2000ms | < 8000ms | < 15000ms | Stream responses; show progress |

### Throughput Benchmarks

| Tier | Sustained RPS | Burst RPS (10s) | Typical Architecture |
|------|--------------|-----------------|---------------------|
| Startup (< 1K users) | 50 | 200 | Single instance, vertical scaling |
| Growth (1K-10K users) | 200 | 1,000 | 2-4 instances, load balancer |
| Scale (10K-100K users) | 1,000 | 5,000 | Auto-scaling group, CDN, caching layer |
| Enterprise (100K-1M users) | 5,000 | 25,000 | Multi-region, edge compute, sharding |

### Database Query Time Targets

| Query Type | Target | Red Flag |
|------------|--------|----------|
| Indexed point lookup | < 5ms | > 20ms |
| Indexed range scan (< 1K rows) | < 20ms | > 100ms |
| Join (2-3 tables, indexed) | < 50ms | > 200ms |
| Aggregation (< 100K rows) | < 100ms | > 500ms |
| Full table scan (any size) | Avoid | Always a red flag in production |
| Unindexed filter | Avoid | Add index or redesign query |

**Rule**: Any query > 200ms in production must have a documented justification or optimization plan.

---

## 2. Scalability Tiers -- Architecture Decision Points

### User Count Impact Matrix

| Aspect | 100 Users | 1K Users | 10K Users | 100K Users | 1M Users |
|--------|-----------|----------|-----------|------------|----------|
| **Compute** | 1 instance (0.5 vCPU) | 1-2 instances (1 vCPU) | 2-4 instances + auto-scale | Multi-AZ auto-scale group | Multi-region, edge compute |
| **Database** | Shared/small (1 vCPU, 2GB) | Dedicated small (2 vCPU, 4GB) | Dedicated medium + read replicas | Dedicated large + connection pooling + read replicas | Sharded or managed distributed DB |
| **Cache** | In-process (LRU) | Redis single node (0.5GB) | Redis cluster (2-4GB) | Redis cluster (16-64GB) + local L1 cache | Multi-tier: L1 in-process + L2 Redis cluster |
| **Storage** | 1-10 GB | 10-100 GB | 100 GB-1 TB | 1-10 TB | 10-100 TB, tiered storage |
| **CDN** | Optional | Recommended | Required | Required + edge caching | Required + edge compute |
| **Search** | DB LIKE/ILIKE | pg_trgm or basic index | Elasticsearch single node | Elasticsearch cluster | Elasticsearch multi-cluster |
| **Background Jobs** | In-process setTimeout | Simple queue (1 worker) | Job queue + 2-4 workers | Distributed queue + auto-scale workers | Event-driven architecture, stream processing |
| **Est. Monthly Cost** | $20-50 | $100-300 | $500-2,000 | $5,000-20,000 | $50,000-200,000+ |

### Scaling Decision Points -- When to Act

| Signal | Threshold | Action |
|--------|-----------|--------|
| CPU sustained > 70% for 5 min | Immediate | Add instance or upgrade |
| Memory > 80% | Immediate | Scale up or optimize |
| DB connections > 80% of max | Urgent | Add connection pooler (PgBouncer) |
| P95 latency > 2x baseline | Urgent | Profile and optimize or scale |
| DB size > 50% of disk | Plan | Provision larger disk or archival strategy |
| Single-instance DB | At 1K users | Plan for read replica |
| Single-region deployment | At 10K users | Plan multi-AZ; evaluate multi-region |
| Synchronous processing > 5s | At any scale | Move to async job queue |
| Cache hit ratio < 80% | At any scale | Review cache strategy and TTLs |

### Horizontal vs. Vertical Scaling Decision

```
Is the bottleneck CPU or memory on a single node?
  |-- Yes, CPU        -> Horizontal scale (add instances)
  |-- Yes, memory     -> Vertical scale first (bigger instance), then shard
  +-- No, it is I/O   ->
        |-- Database I/O -> Read replicas, connection pooling, query optimization
        |-- Disk I/O     -> Faster storage tier (SSD to NVMe)
        +-- Network I/O  -> CDN, compression, edge caching
```

---

## 3. Availability & Reliability

### SLA Tiers

| SLA | Annual Downtime | Monthly Downtime | Weekly Downtime | Typical Use Case | Approximate Cost Multiplier |
|-----|----------------|------------------|-----------------|-----------------|---------------------------|
| 99.0% | 3d 15h 36m | 7h 18m | 1h 41m | Internal tools, dev environments | 1x (baseline) |
| 99.5% | 1d 19h 48m | 3h 39m | 50m | Non-critical B2B features | 1.2x |
| 99.9% | 8h 46m | 43m 50s | 10m 5s | Standard B2B SaaS | 1.5-2x |
| 99.95% | 4h 23m | 21m 55s | 5m 2s | Business-critical SaaS | 2-3x |
| 99.99% | 52m 36s | 4m 23s | 1m 0s | Financial, healthcare, real-time | 5-10x |
| 99.999% | 5m 15s | 26s | 6s | Life-critical systems | 10-50x |

**Recommendation for most B2B SaaS**: Start at 99.9%. Move to 99.95% only when contractual SLAs demand it. Each additional nine roughly doubles infrastructure cost and triples operational complexity.

### RTO / RPO Definitions

| Term | Definition | Question It Answers |
|------|-----------|-------------------|
| **RTO** (Recovery Time Objective) | Maximum acceptable time to restore service after an outage | "How long can we be down?" |
| **RPO** (Recovery Point Objective) | Maximum acceptable data loss measured in time | "How much data can we lose?" |

### RTO / RPO Targets by Tier

| Tier | RTO | RPO | Implementation | Est. Cost |
|------|-----|-----|----------------|-----------|
| **Bronze** | < 4 hours | < 24 hours | Daily backups, manual restore, single region | $50-200/mo |
| **Silver** | < 1 hour | < 1 hour | Hourly backups or WAL archiving, automated failover, single region | $200-800/mo |
| **Gold** | < 15 minutes | < 5 minutes | Streaming replication, automated failover, multi-AZ | $800-3,000/mo |
| **Platinum** | < 1 minute | < 0 (zero data loss) | Synchronous multi-AZ replication, hot standby, multi-region | $3,000-15,000/mo |

### RTO / RPO Examples

| Scenario | Recommended RTO | Recommended RPO | Reasoning |
|----------|----------------|-----------------|-----------|
| User-generated content (notes, docs) | 1 hour | 5 minutes | Users expect recent edits to survive |
| Financial transactions | 5 minutes | 0 (zero loss) | Regulatory and trust requirement |
| Analytics / reporting data | 4 hours | 24 hours | Can be recomputed from source |
| Session / cache data | N/A (ephemeral) | N/A | Rebuild from source of truth |
| Audit logs | 15 minutes | 0 (zero loss) | Compliance requirement; append-only |

### Reliability Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Error rate (5xx) | < 0.1% of requests | Error count / total requests over 5 min window |
| Error budget burn rate | < 1x (steady state) | (error minutes used) / (error minutes allowed) per window |
| Successful deployment rate | > 95% | Deploys without rollback / total deploys |
| Mean Time Between Failures (MTBF) | > 30 days | Average time between P1 incidents |
| Mean Time to Detection (MTTD) | < 5 minutes | Time from failure to alert firing |
| Mean Time to Recovery (MTTR) | < 30 minutes | Time from alert to service restored |

---

## 4. Observability Requirements

### The RED Method -- For Services (Request-Driven)

| Signal | Metric | Alert Threshold | Dashboard |
|--------|--------|-----------------|-----------|
| **R**ate | Requests per second | > 2x baseline or < 0.5x baseline | Time series, per endpoint |
| **E**rrors | Error rate (%) | > 1% 5xx for 5 min | Stacked area: 4xx vs 5xx |
| **D**uration | Latency percentiles | P95 > 2x baseline for 5 min | Heatmap, P50/P95/P99 lines |

### The USE Method -- For Resources (Infrastructure)

| Resource | **U**tilization | **S**aturation | **E**rrors |
|----------|-----------------|----------------|------------|
| CPU | % usage per core | Run queue length | Machine check exceptions |
| Memory | % used | Swap usage, OOM kills | ECC errors |
| Disk | % capacity, IOPS used | I/O wait queue depth | Read/write errors |
| Network | Bandwidth used (%) | TCP retransmits, dropped packets | Interface errors |
| DB Connections | Active / max pool | Queued connection requests | Connection timeouts |

### Logging Requirements

| Level | When to Use | Retention | Examples |
|-------|-------------|-----------|---------|
| **ERROR** | Unexpected failure requiring attention | 90 days | Unhandled exception, external service failure, data corruption |
| **WARN** | Degraded operation, not a failure yet | 30 days | Retry succeeded, slow query, approaching quota |
| **INFO** | Significant business events | 30 days | User signup, payment processed, deployment completed |
| **DEBUG** | Diagnostic detail | 7 days (staging only) | Request/response bodies, cache hit/miss, query plans |

**Structured logging format** (mandatory):
```json
{
  "timestamp": "2025-03-23T10:15:30.123Z",
  "level": "ERROR",
  "service": "api",
  "traceId": "abc-123-def",
  "userId": "user_456",
  "message": "Payment processing failed",
  "error": { "code": "STRIPE_DECLINED", "message": "Card declined" },
  "context": { "orderId": "order_789", "amount": 4999 }
}
```

**Rules**:
- NEVER log secrets, passwords, tokens, PII, or full credit card numbers
- ALWAYS include traceId for request correlation
- ALWAYS include userId when available (for debugging, not surveillance)
- Log at boundaries: incoming requests, outgoing calls, queue publish/consume

### Distributed Tracing

| Requirement | Standard |
|-------------|----------|
| Trace propagation | W3C Trace Context (`traceparent` header) |
| Span naming | `{service}.{operation}` (e.g., `api.createOrder`) |
| Minimum spans | HTTP handler, DB query, external HTTP call, queue publish/consume |
| Sampling rate (production) | 1-10% for normal traffic; 100% for errors |
| Trace retention | 7 days |

### Alerting Thresholds

| Alert | Condition | Severity | Response Time |
|-------|-----------|----------|---------------|
| Service down (0 healthy instances) | Health check fails for 60s | P1 Critical | < 5 min |
| Error rate spike | 5xx > 5% for 5 min | P1 Critical | < 5 min |
| High latency | P95 > 3x baseline for 10 min | P2 High | < 15 min |
| Disk space | > 85% used | P2 High | < 1 hour |
| Memory pressure | > 90% used for 5 min | P2 High | < 15 min |
| Error rate elevated | 5xx > 1% for 10 min | P3 Medium | < 4 hours |
| Certificate expiry | < 14 days remaining | P3 Medium | < 24 hours |
| Slow queries | Queries > 1s, > 10/min | P4 Low | Next business day |

### Dashboard Essentials (Minimum Viable Observability)

Every production service must have:

1. **Service Health**: Request rate, error rate, latency P50/P95/P99 (RED method)
2. **Infrastructure**: CPU, memory, disk, network per instance (USE method)
3. **Database**: Query rate, slow query count, connection pool usage, replication lag
4. **Business Events**: Signups, logins, key feature usage, payment events
5. **Error Breakdown**: Top errors by type, affected users, trending errors
6. **Dependency Health**: Status and latency of external services (Stripe, email, etc.)

---

## 5. Maintainability

### Code Quality Targets

| Metric | Target | Measurement | Notes |
|--------|--------|-------------|-------|
| Test coverage (line) | > 80% | Istanbul/c8/coverage tool | 80% is the diminishing returns inflection point |
| Test coverage (branch) | > 70% | Same tool, branch mode | Branch coverage catches more real bugs than line |
| Critical path coverage | 100% | Manual audit | Auth, payment, data mutation paths |
| Type coverage | > 95% | `typescript --strict`, no `any` | Enforce via tsconfig `strict: true` |
| Lint violations | 0 (blocking) | ESLint in CI | Treat warnings as errors in CI |
| Cyclomatic complexity | < 15 per function | ESLint rule `complexity` | Functions > 15 must be refactored or justified |
| Max function length | < 50 lines | ESLint rule `max-lines-per-function` | Guideline, not hard block |

### Deployment Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| Deployment frequency | > 1/week (min); daily (ideal) | Count deployments per week |
| Lead time for changes | < 1 day (code merged to production) | Merge timestamp to deploy timestamp |
| Change failure rate | < 15% | Deploys requiring hotfix or rollback / total deploys |
| Time to rollback | < 5 minutes | Measured in runbook drill |
| Build time | < 5 minutes | CI pipeline duration (build + test + deploy) |
| CI pipeline reliability | > 98% pass rate on main | Failed CI / total CI runs (excluding legit failures) |

### Mean Time to Recovery (MTTR) Targets

| Incident Severity | MTTR Target | Escalation |
|-------------------|-------------|------------|
| P1 (service down) | < 30 minutes | Immediate page, all hands |
| P2 (degraded) | < 2 hours | Page on-call, team standup |
| P3 (minor impact) | < 8 hours | Next available engineer |
| P4 (cosmetic/low) | < 5 business days | Backlog, normal sprint |

### Technical Debt Metrics

| Metric | Healthy | Warning | Action Required |
|--------|---------|---------|-----------------|
| TODO/FIXME/HACK count | < 20 | 20-50 | > 50 -- schedule debt sprint |
| Dependency age (major behind) | 0-1 major versions | 2 major versions | > 2 -- security risk, schedule upgrade |
| Unused dependency count | 0 | 1-3 | > 3 -- remove immediately |
| Duplicated code (%) | < 3% | 3-5% | > 5% -- extract shared modules |
| Files > 500 lines | < 5% of codebase | 5-10% | > 10% -- refactor |

---

## 6. Usability & Accessibility

### Core Web Vitals Targets (Google Thresholds)

| Metric | Good | Needs Improvement | Poor | Measures |
|--------|------|-------------------|------|----------|
| **LCP** (Largest Contentful Paint) | < 2.5s | 2.5-4.0s | > 4.0s | Perceived load speed |
| **INP** (Interaction to Next Paint) | < 200ms | 200-500ms | > 500ms | Responsiveness to user input |
| **CLS** (Cumulative Layout Shift) | < 0.1 | 0.1-0.25 | > 0.25 | Visual stability |
| **FCP** (First Contentful Paint) | < 1.8s | 1.8-3.0s | > 3.0s | First visual feedback |
| **TTFB** (Time to First Byte) | < 800ms | 800ms-1.8s | > 1.8s | Server responsiveness |

### WCAG 2.1 AA Essentials (Minimum for B2B SaaS)

These are the highest-impact, most commonly violated criteria:

| Criterion | WCAG Ref | Requirement | How to Test |
|-----------|----------|-------------|-------------|
| Color contrast (text) | 1.4.3 | 4.5:1 for normal text, 3:1 for large text (18px+) | axe-core, Lighthouse |
| Color contrast (UI) | 1.4.11 | 3:1 for interactive components and graphics | Manual + axe-core |
| Keyboard navigation | 2.1.1 | All functionality accessible via keyboard alone | Tab through entire app |
| Focus visibility | 2.4.7 | Visible focus indicator on all interactive elements | Tab and verify ring/outline |
| Alt text for images | 1.1.1 | All meaningful images have descriptive alt text | Automated scan + manual review |
| Form labels | 1.3.1, 4.1.2 | Every input has a programmatically associated label | axe-core |
| Error identification | 3.3.1 | Errors identified in text (not color alone) | Manual + axe-core |
| Heading hierarchy | 1.3.1 | Headings follow logical order (h1 > h2 > h3) | axe-core, heading outline tool |
| Link purpose | 2.4.4 | Link text describes destination (no "click here") | Manual review |
| Skip navigation | 2.4.1 | "Skip to main content" link for keyboard users | Tab on page load |
| ARIA landmarks | 1.3.1 | Main, nav, banner, contentinfo landmarks present | axe-core |
| Touch targets | 2.5.8 | Minimum 24x24px (AA), recommend 44x44px | Manual measurement |

**Testing approach**: Run axe-core in CI (blocks on violations), Lighthouse accessibility audit > 90, quarterly manual audit with screen reader (NVDA or VoiceOver).

### Mobile Responsiveness Requirements

| Requirement | Specification |
|-------------|--------------|
| Breakpoints | 320px (mobile), 768px (tablet), 1024px (desktop), 1440px (wide) |
| Minimum supported width | 320px (iPhone SE) |
| Touch target size | >= 44x44px on mobile |
| No horizontal scroll | Content fits viewport at every breakpoint |
| Readable without zoom | Base font >= 16px on mobile |
| Viewport meta tag | `<meta name="viewport" content="width=device-width, initial-scale=1">` |
| Orientation | Support both portrait and landscape |

---

## 7. Cost Constraints

### Infrastructure Cost-Per-User Benchmarks (Cloud)

| Scale | Cost/User/Month | Notes |
|-------|----------------|-------|
| < 1K users | $0.50-2.00 | High per-user cost is normal; fixed costs dominate |
| 1K-10K users | $0.10-0.50 | Economies of scale begin; optimize databases first |
| 10K-100K users | $0.03-0.15 | Caching and CDN ROI is highest here |
| 100K-1M users | $0.01-0.05 | Architecture efficiency dominates; reserved instances |
| > 1M users | < $0.01 | Custom pricing, spot instances, edge optimization |

**Rule**: If cost-per-user is > 2x the benchmark for your tier, flag it for architecture review.

### Estimation Formulas

**Compute** (per instance/month):
```
Cost = vCPU_count x $30/mo + RAM_GB x $4/mo    (on-demand, approximate)
Cost = above x 0.6                               (1-year reserved)
Cost = above x 0.4                               (3-year reserved)
```

**Database** (managed PostgreSQL, approximate):
```
Cost = vCPU x $50/mo + Storage_GB x $0.12/mo + IOPS x $0.001
Backup = Storage_GB x $0.02/mo (beyond free tier)
```

**Storage** (object storage):
```
Cost = GB_stored x $0.023/mo + GET_requests/1000 x $0.0004 + PUT_requests/1000 x $0.005
Egress = GB_transferred x $0.09 (first 10TB)
```

**Bandwidth / CDN**:
```
CDN Cost = GB_transferred x $0.085 (first 10TB, decreases with volume)
Origin Shield = ~$0.01/10K requests (reduces origin load)
```

**AI / LLM Calls** (variable, check provider pricing):
```
Cost = input_tokens/1M x input_price + output_tokens/1M x output_price
Example: GPT-4o -- $2.50/1M input + $10.00/1M output
Example: Claude Sonnet -- $3.00/1M input + $15.00/1M output
Budget = avg_tokens_per_call x calls_per_user_per_day x user_count x 30 x token_price
```

### Cost-Performance Trade-off Decision Points

Flag these for explicit decision when they arise:

| Trade-off | When to Flag |
|-----------|-------------|
| CDN vs. origin-serve | When bandwidth > $100/mo |
| Read replica vs. query optimization | When DB CPU > 60% sustained |
| Cache layer (Redis) vs. DB optimization | When identical queries > 30% of DB load |
| Reserved vs. on-demand instances | When monthly spend > $500 |
| Multi-region vs. single-region | When latency SLA < 100ms for global users |
| Managed service vs. self-hosted | When ops cost > managed service premium |
| Serverless vs. always-on | When traffic is bursty (> 10x peak/trough ratio) |
| AI model tier (GPT-4o vs. GPT-4o-mini) | When AI cost > 20% of total infrastructure |

### Budget Guard Rails

| Metric | Action |
|--------|--------|
| Monthly spend > 120% of budget | Alert team lead |
| Monthly spend > 150% of budget | Emergency review, stop non-essential services |
| Single resource > 40% of total spend | Architecture review (over-reliance) |
| Cost-per-user increasing month-over-month | Investigate scaling inefficiency |

---

## 8. NFR Priority Framework

### Priority Definitions

| Priority | Definition | Timeline | Gate |
|----------|-----------|----------|------|
| **P1** -- Must Have | System cannot launch without meeting this NFR. Failure means broken product, security breach, or regulatory violation. | Must meet before launch | **Launch blocker** |
| **P2** -- Should Have | System can launch without it but must meet within 3 months. Failure causes user dissatisfaction or operational friction. | Within 3 months post-launch | **Sprint planning** |
| **P3** -- Nice to Have | Improves experience or efficiency but not critical. Can be deferred to a future quarter. | Backlog / next quarter | **Quarterly review** |

### Priority Assignment Guide

| Category | P1 (Launch Blocker) | P2 (3-Month) | P3 (Backlog) |
|----------|-------------------|--------------|-------------|
| **Performance** | Core flow P95 < 3s | Non-core flow P95 < 3s | P99 optimization |
| **Scalability** | Handle 2x projected launch load | Handle 10x launch load | Handle 100x (future-proofing) |
| **Availability** | 99.9% uptime | 99.95% uptime | 99.99% uptime |
| **Reliability** | Automated backups, RPO < 1h | Automated failover, RPO < 5min | Multi-region, RPO = 0 |
| **Security** | AuthN, AuthZ, encryption at rest/transit, OWASP top 10 | Penetration test, SOC 2 prep | SOC 2 Type II, bug bounty |
| **Observability** | Error alerting, basic dashboard | Full RED/USE dashboards, tracing | Anomaly detection, SLO tracking |
| **Maintainability** | CI/CD pipeline, automated tests | 80% coverage, < 5 min deploy | Tech debt budget, dependency automation |
| **Usability** | WCAG 2.1 AA critical (contrast, keyboard) | Full WCAG 2.1 AA compliance | WCAG 2.1 AAA where feasible |
| **Cost** | Stays within approved budget | Cost-per-user within benchmark | Reserved instance optimization |

### Prioritization Decision Tree

```
Is there a regulatory or legal requirement?
  +-- Yes -> P1

Does failure prevent core user workflow?
  +-- Yes -> P1

Does failure cause data loss or security breach?
  +-- Yes -> P1

Does failure cause measurable user dissatisfaction?
  +-- Yes -> P2

Does failure increase operational cost or burden?
  +-- Yes -> P2

Is this an optimization or future-proofing measure?
  +-- Yes -> P3
```

### NFR Review Cadence

| Action | When |
|--------|------|
| P1 NFRs verified | Before every release |
| P2 NFRs reviewed | Sprint planning (biweekly) |
| P3 NFRs reviewed | Quarterly planning |
| All NFRs re-prioritized | Major feature launch or architecture change |
| Cost NFRs audited | Monthly |

---

## Appendix A -- NFR Checklist for Tech Spec Review

Use this checklist when reviewing a tech spec for NFR completeness:

```
Performance
  [ ] Page load targets defined (LCP at P50/P95/P99)
  [ ] API latency targets defined per endpoint type
  [ ] Database query performance considered
  [ ] Caching strategy defined (if applicable)

Scalability
  [ ] Target user count specified
  [ ] Scaling strategy documented (horizontal/vertical)
  [ ] Database scaling plan exists (if > 1K users)
  [ ] Bottleneck identified and mitigation planned

Availability & Reliability
  [ ] SLA target stated with justification
  [ ] RTO and RPO defined
  [ ] Backup strategy documented
  [ ] Failover mechanism described (if P1)

Security
  [ ] Authentication mechanism specified
  [ ] Authorization model defined
  [ ] Data encryption (at rest + in transit) confirmed
  [ ] OWASP top 10 addressed
  [ ] PII handling documented

Observability
  [ ] Logging strategy defined (levels, retention, format)
  [ ] Key metrics identified (RED for services, USE for infra)
  [ ] Alerting thresholds set for P1 scenarios
  [ ] Tracing approach described (if distributed)

Maintainability
  [ ] Test coverage target set
  [ ] CI/CD pipeline requirements stated
  [ ] Deployment strategy defined (blue/green, canary, rolling)
  [ ] Rollback procedure documented

Usability & Accessibility
  [ ] WCAG 2.1 AA compliance planned
  [ ] Core Web Vitals targets set
  [ ] Mobile breakpoints defined
  [ ] Keyboard navigation required

Cost
  [ ] Infrastructure budget stated
  [ ] Cost-per-user estimated
  [ ] Cost growth model described (linear? sub-linear?)
  [ ] Expensive resources flagged (AI calls, egress, etc.)
```

---

## Appendix B -- Quick Reference: Common NFR Patterns

### Pattern 1: "Standard B2B SaaS"
```
[NFR-001] PERF -- Page Load:           P95 LCP < 2.5s
[NFR-002] PERF -- API Latency:         P95 < 300ms (reads), P95 < 500ms (writes)
[NFR-003] AVAIL -- Uptime:             99.9% monthly
[NFR-004] REL -- Data Recovery:        RPO < 1h, RTO < 1h
[NFR-005] SEC -- Auth:                 JWT + RBAC, TLS 1.2+, encryption at rest
[NFR-006] OBS -- Alerting:             5xx > 1% -> P1 alert within 5 min
[NFR-007] MAINT -- Deployment:         CI/CD, < 5 min rollback, > 80% coverage
[NFR-008] USE -- Accessibility:        WCAG 2.1 AA, Lighthouse a11y > 90
[NFR-009] COST -- Infrastructure:      < $0.50/user/month at 1K users
```

### Pattern 2: "AI-Heavy SaaS (LLM Features)"
```
All of Pattern 1, plus:
[NFR-010] PERF -- AI Response:         First token < 1s (streaming), total < 15s
[NFR-011] COST -- AI Spend:            < $0.05/user/day for LLM calls
[NFR-012] REL -- AI Fallback:          Graceful degradation if LLM provider is down
[NFR-013] OBS -- AI Monitoring:        Token usage, latency, error rate per model
[NFR-014] SEC -- AI Safety:            Prompt injection prevention, output sanitization
```

### Pattern 3: "Compliance-Sensitive (Healthcare/Finance)"
```
All of Pattern 1, plus:
[NFR-015] SEC -- Audit Trail:          Immutable log of all data access, 7-year retention
[NFR-016] SEC -- Encryption:           AES-256 at rest, TLS 1.3 in transit, field-level for PII
[NFR-017] AVAIL -- Uptime:             99.99% monthly (upgrade from 99.9%)
[NFR-018] REL -- Data Recovery:        RPO = 0 (synchronous replication), RTO < 5 min
[NFR-019] MAINT -- Compliance:         SOC 2 Type II, annual pen test, quarterly access review
```
