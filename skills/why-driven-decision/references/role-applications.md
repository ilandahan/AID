# Role-Specific WHY Applications

How each role embeds WHY-driven thinking into daily work.

## Product Manager

**WHY Focus:** User value and business impact

**Daily Questions:**
- "Why would a user choose this over alternatives?"
- "Why is this the most important thing right now?"
- "Why will this move metrics we care about?"
- "Why should engineering spend time on this?"

**In Every Conversation:**
- Before requesting: "The WHY is..."
- When prioritizing: "This ranks higher because..."
- When saying no: "We're not doing this because..."

## Developer

**WHY Focus:** Technical decisions, code quality, and component relationships

**Daily Questions:**
- "Why am I building it this way?"
- "Why will this be maintainable?"
- "Why is this the right abstraction?"
- "Why will future-me thank present-me?"

**Component Connection Questions:**
- "Why does this module depend on that one?"
- "Why is this the right boundary between components?"
- "Why expose this interface vs keeping it internal?"
- "Why this data flow direction?"

**In Every PR:**
- Comment explaining WHY, not just WHAT
- "I chose X over Y because..."
- "This approach enables..."
- "This connects to [component] because..."

**WHY-Driven Code Comments:**
```python
# WHY: Users with large datasets were timing out.
# This pagination keeps response times under 200ms
# while allowing unlimited result sets.
def paginated_query(query, page_size=100):
    ...
```

**Component Documentation Pattern:**
```python
"""
UserAuthService

WHY THIS EXISTS:
Centralizes all authentication logic to ensure consistent security
policies across the application.

CONNECTIONS:
- CALLED BY: LoginController, APIGateway, WebSocketHandler
- CALLS: UserRepository, TokenService, AuditLogger
- WHY THESE CONNECTIONS: Single entry point for auth decisions,
  audit trail for compliance, token management for stateless auth

DESIGN DECISIONS:
- WHY stateless tokens: Enables horizontal scaling without session affinity
- WHY refresh tokens: Balance security (short-lived) with UX (no re-login)
- WHY audit logging here: Auth is the trust boundary, must be auditable
"""
```

## Tech Lead

**WHY Focus:** Architecture and team decisions

**Daily Questions:**
- "Why this architecture for this problem?"
- "Why assign this to this person?"
- "Why is this technical debt acceptable/not?"
- "Why will this scale?"

**In Every Review:**
- "Why did you choose this approach?"
- "What's the WHY behind this pattern?"

## QA Engineer

**WHY Focus:** Risk, user protection, and failure prevention

**Daily Questions:**
- "Why would this fail?"
- "Why does this test matter?"
- "Why is this edge case important?"
- "Why is this severity level correct?"

**In Every Test:**
- Document WHY this scenario matters
- "This test exists because..."

### BDD Integration

**Every Gherkin feature needs WHY context:**
```gherkin
Feature: Shopping Cart Checkout
  """
  WHY: Cart abandonment costs us $2M/year. A smooth checkout
  reduces abandonment by 15%.
  """
  
  Scenario: Apply discount code
    """
    WHY: 40% of purchases use discount codes. Failures here
    directly impact revenue and customer satisfaction.
    """
    Given a cart with items totaling $100
    When I apply discount code "SAVE20"
    Then the total should be $80
```

### TDD Integration

**Write WHY before writing the test:**
```python
def test_prevents_duplicate_order_submission():
    """
    WHY THIS TEST:
    - PROBLEM: Users double-clicking submit created duplicate orders
    - FREQUENCY: 2.3% of all orders were duplicates
    - COST: $45K/month in refund processing + customer frustration
    - SOLUTION: Idempotency key prevents duplicate processing
    - SUCCESS METRIC: Duplicate orders < 0.1%
    """
    # Test implementation
```

**Test Suite Organization by WHY:**
```python
class TestPaymentFailurePrevention:
    """
    WHY THIS SUITE:
    These tests prevent the top 5 payment failures that cost us
    $50K/month in support and lost revenue.
    
    Priority order based on business impact:
    1. Double charges ($20K/month)
    2. Silent failures ($15K/month)
    3. Timeout handling ($10K/month)
    4. Invalid card handling ($3K/month)
    5. Currency conversion ($2K/month)
    """
```

## Designer

**WHY Focus:** User experience and behavior

**Daily Questions:**
- "Why will users understand this?"
- "Why is this the right interaction?"
- "Why does this solve the user's real problem?"
- "Why is this accessible?"

**In Every Design:**
- Annotate WHY decisions, not just WHAT
- "Users need this because..."

## WHY-Driven Communication Examples

### In Slack/Chat
```
❌ "Can you add a loading spinner?"
✅ "Users are confused when data takes time to load—can you add a 
    spinner so they know it's working?"
```

### In PRs
```
❌ "Refactored the auth module"
✅ "Refactored auth to separate concerns—this makes adding OAuth 
    providers easier"
```

### In Tickets
```
❌ "Add export button"
✅ "Add export button—users need to share reports with stakeholders 
    who don't have system access"
```

### In Meetings
```
❌ "I think we should use Redis"
✅ "I think we should use Redis because we need sub-millisecond reads 
    for the autocomplete feature"
```

### In Commits
```
feat: add retry logic to payment processing

WHY: 3% of payments were failing due to temporary network issues. 
Retry with exponential backoff recovers 90% of these.
```

## WHY-Driven Code Review Checklist

When reviewing code, ask:

1. **Is the WHY clear?**
   - Can I understand why this code exists?
   - Are the decisions self-documenting?

2. **Is the WHY valid?**
   - Does this actually solve the stated problem?
   - Is there a simpler way to achieve the same WHY?

3. **Is the WHY complete?**
   - Are edge cases handled? (Why or why not?)
   - Are errors handled appropriately?

**Review comments should include WHY:**
```
❌ "Use a map instead of filter + find"
✅ "Use a map instead—O(1) lookup matters here because this runs 
    on every keystroke"
```

## WHY-Driven Debugging

When something breaks:

1. **WHY did it break?** (Root cause)
2. **WHY didn't we catch it?** (Testing gap)
3. **WHY might it happen again?** (Systemic issue)
4. **WHY is this the right fix?** (Solution validation)
