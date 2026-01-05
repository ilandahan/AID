# Learning Mode - Simulation Examples

Real interaction examples showing Learning Mode in action.

## Simulation 1: Architecture Decision with Debate

**Context:** Phase 2 Tech Spec, Developer, Database choice

**User:** We need to decide on a database for the new e-commerce platform.

**Claude:**

```markdown
<debate-invitation>
**Topic:** Database selection for e-commerce platform

**Option A: PostgreSQL**
- Pros: Strong ACID compliance, excellent relational queries, battle-tested, JSON support
- Cons: Horizontal scaling requires more effort
- Best when: Complex queries, financial data, relationships matter

**Option B: MongoDB**
- Pros: Flexible schema, easy horizontal scaling, fast reads
- Cons: Weaker transaction support, joins are expensive
- Best when: Catalog-heavy, varied product schemas, scale-out needed

**Option C: PostgreSQL + Redis Cache**
- Pros: Best of both: ACID for orders + fast reads for catalog
- Cons: Two systems to maintain, cache invalidation complexity
- Best when: High traffic, need both reliability and speed

**My Lean:** Option C - E-commerce needs transaction safety for orders AND fast catalog reads.

**But Consider:** If team has limited DevOps capacity, managing two data stores adds complexity.

**Your Input Needed:** Expected traffic? Team Redis experience? How varied are product types?
</debate-invitation>
```

**User:** Moderate traffic, team knows PostgreSQL but not Redis. Products fairly standard.

**Claude:**

```markdown
<decision-transparency>
**Decision:** PostgreSQL only with JSON columns for custom attributes

**Reasoning:**
- **Traffic level**: Moderate traffic doesn't require cache layer initially
- **Team expertise**: Team knows PostgreSQL, no Redis experience = faster development
- **Product structure**: Standard products suit relational model well
- **Future path**: Can add Redis later if traffic demands it

**Alternatives Considered:**
1. PostgreSQL + Redis - Deferred: Adds complexity team isn't ready for
2. MongoDB - Rejected: Team expertise is in PostgreSQL

**Confidence:** High - Clear match between requirements and solution

**Open to Debate:** Yes - If you anticipate rapid traffic growth, we could discuss Redis from day 1
</decision-transparency>

<learning-captured>
**What I Learned:**
This team values simplicity and leveraging existing expertise over optimal architecture.

**Applied To:**
- Future architecture decisions will weight team expertise more heavily
- Will present "start simple, add complexity later" as valid pattern
</learning-captured>
```

---

## Simulation 2: PRD Phase Feedback

**Context:** Phase 1 PRD, PM, Authentication

**Claude:**

PRD draft completed for User Authentication:
- Email/password registration and login
- Password reset flow
- Session management
- OAuth (Google, GitHub) - Phase 2

```markdown
<feedback-request>
**Context:** PRD draft completed for User Authentication feature

**Seeking Feedback On:**
1. Completeness: Did I capture all authentication scenarios?
2. Scope boundaries: Is OAuth correctly deferred to Phase 2?
3. Acceptance criteria: Are they specific and testable enough?

**Questions:**
- Should "Remember me" functionality be in Phase 1 or deferred?
- Are there specific compliance requirements (SOC2, GDPR)?
- Is the session timeout (24 hours) appropriate?

**Rating Request:** 1-5, how well does this PRD capture your requirements?
</feedback-request>
```

**User:** Rating: 4. Add "Remember me" to Phase 1, session timeout 7 days for remembered. Also need rate limiting for login attempts.

**Claude:**

```markdown
<learning-captured>
**What I Learned:**
1. "Remember me" is baseline expectation, not nice-to-have
2. This team has specific security requirements (rate limiting) to proactively address
3. 7-day session for remembered users is preferred default

**Applied To:**
- Future auth PRDs will include "Remember me" by default
- Will proactively include rate limiting in login-related features
</learning-captured>
```

Updates made:
1. Added "Remember me" to login flow (Phase 1)
2. Updated sessions: Standard 24h, Remembered 7 days
3. Added rate limiting: Max 5 failed attempts/15 min, lockout notification

---

## Simulation 3: Code Review with Learning

**Context:** Phase 4 Development, Developer, Code review

**User:** Please review my authentication middleware:

```typescript
const authMiddleware = async (req, res, next) => {
  const token = req.headers.authorization?.split(' ')[1];
  if (!token) {
    return res.status(401).json({ error: 'No token provided' });
  }
  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    req.user = decoded;
    next();
  } catch (err) {
    return res.status(401).json({ error: 'Invalid token' });
  }
};
```

**Claude:**

```markdown
<decision-transparency>
**Decision:** Approve with minor suggestions

**Reasoning:**
- Core logic correct - token extraction, verification, error handling proper
- Security good - doesn't expose internal error details
- Pattern: Standard JWT middleware

**Confidence:** High - This is standard, secure middleware
</decision-transparency>
```

Review Result: Approved

Optional improvement if using TypeScript:
```typescript
interface JWTPayload {
  userId: string;
  email: string;
}
const authMiddleware = async (
  req: Request & { user?: JWTPayload },
  res: Response,
  next: NextFunction
) => { /* same logic */ };
```

**User:** We don't use TypeScript. Prefer keeping middleware simple.

**Claude:**

```markdown
<learning-captured>
**What I Learned:**
1. This project uses JavaScript, not TypeScript
2. Team prefers simple, minimal middleware
3. Should check project language before suggesting typed patterns

**Applied To:**
- Will check package.json/project config before suggesting typed patterns
- JavaScript projects get JavaScript suggestions
</learning-captured>
```

Understood! Your middleware is good as-is - clean, simple, handles essential cases.

---

## Simulation 4: Tech Spec Phase Gate

**Context:** Phase 2 Tech Spec completing, Tech Lead

**Claude:**

```markdown
<feedback-request>
**Context:** Phase 2 Technical Specification completed

**Deliverables:**
- System Architecture: Microservices with API Gateway
- Database Schema: 15 tables, normalized
- API Contracts: 42 endpoints in OpenAPI
- Security: JWT auth, rate limiting
- Infrastructure: AWS ECS, RDS, ElastiCache

**Seeking Feedback On:**
1. Is architecture appropriate for discussed scale?
2. Are API contracts complete for frontend development?
3. Any security concerns before implementation?

**Rating:** 1-5, how ready for Implementation Planning?
</feedback-request>
```

**User:** Rating: 3. Concerns about microservices for our small team. Need WebSocket specs for notifications.

**Claude:**

```markdown
<debate-invitation>
**Topic:** Architecture approach - Microservices vs Monolith for small team

**Option A: Keep Microservices**
- Pros: Independent scaling, technology flexibility, clear boundaries
- Cons: Operational overhead, network complexity, distributed debugging
- Best when: Large team, need independent deployments

**Option B: Modular Monolith**
- Pros: Simpler ops (one deployment), easier debugging, lower cost, can extract later
- Cons: All-or-nothing deployments, potential coupling
- Best when: Small team, rapid iteration, unclear scaling needs

**Option C: Hybrid (Monolith + Notification Service)**
- Pros: Simple core with flexibility, best "start simple, scale later" path
- Cons: Still need some distributed ops
- Best when: Want options open

**My Lean:** Option B given small team. Design with module boundaries for later extraction.

**Your Input Needed:** How small is team? Any service needing independent scaling?
</debate-invitation>
```

**User:** Team is 3 developers. Go modular monolith. Notifications separate since different load patterns.

**Claude:**

```markdown
<decision-transparency>
**Decision:** Hybrid - Modular Monolith + Notification Microservice

**Reasoning:**
- **Team size (3)**: Too small for full microservices overhead
- **Core services**: Auth, Users, Products, Orders -> Monolith with modules
- **Notifications**: Separate due to spiky scaling patterns
- **Future**: Module boundaries allow extraction when team grows

**Confidence:** High - Clear team size and scaling constraints
</decision-transparency>

<learning-captured>
**What I Learned:**
1. Team size is critical context for architecture decisions
2. For small teams (<=5), default to monolith unless specific needs differ
3. This team prefers practical over theoretical optimal

**Applied To:**
- Will ask about team size early in Tech Spec phase
- Will default to simpler architectures for small teams
</learning-captured>
```

---

## Simulation 5: Test Strategy Debate

**Context:** Phase 4 Development, QA, Test strategy

**User:** Need to define testing approach for checkout flow.

**Claude:**

```markdown
<debate-invitation>
**Topic:** Test strategy for checkout flow

**Option A: Heavy Unit Testing**
- Pros: Fast feedback, isolated, easy to maintain
- Cons: Doesn't catch integration issues
- Target: 90% unit, 10% integration, few E2E

**Option B: Integration-Focused**
- Pros: Tests real interactions, catches more bugs
- Cons: Slower, harder to debug, flakier
- Target: 50% unit, 40% integration, 10% E2E

**Option C: E2E-Heavy**
- Pros: Tests what users do, highest confidence
- Cons: Slowest, most brittle, expensive
- Target: 30% unit, 30% integration, 40% E2E

**Option D: Testing Trophy (Recommended)**
- Pros: Balanced - unit for logic, integration for flows, E2E for critical
- Cons: Requires discipline
- Target: 40% unit, 40% integration, 20% E2E

**My Lean:** Option D - Checkout is critical and complex

**Your Input Needed:** Acceptable CI time? How critical is checkout? Team E2E experience?
</debate-invitation>
```

**User:** Checkout is critical - 100% of revenue. Team knows Playwright. CI under 10 min.

**Claude:**

```markdown
<decision-transparency>
**Decision:** Testing Trophy with optimized E2E for CI

**Reasoning:**
- **Revenue criticality**: 100% = maximum coverage needed
- **Team capability**: Playwright experience enables E2E
- **CI constraint**: 10 min limit requires smart test selection

**Strategy:**
1. Unit (40%): Price calc, discounts, validation - < 1 min
2. Integration (40%): Payment mock, inventory - < 3 min
3. E2E (20%): Critical paths, parallelized - < 5 min
4. Full E2E: On merge to main only

**PR Pipeline (< 10 min):**
- Unit: Cart calculations, discount validation, address validation
- Integration: Payment gateway (mocked), inventory check, order creation
- E2E critical paths: Happy path, payment failure, out of stock, discount code, guest checkout

**Confidence:** High - Matches constraints and criticality
</decision-transparency>
```

---

## Key Patterns

| Pattern | Used In |
|---------|---------|
| Decision Transparency | 1, 3, 4, 5 |
| Debate Invitation | 1, 4, 5 |
| Feedback Request | 2, 4 |
| Learning Capture | All |

## Anti-Patterns

| Dont | Example |
|------|---------|
| Over-ceremony for simple | Debate on variable naming |
| Ignore user signals | Suggest TS after user said JS |
| Fake debates | When answer is obvious |
| Too many feedback requests | After every small task |
