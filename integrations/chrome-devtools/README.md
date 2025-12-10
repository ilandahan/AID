# Chrome DevTools MCP Integration

Browser automation, debugging, and performance analysis for AI-assisted development.

## Overview

Chrome DevTools MCP allows Claude Code to control and inspect a live Chrome browser, providing:

- **Performance Insights** - Record traces and extract actionable performance data
- **Browser Debugging** - Analyze network requests, console logs, and errors
- **Screenshots** - Capture page screenshots for visual verification
- **Reliable Automation** - Puppeteer-based actions with automatic wait handling
- **JavaScript Execution** - Run JS directly in browser context
- **DOM Inspection** - Inspect elements, page metrics, and multi-frame support

## Dependencies

| Package | Type | Installation | Purpose |
|---------|------|--------------|---------|
| `chrome-devtools-mcp@latest` | MCP Server | `npx` (on-demand) | Browser automation via Claude |
| `puppeteer` | Dev dependency | `npm install --save-dev` | Browser automation testing |
| `chromium` | Binary | Auto-installed by puppeteer | Headless browser for testing |

### Install Dependencies

```bash
# Install puppeteer (includes Chromium)
npm install --save-dev puppeteer

# Or install from package.json
npm install
```

**Note:** Chromium (~170MB) is automatically downloaded when installing puppeteer.

## Installation

### Claude Code CLI

```bash
claude mcp add chrome-devtools npx chrome-devtools-mcp@latest
```

### Configuration File (.mcp.json)

```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": ["-y", "chrome-devtools-mcp@latest"]
    }
  }
}
```

### Connect to Existing Chrome Instance

```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": [
        "-y",
        "chrome-devtools-mcp@latest",
        "--browser-url=http://127.0.0.1:9222"
      ]
    }
  }
}
```

## Available Tools

| Tool | Description |
|------|-------------|
| `navigate_page` | Navigate to a URL |
| `take_snapshot` | Capture accessibility snapshot of page |
| `take_screenshot` | Take visual screenshot |
| `click` | Click on element by UID |
| `fill` | Fill input field |
| `get_console_logs` | Retrieve browser console output |
| `get_network_requests` | Monitor network activity |
| `execute_javascript` | Run JS in browser context |
| `get_performance_metrics` | Capture performance data |
| `record_trace` | Record performance trace |

## Usage by Phase

### Phase 5: Development

```
"Navigate to localhost:3000 and take a screenshot of the homepage"
"Check the console for any errors after clicking the submit button"
"Fill in the login form with test credentials and verify redirect"
```

### Phase 6: Testing

```
"Take screenshots of all main pages for visual regression"
"Record a performance trace while loading the dashboard"
"Verify all API calls complete successfully on the checkout flow"
```

### Phase 7: Code Review

```
"Analyze the network requests on page load - are there any unnecessary calls?"
"Check Core Web Vitals metrics for the landing page"
"Verify no console errors appear during normal user flow"
```

## Chrome Setup Options

### Automatic (Default)

Chrome DevTools MCP starts Chrome automatically - no setup needed.

### Manual Chrome Instance

Launch Chrome with remote debugging:

```bash
# macOS
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222

# Linux
google-chrome --remote-debugging-port=9222

# Windows
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222
```

### Headless Mode (CI/CD)

```bash
npx chrome-devtools-mcp@latest --headless
```

### Isolated Session

```bash
npx chrome-devtools-mcp@latest --isolated
```

## Example Workflows

### Visual Testing Flow

```
1. navigate_page("http://localhost:3000")
2. take_screenshot() -> save as baseline
3. Make code changes
4. take_screenshot() -> compare with baseline
```

### Performance Audit

```
1. navigate_page("https://your-app.com")
2. record_trace() for 5 seconds
3. get_performance_metrics()
4. Analyze Core Web Vitals
```

### E2E User Flow

```
1. navigate_page("http://localhost:3000/login")
2. take_snapshot()
3. fill(email_field, "test@example.com")
4. fill(password_field, "password123")
5. click(submit_button)
6. take_snapshot() -> verify dashboard loaded
7. get_console_logs() -> check for errors
```

## Security Notes

⚠️ **Important**: Chrome DevTools MCP exposes browser content to AI assistants.

- Don't use with browsers containing saved passwords or authenticated sessions
- Use `--isolated` flag for temporary browser profiles
- Avoid production data during debugging
- Review AI assistant data handling policies

## Troubleshooting

### Connection Issues

```bash
# Verify Chrome is accessible
curl http://127.0.0.1:9222/json/version

# Remove and re-add server
claude mcp remove chrome-devtools
claude mcp add chrome-devtools npx chrome-devtools-mcp@latest
```

### Sandbox Issues

Some environments block Chrome sandbox. Use:

```bash
npx chrome-devtools-mcp@latest --no-sandbox
```

### Timeout Issues

Increase startup timeout in configuration if Chrome is slow to launch.

## Resources

- [Chrome DevTools MCP GitHub](https://github.com/ChromeDevTools/chrome-devtools-mcp)
- [Chrome DevTools Protocol](https://chromedevtools.github.io/devtools-protocol/)
- [Puppeteer Documentation](https://pptr.dev/)

## Test Recordings Directory

All test recordings are stored in `test-recordings/`:

```
test-recordings/
├── screenshots/     # Static screenshots (.png, .jpg)
├── videos/          # Screen recordings (.webm, .mp4)
├── traces/          # Performance traces (.json)
└── reports/         # Generated reports (.html)
```

### Save Screenshot

```
"Take a screenshot and save to test-recordings/screenshots/homepage.png"
```

### Record Video

```
"Start recording, perform the login flow, save to test-recordings/videos/login-flow.webm"
```

### Performance Trace

```
"Record a performance trace of the checkout page, save to test-recordings/traces/checkout.json"
```

### Cleanup Old Recordings

```bash
# Delete recordings older than 7 days
make clean-recordings

# Or manually
find test-recordings/ -type f -not -name ".gitkeep" -not -name "README.md" -mtime +7 -delete
```
