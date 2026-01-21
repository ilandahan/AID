# GUI Testing with DevTools MCP

Complete guide for E2E and visual testing using Chrome DevTools MCP.

---

## DevTools MCP Overview

The Chrome DevTools MCP (Model Context Protocol) server provides browser automation capabilities for:
- Navigation and interaction
- Element inspection and manipulation
- Screenshot capture
- Performance monitoring
- Accessibility audits
- Network interception

---

## Setup

### MCP Configuration

```json
// .mcp/config.json
{
  "servers": {
    "devtools": {
      "command": "npx",
      "args": ["@anthropic/mcp-server-chrome-devtools"],
      "env": {
        "CHROME_PATH": "/path/to/chrome",
        "HEADLESS": "true"
      }
    }
  }
}
```

### Test Setup File

```typescript
// tests/setup/mcp.ts
import { MCPClient } from '@anthropic/mcp-client';

let mcpClient: MCPClient;

export async function setupMCP() {
  mcpClient = new MCPClient();
  await mcpClient.connect('devtools');
  return mcpClient;
}

export async function teardownMCP() {
  await mcpClient?.disconnect();
}

export { mcpClient as mcp };
```

### Jest Configuration

```javascript
// jest.e2e.config.js
module.exports = {
  ...require('./jest.config'),
  testMatch: ['**/*.e2e.test.ts'],
  setupFilesAfterEnv: ['./tests/setup/mcp.setup.ts'],
  testTimeout: 60000, // E2E tests need more time
  maxWorkers: 1 // Run sequentially for browser tests
};
```

---

## Core Operations

### Navigation

```typescript
// Navigate to URL
await mcp.devtools.navigate('https://example.com');

// Wait for page load
await mcp.devtools.waitForLoad();

// Get current URL
const url = await mcp.devtools.getCurrentUrl();

// Go back/forward
await mcp.devtools.goBack();
await mcp.devtools.goForward();

// Refresh
await mcp.devtools.refresh();
```

### Element Selection

```typescript
// Query single element
const element = await mcp.devtools.querySelector('.my-class');

// Query multiple elements
const elements = await mcp.devtools.querySelectorAll('li.item');

// Wait for element
await mcp.devtools.waitForSelector('#dynamic-content');

// Wait for element to disappear
await mcp.devtools.waitForSelectorToDisappear('.loading-spinner');

// Check if element exists
const exists = await mcp.devtools.exists('#optional-element');
```

### Interaction

```typescript
// Click element
await mcp.devtools.click('#submit-button');

// Double click
await mcp.devtools.doubleClick('.editable-text');

// Right click
await mcp.devtools.rightClick('.context-menu-trigger');

// Type text
await mcp.devtools.type('#email-input', 'user@example.com');

// Clear and type
await mcp.devtools.clear('#search-input');
await mcp.devtools.type('#search-input', 'new search');

// Press key
await mcp.devtools.press('Enter');
await mcp.devtools.press('Escape');

// Key combination
await mcp.devtools.press('Control+A');
await mcp.devtools.press('Meta+C'); // Cmd+C on Mac

// Hover
await mcp.devtools.hover('.tooltip-trigger');

// Focus
await mcp.devtools.focus('#input-field');

// Scroll
await mcp.devtools.scroll({ y: 500 });
await mcp.devtools.scrollIntoView('#footer');
```

### Form Handling

```typescript
// Fill form
await mcp.devtools.type('#name', 'John Doe');
await mcp.devtools.type('#email', 'john@example.com');

// Select dropdown
await mcp.devtools.select('#country', 'US');

// Check/uncheck checkbox
await mcp.devtools.check('#agree-terms');
await mcp.devtools.uncheck('#newsletter');

// Radio button
await mcp.devtools.click('input[name="plan"][value="premium"]');

// File upload
await mcp.devtools.uploadFile('#file-input', '/path/to/file.pdf');

// Submit form
await mcp.devtools.click('button[type="submit"]');
```

### Getting Content

```typescript
// Get text content
const text = await mcp.devtools.getText('.message');

// Get HTML
const html = await mcp.devtools.getHTML('.content');

// Get attribute
const href = await mcp.devtools.getAttribute('a.link', 'href');

// Get value (for inputs)
const value = await mcp.devtools.getValue('#email-input');

// Get computed style
const color = await mcp.devtools.getStyle('.button', 'background-color');

// Check visibility
const isVisible = await mcp.devtools.isVisible('.modal');

// Check enabled state
const isEnabled = await mcp.devtools.isEnabled('#submit-btn');
```

---

## Visual Testing

### Screenshots

```typescript
// Full page screenshot
const screenshot = await mcp.devtools.screenshot();

// Element screenshot
const elementShot = await mcp.devtools.screenshot({
  selector: '.card-component'
});

// Specific viewport
const mobileShot = await mcp.devtools.screenshot({
  viewport: { width: 375, height: 667 }
});

// Save to file
await mcp.devtools.screenshot({
  path: './screenshots/homepage.png'
});
```

### Visual Regression

```typescript
// Using jest-image-snapshot
import { toMatchImageSnapshot } from 'jest-image-snapshot';
expect.extend({ toMatchImageSnapshot });

test('homepage matches baseline', async () => {
  await mcp.devtools.navigate('http://localhost:3000');

  const screenshot = await mcp.devtools.screenshot();

  expect(screenshot).toMatchImageSnapshot({
    failureThreshold: 0.01, // 1% difference allowed
    failureThresholdType: 'percent'
  });
});

// Component-level visual test
test('button states match design', async () => {
  await mcp.devtools.navigate('http://localhost:3000/components/button');

  // Default state
  const defaultShot = await mcp.devtools.screenshot({
    selector: '.button-default'
  });
  expect(defaultShot).toMatchImageSnapshot();

  // Hover state
  await mcp.devtools.hover('.button-default');
  const hoverShot = await mcp.devtools.screenshot({
    selector: '.button-default'
  });
  expect(hoverShot).toMatchImageSnapshot();
});
```

### Responsive Testing

```typescript
const viewports = [
  { name: 'mobile', width: 375, height: 667 },
  { name: 'tablet', width: 768, height: 1024 },
  { name: 'desktop', width: 1440, height: 900 }
];

test.each(viewports)('homepage renders correctly on $name', async ({ width, height }) => {
  await mcp.devtools.setViewport({ width, height });
  await mcp.devtools.navigate('http://localhost:3000');

  const screenshot = await mcp.devtools.screenshot();
  expect(screenshot).toMatchImageSnapshot();
});
```

---

## Accessibility Testing

### Lighthouse Audit

```typescript
test('page meets accessibility standards', async () => {
  await mcp.devtools.navigate('http://localhost:3000');

  const audit = await mcp.devtools.runAccessibilityAudit();

  expect(audit.score).toBeGreaterThanOrEqual(90);

  // Check specific issues
  expect(audit.violations).toEqual([]);
});

test('form is accessible', async () => {
  await mcp.devtools.navigate('http://localhost:3000/contact');

  const audit = await mcp.devtools.runAccessibilityAudit({
    selector: 'form#contact-form'
  });

  expect(audit.violations).toHaveLength(0);
});
```

### Manual Accessibility Checks

```typescript
test('all images have alt text', async () => {
  await mcp.devtools.navigate('http://localhost:3000');

  const images = await mcp.devtools.querySelectorAll('img');

  for (const img of images) {
    const alt = await mcp.devtools.getAttribute(img, 'alt');
    expect(alt).toBeTruthy();
  }
});

test('form labels are associated', async () => {
  await mcp.devtools.navigate('http://localhost:3000/signup');

  const inputs = await mcp.devtools.querySelectorAll('input:not([type="hidden"])');

  for (const input of inputs) {
    const id = await mcp.devtools.getAttribute(input, 'id');
    const ariaLabel = await mcp.devtools.getAttribute(input, 'aria-label');
    const labelledBy = await mcp.devtools.getAttribute(input, 'aria-labelledby');

    // Either has associated label or aria attribute
    const hasLabel = id && await mcp.devtools.exists(`label[for="${id}"]`);
    expect(hasLabel || ariaLabel || labelledBy).toBeTruthy();
  }
});

test('focus is visible', async () => {
  await mcp.devtools.navigate('http://localhost:3000');

  // Tab to first focusable element
  await mcp.devtools.press('Tab');

  const activeElement = await mcp.devtools.evaluate(() =>
    document.activeElement?.tagName
  );

  // Check focus indicator is visible
  const focusOutline = await mcp.devtools.getStyle(':focus', 'outline');
  expect(focusOutline).not.toBe('none');
});
```

---

## Performance Testing

### Page Load Metrics

```typescript
test('page loads within performance budget', async () => {
  const metrics = await mcp.devtools.getPerformanceMetrics(
    'http://localhost:3000'
  );

  expect(metrics.firstContentfulPaint).toBeLessThan(1500);
  expect(metrics.largestContentfulPaint).toBeLessThan(2500);
  expect(metrics.timeToInteractive).toBeLessThan(3500);
  expect(metrics.totalBlockingTime).toBeLessThan(300);
});
```

### Network Monitoring

```typescript
test('API calls complete within timeout', async () => {
  const requests: any[] = [];

  await mcp.devtools.onRequest((request) => {
    if (request.url.includes('/api/')) {
      requests.push({
        url: request.url,
        startTime: Date.now()
      });
    }
  });

  await mcp.devtools.onResponse((response) => {
    const request = requests.find(r => r.url === response.url);
    if (request) {
      request.duration = Date.now() - request.startTime;
    }
  });

  await mcp.devtools.navigate('http://localhost:3000/dashboard');
  await mcp.devtools.waitForLoad();

  // Check all API calls completed within 2 seconds
  for (const request of requests) {
    expect(request.duration).toBeLessThan(2000);
  }
});
```

---

## Common E2E Patterns

### Login Flow

```typescript
async function login(email: string, password: string) {
  await mcp.devtools.navigate('http://localhost:3000/login');
  await mcp.devtools.type('#email', email);
  await mcp.devtools.type('#password', password);
  await mcp.devtools.click('#submit');
  await mcp.devtools.waitForNavigation();
}

test('user can login and access dashboard', async () => {
  await login('user@example.com', 'password123');

  const url = await mcp.devtools.getCurrentUrl();
  expect(url).toContain('/dashboard');

  const welcome = await mcp.devtools.getText('.welcome');
  expect(welcome).toContain('Welcome');
});
```

### CRUD Operations

```typescript
describe('Todo CRUD', () => {
  beforeEach(async () => {
    await login('user@example.com', 'password123');
    await mcp.devtools.navigate('http://localhost:3000/todos');
  });

  test('creates new todo', async () => {
    await mcp.devtools.type('#new-todo', 'Buy groceries');
    await mcp.devtools.click('#add-todo');

    await mcp.devtools.waitForSelector('.todo-item:last-child');
    const todoText = await mcp.devtools.getText('.todo-item:last-child');
    expect(todoText).toContain('Buy groceries');
  });

  test('marks todo as complete', async () => {
    await mcp.devtools.click('.todo-item:first-child .checkbox');

    const isCompleted = await mcp.devtools.exists(
      '.todo-item:first-child.completed'
    );
    expect(isCompleted).toBe(true);
  });

  test('deletes todo', async () => {
    const countBefore = (await mcp.devtools.querySelectorAll('.todo-item')).length;

    await mcp.devtools.click('.todo-item:first-child .delete-btn');
    await mcp.devtools.waitForSelectorToDisappear('.todo-item:first-child');

    const countAfter = (await mcp.devtools.querySelectorAll('.todo-item')).length;
    expect(countAfter).toBe(countBefore - 1);
  });
});
```

### Modal/Dialog Testing

```typescript
test('confirmation modal works correctly', async () => {
  await mcp.devtools.click('.delete-account-btn');

  // Wait for modal
  await mcp.devtools.waitForSelector('.modal');

  // Check modal content
  const title = await mcp.devtools.getText('.modal-title');
  expect(title).toBe('Confirm Delete');

  // Cancel
  await mcp.devtools.click('.modal-cancel');
  await mcp.devtools.waitForSelectorToDisappear('.modal');

  // Open again and confirm
  await mcp.devtools.click('.delete-account-btn');
  await mcp.devtools.waitForSelector('.modal');
  await mcp.devtools.click('.modal-confirm');

  // Verify action completed
  await mcp.devtools.waitForNavigation();
  const url = await mcp.devtools.getCurrentUrl();
  expect(url).toContain('/goodbye');
});
```

---

## Test Utilities

### Page Objects

```typescript
// tests/pages/LoginPage.ts
export class LoginPage {
  async navigate() {
    await mcp.devtools.navigate('http://localhost:3000/login');
  }

  async login(email: string, password: string) {
    await mcp.devtools.type('#email', email);
    await mcp.devtools.type('#password', password);
    await mcp.devtools.click('#submit');
  }

  async getErrorMessage() {
    return mcp.devtools.getText('.error-message');
  }

  async isLoggedIn() {
    await mcp.devtools.waitForNavigation();
    return (await mcp.devtools.getCurrentUrl()).includes('/dashboard');
  }
}

// Usage
test('login with valid credentials', async () => {
  const loginPage = new LoginPage();
  await loginPage.navigate();
  await loginPage.login('user@example.com', 'password123');

  expect(await loginPage.isLoggedIn()).toBe(true);
});
```

### Custom Assertions

```typescript
// tests/assertions/visual.ts
export async function expectElementToMatchDesign(
  selector: string,
  baselineName: string
) {
  const screenshot = await mcp.devtools.screenshot({ selector });
  expect(screenshot).toMatchImageSnapshot({
    customSnapshotIdentifier: baselineName
  });
}

// Usage
test('header matches design', async () => {
  await mcp.devtools.navigate('http://localhost:3000');
  await expectElementToMatchDesign('header', 'header-default');
});
```

---

## Debugging

### Console Logs

```typescript
await mcp.devtools.onConsole((message) => {
  console.log(`[Browser ${message.type}]`, message.text);
});
```

### Network Debugging

```typescript
await mcp.devtools.onRequest((request) => {
  console.log('Request:', request.method, request.url);
});

await mcp.devtools.onResponse((response) => {
  console.log('Response:', response.status, response.url);
});
```

### Evaluate JavaScript

```typescript
const result = await mcp.devtools.evaluate(() => {
  return {
    localStorage: { ...localStorage },
    cookies: document.cookie,
    userAgent: navigator.userAgent
  };
});
console.log('Page state:', result);
```
