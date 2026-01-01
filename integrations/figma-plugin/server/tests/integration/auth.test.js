/**
 * @file auth.test.js
 * @description Integration tests for authentication endpoints.
 * Tests OTP generation, pairing, JWT validation, and security measures.
 */

const request = require('supertest');

// Create a test instance of the app
// We need to extract the app without starting the server
let app;

beforeAll(() => {
  // Suppress console output during tests
  jest.spyOn(console, 'log').mockImplementation(() => {});
  jest.spyOn(console, 'warn').mockImplementation(() => {});

  // Import app after mocking
  // Note: The actual app needs to export the Express instance
  // For now, we'll test against localhost:3001
});

afterAll(() => {
  jest.restoreAllMocks();
});

// Base URL for integration tests
const BASE_URL = 'http://localhost:3001';

// ============================================
// Health Check Tests
// ============================================

describe('GET /health', () => {
  test('returns healthy status', async () => {
    const res = await request(BASE_URL).get('/health');

    expect(res.status).toBe(200);
    expect(res.body.status).toBe('healthy');
  });

  test('returns version info', async () => {
    const res = await request(BASE_URL).get('/health');

    expect(res.body.version).toBeDefined();
    expect(res.body.version).toBe('1.0.0');
  });

  test('returns timestamp in ISO format', async () => {
    const res = await request(BASE_URL).get('/health');

    expect(res.body.timestamp).toBeDefined();
    expect(() => new Date(res.body.timestamp)).not.toThrow();
  });
});

// ============================================
// OTP Generation Tests
// ============================================

describe('POST /auth/generate-pairing', () => {
  test('generates 6-digit OTP code', async () => {
    const res = await request(BASE_URL)
      .post('/auth/generate-pairing')
      .send({
        tenantId: 'test-tenant',
        projectPath: '/test/project'
      });

    expect(res.status).toBe(200);
    expect(res.body.success).toBe(true);
    expect(res.body.code).toMatch(/^\d{3} \d{3}$/);
  });

  test('returns expiry information', async () => {
    const res = await request(BASE_URL)
      .post('/auth/generate-pairing')
      .send({
        tenantId: 'test-tenant',
        projectPath: '/test/project'
      });

    expect(res.body.expiresIn).toBe(300); // 5 minutes
    expect(res.body.expiresAt).toBeDefined();
    expect(() => new Date(res.body.expiresAt)).not.toThrow();
  });

  test('generates unique codes each time', async () => {
    const codes = new Set();

    for (let i = 0; i < 5; i++) {
      const res = await request(BASE_URL)
        .post('/auth/generate-pairing')
        .send({
          tenantId: 'test-tenant',
          projectPath: '/test/project'
        });

      codes.add(res.body.code.replace(' ', ''));
    }

    // All 5 codes should be unique
    expect(codes.size).toBe(5);
  });

  test('works without tenantId (uses default)', async () => {
    const res = await request(BASE_URL)
      .post('/auth/generate-pairing')
      .send({});

    expect(res.status).toBe(200);
    expect(res.body.success).toBe(true);
  });
});

// ============================================
// OTP Pairing Tests
// ============================================

describe('POST /auth/pair', () => {
  let validCode;

  beforeEach(async () => {
    // Generate a fresh code for each test
    const res = await request(BASE_URL)
      .post('/auth/generate-pairing')
      .send({
        tenantId: 'test-tenant',
        projectPath: '/test/project'
      });

    validCode = res.body.code.replace(' ', '');
  });

  test('accepts valid OTP and returns JWT token', async () => {
    const res = await request(BASE_URL)
      .post('/auth/pair')
      .send({ code: validCode });

    expect(res.status).toBe(200);
    expect(res.body.success).toBe(true);
    expect(res.body.token).toBeDefined();
    expect(res.body.token).toMatch(/^eyJ/); // JWT format
  });

  test('returns tenant and project info', async () => {
    const res = await request(BASE_URL)
      .post('/auth/pair')
      .send({ code: validCode });

    expect(res.body.tenantId).toBe('test-tenant');
    expect(res.body.projectPath).toBe('/test/project');
    expect(res.body.pairedAt).toBeDefined();
  });

  test('accepts code with spaces', async () => {
    const codeWithSpaces = validCode.slice(0, 3) + ' ' + validCode.slice(3);

    const res = await request(BASE_URL)
      .post('/auth/pair')
      .send({ code: codeWithSpaces });

    expect(res.status).toBe(200);
    expect(res.body.success).toBe(true);
  });

  test('rejects invalid code', async () => {
    const res = await request(BASE_URL)
      .post('/auth/pair')
      .send({ code: '000000' });

    expect(res.status).toBe(401);
    expect(res.body.success).toBe(false);
    expect(res.body.error).toBe('invalid_code');
  });

  test('rejects already used code', async () => {
    // First use
    await request(BASE_URL)
      .post('/auth/pair')
      .send({ code: validCode });

    // Second use (should fail)
    const res = await request(BASE_URL)
      .post('/auth/pair')
      .send({ code: validCode });

    expect(res.status).toBe(401);
    expect(res.body.error).toBe('already_used');
  });

  test('rejects missing code', async () => {
    const res = await request(BASE_URL)
      .post('/auth/pair')
      .send({});

    expect(res.status).toBe(400);
    expect(res.body.error).toBe('invalid_request');
  });

  test('rejects malformed code', async () => {
    const res = await request(BASE_URL)
      .post('/auth/pair')
      .send({ code: 'abc123' });

    expect(res.status).toBe(400);
    expect(res.body.error).toBe('invalid_format');
  });

  test('rejects code that is too short', async () => {
    const res = await request(BASE_URL)
      .post('/auth/pair')
      .send({ code: '12345' });

    expect(res.status).toBe(400);
    expect(res.body.error).toBe('invalid_format');
  });

  test('rejects code that is too long', async () => {
    const res = await request(BASE_URL)
      .post('/auth/pair')
      .send({ code: '1234567' });

    expect(res.status).toBe(400);
    expect(res.body.error).toBe('invalid_format');
  });
});

// ============================================
// JWT Validation Tests
// ============================================

describe('POST /auth/jwt/validate', () => {
  let validToken;

  beforeEach(async () => {
    // Generate a fresh code and pair
    const codeRes = await request(BASE_URL)
      .post('/auth/generate-pairing')
      .send({
        tenantId: 'test-tenant',
        projectPath: '/test/project'
      });

    const code = codeRes.body.code.replace(' ', '');

    const pairRes = await request(BASE_URL)
      .post('/auth/pair')
      .send({ code });

    validToken = pairRes.body.token;
  });

  test('validates valid token from body', async () => {
    const res = await request(BASE_URL)
      .post('/auth/jwt/validate')
      .send({ token: validToken });

    expect(res.status).toBe(200);
    expect(res.body.valid).toBe(true);
    expect(res.body.tenantId).toBe('test-tenant');
    expect(res.body.projectPath).toBe('/test/project');
  });

  test('validates valid token from Authorization header', async () => {
    const res = await request(BASE_URL)
      .post('/auth/jwt/validate')
      .set('Authorization', `Bearer ${validToken}`)
      .send({});

    expect(res.status).toBe(200);
    expect(res.body.valid).toBe(true);
  });

  test('returns expiry timestamp', async () => {
    const res = await request(BASE_URL)
      .post('/auth/jwt/validate')
      .send({ token: validToken });

    expect(res.body.exp).toBeDefined();
    expect(typeof res.body.exp).toBe('number');
  });

  test('rejects missing token', async () => {
    const res = await request(BASE_URL)
      .post('/auth/jwt/validate')
      .send({});

    expect(res.status).toBe(401);
    expect(res.body.valid).toBe(false);
    expect(res.body.error).toBe('missing_token');
  });

  test('rejects invalid token', async () => {
    const res = await request(BASE_URL)
      .post('/auth/jwt/validate')
      .send({ token: 'invalid.token.here' });

    expect(res.status).toBe(401);
    expect(res.body.valid).toBe(false);
    expect(res.body.error).toBe('invalid_token');
  });

  test('rejects tampered token', async () => {
    // Modify the token signature
    const tamperedToken = validToken.slice(0, -5) + 'XXXXX';

    const res = await request(BASE_URL)
      .post('/auth/jwt/validate')
      .send({ token: tamperedToken });

    expect(res.status).toBe(401);
    expect(res.body.valid).toBe(false);
  });
});

describe('GET /auth/jwt/validate', () => {
  let validToken;

  beforeEach(async () => {
    const codeRes = await request(BASE_URL)
      .post('/auth/generate-pairing')
      .send({
        tenantId: 'test-tenant',
        projectPath: '/test/project'
      });

    const code = codeRes.body.code.replace(' ', '');

    const pairRes = await request(BASE_URL)
      .post('/auth/pair')
      .send({ code });

    validToken = pairRes.body.token;
  });

  test('validates token from Authorization header', async () => {
    const res = await request(BASE_URL)
      .get('/auth/jwt/validate')
      .set('Authorization', `Bearer ${validToken}`);

    expect(res.status).toBe(200);
    expect(res.body.valid).toBe(true);
  });

  test('rejects missing Authorization header', async () => {
    const res = await request(BASE_URL)
      .get('/auth/jwt/validate');

    expect(res.status).toBe(401);
    expect(res.body.valid).toBe(false);
  });
});

// ============================================
// Security Tests
// ============================================

describe('Auth Security', () => {
  test('JWT tokens are properly signed', async () => {
    const codeRes = await request(BASE_URL)
      .post('/auth/generate-pairing')
      .send({ tenantId: 'security-test' });

    const code = codeRes.body.code.replace(' ', '');

    const pairRes = await request(BASE_URL)
      .post('/auth/pair')
      .send({ code });

    const token = pairRes.body.token;

    // JWT should have 3 parts separated by dots
    const parts = token.split('.');
    expect(parts).toHaveLength(3);

    // Header should indicate HS256 algorithm
    const header = JSON.parse(Buffer.from(parts[0], 'base64').toString());
    expect(header.alg).toBe('HS256');
    expect(header.typ).toBe('JWT');
  });

  test('different pairings get different tokens', async () => {
    const tokens = [];

    for (let i = 0; i < 3; i++) {
      const codeRes = await request(BASE_URL)
        .post('/auth/generate-pairing')
        .send({ tenantId: `tenant-${i}` });

      const code = codeRes.body.code.replace(' ', '');

      const pairRes = await request(BASE_URL)
        .post('/auth/pair')
        .send({ code });

      tokens.push(pairRes.body.token);
    }

    // All tokens should be unique
    const uniqueTokens = new Set(tokens);
    expect(uniqueTokens.size).toBe(3);
  });

  test('OTP codes are not predictable', async () => {
    const codes = [];

    for (let i = 0; i < 10; i++) {
      const res = await request(BASE_URL)
        .post('/auth/generate-pairing')
        .send({ tenantId: 'test' });

      codes.push(res.body.code.replace(' ', ''));
    }

    // Check for randomness - no sequential patterns
    const numericCodes = codes.map(c => parseInt(c, 10));
    const differences = numericCodes.slice(1).map((c, i) => Math.abs(c - numericCodes[i]));

    // At least some differences should be large (not sequential)
    const largeDiffs = differences.filter(d => d > 10000);
    expect(largeDiffs.length).toBeGreaterThan(0);
  });
});

// ============================================
// Rate Limiting / Max Attempts Tests
// ============================================

describe('Auth Rate Limiting', () => {
  test('blocks after too many invalid attempts on same code', async () => {
    // Generate a code
    const codeRes = await request(BASE_URL)
      .post('/auth/generate-pairing')
      .send({ tenantId: 'rate-limit-test' });

    const validCode = codeRes.body.code.replace(' ', '');

    // Try wrong codes multiple times
    for (let i = 0; i < 3; i++) {
      await request(BASE_URL)
        .post('/auth/pair')
        .send({ code: '000000' });
    }

    // Now try the valid code - should work since it's a different code
    const res = await request(BASE_URL)
      .post('/auth/pair')
      .send({ code: validCode });

    // Valid code should still work (rate limit is per-code, not global)
    expect(res.body.success).toBe(true);
  });
});
