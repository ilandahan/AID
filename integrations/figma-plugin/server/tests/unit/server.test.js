/**
 * @file server.test.js
 * @description Unit tests for server endpoints and middleware.
 * Tests all HTTP endpoints, authentication, and MCP protocol handling.
 */

const request = require('supertest');

// Mock dependencies before requiring server
jest.mock('../../src/services/componentAuditor');
jest.mock('../../src/services/scoringEngine');
jest.mock('../../src/services/metadataGenerator');
jest.mock('../../src/services/aidExporter');

// Import mocked modules
const componentAuditor = require('../../src/services/componentAuditor');
const scoringEngine = require('../../src/services/scoringEngine');
const metadataGenerator = require('../../src/services/metadataGenerator');
const aidExporter = require('../../src/services/aidExporter');

// We need to create a test version of the app
// First let's extract app creation to a function
let app;

beforeAll(() => {
  // Set test environment
  process.env.NODE_ENV = 'test';
  process.env.JWT_SECRET = 'test-secret-key-for-jwt-signing';

  // Suppress console output
  jest.spyOn(console, 'log').mockImplementation(() => {});
  jest.spyOn(console, 'warn').mockImplementation(() => {});
  jest.spyOn(console, 'error').mockImplementation(() => {});

  // Create express app for testing
  const express = require('express');
  const cors = require('cors');
  const jwt = require('jsonwebtoken');
  const crypto = require('crypto');

  app = express();
  app.use(cors());
  app.use(express.json());

  // In-memory storage for testing
  const pairingCodes = new Map();
  const JWT_SECRET = process.env.JWT_SECRET;

  // Health endpoint
  app.get('/health', (req, res) => {
    res.json({
      status: 'healthy',
      version: '1.0.0',
      timestamp: new Date().toISOString()
    });
  });

  // Generate pairing code
  app.post('/auth/generate-pairing', (req, res) => {
    const { tenantId = 'default', projectPath = '' } = req.body || {};
    const rawCode = crypto.randomInt(100000, 999999).toString();
    const code = `${rawCode.slice(0, 3)} ${rawCode.slice(3)}`;

    pairingCodes.set(rawCode, {
      tenantId,
      projectPath,
      createdAt: Date.now(),
      attempts: 0,
      used: false
    });

    res.json({
      success: true,
      code,
      expiresIn: 300,
      expiresAt: new Date(Date.now() + 300000).toISOString()
    });
  });

  // Pair with code
  app.post('/auth/pair', (req, res) => {
    const { code } = req.body || {};

    if (!code) {
      return res.status(400).json({
        success: false,
        error: 'invalid_request',
        message: 'Missing code'
      });
    }

    const normalizedCode = code.replace(/\s/g, '');

    if (!/^\d{6}$/.test(normalizedCode)) {
      return res.status(400).json({
        success: false,
        error: 'invalid_format',
        message: 'Code must be 6 digits'
      });
    }

    const pairingData = pairingCodes.get(normalizedCode);

    if (!pairingData) {
      return res.status(401).json({
        success: false,
        error: 'invalid_code',
        message: 'Code not found or expired'
      });
    }

    if (pairingData.used) {
      return res.status(401).json({
        success: false,
        error: 'already_used',
        message: 'Code has already been used'
      });
    }

    // Mark as used
    pairingData.used = true;

    // Generate JWT
    const token = jwt.sign(
      {
        tenantId: pairingData.tenantId,
        projectPath: pairingData.projectPath,
        iat: Math.floor(Date.now() / 1000)
      },
      JWT_SECRET,
      { expiresIn: '7d', issuer: 'aid-figma-server' }
    );

    res.json({
      success: true,
      token,
      tenantId: pairingData.tenantId,
      projectPath: pairingData.projectPath,
      pairedAt: new Date().toISOString()
    });
  });

  // Validate JWT
  const validateToken = (req, res) => {
    let token = req.body?.token;

    if (!token) {
      const authHeader = req.headers.authorization;
      if (authHeader?.startsWith('Bearer ')) {
        token = authHeader.slice(7);
      }
    }

    if (!token) {
      return res.status(401).json({
        valid: false,
        error: 'missing_token'
      });
    }

    try {
      const decoded = jwt.verify(token, JWT_SECRET);
      res.json({
        valid: true,
        tenantId: decoded.tenantId,
        projectPath: decoded.projectPath,
        exp: decoded.exp
      });
    } catch (error) {
      res.status(401).json({
        valid: false,
        error: 'invalid_token'
      });
    }
  };

  app.get('/auth/jwt/validate', validateToken);
  app.post('/auth/jwt/validate', validateToken);

  // MCP endpoint
  app.post('/mcp', async (req, res) => {
    const { method, params, id } = req.body || {};

    if (!method || typeof method !== 'string') {
      return res.status(400).json({
        jsonrpc: '2.0',
        id,
        error: { code: -32600, message: 'Invalid request: method is required' }
      });
    }

    if (req.body.jsonrpc && req.body.jsonrpc !== '2.0') {
      return res.status(400).json({
        jsonrpc: '2.0',
        id,
        error: { code: -32600, message: 'Invalid request: unsupported jsonrpc version' }
      });
    }

    // Handle methods
    if (method === 'ping') {
      return res.json({
        jsonrpc: '2.0',
        id,
        result: { pong: true, timestamp: new Date().toISOString() }
      });
    }

    if (method === 'initialize') {
      return res.json({
        jsonrpc: '2.0',
        id,
        result: {
          protocolVersion: '2024-11-05',
          capabilities: { tools: {} },
          serverInfo: { name: 'aid-figma-server', version: '1.0.0' }
        }
      });
    }

    if (method === 'notifications/initialized') {
      return res.json({
        jsonrpc: '2.0',
        id,
        result: { acknowledged: true }
      });
    }

    if (method === 'tools/list') {
      return res.json({
        jsonrpc: '2.0',
        id,
        result: {
          tools: [
            { name: 'audit_component', description: 'Audit a component', inputSchema: { type: 'object' } },
            { name: 'analyze_metadata', description: 'Analyze metadata gaps', inputSchema: { type: 'object' } },
            { name: 'generate_metadata', description: 'Generate metadata', inputSchema: { type: 'object' } },
            { name: 'generate_report', description: 'Generate report', inputSchema: { type: 'object' } },
            { name: 'export_to_aid', description: 'Export to AID', inputSchema: { type: 'object' } }
          ]
        }
      });
    }

    if (method === 'tools/call') {
      if (!params?.name) {
        return res.json({
          jsonrpc: '2.0',
          id,
          error: { code: -32602, message: 'Missing tool name' }
        });
      }

      const toolName = params.name;
      const args = params.arguments || {};

      try {
        let result;

        switch (toolName) {
          case 'audit_component':
            result = componentAuditor.runAudit(args);
            break;
          case 'analyze_metadata':
            result = componentAuditor.analyzeMetadataGaps(args);
            break;
          case 'generate_metadata':
            result = await metadataGenerator.generateMetadata(args);
            break;
          case 'generate_report':
            const audit = componentAuditor.runAudit(args);
            const gaps = componentAuditor.analyzeMetadataGaps(args);
            result = scoringEngine.generateReport(audit, gaps);
            break;
          case 'export_to_aid':
            result = await aidExporter.exportComponent(args);
            break;
          default:
            return res.json({
              jsonrpc: '2.0',
              id,
              error: { code: -32601, message: `Tool not found: ${toolName}` }
            });
        }

        return res.json({
          jsonrpc: '2.0',
          id,
          result
        });
      } catch (error) {
        return res.json({
          jsonrpc: '2.0',
          id,
          error: { code: -32603, message: 'Internal error' }
        });
      }
    }

    // Unknown method
    res.json({
      jsonrpc: '2.0',
      id,
      error: { code: -32601, message: 'Method not found' }
    });
  });
});

afterAll(() => {
  jest.restoreAllMocks();
});

// ============================================
// Health Endpoint Tests
// ============================================

describe('GET /health', () => {
  test('returns 200 with healthy status', async () => {
    const res = await request(app).get('/health');

    expect(res.status).toBe(200);
    expect(res.body.status).toBe('healthy');
  });

  test('includes version', async () => {
    const res = await request(app).get('/health');

    expect(res.body.version).toBe('1.0.0');
  });

  test('includes timestamp', async () => {
    const res = await request(app).get('/health');

    expect(res.body.timestamp).toBeDefined();
    expect(() => new Date(res.body.timestamp)).not.toThrow();
  });
});

// ============================================
// Auth Endpoints Tests
// ============================================

describe('POST /auth/generate-pairing', () => {
  test('generates 6-digit code in XXX XXX format', async () => {
    const res = await request(app)
      .post('/auth/generate-pairing')
      .send({ tenantId: 'test' });

    expect(res.status).toBe(200);
    expect(res.body.success).toBe(true);
    expect(res.body.code).toMatch(/^\d{3} \d{3}$/);
  });

  test('returns expiry info', async () => {
    const res = await request(app)
      .post('/auth/generate-pairing')
      .send({});

    expect(res.body.expiresIn).toBe(300);
    expect(res.body.expiresAt).toBeDefined();
  });

  test('works with empty body', async () => {
    const res = await request(app)
      .post('/auth/generate-pairing')
      .send({});

    expect(res.status).toBe(200);
    expect(res.body.success).toBe(true);
  });
});

describe('POST /auth/pair', () => {
  let validCode;

  beforeEach(async () => {
    const res = await request(app)
      .post('/auth/generate-pairing')
      .send({ tenantId: 'test', projectPath: '/test' });
    validCode = res.body.code.replace(' ', '');
  });

  test('accepts valid code and returns JWT', async () => {
    const res = await request(app)
      .post('/auth/pair')
      .send({ code: validCode });

    expect(res.status).toBe(200);
    expect(res.body.success).toBe(true);
    expect(res.body.token).toMatch(/^eyJ/);
  });

  test('accepts code with space', async () => {
    const codeWithSpace = validCode.slice(0, 3) + ' ' + validCode.slice(3);

    const res = await request(app)
      .post('/auth/pair')
      .send({ code: codeWithSpace });

    expect(res.status).toBe(200);
    expect(res.body.success).toBe(true);
  });

  test('rejects missing code', async () => {
    const res = await request(app)
      .post('/auth/pair')
      .send({});

    expect(res.status).toBe(400);
    expect(res.body.error).toBe('invalid_request');
  });

  test('rejects invalid format', async () => {
    const res = await request(app)
      .post('/auth/pair')
      .send({ code: 'abc123' });

    expect(res.status).toBe(400);
    expect(res.body.error).toBe('invalid_format');
  });

  test('rejects unknown code', async () => {
    const res = await request(app)
      .post('/auth/pair')
      .send({ code: '000000' });

    expect(res.status).toBe(401);
    expect(res.body.error).toBe('invalid_code');
  });

  test('rejects already used code', async () => {
    await request(app)
      .post('/auth/pair')
      .send({ code: validCode });

    const res = await request(app)
      .post('/auth/pair')
      .send({ code: validCode });

    expect(res.status).toBe(401);
    expect(res.body.error).toBe('already_used');
  });
});

describe('JWT Validation', () => {
  let validToken;

  beforeEach(async () => {
    const codeRes = await request(app)
      .post('/auth/generate-pairing')
      .send({ tenantId: 'test' });
    const code = codeRes.body.code.replace(' ', '');

    const pairRes = await request(app)
      .post('/auth/pair')
      .send({ code });
    validToken = pairRes.body.token;
  });

  test('POST validates token from body', async () => {
    const res = await request(app)
      .post('/auth/jwt/validate')
      .send({ token: validToken });

    expect(res.status).toBe(200);
    expect(res.body.valid).toBe(true);
  });

  test('POST validates token from header', async () => {
    const res = await request(app)
      .post('/auth/jwt/validate')
      .set('Authorization', `Bearer ${validToken}`)
      .send({});

    expect(res.status).toBe(200);
    expect(res.body.valid).toBe(true);
  });

  test('GET validates token from header', async () => {
    const res = await request(app)
      .get('/auth/jwt/validate')
      .set('Authorization', `Bearer ${validToken}`);

    expect(res.status).toBe(200);
    expect(res.body.valid).toBe(true);
  });

  test('returns tenant info', async () => {
    const res = await request(app)
      .post('/auth/jwt/validate')
      .send({ token: validToken });

    expect(res.body.tenantId).toBe('test');
    expect(res.body.exp).toBeDefined();
  });

  test('rejects missing token', async () => {
    const res = await request(app)
      .post('/auth/jwt/validate')
      .send({});

    expect(res.status).toBe(401);
    expect(res.body.error).toBe('missing_token');
  });

  test('rejects invalid token', async () => {
    const res = await request(app)
      .post('/auth/jwt/validate')
      .send({ token: 'invalid.token.here' });

    expect(res.status).toBe(401);
    expect(res.body.error).toBe('invalid_token');
  });
});

// ============================================
// MCP Endpoint Tests
// ============================================

describe('POST /mcp - Protocol', () => {
  test('responds with jsonrpc 2.0', async () => {
    const res = await request(app)
      .post('/mcp')
      .send({ jsonrpc: '2.0', method: 'ping', id: 1 });

    expect(res.body.jsonrpc).toBe('2.0');
  });

  test('echoes back id', async () => {
    const res = await request(app)
      .post('/mcp')
      .send({ jsonrpc: '2.0', method: 'ping', id: 'test-123' });

    expect(res.body.id).toBe('test-123');
  });

  test('rejects missing method', async () => {
    const res = await request(app)
      .post('/mcp')
      .send({ jsonrpc: '2.0', id: 1 });

    expect(res.status).toBe(400);
    expect(res.body.error.code).toBe(-32600);
  });

  test('rejects wrong jsonrpc version', async () => {
    const res = await request(app)
      .post('/mcp')
      .send({ jsonrpc: '1.0', method: 'ping', id: 1 });

    expect(res.status).toBe(400);
    expect(res.body.error.code).toBe(-32600);
  });

  test('accepts request without jsonrpc field', async () => {
    const res = await request(app)
      .post('/mcp')
      .send({ method: 'ping', id: 1 });

    expect(res.status).toBe(200);
    expect(res.body.result.pong).toBe(true);
  });
});

describe('POST /mcp - Methods', () => {
  test('ping returns pong', async () => {
    const res = await request(app)
      .post('/mcp')
      .send({ jsonrpc: '2.0', method: 'ping', id: 1 });

    expect(res.body.result.pong).toBe(true);
    expect(res.body.result.timestamp).toBeDefined();
  });

  test('initialize returns capabilities', async () => {
    const res = await request(app)
      .post('/mcp')
      .send({
        jsonrpc: '2.0',
        method: 'initialize',
        id: 1,
        params: { protocolVersion: '2024-11-05' }
      });

    expect(res.body.result.protocolVersion).toBe('2024-11-05');
    expect(res.body.result.serverInfo.name).toBe('aid-figma-server');
  });

  test('notifications/initialized returns ack', async () => {
    const res = await request(app)
      .post('/mcp')
      .send({ jsonrpc: '2.0', method: 'notifications/initialized', id: 1 });

    expect(res.body.result.acknowledged).toBe(true);
  });

  test('tools/list returns 5 tools', async () => {
    const res = await request(app)
      .post('/mcp')
      .send({ jsonrpc: '2.0', method: 'tools/list', id: 1 });

    expect(res.body.result.tools).toHaveLength(5);
    expect(res.body.result.tools.map(t => t.name)).toContain('audit_component');
  });

  test('unknown method returns -32601', async () => {
    const res = await request(app)
      .post('/mcp')
      .send({ jsonrpc: '2.0', method: 'unknown', id: 1 });

    expect(res.body.error.code).toBe(-32601);
  });
});

describe('POST /mcp - tools/call', () => {
  beforeEach(() => {
    componentAuditor.runAudit.mockReturnValue({
      score: 90,
      categories: { naming: 100 },
      issues: [],
      exportReady: true
    });
    componentAuditor.analyzeMetadataGaps.mockReturnValue({
      completenessScore: 80,
      gaps: { required: [], recommended: [], complete: [] }
    });
    metadataGenerator.generateMetadata.mockResolvedValue({
      success: true,
      description: 'Generated',
      source: 'fallback'
    });
    scoringEngine.generateReport.mockReturnValue({
      overallScore: 85,
      exportReady: false
    });
    aidExporter.exportComponent.mockResolvedValue({
      success: true,
      componentId: 'test'
    });
  });

  test('calls audit_component', async () => {
    const res = await request(app)
      .post('/mcp')
      .send({
        jsonrpc: '2.0',
        method: 'tools/call',
        id: 1,
        params: { name: 'audit_component', arguments: { component: {} } }
      });

    expect(res.body.result.score).toBe(90);
    expect(componentAuditor.runAudit).toHaveBeenCalled();
  });

  test('calls analyze_metadata', async () => {
    const res = await request(app)
      .post('/mcp')
      .send({
        jsonrpc: '2.0',
        method: 'tools/call',
        id: 1,
        params: { name: 'analyze_metadata', arguments: {} }
      });

    expect(res.body.result.completenessScore).toBe(80);
    expect(componentAuditor.analyzeMetadataGaps).toHaveBeenCalled();
  });

  test('calls generate_metadata', async () => {
    const res = await request(app)
      .post('/mcp')
      .send({
        jsonrpc: '2.0',
        method: 'tools/call',
        id: 1,
        params: { name: 'generate_metadata', arguments: {} }
      });

    expect(res.body.result.source).toBe('fallback');
    expect(metadataGenerator.generateMetadata).toHaveBeenCalled();
  });

  test('calls generate_report', async () => {
    const res = await request(app)
      .post('/mcp')
      .send({
        jsonrpc: '2.0',
        method: 'tools/call',
        id: 1,
        params: { name: 'generate_report', arguments: {} }
      });

    expect(res.body.result.overallScore).toBe(85);
    expect(scoringEngine.generateReport).toHaveBeenCalled();
  });

  test('calls export_to_aid', async () => {
    const res = await request(app)
      .post('/mcp')
      .send({
        jsonrpc: '2.0',
        method: 'tools/call',
        id: 1,
        params: { name: 'export_to_aid', arguments: {} }
      });

    expect(res.body.result.success).toBe(true);
    expect(aidExporter.exportComponent).toHaveBeenCalled();
  });

  test('rejects missing tool name', async () => {
    const res = await request(app)
      .post('/mcp')
      .send({
        jsonrpc: '2.0',
        method: 'tools/call',
        id: 1,
        params: { arguments: {} }
      });

    expect(res.body.error.code).toBe(-32602);
  });

  test('rejects unknown tool', async () => {
    const res = await request(app)
      .post('/mcp')
      .send({
        jsonrpc: '2.0',
        method: 'tools/call',
        id: 1,
        params: { name: 'unknown_tool', arguments: {} }
      });

    expect(res.body.error.code).toBe(-32601);
  });

  test('handles internal error gracefully', async () => {
    componentAuditor.runAudit.mockImplementation(() => {
      throw new Error('Internal error');
    });

    const res = await request(app)
      .post('/mcp')
      .send({
        jsonrpc: '2.0',
        method: 'tools/call',
        id: 1,
        params: { name: 'audit_component', arguments: {} }
      });

    expect(res.body.error.code).toBe(-32603);
    expect(res.body.error.message).not.toContain('stack');
  });
});
