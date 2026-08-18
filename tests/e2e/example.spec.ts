import { test, expect } from '@playwright/test';

test.describe('Application Health', () => {
  test('homepage loads successfully', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveTitle(/.+/);
  });
});
