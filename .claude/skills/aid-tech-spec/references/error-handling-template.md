# Error Handling Strategy Template

## 1. Error Taxonomy

### Layer Classification

Every error MUST be classified by the layer where it originates:

| Layer | Prefix | Description | Example |
|-------|--------|-------------|---------|
| Client | `CLT` | Invalid input, auth failure, rate limit | Malformed JSON, expired token |
| Server | `SRV` | Business logic failure, state conflict | Insufficient balance, duplicate entry |
| Database | `DB` | Connection, query, constraint violation | Deadlock, unique constraint, timeout |
| Third-Party | `EXT` | External API failure, webhook error | Payment gateway timeout, SMS delivery fail |
| Infrastructure | `INF` | Network, DNS, disk, memory | OOM kill, certificate expiry, DNS resolution |

### Severity Classification

| Severity | Code | Criteria | Response Time |
|----------|------|----------|---------------|
| Critical | `P0` | Data loss risk, full outage, security breach | < 15 minutes |
| Error | `P1` | Feature broken, degraded for many users | < 1 hour |
| Warning | `P2` | Intermittent issue, workaround exists | < 4 hours |
| Info | `P3` | Expected failure, handled gracefully | Next business day |

### Error Documentation Template

For each error type in the system, document:

```markdown
## Error: [ERROR_CODE]

- **Layer**: Client / Server / Database / Third-Party / Infrastructure
- **Severity**: P0 / P1 / P2 / P3
- **HTTP Status**: [status code]
- **Trigger**: [What causes this error]
- **User Message**: [What the user sees]
- **Internal Message**: [What appears in logs]
- **Recovery Strategy**: [Auto-retry / Circuit breaker / Manual / None]
- **Monitoring**: [Alert channel + threshold]
- **Runbook**: [Link to resolution steps]
```

---

## 2. Error Code System

### Naming Convention

Format: `{LAYER}_{DOMAIN}_{SEQUENCE}`

```
AUTH_001              -- Authentication domain, first error
AUTH_002              -- Authentication domain, second error
DB_CONN_TIMEOUT       -- Database connection timeout
EXT_PAYMENT_DECLINED  -- External payment declined
SRV_ORDER_CONFLICT    -- Server order state conflict
```

### Code Ranges by Category

| Range | Category | Examples |
|-------|----------|---------|
| `AUTH_001-099` | Authentication & Authorization | Token expired, invalid credentials, insufficient permissions |
| `VAL_100-199` | Input Validation | Missing field, invalid format, out of range |
| `RES_200-299` | Resource Operations | Not found, already exists, conflict, gone |
| `BIZ_300-399` | Business Logic | Insufficient balance, limit exceeded, invalid state transition |
| `DB_400-499` | Database | Connection failed, query timeout, constraint violation, deadlock |
| `EXT_500-599` | Third-Party Integrations | API unavailable, rate limited, invalid response |
| `INF_600-699` | Infrastructure | Disk full, memory pressure, certificate error |
| `SYS_900-999` | System / Catch-All | Unknown error, unhandled exception |

### HTTP Status Code Mapping

| Error Category | Primary HTTP Status | When to Use |
|---------------|-------------------|-------------|
| `AUTH_001` Invalid credentials | 401 Unauthorized | Credentials wrong or missing |
| `AUTH_002` Token expired | 401 Unauthorized | Token no longer valid |
| `AUTH_003` Insufficient permissions | 403 Forbidden | Valid auth but no access |
| `VAL_1xx` Validation errors | 400 Bad Request | Input fails validation |
| `RES_200` Not found | 404 Not Found | Resource does not exist |
| `RES_201` Already exists | 409 Conflict | Duplicate creation attempt |
| `RES_202` State conflict | 409 Conflict | Optimistic lock / state mismatch |
| `BIZ_3xx` Business rule violation | 422 Unprocessable Entity | Valid input, invalid operation |
| `DB_4xx` Database errors | 503 Service Unavailable | Transient DB issues |
| `EXT_5xx` Third-party failures | 502 Bad Gateway | Upstream dependency failed |
| `EXT_501` Third-party timeout | 504 Gateway Timeout | Upstream dependency timed out |
| `INF_6xx` Infrastructure | 503 Service Unavailable | System-level failures |
| `SYS_9xx` Unknown errors | 500 Internal Server Error | Catch-all for unhandled cases |

### Dual-Message Pattern

Every error MUST have two messages. Never expose internal details to users.

```typescript
interface AppError {
  // What the user sees -- helpful, non-technical, actionable
  userMessage: string;

  // What engineers see in logs -- technical, detailed, debuggable
  internalMessage: string;

  // Structured error identity
  code: string;          // "AUTH_002"
  httpStatus: number;    // 401
  severity: 'P0' | 'P1' | 'P2' | 'P3';

  // Correlation
  requestId: string;     // "req_abc123" -- ties logs to user report
  traceId?: string;      // Distributed tracing ID

  // Context (never sent to client)
  context?: Record<string, unknown>;
}
```

**Example:**

```typescript
// WRONG -- leaks internal details
{ message: "SELECT * FROM users WHERE id = 'x'; relation 'users' does not exist" }

// RIGHT -- separated messages
{
  code: "DB_401",
  userMessage: "We're having trouble loading your profile. Please try again in a moment.",
  internalMessage: "PostgreSQL relation 'users' not found -- possible migration drift",
  httpStatus: 503,
  severity: "P0",
  requestId: "req_7f3a2b",
  context: { query: "findUserById", table: "users", pgCode: "42P01" }
}
```

---

## 3. Recovery Strategies

### 3a. Retry with Exponential Backoff and Jitter

Use for: transient failures (network blips, temporary overload, lock contention).

```
Attempt 1: immediate
Attempt 2: wait  200ms + random(0-100ms)
Attempt 3: wait  400ms + random(0-200ms)
Attempt 4: wait  800ms + random(0-400ms)
Attempt 5: wait 1600ms + random(0-800ms)
-- give up after max_retries --
```

**Configuration Template:**

| Parameter | Default | Notes |
|-----------|---------|-------|
| `maxRetries` | 3 | Set per-operation based on criticality |
| `baseDelay` | 200ms | Initial wait before first retry |
| `maxDelay` | 30s | Cap to prevent unbounded waits |
| `backoffMultiplier` | 2 | Exponential factor |
| `jitterMode` | `full` | `full` = random(0, delay); `equal` = delay/2 + random(0, delay/2) |
| `retryableErrors` | `[429, 502, 503, 504]` | HTTP codes that trigger retry |
| `retryableExceptions` | `[ECONNRESET, ETIMEDOUT]` | System errors that trigger retry |

**Idempotency Requirement:**

Retried operations MUST be idempotent. For non-idempotent operations:

| Method | Idempotent? | Strategy |
|--------|-------------|----------|
| GET | Yes | Safe to retry |
| PUT | Yes | Safe to retry (same payload = same result) |
| DELETE | Yes | Safe to retry (deleting twice = same result) |
| POST | No | Use idempotency key: `Idempotency-Key: uuid` header |
| PATCH | Depends | Safe if using absolute values; unsafe if using deltas |

```typescript
// Idempotency key pattern for POST
const response = await fetch('/api/v1/orders', {
  method: 'POST',
  headers: {
    'Idempotency-Key': crypto.randomUUID(), // Generated client-side, stored for retry
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(orderData)
});
```

Server MUST:
1. Store idempotency key + response for at least 24 hours
2. Return cached response for duplicate key (same status, same body)
3. Return `409 Conflict` if same key sent with different payload

### 3b. Circuit Breaker

Use for: protecting against cascading failures from slow or failing dependencies.

```
State Machine:

  CLOSED  --[success]--> CLOSED       (normal operation)
    |
    | failure threshold reached
    v
   OPEN   (all requests fail-fast with fallback)
    |
    | timeout expires
    v
  HALF-OPEN --[success]--> CLOSED     (recovery confirmed)
    |
    | failure
    v
   OPEN   (back to open, reset timeout)
```

**Configuration Template:**

| Parameter | Default | Notes |
|-----------|---------|-------|
| `failureThreshold` | 5 | Failures before opening circuit |
| `failureWindow` | 60s | Window in which failures are counted |
| `openTimeout` | 30s | How long to stay open before trying half-open |
| `halfOpenMaxAttempts` | 3 | Requests allowed in half-open state |
| `successThreshold` | 2 | Successes in half-open to close circuit |
| `monitoredErrors` | `[5xx, timeout, connection refused]` | What counts as a failure |

**Fallback Behavior by Circuit State:**

| State | Behavior |
|-------|----------|
| Closed | Normal operation, count failures |
| Open | Return fallback immediately, do not call dependency |
| Half-Open | Allow limited traffic, observe results |

### 3c. Fallback Strategies

Define a fallback for every external dependency. No dependency should cause a full outage.

| Fallback Type | Use When | Example |
|---------------|----------|---------|
| Cached response | Data is read-only or tolerant of staleness | Return last-known user profile from Redis |
| Degraded response | Partial data is better than no data | Return order without real-time shipping status |
| Default value | A sensible default exists | Show default pricing tier when pricing service is down |
| Queue for later | Operation can be deferred | Queue email send, process when service recovers |
| Alternative provider | Redundant service available | Failover from primary to secondary payment processor |
| Graceful refusal | No safe fallback exists | Return 503 with retry-after header and helpful message |

**Staleness Budget:**

For cached fallbacks, define acceptable staleness per resource:

| Resource | Max Staleness | Cache Strategy |
|----------|--------------|----------------|
| User profile | 5 minutes | Read-through cache, async refresh |
| Product catalog | 1 hour | Background refresh every 30 min |
| Feature flags | 30 seconds | Polling with local fallback |
| Pricing data | 0 (real-time) | No cache -- use default or refuse |

### 3d. Compensation (Saga Pattern)

Use for: multi-step operations that span multiple services where partial failure requires rollback.

```
Step 1: Reserve inventory    --> Compensate: Release inventory
Step 2: Charge payment       --> Compensate: Refund payment
Step 3: Create shipment      --> Compensate: Cancel shipment
Step 4: Send confirmation    --> Compensate: Send cancellation notice
```

**Saga Implementation Approaches:**

| Approach | When to Use | Trade-off |
|----------|-------------|-----------|
| Choreography | Few steps (2-3), simple coordination | Each service reacts to events; harder to reason about |
| Orchestration | Many steps, complex ordering | Central coordinator; single point of failure but easier to debug |

**Compensation Log Template:**

```markdown
## Saga: [Name]

### Steps (in order)
| Step | Service | Action | Compensation | Timeout |
|------|---------|--------|-------------|---------|
| 1 | Inventory | Reserve items | Release reservation | 30s |
| 2 | Payment | Charge card | Issue refund | 60s |
| 3 | Shipping | Create label | Void label | 45s |

### Failure Scenarios
| Fails At | Steps to Compensate | Order |
|----------|-------------------|-------|
| Step 2 | Compensate Step 1 | Reverse |
| Step 3 | Compensate Step 2, then Step 1 | Reverse |

### Idempotency
All compensation actions MUST be idempotent -- compensating twice
must produce the same result as compensating once.

### Dead Letter
If compensation itself fails after 3 retries:
1. Write to dead letter queue
2. Alert ops team (P1)
3. Manual resolution required within [SLA]
```

---

## 4. Graceful Degradation Hierarchy

Define degradation levels upfront. Each level has a trigger, a behavior change, and a user communication plan.

```
Level 0: FULL SERVICE         (everything works)
   |
   v  trigger: non-critical dependency down
Level 1: REDUCED FEATURES     (secondary features disabled)
   |
   v  trigger: primary write path degraded
Level 2: READ-ONLY            (reads work, writes queued or refused)
   |
   v  trigger: database failover in progress
Level 3: MAINTENANCE MODE     (static page, no dynamic content)
   |
   v  trigger: full outage, security incident
Level 4: OFFLINE              (service unreachable)
```

### Degradation Level Specification

| Level | Name | Trigger | Behavior | User Communication |
|-------|------|---------|----------|-------------------|
| 0 | Full Service | All systems nominal | Normal operation | None needed |
| 1 | Reduced Features | Non-critical service down (e.g., recommendations, analytics) | Core flows work; secondary features show "temporarily unavailable" | Subtle banner: "Some features are temporarily limited" |
| 2 | Read-Only | Write path degraded, DB failover | Reads served from replica; writes return 503 with retry-after | Banner: "We're in read-only mode. Your changes will be saved when we're back." |
| 3 | Maintenance Mode | Major outage, security incident, data migration | Static status page served from CDN | Full-screen: "We're performing maintenance. Check [status page] for updates." |
| 4 | Offline | Complete infrastructure failure | DNS-level failover to static page or nothing | Status page (external): "We're aware of an outage and working to restore service." |

### Feature Criticality Matrix

Before implementing degradation, classify every feature:

| Criticality | Definition | Degradation Behavior | Examples |
|-------------|-----------|---------------------|---------|
| P0 Critical | Core value proposition; outage = revenue loss | Last to degrade, first to restore | Login, checkout, data access |
| P1 Important | Key workflow; degradation = poor UX | Degrade after P0 is protected | Search, notifications, real-time sync |
| P2 Enhancement | Nice-to-have; absence is tolerable | First to shed under load | Recommendations, analytics, avatars |
| P3 Optional | Cosmetic or informational | Can be disabled preemptively | Animations, usage tips, social features |

### Automatic Degradation Rules

```typescript
// Degradation trigger configuration
interface DegradationConfig {
  level1: {
    trigger: 'dependency_circuit_open';
    dependencies: ['recommendation-svc', 'analytics-svc'];
    action: 'disable_features';
    features: ['recommendations', 'real-time-analytics'];
  };
  level2: {
    trigger: 'error_rate_threshold';
    threshold: 0.10; // 10% error rate on write path
    window: '5m';
    action: 'read_only_mode';
  };
  level3: {
    trigger: 'manual' | 'database_unreachable';
    action: 'serve_static_maintenance_page';
  };
}
```

---

## 5. User-Facing Error Experience

### Error Message Guidelines

| Principle | Good | Bad |
|-----------|------|-----|
| Be specific about what happened | "We couldn't save your changes because the file is too large (max 10MB)." | "An error occurred." |
| Be specific about what to do | "Try again, or contact support at help@example.com with code ERR-1234." | "Please try again later." |
| Never blame the user | "We couldn't process that request." | "You entered an invalid value." |
| Never expose internals | "Something went wrong on our end." | "NullPointerException at UserService.java:142" |
| Include a reference code | "Reference: REQ-7f3a2b" | (no way to trace) |
| Give a time estimate when known | "This usually resolves in a few minutes." | "Try again later." |

### Error Message Template

```
[What happened -- one sentence, plain language]
[What the user can do -- specific action]
[Reference code for support -- if applicable]
```

**Examples by severity:**

```
# Transient (auto-retry behind the scenes)
"Saving your changes... taking a bit longer than usual."

# Recoverable (user action needed)
"We couldn't process your payment. Please check your card details and try again.
If the problem continues, contact support with reference PAY-a3f2."

# Blocking (nothing the user can do)
"We're experiencing technical difficulties. Our team has been notified
and is working on it. Check status.example.com for updates. (REF: SYS-9f21)"
```

### Error Page Patterns

| Scenario | Pattern | Content |
|----------|---------|---------|
| 404 Not Found | Helpful redirect | Search bar, popular links, "Go home" button |
| 403 Forbidden | Explain + escalate | Why access is denied, who to contact for access |
| 500 Server Error | Reassure + status | "We know, we're on it", link to status page |
| 503 Maintenance | Estimate + status | Expected return time, status page link |
| Network Error (client) | Offline detection | "You appear to be offline. Changes will sync when you reconnect." |

### Toast / Banner Patterns

| Severity | Style | Duration | Dismissible | Position |
|----------|-------|----------|-------------|----------|
| Success | Green | 3-5s auto-dismiss | Yes | Top-right |
| Info | Blue | 5-8s auto-dismiss | Yes | Top-right |
| Warning | Yellow | Persistent until resolved | Yes | Top-center banner |
| Error | Red | Persistent until dismissed or resolved | Yes | Top-center banner |
| Critical | Red | Persistent, blocks interaction | No (requires action) | Modal overlay |

### Retry UX

| Scenario | UX Pattern |
|----------|-----------|
| Auto-retry in progress | Spinner with "Retrying..." (no user action needed) |
| Auto-retry exhausted | "We couldn't complete this action. [Retry] [Cancel]" button |
| Manual retry appropriate | "Something went wrong. [Try Again]" button with original action |
| Retry inappropriate | "This action cannot be completed right now. Please contact support." (no retry button) |

---

## 6. Monitoring and Alerting Thresholds

### Error Rate Thresholds

| Metric | Warning | Critical | Window | Action |
|--------|---------|----------|--------|--------|
| Overall error rate (5xx) | > 1% | > 5% | 5 min rolling | Page on-call at critical |
| Specific endpoint error rate | > 5% | > 15% | 5 min rolling | Alert channel at warning |
| Client error rate (4xx) | > 10% | > 25% | 15 min rolling | Investigate at warning |
| Database error rate | > 0.1% | > 1% | 5 min rolling | Page on-call at critical |
| Third-party error rate | > 5% | > 20% | 5 min rolling | Activate circuit breaker |
| Timeout rate | > 2% | > 10% | 5 min rolling | Investigate scaling |

### Latency Thresholds

| Metric | Warning | Critical | Window |
|--------|---------|----------|--------|
| P50 latency | > 200ms | > 500ms | 5 min |
| P95 latency | > 1s | > 3s | 5 min |
| P99 latency | > 3s | > 10s | 5 min |
| Database query P95 | > 100ms | > 500ms | 5 min |
| External API P95 | > 2s | > 5s | 5 min |

### Alert Routing

| Severity | Channel | Responder | SLA |
|----------|---------|-----------|-----|
| Critical (P0) | PagerDuty + Slack #incidents | On-call engineer | Acknowledge < 5 min, mitigate < 15 min |
| Error (P1) | Slack #alerts + PagerDuty (low urgency) | On-call engineer | Acknowledge < 15 min, mitigate < 1 hour |
| Warning (P2) | Slack #alerts | Team channel | Investigate within 4 hours |
| Info (P3) | Dashboard only | Review at standup | Next business day |

### Alert Fatigue Prevention

| Rule | Implementation |
|------|---------------|
| Deduplicate | Same error code fires once per window, not per occurrence |
| Group related | Database timeout + query timeout = single incident, not two |
| Auto-resolve | If threshold returns to normal for 2x window, auto-close alert |
| Escalation path | Warning not acknowledged in 30 min escalates to Error |
| Snooze mechanism | Allow 1-hour snooze during active investigation (max 3 snoozes) |

### Dashboard Essentials

Every error handling dashboard MUST include:

```
1. Error Rate Over Time     -- line chart, 5xx by endpoint, last 24h
2. Error Distribution       -- pie chart, by error code, last 1h
3. Top 10 Errors            -- table, code + count + trend, last 1h
4. Latency Percentiles      -- P50/P95/P99 over time, last 24h
5. Circuit Breaker Status   -- per-dependency, current state
6. Degradation Level        -- current level with history
7. Active Alerts            -- open incidents with age
8. Error Budget Remaining   -- percentage of monthly budget consumed
```

---

## 7. Error Budgets and SLOs

### Connecting Error Budget to Availability SLO

| SLO Target | Monthly Error Budget | Daily Error Budget | Meaning |
|------------|---------------------|-------------------|---------|
| 99.9% | 43.8 minutes downtime | ~1.4 minutes | Three nines |
| 99.95% | 21.9 minutes downtime | ~43 seconds | Three and a half nines |
| 99.99% | 4.38 minutes downtime | ~8.6 seconds | Four nines |

Error budget = `(1 - SLO target) * time period`

**Example:** 99.9% monthly SLO = 0.1% of 30 days = 43.2 minutes of allowed downtime/errors.

### Error Budget Burn Rate

| Burn Rate | Meaning | Alert |
|-----------|---------|-------|
| 1x | Consuming budget at expected pace | Normal |
| 2x | Consuming at 2x rate; will exhaust in half the period | Warning |
| 5x | Consuming at 5x rate; will exhaust in ~6 days | Page on-call |
| 10x+ | Major incident consuming budget rapidly | Incident commander |

**Multi-window burn rate alert (recommended):**

| Alert | Short Window | Long Window | Action |
|-------|-------------|-------------|--------|
| Page | 2% budget in 1 hour (14.4x) | 5% budget in 6 hours (6x) | Page on-call |
| Ticket | 5% budget in 3 days (0.5x) | 10% budget in 7 days (0.43x) | Triage at standup |

Both windows must fire simultaneously to reduce false positives.

### Deploy Freeze Policy

| Budget Remaining | Policy |
|-----------------|--------|
| > 50% | Normal deploy cadence |
| 25-50% | Deploy with extra review (requires tech lead approval) |
| 10-25% | Deploy only critical fixes and rollback-ready changes |
| < 10% | Deploy freeze -- only incident fixes allowed |
| Exhausted (0%) | Full freeze until next budget period; post-mortem required |

### SLO Definition Template

```markdown
## SLO: [Service Name]

### SLIs (Service Level Indicators)
| SLI | Measurement | Good Threshold |
|-----|-------------|---------------|
| Availability | Successful requests / total requests | Request returns non-5xx in < 1s |
| Latency | P95 response time | < 500ms |
| Correctness | Valid responses / total responses | Response matches expected schema |

### SLO Targets
| SLI | Target | Measurement Window |
|-----|--------|-------------------|
| Availability | 99.9% | 30-day rolling |
| Latency (P95) | < 500ms | 30-day rolling |
| Correctness | 99.99% | 30-day rolling |

### Error Budget
| SLI | Monthly Budget | Current Burn Rate |
|-----|---------------|------------------|
| Availability | 43.2 minutes | [calculated] |
| Latency | 0.1% of requests can exceed 500ms | [calculated] |

### Stakeholders
- Budget owner: [Team/person]
- Escalation: [Process for budget alerts]
```

---

## 8. Chaos Engineering Basics

### What to Test

| Failure Mode | What to Inject | Expected Behavior |
|-------------|---------------|-------------------|
| Network failure | Drop packets between services | Circuit breaker opens; fallback serves; alert fires |
| Service crash | Kill a service instance | Load balancer routes around; auto-restart; no user impact |
| Slow dependency | Add 5s latency to external API | Timeout triggers; fallback activates; no cascade |
| Database failover | Force primary to replica switch | Writes pause briefly; reads continue; automatic recovery |
| Disk full | Fill disk on one node | Alerts fire; logs rotate; service degrades gracefully |
| DNS failure | Block DNS for a dependency | Cached DNS serves temporarily; circuit breaker opens |
| Certificate expiry | Use expired cert on internal service | TLS error caught; alert fires; fallback or clear error |
| Memory pressure | Consume 90% of available memory | OOM killer targets low-priority; core services survive |
| Clock skew | Shift system clock by 5 minutes | Token validation handles drift; no auth failures |
| Config poison | Deploy invalid config value | Validation rejects; previous config retained; alert fires |

### Chaos Experiment Template

```markdown
## Chaos Experiment: [Name]

### Hypothesis
We believe that [system] can tolerate [failure mode] without
[unacceptable impact] because [reason / mechanism].

### Steady State
Define "normal" before breaking things:
- Error rate: [baseline]
- Latency P95: [baseline]
- Throughput: [baseline]
- User-facing impact: [none expected]

### Method
1. **Scope**: [Which environment: staging / canary / production]
2. **Blast radius**: [Which service / percentage of traffic]
3. **Injection**: [Exact failure to inject]
4. **Duration**: [How long]
5. **Abort criteria**: [Stop immediately if...]

### Observation
- [ ] Monitor error rates during experiment
- [ ] Monitor latency during experiment
- [ ] Check circuit breaker state transitions
- [ ] Verify alerts fired as expected
- [ ] Verify fallback behavior engaged
- [ ] Confirm user-facing impact matches hypothesis

### Result
PASS / FAIL

### Findings
- [What happened]
- [What was surprising]
- [What needs to change]
```

### Tools Overview

| Tool | Type | Best For |
|------|------|---------|
| Chaos Monkey | Instance termination | Testing auto-recovery from instance loss |
| Toxiproxy | Network fault injection | Latency, packet loss, bandwidth limits between services |
| Litmus | Kubernetes-native chaos | Pod kill, network partition, disk fill in K8s |
| Gremlin | Commercial platform | Full-stack chaos with safety controls and reporting |
| AWS FIS | AWS-native | Injecting faults into AWS resources (EC2, RDS, ECS) |
| tc (Linux) | Network shaping | Low-level latency/packet loss injection on Linux hosts |
| kill -9 / docker stop | Manual | Quick process kill for local testing |

### Game Day Planning

```markdown
## Game Day: [Date]

### Objective
Test resilience of [system] against [failure scenarios].

### Participants
- **Facilitator**: [Name] -- runs the experiments
- **Observers**: [Names] -- monitor dashboards
- **Incident Commander**: [Name] -- authorized to abort

### Pre-Requisites
- [ ] Steady-state metrics baselined
- [ ] Rollback procedure confirmed
- [ ] All participants briefed
- [ ] Abort criteria documented
- [ ] Stakeholders notified (especially if production)
- [ ] On-call aware and standing by

### Experiments (in order)
1. [Experiment 1 -- lowest risk first]
2. [Experiment 2]
3. [Experiment 3 -- highest risk last]

### Abort Protocol
If at any point:
- Error rate exceeds [threshold]
- User-facing impact exceeds [threshold]
- Participant calls "abort"

Then immediately stop injection, verify recovery, document findings.

### Post-Game Day
- [ ] Document all findings
- [ ] Create tickets for issues discovered
- [ ] Update runbooks based on learnings
- [ ] Schedule follow-up experiments
- [ ] Share summary with broader team
```

---

## 9. Common Error Handling Anti-Patterns

### Anti-Pattern Catalog

| # | Anti-Pattern | Problem | Fix |
|---|-------------|---------|-----|
| 1 | **Swallowing exceptions** | `catch (e) { /* ignore */ }` hides failures; bugs become invisible | Always log, always propagate or handle explicitly. If intentionally ignoring, add a comment explaining WHY and log at debug level. |
| 2 | **Generic catch-all** | `catch (Exception e) { return "Error" }` treats all errors identically | Catch specific error types; handle each with appropriate recovery strategy. Use catch-all only as a final safety net with full logging. |
| 3 | **Error codes without messages** | Returning `{ error: 42 }` with no human-readable explanation | Every error code MUST have a user message and an internal message (see Section 2). |
| 4 | **No correlation IDs** | Logs from multiple services for one request are impossible to connect | Generate `requestId` at API gateway; propagate through all service calls; include in error responses and logs. |
| 5 | **Logging PII in errors** | `log.error("Login failed for user john@example.com with password p@ss123")` | Never log passwords, tokens, credit card numbers, or PII. Log user IDs (not emails) and sanitize context. |
| 6 | **Retry without backoff** | Tight retry loop hammers a failing service, making it worse | Always use exponential backoff with jitter (see Section 3a). |
| 7 | **Retry non-idempotent operations** | Retrying a payment charge creates duplicate charges | Only retry idempotent operations, or use idempotency keys for non-idempotent ones (see Section 3a). |
| 8 | **No circuit breaker** | One slow dependency brings down the entire system via thread exhaustion | Wrap every external call with a circuit breaker (see Section 3b). |
| 9 | **Leaking stack traces** | Sending `Error: at com.app.UserService.findUser(UserService.java:142)` to the client | Stack traces are internal-only. Return sanitized error with code and user message. |
| 10 | **Boolean error returns** | `function save(): boolean` -- caller has no idea what went wrong | Return result objects or throw typed errors with specific error codes. |
| 11 | **String-based error checking** | `if (error.message.includes("timeout"))` -- fragile, breaks on message changes | Use error codes or typed error classes, never string matching on messages. |
| 12 | **Missing timeout on external calls** | HTTP call with no timeout blocks thread indefinitely | Set explicit timeouts on every external call. Default: connect 5s, read 30s. |
| 13 | **Catch-and-rethrow without context** | `catch (e) { throw e; }` adds a stack frame but no information | If rethrowing, wrap with additional context: `throw new AppError("OrderService.create failed", { cause: e })`. |
| 14 | **Alert on every error** | Every 404 pages the on-call engineer | Alert on rates and patterns, not individual occurrences. Use thresholds (see Section 6). |
| 15 | **No dead letter queue** | Failed async messages are silently dropped | Always route failed messages to a dead letter queue after max retries. Monitor DLQ depth. |

### Detection Checklist

Use during code review to catch anti-patterns:

```markdown
## Error Handling Review Checklist

- [ ] No empty catch blocks (anti-pattern #1)
- [ ] Specific exceptions caught before generic (anti-pattern #2)
- [ ] All error responses include code + user message (anti-pattern #3)
- [ ] Request ID propagated through all layers (anti-pattern #4)
- [ ] No PII in log statements (anti-pattern #5)
- [ ] External calls have retry with backoff (anti-pattern #6)
- [ ] Non-idempotent retries use idempotency keys (anti-pattern #7)
- [ ] External dependencies wrapped with circuit breaker (anti-pattern #8)
- [ ] No stack traces in API responses (anti-pattern #9)
- [ ] Functions return typed errors, not booleans/strings (anti-pattern #10, #11)
- [ ] All external calls have explicit timeouts (anti-pattern #12)
- [ ] Rethrown errors include added context (anti-pattern #13)
- [ ] Alerts configured on rates, not individual errors (anti-pattern #14)
- [ ] Async failures route to dead letter queue (anti-pattern #15)
```

---

## Appendix A: Error Response Envelope (Standard)

```json
{
  "error": {
    "code": "AUTH_002",
    "message": "Your session has expired. Please sign in again.",
    "details": [
      {
        "field": "token",
        "issue": "Token expired at 2024-01-15T10:30:00Z"
      }
    ],
    "retryable": false,
    "retryAfter": null,
    "helpUrl": "https://docs.example.com/errors/AUTH_002",
    "requestId": "req_7f3a2b9c"
  }
}
```

**Field definitions:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `code` | string | Yes | Machine-readable error code |
| `message` | string | Yes | User-friendly description |
| `details` | array | No | Field-level errors for validation |
| `retryable` | boolean | Yes | Whether the client should retry |
| `retryAfter` | integer/null | No | Seconds to wait before retry (if retryable) |
| `helpUrl` | string | No | Link to documentation for this error |
| `requestId` | string | Yes | Correlation ID for support/debugging |

---

## Appendix B: Error Handling Decision Tree

```
Error occurs
  |
  +-- Is it expected? (validation, auth, not-found)
  |     '-- YES -> Return appropriate 4xx with user message
  |
  +-- Is it transient? (timeout, connection reset, 503)
  |     '-- YES -> Retry with backoff
  |           +-- Retry succeeds -> Continue normally
  |           '-- Retries exhausted -> Check circuit breaker
  |                 +-- Circuit open -> Return fallback
  |                 '-- Circuit closed -> Open circuit, return fallback
  |
  +-- Is it a dependency failure? (external API, database)
  |     '-- YES -> Check circuit breaker state
  |           +-- Open -> Return cached/fallback immediately
  |           '-- Closed/Half-open -> Attempt call with timeout
  |
  '-- Is it unexpected? (null pointer, logic error)
        '-- YES -> Log full context (no PII), return 500 with requestId
              '-- Alert if rate exceeds threshold
```

---

## Appendix C: Implementation Checklist

Use this checklist when implementing error handling for a new service or feature:

```markdown
## Error Handling Implementation Checklist

### Foundation
- [ ] Error code registry created for this domain
- [ ] Custom error classes defined (extends base AppError)
- [ ] Error response envelope follows standard format (Appendix A)
- [ ] Request ID middleware installed (generates and propagates)
- [ ] Global error handler catches unhandled exceptions

### Per External Dependency
- [ ] Circuit breaker configured
- [ ] Retry policy defined (max retries, backoff, jitter)
- [ ] Timeout set (connect + read)
- [ ] Fallback behavior defined
- [ ] Health check endpoint monitors dependency

### Monitoring
- [ ] Error rate dashboards created
- [ ] Alert thresholds configured per Section 6
- [ ] Error budget tracking enabled
- [ ] Correlation ID searchable in log aggregator

### User Experience
- [ ] Error messages reviewed for clarity (non-technical, actionable)
- [ ] Error pages designed for major failure modes
- [ ] Toast/banner patterns consistent with Section 5
- [ ] Retry UX appropriate per error type

### Resilience
- [ ] Graceful degradation levels defined (Section 4)
- [ ] Feature criticality classified
- [ ] Chaos experiments planned for critical paths
- [ ] Runbooks written for top 5 expected failure modes
```
