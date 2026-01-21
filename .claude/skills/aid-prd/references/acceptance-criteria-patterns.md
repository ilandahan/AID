# Acceptance Criteria Patterns Reference

Comprehensive patterns for writing clear, testable acceptance criteria.

## Core Principles

### What Makes Good Acceptance Criteria

```
┌─────────────────────────────────────────────────────────────────┐
│               ACCEPTANCE CRITERIA PRINCIPLES                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ✓ SPECIFIC                                                     │
│    No ambiguity about what's expected                           │
│    Bad:  "System should respond quickly"                        │
│    Good: "API responds within 500ms at P95"                     │
│                                                                  │
│  ✓ MEASURABLE                                                   │
│    Can objectively verify pass/fail                             │
│    Bad:  "User experience should be good"                       │
│    Good: "User completes flow in ≤3 clicks"                     │
│                                                                  │
│  ✓ TESTABLE                                                     │
│    QA can create test cases from criteria                       │
│    Bad:  "Must be mobile-friendly"                              │
│    Good: "Layout adapts at 320px, 768px, 1024px breakpoints"   │
│                                                                  │
│  ✓ INDEPENDENT                                                  │
│    Each criterion stands alone                                   │
│    Bad:  "If previous criterion passes, then..."                │
│    Good: "Given [context], when [action], then [result]"        │
│                                                                  │
│  ✓ COMPLETE                                                     │
│    Covers happy path, errors, and edge cases                    │
│    Bad:  Only happy path                                        │
│    Good: Success + failure + boundary conditions                │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Pattern Library

### 1. Happy Path Pattern

The successful scenario when everything works correctly.

```gherkin
Given [user is in valid starting state]
And [all prerequisites are met]
When [user performs the expected action]
Then [primary success outcome occurs]
And [secondary effects happen]
And [user sees confirmation]
```

**Example:**
```gherkin
Given I am a logged-in customer
And I have a verified payment method on file
When I click "Place Order" on the checkout page
Then my order is created with status "Confirmed"
And my payment method is charged
And I receive an order confirmation email
And I am redirected to the order confirmation page
```

---

### 2. Input Validation Pattern

Validating user inputs before processing.

```gherkin
Given [user is on input form]
When [user enters invalid data: specific case]
Then [specific validation error appears]
And [invalid field is highlighted]
And [form is not submitted]
And [other valid fields retain their values]
```

**Examples:**
```gherkin
# Empty required field
Given I am on the registration form
When I leave the email field empty
And I click "Register"
Then I see "Email is required" below the email field
And the email field has a red border
And the form is not submitted

# Invalid format
Given I am on the registration form
When I enter "notanemail" in the email field
And I click "Register"
Then I see "Please enter a valid email address"
And the form is not submitted

# Invalid length
Given I am on the registration form
When I enter a password with 5 characters
And I click "Register"
Then I see "Password must be at least 8 characters"
And the form is not submitted
```

---

### 3. Boundary Condition Pattern

Testing at the edges of acceptable input ranges.

```gherkin
# At minimum boundary
Given [minimum value condition]
When [action at boundary]
Then [expected minimum behavior]

# At maximum boundary
Given [maximum value condition]
When [action at boundary]
Then [expected maximum behavior]

# Just below minimum (error)
Given [below minimum condition]
When [action attempted]
Then [appropriate error]

# Just above maximum (error)
Given [above maximum condition]
When [action attempted]
Then [appropriate error]
```

**Examples:**
```gherkin
# At minimum (valid)
Given I am adjusting product quantity
When I set quantity to 1
Then the quantity is updated to 1
And the cart total is recalculated

# At maximum (valid)
Given I am adjusting product quantity
When I set quantity to 99 (maximum allowed)
Then the quantity is updated to 99
And the cart total is recalculated

# Below minimum (invalid)
Given I am adjusting product quantity
When I set quantity to 0
Then I see "Quantity must be at least 1"
And the quantity remains unchanged

# Above maximum (invalid)
Given I am adjusting product quantity
When I set quantity to 100
Then I see "Maximum quantity is 99"
And the quantity is set to 99
```

---

### 4. Permission/Authorization Pattern

Verifying access controls work correctly.

```gherkin
# Authorized access
Given I am logged in as [role with permission]
When I [attempt authorized action]
Then [action succeeds]

# Unauthorized access
Given I am logged in as [role without permission]
When I [attempt restricted action]
Then I see [access denied message]
And [action is not performed]
And [attempt is logged]

# Unauthenticated access
Given I am not logged in
When I [attempt to access protected resource]
Then I am redirected to the login page
And I see "Please log in to continue"
And the return URL is preserved
```

**Examples:**
```gherkin
# Admin can delete
Given I am logged in as an Admin
When I click "Delete" on a user account
Then the user account is deleted
And I see "User deleted successfully"

# Regular user cannot delete
Given I am logged in as a regular User
When I attempt to access the user deletion endpoint
Then I receive a 403 Forbidden response
And the user account is not deleted
And the attempt is logged in the audit trail

# Not logged in
Given I am not logged in
When I navigate to /admin/users
Then I am redirected to /login
And I see "Please log in to access this page"
And after login I am redirected to /admin/users
```

---

### 5. State Transition Pattern

When objects move through defined states.

```gherkin
Given [object is in state A]
And [transition conditions are met]
When [transition trigger occurs]
Then [object moves to state B]
And [state-specific behaviors change]
And [relevant parties are notified]
```

**Examples:**
```gherkin
# Order state transitions
Given an order is in "Pending" state
And payment has been verified
When the warehouse confirms item availability
Then the order moves to "Processing" state
And the customer receives a "Order being prepared" email
And the order appears in the fulfillment queue

Given an order is in "Processing" state
When the order is handed to the carrier
Then the order moves to "Shipped" state
And the tracking number is recorded
And the customer receives a shipping notification with tracking link

Given an order is in "Shipped" state
And carrier confirms delivery
When delivery confirmation is received
Then the order moves to "Delivered" state
And the customer can now leave a review
And the refund window begins (30 days)
```

---

### 6. Error Handling Pattern

System errors and recovery.

```gherkin
# System error
Given [normal operating conditions]
When [action triggers system error]
Then [user-friendly error message appears]
And [technical details are logged]
And [user can retry or recover]
And [no data is corrupted]

# External service failure
Given [dependency on external service]
When [external service is unavailable]
Then [graceful degradation occurs]
And [user is informed appropriately]
And [retry mechanism activates if applicable]
```

**Examples:**
```gherkin
# Database error
Given I am submitting a new post
When a database connection error occurs
Then I see "Unable to save. Please try again."
And my draft is preserved in local storage
And the error is logged with full stack trace
And I can click "Retry" to attempt again

# Payment gateway timeout
Given I am completing checkout
When the payment gateway times out
Then I see "Payment processing is taking longer than expected"
And my cart is not cleared
And no duplicate charges are created
And I receive an email if payment eventually succeeds

# External API failure
Given the product page needs to display reviews from ReviewAPI
When ReviewAPI is unavailable
Then the product page still loads
And the reviews section shows "Reviews temporarily unavailable"
And the rest of the page functions normally
```

---

### 7. Concurrent Operation Pattern

Multiple users or processes interacting.

```gherkin
Given [initial state]
When [user A performs action]
And [user B performs conflicting action simultaneously]
Then [conflict is detected]
And [appropriate resolution occurs]
And [both users are informed]
And [data integrity is maintained]
```

**Examples:**
```gherkin
# Optimistic locking
Given User A and User B are both editing the same document
And User A saves their changes first
When User B attempts to save their changes
Then User B sees "Document was modified by another user"
And User B's changes are not lost
And User B can choose to merge, overwrite, or discard

# Inventory race condition
Given only 1 item remains in stock
And User A and User B both have the item in their cart
When User A completes checkout first
Then the item is marked out of stock
And when User B attempts checkout
Then User B sees "Item is no longer available"
And User B's cart is updated
And User B is offered similar alternatives
```

---

### 8. Async Operation Pattern

For operations that don't complete immediately.

```gherkin
Given [operation requires async processing]
When [user initiates operation]
Then [immediate acknowledgment is shown]
And [progress indicator appears]
And [user can continue using the app]
And [notification sent when complete]
```

**Examples:**
```gherkin
# File upload
Given I am uploading a large file
When I select a 500MB file and click Upload
Then I see "Upload in progress: 0%"
And a progress bar shows upload percentage
And I can navigate away without canceling the upload
And I receive a notification when upload completes
And if upload fails, I see the error and can retry

# Report generation
Given I request a large data export
When I click "Generate Report"
Then I see "Report generation started"
And I can close the modal and continue working
And the report appears in "My Reports" when ready
And I receive an email with download link
And the report expires after 7 days
```

---

### 9. Search & Filter Pattern

For data retrieval with criteria.

```gherkin
Given [data set exists]
When [search/filter is applied]
Then [matching results are displayed]
And [non-matching items are hidden]
And [result count is shown]
And [applied filters are visible]
And [user can clear filters]
```

**Examples:**
```gherkin
# Search
Given there are 100 products in the catalog
When I search for "blue shirt"
Then only products matching "blue shirt" are displayed
And I see "Showing 8 results for 'blue shirt'"
And my search term appears in the search box
And I can click "Clear" to see all products

# Combined filters
Given I am viewing all products
When I filter by Category: "Clothing"
And I filter by Price: "$50-$100"
And I filter by Size: "Medium"
Then only products matching all criteria are shown
And I see active filter badges for each filter
And I can remove individual filters
And result count updates with each filter change

# No results
Given I am searching products
When my search returns no matches
Then I see "No products found"
And I see suggestions: "Try different keywords" or "Clear filters"
And I can easily modify my search
```

---

### 10. Pagination Pattern

For large data sets.

```gherkin
Given [result set is larger than page size]
When [page is loaded/changed]
Then [correct page of results appears]
And [pagination controls are accurate]
And [current position is indicated]
And [page size preference is respected]
```

**Examples:**
```gherkin
# Initial load
Given there are 150 orders in my history
When I view "My Orders"
Then I see the first 20 orders (most recent first)
And I see "Showing 1-20 of 150"
And pagination shows pages 1, 2, 3, ..., 8

# Navigate to page
Given I am on page 1 of my orders
When I click page 3
Then I see orders 41-60
And page 3 is highlighted in pagination
And I see "Showing 41-60 of 150"
And the page scrolls to top

# Last page
Given I am viewing orders
When I click the last page
Then I see orders 141-150 (10 results)
And "Next" button is disabled
And I see "Showing 141-150 of 150"
```

---

## Coverage Checklist

For each user story, ensure criteria cover:

```markdown
## Acceptance Criteria Coverage

### Happy Path
- [ ] Primary success scenario
- [ ] All expected outcomes stated
- [ ] User feedback/confirmation included

### Input Validation
- [ ] Required fields
- [ ] Format validation
- [ ] Length limits
- [ ] Type validation

### Boundaries
- [ ] Minimum values
- [ ] Maximum values
- [ ] Edge cases

### Permissions
- [ ] Authorized users
- [ ] Unauthorized attempts
- [ ] Unauthenticated attempts

### Error Handling
- [ ] User errors
- [ ] System errors
- [ ] External service failures

### State Management
- [ ] Valid state transitions
- [ ] Invalid transition attempts
- [ ] State-dependent behavior

### Special Cases
- [ ] Empty states
- [ ] First-time user experience
- [ ] Concurrent operations
- [ ] Async operations
```

---

## Anti-Patterns to Avoid

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| "Should be fast" | Unmeasurable | "Loads in < 2 seconds" |
| "Easy to use" | Subjective | "Completes in ≤ 3 steps" |
| "Works on mobile" | Vague | "Displays correctly at 320px width" |
| "Handles errors gracefully" | Undefined | Specific error scenarios |
| "Users can..." | Missing conditions | "Given X, When Y, Then Z" |
| Implementation details | Wrong abstraction | Focus on outcomes |
| Missing error cases | Incomplete | Add failure scenarios |
| "Works like competitor X" | External reference | Define explicit behavior |
