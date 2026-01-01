/**
 * @file index.ts
 * @description MCP Server entry point for Figma Design Review.
 * Handles JSON-RPC 2.0 requests from the Figma plugin.
 *
 * IMPORTANT: This server is AID-exclusive. The plugin MUST be paired
 * with AID using /aid-pair command before it can function.
 *
 * @related
 *   - ./tools/design-review.ts - Tool implementations
 *   - ./claude/client.ts - Claude API integration
 *   - ./i18n/messages.ts - Internationalization
 *   - ./auth/aid-pairing.ts - AID pairing system
 *   - ./auth/jwt-middleware.ts - JWT authentication
 */

import express from 'express';
import cors from 'cors';
import { config } from 'dotenv';
import {
  auditComponent,
  analyzeMetadata,
  generateMetadata,
  generateReport,
  runQualityPipeline,
  exportToAID
} from './tools/design-review.js';
import { loadSkills, validateSkillContext } from './claude/skill-loader.js';
import { detectLocale, getMessages, type Locale } from './i18n/messages.js';
import type { ComponentData } from './claude/prompt-builder.js';
import { jwtAuth, type AuthenticatedRequest } from './auth/jwt-middleware.js';
import {
  generatePairingCode,
  validatePairingCode,
  getPairingStatus,
  formatPairingCodeMessage
} from './auth/aid-pairing.js';
import {
  queueRequest,
  getPendingRequests,
  markProcessing,
  completeRequest,
  failRequest,
  getQueueStats,
  type QueuedRequest
} from './relay/request-queue.js';

// Load environment variables
config();

const app = express();
const PORT = process.env.PORT || 3001;

// Middleware
app.use(cors());
app.use(express.json({ limit: '10mb' }));

// MCP Protocol types
interface MCPRequest {
  jsonrpc: '2.0';
  id: number | string | null;
  method: string;
  params?: unknown;
}

interface MCPResponse {
  jsonrpc: '2.0';
  id: number | string | null;
  result?: unknown;
  error?: {
    code: number;
    message: string;
    data?: unknown;
  };
}

// Tool definitions for MCP
const TOOLS = [
  {
    name: 'audit_component',
    description: 'Audit a Figma component for quality issues using SKILL.md validation rules',
    inputSchema: {
      type: 'object',
      properties: {
        component: { type: 'object', description: 'Component data from Figma' },
        checks: { type: 'array', items: { type: 'string' }, description: 'Categories to check' },
        locale: { type: 'string', enum: ['en', 'he'], description: 'Response language' }
      },
      required: ['component']
    }
  },
  {
    name: 'analyze_metadata',
    description: 'Analyze metadata completeness based on SKILL.md format',
    inputSchema: {
      type: 'object',
      properties: {
        component: { type: 'object', description: 'Component data from Figma' },
        existingDescription: { type: 'string', description: 'Current description if any' },
        locale: { type: 'string', enum: ['en', 'he'] }
      },
      required: ['component']
    }
  },
  {
    name: 'generate_metadata',
    description: 'Generate metadata suggestions using SKILL.md format',
    inputSchema: {
      type: 'object',
      properties: {
        component: { type: 'object', description: 'Component data from Figma' },
        tokens: { type: 'array', description: 'Extracted design tokens' },
        variants: { type: 'array', description: 'Component variants' },
        locale: { type: 'string', enum: ['en', 'he'] }
      },
      required: ['component']
    }
  },
  {
    name: 'generate_report',
    description: 'Generate complete quality report using ENRICHMENT_TEMPLATE structure',
    inputSchema: {
      type: 'object',
      properties: {
        component: { type: 'object' },
        audit: { type: 'object' },
        metadata: { type: 'object' },
        generated: { type: 'object' },
        locale: { type: 'string', enum: ['en', 'he'] }
      },
      required: ['component', 'audit', 'metadata', 'generated']
    }
  },
  {
    name: 'run_quality_pipeline',
    description: 'Run full quality pipeline (audit + analyze + generate + report)',
    inputSchema: {
      type: 'object',
      properties: {
        component: { type: 'object', description: 'Component data from Figma' },
        locale: { type: 'string', enum: ['en', 'he'] }
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
        component: { type: 'object' },
        report: { type: 'object' },
        locale: { type: 'string', enum: ['en', 'he'] }
      },
      required: ['component', 'report']
    }
  },
  {
    name: 'get_messages',
    description: 'Get localized UI messages for specified locale',
    inputSchema: {
      type: 'object',
      properties: {
        locale: { type: 'string', enum: ['en', 'he'] }
      },
      required: ['locale']
    }
  }
];

// MCP request handler
async function handleMCPRequest(request: MCPRequest): Promise<MCPResponse> {
  const { id, method, params } = request;

  try {
    switch (method) {
      case 'initialize': {
        // Validate skills are loaded
        const skills = loadSkills();
        const validation = validateSkillContext(skills);

        if (!validation.valid) {
          return {
            jsonrpc: '2.0',
            id,
            error: {
              code: -32000,
              message: 'Skill validation failed',
              data: validation.errors
            }
          };
        }

        return {
          jsonrpc: '2.0',
          id,
          result: {
            protocolVersion: '2024-11-05',
            serverInfo: {
              name: 'fig-plugin-mcp-server',
              version: '1.0.0'
            },
            capabilities: {
              tools: {},
              resources: {}
            }
          }
        };
      }

      case 'notifications/initialized': {
        return { jsonrpc: '2.0', id, result: {} };
      }

      case 'ping': {
        return { jsonrpc: '2.0', id, result: { pong: true } };
      }

      case 'tools/list': {
        return {
          jsonrpc: '2.0',
          id,
          result: { tools: TOOLS }
        };
      }

      case 'tools/call': {
        const { name, arguments: args } = params as { name: string; arguments: Record<string, unknown> };
        const locale = (args.locale as Locale) || 'en';

        // Map tool names to queue request types
        const toolTypeMap: Record<string, 'audit' | 'analyze' | 'generate' | 'report' | 'pipeline' | 'export'> = {
          'audit_component': 'audit',
          'analyze_metadata': 'analyze',
          'generate_metadata': 'generate',
          'generate_report': 'report',
          'run_quality_pipeline': 'pipeline',
          'export_to_aid': 'export'
        };

        switch (name) {
          case 'audit_component': {
            // Process directly using Claude API
            const component = args.component as ComponentData;
            const checks = args.checks as string[] | undefined;

            try {
              const result = await auditComponent(component, checks, locale);
              return { jsonrpc: '2.0', id, result };
            } catch (error) {
              return {
                jsonrpc: '2.0',
                id,
                error: {
                  code: -32000,
                  message: error instanceof Error ? error.message : 'Audit failed'
                }
              };
            }
          }

          case 'analyze_metadata': {
            const component = args.component as ComponentData;

            try {
              const result = await analyzeMetadata(component, locale);
              return { jsonrpc: '2.0', id, result };
            } catch (error) {
              return {
                jsonrpc: '2.0',
                id,
                error: {
                  code: -32000,
                  message: error instanceof Error ? error.message : 'Analysis failed'
                }
              };
            }
          }

          case 'generate_metadata': {
            const component = args.component as ComponentData;

            try {
              const result = await generateMetadata(component, locale);
              return { jsonrpc: '2.0', id, result };
            } catch (error) {
              return {
                jsonrpc: '2.0',
                id,
                error: {
                  code: -32000,
                  message: error instanceof Error ? error.message : 'Generation failed'
                }
              };
            }
          }

          case 'generate_report': {
            const component = args.component as ComponentData;
            const audit = args.audit as Parameters<typeof generateReport>[1];
            const metadata = args.metadata as Parameters<typeof generateReport>[2];
            const generated = args.generated as Parameters<typeof generateReport>[3];

            try {
              const result = await generateReport(component, audit, metadata, generated, locale);
              return { jsonrpc: '2.0', id, result };
            } catch (error) {
              return {
                jsonrpc: '2.0',
                id,
                error: {
                  code: -32000,
                  message: error instanceof Error ? error.message : 'Report generation failed'
                }
              };
            }
          }

          case 'run_quality_pipeline': {
            const component = args.component as ComponentData;

            try {
              const result = await runQualityPipeline(component, locale);
              return { jsonrpc: '2.0', id, result };
            } catch (error) {
              return {
                jsonrpc: '2.0',
                id,
                error: {
                  code: -32000,
                  message: error instanceof Error ? error.message : 'Pipeline failed'
                }
              };
            }
          }

          case 'export_to_aid': {
            const component = args.component as ComponentData;
            const report = args.report as Parameters<typeof exportToAID>[1];

            try {
              const result = await exportToAID(component, report, locale);
              return { jsonrpc: '2.0', id, result };
            } catch (error) {
              return {
                jsonrpc: '2.0',
                id,
                error: {
                  code: -32000,
                  message: error instanceof Error ? error.message : 'Export failed'
                }
              };
            }
          }

          case 'get_messages': {
            // This doesn't need Claude - return directly
            const messages = getMessages(locale);
            return { jsonrpc: '2.0', id, result: { messages, locale } };
          }

          default:
            return {
              jsonrpc: '2.0',
              id,
              error: {
                code: -32601,
                message: `Unknown tool: ${name}`
              }
            };
        }
      }

      default:
        return {
          jsonrpc: '2.0',
          id,
          error: {
            code: -32601,
            message: `Method not found: ${method}`
          }
        };
    }
  } catch (error) {
    console.error('MCP request error:', error);
    return {
      jsonrpc: '2.0',
      id,
      error: {
        code: -32000,
        message: error instanceof Error ? error.message : 'Unknown error',
        data: error instanceof Error ? error.stack : undefined
      }
    };
  }
}

// NOTE: MCP endpoint is defined below with JWT authentication
// See "Protected MCP Endpoint" section

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    version: '1.0.0',
    skills: validateSkillContext(loadSkills())
  });
});

// Locale detection endpoint
app.get('/locale', (req, res) => {
  const acceptLanguage = req.headers['accept-language'];
  const locale = detectLocale(acceptLanguage);
  res.json({ locale, messages: getMessages(locale) });
});

// ============================================
// AID Pairing Endpoints (Required for plugin)
// ============================================

/**
 * Generate a pairing code (called by /aid-pair command)
 * This endpoint is only accessible from localhost (Claude Code)
 */
app.post('/auth/generate-pairing', (req, res) => {
  // Only allow from localhost for security
  const clientIp = req.ip || req.socket.remoteAddress || '';
  const isLocalhost = clientIp === '127.0.0.1' || clientIp === '::1' || clientIp === '::ffff:127.0.0.1';

  if (!isLocalhost && process.env.NODE_ENV !== 'development') {
    return res.status(403).json({
      success: false,
      error: 'Pairing codes can only be generated from localhost'
    });
  }

  const { tenantId, projectPath, locale = 'en' } = req.body;

  if (!tenantId || !projectPath) {
    return res.status(400).json({
      success: false,
      error: 'tenantId and projectPath are required'
    });
  }

  const code = generatePairingCode(tenantId, projectPath);
  const message = formatPairingCodeMessage(code, locale as 'en' | 'he');

  res.json({
    success: true,
    code,
    message,
    expiresIn: 300 // 5 minutes in seconds
  });
});

/**
 * Validate a pairing code (called by Figma plugin)
 */
app.post('/auth/pair', (req, res) => {
  const clientIp = req.ip || req.socket.remoteAddress || '0.0.0.0';
  const { code } = req.body;

  if (!code) {
    return res.status(400).json({
      success: false,
      error: 'Pairing code is required'
    });
  }

  const result = validatePairingCode(code, clientIp);

  if (result.success) {
    res.json(result);
  } else {
    res.status(401).json(result);
  }
});

/**
 * Check pairing code status (for polling)
 */
app.get('/auth/pair/:code/status', (req, res) => {
  const status = getPairingStatus(req.params.code);
  res.json(status);
});

/**
 * Validate JWT token
 * Called by plugin to check if stored token is still valid
 */
app.get('/auth/jwt/validate', jwtAuth, (req: AuthenticatedRequest, res) => {
  // If we get here, the token is valid (jwtAuth middleware passed)
  res.json({
    valid: true,
    user: req.user
  });
});

// ============================================
// Claude Code Relay Endpoints (localhost only)
// ============================================

/**
 * Get pending requests (polled by Claude Code)
 * Only accessible from localhost
 */
app.get('/relay/pending', (req, res) => {
  const clientIp = req.ip || req.socket.remoteAddress || '';
  const isLocalhost = clientIp === '127.0.0.1' || clientIp === '::1' || clientIp === '::ffff:127.0.0.1';

  if (!isLocalhost && process.env.NODE_ENV !== 'development') {
    return res.status(403).json({ error: 'Relay endpoints only accessible from localhost' });
  }

  const pending = getPendingRequests();
  res.json({ requests: pending, stats: getQueueStats() });
});

/**
 * Mark request as processing (called by Claude Code)
 */
app.post('/relay/process/:requestId', (req, res) => {
  const clientIp = req.ip || req.socket.remoteAddress || '';
  const isLocalhost = clientIp === '127.0.0.1' || clientIp === '::1' || clientIp === '::ffff:127.0.0.1';

  if (!isLocalhost && process.env.NODE_ENV !== 'development') {
    return res.status(403).json({ error: 'Relay endpoints only accessible from localhost' });
  }

  const success = markProcessing(req.params.requestId);
  res.json({ success });
});

/**
 * Complete a request with result (called by Claude Code)
 */
app.post('/relay/complete/:requestId', (req, res) => {
  const clientIp = req.ip || req.socket.remoteAddress || '';
  const isLocalhost = clientIp === '127.0.0.1' || clientIp === '::1' || clientIp === '::ffff:127.0.0.1';

  if (!isLocalhost && process.env.NODE_ENV !== 'development') {
    return res.status(403).json({ error: 'Relay endpoints only accessible from localhost' });
  }

  const { result } = req.body;
  const success = completeRequest(req.params.requestId, result);
  res.json({ success });
});

/**
 * Fail a request with error (called by Claude Code)
 */
app.post('/relay/fail/:requestId', (req, res) => {
  const clientIp = req.ip || req.socket.remoteAddress || '';
  const isLocalhost = clientIp === '127.0.0.1' || clientIp === '::1' || clientIp === '::ffff:127.0.0.1';

  if (!isLocalhost && process.env.NODE_ENV !== 'development') {
    return res.status(403).json({ error: 'Relay endpoints only accessible from localhost' });
  }

  const { error } = req.body;
  const success = failRequest(req.params.requestId, error || 'Unknown error');
  res.json({ success });
});

// ============================================
// Protected MCP Endpoint (Requires JWT)
// ============================================

// Apply JWT auth to MCP endpoint
app.post('/mcp', jwtAuth, async (req: AuthenticatedRequest, res) => {
  const request = req.body as MCPRequest;

  // Log authenticated request
  console.log(`[MCP] ${request.method} from tenant: ${req.user?.tenantId || 'unknown'}`);

  if (!request.jsonrpc || request.jsonrpc !== '2.0') {
    return res.status(400).json({
      jsonrpc: '2.0',
      id: null,
      error: {
        code: -32600,
        message: 'Invalid JSON-RPC request'
      }
    });
  }

  const response = await handleMCPRequest(request);
  res.json(response);
});

// Start server
app.listen(PORT, () => {
  console.log(`
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   🎨 Figma Design Review MCP Server (AID-Exclusive)          ║
║                                                              ║
║   Running on: http://localhost:${PORT}                         ║
║   MCP Endpoint: http://localhost:${PORT}/mcp (JWT Required)    ║
║                                                              ║
║   🔐 Authentication:                                         ║
║   ├── Pairing: POST /auth/pair                               ║
║   └── Generate: POST /auth/generate-pairing (localhost only) ║
║                                                              ║
║   📦 Skills loaded:                                          ║
║   ├── component-metadata (SKILL.md)                          ║
║   ├── figma-design-review                                    ║
║   └── atomic-design                                          ║
║                                                              ║
║   🌐 Languages: English (LTR), Hebrew (RTL)                  ║
║                                                              ║
║   ⚠️  Plugin must be paired with AID using /aid-pair         ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
  `);

  // Validate skills on startup
  try {
    const skills = loadSkills();
    const validation = validateSkillContext(skills);
    if (!validation.valid) {
      console.warn('⚠️ Skill validation warnings:', validation.errors);
    } else {
      console.log('✅ All skills loaded successfully');
    }
  } catch (error) {
    console.error('❌ Failed to load skills:', error);
  }
});

export { app };
