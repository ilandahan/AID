/**
 * @file aid-pairing.test.ts
 * @description Comprehensive tests for the AID pairing system.
 * Tests OTP generation, validation, expiry, and rate limiting.
 *
 * @related
 *   - ./aid-pairing.ts - Implementation under test
 *   - ./jwt-middleware.ts - JWT generation used by pairing
 */

import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';
import {
  generatePairingCode,
  validatePairingCode,
  getPairingStatus,
  formatPairingCodeMessage,
  revokeTenantCodes,
  clearPairingState,
} from './aid-pairing.js';

// Realistic test data matching production patterns
const testTenants = [
  {
    tenantId: 'tenant_abc123_prod',
    projectPath: 'C:\\Users\\Maria\\Projects\\design-system',
    description: 'Standard Windows path',
  },
  {
    tenantId: 'tenant_xyz789_staging',
    projectPath: '/home/dev/projects/acme-corp/frontend',
    description: 'Unix path with subdirectories',
  },
  {
    tenantId: 'org_李明_dev',
    projectPath: "C:\\Users\\O'Brien\\My Projects\\client-app",
    description: 'Unicode tenant ID and path with special chars',
  },
];

const testClientIps = [
  '127.0.0.1',
  '::1',
  '::ffff:127.0.0.1',
  '192.168.1.100',
  '2001:0db8:85a3:0000:0000:8a2e:0370:7334',
];

describe('AID Pairing System', () => {
  beforeEach(() => {
    // Clear all state between tests
    clearPairingState();
    vi.useFakeTimers();
  });

  afterEach(() => {
    clearPairingState();
    vi.useRealTimers();
  });

  describe('generatePairingCode', () => {
    it('generates a 6-digit numeric code', () => {
      const { tenantId, projectPath } = testTenants[0];

      const code = generatePairingCode(tenantId, projectPath);

      expect(code).toMatch(/^\d{6}$/);
      expect(parseInt(code)).toBeGreaterThanOrEqual(100000);
      expect(parseInt(code)).toBeLessThan(1000000);
    });

    it('generates unique codes for each call', () => {
      const { tenantId, projectPath } = testTenants[0];
      const codes = new Set<string>();

      // Generate 100 codes and check uniqueness
      for (let i = 0; i < 100; i++) {
        const code = generatePairingCode(tenantId, projectPath);
        codes.add(code);
      }

      // With 6 digits, collision in 100 codes is extremely unlikely
      expect(codes.size).toBeGreaterThanOrEqual(95);
    });

    it('handles unicode tenant IDs correctly', () => {
      const { tenantId, projectPath } = testTenants[2];

      const code = generatePairingCode(tenantId, projectPath);

      expect(code).toMatch(/^\d{6}$/);
      // Verify code can be validated
      const status = getPairingStatus(code);
      expect(status.valid).toBe(true);
    });

    it('handles paths with special characters', () => {
      const code = generatePairingCode('test_tenant', "C:\\Users\\Test's Path\\Project");

      expect(code).toMatch(/^\d{6}$/);
      const status = getPairingStatus(code);
      expect(status.valid).toBe(true);
    });
  });

  describe('validatePairingCode', () => {
    describe('successful validation', () => {
      it('returns JWT token for valid code', () => {
        const { tenantId, projectPath } = testTenants[0];
        const code = generatePairingCode(tenantId, projectPath);

        const result = validatePairingCode(code, '127.0.0.1');

        expect(result.success).toBe(true);
        expect(result.token).toBeDefined();
        expect(result.token).toMatch(/^eyJ/); // JWT format
        expect(result.tenantId).toBe(tenantId);
        expect(result.projectPath).toBe(projectPath);
        expect(result.error).toBeUndefined();
      });

      it('accepts validation from any IP address', () => {
        const { tenantId, projectPath } = testTenants[1];

        for (const clientIp of testClientIps) {
          const code = generatePairingCode(tenantId, projectPath);
          const result = validatePairingCode(code, clientIp);

          expect(result.success).toBe(true);
          expect(result.token).toBeDefined();
        }
      });
    });

    describe('code expiry', () => {
      it('rejects code after 5 minutes', () => {
        const { tenantId, projectPath } = testTenants[0];
        const code = generatePairingCode(tenantId, projectPath);

        // Advance time by 5 minutes + 1 second
        vi.advanceTimersByTime(5 * 60 * 1000 + 1000);

        const result = validatePairingCode(code, '127.0.0.1');

        expect(result.success).toBe(false);
        expect(result.error).toContain('expired');
        expect(result.token).toBeUndefined();
      });

      it('accepts code just before 5 minute expiry', () => {
        const { tenantId, projectPath } = testTenants[0];
        const code = generatePairingCode(tenantId, projectPath);

        // Advance time by 4 minutes 59 seconds
        vi.advanceTimersByTime(4 * 60 * 1000 + 59 * 1000);

        const result = validatePairingCode(code, '127.0.0.1');

        expect(result.success).toBe(true);
        expect(result.token).toBeDefined();
      });
    });

    describe('single-use enforcement', () => {
      it('rejects code after first successful use', () => {
        const { tenantId, projectPath } = testTenants[0];
        const code = generatePairingCode(tenantId, projectPath);

        // First use - should succeed
        const firstResult = validatePairingCode(code, '127.0.0.1');
        expect(firstResult.success).toBe(true);

        // Second use - should fail (code is deleted after use)
        const secondResult = validatePairingCode(code, '127.0.0.2'); // Different IP to avoid rate limit
        expect(secondResult.success).toBe(false);
        expect(secondResult.error).toContain('Invalid'); // Code no longer exists
      });
    });

    describe('invalid codes', () => {
      it('rejects non-existent code', () => {
        const result = validatePairingCode('999999', '10.0.1.1');

        expect(result.success).toBe(false);
        expect(result.error).toContain('Invalid');
      });

      it('rejects empty code', () => {
        const result = validatePairingCode('', '10.0.1.2');

        expect(result.success).toBe(false);
        expect(result.error).toContain('Invalid');
      });

      it('rejects non-numeric code', () => {
        const result = validatePairingCode('abc123', '10.0.1.3');

        expect(result.success).toBe(false);
        expect(result.error).toContain('Invalid');
      });

      it('rejects code with wrong length', () => {
        const result = validatePairingCode('12345', '10.0.1.4'); // 5 digits

        expect(result.success).toBe(false);
        expect(result.error).toContain('Invalid');
      });
    });

    describe('rate limiting', () => {
      it('allows up to 5 attempts per minute per IP', () => {
        const clientIp = '192.168.1.100';

        // Make 5 failed attempts - all should be processed
        for (let i = 0; i < 5; i++) {
          const result = validatePairingCode('000000', clientIp);
          expect(result.error).toContain('Invalid'); // Not rate limited
        }
      });

      it('blocks 6th attempt within same minute', () => {
        const clientIp = '192.168.1.101';

        // Make 5 attempts
        for (let i = 0; i < 5; i++) {
          validatePairingCode('000000', clientIp);
        }

        // 6th attempt should be rate limited
        const result = validatePairingCode('000000', clientIp);
        expect(result.success).toBe(false);
        expect(result.error).toContain('Too many attempts');
      });

      it('resets rate limit after 1 minute', () => {
        const clientIp = '192.168.1.102';

        // Exhaust rate limit
        for (let i = 0; i < 5; i++) {
          validatePairingCode('000000', clientIp);
        }

        // Verify blocked
        const blocked = validatePairingCode('000000', clientIp);
        expect(blocked.error).toContain('Too many attempts');

        // Wait 1 minute
        vi.advanceTimersByTime(60 * 1000 + 1);

        // Should work again (still invalid code, but not rate limited)
        const result = validatePairingCode('000000', clientIp);
        expect(result.error).toContain('Invalid'); // Not rate limited message
      });

      it('rate limits are per-IP', () => {
        // Exhaust rate limit for IP1
        for (let i = 0; i < 5; i++) {
          validatePairingCode('000000', '10.0.0.1');
        }

        // IP2 should still work
        const result = validatePairingCode('000000', '10.0.0.2');
        expect(result.error).toContain('Invalid'); // Not rate limited
      });
    });

    describe('attempt limiting per code', () => {
      it('tracks attempts per code', () => {
        const { tenantId, projectPath } = testTenants[0];
        const code = generatePairingCode(tenantId, projectPath);

        // Each validation call counts as an attempt
        // After MAX_ATTEMPTS (3), the code is invalidated
        validatePairingCode(code, '10.1.0.1');
        validatePairingCode(code, '10.1.0.2');
        validatePairingCode(code, '10.1.0.3');

        // 4th attempt - code should be deleted due to max attempts
        const result = validatePairingCode(code, '10.1.0.4');
        expect(result.success).toBe(false);
        // Code is now deleted, so it's "Invalid"
        expect(result.error).toBeDefined();
      });
    });
  });

  describe('getPairingStatus', () => {
    it('returns valid status for fresh code', () => {
      const code = generatePairingCode('tenant_123', '/path/to/project');

      const status = getPairingStatus(code);

      expect(status.valid).toBe(true);
      expect(status.expired).toBe(false);
      expect(status.used).toBe(false);
      expect(status.remainingSeconds).toBe(300); // 5 minutes
    });

    it('updates remaining seconds as time passes', () => {
      const code = generatePairingCode('tenant_123', '/path/to/project');

      // Wait 2 minutes
      vi.advanceTimersByTime(2 * 60 * 1000);

      const status = getPairingStatus(code);

      expect(status.valid).toBe(true);
      expect(status.remainingSeconds).toBe(180); // 3 minutes left
    });

    it('shows expired status after 5 minutes', () => {
      const code = generatePairingCode('tenant_123', '/path/to/project');

      vi.advanceTimersByTime(5 * 60 * 1000 + 1);

      const status = getPairingStatus(code);

      expect(status.valid).toBe(false);
      expect(status.expired).toBe(true);
      expect(status.remainingSeconds).toBe(0);
    });

    it('code is deleted after being consumed', () => {
      const code = generatePairingCode('tenant_123', '/path/to/project');
      const result = validatePairingCode(code, '10.5.0.1'); // Consume the code

      expect(result.success).toBe(true);

      // Code is deleted after successful use
      const status = getPairingStatus(code);
      expect(status.valid).toBe(false);
      expect(status.expired).toBe(true); // Non-existent codes show as expired
    });

    it('returns invalid status for non-existent code', () => {
      const status = getPairingStatus('000000');

      expect(status.valid).toBe(false);
      expect(status.expired).toBe(true);
      expect(status.remainingSeconds).toBe(0);
    });
  });

  describe('formatPairingCodeMessage', () => {
    it('formats English message correctly', () => {
      const message = formatPairingCodeMessage('123456', 'en');

      expect(message).toContain('123 456'); // Formatted code
      expect(message).toContain('AID PAIRING CODE');
      expect(message).toContain('5 minutes');
      expect(message).toContain('Single use only');
      expect(message).toContain('Figma');
    });

    it('formats Hebrew message correctly', () => {
      const message = formatPairingCodeMessage('654321', 'he');

      expect(message).toContain('654 321'); // Formatted code
      expect(message).toContain('קוד התחברות');
      expect(message).toContain('5 דקות');
      expect(message).toContain('חד פעמי');
    });

    it('handles all valid code formats', () => {
      const codes = ['000000', '999999', '123456', '654321'];

      for (const code of codes) {
        const message = formatPairingCodeMessage(code, 'en');
        expect(message).toContain(`${code.slice(0, 3)} ${code.slice(3)}`);
      }
    });
  });

  describe('revokeTenantCodes', () => {
    it('revokes all codes for a specific tenant', () => {
      const tenantId = 'tenant_to_revoke';

      // Generate multiple codes for the tenant
      const code1 = generatePairingCode(tenantId, '/path1');
      const code2 = generatePairingCode(tenantId, '/path2');
      const code3 = generatePairingCode(tenantId, '/path3');

      // Generate code for different tenant
      const otherCode = generatePairingCode('other_tenant', '/path');

      // Revoke
      const revokedCount = revokeTenantCodes(tenantId);

      expect(revokedCount).toBe(3);

      // Verify revoked codes are invalid
      expect(getPairingStatus(code1).valid).toBe(false);
      expect(getPairingStatus(code2).valid).toBe(false);
      expect(getPairingStatus(code3).valid).toBe(false);

      // Other tenant's code should still work
      expect(getPairingStatus(otherCode).valid).toBe(true);
    });

    it('returns 0 when no codes exist for tenant', () => {
      const count = revokeTenantCodes('non_existent_tenant');
      expect(count).toBe(0);
    });
  });
});
