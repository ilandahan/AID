---
name: cucumber-bdd
description: Extended Cucumber BDD guide with advanced patterns
---

# Cucumber BDD - Extended Guide

Advanced patterns for production-ready Cucumber implementations.

---

## Data Tables

### Horizontal Tables (List of Objects)

```gherkin
Scenario: Create multiple users
  Given the following users exist:
    | email              | role    | active |
    | alice@example.com  | admin   | true   |
    | bob@example.com    | user    | true   |
    | carol@example.com  | viewer  | false  |
```

```typescript
Given('the following users exist:', async function(dataTable) {
  const users = dataTable.hashes(); // Array of objects
  for (const user of users) {
    await createUser({
      email: user.email,
      role: user.role,
      active: user.active === 'true'
    });
  }
});
```

### Vertical Tables (Key-Value Pairs)

```gherkin
Scenario: Update user profile
  When I update my profile with:
    | name     | Alice Smith      |
    | bio      | Software Engineer|
    | location | San Francisco    |
```

```typescript
When('I update my profile with:', async function(dataTable) {
  const data = dataTable.rowsHash(); // { name: '...', bio: '...', location: '...' }
  await this.updateProfile(data);
});
```

---

## Doc Strings

### Multi-line Text

```gherkin
Scenario: Create blog post
  When I create a post with content:
    """
    # Welcome to My Blog

    This is the first paragraph of my amazing blog post.

    ## Features
    - Easy to read
    - Well formatted
    """
```

### JSON Content

```gherkin
Scenario: Create product via API
  When I send a POST request to "/api/products" with:
    """json
    {
      "name": "Widget Pro",
      "price": 29.99,
      "categories": ["electronics", "gadgets"]
    }
    """
```

```typescript
When('I send a POST request to {string} with:', async function(endpoint, docString) {
  const body = JSON.parse(docString);
  this.response = await this.api.post(endpoint, body);
});
```

---

## Hooks

### Lifecycle Hooks

```typescript
// features/support/hooks.ts
import { Before, After, BeforeAll, AfterAll, BeforeStep, AfterStep } from '@cucumber/cucumber';

// Run once before all scenarios
BeforeAll(async function() {
  await startDatabase();
  await seedTestData();
});

// Run once after all scenarios
AfterAll(async function() {
  await cleanupDatabase();
  await stopDatabase();
});

// Run before each scenario
Before(async function(scenario) {
  console.log(`Starting: ${scenario.pickle.name}`);
  this.startTime = Date.now();
});

// Run after each scenario
After(async function(scenario) {
  const duration = Date.now() - this.startTime;
  console.log(`Finished: ${scenario.pickle.name} (${duration}ms)`);

  // Screenshot on failure
  if (scenario.result?.status === 'FAILED' && this.page) {
    const screenshot = await this.page.screenshot();
    this.attach(screenshot, 'image/png');
  }
});
```

### Tagged Hooks

```typescript
// Only run for scenarios tagged @auth
Before('@auth', async function() {
  this.authToken = await getAuthToken();
});

// Cleanup for @database scenarios
After('@database', async function() {
  await this.db.rollback();
});

// Skip setup for @fast scenarios
Before({ tags: 'not @fast' }, async function() {
  await this.seedFullTestData();
});
```

---

## Custom Parameter Types

```typescript
// features/support/parameter-types.ts
import { defineParameterType } from '@cucumber/cucumber';

// Match "admin", "user", or "viewer" roles
defineParameterType({
  name: 'role',
  regexp: /admin|user|viewer/,
  transformer: (s) => s
});

// Match currency amounts like "$19.99"
defineParameterType({
  name: 'currency',
  regexp: /\$[\d,]+(?:\.\d{2})?/,
  transformer: (s) => parseFloat(s.replace(/[$,]/g, ''))
});

// Match dates like "2024-01-15"
defineParameterType({
  name: 'date',
  regexp: /\d{4}-\d{2}-\d{2}/,
  transformer: (s) => new Date(s)
});
```

Usage:
```gherkin
Scenario: Price check
  Given I am a {role} user
  When I view a product priced at {currency}
  Then the discount should be applied after {date}
```

---

## Parallel Execution

### Configuration

```javascript
// cucumber.js
module.exports = {
  default: {
    parallel: 4,  // Run 4 scenarios in parallel
    require: ['features/support/**/*.ts'],
    // ...
  }
};
```

### Considerations for Parallel Execution

1. **No shared state between scenarios** - Use scenario-scoped World
2. **Database isolation** - Use transactions or separate test DBs
3. **Unique test data** - Generate unique IDs per scenario
4. **Resource cleanup** - Each scenario cleans its own data

```typescript
// features/support/world.ts
export class CustomWorld extends World {
  uniqueId: string;

  constructor(options: IWorldOptions) {
    super(options);
    this.uniqueId = `test-${Date.now()}-${Math.random().toString(36).slice(2)}`;
  }
}

// Use uniqueId for test data isolation
Given('I create a test user', async function() {
  this.testUser = await createUser({
    email: `user-${this.uniqueId}@test.com`
  });
});
```

---

## Debugging

### Rerun Failed Scenarios

```bash
# Save failures to a file
npx cucumber-js --format rerun:@rerun.txt

# Rerun only failed scenarios
npx cucumber-js @rerun.txt
```

### Step-by-Step Logging

```typescript
import { BeforeStep, AfterStep } from '@cucumber/cucumber';

BeforeStep(function({ pickleStep }) {
  console.log(`  → ${pickleStep.text}`);
});

AfterStep(function({ result, pickleStep }) {
  if (result.status === 'FAILED') {
    console.log(`  ✗ FAILED: ${pickleStep.text}`);
    console.log(`    Error: ${result.message}`);
  }
});
```

### Screenshots on Failure

```typescript
After(async function(scenario) {
  if (scenario.result?.status === 'FAILED') {
    // Take screenshot
    const screenshot = await this.page.screenshot({ fullPage: true });

    // Attach to report
    this.attach(screenshot, 'image/png');

    // Save to file
    const filename = `reports/failure-${Date.now()}.png`;
    await fs.writeFile(filename, screenshot);
  }
});
```

---

## Anti-Patterns to Avoid

### 1. Giant Scenarios (>10 Steps)

**Bad:**
```gherkin
Scenario: Complete checkout flow
  Given I am logged in
  And I have items in cart
  And I go to checkout
  And I enter shipping address
  And I select shipping method
  And I enter payment details
  And I review order
  And I confirm order
  And I receive confirmation
  And I get email
  And order appears in history
```

**Good:** Break into focused scenarios
```gherkin
@checkout
Scenario: Enter shipping information
  Given I am at checkout with items in cart
  When I enter valid shipping address
  Then shipping options should be displayed

@checkout
Scenario: Complete payment
  Given I have entered shipping information
  When I enter valid payment details
  And I confirm the order
  Then I should see order confirmation
```

### 2. UI Details in Gherkin

**Bad:**
```gherkin
When I click the blue button with id "submit-btn" at coordinates 100,200
```

**Good:**
```gherkin
When I submit the form
```

### 3. Implementation Details

**Bad:**
```gherkin
When the API returns HTTP 200 with JSON body containing "success": true
```

**Good:**
```gherkin
When the request succeeds
```

### 4. Shared State Between Scenarios

**Bad:** Using global variables that persist across scenarios

**Good:** Each scenario starts fresh with its own World instance

### 5. Hard-Coded Test Data

**Bad:**
```gherkin
Given user "john@example.com" with password "password123" exists
```

**Good:**
```gherkin
Given I have a registered user account
# Step implementation generates unique test user
```

---

## CI/CD Integration

### GitHub Actions

```yaml
# .github/workflows/cucumber.yml
name: Cucumber BDD Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Run Cucumber tests
        run: npm run cucumber -- --profile ci

      - name: Upload report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: cucumber-report
          path: reports/cucumber-report.html
```

### GitLab CI

```yaml
# .gitlab-ci.yml
cucumber:
  stage: test
  script:
    - npm ci
    - npm run cucumber -- --profile ci
  artifacts:
    when: always
    paths:
      - reports/
    reports:
      junit: reports/cucumber-junit.xml
```

---

## Allure Reporting (Optional)

For richer reports with history and trends:

```bash
npm install --save-dev allure-cucumberjs
```

```javascript
// cucumber.js
module.exports = {
  default: {
    format: [
      'allure-cucumberjs/reporter',
      'html:reports/cucumber-report.html'
    ],
    formatOptions: {
      resultsDir: 'allure-results'
    }
  }
};
```

Generate report:
```bash
npx allure generate allure-results --clean
npx allure open
```
