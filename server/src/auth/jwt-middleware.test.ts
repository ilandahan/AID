/**
 * @file jwt-middleware.test.ts
 * @description Comprehensive tests for JWT authentication middleware.
 * Tests token validation, expiry, role checking, and error handling.
 *
 * @related
 *   - ./jwt-middleware.ts - Implementation under test
 *   - ./aid-pairing.ts - Uses generateToken from this module
 */

import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';
import type { Response, NextFunction } from 'express';
import jwt from 'jsonwebtoken';
import {
  jwtAuth,
  generateToken,
  verifyToken,
  requireRoles,
  type AuthenticatedRequest,
  type JWTPayload,
} from './jwt-middleware.js';

// Test JWT secret (must match setup.ts)
const TEST_SECRET = 'test-jwt-secret-256-bits-minimum-length-for-security';

// Realistic test data
const testUsers = [
  {
    sub: 'user_maria_garcia_001',
    tenantId: 'tenant_acme_corp_prod',
    email: 'maria.garcia@acme-corp.com',
    roles: ['designer', 'reviewer'],
  },
  {
    sub: 'figma-plugin-tenant_xyz_staging',
    tenantId: 'tenant_xyz_staging',
    roles: ['figma-plugin'],
  },
  {
    sub: 'admin_李明_system',
    tenantId: 'org_global_admin',
    email: 'admin@example.org',
    roles: ['admin', 'super-admin'],
  },
];

// Mock Express response
function createMockResponse(): Response {
  const res = {
    status: vi.fn().mockReturnThis(),
    json: vi.fn().mockReturnThis(),
  } as unknown as Response;
  return res;
}

// Mock Express next function
function createMockNext(): NextFunction {
  return vi.fn() as unknown as NextFunction;
}

describe('JWT Middleware', () => {
  beforeEach(() => {
    process.env.JWT_SECRET = TEST_SECRET;
    process.env.SKIP_AUTH = 'false';
    process.env.NODE_ENV = 'test';
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('generateToken', () => {
    it('generates valid JWT token with payload', () => {
      const payload = testUsers[0];

      const token = generateToken(payload);

      expect(token).toMatch(/^eyJ/); // JWT header
      expect(token.split('.')).toHaveLength(3); // Header.Payload.Signature
    });

    it('includes all payload fields in token', () => {
      const payload = testUsers[0];
      const token = generateToken(payload);

      const decoded = jwt.verify(token, TEST_SECRET) as JWTPayload;

      expect(decoded.sub).toBe(payload.sub);
      expect(decoded.tenantId).toBe(payload.tenantId);
      expect(decoded.email).toBe(payload.email);
      expect(decoded.roles).toEqual(payload.roles);
    });

    it('sets default expiry to 24 hours', () => {
      const payload = testUsers[0];
      const token = generateToken(payload);

      const decoded = jwt.verify(token, TEST_SECRET) as JWTPayload;
      const now = Math.floor(Date.now() / 1000);

      expect(decoded.exp).toBeGreaterThan(now);
      expect(decoded.exp).toBeLessThanOrEqual(now + 24 * 60 * 60 + 1);
    });

    it('respects custom expiry time', () => {
      const payload = testUsers[0];
      const token = generateToken(payload, '1h');

      const decoded = jwt.verify(token, TEST_SECRET) as JWTPayload;
      const now = Math.floor(Date.now() / 1000);

      expect(decoded.exp).toBeLessThanOrEqual(now + 60 * 60 + 1);
    });

    it('sets iat (issued at) timestamp', () => {
      const payload = testUsers[0];
      const token = generateToken(payload);

      const decoded = jwt.verify(token, TEST_SECRET) as JWTPayload;
      const now = Math.floor(Date.now() / 1000);

      expect(decoded.iat).toBeGreaterThanOrEqual(now - 1);
      expect(decoded.iat).toBeLessThanOrEqual(now + 1);
    });

    it('handles unicode characters in payload', () => {
      const payload = testUsers[2]; // Has unicode in sub

      const token = generateToken(payload);
      const decoded = jwt.verify(token, TEST_SECRET) as JWTPayload;

      expect(decoded.sub).toBe('admin_李明_system');
    });
  });

  describe('verifyToken', () => {
    it('verifies and decodes valid token', () => {
      const payload = testUsers[0];
      const token = generateToken(payload);

      const decoded = verifyToken(token);

      expect(decoded.sub).toBe(payload.sub);
      expect(decoded.tenantId).toBe(payload.tenantId);
    });

    it('throws for invalid token', () => {
      expect(() => verifyToken('invalid.token.here')).toThrow();
    });

    it('throws for token with wrong secret', () => {
      const wrongToken = jwt.sign({ sub: 'test' }, 'wrong-secret');

      expect(() => verifyToken(wrongToken)).toThrow();
    });

    it('throws for expired token', () => {
      const payload = testUsers[0];
      const token = jwt.sign(
        { ...payload, iat: Math.floor(Date.now() / 1000) - 3600, exp: Math.floor(Date.now() / 1000) - 60 },
        TEST_SECRET
      );

      expect(() => verifyToken(token)).toThrow();
    });
  });

  describe('jwtAuth middleware', () => {
    describe('skip paths', () => {
      it('skips authentication for /health endpoint', () => {
        const req = { path: '/health', headers: {} } as AuthenticatedRequest;
        const res = createMockResponse();
        const next = createMockNext();

        jwtAuth(req, res, next);

        expect(next).toHaveBeenCalled();
        expect(res.status).not.toHaveBeenCalled();
      });

      it('skips authentication for /locale endpoint', () => {
        const req = { path: '/locale', headers: {} } as AuthenticatedRequest;
        const res = createMockResponse();
        const next = createMockNext();

        jwtAuth(req, res, next);

        expect(next).toHaveBeenCalled();
        expect(res.status).not.toHaveBeenCalled();
      });
    });

    describe('Bearer token authentication', () => {
      it('authenticates valid Bearer token', () => {
        const payload = testUsers[0];
        const token = generateToken(payload);
        const req = {
          path: '/mcp',
          headers: { authorization: `Bearer ${token}` },
        } as AuthenticatedRequest;
        const res = createMockResponse();
        const next = createMockNext();

        jwtAuth(req, res, next);

        expect(next).toHaveBeenCalled();
        expect(req.user).toBeDefined();
        expect(req.user?.sub).toBe(payload.sub);
        expect(req.user?.tenantId).toBe(payload.tenantId);
      });

      it('rejects expired token', () => {
        const payload = testUsers[0];
        const token = jwt.sign(
          { ...payload, iat: Math.floor(Date.now() / 1000) - 3600, exp: Math.floor(Date.now() / 1000) - 60 },
          TEST_SECRET
        );
        const req = {
          path: '/mcp',
          headers: { authorization: `Bearer ${token}` },
        } as AuthenticatedRequest;
        const res = createMockResponse();
        const next = createMockNext();

        jwtAuth(req, res, next);

        expect(next).not.toHaveBeenCalled();
        expect(res.status).toHaveBeenCalledWith(401);
        expect(res.json).toHaveBeenCalledWith(
          expect.objectContaining({
            error: expect.objectContaining({
              code: -32001,
            }),
          })
        );
      });

      it('rejects invalid token', () => {
        const req = {
          path: '/mcp',
          headers: { authorization: 'Bearer invalid.token.here' },
        } as AuthenticatedRequest;
        const res = createMockResponse();
        const next = createMockNext();

        jwtAuth(req, res, next);

        expect(next).not.toHaveBeenCalled();
        expect(res.status).toHaveBeenCalledWith(401);
        expect(res.json).toHaveBeenCalledWith(
          expect.objectContaining({
            error: expect.objectContaining({
              message: 'Invalid token',
            }),
          })
        );
      });

      it('rejects malformed Authorization header', () => {
        const req = {
          path: '/mcp',
          headers: { authorization: 'NotBearer token' },
        } as AuthenticatedRequest;
        const res = createMockResponse();
        const next = createMockNext();

        jwtAuth(req, res, next);

        expect(next).not.toHaveBeenCalled();
        expect(res.status).toHaveBeenCalledWith(401);
      });
    });

    describe('API Key authentication (legacy)', () => {
      it('authenticates valid API key with tenant ID', () => {
        process.env.API_KEY = 'valid-api-key-12345';
        const req = {
          path: '/mcp',
          headers: {
            'x-api-key': 'valid-api-key-12345',
            'x-tenant-id': 'tenant_legacy_client',
          },
        } as AuthenticatedRequest;
        const res = createMockResponse();
        const next = createMockNext();

        jwtAuth(req, res, next);

        expect(next).toHaveBeenCalled();
        expect(req.user?.tenantId).toBe('tenant_legacy_client');
      });

      it('rejects invalid API key', () => {
        process.env.API_KEY = 'valid-api-key-12345';
        const req = {
          path: '/mcp',
          headers: {
            'x-api-key': 'wrong-api-key',
            'x-tenant-id': 'tenant_legacy_client',
          },
        } as AuthenticatedRequest;
        const res = createMockResponse();
        const next = createMockNext();

        jwtAuth(req, res, next);

        expect(next).not.toHaveBeenCalled();
        expect(res.status).toHaveBeenCalledWith(401);
      });

      it('rejects API key without tenant ID', () => {
        process.env.API_KEY = 'valid-api-key-12345';
        const req = {
          path: '/mcp',
          headers: {
            'x-api-key': 'valid-api-key-12345',
          },
        } as AuthenticatedRequest;
        const res = createMockResponse();
        const next = createMockNext();

        jwtAuth(req, res, next);

        expect(next).not.toHaveBeenCalled();
        expect(res.status).toHaveBeenCalledWith(401);
      });
    });

    describe('development mode bypass', () => {
      it('allows unauthenticated access when SKIP_AUTH=true in development', () => {
        process.env.NODE_ENV = 'development';
        process.env.SKIP_AUTH = 'true';
        const req = {
          path: '/mcp',
          headers: {},
        } as AuthenticatedRequest;
        const res = createMockResponse();
        const next = createMockNext();

        jwtAuth(req, res, next);

        expect(next).toHaveBeenCalled();
        expect(req.user?.sub).toBe('dev-user');
        expect(req.user?.tenantId).toBe('dev-tenant');
        expect(req.user?.roles).toContain('admin');
      });

      it('requires authentication when SKIP_AUTH=false even in development', () => {
        process.env.NODE_ENV = 'development';
        process.env.SKIP_AUTH = 'false';
        const req = {
          path: '/mcp',
          headers: {},
        } as AuthenticatedRequest;
        const res = createMockResponse();
        const next = createMockNext();

        jwtAuth(req, res, next);

        expect(next).not.toHaveBeenCalled();
        expect(res.status).toHaveBeenCalledWith(401);
      });
    });

    describe('error responses', () => {
      it('returns JSON-RPC formatted error for missing auth', () => {
        const req = {
          path: '/mcp',
          headers: {},
        } as AuthenticatedRequest;
        const res = createMockResponse();
        const next = createMockNext();

        jwtAuth(req, res, next);

        expect(res.json).toHaveBeenCalledWith({
          jsonrpc: '2.0',
          id: null,
          error: {
            code: -32001,
            message: expect.stringContaining('Authentication required'),
          },
        });
      });
    });
  });

  describe('requireRoles middleware', () => {
    it('allows access when user has required role', () => {
      const req = {
        user: { ...testUsers[0], iat: Date.now(), exp: Date.now() + 3600 },
      } as AuthenticatedRequest;
      const res = createMockResponse();
      const next = createMockNext();

      const middleware = requireRoles('designer');
      middleware(req, res, next);

      expect(next).toHaveBeenCalled();
      expect(res.status).not.toHaveBeenCalled();
    });

    it('allows access when user has any of multiple required roles', () => {
      const req = {
        user: { ...testUsers[0], iat: Date.now(), exp: Date.now() + 3600 },
      } as AuthenticatedRequest;
      const res = createMockResponse();
      const next = createMockNext();

      const middleware = requireRoles('admin', 'designer', 'owner');
      middleware(req, res, next);

      expect(next).toHaveBeenCalled();
    });

    it('rejects access when user lacks required role', () => {
      const req = {
        user: { ...testUsers[0], iat: Date.now(), exp: Date.now() + 3600 },
      } as AuthenticatedRequest;
      const res = createMockResponse();
      const next = createMockNext();

      const middleware = requireRoles('admin');
      middleware(req, res, next);

      expect(next).not.toHaveBeenCalled();
      expect(res.status).toHaveBeenCalledWith(403);
      expect(res.json).toHaveBeenCalledWith(
        expect.objectContaining({
          error: expect.objectContaining({
            code: -32002,
            message: expect.stringContaining('admin'),
          }),
        })
      );
    });

    it('rejects access when user is not authenticated', () => {
      const req = { user: undefined } as AuthenticatedRequest;
      const res = createMockResponse();
      const next = createMockNext();

      const middleware = requireRoles('designer');
      middleware(req, res, next);

      expect(next).not.toHaveBeenCalled();
      expect(res.status).toHaveBeenCalledWith(401);
    });

    it('handles user with no roles array', () => {
      const req = {
        user: { sub: 'test', tenantId: 'test', iat: Date.now(), exp: Date.now() + 3600 },
      } as AuthenticatedRequest;
      const res = createMockResponse();
      const next = createMockNext();

      const middleware = requireRoles('designer');
      middleware(req, res, next);

      expect(next).not.toHaveBeenCalled();
      expect(res.status).toHaveBeenCalledWith(403);
    });
  });

  describe('error handling', () => {
    it('throws when JWT_SECRET is missing', () => {
      delete process.env.JWT_SECRET;
      const payload = testUsers[0];

      expect(() => generateToken(payload)).toThrow('JWT_SECRET environment variable is required');
    });
  });
});
