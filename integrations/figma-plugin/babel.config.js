/**
 * Babel Configuration
 * Used by Jest for JavaScript test files
 */
module.exports = {
  presets: [
    ['@babel/preset-env', {
      targets: {
        node: 'current',
      },
    }],
  ],
};
