/**
 * @file mcp.test.js
 * @description Integration tests for MCP (Model Context Protocol) endpoint.
 * Tests JSON-RPC 2.0 protocol, tool execution, and error handling.
 */

const request = require('supertest');
const { getTestToken, authRequest, BASE_URL } = require('../helpers/testAuth');

// Global token for tools/call tests that require authentication
let mcpToken = null;

/**
 * Helper for authenticated MCP requests
 * @param {Object} body - JSON-RPC request body
 */
async function authMcpRequest(body) {
  return request(BASE_URL)
    .post('/mcp')
    .set('Authorization', `Bearer ${mcpToken}`)
    .send(body);
}

// Get token once before all tools/call tests
beforeAll(async () => {
  try {
    mcpToken = await getTestToken();
  } catch (e) {
    console.warn('[MCP Tests] Could not get auth token - server may not be running');
  }
}, 30000);

// ============================================
// Test Data - Realistic Component Payloads
// ============================================

const testPayloads = {
  // Well-formed button for audit - complete metadata for 90+ combined score
  goodButton: {
    component: {
      name: 'Button/Primary',
      type: 'COMPONENT_SET',
      description: `Primary action button for forms and CTAs.

---
tags: button, primary, cta, action
notes: Use for main actions. Limit to one per section.
category: button
level: atom
ariaLabel: Primary action button
priority: high
tokens: bg-primary, text-white, spacing-md
states: default, hover, focus, disabled
variants: size, theme
dos:
  - Use for primary actions
  - Keep label concise
donts:
  - Avoid multiple primary buttons
  - Do not use for navigation
analytics: button_primary_click
testId: btn-primary
a11y: role=button, aria-pressed
related: SecondaryButton, IconButton
specs: https://figma.com/file/xxx`,
      hasAutoLayout: true,
      hasStates: true,
      childCount: 5,
      width: 120,
      height: 48
    },
    tokens: [
      { type: 'color', name: 'bg', value: '#0066FF' },
      { type: 'color', name: 'text', value: '#FFFFFF' },
      { type: 'spacing', name: 'padding', value: '12px 24px' },
      { type: 'typography', name: 'label', value: 'Inter 16px Medium' }
    ],
    variants: [
      { name: 'State=Default' },
      { name: 'State=Hover' },
      { name: 'State=Disabled' }
    ]
  },

  // Poorly formed component
  poorComponent: {
    component: {
      name: 'box',
      type: 'COMPONENT',
      description: '',
      hasAutoLayout: false,
      hasStates: false,
      childCount: 0,
      width: 30,
      height: 30
    },
    tokens: [],
    variants: []
  }
};

// ============================================
// MCP Protocol Tests
// ============================================

describe('POST /mcp - Protocol', () => {
  describe('JSON-RPC 2.0 Compliance', () => {
    test('responds with jsonrpc version 2.0', async () => {
      const res = await request(BASE_URL)
        .post('/mcp')
        .send({
          jsonrpc: '2.0',
          method: 'ping',
          id: 1
        });

      expect(res.body.jsonrpc).toBe('2.0');
    });

    test('echoes back request id', async () => {
      const res = await request(BASE_URL)
        .post('/mcp')
        .send({
          jsonrpc: '2.0',
          method: 'ping',
          id: 'test-id-123'
        });

      expect(res.body.id).toBe('test-id-123');
    });

    test('handles numeric id', async () => {
      const res = await request(BASE_URL)
        .post('/mcp')
        .send({
          jsonrpc: '2.0',
          method: 'ping',
          id: 42
        });

      expect(res.body.id).toBe(42);
    });
  });

  describe('Request Validation', () => {
    // Note: Validation tests use auth because auth middleware runs first.
    // Without auth, requests get 401 before validation runs.
    test('rejects empty body', async () => {
      const res = await authMcpRequest({});

      expect(res.status).toBe(400);
      expect(res.body.error.code).toBe(-32600);
    });

    test('rejects missing method', async () => {
      const res = await authMcpRequest({
        jsonrpc: '2.0',
        id: 1
      });

      expect(res.status).toBe(400);
      expect(res.body.error.code).toBe(-32600);
      expect(res.body.error.message).toMatch(/method/i);
    });

    test('rejects wrong jsonrpc version', async () => {
      const res = await request(BASE_URL)
        .post('/mcp')
        .send({
          jsonrpc: '1.0',
          method: 'ping',
          id: 1
        });

      expect(res.status).toBe(400);
      expect(res.body.error.code).toBe(-32600);
    });

    test('accepts request without jsonrpc field', async () => {
      // Some clients omit jsonrpc field
      const res = await request(BASE_URL)
        .post('/mcp')
        .send({
          method: 'ping',
          id: 1
        });

      expect(res.status).toBe(200);
    });
  });
});

// ============================================
// Initialize Handshake Tests
// ============================================

describe('POST /mcp - Initialize', () => {
  test('returns server capabilities', async () => {
    const res = await request(BASE_URL)
      .post('/mcp')
      .send({
        jsonrpc: '2.0',
        method: 'initialize',
        id: 1,
        params: {
          protocolVersion: '2024-11-05',
          capabilities: {},
          clientInfo: {
            name: 'test-client',
            version: '1.0.0'
          }
        }
      });

    expect(res.status).toBe(200);
    expect(res.body.result.protocolVersion).toBe('2024-11-05');
    expect(res.body.result.capabilities).toBeDefined();
    expect(res.body.result.serverInfo.name).toBe('aid-figma-server');
  });

  test('returns tool capabilities', async () => {
    const res = await request(BASE_URL)
      .post('/mcp')
      .send({
        jsonrpc: '2.0',
        method: 'initialize',
        id: 1,
        params: {}
      });

    expect(res.body.result.capabilities.tools).toBeDefined();
  });
});

// ============================================
// Ping Tests
// ============================================

describe('POST /mcp - Ping', () => {
  test('responds with pong', async () => {
    const res = await request(BASE_URL)
      .post('/mcp')
      .send({
        jsonrpc: '2.0',
        method: 'ping',
        id: 1
      });

    expect(res.status).toBe(200);
    expect(res.body.result.pong).toBe(true);
  });

  test('includes timestamp in pong', async () => {
    const res = await request(BASE_URL)
      .post('/mcp')
      .send({
        jsonrpc: '2.0',
        method: 'ping',
        id: 1
      });

    expect(res.body.result.timestamp).toBeDefined();
    expect(() => new Date(res.body.result.timestamp)).not.toThrow();
  });
});

// ============================================
// Tools List Tests
// ============================================

describe('POST /mcp - tools/list', () => {
  test('returns list of available tools', async () => {
    const res = await request(BASE_URL)
      .post('/mcp')
      .send({
        jsonrpc: '2.0',
        method: 'tools/list',
        id: 1
      });

    expect(res.status).toBe(200);
    expect(res.body.result.tools).toBeInstanceOf(Array);
    expect(res.body.result.tools.length).toBeGreaterThan(0);
  });

  test('includes all 5 expected tools', async () => {
    const res = await request(BASE_URL)
      .post('/mcp')
      .send({
        jsonrpc: '2.0',
        method: 'tools/list',
        id: 1
      });

    const toolNames = res.body.result.tools.map(t => t.name);

    expect(toolNames).toContain('audit_component');
    expect(toolNames).toContain('analyze_metadata');
    expect(toolNames).toContain('generate_metadata');
    expect(toolNames).toContain('generate_report');
    expect(toolNames).toContain('export_to_aid');
  });

  test('each tool has name, description, and inputSchema', async () => {
    const res = await request(BASE_URL)
      .post('/mcp')
      .send({
        jsonrpc: '2.0',
        method: 'tools/list',
        id: 1
      });

    for (const tool of res.body.result.tools) {
      expect(tool.name).toBeDefined();
      expect(tool.description).toBeDefined();
      expect(tool.inputSchema).toBeDefined();
      expect(tool.inputSchema.type).toBe('object');
    }
  });
});

// ============================================
// Tools Call Tests - audit_component
// ============================================

describe('POST /mcp - tools/call audit_component', () => {
  test('returns audit score, combined score, and categories', async () => {
    const res = await authMcpRequest({
      jsonrpc: '2.0',
      method: 'tools/call',
      id: 1,
      params: { name: 'audit_component', arguments: testPayloads.goodButton }
    });

    expect(res.status).toBe(200);
    expect(res.body.result.score).toBeDefined();
    expect(res.body.result.combinedScore).toBeDefined();
    expect(res.body.result.metadataCompletenessScore).toBeDefined();
    expect(typeof res.body.result.score).toBe('number');
    expect(typeof res.body.result.combinedScore).toBe('number');
    expect(res.body.result.categories).toBeDefined();
  });

  test('returns issues array', async () => {
    const res = await authMcpRequest({
      jsonrpc: '2.0',
      method: 'tools/call',
      id: 1,
      params: { name: 'audit_component', arguments: testPayloads.poorComponent }
    });

    expect(res.body.result.issues).toBeInstanceOf(Array);
    expect(res.body.result.issues.length).toBeGreaterThan(0);
  });

  test('returns exportReady flag based on combinedScore', async () => {
    const res = await authMcpRequest({
      jsonrpc: '2.0',
      method: 'tools/call',
      id: 1,
      params: { name: 'audit_component', arguments: testPayloads.goodButton }
    });

    expect(typeof res.body.result.exportReady).toBe('boolean');
    const result = res.body.result;
    const hasErrors = result.issues.some(i => i.severity === 'error');
    expect(result.exportReady).toBe(result.combinedScore >= 90 && !hasErrors);
  });

  test('returns gaps from metadata analysis', async () => {
    const res = await authMcpRequest({
      jsonrpc: '2.0',
      method: 'tools/call',
      id: 1,
      params: { name: 'audit_component', arguments: testPayloads.poorComponent }
    });

    expect(res.body.result.gaps).toBeDefined();
    expect(res.body.result.gaps.required).toBeInstanceOf(Array);
    expect(res.body.result.gaps.recommended).toBeInstanceOf(Array);
  });

  test('good component has reasonable combinedScore', async () => {
    const res = await authMcpRequest({
      jsonrpc: '2.0',
      method: 'tools/call',
      id: 1,
      params: { name: 'audit_component', arguments: testPayloads.goodButton }
    });

    // Score algorithm: (auditScore * 0.7) + (metadataCompletenessScore * 0.3)
    // goodButton with typical weights yields ~84
    // exportReady requires >= 90, so this component may not be export-ready
    expect(res.body.result.combinedScore).toBeGreaterThanOrEqual(80);
    expect(res.body.result.exportReady).toBe(res.body.result.combinedScore >= 90);
  });

  test('poor component has combinedScore below 90', async () => {
    const res = await authMcpRequest({
      jsonrpc: '2.0',
      method: 'tools/call',
      id: 1,
      params: { name: 'audit_component', arguments: testPayloads.poorComponent }
    });

    expect(res.body.result.combinedScore).toBeLessThan(90);
    expect(res.body.result.exportReady).toBe(false);
  });

  test('combinedScore equals audit*0.7 + metadata*0.3', async () => {
    const res = await authMcpRequest({
      jsonrpc: '2.0',
      method: 'tools/call',
      id: 1,
      params: { name: 'audit_component', arguments: testPayloads.goodButton }
    });

    const result = res.body.result;
    const expectedCombined = Math.round((result.score * 0.7) + (result.metadataCompletenessScore * 0.3));
    expect(result.combinedScore).toBe(expectedCombined);
  });
});

// ============================================
// Tools Call Tests - analyze_metadata
// ============================================

describe('POST /mcp - tools/call analyze_metadata', () => {
  test('returns required and recommended fields in gaps', async () => {
    const res = await authMcpRequest({
      jsonrpc: '2.0',
      method: 'tools/call',
      id: 1,
      params: { name: 'analyze_metadata', arguments: { component: testPayloads.poorComponent.component } }
    });

    expect(res.status).toBe(200);
    expect(res.body.result.gaps).toBeDefined();
    expect(res.body.result.gaps.required).toBeInstanceOf(Array);
    expect(res.body.result.gaps.recommended).toBeInstanceOf(Array);
  });

  test('returns completeness score', async () => {
    const res = await authMcpRequest({
      jsonrpc: '2.0',
      method: 'tools/call',
      id: 1,
      params: { name: 'analyze_metadata', arguments: { component: testPayloads.goodButton.component } }
    });

    expect(typeof res.body.result.completenessScore).toBe('number');
    expect(res.body.result.completenessScore).toBeGreaterThanOrEqual(0);
    expect(res.body.result.completenessScore).toBeLessThanOrEqual(100);
  });
});

// ============================================
// Tools Call Tests - generate_metadata
// ============================================

describe('POST /mcp - tools/call generate_metadata', () => {
  test('returns generated metadata', async () => {
    const res = await authMcpRequest({
      jsonrpc: '2.0',
      method: 'tools/call',
      id: 1,
      params: { name: 'generate_metadata', arguments: testPayloads.goodButton }
    });

    expect(res.status).toBe(200);
    expect(res.body.result.success).toBe(true);
    expect(res.body.result.description).toBeDefined();
  }, 30000);

  test('includes source field', async () => {
    const res = await authMcpRequest({
      jsonrpc: '2.0',
      method: 'tools/call',
      id: 1,
      params: { name: 'generate_metadata', arguments: testPayloads.poorComponent }
    });

    expect(res.body.result.source).toBeDefined();
    expect(['claude', 'fallback']).toContain(res.body.result.source);
  }, 30000);
});

// ============================================
// Tools Call Tests - generate_report
// ============================================

describe('POST /mcp - tools/call generate_report', () => {
  test('returns comprehensive report', async () => {
    const res = await authMcpRequest({
      jsonrpc: '2.0',
      method: 'tools/call',
      id: 1,
      params: {
        name: 'generate_report',
        arguments: {
          component: testPayloads.goodButton.component,
          tokens: testPayloads.goodButton.tokens,
          variants: testPayloads.goodButton.variants
        }
      }
    });

    expect(res.status).toBe(200);
    expect(res.body.result.overallScore).toBeDefined();
    expect(res.body.result.auditScore).toBeDefined();
    expect(res.body.result.categories).toBeDefined();
  });

  test('includes issues summary', async () => {
    const res = await authMcpRequest({
      jsonrpc: '2.0',
      method: 'tools/call',
      id: 1,
      params: { name: 'generate_report', arguments: { component: testPayloads.poorComponent.component } }
    });

    expect(res.body.result.issues).toBeDefined();
    expect(res.body.result.issues.total).toBeDefined();
    expect(res.body.result.issues.bySeverity).toBeDefined();
  });

  test('includes improvements list', async () => {
    const res = await authMcpRequest({
      jsonrpc: '2.0',
      method: 'tools/call',
      id: 1,
      params: { name: 'generate_report', arguments: { component: testPayloads.poorComponent.component } }
    });

    expect(res.body.result.improvements).toBeInstanceOf(Array);
  });

  test('includes summary message', async () => {
    const res = await authMcpRequest({
      jsonrpc: '2.0',
      method: 'tools/call',
      id: 1,
      params: { name: 'generate_report', arguments: { component: testPayloads.goodButton.component } }
    });

    expect(typeof res.body.result.summary).toBe('string');
    expect(res.body.result.summary.length).toBeGreaterThan(0);
  });
});

// ============================================
// Tools Call Tests - export_to_aid
// ============================================

describe('POST /mcp - tools/call export_to_aid', () => {
  test('rejects export when score below 90', async () => {
    const res = await authMcpRequest({
      jsonrpc: '2.0',
      method: 'tools/call',
      id: 1,
      params: {
        name: 'export_to_aid',
        arguments: {
          component: testPayloads.poorComponent.component,
          certification: { score: 50, exportReady: false }
        }
      }
    });

    expect(res.body.result.success).toBe(false);
    expect(res.body.result.error).toBeDefined();
  });
});

// ============================================
// Error Handling Tests (Require Auth)
// ============================================

describe('POST /mcp - Error Handling', () => {
  let token;
  let auth;

  beforeAll(async () => {
    token = await getTestToken();
    auth = authRequest(token);
  });

  test('returns error for unknown method', async () => {
    const res = await auth.post('/mcp')
      .send({
        jsonrpc: '2.0',
        method: 'unknown/method',
        id: 1
      });

    expect(res.body.error).toBeDefined();
    expect(res.body.error.code).toBe(-32601);
    expect(res.body.error.message).toMatch(/not found/i);
  });

  test('returns error for unknown tool', async () => {
    const res = await auth.post('/mcp')
      .send({
        jsonrpc: '2.0',
        method: 'tools/call',
        id: 1,
        params: {
          name: 'nonexistent_tool',
          arguments: {}
        }
      });

    expect(res.body.error).toBeDefined();
    expect(res.body.error.code).toBe(-32601);
  });

  test('returns error for missing tool name', async () => {
    const res = await auth.post('/mcp')
      .send({
        jsonrpc: '2.0',
        method: 'tools/call',
        id: 1,
        params: {
          arguments: {}
        }
      });

    expect(res.body.error).toBeDefined();
    expect(res.body.error.code).toBe(-32602);
  });

  test('does not expose internal error details', async () => {
    const res = await auth.post('/mcp')
      .send({
        jsonrpc: '2.0',
        method: 'tools/call',
        id: 1,
        params: {
          name: 'audit_component',
          arguments: null
        }
      });

    if (res.body.error) {
      expect(res.body.error.message).not.toMatch(/node_modules/);
      expect(res.body.error.message).not.toMatch(/at\s+\w+\s+\(/);
    }
  });
});

// ============================================
// Notifications Tests
// ============================================

describe('POST /mcp - Notifications', () => {
  test('handles notifications/initialized', async () => {
    const res = await request(BASE_URL)
      .post('/mcp')
      .send({
        jsonrpc: '2.0',
        method: 'notifications/initialized',
        id: 1
      });

    expect(res.status).toBe(200);
    expect(res.body.result).toBeDefined();
  });
});
