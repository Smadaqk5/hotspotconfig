import { test, expect } from '@playwright/test';

test('Basic functionality test', async ({ page }) => {
  // Test homepage
  await page.goto('/');
  await expect(page.locator('h1')).toContainText('Monetize Your WiFi Easily');
  
  // Test login page
  await page.goto('/login/');
  await expect(page.locator('h2')).toContainText('Sign in to your account');
  
  // Test login functionality
  await page.fill('input[name="username"]', 'customer1');
  await page.fill('input[name="password"]', 'customer123456');
  await page.click('button[type="submit"]');
  
  // Should redirect to dashboard
  await expect(page).toHaveURL(/.*dashboard/);
  await expect(page.locator('h1')).toContainText('Dashboard');
});
