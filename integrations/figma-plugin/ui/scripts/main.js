/**
 * Main Entry Point
 * Initializes the Figma plugin UI
 */

import { initializeTranslations } from './utils/i18n.js';
import { initMessageHandler } from './handlers/messages.js';
import { initEventHandlers } from './handlers/events.js';
import { initPairingHandlers } from './handlers/pairing.js';

/**
 * Initialize the plugin UI
 */
function init() {
  console.log('[UI] Initializing Figma Plugin UI...');

  // Initialize translations
  initializeTranslations();

  // Initialize event handlers
  initEventHandlers();

  // Initialize pairing handlers (OTP input, Enter key, Pair button)
  initPairingHandlers();

  // Initialize message handler for Figma communication
  initMessageHandler();

  console.log('[UI] ✅ UI initialized successfully');
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}
