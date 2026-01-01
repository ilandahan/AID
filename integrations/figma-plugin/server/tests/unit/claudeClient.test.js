/**
 * @file claudeClient.test.js
 * @description Unit tests for Claude API client wrapper.
 * Tests availability check only - API calls require mocking at runtime.
 */

describe('ClaudeClient', () => {
  const originalEnv = process.env;

  beforeEach(() => {
    jest.resetModules();
    process.env = { ...originalEnv };
  });

  afterEach(() => {
    process.env = originalEnv;
  });

  // ============================================
  // isAvailable Tests
  // ============================================

  describe('isAvailable', () => {
    test('returns true when API key is set', () => {
      process.env.ANTHROPIC_API_KEY = 'sk-ant-api03-test-key';
      const claudeClient = require('../../src/utils/claudeClient');

      expect(claudeClient.isAvailable()).toBe(true);
    });

    test('returns false when API key is not set', () => {
      delete process.env.ANTHROPIC_API_KEY;
      const claudeClient = require('../../src/utils/claudeClient');

      expect(claudeClient.isAvailable()).toBe(false);
    });

    test('returns false when API key is empty string', () => {
      process.env.ANTHROPIC_API_KEY = '';
      const claudeClient = require('../../src/utils/claudeClient');

      expect(claudeClient.isAvailable()).toBe(false);
    });
  });

  // ============================================
  // generateMetadata Tests (without actual API call)
  // ============================================

  describe('generateMetadata error handling', () => {
    test('throws error when API key not set', async () => {
      delete process.env.ANTHROPIC_API_KEY;
      const claudeClient = require('../../src/utils/claudeClient');

      await expect(
        claudeClient.generateMetadata(
          { component: { name: 'Test' }, tokens: [], variants: [] },
          'SKILL'
        )
      ).rejects.toThrow('ANTHROPIC_API_KEY');
    });
  });
});
