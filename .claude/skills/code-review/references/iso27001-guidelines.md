# ISO 27001 Guidelines for Code Projects

Security controls and best practices aligned with ISO 27001 for organized, secure development.

---

## Overview

ISO 27001 is the international standard for Information Security Management Systems (ISMS). These guidelines map ISO 27001 controls to practical code project organization.

---

## A.8 Asset Management

### A.8.1 Inventory of Assets

**Requirement:** Maintain inventory of all information assets.

```
project/
├── ASSETS.md                    # Document all assets
├── docs/
│   ├── architecture.md          # System architecture
│   ├── data-flow.md             # Data flow diagrams
│   └── third-party-services.md  # External dependencies
└── package.json                 # Dependency inventory
```

**Checklist:**
- [ ] All third-party dependencies documented
- [ ] External APIs and services listed
- [ ] Data stores and their purposes documented
- [ ] License compliance tracked

### A.8.2 Classification of Information

**Requirement:** Classify information by sensitivity.

```typescript
// Define data classification levels
enum DataClassification {
  PUBLIC = 'public',           // Can be shared freely
  INTERNAL = 'internal',       // Internal use only
  CONFIDENTIAL = 'confidential', // Limited access
  RESTRICTED = 'restricted'    // Highly sensitive (PII, credentials)
}

// Document in code
interface UserData {
  id: string;                  // INTERNAL
  email: string;               // CONFIDENTIAL - PII
  passwordHash: string;        // RESTRICTED - never log
  publicProfile: object;       // PUBLIC
}
```

**Project Structure:**
```
src/
├── public/          # Public assets, no sensitive data
├── internal/        # Internal business logic
├── confidential/    # PII handling, requires audit
└── restricted/      # Crypto, auth, secrets handling
```

---

## A.9 Access Control

### A.9.1 Access Control Policy

**Requirement:** Restrict access based on business needs.

**Repository Access:**
```yaml
# .github/CODEOWNERS
# Define who can approve changes to sensitive areas

# Security-critical code requires security team review
/src/auth/           @security-team
/src/crypto/         @security-team
/src/api/middleware/ @security-team @backend-team

# Infrastructure requires DevOps approval
/infra/              @devops-team
/.github/workflows/  @devops-team

# Database schemas require DBA review
/migrations/         @dba-team @backend-team
```

**Environment Access:**
```
Production:  Security team + Senior devs only
Staging:     All developers (read), DevOps (write)
Development: All developers
```

### A.9.2 Secure Authentication

**Requirement:** Implement secure authentication mechanisms.

```typescript
// Authentication checklist in code
const authConfig = {
  // Password requirements
  password: {
    minLength: 12,
    requireUppercase: true,
    requireLowercase: true,
    requireNumbers: true,
    requireSymbols: true,
    preventCommon: true,      // Check against breached passwords
    maxAge: 90 * 24 * 60 * 60 // 90 days
  },

  // Session management
  session: {
    maxAge: 8 * 60 * 60,      // 8 hours
    renewalThreshold: 30 * 60, // Renew if < 30 min left
    absoluteTimeout: 24 * 60 * 60, // Force re-auth after 24h
    secureCookie: true,
    httpOnly: true,
    sameSite: 'strict'
  },

  // MFA
  mfa: {
    required: ['admin', 'finance'], // Required for these roles
    methods: ['totp', 'webauthn'],
    backupCodes: 10
  },

  // Lockout
  lockout: {
    maxAttempts: 5,
    duration: 15 * 60,        // 15 minutes
    notifyUser: true
  }
};
```

### A.9.4 System Access Control

**Requirement:** Secure access to systems and applications.

**API Security:**
```typescript
// Rate limiting
const rateLimits = {
  public: { window: '15m', max: 100 },
  authenticated: { window: '15m', max: 1000 },
  admin: { window: '15m', max: 5000 }
};

// Authorization middleware pattern
const authorize = (requiredPermissions: string[]) => {
  return (req, res, next) => {
    // 1. Verify authentication
    if (!req.user) {
      return res.status(401).json({ error: 'Authentication required' });
    }

    // 2. Check permissions
    const hasPermission = requiredPermissions.every(
      perm => req.user.permissions.includes(perm)
    );

    if (!hasPermission) {
      // Log unauthorized access attempt
      auditLog.warn('Unauthorized access attempt', {
        userId: req.user.id,
        resource: req.path,
        required: requiredPermissions,
        actual: req.user.permissions
      });
      return res.status(403).json({ error: 'Insufficient permissions' });
    }

    next();
  };
};
```

---

## A.12 Operations Security

### A.12.1 Documented Operating Procedures

**Requirement:** Document all operational procedures.

**Required Documentation:**
```
docs/
├── operations/
│   ├── deployment.md          # Deployment procedures
│   ├── rollback.md            # Rollback procedures
│   ├── incident-response.md   # Incident handling
│   ├── backup-restore.md      # Backup procedures
│   └── monitoring.md          # Monitoring setup
├── runbooks/
│   ├── database-failover.md
│   ├── service-restart.md
│   └── security-incident.md
└── README.md                  # Getting started
```

### A.12.2 Change Management

**Requirement:** Control changes to systems.

**Git Workflow:**
```
main (protected)
  │
  ├── develop (protected)
  │     │
  │     ├── feature/ABC-123-description
  │     ├── bugfix/ABC-456-description
  │     └── hotfix/ABC-789-critical-fix
  │
  └── release/v1.2.0
```

**Branch Protection Rules:**
```yaml
# Required for main and develop branches
protection_rules:
  main:
    required_reviews: 2
    required_checks:
      - build
      - test
      - security-scan
      - lint
    dismiss_stale_reviews: true
    require_code_owner_review: true
    restrict_push: [release-managers]

  develop:
    required_reviews: 1
    required_checks:
      - build
      - test
      - lint
```

**Commit Message Standard:**
```
<type>(<scope>): <subject>

<body>

<footer>

Types: feat, fix, docs, style, refactor, test, chore, security
Scope: component or module affected
Footer: Issue references, breaking changes

Example:
security(auth): implement rate limiting on login endpoint

Added rate limiting to prevent brute force attacks.
- 5 attempts per 15 minutes per IP
- Account lockout after 10 failed attempts
- Notification sent to user on lockout

Fixes: SEC-123
Reviewed-by: @security-team
```

### A.12.3 Capacity Management

**Requirement:** Monitor and plan for capacity needs.

```typescript
// Resource monitoring configuration
const monitoring = {
  metrics: {
    cpu: { warning: 70, critical: 90 },
    memory: { warning: 75, critical: 90 },
    disk: { warning: 80, critical: 95 },
    connections: { warning: 80, critical: 95 }
  },

  alerts: {
    channels: ['slack', 'pagerduty'],
    escalation: {
      warning: { delay: '5m', notify: ['on-call'] },
      critical: { delay: '0', notify: ['on-call', 'manager'] }
    }
  }
};
```

### A.12.4 Separation of Environments

**Requirement:** Separate development, testing, and production.

```
environments/
├── development/
│   ├── .env.development
│   └── config.development.yaml
├── staging/
│   ├── .env.staging
│   └── config.staging.yaml
└── production/
    ├── .env.production        # Template only, actual in vault
    └── config.production.yaml
```

**Environment Rules:**
| Environment | Data | Access | Deployment |
|-------------|------|--------|------------|
| Development | Synthetic/Mock | All devs | Manual |
| Staging | Anonymized prod copy | All devs | Auto on develop merge |
| Production | Real data | Restricted | Manual approval required |

### A.12.6 Logging and Monitoring

**Requirement:** Log events and monitor for anomalies.

```typescript
// Structured logging standard
interface AuditLog {
  timestamp: string;        // ISO 8601
  level: 'info' | 'warn' | 'error' | 'security';
  event: string;            // Event type
  actor: {
    id: string;
    type: 'user' | 'system' | 'api';
    ip?: string;
  };
  resource: {
    type: string;
    id: string;
  };
  action: string;           // CRUD operation
  outcome: 'success' | 'failure';
  details: object;          // Additional context
}

// Required audit events
const auditableEvents = [
  'auth.login',
  'auth.logout',
  'auth.failed',
  'auth.mfa_enabled',
  'user.created',
  'user.deleted',
  'user.role_changed',
  'user.permissions_changed',
  'data.exported',
  'data.bulk_deleted',
  'admin.config_changed',
  'security.alert'
];

// Log retention policy
const retention = {
  security: '7 years',      // Security events
  audit: '3 years',         // Audit trail
  application: '1 year',    // App logs
  debug: '30 days'          // Debug logs
};
```

---

## A.14 System Development Security

### A.14.1 Security Requirements

**Requirement:** Include security in all development phases.

**Security Requirements Checklist:**
```markdown
## Feature: [Feature Name]

### Security Requirements
- [ ] Authentication: What auth is required?
- [ ] Authorization: What roles/permissions?
- [ ] Data classification: What data is handled?
- [ ] Input validation: What inputs are accepted?
- [ ] Output encoding: How is output sanitized?
- [ ] Logging: What events are logged?
- [ ] Rate limiting: What limits apply?

### Threat Model
- [ ] What can go wrong? (STRIDE analysis)
- [ ] What are we doing about it?
- [ ] What are we accepting as risk?

### Security Tests
- [ ] Unit tests for security controls
- [ ] Integration tests for auth/authz
- [ ] Penetration test requirements
```

### A.14.2 Secure Development Environment

**Requirement:** Establish secure development practices.

**Pre-commit Hooks:**
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    hooks:
      - id: detect-private-key
      - id: detect-aws-credentials
      - id: check-added-large-files

  - repo: https://github.com/zricethezav/gitleaks
    hooks:
      - id: gitleaks        # Scan for secrets

  - repo: local
    hooks:
      - id: npm-audit
        name: npm audit
        entry: npm audit --audit-level=high
        language: system
        pass_filenames: false
```

**IDE Security Extensions:**
```json
// .vscode/extensions.json
{
  "recommendations": [
    "snyk-security.snyk-vulnerability-scanner",
    "streetsidesoftware.code-spell-checker",
    "sonarsource.sonarlint-vscode",
    "redhat.vscode-yaml"
  ]
}
```

### A.14.2.8 System Security Testing

**Requirement:** Test security throughout development.

**Security Testing Pipeline:**
```yaml
# CI/CD security stages
security_pipeline:
  stages:
    - name: SAST (Static Analysis)
      tools: [semgrep, eslint-security, sonarqube]
      fail_on: high, critical

    - name: Dependency Scan
      tools: [npm-audit, snyk, dependabot]
      fail_on: high, critical

    - name: Secret Scan
      tools: [gitleaks, trufflehog]
      fail_on: any

    - name: Container Scan
      tools: [trivy, clair]
      fail_on: high, critical

    - name: DAST (Dynamic Analysis)
      tools: [owasp-zap, burp]
      environment: staging
      schedule: weekly

    - name: Penetration Test
      frequency: quarterly
      scope: full_application
```

---

## A.18 Compliance

### A.18.1 Legal and Regulatory Requirements

**Requirement:** Identify and document compliance requirements.

**Compliance Documentation:**
```
compliance/
├── requirements/
│   ├── gdpr.md              # GDPR requirements
│   ├── pci-dss.md           # PCI DSS (if handling payments)
│   ├── hipaa.md             # HIPAA (if handling health data)
│   └── sox.md               # SOX (if financial reporting)
├── controls/
│   ├── data-protection.md   # How we protect data
│   ├── access-control.md    # How we control access
│   └── audit-logging.md     # How we audit
└── evidence/
    ├── security-tests/      # Test results
    ├── audit-reports/       # Audit findings
    └── certifications/      # Compliance certs
```

### A.18.2 Information Security Reviews

**Requirement:** Regularly review security posture.

**Review Schedule:**
| Review Type | Frequency | Owner |
|-------------|-----------|-------|
| Code review (security) | Every PR | Dev team |
| Dependency audit | Weekly | Automated |
| Access review | Quarterly | Security team |
| Penetration test | Annually | External |
| Policy review | Annually | CISO |
| Risk assessment | Annually | Security team |

---

## Project Organization Checklist

### Repository Structure
```
project/
├── .github/
│   ├── CODEOWNERS           # Access control
│   ├── SECURITY.md          # Security policy
│   ├── workflows/           # CI/CD pipelines
│   └── PULL_REQUEST_TEMPLATE.md
├── docs/
│   ├── architecture/        # System design
│   ├── operations/          # Runbooks
│   ├── security/            # Security docs
│   └── compliance/          # Compliance evidence
├── src/
│   └── [organized by feature or layer]
├── tests/
│   ├── unit/
│   ├── integration/
│   └── security/            # Security-specific tests
├── scripts/
│   └── security/            # Security automation
├── .env.example             # Environment template (no secrets!)
├── .gitignore               # Exclude sensitive files
├── .pre-commit-config.yaml  # Pre-commit hooks
├── CHANGELOG.md             # Change history
├── LICENSE
└── README.md
```

### Files That Must Exist
- [ ] `SECURITY.md` - Security policy and reporting
- [ ] `CODEOWNERS` - Code ownership for reviews
- [ ] `.gitignore` - Excludes secrets, logs, etc.
- [ ] `.env.example` - Template without real values
- [ ] `docs/security/` - Security documentation

### Files That Must NOT Exist in Repo
- [ ] `.env` with real credentials
- [ ] Private keys (`*.pem`, `*.key`)
- [ ] Certificates (except public)
- [ ] Database dumps
- [ ] Log files
- [ ] Credentials files

---

## Quick Reference: ISO 27001 Controls for Code Review

| Control | Check During Review |
|---------|---------------------|
| A.8.1 Asset Management | Dependencies documented? |
| A.8.2 Classification | Data sensitivity marked? |
| A.9.2 Authentication | Secure auth implemented? |
| A.9.4 Access Control | Authorization checked? |
| A.12.2 Change Management | Proper PR process? |
| A.12.6 Logging | Audit events logged? |
| A.14.2 Secure Development | Security tests included? |
| A.18.1 Compliance | Regulatory requirements met? |
