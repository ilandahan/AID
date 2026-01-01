/**
 * Testing Utilities
 *
 * Custom render functions and test helpers for the AID project.
 * Provides consistent test setup with providers and common utilities.
 */

import { ReactElement, ReactNode } from 'react';
import { render, RenderOptions, RenderResult } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

/**
 * Provider wrapper for tests
 * Add any context providers needed for testing here
 */
interface AllProvidersProps {
  children: ReactNode;
}

function AllProviders({ children }: AllProvidersProps): ReactElement {
  return (
    <>
      {/* Add ThemeProvider, AuthProvider, etc. as needed */}
      {children}
    </>
  );
}

/**
 * Custom render function that wraps components with necessary providers
 *
 * @example
 * ```tsx
 * import { renderWithProviders } from '@/test-utils';
 *
 * test('renders component', () => {
 *   const { getByText } = renderWithProviders(<MyComponent />);
 *   expect(getByText('Hello')).toBeInTheDocument();
 * });
 * ```
 */
function customRender(
  ui: ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
): RenderResult {
  return render(ui, { wrapper: AllProviders, ...options });
}

/**
 * Setup userEvent with render
 * Returns both render result and user instance
 *
 * @example
 * ```tsx
 * import { renderWithUser } from '@/test-utils';
 *
 * test('handles user interaction', async () => {
 *   const { user, getByRole } = renderWithUser(<Button label="Click" />);
 *   await user.click(getByRole('button'));
 * });
 * ```
 */
function renderWithUser(
  ui: ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
) {
  return {
    user: userEvent.setup(),
    ...customRender(ui, options),
  };
}

/**
 * Create a mock function with typed return value
 *
 * @example
 * ```tsx
 * const mockFn = createMockFn<string>('default');
 * ```
 */
function createMockFn<T>(returnValue?: T) {
  return jest.fn().mockReturnValue(returnValue);
}

/**
 * Create an async mock function
 *
 * @example
 * ```tsx
 * const mockAsync = createAsyncMock({ data: 'result' });
 * await mockAsync(); // Returns { data: 'result' }
 * ```
 */
function createAsyncMock<T>(resolveValue?: T) {
  return jest.fn().mockResolvedValue(resolveValue);
}

/**
 * Create a rejecting async mock
 *
 * @example
 * ```tsx
 * const mockReject = createRejectingMock(new Error('Failed'));
 * await mockReject(); // Throws Error('Failed')
 * ```
 */
function createRejectingMock(error: Error) {
  return jest.fn().mockRejectedValue(error);
}

/**
 * Wait for a condition to be true
 *
 * @example
 * ```tsx
 * await waitForCondition(() => element.textContent === 'Loaded');
 * ```
 */
async function waitForCondition(
  condition: () => boolean,
  timeout = 1000,
  interval = 50
): Promise<void> {
  const startTime = Date.now();

  return new Promise((resolve, reject) => {
    const check = () => {
      if (condition()) {
        resolve();
      } else if (Date.now() - startTime >= timeout) {
        reject(new Error('Condition not met within timeout'));
      } else {
        setTimeout(check, interval);
      }
    };
    check();
  });
}

/**
 * Generate test IDs consistently
 *
 * @example
 * ```tsx
 * const id = testId('button', 'submit');
 * // Returns: 'button-submit'
 * ```
 */
function testId(...parts: string[]): string {
  return parts.join('-');
}

/**
 * Mock console methods for testing
 * Returns restore function to reset console
 *
 * @example
 * ```tsx
 * const restore = mockConsole('error');
 * // ... test code that logs errors ...
 * expect(console.error).toHaveBeenCalled();
 * restore();
 * ```
 */
function mockConsole(method: 'log' | 'warn' | 'error' | 'info') {
  const original = console[method];
  console[method] = jest.fn();

  return () => {
    console[method] = original;
  };
}

/**
 * Create a mock event
 *
 * @example
 * ```tsx
 * const event = createMockEvent({ target: { value: 'test' } });
 * fireEvent.change(input, event);
 * ```
 */
function createMockEvent<T extends object>(overrides: T = {} as T) {
  return {
    preventDefault: jest.fn(),
    stopPropagation: jest.fn(),
    ...overrides,
  };
}

/**
 * Generate random test data
 */
const testData = {
  /**
   * Generate a random string
   */
  string: (length = 10): string => {
    const chars = 'abcdefghijklmnopqrstuvwxyz';
    return Array.from({ length }, () =>
      chars.charAt(Math.floor(Math.random() * chars.length))
    ).join('');
  },

  /**
   * Generate a random email
   */
  email: (): string => {
    return `${testData.string(8)}@test.com`;
  },

  /**
   * Generate a random number
   */
  number: (min = 0, max = 100): number => {
    return Math.floor(Math.random() * (max - min + 1)) + min;
  },

  /**
   * Generate a UUID-like string
   */
  uuid: (): string => {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
      const r = (Math.random() * 16) | 0;
      const v = c === 'x' ? r : (r & 0x3) | 0x8;
      return v.toString(16);
    });
  },
};

// Re-export everything from testing-library
export * from '@testing-library/react';
export { userEvent };

// Export custom utilities
export {
  customRender as render,
  renderWithUser,
  createMockFn,
  createAsyncMock,
  createRejectingMock,
  waitForCondition,
  testId,
  mockConsole,
  createMockEvent,
  testData,
};
