# User Stories Guide Reference

Complete guide to writing effective user stories with acceptance criteria.

## User Story Format

### Standard Template

```
As a [role/persona]
I want [capability/action]
So that [benefit/value]
```

### Extended Template with Traceability

```markdown
### US-XXX: [Descriptive Title]
**Research Backing**: [PROJECT]-A-XXX, [PROJECT]-B-XXX
<!-- If no research: ASSUMPTION - [brief rationale] -->

**As a** [specific role or persona name]
**I want** [specific capability or action]
**So that** [measurable benefit or value]

**Acceptance Criteria:**
- [ ] Given [context], when [action], then [outcome]
- [ ] Given [context], when [action], then [outcome]

**Priority**: Must Have / Should Have / Could Have / Won't Have
**Complexity**: S / M / L / XL
```

---

## INVEST Criteria

Every user story should be:

```
┌─────────────────────────────────────────────────────────────────┐
│                    INVEST CRITERIA                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  I - INDEPENDENT                                                │
│      Can be developed without depending on other stories         │
│      ✗ Bad: "As a user, I want part 1 of the checkout"         │
│      ✓ Good: "As a user, I want to add items to my cart"       │
│                                                                  │
│  N - NEGOTIABLE                                                 │
│      Details can be discussed; not a rigid contract             │
│      ✗ Bad: "Must use React with Redux and Material UI"        │
│      ✓ Good: "User can filter search results"                  │
│                                                                  │
│  V - VALUABLE                                                   │
│      Delivers value to the user or business                     │
│      ✗ Bad: "Refactor the database layer"                      │
│      ✓ Good: "User can see order status in real-time"          │
│                                                                  │
│  E - ESTIMABLE                                                  │
│      Team can estimate the effort required                       │
│      ✗ Bad: "Improve the system performance"                   │
│      ✓ Good: "Page loads in under 2 seconds"                   │
│                                                                  │
│  S - SMALL                                                      │
│      Completable in one sprint/iteration                        │
│      ✗ Bad: "User can manage their entire profile"             │
│      ✓ Good: "User can update their email address"             │
│                                                                  │
│  T - TESTABLE                                                   │
│      Clear criteria for when it's "done"                        │
│      ✗ Bad: "System should be user-friendly"                   │
│      ✓ Good: "User completes checkout in under 3 steps"        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### INVEST Validation Checklist

```markdown
## Story: US-XXX

| Criterion | Pass | Notes |
|-----------|------|-------|
| Independent | ☐ | [Can be built alone?] |
| Negotiable | ☐ | [Room for discussion?] |
| Valuable | ☐ | [Clear user/business value?] |
| Estimable | ☐ | [Team can estimate?] |
| Small | ☐ | [Fits in one sprint?] |
| Testable | ☐ | [Clear done criteria?] |
```

---

## Acceptance Criteria Formats

### Given-When-Then (Gherkin)

Best for: Behavior-driven stories with clear scenarios

```gherkin
Given [precondition/context]
When [action performed]
Then [expected outcome]
And [additional outcome]
```

**Example:**
```gherkin
Given I am a logged-in customer
And I have items in my cart
When I click "Proceed to Checkout"
Then I am taken to the checkout page
And my cart items are displayed
And the total price is calculated correctly
```

### Checklist Format

Best for: Simpler acceptance with multiple conditions

```markdown
**Acceptance Criteria:**
- [ ] User can see a list of their orders
- [ ] Orders are sorted by date (newest first)
- [ ] Each order shows: order ID, date, status, total
- [ ] Clicking an order shows order details
- [ ] Empty state shown when no orders exist
```

### Rule-Based Format

Best for: Stories with complex business rules

```markdown
**Business Rules:**
1. Password must be at least 8 characters
2. Password must contain at least one uppercase letter
3. Password must contain at least one number
4. Password cannot match the last 5 passwords
5. Account locks after 5 failed attempts
```

---

## Writing Good Acceptance Criteria

### Criteria Characteristics

| Good Criteria | Bad Criteria |
|---------------|--------------|
| Specific and measurable | Vague and subjective |
| Binary (pass/fail) | Open to interpretation |
| Independent of implementation | Prescribes how to build |
| Covers edge cases | Only happy path |
| Includes error scenarios | Ignores failures |

### Common Patterns

**Happy Path**
```gherkin
Given [normal conditions]
When [expected action]
Then [successful outcome]
```

**Error Case**
```gherkin
Given [error condition]
When [action attempted]
Then [appropriate error message]
And [system remains stable]
```

**Boundary Condition**
```gherkin
Given [edge case condition]
When [action at boundary]
Then [correct boundary behavior]
```

**Permission Check**
```gherkin
Given [user role]
When [attempting restricted action]
Then [access granted/denied appropriately]
```

---

## User Story Examples

### Example 1: E-commerce Cart

```markdown
### US-101: Add Product to Cart
**Research Backing**: AUTH-A-INT-003, AUTH-B-IDEA-012

**As a** shopper
**I want** to add products to my shopping cart
**So that** I can purchase multiple items in one transaction

**Acceptance Criteria:**
- [ ] Given I am viewing a product page
      When I click "Add to Cart"
      Then the product is added to my cart
      And the cart icon updates to show the new count

- [ ] Given I am viewing a product with variants (size, color)
      When I click "Add to Cart" without selecting a variant
      Then I see an error message "Please select [variant type]"

- [ ] Given the product is out of stock
      When I view the product page
      Then the "Add to Cart" button is disabled
      And I see "Out of Stock" message

- [ ] Given I have the same product in my cart
      When I add it again
      Then the quantity increases by 1
      And I see a confirmation message

**Priority**: Must Have
**Complexity**: M
```

### Example 2: User Authentication

```markdown
### US-102: User Login
**Research Backing**: AUTH-A-JTBD-001, AUTH-C-OPP-002

**As a** registered user
**I want** to log into my account
**So that** I can access my personalized content and history

**Acceptance Criteria:**
- [ ] Given I am on the login page
      When I enter valid email and password
      And click "Login"
      Then I am redirected to my dashboard
      And I see a welcome message with my name

- [ ] Given I enter an invalid email format
      When I attempt to submit
      Then I see "Please enter a valid email address"
      And the form is not submitted

- [ ] Given I enter incorrect credentials
      When I click "Login"
      Then I see "Invalid email or password"
      And password field is cleared
      And login attempt is logged

- [ ] Given I have failed login 5 times
      When I attempt another login
      Then my account is locked for 15 minutes
      And I see "Account locked. Try again in 15 minutes."
      And I receive an email notification

- [ ] Given I am already logged in
      When I navigate to the login page
      Then I am redirected to my dashboard

**Priority**: Must Have
**Complexity**: L
```

### Example 3: With Assumption

```markdown
### US-103: Social Login
**Research Backing**: ASSUMPTION - User interviews indicated preference (informal)

**As a** new user
**I want** to sign up using my Google account
**So that** I can start using the app without creating a new password

**Acceptance Criteria:**
- [ ] Given I am on the signup page
      When I click "Continue with Google"
      Then Google OAuth popup appears
      And I can authorize the application

- [ ] Given I authorize with Google
      When OAuth completes successfully
      Then my account is created with Google profile info
      And I am logged in automatically
      And I am redirected to onboarding

- [ ] Given I already have an account with same email
      When I try Google login
      Then accounts are linked
      And I am logged into existing account

**Priority**: Should Have
**Complexity**: L

**Assumption Risk**: Medium - Based on informal feedback, not formal research
**Validation Plan**: A/B test signup with/without social login
```

---

## Story Sizing Guidelines

### Complexity Estimation

| Size | Description | Typical Duration | Story Points |
|------|-------------|------------------|--------------|
| XS | Trivial change, no unknowns | < 2 hours | 1 |
| S | Simple, well-understood | 2-4 hours | 2 |
| M | Moderate complexity | 1-2 days | 3-5 |
| L | Complex, some unknowns | 3-5 days | 8 |
| XL | Very complex, needs breakdown | > 1 week | 13+ |

### When to Split Stories

Split when:
- Story is > L size
- Story has multiple acceptance criteria groups
- Story covers multiple user types
- Story spans multiple system areas

**Splitting Patterns:**

1. **By Workflow Step**
   - Original: "User can complete checkout"
   - Split: "User can enter shipping info" + "User can enter payment" + "User can confirm order"

2. **By Data Variation**
   - Original: "User can export reports"
   - Split: "Export to PDF" + "Export to CSV" + "Export to Excel"

3. **By User Role**
   - Original: "Users can manage team members"
   - Split: "Admin can add members" + "Admin can remove members" + "Members can view team"

4. **By Business Rule**
   - Original: "User can apply discount codes"
   - Split: "Percentage discount codes" + "Fixed amount codes" + "Free shipping codes"

---

## Story Mapping

### User Story Map Structure

```
                         BACKBONE (User Activities)
┌─────────────┬─────────────┬─────────────┬─────────────┬─────────────┐
│   Browse    │    Cart     │  Checkout   │   Account   │   Orders    │
└─────────────┴─────────────┴─────────────┴─────────────┴─────────────┘
      │             │             │             │             │
      ▼             ▼             ▼             ▼             ▼
┌─────────────────────────────────────────────────────────────────────┐
│ MVP (Release 1)                                                      │
├─────────────┬─────────────┬─────────────┬─────────────┬─────────────┤
│ View        │ Add to      │ Enter       │ Register    │ View order  │
│ products    │ cart        │ shipping    │             │ history     │
├─────────────┼─────────────┼─────────────┼─────────────┼─────────────┤
│ Search      │ Update qty  │ Enter       │ Login       │ Track       │
│ products    │             │ payment     │             │ shipment    │
└─────────────┴─────────────┴─────────────┴─────────────┴─────────────┘
┌─────────────────────────────────────────────────────────────────────┐
│ Release 2                                                            │
├─────────────┬─────────────┬─────────────┬─────────────┬─────────────┤
│ Filter by   │ Save for    │ Apply       │ Social      │ Cancel      │
│ category    │ later       │ coupons     │ login       │ order       │
├─────────────┼─────────────┼─────────────┼─────────────┼─────────────┤
│ Product     │ Wishlist    │ Gift wrap   │ Password    │ Return      │
│ reviews     │             │             │ reset       │ items       │
└─────────────┴─────────────┴─────────────┴─────────────┴─────────────┘
```

---

## Research-Backed Story Template

```markdown
### US-XXX: [Title]

#### Research Foundation
| ID | Type | Finding Summary |
|----|------|-----------------|
| [PROJECT]-A-INT-XXX | Interview | [Key quote or insight] |
| [PROJECT]-C-OPP-XXX | Opportunity | [Opportunity statement] |

#### User Story
**As a** [persona from research]
**I want** [capability derived from JTBD/pain points]
**So that** [benefit aligned with opportunity]

#### Acceptance Criteria
Based on research findings:

1. **From [PROJECT]-A-INT-XXX:**
   - [ ] Given... When... Then...

2. **From [PROJECT]-A-COMP-XXX:**
   - [ ] Given... When... Then...

3. **Edge cases identified in [PROJECT]-B-ROOT-XXX:**
   - [ ] Given... When... Then...

#### Traceability
- **Research IDs**: [list all]
- **Opportunity**: [PROJECT]-C-OPP-XXX
- **Assumptions**: [ASSUME-XXX if any]

#### Definition of Done
- [ ] All acceptance criteria pass
- [ ] Code reviewed and merged
- [ ] Unit tests written (>80% coverage)
- [ ] Integration tests pass
- [ ] Documentation updated
- [ ] Stakeholder demo completed
```

---

## Quick Reference

### Story Checklist

```
Before submission:
☐ Title is clear and descriptive
☐ Role is specific (not "user")
☐ Want describes action, not implementation
☐ Benefit explains the "why"
☐ Research IDs linked OR assumption flagged
☐ Acceptance criteria are testable
☐ Error cases are covered
☐ Size is S, M, or L (not XL)
☐ INVEST criteria validated
```

### Acceptance Criteria Checklist

```
For each criterion:
☐ Written in Given-When-Then or checklist format
☐ Specific and measurable
☐ Binary pass/fail
☐ No implementation details
☐ Covers happy path AND errors
☐ Testable by QA
```
