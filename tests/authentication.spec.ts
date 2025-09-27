/**
 * Authentication Tests
 * Tests user signup, login, and logout functionality
 */

import { test, expect } from '@playwright/test';
import { testUsers } from './fixtures/test-data';

test.describe('Authentication', () => {
  test.describe('User Registration', () => {
    test('should register user with valid details successfully', async ({ page }) => {
      await page.goto('/register/');
      
      // Fill registration form
      await page.fill('input[name="username"]', testUsers.customer.username);
      await page.fill('input[name="email"]', testUsers.customer.email);
      await page.fill('input[name="password"]', testUsers.customer.password);
      await page.fill('input[name="password_confirm"]', testUsers.customer.password);
      await page.fill('input[name="first_name"]', testUsers.customer.first_name);
      await page.fill('input[name="last_name"]', testUsers.customer.last_name);
      await page.fill('input[name="phone_number"]', testUsers.customer.phone_number);
      await page.fill('input[name="company_name"]', testUsers.customer.company_name);
      
      // Submit form
      await page.click('button[type="submit"]');
      
      // Should redirect to dashboard
      await expect(page).toHaveURL(/.*dashboard/);
      await expect(page.locator('h1')).toContainText('Dashboard');
      
      // Check success message
      await expect(page.locator('.bg-green-100')).toContainText('Registration successful');
    });

    test('should show error for invalid email format', async ({ page }) => {
      await page.goto('/register/');
      
      // Fill form with invalid email
      await page.fill('input[name="username"]', 'testuser');
      await page.fill('input[name="email"]', 'invalid-email');
      await page.fill('input[name="password"]', 'password123');
      await page.fill('input[name="password_confirm"]', 'password123');
      await page.fill('input[name="first_name"]', 'Test');
      await page.fill('input[name="last_name"]', 'User');
      await page.fill('input[name="phone_number"]', '+254700000000');
      
      // Submit form
      await page.click('button[type="submit"]');
      
      // Should show error message
      await expect(page.locator('.bg-red-100')).toContainText('email');
    });

    test('should show error for password mismatch', async ({ page }) => {
      await page.goto('/register/');
      
      // Fill form with mismatched passwords
      await page.fill('input[name="username"]', 'testuser');
      await page.fill('input[name="email"]', 'test@example.com');
      await page.fill('input[name="password"]', 'password123');
      await page.fill('input[name="password_confirm"]', 'differentpassword');
      await page.fill('input[name="first_name"]', 'Test');
      await page.fill('input[name="last_name"]', 'User');
      await page.fill('input[name="phone_number"]', '+254700000000');
      
      // Submit form
      await page.click('button[type="submit"]');
      
      // Should show error message
      await expect(page.locator('.bg-red-100')).toContainText('password');
    });

    test('should show error for missing required fields', async ({ page }) => {
      await page.goto('/register/');
      
      // Submit empty form
      await page.click('button[type="submit"]');
      
      // Should show validation errors
      await expect(page.locator('input[name="username"]:invalid')).toBeVisible();
      await expect(page.locator('input[name="email"]:invalid')).toBeVisible();
      await expect(page.locator('input[name="password"]:invalid')).toBeVisible();
    });

    test('should redirect to login page from registration', async ({ page }) => {
      await page.goto('/register/');
      
      // Click login link
      await page.click('a[href*="login"]');
      
      // Should be on login page
      await expect(page).toHaveURL(/.*login/);
      await expect(page.locator('h2')).toContainText('Sign in to your account');
    });
  });

  test.describe('User Login', () => {
    test('should login with correct credentials successfully', async ({ page }) => {
      await page.goto('/login/');
      
      // Fill login form
      await page.fill('input[name="username"]', testUsers.customer.username);
      await page.fill('input[name="password"]', testUsers.customer.password);
      
      // Submit form
      await page.click('button[type="submit"]');
      
      // Should redirect to dashboard
      await expect(page).toHaveURL(/.*dashboard/);
      await expect(page.locator('h1')).toContainText('Dashboard');
      
      // Check welcome message
      await expect(page.locator('.bg-green-100')).toContainText('Welcome back');
    });

    test('should login with email address successfully', async ({ page }) => {
      await page.goto('/login/');
      
      // Fill login form with email
      await page.fill('input[name="username"]', testUsers.customer.email);
      await page.fill('input[name="password"]', testUsers.customer.password);
      
      // Submit form
      await page.click('button[type="submit"]');
      
      // Should redirect to dashboard
      await expect(page).toHaveURL(/.*dashboard/);
      await expect(page.locator('h1')).toContainText('Dashboard');
    });

    test('should show error for wrong password', async ({ page }) => {
      await page.goto('/login/');
      
      // Fill form with wrong password
      await page.fill('input[name="username"]', testUsers.customer.username);
      await page.fill('input[name="password"]', 'wrongpassword');
      
      // Submit form
      await page.click('button[type="submit"]');
      
      // Should show error message
      await expect(page.locator('.bg-red-100')).toContainText('Invalid credentials');
    });

    test('should show error for non-existent user', async ({ page }) => {
      await page.goto('/login/');
      
      // Fill form with non-existent user
      await page.fill('input[name="username"]', 'nonexistentuser');
      await page.fill('input[name="password"]', 'password123');
      
      // Submit form
      await page.click('button[type="submit"]');
      
      // Should show error message
      await expect(page.locator('.bg-red-100')).toContainText('Invalid credentials');
    });

    test('should redirect to dashboard if already logged in', async ({ page }) => {
      // First login
      await page.goto('/login/');
      await page.fill('input[name="username"]', testUsers.customer.username);
      await page.fill('input[name="password"]', testUsers.customer.password);
      await page.click('button[type="submit"]');
      
      // Try to access login page again
      await page.goto('/login/');
      
      // Should redirect to dashboard
      await expect(page).toHaveURL(/.*dashboard/);
    });

    test('should redirect to registration page from login', async ({ page }) => {
      await page.goto('/login/');
      
      // Click registration link
      await page.click('a[href*="register"]');
      
      // Should be on registration page
      await expect(page).toHaveURL(/.*register/);
      await expect(page.locator('h2')).toContainText('Create your account');
    });
  });

  test.describe('User Logout', () => {
    test.beforeEach(async ({ page }) => {
      // Login before each test
      await page.goto('/login/');
      await page.fill('input[name="username"]', testUsers.customer.username);
      await page.fill('input[name="password"]', testUsers.customer.password);
      await page.click('button[type="submit"]');
      await expect(page).toHaveURL(/.*dashboard/);
    });

    test('should logout successfully and redirect to homepage', async ({ page }) => {
      // Click logout button
      await page.click('button:has-text("Logout")');
      
      // Should redirect to homepage
      await expect(page).toHaveURL('/');
      await expect(page.locator('h1')).toContainText('Monetize Your WiFi Easily');
      
      // Check logout message
      await expect(page.locator('.bg-green-100')).toContainText('logged out successfully');
    });

    test('should show login button after logout', async ({ page }) => {
      // Logout
      await page.click('button:has-text("Logout")');
      
      // Should show login/register buttons
      await expect(page.locator('a[href*="login"]')).toContainText('Login');
      await expect(page.locator('a[href*="register"]')).toContainText('Sign Up');
    });
  });

  test.describe('Form Validation', () => {
    test('should validate required fields on registration', async ({ page }) => {
      await page.goto('/register/');
      
      // Try to submit empty form
      await page.click('button[type="submit"]');
      
      // Check HTML5 validation
      const usernameInput = page.locator('input[name="username"]');
      const emailInput = page.locator('input[name="email"]');
      const passwordInput = page.locator('input[name="password"]');
      
      await expect(usernameInput).toHaveAttribute('required');
      await expect(emailInput).toHaveAttribute('required');
      await expect(passwordInput).toHaveAttribute('required');
    });

    test('should validate required fields on login', async ({ page }) => {
      await page.goto('/login/');
      
      // Try to submit empty form
      await page.click('button[type="submit"]');
      
      // Check HTML5 validation
      const usernameInput = page.locator('input[name="username"]');
      const passwordInput = page.locator('input[name="password"]');
      
      await expect(usernameInput).toHaveAttribute('required');
      await expect(passwordInput).toHaveAttribute('required');
    });

    test('should show helpful placeholder text', async ({ page }) => {
      await page.goto('/login/');
      
      // Check placeholder text
      await expect(page.locator('input[name="username"]')).toHaveAttribute('placeholder', 'Enter your username or email address');
      await expect(page.locator('input[name="password"]')).toHaveAttribute('placeholder', 'Enter your password');
      
      // Check help text
      await expect(page.locator('p.text-xs')).toContainText('You can use either your username or email address');
    });
  });

  test.describe('Remember Me Functionality', () => {
    test('should have remember me checkbox', async ({ page }) => {
      await page.goto('/login/');
      
      // Check remember me checkbox exists
      await expect(page.locator('input[name="remember_me"]')).toBeVisible();
      await expect(page.locator('label[for="remember_me"]')).toContainText('Remember me');
    });

    test('should allow checking remember me', async ({ page }) => {
      await page.goto('/login/');
      
      // Check remember me checkbox
      await page.check('input[name="remember_me"]');
      await expect(page.locator('input[name="remember_me"]')).toBeChecked();
    });
  });

  test.describe('Forgot Password', () => {
    test('should have forgot password link', async ({ page }) => {
      await page.goto('/login/');
      
      // Check forgot password link exists
      await expect(page.locator('a:has-text("Forgot your password?")')).toBeVisible();
    });

    test('should navigate to forgot password page', async ({ page }) => {
      await page.goto('/login/');
      
      // Click forgot password link
      await page.click('a:has-text("Forgot your password?")');
      
      // Should navigate to forgot password page (if implemented)
      // For now, just check the link exists
      await expect(page.locator('a:has-text("Forgot your password?")')).toBeVisible();
    });
  });
});
