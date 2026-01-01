/**
 * @file AuthService.ts
 * @description Authentication service for the Figma plugin supporting API Key, OAuth, and JWT flows.
 * @created 2024-12
 * @refactored 2024-12 - Extracted modules to ./services/AuthService/
 *
 * This file re-exports the modular AuthService for backward compatibility.
 * The actual implementation is in ./services/AuthService/
 */

// Re-export everything from the modular implementation
export {
  // Main class and singleton
  AuthService,
  authService,

  // Types
  type AuthMethod,
  type AuthConfig,
  type OAuthConfig,
  type AuthResult,
  type UserInfo,

  // Constants
  STORAGE_KEYS,
} from './services/AuthService';

// Default export for backward compatibility
export { AuthService as default } from './services/AuthService';
