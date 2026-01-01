/**
 * @file index.js
 * @description Main Express server for Figma plugin integration with AID methodology.
 *              Handles OTP pairing, JWT authentication, and MCP tool execution.
 * @related
 *   - ./services/componentAuditor.js - Component quality auditing
 *   - ./services/metadataGenerator.js - AI-powered metadata generation
 *   - ./services/scoringEngine.js - Quality scoring and reporting
 *   - ./services/aidExporter.js - Export to AID pipeline
 * @created 2025-12-23
 */

// Load environment variables from .env file
require('dotenv').config();

const express = require('express');
const cors = require('cors');
const crypto = require('crypto');
const jwt = require('jsonwebtoken');

// Import MCP services
const componentAuditor = require('./services/componentAuditor');
const scoringEngine = require('./services/scoringEngine');
const metadataGenerator = require('./services/metadataGenerator');
const aidExporter = require('./services/aidExporter');
const zipExporter = require('./services/zipExporter');

// ============================================
// Constants
// ============================================

const PORT = process.env.PORT || 3001;
const JWT_SECRET = process.env.JWT_SECRET || crypto.randomBytes(32).toString('hex');
const OTP_EXPIRY_MS = 5 * 60 * 1000;           // 5 minutes
const TOKEN_EXPIRY_SECONDS = 24 * 60 * 60;     // 24 hours
const MAX_OTP_ATTEMPTS = 3;
const CLEANUP_INTERVAL_MS = 60 * 1000;         // 1 minute
const SERVER_VERSION = '1.0.0';

// Allowed origins for CORS
const ALLOWED_ORIGINS = [
  'https://www.figma.com',
  'https://figma.com',
  'null', // Figma plugin sandbox origin
  'https://figma-plugin-server-983606191500.us-central1.run.app' // Cloud Run self-reference
];

// In development, also allow localhost
if (process.env.NODE_ENV !== 'production') {
  ALLOWED_ORIGINS.push('http://localhost:3000');
  ALLOWED_ORIGINS.push('http://localhost:3001');
}

// ============================================
// App Setup
// ============================================

const app = express();

// CORS configuration - restrict to Figma origins
app.use(cors({
  origin: (origin, callback) => {
    // Allow requests with no origin (like mobile apps or curl)
    if (!origin) return callback(null, true);

    if (ALLOWED_ORIGINS.includes(origin)) {
      callback(null, true);
    } else {
      console.warn(`[CORS] Blocked origin: ${origin}`);
      callback(null, false);
    }
  },
  credentials: true
}));

app.use(express.json({ limit: '1mb' }));

// Request logging middleware
app.use((req, res, next) => {
  const timestamp = new Date().toISOString();
  console.log(`[${timestamp}] ${req.method} ${req.path}`);
  next();
});

// ============================================
// OTP Store
// ============================================

const otpStore = new Map();

// Cleanup expired codes periodically
setInterval(() => {
  const now = Date.now();
  for (const [code, data] of otpStore.entries()) {
    if (now > data.expiresAt) {
      otpStore.delete(code);
    }
  }
}, CLEANUP_INTERVAL_MS);

// ============================================
// Health Check
// ============================================

app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    version: SERVER_VERSION
  });
});

// ============================================
// ZIP Download Endpoint
// ============================================

/**
 * Download a ZIP file by token
 * GET /download/:token
 *
 * The token is returned from export_to_aid when running in cloud mode.
 * After download, the ZIP file is automatically deleted.
 */
app.get('/download/:token', (req, res) => {
  const { token } = req.params;

  if (!token) {
    return res.status(400).json({
      error: 'missing_token',
      message: 'Download token is required'
    });
  }

  console.log(`[Download] Requested: token=${token.substring(0, 8)}...`);

  const download = zipExporter.getDownloadStream(token);

  if (!download) {
    console.log(`[Download] Token not found or expired: ${token.substring(0, 8)}...`);
    return res.status(404).json({
      error: 'not_found',
      message: 'Download not found or expired'
    });
  }

  const { stream, info } = download;

  console.log(`[Download] Serving: ${info.filename} (${info.size} bytes)`);

  // Set headers for file download
  res.setHeader('Content-Type', 'application/zip');
  res.setHeader('Content-Disposition', `attachment; filename="${info.filename}"`);
  res.setHeader('Content-Length', info.size);

  // Pipe the file to response
  stream.pipe(res);

  // After stream ends, mark for cleanup
  stream.on('end', () => {
    console.log(`[Download] Complete: ${info.filename}`);
    zipExporter.completeDownload(token);
  });

  stream.on('error', (err) => {
    console.error(`[Download] Stream error:`, err);
    res.status(500).json({
      error: 'stream_error',
      message: 'Error streaming file'
    });
  });
});

/**
 * Get download info without downloading (for UI preview)
 * GET /download/:token/info
 */
app.get('/download/:token/info', (req, res) => {
  const { token } = req.params;

  const info = zipExporter.getDownloadInfo(token);

  if (!info) {
    return res.status(404).json({
      error: 'not_found',
      message: 'Download not found or expired'
    });
  }

  res.json({
    filename: info.filename,
    componentName: info.componentName,
    relativePath: info.relativePath,
    size: info.size,
    createdAt: info.createdAt
  });
});

// ============================================
// Landing Page
// ============================================

app.get('/', (req, res) => {
  res.send(`
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Figma Plugin Server - AID</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 20px;
    }
    .container {
      background: white;
      border-radius: 16px;
      padding: 40px;
      max-width: 500px;
      width: 100%;
      box-shadow: 0 20px 60px rgba(0,0,0,0.3);
    }
    h1 {
      color: #333;
      margin-bottom: 8px;
      font-size: 28px;
    }
    .subtitle {
      color: #666;
      margin-bottom: 30px;
      font-size: 14px;
    }
    .status {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 12px 16px;
      background: #e8f5e9;
      border-radius: 8px;
      margin-bottom: 30px;
    }
    .status-dot {
      width: 10px;
      height: 10px;
      background: #4caf50;
      border-radius: 50%;
      animation: pulse 2s infinite;
    }
    @keyframes pulse {
      0%, 100% { opacity: 1; }
      50% { opacity: 0.5; }
    }
    .status-text { color: #2e7d32; font-weight: 500; }
    .pairing-section {
      text-align: center;
      padding: 30px;
      background: #f5f5f5;
      border-radius: 12px;
      margin-bottom: 30px;
    }
    .pairing-code {
      font-size: 48px;
      font-weight: bold;
      letter-spacing: 8px;
      color: #333;
      margin: 20px 0;
      font-family: 'Monaco', 'Consolas', monospace;
    }
    .pairing-code.empty {
      font-size: 18px;
      letter-spacing: normal;
      color: #999;
    }
    .expires {
      font-size: 14px;
      color: #666;
    }
    button {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      border: none;
      padding: 14px 28px;
      border-radius: 8px;
      font-size: 16px;
      font-weight: 600;
      cursor: pointer;
      transition: transform 0.2s, box-shadow 0.2s;
    }
    button:hover {
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    button:disabled {
      opacity: 0.6;
      cursor: not-allowed;
      transform: none;
    }
    .instructions {
      margin-top: 30px;
      padding-top: 20px;
      border-top: 1px solid #eee;
    }
    .instructions h3 {
      color: #333;
      margin-bottom: 12px;
      font-size: 16px;
    }
    .instructions ol {
      color: #666;
      font-size: 14px;
      padding-left: 20px;
    }
    .instructions li { margin-bottom: 8px; }
    .version {
      text-align: center;
      margin-top: 20px;
      color: #999;
      font-size: 12px;
    }
  </style>
</head>
<body>
  <div class="container">
    <h1>🎨 Figma Plugin Server</h1>
    <p class="subtitle">Atomic Design Extractor - AID Integration</p>

    <div class="status">
      <div class="status-dot"></div>
      <span class="status-text">Server Online</span>
    </div>

    <div class="pairing-section">
      <p>Generate a pairing code to connect your Figma plugin:</p>
      <div class="pairing-code empty" id="pairingCode">Click button below</div>
      <p class="expires" id="expiresText"></p>
      <button id="generateBtn" onclick="generateCode()">Generate Pairing Code</button>
    </div>

    <div class="instructions">
      <h3>How to pair:</h3>
      <ol>
        <li>Click "Generate Pairing Code" above</li>
        <li>Open Figma and run the Atomic Design Extractor plugin</li>
        <li>Click "Pair with AID" in the plugin</li>
        <li>Enter the 6-digit code</li>
      </ol>
    </div>

    <p class="version">Version ${SERVER_VERSION}</p>
  </div>

  <script>
    let currentTimer = null;

    async function generateCode() {
      const btn = document.getElementById('generateBtn');
      const codeEl = document.getElementById('pairingCode');
      const expiresEl = document.getElementById('expiresText');

      // Clear any existing timer to prevent multiple timers running
      if (currentTimer) {
        clearInterval(currentTimer);
        currentTimer = null;
      }

      btn.disabled = true;
      btn.textContent = 'Generating...';

      try {
        const res = await fetch('/auth/generate-pairing', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({})
        });
        const data = await res.json();

        if (data.success) {
          codeEl.textContent = data.code;
          codeEl.classList.remove('empty');
          expiresEl.textContent = 'Expires in 5 minutes';

          // Countdown timer - use global currentTimer to allow clearing on regenerate
          let seconds = data.expiresIn;
          currentTimer = setInterval(() => {
            seconds--;
            if (seconds <= 0) {
              clearInterval(currentTimer);
              currentTimer = null;
              codeEl.textContent = 'Code expired';
              codeEl.classList.add('empty');
              expiresEl.textContent = '';
            } else {
              const mins = Math.floor(seconds / 60);
              const secs = seconds % 60;
              expiresEl.textContent = 'Expires in ' + mins + ':' + secs.toString().padStart(2, '0');
            }
          }, 1000);
        }
      } catch (err) {
        codeEl.textContent = 'Error generating code';
        codeEl.classList.add('empty');
      }

      btn.disabled = false;
      btn.textContent = 'Generate New Code';
    }
  </script>
</body>
</html>
  `);
});

// ============================================
// OTP Generation
// ============================================

/**
 * Generate a 6-digit OTP code
 * @returns {string} 6-digit numeric string
 */
function generateOTP() {
  return crypto.randomInt(100000, 999999).toString();
}

/**
 * Generate pairing code endpoint
 * Creates a new OTP for plugin pairing
 */
app.post('/auth/generate-pairing', (req, res) => {
  const { tenantId, projectPath } = req.body;

  const otp = generateOTP();
  const formattedOtp = `${otp.slice(0, 3)} ${otp.slice(3)}`;
  const expiresAt = Date.now() + OTP_EXPIRY_MS;

  otpStore.set(otp, {
    tenantId: tenantId || 'default',
    projectPath: projectPath || process.cwd(),
    createdAt: Date.now(),
    expiresAt,
    attempts: 0,
    used: false
  });

  res.json({
    success: true,
    code: formattedOtp,
    expiresIn: OTP_EXPIRY_MS / 1000,
    expiresAt: new Date(expiresAt).toISOString()
  });
});

// ============================================
// JWT Token Management
// ============================================

/**
 * Generate a signed JWT token
 * @param {string} tenantId - Tenant identifier
 * @param {string} projectPath - Project path
 * @returns {string} Signed JWT token
 */
function generateToken(tenantId, projectPath) {
  const payload = {
    tenantId,
    projectPath,
    type: 'figma_plugin'
  };

  return jwt.sign(payload, JWT_SECRET, {
    expiresIn: TOKEN_EXPIRY_SECONDS,
    issuer: 'aid-figma-server'
  });
}

/**
 * Verify a JWT token
 * @param {string} token - JWT token to verify
 * @returns {object|null} Decoded payload or null if invalid
 */
function verifyToken(token) {
  try {
    return jwt.verify(token, JWT_SECRET, {
      issuer: 'aid-figma-server'
    });
  } catch (error) {
    return null;
  }
}

// ============================================
// Pairing Endpoint
// ============================================

/**
 * Pair endpoint - validates OTP and issues JWT
 */
app.post('/auth/pair', (req, res) => {
  const { code } = req.body;

  if (!code || typeof code !== 'string') {
    return res.status(400).json({
      success: false,
      error: 'invalid_request',
      message: 'Pairing code is required'
    });
  }

  const normalizedCode = code.replace(/\s/g, '');

  if (!/^\d{6}$/.test(normalizedCode)) {
    return res.status(400).json({
      success: false,
      error: 'invalid_format',
      message: 'Pairing code must be 6 digits'
    });
  }

  const data = otpStore.get(normalizedCode);

  if (!data) {
    return res.status(401).json({
      success: false,
      error: 'invalid_code',
      message: 'Invalid or expired pairing code'
    });
  }

  if (Date.now() > data.expiresAt) {
    otpStore.delete(normalizedCode);
    return res.status(401).json({
      success: false,
      error: 'expired',
      message: 'Pairing code has expired'
    });
  }

  if (data.used) {
    return res.status(401).json({
      success: false,
      error: 'already_used',
      message: 'Pairing code has already been used'
    });
  }

  data.attempts++;
  if (data.attempts > MAX_OTP_ATTEMPTS) {
    otpStore.delete(normalizedCode);
    return res.status(401).json({
      success: false,
      error: 'too_many_attempts',
      message: 'Too many incorrect attempts'
    });
  }

  data.used = true;
  const token = generateToken(data.tenantId, data.projectPath);

  res.json({
    success: true,
    token,
    tenantId: data.tenantId,
    projectPath: data.projectPath,
    pairedAt: new Date().toISOString()
  });
});

// ============================================
// JWT Validation
// ============================================

/**
 * Validate JWT token - shared logic for GET and POST
 */
function validateTokenHandler(req, res) {
  let token;
  const authHeader = req.headers.authorization;

  if (authHeader && authHeader.startsWith('Bearer ')) {
    token = authHeader.slice(7);
  } else if (req.body && req.body.token) {
    token = req.body.token;
  }

  if (!token) {
    return res.status(401).json({
      valid: false,
      error: 'missing_token',
      message: 'No token provided'
    });
  }

  const payload = verifyToken(token);

  if (!payload) {
    return res.status(401).json({
      valid: false,
      error: 'invalid_token',
      message: 'Token is invalid or expired'
    });
  }

  res.json({
    valid: true,
    tenantId: payload.tenantId,
    projectPath: payload.projectPath,
    exp: payload.exp
  });
}

app.get('/auth/jwt/validate', validateTokenHandler);
app.post('/auth/jwt/validate', validateTokenHandler);

// Lightweight ping endpoint for heartbeat/session keep-alive
app.get('/auth/ping', (req, res) => {
  const authHeader = req.headers.authorization;

  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return res.status(401).json({
      alive: false,
      error: 'missing_token'
    });
  }

  const token = authHeader.slice(7);
  const payload = verifyToken(token);

  if (!payload) {
    return res.status(401).json({
      alive: false,
      error: 'invalid_token'
    });
  }

  const now = Math.floor(Date.now() / 1000);
  const remainingSec = payload.exp - now;

  res.json({
    alive: true,
    exp: payload.exp,
    remainingSec,
    remainingHuman: remainingSec > 3600
      ? `${Math.floor(remainingSec / 3600)}h ${Math.floor((remainingSec % 3600) / 60)}m`
      : `${Math.floor(remainingSec / 60)}m`
  });
});

// Legacy endpoint alias
app.post('/auth/validate-pairing', (req, res) => {
  req.url = '/auth/pair';
  app.handle(req, res);
});

// ============================================
// MCP Tools Definition
// ============================================

const MCP_TOOLS = [
  {
    name: 'audit_component',
    description: 'Audit a Figma component for atomic design compliance and quality',
    inputSchema: {
      type: 'object',
      properties: {
        component: { type: 'object', description: 'Component data from Figma' },
        tokens: { type: 'array', description: 'Design tokens extracted from component' },
        variants: { type: 'array', description: 'Component variants' },
        checks: { type: 'array', description: 'Audit categories to run' }
      },
      required: ['component']
    }
  },
  {
    name: 'analyze_metadata',
    description: 'Analyze metadata gaps against SKILL.md format',
    inputSchema: {
      type: 'object',
      properties: {
        component: { type: 'object', description: 'Component data' },
        existingDescription: { type: 'string', description: 'Current component description' }
      },
      required: ['component']
    }
  },
  {
    name: 'generate_metadata',
    description: 'Generate metadata suggestions using AI',
    inputSchema: {
      type: 'object',
      properties: {
        component: { type: 'object', description: 'Component data' },
        tokens: { type: 'array', description: 'Design tokens' },
        variants: { type: 'array', description: 'Variants' }
      },
      required: ['component']
    }
  },
  {
    name: 'generate_report',
    description: 'Generate a comprehensive quality report',
    inputSchema: {
      type: 'object',
      properties: {
        component: { type: 'object', description: 'Component data' },
        auditResult: { type: 'object', description: 'Results from audit_component' },
        metadataAnalysis: { type: 'object', description: 'Results from analyze_metadata' },
        generatedMetadata: { type: 'object', description: 'Results from generate_metadata' }
      },
      required: ['component']
    }
  },
  {
    name: 'export_to_aid',
    description: 'Export component to AID pipeline (requires score >= 90)',
    inputSchema: {
      type: 'object',
      properties: {
        component: { type: 'object', description: 'Component data' },
        metadata: { type: 'object', description: 'Component metadata' },
        tokens: { type: 'array', description: 'Design tokens' },
        content: { type: 'object', description: 'Component content' },
        certification: { type: 'object', description: 'Quality certification' }
      },
      required: ['component', 'certification']
    }
  }
];

// ============================================
// MCP Endpoint
// ============================================

/**
 * Validate MCP request structure
 * @param {object} body - Request body
 * @returns {object} Validation result with error details if invalid
 */
function validateMCPRequest(body) {
  if (!body || typeof body !== 'object') {
    return { valid: false, error: 'Request body must be a JSON object' };
  }

  if (body.jsonrpc && body.jsonrpc !== '2.0') {
    return { valid: false, error: 'Invalid JSON-RPC version' };
  }

  if (!body.method || typeof body.method !== 'string') {
    return { valid: false, error: 'Method is required and must be a string' };
  }

  return { valid: true };
}

/**
 * MCP authentication middleware
 * Allows handshake methods without auth, requires JWT for tool calls
 */
const verifyMCPAuth = (req, res, next) => {
  // Allow handshake and health-check methods without auth
  const method = req.body?.method;
  if (method === 'initialize' ||
      method === 'notifications/initialized' ||
      method === 'tools/list' ||
      method === 'ping') {
    return next();
  }

  const authHeader = req.headers.authorization;
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    console.log('[MCP] Auth failed: No bearer token');
    return res.status(401).json({
      jsonrpc: '2.0',
      id: req.body?.id || null,
      error: { code: -32700, message: 'Authorization required' }
    });
  }

  const token = authHeader.slice(7);
  const payload = verifyToken(token);

  if (!payload) {
    console.log('[MCP] Auth failed: Invalid or expired token');
    return res.status(401).json({
      jsonrpc: '2.0',
      id: req.body?.id || null,
      error: { code: -32700, message: 'Invalid or expired token' }
    });
  }

  req.tenantId = payload.tenantId;
  console.log(`[MCP] Auth OK: tenantId=${payload.tenantId}`);
  next();
};

/**
 * MCP endpoint - JSON-RPC 2.0 implementation
 */
app.post('/mcp', verifyMCPAuth, async (req, res) => {
  const validation = validateMCPRequest(req.body);
  if (!validation.valid) {
    return res.status(400).json({
      jsonrpc: '2.0',
      id: req.body?.id || null,
      error: {
        code: -32600,
        message: validation.error
      }
    });
  }

  const { method, params, id } = req.body;
  console.log(`[MCP] Request: method=${method}, id=${id}`);

  try {
    // Handle initialize (MCP handshake)
    if (method === 'initialize') {
      return res.json({
        jsonrpc: '2.0',
        id,
        result: {
          protocolVersion: '2024-11-05',
          capabilities: {
            tools: { listChanged: false },
            resources: { listChanged: false }
          },
          serverInfo: {
            name: 'aid-figma-server',
            version: SERVER_VERSION
          }
        }
      });
    }

    // Handle notifications
    if (method === 'notifications/initialized') {
      return res.json({ jsonrpc: '2.0', id, result: {} });
    }

    // Handle ping
    if (method === 'ping') {
      return res.json({
        jsonrpc: '2.0',
        id,
        result: { pong: true, timestamp: new Date().toISOString() }
      });
    }

    // Handle tools/list
    if (method === 'tools/list') {
      return res.json({
        jsonrpc: '2.0',
        id,
        result: { tools: MCP_TOOLS }
      });
    }

    // Handle tools/call
    if (method === 'tools/call') {
      const toolName = params?.name;
      const args = params?.arguments || {};

      if (!toolName) {
        return res.json({
          jsonrpc: '2.0',
          id,
          error: {
            code: -32602,
            message: 'Tool name is required in params.name'
          }
        });
      }

      let result;

      // Log incoming component data for debugging
      console.log('[MCP] Tool call:', toolName);
      console.log('[MCP] Component name:', args?.component?.name || 'NO NAME');
      console.log('[MCP] Component type:', args?.component?.type || 'NO TYPE');
      console.log('[MCP] Has description:', !!args?.component?.description || !!args?.existingDescription);
      console.log('[MCP] Description preview:', (args?.component?.description || args?.existingDescription || 'NONE').substring(0, 100));
      console.log('[MCP] Variants count:', args?.component?.variants?.length || args?.variants?.length || 0);
      console.log('[MCP] Tokens count:', args?.tokens?.length || 0);
      console.log('[MCP] hasAutoLayout:', args?.component?.hasAutoLayout);
      console.log('[MCP] hasStates:', args?.component?.hasStates);
      console.log('[MCP] childCount:', args?.component?.childCount);
      console.log('[MCP] Properties count:', args?.component?.properties?.length || 0);
      console.log('[MCP] Properties:', JSON.stringify(args?.component?.properties?.map(p => ({ name: p.name, type: p.type })) || []));

      switch (toolName) {
        case 'audit_component':
          result = componentAuditor.runAudit(args);
          console.log('[MCP] Audit result score:', result?.score, 'combined:', result?.combinedScore);
          break;

        case 'analyze_metadata':
          result = componentAuditor.analyzeMetadataGaps(args);
          console.log('[MCP] Metadata completeness:', result?.completenessScore);
          break;

        case 'generate_metadata':
          result = await metadataGenerator.generateMetadata(args);
          console.log('[MCP] Generated metadata source:', result?.source);
          break;

        case 'generate_report': {
          console.log('[MCP] generate_report args.metadataAnalysis:', args.metadataAnalysis ? JSON.stringify(args.metadataAnalysis).substring(0, 150) : 'NOT PROVIDED');
          console.log('[MCP] generate_report args.auditResult:', args.auditResult ? 'PROVIDED' : 'NOT PROVIDED');
          const auditResult = args.auditResult || componentAuditor.runAudit(args);
          // Use provided metadataAnalysis if it has a valid completenessScore, otherwise recalculate
          let metadataAnalysis = args.metadataAnalysis;
          if (!metadataAnalysis || metadataAnalysis.completenessScore === undefined) {
            metadataAnalysis = componentAuditor.analyzeMetadataGaps(args);
          }
          console.log('[MCP] Using metadataAnalysis.completenessScore:', metadataAnalysis?.completenessScore);
          // Pass component data for comprehensive evaluation
          result = scoringEngine.generateReport(auditResult, metadataAnalysis, args.generatedMetadata, args);
          console.log('[MCP] Report overall score:', result?.overallScore);
          break;
        }

        case 'export_to_aid':
          result = await aidExporter.exportComponent(args);
          break;

        default:
          return res.json({
            jsonrpc: '2.0',
            id,
            error: {
              code: -32601,
              message: `Unknown tool: ${toolName}`
            }
          });
      }

      return res.json({
        jsonrpc: '2.0',
        id,
        result
      });
    }

    // Unknown method
    res.json({
      jsonrpc: '2.0',
      id,
      error: {
        code: -32601,
        message: `Method not found: ${method}`
      }
    });

  } catch (error) {
    console.error('[MCP] Error:', error);
    res.json({
      jsonrpc: '2.0',
      id,
      error: {
        code: -32603,
        message: 'Internal server error'
      }
    });
  }
});

// ============================================
// Start Server
// ============================================

app.listen(PORT, () => {
  console.log(`
╔══════════════════════════════════════════════════════════╗
║           Figma Plugin Server Started                     ║
╠══════════════════════════════════════════════════════════╣
║  Port: ${PORT}                                              ║
║  Health: http://localhost:${PORT}/health                    ║
║  Pairing: http://localhost:${PORT}/auth/generate-pairing    ║
║  Version: ${SERVER_VERSION}                                        ║
╚══════════════════════════════════════════════════════════╝
`);
});
