# Cucumber.js Complete Guide

The default and recommended runtime for Cucumber in AID projects.

---

## Prerequisites

- Node.js 18+ (required)
- TypeScript knowledge (recommended)
- npm, yarn, or pnpm

---

## Installation

```bash
# npm
npm install @cucumber/cucumber ts-node --save-dev

# yarn
yarn add @cucumber/cucumber ts-node --dev

# pnpm
pnpm add @cucumber/cucumber ts-node --save-dev
```

---

## Project Structure

```
project/
├── features/
│   ├── auth/
│   │   └── login.feature          # Gherkin feature files
│   ├── checkout/
│   │   └── cart.feature
│   ├── step-definitions/
│   │   ├── auth.steps.ts          # Step implementations
│   │   ├── checkout.steps.ts
│   │   └── common.steps.ts
│   └── support/
│       ├── world.ts               # Custom World class
│       ├── hooks.ts               # Before/After hooks
│       └── helpers/               # Utility functions
├── reports/
│   ├── cucumber-report.html       # Generated HTML report
│   └── cucumber-report.json       # Generated JSON report
├── cucumber.js                    # Cucumber configuration
├── tsconfig.json                  # TypeScript config
└── package.json
```

---

## Configuration (cucumber.js)

```javascript
/**
 * Cucumber.js Configuration
 *
 * Profiles:
 * - default: Development with progress bar + HTML report
 * - ci: CI/CD with JUnit XML, strict mode
 * - smoke: Quick validation (@smoke tags)
 * - critical: Release gate (@critical tags)
 */
module.exports = {
  default: {
    require: [
      'features/step-definitions/**/*.ts',
      'features/support/**/*.ts'
    ],
    requireModule: ['ts-node/register'],
    format: [
      'progress-bar',
      'html:reports/cucumber-report.html',
      'json:reports/cucumber-report.json'
    ],
    formatOptions: { snippetInterface: 'async-await' },
    publishQuiet: true
  },

  ci: {
    require: [
      'features/step-definitions/**/*.ts',
      'features/support/**/*.ts'
    ],
    requireModule: ['ts-node/register'],
    format: [
      'progress',
      'html:reports/cucumber-report.html',
      'junit:reports/cucumber-junit.xml'
    ],
    publishQuiet: true,
    strict: true,
    tags: 'not @skip and not @wip'
  },

  smoke: {
    require: ['features/**/*.ts'],
    requireModule: ['ts-node/register'],
    format: ['progress'],
    publishQuiet: true,
    tags: '@smoke'
  },

  critical: {
    require: ['features/**/*.ts'],
    requireModule: ['ts-node/register'],
    format: ['progress-bar', 'html:reports/critical-report.html'],
    publishQuiet: true,
    strict: true,
    tags: '@critical'
  }
};
```

---

## TypeScript Configuration

```json
// tsconfig.json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "lib": ["ES2020"],
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "outDir": "./dist",
    "rootDir": ".",
    "resolveJsonModule": true
  },
  "include": [
    "features/**/*.ts",
    "src/**/*.ts"
  ]
}
```

---

## World Setup

The World class provides shared context for all steps in a scenario.

```typescript
// features/support/world.ts
import { setWorldConstructor, World, IWorldOptions } from '@cucumber/cucumber';
import { Page, Browser, chromium } from 'playwright';
import { PrismaClient } from '@prisma/client';

export interface ICustomWorld {
  page?: Page;
  browser?: Browser;
  db: PrismaClient;
  testUser?: { id: string; email: string };
  response?: Response;
  token?: string;
}

export class CustomWorld extends World implements ICustomWorld {
  page?: Page;
  browser?: Browser;
  db: PrismaClient;
  testUser?: { id: string; email: string };
  response?: Response;
  token?: string;

  constructor(options: IWorldOptions) {
    super(options);
    this.db = new PrismaClient();
  }

  // Helper methods
  async login(email: string, password: string): Promise<string> {
    const response = await fetch('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password })
    });
    const { token } = await response.json();
    this.token = token;
    return token;
  }
}

setWorldConstructor(CustomWorld);
```

---

## Hooks (Setup/Teardown)

```typescript
// features/support/hooks.ts
import { Before, After, BeforeAll, AfterAll, BeforeStep, AfterStep } from '@cucumber/cucumber';
import { chromium, Browser } from 'playwright';

let browser: Browser;

// Run once before all scenarios
BeforeAll(async function() {
  browser = await chromium.launch({ headless: true });
});

// Run once after all scenarios
AfterAll(async function() {
  await browser?.close();
});

// Run before each scenario
Before(async function() {
  this.page = await browser.newPage();
});

// Run after each scenario
After(async function(scenario) {
  // Screenshot on failure
  if (scenario.result?.status === 'FAILED' && this.page) {
    const screenshot = await this.page.screenshot({ fullPage: true });
    this.attach(screenshot, 'image/png');
  }
  await this.page?.close();
});

// Tagged hooks
Before('@auth', async function() {
  this.token = await this.login('test@example.com', 'password');
});

After('@database', async function() {
  await this.db.$executeRaw`ROLLBACK`;
});
```

---

## Integration: Playwright (Browser Testing)

```typescript
// features/step-definitions/browser.steps.ts
import { Given, When, Then } from '@cucumber/cucumber';
import { expect } from '@playwright/test';

Given('I am on the {string} page', async function(path: string) {
  await this.page.goto(`http://localhost:3000${path}`);
});

When('I fill in {string} with {string}', async function(field: string, value: string) {
  await this.page.fill(`[name="${field}"]`, value);
});

When('I click {string}', async function(text: string) {
  await this.page.click(`text=${text}`);
});

Then('I should see {string}', async function(text: string) {
  const content = await this.page.textContent('body');
  expect(content).toContain(text);
});

Then('the URL should contain {string}', async function(path: string) {
  expect(this.page.url()).toContain(path);
});
```

---

## Integration: API Testing (Supertest)

```typescript
// features/step-definitions/api.steps.ts
import { Given, When, Then } from '@cucumber/cucumber';
import request from 'supertest';
import { app } from '../../src/app';

When('I send a GET request to {string}', async function(endpoint: string) {
  this.response = await request(app)
    .get(endpoint)
    .set('Authorization', `Bearer ${this.token || ''}`);
});

When('I send a POST request to {string} with:', async function(endpoint: string, body: string) {
  this.response = await request(app)
    .post(endpoint)
    .send(JSON.parse(body))
    .set('Authorization', `Bearer ${this.token || ''}`);
});

Then('the response status should be {int}', function(status: number) {
  expect(this.response.status).toBe(status);
});

Then('the response should contain:', function(expected: string) {
  const expectedObj = JSON.parse(expected);
  expect(this.response.body).toMatchObject(expectedObj);
});
```

---

## Integration: Database (Prisma)

```typescript
// features/step-definitions/database.steps.ts
import { Given, When, Then } from '@cucumber/cucumber';

Given('a user exists with email {string}', async function(email: string) {
  this.testUser = await this.db.user.create({
    data: {
      email,
      password: 'hashed_password',
      name: 'Test User'
    }
  });
});

Then('the user should be saved in the database', async function() {
  const user = await this.db.user.findUnique({
    where: { email: this.testUser.email }
  });
  expect(user).not.toBeNull();
});

// Cleanup hook for database scenarios
After('@database', async function() {
  await this.db.user.deleteMany({
    where: { email: { contains: '@test.com' } }
  });
});
```

---

## Running Tests

```bash
# Run all features
npm run cucumber

# Run with specific profile
npx cucumber-js --profile ci

# Run specific feature file
npx cucumber-js features/auth/login.feature

# Run specific scenario by line number
npx cucumber-js features/auth/login.feature:15

# Run with tags
npx cucumber-js --tags "@smoke"
npx cucumber-js --tags "@critical and @auth"
npx cucumber-js --tags "not @wip"

# Dry run (validate syntax only)
npm run cucumber:dry

# Generate HTML report
npm run test:bdd
```

---

## CI/CD: GitHub Actions

```yaml
# .github/workflows/cucumber.yml
name: Cucumber BDD Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Install Playwright browsers
        run: npx playwright install --with-deps chromium

      - name: Run Cucumber tests
        run: npm run cucumber -- --profile ci

      - name: Upload report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: cucumber-report
          path: reports/
```

---

## Troubleshooting

### Undefined Steps

```bash
# Find undefined steps
npm run cucumber:dry

# Output shows suggested snippets
Given('I am logged in', async function() {
  // Write code here
  return 'pending';
});
```

### TypeScript Errors

```bash
# Ensure ts-node is registered
npx cucumber-js --require-module ts-node/register

# Check tsconfig.json includes features folder
```

### Slow Tests

```javascript
// cucumber.js - increase timeout
module.exports = {
  default: {
    worldParameters: {
      timeout: 30000  // 30 seconds
    }
  }
};
```

---

## Resources

- [Cucumber.js Documentation](https://cucumber.io/docs/installation/javascript/)
- [Gherkin Reference](https://cucumber.io/docs/gherkin/reference/)
- [Playwright Documentation](https://playwright.dev/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
