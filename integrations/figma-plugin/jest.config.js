/**
 * @file jest.config.js
 * @description Jest configuration for Figma plugin unit tests
 */

/** @type {import('jest').Config} */
module.exports = {
  // Test environment - Node since Figma plugin runs in a sandbox
  testEnvironment: 'node',

  // TypeScript support
  preset: 'ts-jest',

  // Root directory
  rootDir: '.',

  // Test patterns
  testMatch: [
    '**/__tests__/**/*.test.ts',
    '**/__tests__/**/*.spec.ts',
    '**/__tests__/**/*.test.js',
    '**/__tests__/**/*.spec.js',
  ],

  // Ignore patterns
  testPathIgnorePatterns: [
    '/node_modules/',
    '/dist/',
    '/server/',
  ],

  // Transform settings
  transform: {
    '^.+\\.tsx?$': ['ts-jest', {
      tsconfig: {
        target: 'ES2020',
        module: 'ESNext',
        moduleResolution: 'node',
        esModuleInterop: true,
        strict: false,
        noImplicitAny: false,
        skipLibCheck: true,
        types: ['jest', 'node'],
        typeRoots: ['./node_modules/@types', './__tests__'],
      },
    }],
    '^.+\\.jsx?$': 'babel-jest',
  },

  // Allow ES modules in JavaScript files
  transformIgnorePatterns: [
    '/node_modules/',
  ],

  // Coverage configuration
  collectCoverageFrom: [
    '**/*.ts',
    '!**/*.d.ts',
    '!**/node_modules/**',
    '!**/dist/**',
    '!**/__tests__/**',
    '!**/server/**',
    '!jest.config.js',
  ],

  // Verbose output
  verbose: true,

  // Clear mocks between tests
  clearMocks: true,

  // Coverage thresholds (start low, increase over time)
  coverageThreshold: {
    global: {
      branches: 50,
      functions: 50,
      lines: 50,
      statements: 50,
    },
  },
};
