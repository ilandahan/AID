# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability in AID, please report it responsibly:

### How to Report

1. **DO NOT** create a public GitHub issue for security vulnerabilities
2. Email the security team directly (or use GitHub's private security advisory feature)
3. Include detailed information about the vulnerability:
   - Type of vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

### What to Expect

- **Acknowledgment**: Within 48 hours
- **Initial Assessment**: Within 1 week
- **Resolution Timeline**: Depends on severity
  - Critical: 24-72 hours
  - High: 1 week
  - Medium: 2 weeks
  - Low: Next release cycle

## Security Best Practices for Contributors

### Code Security

Per the `code-review` and `security.md` rules:

- **Input Validation**: All user inputs must be validated using Zod schemas
- **SQL Injection**: Use parameterized queries (Prisma handles this)
- **XSS Prevention**: Never use `dangerouslySetInnerHTML` without sanitization
- **Authentication**: Store JWT in httpOnly cookies, never localStorage
- **Secrets**: Use environment variables, never hardcode credentials

### OWASP Top 10 Compliance

This project follows OWASP Top 10 security guidelines:

1. **Injection** - Parameterized queries via Prisma
2. **Broken Authentication** - bcrypt password hashing, JWT with short expiry
3. **Sensitive Data Exposure** - Encryption at rest and in transit
4. **XXE** - External entity processing disabled
5. **Broken Access Control** - Permission checks on all routes
6. **Security Misconfiguration** - Security headers configured
7. **XSS** - React auto-escaping, CSP headers
8. **Insecure Deserialization** - No eval() on user data
9. **Vulnerable Components** - Regular npm audit
10. **Insufficient Logging** - Auth events logged, secrets never logged

### Before Submitting Code

- [ ] Run `npm audit` to check for vulnerable dependencies
- [ ] Ensure no secrets are committed (check `.env.example` for patterns)
- [ ] Validate all user inputs with Zod schemas
- [ ] Check for OWASP Top 10 vulnerabilities
- [ ] Review authentication and authorization logic
- [ ] Test error messages don't leak sensitive info

### Environment Variables

**Never commit:**
- API keys
- Database credentials
- JWT secrets
- Encryption keys
- Personal access tokens

**Use `.env.example` as a template** - it should contain placeholder values only.

## Security Features

### Headers (Configured in next.config.js)

- `X-Frame-Options: DENY` - Prevents clickjacking
- `X-Content-Type-Options: nosniff` - Prevents MIME sniffing
- `Strict-Transport-Security` - Enforces HTTPS
- `Content-Security-Policy` - Prevents XSS and injection
- `Permissions-Policy` - Restricts browser features
- `Referrer-Policy` - Controls referrer information
- `X-XSS-Protection` - Additional XSS protection

### Authentication

- Passwords hashed with bcrypt (cost factor 12+)
- JWT tokens with short expiration (15 min access, refresh rotation)
- Rate limiting on auth endpoints
- Secure session management

### Data Protection

- Sensitive data encrypted at rest
- TLS for data in transit
- PII handling compliant with GDPR
- Audit logging for security events

### Development Security

- Pre-commit hooks for security checks
- Automated dependency scanning
- Code review requirements for security-sensitive changes

## Compliance

This project follows:
- **ISO 27001** security controls (see `system-architect` skill)
- **OWASP** secure coding guidelines (see `code-review` skill)
- **GDPR** data protection requirements (where applicable)

## Security Skills & Documentation

For detailed security guidance, see:
- `.claude/skills/code-review/` - Security review patterns
- `.claude/skills/system-architect/` - Security architecture
- `.claude/rules/security.md` - Security coding rules
- `skills/code-review/references/iso27001-guidelines.md`
- `skills/code-review/references/security-patterns.md`
- `skills/system-architect/references/security-architecture.md`

## Security Contacts

For security-related inquiries:
- Create a private security advisory on GitHub
- Or contact the maintainers directly

---

*This security policy is reviewed and updated regularly as part of the AID methodology.*
