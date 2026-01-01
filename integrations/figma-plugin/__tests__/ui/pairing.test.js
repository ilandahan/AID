/**
 * @jest-environment jsdom
 */

/**
 * Pairing Module Tests
 * Tests for OTP input handling and pairing functionality
 */

// Mock parent.postMessage for Figma plugin environment
const mockPostMessage = jest.fn();
global.parent = { postMessage: mockPostMessage };

// Mock fetch for pairing API
global.fetch = jest.fn();

describe('Pairing Module', () => {
  let pairingModule;

  beforeEach(() => {
    jest.resetModules();
    mockPostMessage.mockClear();
    global.fetch.mockClear();

    // Set up DOM structure matching ui.html
    document.body.innerHTML = `
      <div class="locked-overlay" id="aidLockOverlay">
        <div class="aid-pairing">
          <div class="pairing-input-group">
            <input type="text" class="otp-input" maxlength="1" data-otp="0" inputmode="numeric">
            <input type="text" class="otp-input" maxlength="1" data-otp="1" inputmode="numeric">
            <input type="text" class="otp-input" maxlength="1" data-otp="2" inputmode="numeric">
            <input type="text" class="otp-input" maxlength="1" data-otp="3" inputmode="numeric">
            <input type="text" class="otp-input" maxlength="1" data-otp="4" inputmode="numeric">
            <input type="text" class="otp-input" maxlength="1" data-otp="5" inputmode="numeric">
          </div>
          <div class="aid-status unpaired" id="aidStatus">Not paired</div>
          <button class="btn btn-primary" id="pairBtn">Pair with AI.D</button>
        </div>
      </div>
    `;
  });

  describe('OTP Input Auto-Advance', () => {
    beforeEach(async () => {
      pairingModule = await import('../../ui/scripts/handlers/pairing.js');
      pairingModule.initPairingHandlers();
    });

    test('should auto-advance to next input when digit is entered', () => {
      const inputs = document.querySelectorAll('.otp-input');
      const firstInput = inputs[0];
      const secondInput = inputs[1];

      // Focus first input
      firstInput.focus();
      expect(document.activeElement).toBe(firstInput);

      // Simulate typing a digit
      firstInput.value = '7';
      firstInput.dispatchEvent(new Event('input', { bubbles: true }));

      // Should auto-focus next input
      expect(document.activeElement).toBe(secondInput);
    });

    test('should NOT advance when non-digit is entered', () => {
      const inputs = document.querySelectorAll('.otp-input');
      const firstInput = inputs[0];

      firstInput.focus();
      firstInput.value = 'a';
      firstInput.dispatchEvent(new Event('input', { bubbles: true }));

      // Should clear invalid input and stay focused
      expect(firstInput.value).toBe('');
      expect(document.activeElement).toBe(firstInput);
    });

    test('should stay on last input when complete', () => {
      const inputs = document.querySelectorAll('.otp-input');
      const lastInput = inputs[5];

      lastInput.focus();
      lastInput.value = '5';
      lastInput.dispatchEvent(new Event('input', { bubbles: true }));

      // Should stay on last input (no more to advance to)
      expect(document.activeElement).toBe(lastInput);
    });

    test('should handle backspace to go to previous input', () => {
      const inputs = document.querySelectorAll('.otp-input');
      const secondInput = inputs[1];
      const firstInput = inputs[0];

      // Set up: first input has value, second is focused and empty
      firstInput.value = '7';
      secondInput.focus();

      // Simulate backspace on empty input
      const backspaceEvent = new KeyboardEvent('keydown', {
        key: 'Backspace',
        bubbles: true
      });
      secondInput.dispatchEvent(backspaceEvent);

      // Should focus previous input
      expect(document.activeElement).toBe(firstInput);
    });
  });

  describe('Enter Key to Pair', () => {
    beforeEach(async () => {
      pairingModule = await import('../../ui/scripts/handlers/pairing.js');
      pairingModule.initPairingHandlers();
    });

    test('should trigger pairing when Enter is pressed on last input', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ success: true, token: 'test-token' })
      });

      const inputs = document.querySelectorAll('.otp-input');

      // Fill all inputs
      inputs[0].value = '7';
      inputs[1].value = '9';
      inputs[2].value = '2';
      inputs[3].value = '6';
      inputs[4].value = '6';
      inputs[5].value = '5';
      inputs[5].focus();

      // Simulate Enter key
      const enterEvent = new KeyboardEvent('keydown', {
        key: 'Enter',
        bubbles: true
      });
      inputs[5].dispatchEvent(enterEvent);

      // Should send postMessage to plugin (not direct fetch)
      expect(mockPostMessage).toHaveBeenCalledWith(
        { pluginMessage: { type: 'AID_PAIR', code: '792665' } },
        '*'
      );
    });

    test('should NOT trigger pairing when Enter is pressed with incomplete code', () => {
      const inputs = document.querySelectorAll('.otp-input');

      // Only fill some inputs
      inputs[0].value = '7';
      inputs[1].value = '9';
      inputs[5].focus();

      const enterEvent = new KeyboardEvent('keydown', {
        key: 'Enter',
        bubbles: true
      });
      inputs[5].dispatchEvent(enterEvent);

      // Should NOT attempt to pair
      expect(global.fetch).not.toHaveBeenCalled();
    });
  });

  describe('Pair Button Click', () => {
    beforeEach(async () => {
      pairingModule = await import('../../ui/scripts/handlers/pairing.js');
      pairingModule.initPairingHandlers();
    });

    test('should trigger pairing when Pair button is clicked with complete code', async () => {
      const inputs = document.querySelectorAll('.otp-input');
      const pairBtn = document.getElementById('pairBtn');

      // Fill all inputs
      inputs[0].value = '1';
      inputs[1].value = '2';
      inputs[2].value = '3';
      inputs[3].value = '4';
      inputs[4].value = '5';
      inputs[5].value = '6';

      // Click pair button
      pairBtn.click();

      // Should send postMessage to plugin (not direct fetch)
      expect(mockPostMessage).toHaveBeenCalledWith(
        { pluginMessage: { type: 'AID_PAIR', code: '123456' } },
        '*'
      );
    });

    test('should show error status when code is incomplete', () => {
      const inputs = document.querySelectorAll('.otp-input');
      const pairBtn = document.getElementById('pairBtn');
      const aidStatus = document.getElementById('aidStatus');

      // Only fill some inputs
      inputs[0].value = '1';
      inputs[1].value = '2';

      // Click pair button
      pairBtn.click();

      // Should NOT attempt to pair
      expect(global.fetch).not.toHaveBeenCalled();

      // Should show error
      expect(aidStatus.classList.contains('error')).toBe(true);
    });

    test('should update UI on successful pairing', async () => {
      const aidStatus = document.getElementById('aidStatus');
      const overlay = document.getElementById('aidLockOverlay');

      // Directly call the exported functions to simulate successful pairing
      // (In real app, these are called by message handler when plugin sends AID_PAIRED)
      pairingModule.updateStatus('paired', 'Connected to AI.D');
      pairingModule.hideOverlay();

      // Should hide overlay
      expect(overlay.classList.contains('hidden')).toBe(true);

      // Should update status
      expect(aidStatus.classList.contains('paired')).toBe(true);
    });

    test('should show error on failed pairing', async () => {
      const aidStatus = document.getElementById('aidStatus');

      // Directly call updateStatus to simulate failed pairing
      // (In real app, this is called by message handler when plugin sends AID_PAIR_FAILED)
      pairingModule.updateStatus('error', 'Invalid code');

      // Should show error status
      expect(aidStatus.classList.contains('error')).toBe(true);
    });
  });

  describe('getOtpCode helper', () => {
    beforeEach(async () => {
      pairingModule = await import('../../ui/scripts/handlers/pairing.js');
    });

    test('should return complete 6-digit code', () => {
      const inputs = document.querySelectorAll('.otp-input');
      '123456'.split('').forEach((digit, i) => {
        inputs[i].value = digit;
      });

      expect(pairingModule.getOtpCode()).toBe('123456');
    });

    test('should return partial code when incomplete', () => {
      const inputs = document.querySelectorAll('.otp-input');
      inputs[0].value = '1';
      inputs[1].value = '2';

      expect(pairingModule.getOtpCode()).toBe('12');
    });

    test('should return empty string when no digits entered', () => {
      expect(pairingModule.getOtpCode()).toBe('');
    });
  });

  describe('isCodeComplete helper', () => {
    beforeEach(async () => {
      pairingModule = await import('../../ui/scripts/handlers/pairing.js');
    });

    test('should return true for complete 6-digit code', () => {
      const inputs = document.querySelectorAll('.otp-input');
      '123456'.split('').forEach((digit, i) => {
        inputs[i].value = digit;
      });

      expect(pairingModule.isCodeComplete()).toBe(true);
    });

    test('should return false for incomplete code', () => {
      const inputs = document.querySelectorAll('.otp-input');
      inputs[0].value = '1';
      inputs[1].value = '2';

      expect(pairingModule.isCodeComplete()).toBe(false);
    });
  });
});
