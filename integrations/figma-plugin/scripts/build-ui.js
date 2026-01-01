/**
 * Build script for the Figma plugin UI
 *
 * This script:
 * 1. Uses esbuild to bundle the modular JS from ui/scripts/main.js
 * 2. Reads the original ui.html (which has CSS + HTML + inline JS)
 * 3. Replaces the script section with the bundled JS
 * 4. Writes the result to dist/ui.html
 *
 * Usage: node scripts/build-ui.js
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const PLUGIN_DIR = path.resolve(__dirname, '..');
const UI_DIR = path.join(PLUGIN_DIR, 'ui');
const DIST_DIR = path.join(PLUGIN_DIR, 'dist');

// Ensure dist directory exists
if (!fs.existsSync(DIST_DIR)) {
  fs.mkdirSync(DIST_DIR, { recursive: true });
}

console.log('[Build] Starting UI build...');

// Step 1: Bundle the JS modules using esbuild
console.log('[Build] Bundling JS modules...');
const bundlePath = path.join(DIST_DIR, 'ui-bundle.js');
try {
  execSync(`npx esbuild "${path.join(UI_DIR, 'scripts/main.js')}" --bundle --outfile="${bundlePath}" --format=iife --target=es2015`, {
    cwd: PLUGIN_DIR,
    stdio: 'inherit'
  });
} catch (error) {
  console.error('[Build] Failed to bundle JS:', error.message);
  process.exit(1);
}

// Read the bundled JS
const bundledJS = fs.readFileSync(bundlePath, 'utf-8');
console.log('[Build] Bundle size:', (bundledJS.length / 1024).toFixed(2), 'KB');

// Step 2: Read the original ui.html
console.log('[Build] Reading original ui.html...');
const originalHtml = fs.readFileSync(path.join(PLUGIN_DIR, 'ui.html'), 'utf-8');

// Step 3: Find and replace the script section
// Look for BUILD_PLACEHOLDER marker or use lastIndexOf for script tags
const scriptStart = originalHtml.lastIndexOf('<script>');
const scriptEnd = originalHtml.lastIndexOf('</script>');

if (scriptStart === -1 || scriptEnd === -1) {
  console.error('[Build] Could not find script tags in ui.html');
  process.exit(1);
}

const beforeScript = originalHtml.substring(0, scriptStart);
const afterScript = originalHtml.substring(scriptEnd + '</script>'.length);

const newHtml = `${beforeScript}<script>\n${bundledJS}\n</script>${afterScript}`;

fs.writeFileSync(path.join(DIST_DIR, 'ui.html'), newHtml);
console.log('[Build] Created dist/ui.html with bundled JS (' + (newHtml.length / 1024).toFixed(2) + ' KB)');

// Clean up the intermediate bundle file
try {
  fs.unlinkSync(bundlePath);
  console.log('[Build] Cleaned up intermediate files');
} catch (e) {
  // Ignore cleanup errors
}

console.log('[Build] ✅ UI build complete!');
