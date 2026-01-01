# AID Plugin Pairing

Generate a one-time pairing code to connect your Figma plugin with AID.

## Usage

Run `/aid-pair` when you want to authenticate your Figma plugin with the AID system.

## What This Command Does

### Step 1: Validate Server is Running

```bash
curl -s http://localhost:3001/health
```

**If server is NOT running:**
```
❌ Figma Plugin Server is not running!

Starting server...
cd "C:\ilans' local files\demo\last-one\integrations\figma-plugin\server" && npm run dev &

Waiting for server to be ready...
```

Wait up to 10 seconds for server to respond to `/health`.

**If server fails to start:**
```
❌ Could not start Figma Plugin Server

Please start manually:
  cd "C:\ilans' local files\demo\last-one\integrations\figma-plugin\server"
  npm run dev

Then run /aid-pair again.
```

### Step 2: Validate MCP Connection

Check that the server's MCP endpoint is accessible:

```bash
curl -s -X POST http://localhost:3001/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/list","id":1}'
```

**Expected response:** List of available tools (auditComponent, generateMetadata, etc.)

**If MCP fails:**
```
❌ MCP endpoint not responding

Server is running but MCP is not configured.
Check server logs for errors.
```

### Step 3: Generate OTP Code

Once server and MCP are validated:

```bash
curl -X POST http://localhost:3001/auth/generate-pairing \
  -H "Content-Type: application/json" \
  -d '{"tenantId": "{project-id}", "projectPath": "{cwd}"}'
```

### Step 4: Display Pairing Code

```
╔══════════════════════════════════════════════════════════╗
║                  🔗 AID PAIRING CODE                      ║
╠══════════════════════════════════════════════════════════╣
║                                                          ║
║        Enter this code in your Figma plugin:             ║
║                                                          ║
║                    XXX XXX                               ║
║                                                          ║
║        ⏱️  Valid for 5 minutes                           ║
║        🔒 Single use only                                ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝

In Figma:
1. Open the Atomic Design Extractor plugin
2. Enter the 6-digit code in the pairing screen
3. Click "Pair with AID"
```

## Security

- Codes are single-use only
- Codes expire after 5 minutes
- Maximum 3 incorrect attempts per code
- Rate limited to prevent brute force attacks
- Pairing codes can ONLY be generated from localhost (Claude Code)

## Server Details

| Property | Value |
|----------|-------|
| Server Path | `C:\ilans' local files\demo\last-one\integrations\figma-plugin\server` |
| Port | 3001 |
| Health Check | `http://localhost:3001/health` |
| MCP Endpoint | `http://localhost:3001/mcp` |
| Pairing Endpoint | `http://localhost:3001/auth/generate-pairing` |

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Code expired | Run `/aid-pair` again |
| Invalid code | Check you entered it correctly |
| Too many attempts | Wait 1 minute, run `/aid-pair` for fresh code |
| Server not running | Will auto-start, or run `cd fig-plugin/server && npm run dev` |
| MCP not responding | Check server logs for skill loading errors |

## Flow Diagram

```
/aid-pair
    │
    ▼
┌─────────────────┐
│ Check Server    │──── Not running ───► Start server
│ localhost:3001  │                              │
└────────┬────────┘                              │
         │ Running                               │
         ▼                                       ▼
┌─────────────────┐                    ┌─────────────────┐
│ Check MCP       │                    │ Wait for ready  │
│ POST /mcp       │                    │ (10 sec max)    │
└────────┬────────┘                    └────────┬────────┘
         │ OK                                   │
         ▼                                      │
┌─────────────────┐◄────────────────────────────┘
│ Generate OTP    │
│ POST /auth/...  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Display Code    │
│ 6-digit OTP     │
└─────────────────┘
```
