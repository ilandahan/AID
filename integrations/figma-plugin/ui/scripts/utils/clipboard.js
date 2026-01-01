/**
 * Clipboard Utilities
 * Safe clipboard handling for Figma iframe environment
 */

import { showToast } from './toast.js';

/**
 * Copy text to clipboard with fallback for Figma iframe
 * @param {string} text - Text to copy
 */
export function copyToClipboard(text) {
  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(text).then(() => {
      showToast('Copied to clipboard');
    }).catch(err => {
      console.error('[UI] Clipboard write failed:', err);
      fallbackCopyToClipboard(text);
    });
  } else {
    fallbackCopyToClipboard(text);
  }
}

/**
 * Fallback clipboard method using textarea + execCommand
 * @param {string} text - Text to copy
 */
function fallbackCopyToClipboard(text) {
  const textarea = document.createElement('textarea');
  textarea.value = text;
  textarea.style.position = 'fixed';
  textarea.style.left = '-9999px';
  document.body.appendChild(textarea);
  textarea.select();
  try {
    document.execCommand('copy');
    showToast('Copied to clipboard');
  } catch (err) {
    console.error('[UI] Fallback copy failed:', err);
    showToast('Copy failed - please copy manually');
  }
  document.body.removeChild(textarea);
}
