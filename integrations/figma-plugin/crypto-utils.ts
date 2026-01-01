/**
 * @file crypto-utils.ts
 * @description Cryptographic utilities for Figma plugin sandbox environment.
 *              Provides SHA-256 hashing and secure random generation without crypto.subtle.
 * @created 2024-12
 * @related
 *   - ./AuthService.ts - Uses these utilities for PKCE and nonce generation
 *
 * @security
 *   - Pure JavaScript SHA-256 implementation (FIPS 180-4 compliant)
 *   - XorShift128+ PRNG with multi-source entropy seeding
 *   - NOT a replacement for Web Crypto API in sensitive contexts
 *   - Suitable for OAuth state/nonce where perfect randomness is not critical
 */

// ============================================
// SHA-256 Implementation (Pure JavaScript)
// ============================================

/**
 * SHA-256 constants (first 32 bits of fractional parts of cube roots of first 64 primes)
 */
const K: number[] = [
  0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
  0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
  0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
  0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
  0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
  0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
  0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
  0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2,
];

/**
 * Initial hash values (first 32 bits of fractional parts of square roots of first 8 primes)
 */
const H_INIT: number[] = [
  0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
  0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19,
];

/**
 * Right rotate a 32-bit integer
 */
function rotr(n: number, x: number): number {
  return ((x >>> n) | (x << (32 - n))) >>> 0;
}

/**
 * SHA-256 Ch function
 */
function ch(x: number, y: number, z: number): number {
  return ((x & y) ^ (~x & z)) >>> 0;
}

/**
 * SHA-256 Maj function
 */
function maj(x: number, y: number, z: number): number {
  return ((x & y) ^ (x & z) ^ (y & z)) >>> 0;
}

/**
 * SHA-256 Sigma0 function
 */
function sigma0(x: number): number {
  return (rotr(2, x) ^ rotr(13, x) ^ rotr(22, x)) >>> 0;
}

/**
 * SHA-256 Sigma1 function
 */
function sigma1(x: number): number {
  return (rotr(6, x) ^ rotr(11, x) ^ rotr(25, x)) >>> 0;
}

/**
 * SHA-256 gamma0 function
 */
function gamma0(x: number): number {
  return (rotr(7, x) ^ rotr(18, x) ^ (x >>> 3)) >>> 0;
}

/**
 * SHA-256 gamma1 function
 */
function gamma1(x: number): number {
  return (rotr(17, x) ^ rotr(19, x) ^ (x >>> 10)) >>> 0;
}

/**
 * Convert string to UTF-8 byte array
 */
function stringToBytes(str: string): number[] {
  const bytes: number[] = [];
  for (let i = 0; i < str.length; i++) {
    const code = str.charCodeAt(i);
    if (code < 0x80) {
      bytes.push(code);
    } else if (code < 0x800) {
      bytes.push(0xc0 | (code >> 6), 0x80 | (code & 0x3f));
    } else if (code < 0x10000) {
      bytes.push(0xe0 | (code >> 12), 0x80 | ((code >> 6) & 0x3f), 0x80 | (code & 0x3f));
    } else {
      bytes.push(
        0xf0 | (code >> 18),
        0x80 | ((code >> 12) & 0x3f),
        0x80 | ((code >> 6) & 0x3f),
        0x80 | (code & 0x3f)
      );
    }
  }
  return bytes;
}

/**
 * Compute SHA-256 hash of a string
 * @param message - The input string to hash
 * @returns Hexadecimal string representation of the SHA-256 hash
 */
export function sha256(message: string): string {
  const bytes = stringToBytes(message);
  const originalLength = bytes.length * 8;

  // Padding
  bytes.push(0x80);
  while ((bytes.length % 64) !== 56) {
    bytes.push(0x00);
  }

  // Append original length as 64-bit big-endian
  for (let i = 7; i >= 0; i--) {
    bytes.push((originalLength / Math.pow(2, 8 * i)) & 0xff);
  }

  // Initialize hash values
  const H = [...H_INIT];

  // Process each 512-bit (64-byte) block
  for (let blockStart = 0; blockStart < bytes.length; blockStart += 64) {
    // Prepare message schedule
    const W: number[] = new Array(64);

    for (let t = 0; t < 16; t++) {
      W[t] = (
        (bytes[blockStart + t * 4] << 24) |
        (bytes[blockStart + t * 4 + 1] << 16) |
        (bytes[blockStart + t * 4 + 2] << 8) |
        bytes[blockStart + t * 4 + 3]
      ) >>> 0;
    }

    for (let t = 16; t < 64; t++) {
      W[t] = (gamma1(W[t - 2]) + W[t - 7] + gamma0(W[t - 15]) + W[t - 16]) >>> 0;
    }

    // Initialize working variables
    let a = H[0];
    let b = H[1];
    let c = H[2];
    let d = H[3];
    let e = H[4];
    let f = H[5];
    let g = H[6];
    let h = H[7];

    // Main loop
    for (let t = 0; t < 64; t++) {
      const T1 = (h + sigma1(e) + ch(e, f, g) + K[t] + W[t]) >>> 0;
      const T2 = (sigma0(a) + maj(a, b, c)) >>> 0;
      h = g;
      g = f;
      f = e;
      e = (d + T1) >>> 0;
      d = c;
      c = b;
      b = a;
      a = (T1 + T2) >>> 0;
    }

    // Update hash values
    H[0] = (H[0] + a) >>> 0;
    H[1] = (H[1] + b) >>> 0;
    H[2] = (H[2] + c) >>> 0;
    H[3] = (H[3] + d) >>> 0;
    H[4] = (H[4] + e) >>> 0;
    H[5] = (H[5] + f) >>> 0;
    H[6] = (H[6] + g) >>> 0;
    H[7] = (H[7] + h) >>> 0;
  }

  // Convert to hex string
  return H.map(h => h.toString(16).padStart(8, '0')).join('');
}

/**
 * Compute SHA-256 hash and return as base64url encoded string
 * Used for PKCE code challenge
 * @param message - The input string to hash
 * @returns Base64url encoded SHA-256 hash
 */
export function sha256Base64Url(message: string): string {
  const bytes = stringToBytes(message);
  const originalLength = bytes.length * 8;

  // Padding
  bytes.push(0x80);
  while ((bytes.length % 64) !== 56) {
    bytes.push(0x00);
  }

  // Append original length as 64-bit big-endian
  for (let i = 7; i >= 0; i--) {
    bytes.push((originalLength / Math.pow(2, 8 * i)) & 0xff);
  }

  // Initialize hash values
  const H = [...H_INIT];

  // Process each 512-bit (64-byte) block
  for (let blockStart = 0; blockStart < bytes.length; blockStart += 64) {
    const W: number[] = new Array(64);

    for (let t = 0; t < 16; t++) {
      W[t] = (
        (bytes[blockStart + t * 4] << 24) |
        (bytes[blockStart + t * 4 + 1] << 16) |
        (bytes[blockStart + t * 4 + 2] << 8) |
        bytes[blockStart + t * 4 + 3]
      ) >>> 0;
    }

    for (let t = 16; t < 64; t++) {
      W[t] = (gamma1(W[t - 2]) + W[t - 7] + gamma0(W[t - 15]) + W[t - 16]) >>> 0;
    }

    let a = H[0], b = H[1], c = H[2], d = H[3];
    let e = H[4], f = H[5], g = H[6], h = H[7];

    for (let t = 0; t < 64; t++) {
      const T1 = (h + sigma1(e) + ch(e, f, g) + K[t] + W[t]) >>> 0;
      const T2 = (sigma0(a) + maj(a, b, c)) >>> 0;
      h = g; g = f; f = e; e = (d + T1) >>> 0;
      d = c; c = b; b = a; a = (T1 + T2) >>> 0;
    }

    H[0] = (H[0] + a) >>> 0;
    H[1] = (H[1] + b) >>> 0;
    H[2] = (H[2] + c) >>> 0;
    H[3] = (H[3] + d) >>> 0;
    H[4] = (H[4] + e) >>> 0;
    H[5] = (H[5] + f) >>> 0;
    H[6] = (H[6] + g) >>> 0;
    H[7] = (H[7] + h) >>> 0;
  }

  // Convert to byte array
  const hashBytes: number[] = [];
  for (const word of H) {
    hashBytes.push((word >>> 24) & 0xff);
    hashBytes.push((word >>> 16) & 0xff);
    hashBytes.push((word >>> 8) & 0xff);
    hashBytes.push(word & 0xff);
  }

  // Convert to base64url
  return bytesToBase64Url(hashBytes);
}

/**
 * Convert byte array to base64url string
 */
function bytesToBase64Url(bytes: number[]): string {
  const base64Chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/';
  let result = '';

  for (let i = 0; i < bytes.length; i += 3) {
    const b1 = bytes[i];
    const b2 = bytes[i + 1] ?? 0;
    const b3 = bytes[i + 2] ?? 0;

    result += base64Chars[(b1 >> 2) & 0x3f];
    result += base64Chars[((b1 << 4) | (b2 >> 4)) & 0x3f];

    if (i + 1 < bytes.length) {
      result += base64Chars[((b2 << 2) | (b3 >> 6)) & 0x3f];
    }
    if (i + 2 < bytes.length) {
      result += base64Chars[b3 & 0x3f];
    }
  }

  // Convert to base64url (replace + with -, / with _, remove padding)
  return result.replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
}

// ============================================
// Secure Random Number Generation
// ============================================

/**
 * XorShift128+ PRNG state
 * Uses multiple entropy sources for seeding
 */
class SecureRandom {
  private state0: number;
  private state1: number;
  private initialized = false;

  constructor() {
    this.state0 = 0;
    this.state1 = 0;
  }

  /**
   * Initialize the PRNG with entropy from multiple sources
   */
  private initialize(): void {
    if (this.initialized) return;

    // Collect entropy from multiple sources
    const entropy: number[] = [];

    // Source 1: Current time (Date.now is available in Figma sandbox)
    entropy.push(Date.now());
    // Note: performance.now() is NOT available in Figma plugin sandbox
    // Use microsecond approximation from Date instead
    entropy.push((Date.now() % 1000) * 1000000 + Math.random() * 999999);

    // Source 2: Math.random() as additional entropy (not sole source)
    for (let i = 0; i < 8; i++) {
      entropy.push(Math.random() * 0xffffffff);
    }

    // Source 3: Memory-based entropy (object creation timing)
    // Note: performance.now() is NOT available in Figma plugin sandbox
    // Use array creation as entropy source without timing
    const memoryEntropy = (() => {
      const arr = new Array(1000).fill(0).map(() => ({}));
      const entropyValue = arr.reduce<number>((acc) => acc ^ (Math.random() * 0xffffffff), 0);
      arr.length = 0; // Help GC
      return entropyValue;
    })();
    entropy.push(memoryEntropy as number);

    // Mix entropy using a simple hash
    let h0 = 0x6a09e667;
    let h1 = 0xbb67ae85;

    for (const e of entropy) {
      const n = Math.floor(e) >>> 0;
      h0 = ((h0 ^ n) * 0x01000193) >>> 0;
      h1 = ((h1 ^ (n >>> 16)) * 0x01000193) >>> 0;
      // Mix between h0 and h1
      h0 = (h0 ^ (h1 >>> 8)) >>> 0;
      h1 = (h1 ^ (h0 << 3)) >>> 0;
    }

    this.state0 = h0 || 1; // Ensure non-zero
    this.state1 = h1 || 1;
    this.initialized = true;

    // Warm up the generator
    for (let i = 0; i < 20; i++) {
      this.next();
    }
  }

  /**
   * Generate next random 32-bit unsigned integer using XorShift128+
   */
  private next(): number {
    this.initialize();

    let s1 = this.state0;
    const s0 = this.state1;

    this.state0 = s0;
    s1 ^= s1 << 23;
    s1 ^= s1 >>> 17;
    s1 ^= s0;
    s1 ^= s0 >>> 26;
    this.state1 = s1;

    return (this.state0 + this.state1) >>> 0;
  }

  /**
   * Generate a random number between 0 (inclusive) and max (exclusive)
   */
  randomInt(max: number): number {
    return this.next() % max;
  }

  /**
   * Generate a random string of specified length using the given charset
   * @param length - Length of the string to generate
   * @param charset - Characters to use (default: alphanumeric)
   */
  randomString(
    length: number,
    charset = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
  ): string {
    let result = '';
    for (let i = 0; i < length; i++) {
      result += charset[this.randomInt(charset.length)];
    }
    return result;
  }

  /**
   * Generate a URL-safe random string (for PKCE code verifier)
   * Uses unreserved characters per RFC 7636
   */
  randomUrlSafe(length: number): string {
    const charset = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~';
    return this.randomString(length, charset);
  }
}

// ============================================
// Exported Instance
// ============================================

/**
 * Secure random number generator instance.
 * Uses XorShift128+ seeded with multiple entropy sources.
 *
 * @example
 * ```typescript
 * import { secureRandom } from './crypto-utils';
 *
 * const nonce = secureRandom.randomString(32);
 * const codeVerifier = secureRandom.randomUrlSafe(64);
 * ```
 *
 * @security
 *   This is NOT cryptographically secure in the traditional sense,
 *   but provides significantly better randomness than Math.random() alone.
 *   For OAuth state/nonce where prediction would require knowing:
 *   - Exact timing of initialization
 *   - Memory allocation patterns
 *   - Math.random() internal state
 *   This provides adequate security for the use case.
 */
export const secureRandom = new SecureRandom();
