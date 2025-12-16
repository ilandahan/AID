# Learning Mode - Simulation Examples

Real interaction examples showing Learning Mode in action across phases and roles.

---

## Simulation 1: Architecture Decision with Debate

### Context
- **Phase:** 2 - Tech Spec
- **Role:** Developer
- **Task:** Choose database for new project

### Interaction

**User:** We need to decide on a database for the new e-commerce platform.

**Claude:**

Let me analyze the options based on your project requirements.

<debate-invitation>
**Topic:** Database selection for e-commerce platform

**Option A: PostgreSQL**
- ✅ Pros:
  - Strong ACID compliance for financial transactions
  - Excellent relational query support
  - Rich ecosystem, battle-tested
  - JSON support for flexible product attributes
- ❌ Cons:
  - Horizontal scaling requires more effort
  - Can be complex for simple read-heavy workloads
- Best when: Complex queries, financial data, relationships matter

**Option B: MongoDB**
- ✅ Pros:
  - Flexible schema for varied product types
  - Easy horizontal scaling
  - Fast reads for catalog browsing
- ❌ Cons:
  - Weaker transaction support (improved in recent versions)
  - Can lead to data inconsistency if not careful
  - Joins are expensive
- Best when: Catalog-heavy, varied product schemas, scale-out needed

**Option C: PostgreSQL + Redis Cache**
- ✅ Pros:
  - Best of both: ACID for orders + fast reads for catalog
  - Proven pattern for e-commerce
- ❌ Cons:
  - Two systems to maintain
  - Cache invalidation complexity
- Best when: High traffic, need both reliability and speed

**My Lean:** Option C (PostgreSQL + Redis) - E-commerce needs transaction safety for orders AND fast catalog reads. This is the proven pattern used by most successful platforms.

**But Consider:** If team has limited DevOps capacity, managing two data stores adds complexity. Pure PostgreSQL with proper indexing might be simpler to start.

**Your Input Needed:**
- What's the expected traffic level?
- Does the team have Redis experience?
- How varied are the product types (standard vs. completely different attributes)?
</debate-invitation>

**User:** We expect moderate traffic initially, team knows PostgreSQL well but not Redis. Products are fairly standard with some custom attributes.

**Claude:**

<decision-transparency>
**Decision:** PostgreSQL only (Option A) with JSON columns for custom attributes

**Reasoning:**
- **Traffic level**: Moderate traffic doesn't require cache layer initially
- **Team expertise**: Team knows PostgreSQL, no Redis experience = faster development
- **Product structure**: Fairly standard products means relational model works well
- **Custom attributes**: PostgreSQL's JSONB handles flexible attributes efficiently
- **Future path**: Can add Redis later if traffic demands it

**Alternatives Considered:**
1. PostgreSQL + Redis - Deferred: Adds complexity team isn't ready for
2. MongoDB - Rejected: Team expertise is in PostgreSQL, standard products suit relational model

**Confidence:** High - Clear match between requirements and solution

**Open to Debate:** Yes - If you anticipate rapid traffic growth, we could discuss Redis from day 1
</decision-transparency>

I'll proceed with PostgreSQL in the tech spec. We'll use JSONB columns for custom product attributes, which gives you flexibility without sacrificing query performance.

<learning-captured>
**What I Learned:**
This team values simplicity and leveraging existing expertise over optimal architecture when trade-offs are acceptable.

**Source:**
- User feedback on: Database selection debate
- Decision context: Chose simpler option due to team familiarity

**Applied To:**
- Future architecture decisions will weight team expertise more heavily
- Will present "start simple, add complexity later" as valid pattern

**Verification:**
- Will apply this preference in infrastructure decisions
</learning-captured>

---

## Simulation 2: PRD Phase Feedback

### Context
- **Phase:** 1 - PRD
- **Role:** Product Manager
- **Task:** Complete user authentication PRD

### Interaction

**Claude:**

I've completed the draft PRD for the User Authentication feature. Here's a summary:

**Scope:**
- Email/password registration and login
- Password reset flow
- Session management
- OAuth (Google, GitHub) - Phase 2

**User Stories:** 12 stories covering registration, login, logout, password management

**Acceptance Criteria:** Defined for each story with specific, testable conditions

<feedback-request>
**Context:** PRD draft completed for User Authentication feature

**Seeking Feedback On:**
1. **Completeness**: Did I capture all authentication scenarios?
2. **Scope boundaries**: Is OAuth correctly deferred to Phase 2?
3. **Acceptance criteria**: Are they specific and testable enough?
4. **Security considerations**: Did I address the key security requirements?

**Questions:**
- Should "Remember me" functionality be in Phase 1 or deferred?
- Are there specific compliance requirements (SOC2, GDPR) I should address?
- Is the session timeout (24 hours) appropriate for your use case?

**Rating Request:** On a scale of 1-5, how well does this PRD capture your requirements?
- 1 = Missing major requirements
- 3 = Good start but needs work
- 5 = Ready for Tech Spec phase

**Improvement Ideas Welcome:** What would make this PRD better?
</feedback-request>

**User:** Rating: 4. Good work. Add "Remember me" to Phase 1, session timeout should be 7 days for remembered sessions. Also need to add rate limiting for login attempts - security requirement.

**Claude:**

Thank you for the feedback. I'll update the PRD with these additions:

<learning-captured>
**What I Learned:**
1. "Remember me" is a baseline expectation, not a nice-to-have
2. This team has specific security requirements (rate limiting) that should be proactively addressed
3. 7-day session for remembered users is the preferred default

**Source:**
- User feedback on: PRD Authentication phase
- Rating: 4/5 with specific improvements

**Applied To:**
- Future authentication PRDs will include "Remember me" by default
- Will proactively include rate limiting in any login-related feature
- Will ask about session duration preferences early

**Verification:**
- Will check for these patterns in next security-related PRD
</learning-captured>

**Updates made:**
1. ✅ Added "Remember me" checkbox to login flow (Phase 1)
2. ✅ Updated session management:
   - Standard session: 24 hours
   - Remembered session: 7 days
3. ✅ Added new user story: "Rate Limiting for Login Attempts"
   - Max 5 failed attempts per 15 minutes
   - Lockout notification email
   - Admin unlock capability

Shall I proceed with the Tech Spec phase, or are there other PRD adjustments needed?

---

## Simulation 3: Code Review with Learning

### Context
- **Phase:** 4 - Development
- **Role:** Developer
- **Task:** Review submitted code

### Interaction

**User:** Please review my authentication middleware code.

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

<decision-transparency>
**Decision:** Approve with minor suggestions

**Reasoning:**
- **Core logic**: Correct - token extraction, verification, and error handling are proper
- **Security**: Good - doesn't expose internal error details
- **Pattern**: Standard JWT middleware pattern

**Issues Found:**
1. Minor: No TypeScript types (if using TS)
2. Minor: Could benefit from token expiration check (though jwt.verify handles this)

**Confidence:** High - This is standard, secure middleware

**Open to Debate:** No - This is straightforward approval
</decision-transparency>

**Review Result: ✅ Approved**

The code is solid. A few optional improvements:

```typescript
// Optional: Add explicit typing if using TypeScript
interface JWTPayload {
  userId: string;
  email: string;
  iat: number;
  exp: number;
}

const authMiddleware = async (
  req: Request & { user?: JWTPayload },
  res: Response,
  next: NextFunction
) => {
  // ... same logic
};
```

The current implementation correctly:
- Extracts Bearer token
- Handles missing token case
- Verifies JWT (including expiration)
- Doesn't leak error details

**User:** Actually, we don't use TypeScript in this project. Also, I prefer keeping middleware simple - no need for the explicit typing suggestion.

**Claude:**

<learning-captured>
**What I Learned:**
1. This project uses JavaScript, not TypeScript
2. Team prefers simple, minimal middleware over defensive typing
3. Should check project language before suggesting TypeScript patterns

**Source:**
- User feedback on: Code review suggestions
- Context: TypeScript suggestions were not applicable

**Applied To:**
- Will check package.json/project config before suggesting typed patterns
- Will keep middleware suggestions minimal unless complexity warrants it
- JavaScript projects get JavaScript suggestions

**Verification:**
- Next code review will check project language first
</learning-captured>

Understood! Your middleware is good as-is. Clean, simple, and handles the essential cases correctly.

For this JavaScript project, I'll keep future suggestions focused on logic and security rather than typing patterns.

---

## Simulation 4: Tech Spec Phase Gate

### Context
- **Phase:** 2 - Tech Spec (completing)
- **Role:** Tech Lead
- **Task:** Phase gate review

### Interaction

**Claude:**

Phase 2 (Tech Spec) is complete. Here's the summary:

**Deliverables:**
- System architecture diagram
- Database schema (PostgreSQL)
- API contracts (OpenAPI spec)
- Security architecture
- Infrastructure requirements

<feedback-request>
**Context:** Phase 2 - Technical Specification completed

**Phase Deliverables:**
- ✅ System Architecture: Microservices with API Gateway
- ✅ Database Schema: 15 tables, normalized with proper indexes
- ✅ API Contracts: 42 endpoints documented in OpenAPI
- ✅ Security: JWT auth, rate limiting, input validation
- ✅ Infrastructure: AWS ECS, RDS, ElastiCache

**Seeking Feedback On:**
1. Is the architecture appropriate for the scale we discussed?
2. Are the API contracts complete enough for frontend development?
3. Any security concerns I should address before implementation?

**Questions:**
- Should we add WebSocket specs for real-time features?
- Is the proposed caching strategy sufficient?
- Any infrastructure preferences I should know about?

**Rating Request:** On a scale of 1-5, how ready are we for Implementation Planning?
- 1 = Major gaps, need significant rework
- 3 = Some concerns but can proceed
- 5 = Excellent, ready for Phase 3

**Improvement Ideas Welcome:** What would strengthen this spec?
</feedback-request>

**User:** Rating: 3. The spec is good but I have concerns about the microservices approach for our small team. Also, we need WebSocket specs for the notification system. Let's discuss the architecture.

**Claude:**

<debate-invitation>
**Topic:** Architecture approach - Microservices vs Monolith for small team

**Option A: Keep Microservices (Current)**
- ✅ Pros:
  - Independent scaling per service
  - Technology flexibility
  - Clear service boundaries
- ❌ Cons:
  - Operational overhead for small team
  - Network complexity
  - Distributed debugging challenges
- Best when: Large team, need independent deployments

**Option B: Modular Monolith**
- ✅ Pros:
  - Simpler operations (one deployment)
  - Easier debugging
  - Lower infrastructure cost
  - Can extract to microservices later
- ❌ Cons:
  - All-or-nothing deployments
  - Potential for tight coupling if not careful
- Best when: Small team, rapid iteration, unclear scaling needs

**Option C: Hybrid (API Gateway + Monolith Core)**
- ✅ Pros:
  - Simple core with flexibility for extraction
  - API Gateway handles cross-cutting concerns
  - Best path for "start simple, scale later"
- ❌ Cons:
  - Still need API Gateway ops
- Best when: Want to keep options open

**My Lean:** Option B (Modular Monolith) given the small team context you mentioned. We can design with clear module boundaries so extraction is possible later.

**But Consider:** If one specific service (like notifications) has very different scaling needs, we could do Option C - monolith core with notifications as separate service.

**Your Input Needed:**
- How small is the team?
- Do you anticipate any specific service needing independent scaling?
</debate-invitation>

**User:** Team is 3 developers. Go with modular monolith. Notifications can be a separate service since it might have different load patterns.

**Claude:**

<decision-transparency>
**Decision:** Hybrid architecture - Modular Monolith + Notification Microservice

**Reasoning:**
- **Team size (3)**: Too small for full microservices operational overhead
- **Core services**: Auth, Users, Products, Orders → Monolith with clear modules
- **Notifications**: Separate service due to different scaling patterns (spiky during events)
- **Future flexibility**: Module boundaries allow extraction if/when team grows

**Alternatives Considered:**
1. Full microservices - Rejected: Too much ops overhead for 3 devs
2. Pure monolith - Modified: Notifications genuinely benefits from separation

**Confidence:** High - Clear team size and scaling constraints

**Open to Debate:** No - User decision is clear
</decision-transparency>

<learning-captured>
**What I Learned:**
1. Team size is critical context for architecture decisions
2. For small teams (≤5), default to monolith unless specific service needs differ
3. This team prefers practical over theoretical optimal

**Source:**
- User feedback on: Architecture debate
- Context: 3-person team, chose modular monolith

**Applied To:**
- Will ask about team size early in Tech Spec phase
- Will default to simpler architectures for small teams
- Will only suggest microservices for specific, justified services

**Verification:**
- Next project architecture will start with team size question
</learning-captured>

I'll update the Tech Spec with:

1. **Core Architecture:** Modular Monolith
   - Auth module
   - Users module
   - Products module
   - Orders module

2. **Separate Service:** Notifications
   - WebSocket support for real-time
   - Independent scaling
   - Message queue integration with core

3. **Infrastructure:** Simplified
   - Single ECS service for core (vs 5 separate)
   - Separate ECS service for notifications
   - Shared RDS

Shall I proceed with these updates and add the WebSocket specifications?

---

## Simulation 5: Test Strategy Debate

### Context
- **Phase:** 4 - Development
- **Role:** QA Engineer
- **Task:** Define test strategy

### Interaction

**User:** We need to define the testing approach for the checkout flow.

**Claude:**

<debate-invitation>
**Topic:** Test strategy for checkout flow

**Option A: Heavy Unit Testing**
- ✅ Pros: Fast feedback, isolated, easy to maintain
- ❌ Cons: Doesn't catch integration issues, can miss real-world failures
- Coverage target: 90% unit, 10% integration, few E2E

**Option B: Integration-Focused**
- ✅ Pros: Tests real interactions, catches more bugs
- ❌ Cons: Slower, harder to debug failures, flakier
- Coverage target: 50% unit, 40% integration, 10% E2E

**Option C: E2E-Heavy with Critical Path Coverage**
- ✅ Pros: Tests what users actually do, highest confidence
- ❌ Cons: Slowest, most brittle, expensive to maintain
- Coverage target: 30% unit, 30% integration, 40% E2E

**Option D: Testing Trophy (Recommended)**
- ✅ Pros: Balanced - unit for logic, integration for flows, E2E for critical paths
- ❌ Cons: Requires discipline to maintain balance
- Coverage target: 40% unit, 40% integration, 20% E2E

**My Lean:** Option D (Testing Trophy) - Checkout is critical and complex:
- Unit tests for price calculations, validation logic
- Integration tests for payment gateway, inventory checks
- E2E tests for complete happy path + key failure scenarios

**But Consider:** If CI pipeline time is a constraint, we might lean more toward Option A with strategic E2E.

**Your Input Needed:**
- What's the acceptable CI pipeline time?
- How critical is checkout (is it the core revenue path)?
- Does the team have E2E testing experience (Playwright/Cypress)?
</debate-invitation>

**User:** Checkout is critical - it's 100% of revenue. Team knows Playwright. CI time should stay under 10 minutes for PRs.

**Claude:**

<decision-transparency>
**Decision:** Testing Trophy with optimized E2E for CI

**Reasoning:**
- **Revenue criticality**: 100% of revenue = maximum coverage needed
- **Team capability**: Playwright experience enables E2E
- **CI constraint**: 10 min limit requires smart test selection

**Strategy:**
1. **Unit tests (40%)**: Price calc, discounts, validation - runs in < 1 min
2. **Integration tests (40%)**: Payment mock, inventory service - runs in < 3 min
3. **E2E tests (20%)**: Critical paths only, parallelized - runs in < 5 min
4. **Full E2E suite**: Runs on merge to main (not PRs)

**Test Distribution for Checkout:**
- Unit: ~25 tests (calculation logic)
- Integration: ~15 tests (service interactions)
- E2E: ~5 tests (critical happy/error paths)

**Confidence:** High - Matches constraints and criticality

**Open to Debate:** Yes - E2E test selection could be discussed
</decision-transparency>

Here's the detailed test plan:

**PR Pipeline (< 10 min):**
```
Unit tests: ~1 min
├── Cart calculations
├── Discount validation
├── Address validation
└── Order total logic

Integration tests: ~3 min
├── Payment gateway (mocked)
├── Inventory check
├── Order creation
└── Email trigger

E2E critical paths: ~5 min (parallelized)
├── Happy path: Add → Cart → Checkout → Payment → Confirmation
├── Payment failure + retry
├── Out of stock handling
├── Discount code application
└── Guest vs logged-in checkout
```

**Main branch (full suite):**
- All above + edge cases
- Multiple payment methods
- International addresses
- Various product combinations

<feedback-request>
**Context:** Test strategy defined for checkout

**Seeking Feedback On:**
1. Is the test distribution appropriate?
2. Are the E2E critical paths correct?
3. Any scenarios I'm missing?

**Rating:** 1-5 for this test strategy?
</feedback-request>

---

## Key Patterns Demonstrated

| Pattern | Shown In |
|---------|----------|
| Decision Transparency | Simulations 1, 3, 4, 5 |
| Debate Invitation | Simulations 1, 4, 5 |
| Feedback Request | Simulations 2, 4, 5 |
| Learning Capture | All simulations |
| User Preference Integration | Simulations 1, 3, 4 |
| Phase Gate Review | Simulation 4 |

---

## Anti-Patterns to Avoid

### ❌ Over-ceremony for Simple Decisions

**Bad:**
```
<debate-invitation>
**Topic:** Variable naming

**Option A:** `userData`
**Option B:** `userInfo`
...
```

**Good:** Just use consistent naming and move on.

### ❌ Ignoring User Signals

**Bad:** Continuing to suggest TypeScript after user said they use JavaScript.

**Good:** Capture learning and adapt immediately.

### ❌ Fake Debates (When Answer is Obvious)

**Bad:** Creating a debate when there's clearly one right answer.

**Good:** Use Decision Transparency to explain the obvious choice.

### ❌ Too Many Feedback Requests

**Bad:** Asking for rating after every small task.

**Good:** Request feedback at meaningful milestones and phase gates.
