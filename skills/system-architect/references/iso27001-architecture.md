# ISO 27001 Compliance Architecture

Reference guide for implementing ISO 27001:2022 controls in software architecture.

---

## ISO 27001 Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                   ISO 27001:2022 STRUCTURE                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ISMS (Information Security Management System)                  │
│  ├── Context & Leadership (Clauses 4-5)                         │
│  ├── Planning & Support (Clauses 6-7)                           │
│  ├── Operation (Clause 8)                                       │
│  ├── Performance Evaluation (Clause 9)                          │
│  └── Improvement (Clause 10)                                    │
│                                                                 │
│  Annex A Controls (93 controls in 4 themes)                     │
│  ├── A.5 Organizational (37 controls)                           │
│  ├── A.6 People (8 controls)                                    │
│  ├── A.7 Physical (14 controls)                                 │
│  └── A.8 Technological (34 controls)                            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Annex A Controls Relevant to Software Architecture

### A.5 Organizational Controls

| Control | Title | Architecture Implementation |
|---------|-------|---------------------------|
| A.5.1 | Policies for information security | CLAUDE.md, security policies in docs |
| A.5.9 | Inventory of information | Asset registry, data catalog |
| A.5.10 | Acceptable use of information | Access control policies, RBAC |
| A.5.12 | Classification of information | Data classification system |
| A.5.13 | Labelling of information | Classification tags on data |
| A.5.14 | Information transfer | TLS, encryption policies |
| A.5.15 | Access control | RBAC implementation |
| A.5.16 | Identity management | IAM, user provisioning |
| A.5.17 | Authentication information | Password policies, MFA |
| A.5.18 | Access rights | Permission management |
| A.5.23 | Information security for cloud | Cloud security architecture |
| A.5.31 | Legal requirements | Compliance documentation |

### A.8 Technological Controls

| Control | Title | Architecture Implementation |
|---------|-------|---------------------------|
| A.8.1 | User endpoint devices | Client security policies |
| A.8.2 | Privileged access rights | Admin roles, MFA for admins |
| A.8.3 | Information access restriction | Row-level security, ABAC |
| A.8.4 | Access to source code | Git access controls |
| A.8.5 | Secure authentication | OAuth2, JWT, MFA |
| A.8.6 | Capacity management | Auto-scaling, monitoring |
| A.8.7 | Protection against malware | Dependency scanning |
| A.8.8 | Management of technical vulnerabilities | SAST, DAST, patching |
| A.8.9 | Configuration management | IaC, security baselines |
| A.8.10 | Information deletion | Data retention policies |
| A.8.11 | Data masking | PII masking, anonymization |
| A.8.12 | Data leakage prevention | DLP policies, egress filtering |
| A.8.15 | Logging | Centralized audit logging |
| A.8.16 | Monitoring activities | SIEM, alerting |
| A.8.20 | Networks security | VPC, firewalls, WAF |
| A.8.21 | Security of network services | TLS, API security |
| A.8.24 | Use of cryptography | Encryption standards |
| A.8.25 | Secure development life cycle | Secure SDLC practices |
| A.8.26 | Application security requirements | Security in specs |
| A.8.27 | Secure system architecture | Defense in depth |
| A.8.28 | Secure coding | Code review, SAST |
| A.8.29 | Security testing | DAST, penetration testing |
| A.8.31 | Separation of environments | Dev/staging/prod isolation |
| A.8.32 | Change management | CI/CD, change control |
| A.8.33 | Test information | Test data management |
| A.8.34 | Audit system protection | Tamper-proof logs |

---

## A.5.12 Information Classification Architecture

### Classification Levels

```typescript
// ISO 27001 A.5.12 - Information Classification
enum DataClassification {
  // Level 1: Public
  PUBLIC = 'public',
  // Can be freely shared
  // No special handling required
  // Example: Marketing content, public docs

  // Level 2: Internal
  INTERNAL = 'internal',
  // For internal use only
  // Basic access controls
  // Example: Internal policies, procedures

  // Level 3: Confidential
  CONFIDENTIAL = 'confidential',
  // Restricted to authorized personnel
  // Encryption at rest required
  // Example: Financial data, contracts

  // Level 4: Restricted
  RESTRICTED = 'restricted',
  // Highest sensitivity
  // Field-level encryption, MFA required
  // Example: PII, health data, credentials
}
```

### Classification Handling Matrix

| Classification | Encryption at Rest | Encryption in Transit | Access Control | Audit | Retention | Disposal |
|---------------|-------------------|----------------------|----------------|-------|-----------|----------|
| PUBLIC | Optional | TLS | None | Basic | Standard | Standard |
| INTERNAL | Optional | TLS | Role-based | Basic | Standard | Standard |
| CONFIDENTIAL | Required (AES-256) | TLS 1.3 | Need-to-know | Full | Policy-based | Secure delete |
| RESTRICTED | Field-level + at rest | TLS 1.3 + mTLS | MFA + need-to-know | Full + alert | Regulated | Crypto-shred |

### Database Implementation

```sql
-- A.5.12: Classification column on sensitive tables
ALTER TABLE documents ADD COLUMN classification VARCHAR(20)
    DEFAULT 'internal'
    CHECK (classification IN ('public', 'internal', 'confidential', 'restricted'));

-- A.5.13: Classification labels in metadata
CREATE TABLE data_labels (
    id UUID PRIMARY KEY,
    resource_type VARCHAR(50) NOT NULL,
    resource_id UUID NOT NULL,
    classification VARCHAR(20) NOT NULL,
    handling_instructions TEXT,
    labeled_at TIMESTAMPTZ DEFAULT NOW(),
    labeled_by UUID REFERENCES users(id),

    UNIQUE(resource_type, resource_id)
);
```

---

## A.5.15-18 Access Control Architecture

### A.5.15 Access Control Policy

```
┌─────────────────────────────────────────────────────────────────┐
│               ACCESS CONTROL ARCHITECTURE                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                  Policy Decision Point                   │   │
│  │  • Evaluate access request                              │   │
│  │  • Apply RBAC rules                                     │   │
│  │  • Apply ABAC rules (if needed)                         │   │
│  │  • Return allow/deny                                    │   │
│  └─────────────────────────┬───────────────────────────────┘   │
│                            │                                    │
│                            ▼                                    │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                 Policy Enforcement Points                │   │
│  │                                                         │   │
│  │  ┌───────────┐  ┌───────────┐  ┌───────────┐          │   │
│  │  │    API    │  │   App     │  │  Database │          │   │
│  │  │  Gateway  │  │  Layer    │  │   (RLS)   │          │   │
│  │  └───────────┘  └───────────┘  └───────────┘          │   │
│  │                                                         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### A.5.16 Identity Management

```typescript
// User lifecycle management
interface UserIdentity {
  id: string;
  email: string;
  status: 'active' | 'suspended' | 'deprovisioned';

  // A.5.17: Authentication
  authentication: {
    passwordHash: string;
    mfaEnabled: boolean;
    mfaMethod?: 'totp' | 'sms' | 'webauthn';
    lastPasswordChange: Date;
    passwordExpiresAt?: Date;
  };

  // A.5.18: Access rights
  accessRights: {
    roles: string[];
    permissions: string[];
    tenantId: string;
    effectiveFrom: Date;
    effectiveUntil?: Date;
  };

  // Audit trail
  createdAt: Date;
  createdBy: string;
  lastModifiedAt: Date;
  lastModifiedBy: string;
}

// User provisioning workflow
async function provisionUser(request: ProvisionRequest): Promise<void> {
  // 1. Create identity
  const user = await createUser(request);

  // 2. Assign default role
  await assignRole(user.id, 'viewer');

  // 3. Send activation email
  await sendActivationEmail(user.email);

  // 4. Audit log
  await auditLog('USER_PROVISIONED', { userId: user.id, by: request.requestedBy });
}

// User deprovisioning workflow
async function deprovisionUser(userId: string, reason: string): Promise<void> {
  // 1. Revoke all sessions
  await revokeAllSessions(userId);

  // 2. Remove all roles
  await removeAllRoles(userId);

  // 3. Mark as deprovisioned (don't delete for audit)
  await updateUser(userId, { status: 'deprovisioned' });

  // 4. Audit log
  await auditLog('USER_DEPROVISIONED', { userId, reason });
}
```

### A.5.17 Password Policy

```typescript
const PASSWORD_POLICY = {
  // A.5.17: Authentication information management
  minLength: 12,
  requireUppercase: true,
  requireLowercase: true,
  requireNumbers: true,
  requireSpecialChars: true,
  maxAge: 90, // days
  historyCount: 12, // cannot reuse last 12 passwords
  maxLoginAttempts: 5,
  lockoutDuration: 15, // minutes
};

// MFA requirements
const MFA_POLICY = {
  requiredForRoles: ['admin', 'super_admin'],
  requiredForActions: ['delete_user', 'change_settings', 'export_data'],
  requiredForClassification: ['restricted'],
  gracePeriod: 7, // days to enable MFA after account creation
};
```

---

## A.8.5 Secure Authentication Architecture

### Authentication Flow

```
┌─────────────────────────────────────────────────────────────────┐
│              A.8.5 SECURE AUTHENTICATION                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Step 1: Primary Authentication                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  • Username/Password                                       │ │
│  │  • OAuth2/OIDC (preferred)                                 │ │
│  │  • API Key (for services)                                  │ │
│  └───────────────────────────────────────────────────────────┘ │
│                           │                                     │
│                           ▼                                     │
│  Step 2: Risk Assessment                                        │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  • New device? → Require MFA                              │ │
│  │  • New location? → Require MFA                            │ │
│  │  • Suspicious pattern? → Block or MFA                     │ │
│  │  • Privileged action? → Require MFA                       │ │
│  └───────────────────────────────────────────────────────────┘ │
│                           │                                     │
│                           ▼                                     │
│  Step 3: Multi-Factor Authentication (if required)              │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  • TOTP (authenticator app) - preferred                   │ │
│  │  • WebAuthn/FIDO2 (hardware key) - most secure            │ │
│  │  • SMS OTP - fallback only                                │ │
│  └───────────────────────────────────────────────────────────┘ │
│                           │                                     │
│                           ▼                                     │
│  Step 4: Session Creation                                       │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  • Issue short-lived access token (15 min)                │ │
│  │  • Issue refresh token (7 days, rotatable)                │ │
│  │  • Log authentication event                               │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## A.8.15-16 Logging and Monitoring Architecture

### A.8.15 Audit Log Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                 A.8.15 LOGGING ARCHITECTURE                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │ Application │  │  Database   │  │   Network   │             │
│  │    Logs     │  │   Audit     │  │    Logs     │             │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘             │
│         │                │                │                     │
│         └────────────────┼────────────────┘                     │
│                          ▼                                      │
│              ┌───────────────────────┐                          │
│              │    Log Aggregator     │                          │
│              │  (CloudWatch/Datadog) │                          │
│              └───────────┬───────────┘                          │
│                          │                                      │
│         ┌────────────────┼────────────────┐                     │
│         ▼                ▼                ▼                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │   Archive   │  │    SIEM     │  │  Alerting   │             │
│  │ (S3 Glacier)│  │  Analysis   │  │             │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
│                                                                 │
│  A.8.34: Logs are write-once, tamper-evident                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Required Log Events

| Category | Events | Retention | A.8.15 Requirement |
|----------|--------|-----------|-------------------|
| Authentication | login, logout, mfa, password_change | 2 years | Security event |
| Authorization | access_granted, access_denied, role_change | 2 years | Security event |
| Data Access | read, export (confidential+) | 1 year | User activity |
| Data Modification | create, update, delete | 7 years | Audit trail |
| Admin Actions | user_mgmt, config_change, key_rotation | 7 years | Privileged activity |
| Security Incidents | block, alert, breach_attempt | 2 years | Incident response |

### A.8.16 Monitoring Alerts

```typescript
const SECURITY_MONITORING = {
  // A.8.16: Security event monitoring
  alerts: {
    BRUTE_FORCE: {
      condition: 'failed_logins > 10 in 5 minutes for same IP',
      severity: 'high',
      action: 'block_ip_and_notify',
    },
    CREDENTIAL_STUFFING: {
      condition: 'failed_logins > 100 in 1 minute across users',
      severity: 'critical',
      action: 'enable_captcha_and_page_security',
    },
    PRIVILEGE_ESCALATION: {
      condition: 'role_change without approval workflow',
      severity: 'critical',
      action: 'rollback_and_investigate',
    },
    DATA_EXFILTRATION: {
      condition: 'export_data > normal_baseline * 5',
      severity: 'high',
      action: 'block_and_investigate',
    },
    CROSS_TENANT_ACCESS: {
      condition: 'any tenant_id mismatch',
      severity: 'critical',
      action: 'block_immediately_and_page',
    },
  },
};
```

---

## A.8.24 Cryptography Architecture

### Encryption Standards

| Use Case | Algorithm | Key Size | Notes |
|----------|-----------|----------|-------|
| Symmetric encryption | AES-256-GCM | 256-bit | Data encryption |
| Asymmetric encryption | RSA | 4096-bit | Key exchange |
| Digital signatures | ECDSA | P-384 | JWT signing (RS256 acceptable) |
| Hashing | SHA-256/SHA-384 | N/A | Integrity checks |
| Password hashing | bcrypt/Argon2 | Work factor 12+ | Never use MD5/SHA1 |
| TLS | TLS 1.3 | N/A | TLS 1.2 minimum |

### Key Management

```
┌─────────────────────────────────────────────────────────────────┐
│              A.8.24 KEY MANAGEMENT ARCHITECTURE                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │                    AWS KMS / HashiCorp Vault               │ │
│  │                                                           │ │
│  │  Master Key (CMK)                                         │ │
│  │  └─► Data Encryption Keys (DEK)                           │ │
│  │       └─► Encrypted data                                  │ │
│  │                                                           │ │
│  │  Key Rotation:                                            │ │
│  │  • Master keys: Annual                                    │ │
│  │  • Data keys: On-demand (envelope encryption)             │ │
│  │  • API keys: 90 days                                      │ │
│  │  • JWT signing keys: 30 days                              │ │
│  │                                                           │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  Key Access:                                                    │
│  • Least privilege IAM policies                                │
│  • Audit all key usage                                         │
│  • No human access to production keys                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## A.8.25-28 Secure Development Architecture

### A.8.25 Secure SDLC

```
┌─────────────────────────────────────────────────────────────────┐
│               SECURE DEVELOPMENT LIFECYCLE                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. Requirements (A.8.26)                                       │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  • Security requirements in PRD                           │ │
│  │  • Threat modeling for new features                       │ │
│  │  • Data classification identified                         │ │
│  └───────────────────────────────────────────────────────────┘ │
│                           │                                     │
│                           ▼                                     │
│  2. Design (A.8.27)                                             │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  • Security architecture review                           │ │
│  │  • Tech spec includes security controls                   │ │
│  │  • Defense in depth design                                │ │
│  └───────────────────────────────────────────────────────────┘ │
│                           │                                     │
│                           ▼                                     │
│  3. Development (A.8.28)                                        │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  • Secure coding standards                                │ │
│  │  • Pre-commit hooks (secrets detection)                   │ │
│  │  • Code review for security                               │ │
│  └───────────────────────────────────────────────────────────┘ │
│                           │                                     │
│                           ▼                                     │
│  4. Testing (A.8.29)                                            │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  • SAST (static analysis)                                 │ │
│  │  • Dependency scanning                                    │ │
│  │  • DAST (dynamic analysis)                                │ │
│  │  • Security unit tests                                    │ │
│  └───────────────────────────────────────────────────────────┘ │
│                           │                                     │
│                           ▼                                     │
│  5. Deployment (A.8.32)                                         │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  • Container scanning                                     │ │
│  │  • Infrastructure validation                              │ │
│  │  • Change approval workflow                               │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### CI/CD Security Pipeline

```yaml
# A.8.28, A.8.29: Security in CI/CD
security-checks:
  stages:
    - pre-commit:
        - secrets-detection # gitleaks
        - lint-security # eslint-security

    - build:
        - sast # SonarQube, Semgrep
        - dependency-scan # Snyk, npm audit
        - container-scan # Trivy

    - test:
        - security-unit-tests
        - auth-bypass-tests
        - authz-tests

    - pre-deploy:
        - dast # OWASP ZAP
        - infrastructure-scan # tfsec

    - deploy:
        - require-approval # For production
        - audit-log # Record deployment
```

---

## A.8.31 Environment Separation

```
┌─────────────────────────────────────────────────────────────────┐
│               A.8.31 ENVIRONMENT SEPARATION                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │ Development │  │   Staging   │  │ Production  │             │
│  ├─────────────┤  ├─────────────┤  ├─────────────┤             │
│  │ • Fake data │  │ • Anonymized│  │ • Real data │             │
│  │ • No PII    │  │   data      │  │ • Full audit│             │
│  │ • Relaxed   │  │ • Prod-like │  │ • Strict    │             │
│  │   security  │  │   security  │  │   security  │             │
│  │ • Dev creds │  │ • Separate  │  │ • Prod creds│             │
│  │             │  │   creds     │  │             │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
│                                                                 │
│  Network Isolation:                                             │
│  • Separate VPCs per environment                               │
│  • No cross-environment network access                         │
│  • Separate AWS accounts (recommended)                         │
│                                                                 │
│  Data Isolation:                                                │
│  • Production data NEVER in dev/staging                        │
│  • Use synthetic/anonymized data for testing                   │
│  • Separate databases per environment                          │
│                                                                 │
│  Access Control:                                                │
│  • Developers: dev + staging                                   │
│  • DevOps: all environments                                    │
│  • Production: restricted, with MFA + approval                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## ISO 27001 Compliance Checklist for Tech Specs

### Before Tech Spec Approval

```markdown
## ISO 27001 Compliance Review

### A.5 Organizational Controls
- [ ] A.5.12: Data classification defined for all data elements
- [ ] A.5.13: Classification labels implemented
- [ ] A.5.15: Access control policy documented

### A.8 Technological Controls
- [ ] A.8.3: Row-level security implemented (if multi-tenant)
- [ ] A.8.5: Authentication method specified
- [ ] A.8.8: Vulnerability scanning in CI/CD
- [ ] A.8.9: Configuration managed via IaC
- [ ] A.8.11: Data masking for PII in non-prod
- [ ] A.8.15: Audit logging implemented
- [ ] A.8.16: Security monitoring alerts defined
- [ ] A.8.24: Encryption standards specified
- [ ] A.8.26: Security requirements documented
- [ ] A.8.27: Defense in depth architecture
- [ ] A.8.28: Secure coding practices followed
- [ ] A.8.29: Security testing planned
- [ ] A.8.31: Environment separation verified

### Sign-off
- [ ] Security team reviewed
- [ ] Compliance team approved
- [ ] All controls addressed or exceptions documented
```

---

## References

- [ISO 27001:2022 Standard](https://www.iso.org/standard/27001)
- [ISO 27002:2022 Controls Guidance](https://www.iso.org/standard/75652.html)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [CIS Controls](https://www.cisecurity.org/controls)
