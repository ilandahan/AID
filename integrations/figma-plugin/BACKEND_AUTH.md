# Backend Authentication Requirements

מסמך זה מתאר את ה-endpoints שהבקאנד שלך צריך לממש כדי לתמוך באימות הפלאגין.

## 🔐 שיטות אימות נתמכות

### 1. API Key + Tenant ID (מומלץ לשימוש ארגוני)

הדרך הפשוטה ביותר - כל לקוח מקבל:
- **Tenant ID** - מזהה ייחודי לארגון (למשל: `org_abc123`)
- **API Key** - מפתח סודי (למשל: `ak_live_xxxxxxxxxxxx`)

```
┌─────────────────────┐         ┌─────────────────────┐
│   Figma Plugin      │         │    Your Backend     │
├─────────────────────┤         ├─────────────────────┤
│                     │  POST   │                     │
│  Tenant: org_123    │ ──────► │  /auth/validate     │
│  API Key: ak_xxx    │         │                     │
│                     │ ◄────── │  { valid: true }    │
└─────────────────────┘         └─────────────────────┘
```

#### Endpoint: `POST /auth/validate`

**Request Headers:**
```http
Content-Type: application/json
X-Tenant-ID: org_abc123
X-API-Key: ak_live_xxxxxxxxxxxx
```

**Request Body:**
```json
{
  "tenantId": "org_abc123",
  "apiKey": "ak_live_xxxxxxxxxxxx"
}
```

**Success Response (200):**
```json
{
  "valid": true,
  "user": {
    "id": "user_123",
    "email": "user@company.com",
    "name": "John Doe",
    "tenantId": "org_abc123",
    "roles": ["admin", "designer"]
  },
  "permissions": {
    "canGenerateComponents": true,
    "canExportTokens": true,
    "maxComponentsPerDay": 100
  }
}
```

**Error Response (401):**
```json
{
  "error": "invalid_credentials",
  "message": "Invalid API key or tenant ID"
}
```

---

### 2. OAuth 2.0 + PKCE (מומלץ לאבטחה גבוהה)

לאינטגרציה עם Auth0, Cognito, Okta או כל OAuth provider.

```
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│Figma Plugin  │      │ OAuth Server │      │ Your Backend │
└──────┬───────┘      └──────┬───────┘      └──────┬───────┘
       │                     │                     │
       │ 1. Auth Request     │                     │
       │ ──────────────────► │                     │
       │                     │                     │
       │ 2. Login Page       │                     │
       │ ◄────────────────── │                     │
       │                     │                     │
       │ 3. Auth Code        │                     │
       │ ◄────────────────── │                     │
       │                     │                     │
       │ 4. Exchange Code    │                     │
       │ ──────────────────► │                     │
       │                     │                     │
       │ 5. Access Token     │                     │
       │ ◄────────────────── │                     │
       │                     │                     │
       │ 6. Validate Token   │                     │
       │ ───────────────────────────────────────► │
       │                     │                     │
       │ 7. User Info        │                     │
       │ ◄─────────────────────────────────────── │
       │                     │                     │
```

#### Endpoint: `POST /auth/oauth/callback`

**Request:**
```http
POST /auth/oauth/callback
Authorization: Bearer eyJhbGciOiJSUzI1NiIs...
Content-Type: application/json

{
  "accessToken": "eyJhbGciOiJSUzI1NiIs...",
  "idToken": "eyJhbGciOiJSUzI1NiIs..."
}
```

**Success Response (200):**
```json
{
  "tenantId": "org_abc123",
  "user": {
    "id": "user_123",
    "email": "user@company.com",
    "name": "John Doe",
    "tenantId": "org_abc123",
    "roles": ["designer"]
  }
}
```

---

### 3. JWT Validation (לאינטגרציה עם מערכות קיימות)

אם יש לך כבר מערכת אימות, הפלאגין יכול לקבל JWT ולאמת אותו.

#### Endpoint: `POST /auth/jwt/validate`

**Request:**
```http
POST /auth/jwt/validate
Authorization: Bearer eyJhbGciOiJSUzI1NiIs...
Content-Type: application/json
```

**Success Response (200):**
```json
{
  "valid": true,
  "tenantId": "org_abc123",
  "exp": 1703001600,
  "user": {
    "id": "user_123",
    "email": "user@company.com",
    "name": "John Doe",
    "tenantId": "org_abc123",
    "roles": ["designer"]
  }
}
```

---

## 🔒 אבטחת בקשות MCP

כל בקשה מהפלאגין לבקאנד תכלול:

### Headers לבקשות עם API Key:
```http
X-Tenant-ID: org_abc123
X-API-Key: ak_live_xxxxxxxxxxxx
X-Timestamp: 1703001600000
X-Nonce: a1b2c3d4e5f6g7h8
Content-Type: application/json
```

### Headers לבקשות עם OAuth/JWT:
```http
Authorization: Bearer eyJhbGciOiJSUzI1NiIs...
X-Tenant-ID: org_abc123
X-Timestamp: 1703001600000
X-Nonce: a1b2c3d4e5f6g7h8
Content-Type: application/json
```

### אימות בצד השרת:

```typescript
// Express middleware example
function validateRequest(req, res, next) {
  const timestamp = parseInt(req.headers['x-timestamp']);
  const nonce = req.headers['x-nonce'];
  
  // 1. Check timestamp (reject if older than 5 minutes)
  if (Date.now() - timestamp > 5 * 60 * 1000) {
    return res.status(401).json({ error: 'Request expired' });
  }
  
  // 2. Check nonce (prevent replay attacks)
  if (await nonceStore.exists(nonce)) {
    return res.status(401).json({ error: 'Duplicate request' });
  }
  await nonceStore.add(nonce, timestamp);
  
  // 3. Validate credentials
  const tenantId = req.headers['x-tenant-id'];
  const apiKey = req.headers['x-api-key'];
  const authHeader = req.headers['authorization'];
  
  if (apiKey) {
    // API Key validation
    const valid = await validateApiKey(tenantId, apiKey);
    if (!valid) {
      return res.status(401).json({ error: 'Invalid API key' });
    }
  } else if (authHeader) {
    // JWT validation
    const token = authHeader.replace('Bearer ', '');
    const decoded = await validateJWT(token);
    if (!decoded || decoded.tenantId !== tenantId) {
      return res.status(401).json({ error: 'Invalid token' });
    }
    req.user = decoded;
  } else {
    return res.status(401).json({ error: 'Missing credentials' });
  }
  
  req.tenantId = tenantId;
  next();
}
```

---

## 📋 MCP Endpoints שצריך לממש

### 1. Component Generation
```http
POST /mcp
Content-Type: application/json
X-Tenant-ID: org_abc123
X-API-Key: ak_live_xxxxxxxxxxxx

{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "generate_component",
    "arguments": {
      "component": { /* EnrichedComponentData */ },
      "tokens": [ /* DesignToken[] */ ],
      "metadata": {
        "fileKey": "abc123",
        "nodeId": "1:23",
        "exportedAt": "2024-01-01T00:00:00Z",
        "pluginVersion": "1.0.0"
      }
    }
  }
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "success": true,
    "componentId": "button-primary",
    "files": [
      "src/atoms/Button/Button.tsx",
      "src/atoms/Button/Button.styles.ts",
      "src/atoms/Button/Button.stories.tsx"
    ]
  }
}
```

---

## 🛡️ המלצות אבטחה

### 1. HTTPS בלבד
```
✅ https://api.yourcompany.com/mcp
❌ http://api.yourcompany.com/mcp
```

### 2. Rate Limiting
```typescript
// Limit by tenant
const rateLimiter = rateLimit({
  windowMs: 60 * 1000, // 1 minute
  max: 100, // max 100 requests per minute per tenant
  keyGenerator: (req) => req.tenantId,
});
```

### 3. IP Whitelisting (אופציונלי)
```typescript
// Allow only Figma plugin IPs or customer IPs
const allowedIPs = await getTenantAllowedIPs(tenantId);
if (!allowedIPs.includes(req.ip)) {
  return res.status(403).json({ error: 'IP not allowed' });
}
```

### 4. API Key Rotation
```typescript
// Support multiple active keys for rotation
const keys = await getActiveApiKeys(tenantId);
const valid = keys.some(key => key.value === providedKey && !key.revoked);
```

### 5. Audit Logging
```typescript
// Log all requests for audit
await auditLog.create({
  tenantId,
  userId: req.user?.id,
  action: 'generate_component',
  componentId: component.componentId,
  timestamp: new Date(),
  ip: req.ip,
});
```

---

## 🔑 יצירת API Keys ללקוחות

### בממשק הניהול שלך:

```typescript
// Generate new API key
function generateApiKey(): string {
  const prefix = 'ak_live_';
  const randomPart = crypto.randomBytes(24).toString('base64url');
  return prefix + randomPart;
}

// Store hashed (never store plain text!)
async function createApiKey(tenantId: string, name: string) {
  const plainKey = generateApiKey();
  const hashedKey = await bcrypt.hash(plainKey, 12);
  
  await db.apiKeys.create({
    tenantId,
    name,
    keyHash: hashedKey,
    keyPrefix: plainKey.substring(0, 12), // For identification
    createdAt: new Date(),
    lastUsed: null,
  });
  
  // Return plain key ONLY ONCE
  return plainKey;
}
```

### UI לניהול מפתחות:

```
┌─────────────────────────────────────────────────┐
│  API Keys                              [+ New]  │
├─────────────────────────────────────────────────┤
│                                                 │
│  🔑 Production Key                              │
│     ak_live_xxxx...xxxx                        │
│     Created: Jan 1, 2024 • Last used: 2h ago   │
│     [Revoke]                                    │
│                                                 │
│  🔑 Development Key                             │
│     ak_test_yyyy...yyyy                        │
│     Created: Dec 15, 2023 • Never used         │
│     [Revoke]                                    │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## 📱 דוגמת קוד לבקאנד (Node.js/Express)

```typescript
// backend/src/routes/auth.ts
import express from 'express';
import bcrypt from 'bcrypt';
import jwt from 'jsonwebtoken';

const router = express.Router();

// API Key validation
router.post('/validate', async (req, res) => {
  const { tenantId, apiKey } = req.body;
  
  // Find tenant
  const tenant = await db.tenants.findById(tenantId);
  if (!tenant) {
    return res.status(401).json({ error: 'Invalid tenant' });
  }
  
  // Find and validate API key
  const keys = await db.apiKeys.findByTenant(tenantId);
  let validKey = null;
  
  for (const key of keys) {
    if (await bcrypt.compare(apiKey, key.keyHash)) {
      validKey = key;
      break;
    }
  }
  
  if (!validKey) {
    return res.status(401).json({ error: 'Invalid API key' });
  }
  
  // Update last used
  await db.apiKeys.updateLastUsed(validKey.id);
  
  // Get user info
  const user = await db.users.findByApiKey(validKey.id);
  
  res.json({
    valid: true,
    user: {
      id: user.id,
      email: user.email,
      name: user.name,
      tenantId,
      roles: user.roles,
    },
    permissions: tenant.permissions,
  });
});

// JWT validation
router.post('/jwt/validate', async (req, res) => {
  const token = req.headers.authorization?.replace('Bearer ', '');
  
  if (!token) {
    return res.status(401).json({ error: 'Missing token' });
  }
  
  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    
    // Verify tenant exists
    const tenant = await db.tenants.findById(decoded.tenantId);
    if (!tenant) {
      return res.status(401).json({ error: 'Invalid tenant' });
    }
    
    res.json({
      valid: true,
      tenantId: decoded.tenantId,
      exp: decoded.exp,
      user: decoded.user,
    });
  } catch (err) {
    res.status(401).json({ error: 'Invalid token' });
  }
});

export default router;
```

---

## 🧪 בדיקה

### cURL לבדיקת API Key:
```bash
curl -X POST https://your-backend.com/auth/validate \
  -H "Content-Type: application/json" \
  -H "X-Tenant-ID: org_abc123" \
  -H "X-API-Key: ak_live_xxxxxxxxxxxx" \
  -d '{"tenantId": "org_abc123", "apiKey": "ak_live_xxxxxxxxxxxx"}'
```

### cURL לבדיקת MCP עם אימות:
```bash
curl -X POST https://your-backend.com/mcp \
  -H "Content-Type: application/json" \
  -H "X-Tenant-ID: org_abc123" \
  -H "X-API-Key: ak_live_xxxxxxxxxxxx" \
  -H "X-Timestamp: $(date +%s000)" \
  -H "X-Nonce: $(openssl rand -hex 8)" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list",
    "params": {}
  }'
```
