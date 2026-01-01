/**
 * @file setup.ts
 * @description Test setup and global configuration for Vitest.
 * Sets up environment variables and global mocks.
 */

import { beforeEach, afterEach, vi } from 'vitest';

// Set test environment variables
process.env.NODE_ENV = 'test';
process.env.JWT_SECRET = 'test-jwt-secret-256-bits-minimum-length-for-security';
process.env.SKIP_AUTH = 'false';

// Reset mocks between tests
beforeEach(() => {
  vi.clearAllMocks();
});

afterEach(() => {
  vi.restoreAllMocks();
});
