/**
 * Auth Routes - Handles Figma plugin authentication via OTP pairing
 */

import { Router, Request, Response } from 'express';
import jwt from 'jsonwebtoken';
import { v4 as uuidv4 } from 'uuid';
import { createOTP, validateOTP, getStats } from './otpStore';

const router = Router();

// JWT secret - in production, use environment variable
const JWT_SECRET = process.env.JWT_SECRET || 'aid-figma-plugin-secret-key-change-in-production';
const JWT_EXPIRY = '24h';

// Store active sessions for ping/validation
const activeSessions = new Map<string, { tenantId: string; createdAt: number; lastPing: number }>();

/**
 * POST /auth/generate-pairing
 * Generate a pairing code for Claude Code to display
 * 
 * Body: { tenantId: string, projectPath: string, source: string }
 * Response: { success: boolean, code?: string, error?: string }
 */
router.post('/generate-pairing', (req: Request, res: Response) => {
  try {
    const { tenantId, projectPath, source } = req.body;

    if (!tenantId || !projectPath) {
      return res.status(400).json({ 
        success: false, 
        error: 'Missing required fields: tenantId, projectPath' 
      });
    }

    // Validate source is from Claude Code
    if (source !== 'claude-code') {
      return res.status(403).json({ 
        success: false, 
        error: 'Pairing codes can only be generated from Claude Code' 
      });
    }

    const result = createOTP(tenantId, projectPath, source);
    
    if (result.success) {
      // Format code as XXX XXX for display
      const formattedCode = result.code!.slice(0, 3) + ' ' + result.code!.slice(3);
      return res.json({ 
        success: true, 
        code: formattedCode,
        expiresIn: 300 // 5 minutes in seconds
      });
    } else {
      return res.status(429).json(result);
    }
  } catch (error) {
    console.error('Generate pairing error:', error);
    return res.status(500).json({ 
      success: false, 
      error: 'Internal server error' 
    });
  }
});

/**
 * POST /auth/pair
 * Validate a pairing code from Figma plugin and issue JWT
 * 
 * Body: { code: string }
 * Response: { success: boolean, token?: string, error?: string }
 */
router.post('/pair', (req: Request, res: Response) => {
  try {
    const { code } = req.body;

    if (!code) {
      return res.status(400).json({ 
        success: false, 
        error: 'Missing code' 
      });
    }

    // Remove spaces from code (user may enter XXX XXX)
    const cleanCode = code.replace(/\s/g, '');

    const result = validateOTP(cleanCode);

    if (!result.success) {
      return res.status(401).json(result);
    }

    // Generate JWT token
    const sessionId = uuidv4();
    const token = jwt.sign(
      { 
        sessionId,
        tenantId: result.tenantId,
        projectPath: result.projectPath,
        type: 'figma-plugin'
      },
      JWT_SECRET,
      { expiresIn: JWT_EXPIRY }
    );

    // Store session
    activeSessions.set(sessionId, {
      tenantId: result.tenantId!,
      createdAt: Date.now(),
      lastPing: Date.now()
    });

    return res.json({ 
      success: true, 
      token,
      expiresIn: 86400 // 24 hours in seconds
    });
  } catch (error) {
    console.error('Pair error:', error);
    return res.status(500).json({ 
      success: false, 
      error: 'Internal server error' 
    });
  }
});

/**
 * GET/POST /auth/jwt/validate
 * Validate a JWT token
 *
 * Headers: Authorization: Bearer <token>
 * Response: { valid: boolean, expiresIn?: number }
 */
function handleJwtValidate(req: Request, res: Response) {
  try {
    const authHeader = req.headers.authorization;

    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return res.status(401).json({ valid: false, error: 'Missing token' });
    }

    const token = authHeader.slice(7);

    try {
      const decoded = jwt.verify(token, JWT_SECRET) as jwt.JwtPayload;
      const expiresIn = decoded.exp ? decoded.exp - Math.floor(Date.now() / 1000) : 0;

      return res.json({
        valid: true,
        expiresIn,
        tenantId: decoded.tenantId
      });
    } catch (jwtError) {
      return res.status(401).json({ valid: false, error: 'Invalid or expired token' });
    }
  } catch (error) {
    console.error('Validate error:', error);
    return res.status(500).json({ valid: false, error: 'Internal server error' });
  }
}

// Support both GET and POST for jwt/validate
router.get('/jwt/validate', handleJwtValidate);
router.post('/jwt/validate', handleJwtValidate);

/**
 * GET/POST /auth/ping
 * Keep session alive and check token validity
 * 
 * Headers: Authorization: Bearer <token>
 * Response: { success: boolean, expiresIn?: number }
 */
function handlePing(req: Request, res: Response) {
  try {
    const authHeader = req.headers.authorization;
    
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return res.status(401).json({ success: false, error: 'Missing token' });
    }

    const token = authHeader.slice(7);

    try {
      const decoded = jwt.verify(token, JWT_SECRET) as jwt.JwtPayload;
      const expiresIn = decoded.exp ? decoded.exp - Math.floor(Date.now() / 1000) : 0;
      
      // Update last ping time
      const session = activeSessions.get(decoded.sessionId);
      if (session) {
        session.lastPing = Date.now();
      }
      
      return res.json({ 
        success: true, 
        expiresIn
      });
    } catch (jwtError) {
      return res.status(401).json({ success: false, error: 'Invalid or expired token' });
    }
  } catch (error) {
    console.error('Ping error:', error);
    return res.status(500).json({ success: false, error: 'Internal server error' });
  }
}

// Support both GET and POST for ping
router.get('/ping', handlePing);
router.post('/ping', handlePing);

/**
 * GET /auth/stats
 * Get auth system stats (for monitoring)
 */
router.get('/stats', (req: Request, res: Response) => {
  const stats = getStats();
  return res.json({
    ...stats,
    activeSessions: activeSessions.size
  });
});

export default router;
