# BDD Gherkin Guide

Comprehensive guide for writing Behavior-Driven Development tests using Gherkin syntax.

---

## Gherkin Keywords

| Keyword | Purpose | Example |
|---------|---------|---------|
| `Feature` | Describes the feature being tested | `Feature: User Registration` |
| `Scenario` | A single test case | `Scenario: Successful registration` |
| `Given` | Precondition/setup | `Given I am on the registration page` |
| `When` | Action being taken | `When I submit the form` |
| `Then` | Expected outcome | `Then I should see a welcome message` |
| `And` | Additional step (same type as previous) | `And I should receive a confirmation email` |
| `But` | Negative additional step | `But I should not see the registration form` |
| `Background` | Steps run before each scenario | Common setup |
| `Scenario Outline` | Data-driven scenario | Multiple examples |
| `Examples` | Data table for Scenario Outline | Test data |

---

## Basic Structure

```gherkin
Feature: Short feature description
  As a [role]
  I want [capability]
  So that [benefit]

  Background:
    Given some common precondition
    And another common setup step

  Scenario: Descriptive scenario name
    Given some precondition
    When I take some action
    Then I should see some outcome
    And another expected result

  Scenario: Another scenario
    Given different precondition
    When I take different action
    Then I should see different outcome
```

---

## Feature Examples

### Authentication Feature

```gherkin
Feature: User Authentication
  As a registered user
  I want to log in to my account
  So that I can access my personal dashboard

  Background:
    Given I am on the login page
    And the system is available

  @smoke @critical
  Scenario: Successful login with valid credentials
    Given I have a registered account with email "user@example.com"
    When I enter email "user@example.com"
    And I enter password "SecurePass123!"
    And I click the "Log In" button
    Then I should be redirected to the dashboard
    And I should see "Welcome back" message
    And my last login time should be updated

  @security
  Scenario: Failed login with incorrect password
    Given I have a registered account with email "user@example.com"
    When I enter email "user@example.com"
    And I enter password "WrongPassword"
    And I click the "Log In" button
    Then I should see error message "Invalid email or password"
    And I should remain on the login page
    But I should not see any password hints

  @security @rate-limiting
  Scenario: Account lockout after failed attempts
    Given I have a registered account with email "user@example.com"
    When I enter incorrect password 5 times
    Then I should see error message "Account locked"
    And I should receive a password reset email
    And I should not be able to attempt login for 15 minutes
```

### E-commerce Feature

```gherkin
Feature: Shopping Cart
  As a shopper
  I want to manage items in my cart
  So that I can purchase products I want

  Background:
    Given I am logged in as a customer
    And the product catalog is available

  @happy-path
  Scenario: Add single item to empty cart
    Given my cart is empty
    When I view product "Blue T-Shirt"
    And I select size "Medium"
    And I click "Add to Cart"
    Then my cart should contain 1 item
    And the cart total should be "$29.99"
    And I should see confirmation "Item added to cart"

  @edge-case
  Scenario: Add item that exceeds available stock
    Given product "Limited Edition Watch" has 2 items in stock
    When I try to add 5 of "Limited Edition Watch" to cart
    Then I should see error "Only 2 items available"
    And my cart should contain 2 items
    And I should see "Maximum quantity added"

  @business-rule
  Scenario: Apply percentage discount code
    Given my cart contains items totaling "$100.00"
    When I apply discount code "SAVE20"
    Then the discount "-$20.00" should be applied
    And the cart total should be "$80.00"
    And the discount code should be visible in cart summary
```

---

## Scenario Outline (Data-Driven Testing)

### Basic Example

```gherkin
Scenario Outline: Email validation
  Given I am on the registration page
  When I enter email "<email>"
  And I submit the form
  Then I should see "<message>"

  Examples:
    | email                | message                    |
    | valid@example.com    | Registration successful    |
    | invalid              | Please enter a valid email |
    | user@               | Please enter a valid email |
    |                      | Email is required          |
    | a@b.co               | Registration successful    |
```

### Complex Example with Multiple Columns

```gherkin
Scenario Outline: Product search with filters
  Given I am on the product catalog page
  When I search for "<query>"
  And I filter by category "<category>"
  And I filter by price range "<min_price>" to "<max_price>"
  And I sort by "<sort_option>"
  Then I should see <result_count> products
  And the first product should be "<first_product>"

  Examples: Electronics under $500
    | query    | category    | min_price | max_price | sort_option  | result_count | first_product    |
    | laptop   | Electronics | 0         | 500       | price_low    | 12           | Budget Laptop    |
    | laptop   | Electronics | 0         | 500       | price_high   | 12           | Pro Laptop 499   |
    | laptop   | Electronics | 500       | 1000      | rating       | 8            | Top Rated Laptop |

  Examples: No results scenarios
    | query      | category | min_price | max_price | sort_option | result_count | first_product |
    | xyznotfound| Any      | 0         | 10000     | relevance   | 0            | N/A           |
```

---

## Tags

### Tag Categories

```gherkin
# Priority/Importance
@critical        # Must pass for release
@high-priority   # Important but not blocking
@low-priority    # Nice to have

# Test Type
@smoke           # Quick sanity check
@regression      # Full regression suite
@e2e             # End-to-end flow
@integration     # Integration test
@unit            # Unit-level BDD

# Status
@wip             # Work in progress
@pending         # Not yet implemented
@manual          # Requires manual verification
@flaky           # Known flaky, needs fixing

# Feature Area
@authentication  # Auth-related
@checkout        # Checkout flow
@search          # Search functionality

# Non-functional
@performance     # Performance test
@security        # Security test
@accessibility   # A11y test

# Environment
@staging-only    # Only run in staging
@prod-safe       # Safe to run in production
```

### Running Tagged Tests

```bash
# Run only smoke tests
npx cucumber-js --tags "@smoke"

# Run critical but not WIP
npx cucumber-js --tags "@critical and not @wip"

# Run authentication OR checkout tests
npx cucumber-js --tags "@authentication or @checkout"

# Complex expression
npx cucumber-js --tags "(@smoke or @critical) and not @flaky"
```

---

## Step Definition Patterns

### TypeScript/JavaScript (Cucumber.js)

```typescript
import { Given, When, Then } from '@cucumber/cucumber';
import { expect } from '@playwright/test';

// Simple step
Given('I am on the login page', async function() {
  await this.page.goto('/login');
});

// Step with string parameter
When('I enter email {string}', async function(email: string) {
  await this.page.fill('#email', email);
});

// Step with number parameter
Then('I should see {int} products', async function(count: number) {
  const products = await this.page.locator('.product').count();
  expect(products).toBe(count);
});

// Step with data table
Given('the following users exist:', async function(dataTable) {
  const users = dataTable.hashes();
  for (const user of users) {
    await this.createUser(user.email, user.password, user.role);
  }
});

// Step with doc string
When('I enter the following description:', async function(docString: string) {
  await this.page.fill('#description', docString);
});

// Reusable step with regex
When(/^I wait (\d+) seconds?$/, async function(seconds: number) {
  await this.page.waitForTimeout(seconds * 1000);
});
```

### Data Tables in Steps

```gherkin
Scenario: Create multiple users
  Given the following users exist:
    | email              | password    | role    |
    | admin@example.com  | admin123    | admin   |
    | user@example.com   | user123     | user    |
    | guest@example.com  | guest123    | guest   |
  When I view the user management page
  Then I should see 3 users listed
```

### Doc Strings for Long Text

```gherkin
Scenario: Submit feedback with detailed description
  Given I am on the feedback form
  When I enter the following feedback:
    """
    I really enjoyed using this product!
    
    The interface is intuitive and the features
    are exactly what I needed. 
    
    One suggestion: add dark mode support.
    """
  And I click "Submit"
  Then I should see "Thank you for your feedback"
```

---

## Common Patterns

### Page Object Integration

```typescript
// Step using page object
Given('I am logged in as {string}', async function(userType: string) {
  const loginPage = new LoginPage(this.page);
  const credentials = this.testData.getUser(userType);
  await loginPage.login(credentials.email, credentials.password);
});
```

### Shared State Between Steps

```typescript
// World object for shared state
import { setWorldConstructor, World } from '@cucumber/cucumber';

class CustomWorld extends World {
  page: Page;
  testData: Map<string, any> = new Map();
  
  async saveForLater(key: string, value: any) {
    this.testData.set(key, value);
  }
  
  getLater(key: string) {
    return this.testData.get(key);
  }
}

setWorldConstructor(CustomWorld);

// Usage in steps
When('I create an order', async function() {
  const orderId = await this.createOrder();
  this.saveForLater('orderId', orderId);
});

Then('the order should be confirmed', async function() {
  const orderId = this.getLater('orderId');
  const status = await this.getOrderStatus(orderId);
  expect(status).toBe('confirmed');
});
```

---

## Anti-Patterns and Fixes

### ❌ Too Technical

```gherkin
# BAD: Implementation details
Scenario: API returns correct response
  Given I send POST to "/api/users" with body {"name": "John"}
  When the server processes the request
  Then the response status should be 201
  And the response body should contain "id"
```

```gherkin
# GOOD: Business language
Scenario: Create new user account
  Given I am on the registration page
  When I register with name "John"
  Then my account should be created successfully
  And I should receive a welcome email
```

### ❌ Too Many Steps

```gherkin
# BAD: Too detailed
Scenario: Complete purchase
  Given I am on the home page
  And I click the search box
  And I type "laptop"
  And I press Enter
  And I wait for results
  And I click the first product
  And I click "Add to Cart"
  And I click the cart icon
  And I click "Checkout"
  And I enter shipping address
  And I enter payment details
  And I click "Place Order"
  Then I should see confirmation
```

```gherkin
# GOOD: Abstracted steps
Scenario: Complete purchase
  Given I have "laptop" in my cart
  When I complete checkout with valid payment
  Then I should see order confirmation
```

### ❌ UI Implementation Details

```gherkin
# BAD: Coupled to UI
Scenario: Login
  When I click on element "#login-btn"
  And I fill input[name="email"] with "user@test.com"
  And I fill input[name="password"] with "pass123"
  And I click button.submit
```

```gherkin
# GOOD: Behavior focused
Scenario: Login
  When I log in with email "user@test.com" and password "pass123"
```

### ❌ Dependent Scenarios

```gherkin
# BAD: Scenarios depend on each other
Scenario: Create user
  When I create user "john@test.com"
  Then user should exist

Scenario: Login as created user  # Depends on previous scenario!
  When I login as "john@test.com"
  Then I should see dashboard
```

```gherkin
# GOOD: Independent scenarios
Scenario: Login with valid credentials
  Given user "john@test.com" exists
  When I login as "john@test.com"
  Then I should see dashboard
```

---

## Project Structure

```
features/
├── support/
│   ├── world.ts           # Custom World class
│   ├── hooks.ts           # Before/After hooks
│   └── helpers.ts         # Shared utilities
├── step_definitions/
│   ├── common.steps.ts    # Shared steps
│   ├── auth.steps.ts      # Authentication steps
│   ├── cart.steps.ts      # Shopping cart steps
│   └── checkout.steps.ts  # Checkout steps
├── authentication/
│   ├── login.feature
│   ├── logout.feature
│   └── password-reset.feature
├── shopping/
│   ├── cart.feature
│   ├── checkout.feature
│   └── payment.feature
└── cucumber.js            # Configuration
```

### Cucumber Configuration

```javascript
// cucumber.js
module.exports = {
  default: {
    requireModule: ['ts-node/register'],
    require: ['features/support/**/*.ts', 'features/step_definitions/**/*.ts'],
    format: ['progress', 'html:reports/cucumber-report.html'],
    formatOptions: { snippetInterface: 'async-await' },
    publishQuiet: true,
  },
  smoke: {
    tags: '@smoke',
  },
  ci: {
    tags: 'not @wip and not @manual',
    parallel: 4,
  },
};
```

---

## Quick Reference

### Good Scenario Checklist

```
□ Title describes the behavior being tested
□ Written in business language
□ 5-8 steps maximum
□ Has Given (context), When (action), Then (outcome)
□ Independent from other scenarios
□ Uses Background for common setup
□ Has appropriate tags
□ Can be understood by non-technical stakeholders
```

### Gherkin Best Practices

| Do | Don't |
|----|-------|
| Use business language | Use technical terms |
| Focus on behavior | Focus on implementation |
| Keep scenarios independent | Create dependent scenarios |
| Use Background for common setup | Repeat setup in each scenario |
| Use Scenario Outline for data variations | Duplicate scenarios |
| Tag for organization | Leave scenarios untagged |
| 5-8 steps per scenario | 15+ steps per scenario |
