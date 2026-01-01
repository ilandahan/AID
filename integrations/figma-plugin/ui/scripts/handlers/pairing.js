/**
 * Pairing Handlers Module
 * Handles OTP input and pairing with AID server
 *
 * The actual API call is delegated to the plugin code (code.ts → pairWithAID)
 * to ensure proper authentication flow with authService.
 */

/**
 * Get the current OTP code from all inputs
 * @returns {string} The concatenated OTP code
 */
export function getOtpCode() {
  const inputs = document.querySelectorAll('.otp-input');
  return Array.from(inputs).map(input => input.value).join('');
}

/**
 * Check if the OTP code is complete (6 digits)
 * @returns {boolean} True if code is complete
 */
export function isCodeComplete() {
  return getOtpCode().length === 6;
}

/**
 * Update the status display
 * @param {string} status - 'unpaired' | 'paired' | 'error'
 * @param {string} message - Status message to display
 */
export function updateStatus(status, message) {
  const aidStatus = document.getElementById('aidStatus');
  if (!aidStatus) return;

  aidStatus.classList.remove('unpaired', 'paired', 'error');
  aidStatus.classList.add(status);
  aidStatus.textContent = message;
}

/**
 * Hide the pairing overlay (on successful pairing)
 */
export function hideOverlay() {
  const overlay = document.getElementById('aidLockOverlay');
  if (overlay) {
    overlay.classList.add('hidden');
  }
}

/**
 * Attempt to pair with the server
 * Sends AID_PAIR message to plugin which handles the full auth flow
 */
function attemptPairing() {
  const code = getOtpCode();

  if (!isCodeComplete()) {
    updateStatus('error', 'Please enter the complete 6-digit code');
    return;
  }

  updateStatus('unpaired', 'Connecting...');

  // Send code to plugin - it handles:
  // 1. API call to /auth/pair
  // 2. authService.authenticateWithJWT()
  // 3. connectMCP()
  // 4. startHeartbeat()
  // Then sends AID_PAIRED or AID_PAIR_FAILED back
  parent.postMessage({
    pluginMessage: { type: 'AID_PAIR', code }
  }, '*');
}

/**
 * Clear all OTP inputs and focus the first one
 */
export function clearOtpInputs() {
  const inputs = document.querySelectorAll('.otp-input');
  inputs.forEach(input => {
    input.value = '';
  });
  // Focus first input
  if (inputs[0]) {
    inputs[0].focus();
  }
}

/**
 * Handle input event on OTP inputs
 * @param {Event} e - Input event
 */
function handleOtpInput(e) {
  const input = e.target;
  const value = input.value;

  // Only allow digits
  if (value && !/^\d$/.test(value)) {
    input.value = '';
    return;
  }

  // Auto-advance to next input
  if (value && input.dataset.otp !== undefined) {
    const currentIndex = parseInt(input.dataset.otp, 10);
    const nextIndex = currentIndex + 1;
    const nextInput = document.querySelector(`[data-otp="${nextIndex}"]`);

    if (nextInput) {
      nextInput.focus();
    }
  }
}

/**
 * Handle keydown event on OTP inputs
 * @param {KeyboardEvent} e - Keydown event
 */
function handleOtpKeydown(e) {
  const input = e.target;
  const currentIndex = parseInt(input.dataset.otp, 10);

  // Handle backspace
  if (e.key === 'Backspace' && !input.value && currentIndex > 0) {
    const prevInput = document.querySelector(`[data-otp="${currentIndex - 1}"]`);
    if (prevInput) {
      prevInput.focus();
    }
  }

  // Handle Enter key
  if (e.key === 'Enter') {
    e.preventDefault();
    attemptPairing();
  }
}

/**
 * Handle paste event on OTP inputs
 * @param {ClipboardEvent} e - Paste event
 */
function handleOtpPaste(e) {
  e.preventDefault();
  const pastedData = e.clipboardData.getData('text').replace(/\D/g, '').slice(0, 6);
  const inputs = document.querySelectorAll('.otp-input');

  pastedData.split('').forEach((digit, i) => {
    if (inputs[i]) {
      inputs[i].value = digit;
    }
  });

  // Focus last filled input or first empty
  const lastFilledIndex = Math.min(pastedData.length - 1, 5);
  if (inputs[lastFilledIndex]) {
    inputs[lastFilledIndex].focus();
  }
}

/**
 * Initialize all pairing handlers
 */
export function initPairingHandlers() {
  // OTP input handlers
  const otpInputs = document.querySelectorAll('.otp-input');
  otpInputs.forEach(input => {
    input.addEventListener('input', handleOtpInput);
    input.addEventListener('keydown', handleOtpKeydown);
    input.addEventListener('paste', handleOtpPaste);

    // Select all text on focus for easy replacement
    input.addEventListener('focus', () => {
      input.select();
    });
  });

  // Pair button handler
  const pairBtn = document.getElementById('pairBtn');
  if (pairBtn) {
    pairBtn.addEventListener('click', attemptPairing);
  }

  console.log('[Pairing] Handlers initialized');
}
