# Test Recordings

This directory stores screen recordings and screenshots from automated browser tests using Chrome DevTools MCP.

## Directory Structure

```
test-recordings/
├── screenshots/          # Static screenshots
│   ├── homepage.png
│   ├── login-flow/
│   │   ├── step-1-form.png
│   │   ├── step-2-submit.png
│   │   └── step-3-dashboard.png
│   └── regression/
│       └── 2024-01-15/
├── videos/               # Screen recordings
│   ├── e2e-checkout.webm
│   ├── user-flow-login.webm
│   └── regression/
│       └── 2024-01-15/
├── traces/               # Performance traces
│   ├── homepage-trace.json
│   └── checkout-trace.json
└── reports/              # Generated test reports
    ├── visual-regression.html
    └── performance-audit.html
```

## Usage with Chrome DevTools MCP

### Taking Screenshots

```
"Navigate to localhost:3000 and take a screenshot, save it to test-recordings/screenshots/homepage.png"
```

### Recording Video

```
"Start recording the browser, perform the checkout flow, then stop recording and save to test-recordings/videos/checkout-flow.webm"
```

### Performance Traces

```
"Record a performance trace while loading the dashboard and save to test-recordings/traces/dashboard-trace.json"
```

## Puppeteer Integration

### Screenshot Example

```typescript
import puppeteer from 'puppeteer';

const browser = await puppeteer.launch();
const page = await browser.newPage();

await page.goto('http://localhost:3000');
await page.screenshot({ 
  path: 'test-recordings/screenshots/homepage.png',
  fullPage: true 
});

await browser.close();
```

### Video Recording Example

```typescript
import puppeteer from 'puppeteer';

const browser = await puppeteer.launch();
const page = await browser.newPage();

// Start recording
const recorder = await page.screencast({
  path: 'test-recordings/videos/user-flow.webm'
});

// Perform actions
await page.goto('http://localhost:3000');
await page.click('#login-button');
await page.type('#email', 'test@example.com');
await page.click('#submit');

// Stop recording
await recorder.stop();
await browser.close();
```

### Performance Trace Example

```typescript
import puppeteer from 'puppeteer';

const browser = await puppeteer.launch();
const page = await browser.newPage();

// Start tracing
await page.tracing.start({ 
  path: 'test-recordings/traces/page-load.json',
  screenshots: true 
});

await page.goto('http://localhost:3000');

// Stop tracing
await page.tracing.stop();
await browser.close();
```

## CI/CD Integration

### GitHub Actions

```yaml
- name: Run E2E Tests with Recording
  run: npm run test:e2e

- name: Upload Test Recordings
  uses: actions/upload-artifact@v4
  if: failure()
  with:
    name: test-recordings
    path: test-recordings/
    retention-days: 7
```

### Cleanup Old Recordings

```bash
# Delete recordings older than 7 days
find test-recordings/ -type f -mtime +7 -delete
```

## File Size Considerations

- Screenshots: ~100KB - 500KB each
- Videos: ~1MB - 50MB depending on duration
- Traces: ~500KB - 5MB each

**Recommendation:** Add `test-recordings/videos/` to `.gitignore` for large projects, or use Git LFS.

## Naming Conventions

### Screenshots
```
{feature}-{state}.png
{feature}/{step-number}-{description}.png
regression/{date}/{test-name}.png
```

### Videos
```
{test-type}-{feature}.webm
{date}-{test-suite}.webm
```

### Traces
```
{page-name}-trace.json
{feature}-performance.json
```
