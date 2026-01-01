/**
 * @file jwt-middleware.ts
 * @description JWT authentication middleware for the MCP server.
 * Validates JWT tokens for secure communication with Claude Code.
 *
 * @related
 *   - ../index.ts - Server entry point
 *   - ../../AuthService.ts - Plugin-side auth service
 */

import type { Request, Response, NextFunction } from 'express';
import jwt from 'jsonwebtoken';

export interface JWTPayload {
  sub: string;          // User ID
  tenantId: string;     // Tenant/Organization ID
  email?: string;
  roles?: string[];
  iat: number;          // Issued at
  exp: number;          // Expiration
}

export interface AuthenticatedRequest extends Request {
  user?: JWTPayload;
}

/**
 * Get JWT secret from environment
 */
function getJWTSecret(): string {
  const secret = process.env.JWT_SECRET;
  if (!secret) {
    throw new Error('JWT_SECRET environment variable is required');
  }
  return secret;
}

/**
 * JWT Authentication Middleware
 *
 * Validates the JWT token from the Authorization header.
 * Supports both Bearer token and X-API-Key header for backwards compatibility.
 */
export function jwtAuth(req: AuthenticatedRequest, res: Response, next: NextFunction): void {
  // Skip auth for health check and locale endpoints
  if (req.path === '/health' || req.path === '/locale') {
    return next();
  }

  // Try to get token from Authorization header
  const authHeader = req.headers.authorization;
  const apiKey = req.headers['x-api-key'] as string;
  const tenantId = req.headers['x-tenant-id'] as string;

  // Option 1: JWT Bearer token
  if (authHeader?.startsWith('Bearer ')) {
    const token = authHeader.substring(7);

    try {
      const secret = getJWTSecret();
      const decoded = jwt.verify(token, secret) as JWTPayload;

      // Check expiration
      if (decoded.exp && Date.now() >= decoded.exp * 1000) {
        res.status(401).json({
          jsonrpc: '2.0',
          id: null,
          error: {
            code: -32001,
            message: 'Token expired'
          }
        });
        return;
      }

      req.user = decoded;
      return next();
    } catch (error) {
      res.status(401).json({
        jsonrpc: '2.0',
        id: null,
        error: {
          code: -32001,
          message: 'Invalid token'
        }
      });
      return;
    }
  }

  // Option 2: API Key authentication (for backwards compatibility)
  if (apiKey && tenantId) {
    // Validate API key against environment
    const validApiKey = process.env.API_KEY || process.env.ANTHROPIC_API_KEY;

    if (apiKey === validApiKey) {
      req.user = {
        sub: 'api-key-user',
        tenantId,
        iat: Math.floor(Date.now() / 1000),
        exp: Math.floor(Date.now() / 1000) + 3600
      };
      return next();
    }
  }

  // Option 3: Development mode - skip auth
  if (process.env.NODE_ENV === 'development' && process.env.SKIP_AUTH === 'true') {
    req.user = {
      sub: 'dev-user',
      tenantId: 'dev-tenant',
      roles: ['admin'],
      iat: Math.floor(Date.now() / 1000),
      exp: Math.floor(Date.now() / 1000) + 3600
    };
    return next();
  }

  // No valid authentication found
  res.status(401).json({
    jsonrpc: '2.0',
    id: null,
    error: {
      code: -32001,
      message: 'Authentication required. Provide Bearer token or X-API-Key header.'
    }
  });
}

/**
 * Generate a JWT token for a user
 * Used by the plugin after authentication
 */
export function generateToken(payload: Omit<JWTPayload, 'iat' | 'exp'>, expiresIn = '24h'): string {
  const secret = getJWTSecret();

  return jwt.sign(payload, secret, {
    expiresIn,
    algorithm: 'HS256'
  });
}

/**
 * Verify and decode a JWT token
 */
export function verifyToken(token: string): JWTPayload {
  const secret = getJWTSecret();
  return jwt.verify(token, secret) as JWTPayload;
}

/**
 * Require specific roles middleware
 */
export function requireRoles(...roles: string[]) {
  return (req: AuthenticatedRequest, res: Response, next: NextFunction): void => {
    if (!req.user) {
      res.status(401).json({
        jsonrpc: '2.0',
        id: null,
        error: {
          code: -32001,
          message: 'Authentication required'
        }
      });
      return;
    }

    const userRoles = req.user.roles || [];
    const hasRole = roles.some(role => userRoles.includes(role));

    if (!hasRole) {
      res.status(403).json({
        jsonrpc: '2.0',
        id: null,
        error: {
          code: -32002,
          message: `Required role(s): ${roles.join(', ')}`
        }
      });
      return;
    }

    next();
  };
}
