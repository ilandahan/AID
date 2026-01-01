/**
 * HTML Sanitization Utilities
 * Prevents XSS attacks by escaping HTML special characters
 */

/**
 * Escape HTML special characters to prevent XSS
 * @param {string|any} unsafe - Value to sanitize
 * @returns {string} Sanitized string safe for HTML insertion
 */
export function escapeHtml(unsafe) {
  if (unsafe === null || unsafe === undefined) return '';
  if (typeof unsafe !== 'string') {
    unsafe = String(unsafe);
  }
  return unsafe
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

/**
 * Sanitize an object's string values recursively
 * @param {Object} obj - Object with potentially unsafe values
 * @returns {Object} Object with sanitized string values
 */
export function sanitizeObject(obj) {
  if (!obj || typeof obj !== 'object') return obj;

  const sanitized = {};
  for (const key of Object.keys(obj)) {
    if (!Object.hasOwn(obj, key)) continue;

    const value = obj[key];
    if (typeof value === 'string') {
      sanitized[key] = escapeHtml(value);
    } else if (Array.isArray(value)) {
      sanitized[key] = value.map(v => typeof v === 'string' ? escapeHtml(v) : v);
    } else if (typeof value === 'object' && value !== null) {
      sanitized[key] = sanitizeObject(value);
    } else {
      sanitized[key] = value;
    }
  }
  return sanitized;
}
