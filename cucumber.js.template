/**
 * Cucumber.js Configuration for AID Projects
 *
 * Profiles:
 * - default: Development with progress bar + HTML report
 * - ci: CI/CD with JUnit XML, strict mode, no WIP tests
 * - smoke: Quick validation (@smoke tags only)
 * - critical: Release gate (@critical tags only)
 *
 * Usage:
 *   npm run cucumber              # default profile
 *   npm run cucumber -- --profile ci
 *   npm run test:smoke
 *   npm run test:critical
 */
module.exports = {
  default: {
    // Where to find step definitions and support code
    require: [
      'features/step-definitions/**/*.ts',
      'features/step-definitions/**/*.js',
      'features/support/**/*.ts',
      'features/support/**/*.js'
    ],

    // Enable TypeScript
    requireModule: ['ts-node/register'],

    // Output formats
    format: [
      'progress-bar',
      'html:reports/cucumber-report.html',
      'json:reports/cucumber-report.json'
    ],

    // Generate async-await style snippets for undefined steps
    formatOptions: { snippetInterface: 'async-await' },

    // Don't prompt for Cucumber cloud publishing
    publishQuiet: true
  },

  ci: {
    require: [
      'features/step-definitions/**/*.ts',
      'features/support/**/*.ts'
    ],
    requireModule: ['ts-node/register'],
    format: [
      'progress',
      'html:reports/cucumber-report.html',
      'json:reports/cucumber-report.json',
      'junit:reports/cucumber-junit.xml'
    ],
    formatOptions: { snippetInterface: 'async-await' },
    publishQuiet: true,
    strict: true,
    tags: 'not @skip and not @wip and not @manual'
  },

  smoke: {
    require: [
      'features/step-definitions/**/*.ts',
      'features/support/**/*.ts'
    ],
    requireModule: ['ts-node/register'],
    format: ['progress'],
    publishQuiet: true,
    strict: true,
    tags: '@smoke'
  },

  critical: {
    require: [
      'features/step-definitions/**/*.ts',
      'features/support/**/*.ts'
    ],
    requireModule: ['ts-node/register'],
    format: ['progress-bar', 'html:reports/critical-report.html'],
    publishQuiet: true,
    strict: true,
    tags: '@critical'
  }
};
