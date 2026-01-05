/**
 * OTP Store - Manages one-time pairing codes for Figma plugin authentication
 * 
 * Security features:
 * - Codes expire after 5 minutes
 * - Single use only
 * - Maximum 3 attempts per code
 * - Rate limiting per source
 */

interface OTPEntry {
  code: string;
  tenantId: string;
  projectPath: string;
  source: string;
  createdAt: number;
  expiresAt: number;
  attempts: number;
  used: boolean;
}

// In-memory store (use Redis in production for multi-instance)
const otpStore = new Map<string, OTPEntry>();

// Rate limiting per source
const rateLimits = new Map<string, { count: number; resetAt: number }>();

const OTP_EXPIRY_MS = 5 * 60 * 1000; // 5 minutes
const MAX_ATTEMPTS = 3;
const RATE_LIMIT_WINDOW_MS = 60 * 1000; // 1 minute
const RATE_LIMIT_MAX_REQUESTS = 5;

/**
 * Generate a 6-digit OTP code
 */
function generateCode(): string {
  const code = Math.floor(100000 + Math.random() * 900000).toString();
  return code;
}

/**
 * Check rate limit for a source
 */
function checkRateLimit(source: string): boolean {
  const now = Date.now();
  const limit = rateLimits.get(source);
  
  if (!limit || now > limit.resetAt) {
    rateLimits.set(source, { count: 1, resetAt: now + RATE_LIMIT_WINDOW_MS });
    return true;
  }
  
  if (limit.count >= RATE_LIMIT_MAX_REQUESTS) {
    return false;
  }
  
  limit.count++;
  return true;
}

/**
 * Create a new OTP for pairing
 */
export function createOTP(tenantId: string, projectPath: string, source: string): { success: boolean; code?: string; error?: string } {
  // Check rate limit
  if (!checkRateLimit(source)) {
    return { success: false, error: 'Rate limit exceeded. Please wait 1 minute.' };
  }

  // Generate unique code
  let code = generateCode();
  let attempts = 0;
  while (otpStore.has(code) && attempts < 10) {
    code = generateCode();
    attempts++;
  }

  const now = Date.now();
  const entry: OTPEntry = {
    code,
    tenantId,
    projectPath,
    source,
    createdAt: now,
    expiresAt: now + OTP_EXPIRY_MS,
    attempts: 0,
    used: false
  };

  otpStore.set(code, entry);

  // Cleanup expired entries periodically
  cleanupExpired();

  return { success: true, code };
}

/**
 * Validate an OTP code and return tenant info if valid
 */
export function validateOTP(code: string): { 
  success: boolean; 
  tenantId?: string; 
  projectPath?: string;
  error?: string 
} {
  const entry = otpStore.get(code);

  if (!entry) {
    return { success: false, error: 'Invalid code' };
  }

  if (entry.used) {
    return { success: false, error: 'Code already used' };
  }

  if (Date.now() > entry.expiresAt) {
    otpStore.delete(code);
    return { success: false, error: 'Code expired' };
  }

  entry.attempts++;
  if (entry.attempts > MAX_ATTEMPTS) {
    otpStore.delete(code);
    return { success: false, error: 'Too many attempts. Please generate a new code.' };
  }

  // Mark as used and return success
  entry.used = true;
  
  return { 
    success: true, 
    tenantId: entry.tenantId,
    projectPath: entry.projectPath
  };
}

/**
 * Clean up expired OTP entries
 */
function cleanupExpired(): void {
  const now = Date.now();
  for (const [code, entry] of otpStore.entries()) {
    if (now > entry.expiresAt || entry.used) {
      otpStore.delete(code);
    }
  }
}

/**
 * Get stats for monitoring
 */
export function getStats(): { activeOTPs: number; } {
  cleanupExpired();
  return {
    activeOTPs: otpStore.size
  };
}
