/**
 * Subscription & Payments Tests
 * Tests Pesapal integration and subscription management
 */

import { test, expect } from '@playwright/test';
import { testUsers, testSubscriptions, testPayments } from './fixtures/test-data';
import { mockPesapalAPI } from './fixtures/pesapal-mock';

test.describe('Subscription & Payments', () => {
  test.beforeEach(async ({ page }) => {
    // Login as customer
    await page.goto('/login/');
    await page.fill('input[name="username"]', testUsers.customer.username);
    await page.fill('input[name="password"]', testUsers.customer.password);
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL(/.*dashboard/);
  });

  test.describe('Subscription Plans', () => {
    test('should display subscription plans correctly', async ({ page }) => {
      await page.goto('/pricing/');
      
      // Check all subscription plans are visible
      await expect(page.locator('h3')).toContainText('Basic');
      await expect(page.locator('h3')).toContainText('Professional');
      await expect(page.locator('h3')).toContainText('Enterprise');
      
      // Check pricing
      await expect(page.locator('text=KES 2,500')).toBeVisible();
      await expect(page.locator('text=KES 5,000')).toBeVisible();
      await expect(page.locator('text=KES 10,000')).toBeVisible();
    });

    test('should show plan features correctly', async ({ page }) => {
      await page.goto('/pricing/');
      
      // Check Basic plan features
      await expect(page.locator('text=Unlimited ticket generation')).toBeVisible();
      await expect(page.locator('text=Time & data-based tickets')).toBeVisible();
      await expect(page.locator('text=Basic sales tracking')).toBeVisible();
      
      // Check Professional plan features
      await expect(page.locator('text=Advanced analytics')).toBeVisible();
      await expect(page.locator('text=PDF ticket printing')).toBeVisible();
      await expect(page.locator('text=Priority support')).toBeVisible();
    });

    test('should highlight most popular plan', async ({ page }) => {
      await page.goto('/pricing/');
      
      // Check Professional plan is marked as most popular
      await expect(page.locator('text=Most Popular')).toBeVisible();
      
      // Check Professional plan has special styling
      const professionalPlan = page.locator('.border-2.border-primary');
      await expect(professionalPlan).toBeVisible();
    });
  });

  test.describe('Pesapal Payment Integration', () => {
    test('should redirect to Pesapal checkout when subscribing', async ({ page }) => {
      await page.goto('/pricing/');
      
      // Click subscribe button for Basic plan
      const subscribeButton = page.locator('button:has-text("Get Started")').first();
      await subscribeButton.click();
      
      // Should redirect to Pesapal checkout
      await expect(page).toHaveURL(/.*pesapal/);
      
      // Check Pesapal elements are present
      await expect(page.locator('text=M-PESA')).toBeVisible();
      await expect(page.locator('text=Airtel Money')).toBeVisible();
    });

    test('should handle successful Pesapal payment', async ({ page }) => {
      // Mock successful Pesapal response
      await mockPesapalAPI(page, 'success');
      
      await page.goto('/pricing/');
      await page.click('button:has-text("Get Started")').first();
      
      // Simulate successful payment
      await page.click('button:has-text("Pay with M-PESA")');
      
      // Should redirect back to dashboard with success
      await expect(page).toHaveURL(/.*dashboard/);
      await expect(page.locator('.bg-green-100')).toContainText('Payment successful');
      
      // Check subscription status is now active
      await expect(page.locator('text=Active')).toBeVisible();
    });

    test('should handle failed Pesapal payment', async ({ page }) => {
      // Mock failed Pesapal response
      await mockPesapalAPI(page, 'failed');
      
      await page.goto('/pricing/');
      await page.click('button:has-text("Get Started")').first();
      
      // Simulate failed payment
      await page.click('button:has-text("Pay with M-PESA")');
      
      // Should show error message
      await expect(page.locator('.bg-red-100')).toContainText('Payment failed');
      
      // Check subscription status remains inactive
      await expect(page.locator('text=Inactive')).toBeVisible();
    });

    test('should handle pending Pesapal payment', async ({ page }) => {
      // Mock pending Pesapal response
      await mockPesapalAPI(page, 'pending');
      
      await page.goto('/pricing/');
      await page.click('button:has-text("Get Started")').first();
      
      // Simulate pending payment
      await page.click('button:has-text("Pay with M-PESA")');
      
      // Should show pending message
      await expect(page.locator('.bg-yellow-100')).toContainText('Payment pending');
      
      // Check subscription status is pending
      await expect(page.locator('text=Pending')).toBeVisible();
    });

    test('should allow payment retry after failure', async ({ page }) => {
      // Mock failed then successful Pesapal response
      await mockPesapalAPI(page, 'failed');
      
      await page.goto('/pricing/');
      await page.click('button:has-text("Get Started")').first();
      await page.click('button:has-text("Pay with M-PESA")');
      
      // Should show retry option
      await expect(page.locator('button:has-text("Retry Payment")')).toBeVisible();
      
      // Mock successful response for retry
      await mockPesapalAPI(page, 'success');
      await page.click('button:has-text("Retry Payment")');
      
      // Should succeed on retry
      await expect(page.locator('.bg-green-100')).toContainText('Payment successful');
    });
  });

  test.describe('Subscription Management', () => {
    test('should display current subscription status', async ({ page }) => {
      await page.goto('/dashboard/');
      
      // Check subscription status card
      await expect(page.locator('text=Subscription Status')).toBeVisible();
      
      // Should show current status (Active/Inactive/Pending)
      const statusCard = page.locator('.bg-white.shadow.rounded-lg');
      await expect(statusCard).toBeVisible();
    });

    test('should show subscription details for active subscription', async ({ page }) => {
      // Mock active subscription
      await page.route('**/api/subscription/**', route => {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            status: 'active',
            plan: 'Professional',
            expires_at: '2024-02-15T00:00:00Z',
            features: ['Unlimited tickets', 'Advanced analytics']
          })
        });
      });
      
      await page.goto('/dashboard/');
      
      // Check subscription details
      await expect(page.locator('text=Professional')).toBeVisible();
      await expect(page.locator('text=Active')).toBeVisible();
      await expect(page.locator('text=Unlimited tickets')).toBeVisible();
    });

    test('should show upgrade options for basic plan', async ({ page }) => {
      // Mock basic plan subscription
      await page.route('**/api/subscription/**', route => {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            status: 'active',
            plan: 'Basic',
            expires_at: '2024-02-15T00:00:00Z'
          })
        });
      });
      
      await page.goto('/dashboard/');
      
      // Check upgrade options are shown
      await expect(page.locator('button:has-text("Upgrade Plan")')).toBeVisible();
    });

    test('should handle subscription expiry', async ({ page }) => {
      // Mock expired subscription
      await page.route('**/api/subscription/**', route => {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            status: 'expired',
            plan: 'Professional',
            expired_at: '2024-01-15T00:00:00Z'
          })
        });
      });
      
      await page.goto('/dashboard/');
      
      // Check expired status
      await expect(page.locator('text=Expired')).toBeVisible();
      await expect(page.locator('text=Renew Subscription')).toBeVisible();
    });
  });

  test.describe('Payment History', () => {
    test('should display payment history', async ({ page }) => {
      await page.goto('/dashboard/');
      
      // Navigate to payment history
      await page.click('a:has-text("Payment History")');
      
      // Check payment history table
      await expect(page.locator('table')).toBeVisible();
      await expect(page.locator('th')).toContainText('Date');
      await expect(page.locator('th')).toContainText('Amount');
      await expect(page.locator('th')).toContainText('Status');
    });

    test('should show payment details', async ({ page }) => {
      await page.goto('/dashboard/payments/');
      
      // Check payment entries
      const paymentRows = page.locator('tbody tr');
      await expect(paymentRows).toHaveCount(3); // Mock data
      
      // Check payment details
      await expect(page.locator('text=KES 2,500')).toBeVisible();
      await expect(page.locator('text=Completed')).toBeVisible();
      await expect(page.locator('text=M-PESA')).toBeVisible();
    });

    test('should allow downloading payment receipts', async ({ page }) => {
      await page.goto('/dashboard/payments/');
      
      // Click download receipt button
      const downloadButton = page.locator('button:has-text("Download Receipt")').first();
      await downloadButton.click();
      
      // Should trigger download
      const downloadPromise = page.waitForEvent('download');
      await downloadPromise;
    });
  });

  test.describe('Billing & Invoicing', () => {
    test('should generate invoice for subscription', async ({ page }) => {
      await page.goto('/dashboard/billing/');
      
      // Check invoice generation
      await expect(page.locator('button:has-text("Generate Invoice")')).toBeVisible();
      await page.click('button:has-text("Generate Invoice")');
      
      // Should show invoice
      await expect(page.locator('text=Invoice #')).toBeVisible();
      await expect(page.locator('text=KES 2,500')).toBeVisible();
    });

    test('should send invoice via email', async ({ page }) => {
      await page.goto('/dashboard/billing/');
      
      // Generate invoice
      await page.click('button:has-text("Generate Invoice")');
      
      // Send via email
      await page.click('button:has-text("Send via Email")');
      
      // Should show success message
      await expect(page.locator('.bg-green-100')).toContainText('Invoice sent successfully');
    });

    test('should display billing address', async ({ page }) => {
      await page.goto('/dashboard/billing/');
      
      // Check billing address section
      await expect(page.locator('text=Billing Address')).toBeVisible();
      await expect(page.locator('input[name="company_name"]')).toBeVisible();
      await expect(page.locator('input[name="address"]')).toBeVisible();
    });
  });

  test.describe('Subscription Renewal', () => {
    test('should show renewal reminder before expiry', async ({ page }) => {
      // Mock subscription expiring in 3 days
      await page.route('**/api/subscription/**', route => {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            status: 'active',
            plan: 'Professional',
            expires_at: new Date(Date.now() + 3 * 24 * 60 * 60 * 1000).toISOString()
          })
        });
      });
      
      await page.goto('/dashboard/');
      
      // Check renewal reminder
      await expect(page.locator('.bg-yellow-100')).toContainText('expires in 3 days');
      await expect(page.locator('button:has-text("Renew Now")')).toBeVisible();
    });

    test('should auto-renew subscription', async ({ page }) => {
      await page.goto('/dashboard/billing/');
      
      // Enable auto-renewal
      await page.check('input[name="auto_renewal"]');
      await page.click('button:has-text("Save Settings")');
      
      // Should show success message
      await expect(page.locator('.bg-green-100')).toContainText('Auto-renewal enabled');
    });
  });
});
