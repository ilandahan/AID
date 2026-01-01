/**
 * @file __tests__/AuthService.test.ts
 * @description Comprehensive tests for AuthService modules
 *
 * Tests cover:
 * - Types and constants
 * - Request signing and auth headers
 * - Token expiration checking
 */

import {
  getAuthHeaders,
  signMCPRequest,
  isTokenExpired,
} from '../services/AuthService/signing';

import type {
  AuthMethod,
  AuthConfig,
  OAuthConfig,
  AuthResult,
  UserInfo,
} from '../services/AuthService/types';

import { STORAGE_KEYS } from '../services/AuthService/types';

import type { MCPRequest } from '../types';

// ============================================================================
// Test Helpers
// ============================================================================

/**
 * Create a mock AuthConfig for API key auth
 */
function mockApiKeyConfig(overrides: Partial<AuthConfig> = {}): AuthConfig {
  return {
    method: 'api_key',
    apiKey: 'test-api-key-123',
    tenantId: 'tenant-456',
    ...overrides,
  };
}

/**
 * Create a mock AuthConfig for OAuth auth
 */
function mockOAuthConfig(overrides: Partial<AuthConfig> = {}): AuthConfig {
  return {
    method: 'oauth',
    accessToken: 'oauth-access-token-xyz',
    refreshToken: 'oauth-refresh-token-abc',
    tenantId: 'tenant-456',
    expiresAt: Date.now() + 3600 * 1000, // 1 hour from now
    ...overrides,
  };
}

/**
 * Create a mock AuthConfig for JWT auth
 */
function mockJWTConfig(overrides: Partial<AuthConfig> = {}): AuthConfig {
  return {
    method: 'jwt',
    accessToken: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test-jwt-token',
    tenantId: 'tenant-456',
    expiresAt: Date.now() + 3600 * 1000, // 1 hour from now
    ...overrides,
  };
}

/**
 * Create a mock MCPRequest
 */
function mockMCPRequest(overrides: Partial<MCPRequest> = {}): MCPRequest {
  return {
    jsonrpc: '2.0',
    id: 1,
    method: 'test/method',
    params: { foo: 'bar' },
    ...overrides,
  } as MCPRequest;
}

/**
 * Create a mock UserInfo
 */
function mockUserInfo(overrides: Partial<UserInfo> = {}): UserInfo {
  return {
    id: 'user-123',
    email: 'test@example.com',
    name: 'Test User',
    tenantId: 'tenant-456',
    roles: ['user', 'editor'],
    ...overrides,
  };
}

// ============================================================================
// Types Tests
// ============================================================================

describe('AuthService Types', () => {
  describe('AuthMethod', () => {
    it('should accept valid auth methods', () => {
      const methods: AuthMethod[] = ['api_key', 'oauth', 'jwt'];
      expect(methods).toHaveLength(3);
    });
  });

  describe('AuthConfig', () => {
    it('should accept API key config', () => {
      const config: AuthConfig = {
        method: 'api_key',
        apiKey: 'test-key',
        tenantId: 'tenant-1',
      };
      expect(config.method).toBe('api_key');
    });

    it('should accept OAuth config', () => {
      const config: AuthConfig = {
        method: 'oauth',
        accessToken: 'token',
        refreshToken: 'refresh',
        expiresAt: Date.now() + 3600000,
        oauthProvider: 'auth0',
      };
      expect(config.method).toBe('oauth');
    });

    it('should accept JWT config', () => {
      const config: AuthConfig = {
        method: 'jwt',
        accessToken: 'jwt-token',
        expiresAt: Date.now() + 3600000,
      };
      expect(config.method).toBe('jwt');
    });
  });

  describe('STORAGE_KEYS', () => {
    it('should define all required storage keys', () => {
      expect(STORAGE_KEYS.AUTH_CONFIG).toBeDefined();
      expect(STORAGE_KEYS.TENANT_ID).toBeDefined();
      expect(STORAGE_KEYS.API_KEY).toBeDefined();
      expect(STORAGE_KEYS.ACCESS_TOKEN).toBeDefined();
      expect(STORAGE_KEYS.REFRESH_TOKEN).toBeDefined();
      expect(STORAGE_KEYS.TOKEN_EXPIRY).toBeDefined();
      expect(STORAGE_KEYS.OAUTH_STATE).toBeDefined();
      expect(STORAGE_KEYS.OAUTH_CODE_VERIFIER).toBeDefined();
    });

    it('should have unique key values', () => {
      const values = Object.values(STORAGE_KEYS);
      const uniqueValues = new Set(values);
      expect(uniqueValues.size).toBe(values.length);
    });

    it('should have consistent prefix', () => {
      const authKeys = [
        STORAGE_KEYS.AUTH_CONFIG,
        STORAGE_KEYS.TENANT_ID,
        STORAGE_KEYS.API_KEY,
        STORAGE_KEYS.ACCESS_TOKEN,
        STORAGE_KEYS.REFRESH_TOKEN,
        STORAGE_KEYS.TOKEN_EXPIRY,
      ];

      for (const key of authKeys) {
        expect(key).toContain('atomic_extractor_');
      }
    });
  });
});

// ============================================================================
// Signing Module Tests
// ============================================================================

describe('AuthService Signing', () => {
  describe('getAuthHeaders', () => {
    describe('API Key authentication', () => {
      it('should include X-Tenant-ID header', () => {
        const config = mockApiKeyConfig();
        const headers = getAuthHeaders(config);

        expect(headers['X-Tenant-ID']).toBe('tenant-456');
      });

      it('should include X-API-Key header', () => {
        const config = mockApiKeyConfig();
        const headers = getAuthHeaders(config);

        expect(headers['X-API-Key']).toBe('test-api-key-123');
      });

      it('should not include Authorization header', () => {
        const config = mockApiKeyConfig();
        const headers = getAuthHeaders(config);

        expect(headers['Authorization']).toBeUndefined();
      });
    });

    describe('OAuth authentication', () => {
      it('should include Bearer token in Authorization header', () => {
        const config = mockOAuthConfig();
        const headers = getAuthHeaders(config);

        expect(headers['Authorization']).toBe('Bearer oauth-access-token-xyz');
      });

      it('should include X-Tenant-ID when tenantId is present', () => {
        const config = mockOAuthConfig();
        const headers = getAuthHeaders(config);

        expect(headers['X-Tenant-ID']).toBe('tenant-456');
      });

      it('should not include X-API-Key header', () => {
        const config = mockOAuthConfig();
        const headers = getAuthHeaders(config);

        expect(headers['X-API-Key']).toBeUndefined();
      });
    });

    describe('JWT authentication', () => {
      it('should include Bearer token in Authorization header', () => {
        const config = mockJWTConfig();
        const headers = getAuthHeaders(config);

        expect(headers['Authorization']).toContain('Bearer');
        expect(headers['Authorization']).toContain('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9');
      });

      it('should include tenant ID when present', () => {
        const config = mockJWTConfig();
        const headers = getAuthHeaders(config);

        expect(headers['X-Tenant-ID']).toBe('tenant-456');
      });
    });

    describe('Security headers', () => {
      it('should include timestamp', () => {
        const config = mockApiKeyConfig();
        const headers = getAuthHeaders(config);

        expect(headers['X-Timestamp']).toBeDefined();
        expect(parseInt(headers['X-Timestamp'])).toBeLessThanOrEqual(Date.now());
      });

      it('should include nonce', () => {
        const config = mockApiKeyConfig();
        const headers = getAuthHeaders(config);

        expect(headers['X-Nonce']).toBeDefined();
        expect(headers['X-Nonce'].length).toBeGreaterThan(0);
      });

      it('should generate unique nonce on each call', () => {
        const config = mockApiKeyConfig();
        const headers1 = getAuthHeaders(config);
        const headers2 = getAuthHeaders(config);

        expect(headers1['X-Nonce']).not.toBe(headers2['X-Nonce']);
      });
    });
  });

  describe('signMCPRequest', () => {
    it('should add _auth property to request', () => {
      const config = mockApiKeyConfig();
      const request = mockMCPRequest();

      const signedRequest = signMCPRequest(request, config);

      expect(signedRequest._auth).toBeDefined();
    });

    it('should preserve original request properties', () => {
      const config = mockApiKeyConfig();
      const request = mockMCPRequest({
        method: 'components/analyze',
        params: { nodeId: 'node-123' },
      });

      const signedRequest = signMCPRequest(request, config);

      expect(signedRequest.jsonrpc).toBe('2.0');
      expect(signedRequest.method).toBe('components/analyze');
      expect(signedRequest.params).toEqual({ nodeId: 'node-123' });
    });

    it('should include auth headers in _auth', () => {
      const config = mockApiKeyConfig();
      const request = mockMCPRequest();

      const signedRequest = signMCPRequest(request, config);

      expect(signedRequest._auth['X-Tenant-ID']).toBe('tenant-456');
      expect(signedRequest._auth['X-API-Key']).toBe('test-api-key-123');
    });

    it('should work with OAuth config', () => {
      const config = mockOAuthConfig();
      const request = mockMCPRequest();

      const signedRequest = signMCPRequest(request, config);

      expect(signedRequest._auth['Authorization']).toContain('Bearer');
    });
  });

  describe('isTokenExpired', () => {
    it('should return false when expiresAt is not set', () => {
      const config = mockApiKeyConfig({ expiresAt: undefined });

      expect(isTokenExpired(config)).toBe(false);
    });

    it('should return false when token is not expired', () => {
      const futureTime = Date.now() + 3600 * 1000; // 1 hour from now
      const config = mockOAuthConfig({ expiresAt: futureTime });

      expect(isTokenExpired(config)).toBe(false);
    });

    it('should return true when token is expired', () => {
      const pastTime = Date.now() - 1000; // 1 second ago
      const config = mockOAuthConfig({ expiresAt: pastTime });

      expect(isTokenExpired(config)).toBe(true);
    });

    it('should handle exact expiration time', () => {
      const now = Date.now();
      const config = mockOAuthConfig({ expiresAt: now - 1 }); // Just expired

      expect(isTokenExpired(config)).toBe(true);
    });

    it('should work with JWT config', () => {
      const futureTime = Date.now() + 7200 * 1000; // 2 hours from now
      const config = mockJWTConfig({ expiresAt: futureTime });

      expect(isTokenExpired(config)).toBe(false);
    });
  });
});

// ============================================================================
// UserInfo Tests
// ============================================================================

describe('AuthService UserInfo', () => {
  it('should accept valid user info', () => {
    const user: UserInfo = mockUserInfo();

    expect(user.id).toBe('user-123');
    expect(user.email).toBe('test@example.com');
    expect(user.name).toBe('Test User');
    expect(user.tenantId).toBe('tenant-456');
    expect(user.roles).toContain('user');
  });

  it('should support multiple roles', () => {
    const user: UserInfo = mockUserInfo({
      roles: ['admin', 'developer', 'designer'],
    });

    expect(user.roles).toHaveLength(3);
    expect(user.roles).toContain('admin');
  });

  it('should support empty roles array', () => {
    const user: UserInfo = mockUserInfo({ roles: [] });

    expect(user.roles).toHaveLength(0);
  });
});

// ============================================================================
// AuthResult Tests
// ============================================================================

describe('AuthService AuthResult', () => {
  it('should represent successful auth', () => {
    const result: AuthResult = {
      success: true,
      user: mockUserInfo(),
    };

    expect(result.success).toBe(true);
    expect(result.user).toBeDefined();
    expect(result.error).toBeUndefined();
  });

  it('should represent failed auth with error', () => {
    const result: AuthResult = {
      success: false,
      error: 'Invalid credentials',
    };

    expect(result.success).toBe(false);
    expect(result.error).toBe('Invalid credentials');
    expect(result.user).toBeUndefined();
  });
});

// ============================================================================
// OAuthConfig Tests
// ============================================================================

describe('AuthService OAuthConfig', () => {
  it('should accept valid OAuth config', () => {
    const config: OAuthConfig = {
      clientId: 'client-123',
      authorizationEndpoint: 'https://auth.example.com/authorize',
      tokenEndpoint: 'https://auth.example.com/token',
      redirectUri: 'figma://oauth-callback',
      scope: 'openid profile email',
    };

    expect(config.clientId).toBe('client-123');
    expect(config.scope).toContain('openid');
  });

  it('should require all properties', () => {
    const config: OAuthConfig = {
      clientId: 'client-id',
      authorizationEndpoint: 'https://auth.example.com/authorize',
      tokenEndpoint: 'https://auth.example.com/token',
      redirectUri: 'https://redirect.example.com',
      scope: 'read write',
    };

    expect(Object.keys(config)).toHaveLength(5);
  });
});

// ============================================================================
// Integration Tests
// ============================================================================

describe('AuthService Integration', () => {
  describe('API Key workflow', () => {
    it('should create valid headers for API key auth', () => {
      const config = mockApiKeyConfig({
        apiKey: 'prod-api-key',
        tenantId: 'acme-corp',
      });

      const headers = getAuthHeaders(config);

      expect(headers['X-API-Key']).toBe('prod-api-key');
      expect(headers['X-Tenant-ID']).toBe('acme-corp');
      expect(headers['X-Timestamp']).toBeDefined();
      expect(headers['X-Nonce']).toBeDefined();
    });

    it('should sign MCP requests correctly', () => {
      const config = mockApiKeyConfig();
      const request = mockMCPRequest({
        method: 'components/export',
        params: { componentId: 'btn-primary' },
      });

      const signed = signMCPRequest(request, config);

      expect(signed.method).toBe('components/export');
      expect(signed._auth['X-API-Key']).toBeDefined();
    });
  });

  describe('OAuth workflow', () => {
    it('should handle fresh OAuth token', () => {
      const config = mockOAuthConfig({
        expiresAt: Date.now() + 7200 * 1000, // 2 hours
      });

      expect(isTokenExpired(config)).toBe(false);

      const headers = getAuthHeaders(config);
      expect(headers['Authorization']).toContain('Bearer');
    });

    it('should detect expired OAuth token', () => {
      const config = mockOAuthConfig({
        expiresAt: Date.now() - 60 * 1000, // 1 minute ago
      });

      expect(isTokenExpired(config)).toBe(true);
    });
  });

  describe('JWT workflow', () => {
    it('should handle valid JWT', () => {
      const config = mockJWTConfig({
        expiresAt: Date.now() + 3600 * 1000,
      });

      expect(isTokenExpired(config)).toBe(false);

      const headers = getAuthHeaders(config);
      expect(headers['Authorization']).toContain('Bearer');
      expect(headers['Authorization']).toContain('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9');
    });
  });

  describe('Cross-method consistency', () => {
    it('should always include security headers regardless of auth method', () => {
      const configs = [
        mockApiKeyConfig(),
        mockOAuthConfig(),
        mockJWTConfig(),
      ];

      for (const config of configs) {
        const headers = getAuthHeaders(config);

        expect(headers['X-Timestamp']).toBeDefined();
        expect(headers['X-Nonce']).toBeDefined();
      }
    });
  });
});
