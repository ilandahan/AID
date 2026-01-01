/**
 * @file crypto-utils.test.ts
 * @description Unit tests for crypto-utils module (SHA-256 and secure random)
 */

import { sha256, sha256Base64Url, secureRandom } from '../crypto-utils';

describe('SHA-256 Implementation', () => {
  describe('sha256', () => {
    it('should hash empty string correctly', () => {
      // SHA-256('') = e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
      const result = sha256('');
      expect(result).toBe('e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855');
    });

    it('should hash "hello" correctly', () => {
      // SHA-256('hello') = 2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824
      const result = sha256('hello');
      expect(result).toBe('2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824');
    });

    it('should hash "Hello World" correctly', () => {
      // SHA-256('Hello World') = a591a6d40bf420404a011733cfb7b190d62c65bf0bcda32b57b277d9ad9f146e
      const result = sha256('Hello World');
      expect(result).toBe('a591a6d40bf420404a011733cfb7b190d62c65bf0bcda32b57b277d9ad9f146e');
    });

    it('should hash long strings correctly', () => {
      // Test with a longer string
      const longString = 'The quick brown fox jumps over the lazy dog';
      // SHA-256 = d7a8fbb307d7809469ca9abcb0082e4f8d5651e46d3cdb762d02d0bf37c9e592
      const result = sha256(longString);
      expect(result).toBe('d7a8fbb307d7809469ca9abcb0082e4f8d5651e46d3cdb762d02d0bf37c9e592');
    });

    it('should handle Unicode characters', () => {
      // Test with Unicode
      const result = sha256('こんにちは');
      expect(result).toHaveLength(64); // SHA-256 produces 64 hex chars
      expect(result).toMatch(/^[0-9a-f]{64}$/);
    });

    it('should produce consistent results', () => {
      const input = 'test input for consistency';
      const result1 = sha256(input);
      const result2 = sha256(input);
      expect(result1).toBe(result2);
    });
  });

  describe('sha256Base64Url', () => {
    it('should return base64url encoded hash', () => {
      const result = sha256Base64Url('hello');
      // Should not contain +, /, or =
      expect(result).not.toContain('+');
      expect(result).not.toContain('/');
      expect(result).not.toContain('=');
    });

    it('should return correct length for PKCE challenge', () => {
      // Base64url of 32 bytes (256 bits) should be 43 characters
      const result = sha256Base64Url('test-verifier');
      expect(result.length).toBe(43);
    });

    it('should produce different outputs for different inputs', () => {
      const result1 = sha256Base64Url('input1');
      const result2 = sha256Base64Url('input2');
      expect(result1).not.toBe(result2);
    });
  });
});

describe('Secure Random', () => {
  describe('randomString', () => {
    it('should generate string of correct length', () => {
      const result = secureRandom.randomString(32);
      expect(result).toHaveLength(32);
    });

    it('should generate different strings on each call', () => {
      const results = new Set<string>();
      for (let i = 0; i < 100; i++) {
        results.add(secureRandom.randomString(16));
      }
      // All 100 should be unique (collision probability is negligible)
      expect(results.size).toBe(100);
    });

    it('should only contain alphanumeric characters by default', () => {
      const result = secureRandom.randomString(100);
      expect(result).toMatch(/^[A-Za-z0-9]+$/);
    });

    it('should use custom charset when provided', () => {
      const result = secureRandom.randomString(50, '0123456789');
      expect(result).toMatch(/^[0-9]+$/);
    });
  });

  describe('randomUrlSafe', () => {
    it('should generate URL-safe string', () => {
      const result = secureRandom.randomUrlSafe(64);
      // RFC 7636 unreserved characters: A-Z a-z 0-9 - . _ ~
      expect(result).toMatch(/^[A-Za-z0-9\-._~]+$/);
    });

    it('should generate correct length for PKCE verifier', () => {
      // PKCE requires 43-128 characters
      const result = secureRandom.randomUrlSafe(64);
      expect(result).toHaveLength(64);
      expect(result.length).toBeGreaterThanOrEqual(43);
      expect(result.length).toBeLessThanOrEqual(128);
    });
  });

  describe('randomInt', () => {
    it('should generate numbers within range', () => {
      for (let i = 0; i < 1000; i++) {
        const result = secureRandom.randomInt(10);
        expect(result).toBeGreaterThanOrEqual(0);
        expect(result).toBeLessThan(10);
      }
    });

    it('should have reasonable distribution', () => {
      const counts = new Array(10).fill(0);
      const iterations = 10000;

      for (let i = 0; i < iterations; i++) {
        const result = secureRandom.randomInt(10);
        counts[result]++;
      }

      // Each bucket should have roughly 10% of values (with some variance)
      const expected = iterations / 10;
      const tolerance = expected * 0.3; // 30% tolerance

      for (const count of counts) {
        expect(count).toBeGreaterThan(expected - tolerance);
        expect(count).toBeLessThan(expected + tolerance);
      }
    });
  });
});
