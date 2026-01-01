/**
 * @file jest.config.js
 * @description Jest configuration for Figma plugin server tests
 *
 * Coverage Targets:
 * - Services (componentAuditor, scoringEngine, etc.): 95%+ achieved
 * - claudeClient: Lower coverage expected (requires API mocking)
 * - index.js: Covered by integration tests (requires running server)
 */

module.exports = {
  testEnvironment: 'node',
  testMatch: [
    '**/tests/**/*.test.js',
    '**/tests/**/*.spec.js'
  ],
  collectCoverageFrom: [
    'src/services/*.js',
    '!src/resources/**'
  ],
  coverageDirectory: 'coverage',
  coverageReporters: ['text', 'lcov', 'html'],
  coverageThreshold: {
    global: {
      branches: 70,
      functions: 90,
      lines: 80,
      statements: 80
    }
  },
  testTimeout: 10000,
  verbose: true
};
