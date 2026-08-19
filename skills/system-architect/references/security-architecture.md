# Security Architecture Patterns

Reference guide for implementing security-first architecture in SaaS applications.

---

## Defense in Depth Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         DEFENSE IN DEPTH                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Layer 1: Network Security                                              │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  • WAF (OWASP rules, DDoS protection)                            │   │
│  │  • CDN with edge security                                        │   │
│  │  • Network segmentation (VPC, subnets)                           │   │
│  │  • Firewall rules (security groups)                              │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                              ▼                                          │
│  Layer 2: Application Gateway                                           │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  • API Gateway (rate limiting, throttling)                       │   │
│  │  • JWT validation                                                │   │
│  │  • API key management                                            │   │
│  │  • Request/response logging                                      │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                              ▼                                          │
│  Layer 3: Application Security                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  • Input validation                                              │   │
│  │  • Business logic authorization (RBAC)                           │   │
│  │  • Session management                                            │   │
│  │  • Output encoding                                               │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                              ▼                                          │
│  Layer 4: Data Security                                                 │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  • Row-level security (tenant isolation)                         │   │
│  │  • Field-level encryption                                        │   │
│  │  • Encryption at rest                                            │   │
│  │  • Secure backup and recovery                                    │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Authentication Architecture

### OAuth2 + JWT Flow

```
┌──────────┐                                    ┌──────────────┐
│  Client  │                                    │   Identity   │
│  (SPA)   │                                    │   Provider   │
└────┬─────┘                                    └──────┬───────┘
     │                                                 │
     │  1. Redirect to /authorize                      │
     │────────────────────────────────────────────────▶│
     │                                                 │
     │  2. User authenticates (+ MFA if required)      │
     │                                                 │
     │  3. Authorization code                          │
     │◀────────────────────────────────────────────────│
     │                                                 │
     │  4. Exchange code for tokens                    │
     │                                                 │
┌────▼─────┐                                    ┌──────▼───────┐
│  Client  │                                    │   Identity   │
│  (SPA)   │                                    │   Provider   │
└────┬─────┘                                    └──────────────┘
     │
     │  5. API request with access_token
     │
┌────▼─────────────────────────────────────────────────────────┐
│                       API Gateway                             │
├───────────────────────────────────────────────────────────────┤
│  • Validate JWT signature (RS256)                             │
│  • Check expiration                                           │
│  • Verify audience/issuer                                     │
│  • Extract claims (user_id, tenant_id, roles)                 │
│  • Set request context                                        │
└────┬─────────────────────────────────────────────────────────┘
     │
     │  6. Validated request with claims
     │
┌────▼─────────────────────────────────────────────────────────┐
│                       Application                             │
├───────────────────────────────────────────────────────────────┤
│  • Additional authorization checks                            │
│  • Business logic                                             │
│  • Audit logging                                              │
└──────────────────────────────────────────────────────────────┘
```

### Token Configuration

```typescript
// Access Token (short-lived)
interface AccessToken {
  iss: string;           // Issuer
  sub: string;           // User ID
  aud: string[];         // Audience (API identifiers)
  exp: number;           // Expiration (15 minutes)
  iat: number;           // Issued at
  scope: string;         // Permissions
  tenant_id: string;     // Tenant isolation
  roles: string[];       // User roles
}

// Refresh Token (longer-lived)
interface RefreshToken {
  jti: string;           // Unique token ID (for revocation)
  sub: string;           // User ID
  exp: number;           // Expiration (7 days)
  family: string;        // Token family (for rotation)
}

// Token Settings
const TOKEN_CONFIG = {
  accessToken: {
    algorithm: 'RS256',
    expiresIn: '15m',
    audience: ['https://api.example.com'],
  },
  refreshToken: {
    expiresIn: '7d',
    rotateOnUse: true,    // Issue new refresh token each use
    revokeFamily: true,   // Revoke all tokens in family on reuse
  },
};
```

### API Key Authentication (Service-to-Service)

```typescript
// API Key structure
interface ApiKey {
  id: string;              // Key ID (prefix shown to user)
  hash: string;            // SHA-256 hash of full key
  tenantId: string;        // Owner tenant
  name: string;            // Human-readable name
  scopes: string[];        // Allowed operations
  rateLimit: number;       // Requests per minute
  expiresAt?: Date;        // Optional expiration
  lastUsedAt: Date;        // Track usage
  createdAt: Date;
  createdBy: string;       // User who created
}

// API Key format: prefix_secret
// Example: sk_live_abc123...xyz789
// Only show prefix after creation: sk_live_abc123...
```

---

## Authorization Architecture

### RBAC (Role-Based Access Control)

```
┌─────────────────────────────────────────────────────────────────┐
│                    RBAC HIERARCHY                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐                                               │
│  │    User      │                                               │
│  │   (john)     │                                               │
│  └──────┬───────┘                                               │
│         │ has                                                   │
│         ▼                                                       │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐    │
│  │    Role      │     │    Role      │     │    Role      │    │
│  │   (admin)    │     │   (editor)   │     │   (viewer)   │    │
│  └──────┬───────┘     └──────┬───────┘     └──────┬───────┘    │
│         │ grants             │ grants             │ grants      │
│         ▼                    ▼                    ▼             │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                     Permissions                           │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │  resources:create  resources:read  resources:update      │  │
│  │  resources:delete  users:manage    settings:admin        │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Permission Matrix

| Role | resources:* | users:* | settings:* | audit:* |
|------|------------|---------|------------|---------|
| viewer | read | - | - | - |
| editor | read, create, update | read | read | - |
| admin | all | all | all | read |
| super_admin | all | all | all | all |

### Resource-Level Authorization

```typescript
// Authorization middleware
async function authorize(
  user: User,
  action: string,
  resource: Resource
): Promise<AuthzResult> {
  // 1. Check global permissions
  if (!hasPermission(user, action)) {
    return { allowed: false, reason: 'INSUFFICIENT_PERMISSIONS' };
  }

  // 2. Check tenant isolation
  if (resource.tenantId !== user.tenantId) {
    auditLog('CROSS_TENANT_ACCESS_ATTEMPT', { user, resource });
    return { allowed: false, reason: 'TENANT_VIOLATION' };
  }

  // 3. Check resource-specific rules
  const resourceRules = getResourceRules(resource.type);
  if (resourceRules.ownerOnly && resource.ownerId !== user.id) {
    return { allowed: false, reason: 'NOT_OWNER' };
  }

  // 4. Check attribute-based rules
  if (!evaluateAbacRules(user, action, resource)) {
    return { allowed: false, reason: 'ABAC_DENIED' };
  }

  return { allowed: true };
}
```

---

## Multi-Tenancy Security

### Tenant Isolation Strategies

```
┌─────────────────────────────────────────────────────────────────┐
│                 MULTI-TENANCY MODELS                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Model 1: Shared Database, Row-Level Security                   │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  ┌─────────────────────────────────────────────────────┐  │ │
│  │  │                   Database                          │  │ │
│  │  │  ┌─────────────────────────────────────────────┐   │  │ │
│  │  │  │  tenant_id = 'A' │ tenant_id = 'B' │ ...    │   │  │ │
│  │  │  └─────────────────────────────────────────────┘   │  │ │
│  │  │         RLS Policy enforces isolation              │  │ │
│  │  └─────────────────────────────────────────────────────┘  │ │
│  └───────────────────────────────────────────────────────────┘ │
│  ✓ Cost-effective  ✓ Simple operations  ✗ Noisy neighbor risk │
│                                                                 │
│  Model 2: Schema Per Tenant                                     │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  ┌─────────────────────────────────────────────────────┐  │ │
│  │  │                   Database                          │  │ │
│  │  │  ┌─────────┐  ┌─────────┐  ┌─────────┐            │  │ │
│  │  │  │Schema A │  │Schema B │  │Schema C │            │  │ │
│  │  │  └─────────┘  └─────────┘  └─────────┘            │  │ │
│  │  └─────────────────────────────────────────────────────┘  │ │
│  └───────────────────────────────────────────────────────────┘ │
│  ✓ Better isolation  ✓ Easier backup  ✗ Schema management     │
│                                                                 │
│  Model 3: Database Per Tenant                                   │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐                   │ │
│  │  │  DB A   │  │  DB B   │  │  DB C   │                   │ │
│  │  └─────────┘  └─────────┘  └─────────┘                   │ │
│  └───────────────────────────────────────────────────────────┘ │
│  ✓ Full isolation  ✓ Compliance  ✗ Higher cost  ✗ Complex ops │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Row-Level Security Implementation

```sql
-- Enable RLS on all tenant tables
ALTER TABLE resources ENABLE ROW LEVEL SECURITY;

-- Policy for SELECT, UPDATE, DELETE
CREATE POLICY tenant_isolation_select ON resources
    FOR SELECT
    USING (tenant_id = current_setting('app.tenant_id')::uuid);

CREATE POLICY tenant_isolation_insert ON resources
    FOR INSERT
    WITH CHECK (tenant_id = current_setting('app.tenant_id')::uuid);

CREATE POLICY tenant_isolation_update ON resources
    FOR UPDATE
    USING (tenant_id = current_setting('app.tenant_id')::uuid);

CREATE POLICY tenant_isolation_delete ON resources
    FOR DELETE
    USING (tenant_id = current_setting('app.tenant_id')::uuid);

-- Set tenant context in application
-- Must be set at start of each request
SET app.tenant_id = 'tenant-uuid-here';
```

### Application-Level Tenant Context

```typescript
// Middleware to set tenant context
async function tenantContextMiddleware(req, res, next) {
  const tenantId = req.user?.tenantId;

  if (!tenantId) {
    return res.status(401).json({ error: 'TENANT_REQUIRED' });
  }

  // Set database context for RLS
  await db.raw(`SET app.tenant_id = '${tenantId}'`);

  // Add to request context
  req.tenantId = tenantId;

  next();
}

// Repository with tenant scoping
class ResourceRepository {
  async findById(id: string, tenantId: string): Promise<Resource | null> {
    // Even with RLS, explicitly filter as defense in depth
    return db('resources')
      .where({ id, tenant_id: tenantId })
      .first();
  }
}
```

---

## Data Encryption Architecture

### Encryption Layers

```
┌─────────────────────────────────────────────────────────────────┐
│                    ENCRYPTION LAYERS                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. In Transit (TLS 1.3)                                        │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  Client ◄─── TLS 1.3 ───► Load Balancer                   │ │
│  │  Load Balancer ◄─── TLS ───► Application                  │ │
│  │  Application ◄─── TLS ───► Database                       │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  2. At Rest (AES-256)                                           │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  • Database: RDS encryption (AWS managed)                  │ │
│  │  • Storage: S3 server-side encryption (SSE-KMS)            │ │
│  │  • Backups: Encrypted with same key                        │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  3. Application-Level (Field Encryption)                        │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  • PII fields: AES-256-GCM with KMS data keys             │ │
│  │  • Per-tenant keys for additional isolation               │ │
│  │  • Searchable encryption for specific fields              │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Field-Level Encryption

```typescript
import { KMSClient, GenerateDataKeyCommand, DecryptCommand } from '@aws-sdk/client-kms';

class FieldEncryption {
  private kms: KMSClient;
  private keyId: string;

  async encrypt(plaintext: string, context: Record<string, string>): Promise<EncryptedField> {
    // Generate data key for envelope encryption
    const { Plaintext: dataKey, CiphertextBlob: encryptedDataKey } =
      await this.kms.send(new GenerateDataKeyCommand({
        KeyId: this.keyId,
        KeySpec: 'AES_256',
        EncryptionContext: context, // tenant_id, field_name
      }));

    // Encrypt data with data key
    const cipher = crypto.createCipheriv('aes-256-gcm', dataKey, iv);
    const encrypted = Buffer.concat([cipher.update(plaintext), cipher.final()]);
    const authTag = cipher.getAuthTag();

    // Wipe plaintext key from memory
    dataKey.fill(0);

    return {
      ciphertext: encrypted.toString('base64'),
      encryptedDataKey: encryptedDataKey.toString('base64'),
      iv: iv.toString('base64'),
      authTag: authTag.toString('base64'),
      context,
    };
  }

  async decrypt(field: EncryptedField): Promise<string> {
    // Decrypt data key with KMS
    const { Plaintext: dataKey } = await this.kms.send(new DecryptCommand({
      CiphertextBlob: Buffer.from(field.encryptedDataKey, 'base64'),
      EncryptionContext: field.context,
    }));

    // Decrypt data
    const decipher = crypto.createDecipheriv(
      'aes-256-gcm',
      dataKey,
      Buffer.from(field.iv, 'base64')
    );
    decipher.setAuthTag(Buffer.from(field.authTag, 'base64'));

    const decrypted = Buffer.concat([
      decipher.update(Buffer.from(field.ciphertext, 'base64')),
      decipher.final()
    ]);

    // Wipe key from memory
    dataKey.fill(0);

    return decrypted.toString('utf8');
  }
}
```

---

## Audit Logging Architecture

### Centralized Audit Log

```
┌─────────────────────────────────────────────────────────────────┐
│                    AUDIT LOG ARCHITECTURE                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐    │
│  │ Application  │────▶│   Audit      │────▶│  Write-Once  │    │
│  │   Events     │     │   Service    │     │   Storage    │    │
│  └──────────────┘     └──────────────┘     └──────────────┘    │
│                              │                                  │
│                              ▼                                  │
│                       ┌──────────────┐                          │
│                       │     SIEM     │                          │
│                       │  (Alerting)  │                          │
│                       └──────────────┘                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Audit Event Schema

```typescript
interface AuditEvent {
  // Identity
  id: string;              // Unique event ID
  timestamp: Date;         // ISO 8601 with timezone
  version: string;         // Schema version

  // Actor
  actor: {
    type: 'user' | 'service' | 'system';
    id: string;
    email?: string;
    ip?: string;
    userAgent?: string;
  };

  // Context
  tenant: {
    id: string;
    name: string;
  };

  // Action
  action: {
    type: string;          // e.g., 'resource.create'
    status: 'success' | 'failure';
    reason?: string;       // Failure reason
  };

  // Target
  resource?: {
    type: string;          // e.g., 'user', 'document'
    id: string;
    name?: string;
  };

  // Changes (for modifications)
  changes?: {
    before?: Record<string, unknown>;
    after?: Record<string, unknown>;
  };

  // Request metadata
  request?: {
    id: string;            // Correlation ID
    method: string;
    path: string;
    duration: number;
  };
}
```

### Audit Events to Capture

| Category | Events | Retention |
|----------|--------|-----------|
| **Authentication** | login, logout, mfa_challenge, password_reset | 2 years |
| **Authorization** | permission_denied, role_change, policy_update | 2 years |
| **Data Access** | read, export, search (sensitive data) | 1 year |
| **Data Modification** | create, update, delete | 7 years |
| **Admin Actions** | user_create, user_delete, settings_change | 7 years |
| **Security Events** | suspicious_activity, rate_limit, blocked_ip | 2 years |

---

## Secrets Management

### Secrets Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    SECRETS MANAGEMENT                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                 AWS Secrets Manager                       │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │  │
│  │  │ DB Creds    │  │ API Keys    │  │ Encryption  │      │  │
│  │  │ (rotating)  │  │ (static)    │  │   Keys      │      │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘      │  │
│  └───────────────────────────┬──────────────────────────────┘  │
│                              │                                  │
│                              ▼                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Application (at startup)                     │  │
│  │  • Fetch secrets from Secrets Manager                    │  │
│  │  • Cache in memory (encrypted)                           │  │
│  │  • Refresh on rotation event                             │  │
│  │  • NEVER log or expose secrets                           │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Secrets Handling Rules

```
DO:
✓ Store secrets in AWS Secrets Manager or Vault
✓ Use IAM roles for service authentication
✓ Enable automatic rotation
✓ Use environment variables (injected at runtime)
✓ Audit secret access
✓ Encrypt secrets in transit and at rest

DON'T:
✗ Commit secrets to source control
✗ Log secrets (even partially)
✗ Pass secrets as command line arguments
✗ Store secrets in plain text files
✗ Embed secrets in container images
✗ Share secrets via email/chat
```

---

## Security Monitoring

### Security Metrics Dashboard

| Metric | Normal | Warning | Critical |
|--------|--------|---------|----------|
| Failed logins/min | < 10 | 10-50 | > 50 |
| Auth errors/min | < 5 | 5-20 | > 20 |
| Rate limit hits/min | < 100 | 100-500 | > 500 |
| Blocked IPs/hour | < 5 | 5-20 | > 20 |
| Suspicious requests/hour | < 10 | 10-50 | > 50 |

### Security Alerts

```typescript
const SECURITY_ALERTS = {
  AUTH_FAILURES_SPIKE: {
    condition: 'auth_failures > 5x baseline',
    severity: 'critical',
    action: 'page_security_team',
    runbook: 'https://docs/runbooks/auth-failures',
  },
  UNUSUAL_DATA_ACCESS: {
    condition: 'data_access > 2 std_dev from baseline',
    severity: 'warning',
    action: 'investigate_and_notify',
  },
  CROSS_TENANT_ATTEMPT: {
    condition: 'any cross_tenant access',
    severity: 'critical',
    action: 'block_and_page',
  },
  PRIVILEGE_ESCALATION: {
    condition: 'role_change without approval',
    severity: 'critical',
    action: 'rollback_and_investigate',
  },
};
```

---

## Security Testing

### Security Test Types

| Test Type | When | Tools | Coverage |
|-----------|------|-------|----------|
| SAST | Every commit | SonarQube, Semgrep | Code vulnerabilities |
| Dependency Scan | Every commit | Snyk, Dependabot | Known CVEs |
| DAST | Pre-deploy | OWASP ZAP | Runtime vulnerabilities |
| Penetration Test | Quarterly | Manual | Full stack |
| Red Team | Annual | External firm | Real-world attacks |

### Security Test Checklist

- [ ] SQL injection testing
- [ ] XSS testing (stored, reflected, DOM)
- [ ] CSRF protection validation
- [ ] Authentication bypass attempts
- [ ] Authorization testing (horizontal & vertical)
- [ ] Session management testing
- [ ] Input validation testing
- [ ] File upload validation
- [ ] API rate limiting verification
- [ ] Error handling (no stack traces leaked)
