/**
 * @file Logger.ts
 * @description Configurable logging utility for the Figma plugin.
 *              Supports log levels and can be disabled in production.
 * @created 2024-12
 * @related
 *   - ./code.ts - Main plugin entry point
 *   - All service files - Use logger for consistent logging
 */

// ============================================
// Types
// ============================================

export type LogLevel = 'debug' | 'info' | 'warn' | 'error' | 'none';

export interface LoggerConfig {
  level: LogLevel;
  prefix: string;
  enableTimestamp: boolean;
}

// ============================================
// Log Level Priority
// ============================================

const LOG_LEVELS: Record<LogLevel, number> = {
  debug: 0,
  info: 1,
  warn: 2,
  error: 3,
  none: 4,
};

// ============================================
// Logger Class
// ============================================

/**
 * Configurable logger that supports log levels and prefixes.
 * Use this instead of console.log for consistent, controllable logging.
 *
 * @example
 * ```typescript
 * import { logger } from './Logger';
 *
 * logger.debug('Detailed info for debugging');
 * logger.info('General information');
 * logger.warn('Warning message');
 * logger.error('Error occurred', error);
 *
 * // Disable logging in production
 * logger.setLevel('none');
 * ```
 */
export class Logger {
  private config: LoggerConfig;

  constructor(config?: Partial<LoggerConfig>) {
    this.config = {
      level: 'info',
      prefix: '[PLUGIN]',
      enableTimestamp: false,
      ...config,
    };
  }

  /**
   * Set the minimum log level
   * @param level - Minimum level to log ('debug' | 'info' | 'warn' | 'error' | 'none')
   */
  setLevel(level: LogLevel): void {
    this.config.level = level;
  }

  /**
   * Get the current log level
   */
  getLevel(): LogLevel {
    return this.config.level;
  }

  /**
   * Set the log prefix
   * @param prefix - Prefix to prepend to all log messages
   */
  setPrefix(prefix: string): void {
    this.config.prefix = prefix;
  }

  /**
   * Check if a log level should be logged
   */
  private shouldLog(level: LogLevel): boolean {
    return LOG_LEVELS[level] >= LOG_LEVELS[this.config.level];
  }

  /**
   * Format the log message with prefix and optional timestamp
   */
  private formatMessage(level: string, message: string): string {
    const parts: string[] = [];

    if (this.config.enableTimestamp) {
      parts.push(`[${new Date().toISOString()}]`);
    }

    parts.push(this.config.prefix);
    parts.push(`[${level.toUpperCase()}]`);
    parts.push(message);

    return parts.join(' ');
  }

  /**
   * Log debug messages (most verbose)
   * @param message - The message to log
   * @param args - Additional arguments to log
   */
  debug(message: string, ...args: unknown[]): void {
    if (this.shouldLog('debug')) {
      console.log(this.formatMessage('debug', message), ...args);
    }
  }

  /**
   * Log info messages (general information)
   * @param message - The message to log
   * @param args - Additional arguments to log
   */
  info(message: string, ...args: unknown[]): void {
    if (this.shouldLog('info')) {
      console.log(this.formatMessage('info', message), ...args);
    }
  }

  /**
   * Log warning messages
   * @param message - The message to log
   * @param args - Additional arguments to log
   */
  warn(message: string, ...args: unknown[]): void {
    if (this.shouldLog('warn')) {
      console.warn(this.formatMessage('warn', message), ...args);
    }
  }

  /**
   * Log error messages
   * @param message - The message to log
   * @param args - Additional arguments to log
   */
  error(message: string, ...args: unknown[]): void {
    if (this.shouldLog('error')) {
      console.error(this.formatMessage('error', message), ...args);
    }
  }

  /**
   * Create a child logger with a specific prefix
   * @param prefix - The prefix for the child logger
   * @returns A new Logger instance with the specified prefix
   */
  child(prefix: string): Logger {
    return new Logger({
      ...this.config,
      prefix: `${this.config.prefix}${prefix}`,
    });
  }
}

// ============================================
// Default Logger Instance
// ============================================

/**
 * Default logger instance for the plugin.
 * Import and use this throughout the codebase.
 *
 * @example
 * ```typescript
 * import { logger } from './Logger';
 * logger.info('Plugin initialized');
 * ```
 */
export const logger = new Logger({
  level: 'debug', // Set to 'warn' or 'error' in production
  prefix: '[PLUGIN]',
  enableTimestamp: false,
});

// ============================================
// Specialized Loggers
// ============================================

/**
 * Logger for MCP-related messages
 */
export const mcpLogger = logger.child('[MCP]');

/**
 * Logger for authentication-related messages
 */
export const authLogger = logger.child('[AUTH]');

/**
 * Logger for Figma data extraction
 */
export const figmaLogger = logger.child('[FIGMA]');
