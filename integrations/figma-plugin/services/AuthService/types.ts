/**
 * @file services/AuthService/types.ts
 * @description Type definitions for authentication
 */

export type AuthMethod = 'api_key' | 'oauth' | 'jwt';

export interface AuthConfig {
  method: AuthMethod;
  apiKey?: string;
  tenantId?: string;
  accessToken?: string;
  refreshToken?: string;
  expiresAt?: number;
  oauthProvider?: 'auth0' | 'cognito' | 'okta' | 'custom';
  oauthConfig?: OAuthConfig;
}

export interface OAuthConfig {
  clientId: string;
  authorizationEndpoint: string;
  tokenEndpoint: string;
  redirectUri: string;
  scope: string;
}

export interface AuthResult {
  success: boolean;
  error?: string;
  user?: UserInfo;
}

export interface UserInfo {
  id: string;
  email: string;
  name: string;
  tenantId: string;
  roles: string[];
}

// Storage keys
export const STORAGE_KEYS = {
  AUTH_CONFIG: 'atomic_extractor_auth',
  TENANT_ID: 'atomic_extractor_tenant',
  API_KEY: 'atomic_extractor_api_key',
  ACCESS_TOKEN: 'atomic_extractor_access_token',
  REFRESH_TOKEN: 'atomic_extractor_refresh_token',
  TOKEN_EXPIRY: 'atomic_extractor_token_expiry',
  OAUTH_STATE: 'oauth_state',
  OAUTH_CODE_VERIFIER: 'oauth_code_verifier',
};
