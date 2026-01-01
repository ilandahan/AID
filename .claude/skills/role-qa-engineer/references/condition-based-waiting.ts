/**
 * Condition-Based Waiting Utilities
 * 
 * Reference implementation for async test patterns.
 * Use these instead of arbitrary setTimeout/sleep calls.
 * 
 * @see role-developer.md - Async Testing Pattern section
 */

// =============================================================================
// CORE UTILITY
// =============================================================================

/**
 * Wait for a condition to become truthy
 * 
 * @param condition - Function that returns truthy value when done
 * @param description - Human-readable description for error messages
 * @param timeoutMs - Maximum time to wait (default 5000ms)
 * @returns Promise resolving to the truthy value
 * 
 * @example
 * // Wait for result to be defined
 * await waitFor(() => getResult() !== undefined, 'result to be defined');
 * 
 * @example
 * // Wait for specific state
 * await waitFor(() => machine.state === 'ready', 'machine ready state');
 */
export async function waitFor<T>(
    condition: () => T | undefined | null | false,
    description: string,
    timeoutMs = 5000
): Promise<T> {
    const startTime = Date.now();

    while (true) {
        const result = condition();
        if (result) return result;

        if (Date.now() - startTime > timeoutMs) {
            throw new Error(`Timeout waiting for ${description} after ${timeoutMs}ms`);
        }

        await new Promise(r => setTimeout(r, 10)); // Poll every 10ms
    }
}

// =============================================================================
// EVENT-BASED UTILITIES
// =============================================================================

interface Event {
    type: string;
    data?: unknown;
}

interface EventSource {
    getEvents(id: string): Event[];
}

/**
 * Wait for a specific event type to appear
 * 
 * @example
 * await waitForEvent(eventSource, threadId, 'TOOL_RESULT');
 */
export function waitForEvent(
    source: EventSource,
    id: string,
    eventType: string,
    timeoutMs = 5000
): Promise<Event> {
    return new Promise((resolve, reject) => {
        const startTime = Date.now();

        const check = () => {
            const events = source.getEvents(id);
            const event = events.find((e) => e.type === eventType);

            if (event) {
                resolve(event);
            } else if (Date.now() - startTime > timeoutMs) {
                reject(new Error(`Timeout waiting for ${eventType} event after ${timeoutMs}ms`));
            } else {
                setTimeout(check, 10);
            }
        };

        check();
    });
}

/**
 * Wait for a specific number of events of a given type
 * 
 * @example
 * // Wait for 2 AGENT_MESSAGE events
 * await waitForEventCount(source, threadId, 'AGENT_MESSAGE', 2);
 */
export function waitForEventCount(
    source: EventSource,
    id: string,
    eventType: string,
    count: number,
    timeoutMs = 5000
): Promise<Event[]> {
    return new Promise((resolve, reject) => {
        const startTime = Date.now();

        const check = () => {
            const events = source.getEvents(id);
            const matchingEvents = events.filter((e) => e.type === eventType);

            if (matchingEvents.length >= count) {
                resolve(matchingEvents);
            } else if (Date.now() - startTime > timeoutMs) {
                reject(
                    new Error(
                        `Timeout waiting for ${count} ${eventType} events after ${timeoutMs}ms (got ${matchingEvents.length})`
                    )
                );
            } else {
                setTimeout(check, 10);
            }
        };

        check();
    });
}

/**
 * Wait for an event matching a custom predicate
 * 
 * @example
 * // Wait for TOOL_RESULT with specific ID
 * await waitForEventMatch(
 *   source,
 *   threadId,
 *   (e) => e.type === 'TOOL_RESULT' && e.data.id === 'call_123',
 *   'TOOL_RESULT with id=call_123'
 * );
 */
export function waitForEventMatch(
    source: EventSource,
    id: string,
    predicate: (event: Event) => boolean,
    description: string,
    timeoutMs = 5000
): Promise<Event> {
    return new Promise((resolve, reject) => {
        const startTime = Date.now();

        const check = () => {
            const events = source.getEvents(id);
            const event = events.find(predicate);

            if (event) {
                resolve(event);
            } else if (Date.now() - startTime > timeoutMs) {
                reject(new Error(`Timeout waiting for ${description} after ${timeoutMs}ms`));
            } else {
                setTimeout(check, 10);
            }
        };

        check();
    });
}

// =============================================================================
// STATE-BASED UTILITIES
// =============================================================================

/**
 * Wait for object property to have specific value
 * 
 * @example
 * await waitForState(user, 'status', 'active');
 */
export async function waitForState<T extends object, K extends keyof T>(
    obj: T,
    property: K,
    expectedValue: T[K],
    timeoutMs = 5000
): Promise<void> {
    await waitFor(
        () => obj[property] === expectedValue,
        `${String(property)} to equal ${expectedValue}`,
        timeoutMs
    );
}

/**
 * Wait for array to have minimum length
 * 
 * @example
 * await waitForLength(results, 5);
 */
export async function waitForLength<T>(
    arr: T[],
    minLength: number,
    timeoutMs = 5000
): Promise<T[]> {
    await waitFor(
        () => arr.length >= minLength,
        `array length >= ${minLength}`,
        timeoutMs
    );
    return arr;
}

// =============================================================================
// FILE SYSTEM UTILITIES
// =============================================================================

import { existsSync } from 'fs';

/**
 * Wait for file to exist
 * 
 * @example
 * await waitForFile('/tmp/output.json');
 */
export async function waitForFile(
    path: string,
    timeoutMs = 5000
): Promise<void> {
    await waitFor(
        () => existsSync(path),
        `file ${path} to exist`,
        timeoutMs
    );
}

/**
 * Wait for file to be deleted
 * 
 * @example
 * await waitForFileDeleted('/tmp/lock.pid');
 */
export async function waitForFileDeleted(
    path: string,
    timeoutMs = 5000
): Promise<void> {
    await waitFor(
        () => !existsSync(path),
        `file ${path} to be deleted`,
        timeoutMs
    );
}

// =============================================================================
// USAGE EXAMPLES
// =============================================================================

/*
// ❌ BEFORE (flaky):
const messagePromise = agent.sendMessage('Execute tools');
await new Promise(r => setTimeout(r, 300)); // Hope tools start in 300ms
agent.abort();
await messagePromise;
await new Promise(r => setTimeout(r, 50));  // Hope results arrive in 50ms
expect(toolResults.length).toBe(2);         // Fails randomly

// ✅ AFTER (reliable):
const messagePromise = agent.sendMessage('Execute tools');
await waitForEventCount(source, threadId, 'TOOL_CALL', 2);
agent.abort();
await messagePromise;
await waitForEventCount(source, threadId, 'TOOL_RESULT', 2);
expect(toolResults.length).toBe(2); // Always succeeds

// Result: 60% pass rate → 100%, 40% faster execution
*/

// =============================================================================
// WHEN ARBITRARY TIMEOUT IS CORRECT
// =============================================================================

/*
// Tool ticks every 100ms - need 2 ticks to verify partial output
await waitForEvent(source, id, 'TOOL_STARTED'); // First: wait for condition
await new Promise(r => setTimeout(r, 200));      // Then: wait for timed behavior
// 200ms = 2 ticks at 100ms intervals - documented and justified

Requirements for using arbitrary timeout:
1. First wait for triggering condition (don't guess when it starts)
2. Timeout based on KNOWN timing (not guessing)
3. Comment explaining WHY this specific duration
*/