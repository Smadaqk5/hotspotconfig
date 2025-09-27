import { test, expect } from '@playwright/test';

test('Simple login test', async ({ page }) => {
  // Go to login page
  await page.goto('/login/');
  
  // Check if login page loads
  await expect(page.locator('h2')).toContainText('Sign in to your account');
  
  // Fill login form
  await page.fill('input[name="username"]', 'customer1');
  await page.fill('input[name="password"]', 'customer123456');
  
  // Submit form
  await page.click('button[type="submit"]');
  
  // Check if redirected to dashboard
  await expect(page).toHaveURL(/.*dashboard/);
  
  // Check if dashboard loads
  await expect(page.locator('h1')).toContainText('Dashboard');
});
