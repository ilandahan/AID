/**
 * Toast Notifications
 * Simple toast message display
 */

import { $ } from '../state.js';

/**
 * Show a toast message
 * @param {string} msg - Message to display
 * @param {number} duration - Duration in ms (default 3000)
 */
export function showToast(msg, duration = 3000) {
  const toast = $('toast');
  if (toast) {
    toast.textContent = msg;
    toast.classList.add('show');
    setTimeout(() => toast.classList.remove('show'), duration);
  } else {
    console.log('[Toast]', msg);
  }
}
