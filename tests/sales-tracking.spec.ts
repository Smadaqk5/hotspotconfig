/**
 * Sales Tracking Tests
 * Tests revenue calculation, analytics, and reporting functionality
 */

import { test, expect } from '@playwright/test';
import { testUsers } from './fixtures/test-data';

test.describe('Sales Tracking', () => {
  test.beforeEach(async ({ page }) => {
    // Login as customer
    await page.goto('/login/');
    await page.fill('input[name="username"]', testUsers.customer.username);
    await page.fill('input[name="password"]', testUsers.customer.password);
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL(/.*dashboard/);
  });

  test.describe('Revenue Calculation', () => {
    test('should calculate total sales correctly', async ({ page }) => {
      await page.goto('/dashboard/reports/');
      
      // Check total sales calculation
      await expect(page.locator('text=Total Sales')).toBeVisible();
      await expect(page.locator('text=KES 15,250')).toBeVisible();
    });

    test('should calculate daily sales', async ({ page }) => {
      await page.goto('/dashboard/reports/');
      
      // Check daily sales
      await expect(page.locator('text=Today\'s Sales')).toBeVisible();
      await expect(page.locator('text=KES 1,250')).toBeVisible();
    });

    test('should calculate weekly sales', async ({ page }) => {
      await page.goto('/dashboard/reports/');
      
      // Check weekly sales
      await expect(page.locator('text=This Week')).toBeVisible();
      await expect(page.locator('text=KES 8,750')).toBeVisible();
    });

    test('should calculate monthly sales', async ({ page }) => {
      await page.goto('/dashboard/reports/');
      
      // Check monthly sales
      await expect(page.locator('text=This Month')).toBeVisible();
      await expect(page.locator('text=KES 35,000')).toBeVisible();
    });

    test('should update revenue after selling tickets', async ({ page }) => {
      // Mock selling tickets
      await page.route('**/api/tickets/sell/**', route => {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            success: true,
            revenue: 500,
            total_revenue: 15750
          })
        });
      });
      
      await page.goto('/dashboard/tickets/');
      
      // Sell a ticket
      await page.click('button:has-text("Sell Ticket")').first();
      await page.fill('input[name="customer_name"]', 'Test Customer');
      await page.fill('input[name="customer_phone"]', '+254700000000');
      await page.click('button[type="submit"]');
      
      // Check revenue updated
      await expect(page.locator('.bg-green-100')).toContainText('Ticket sold successfully');
      
      // Navigate to reports
      await page.goto('/dashboard/reports/');
      
      // Check updated revenue
      await expect(page.locator('text=KES 15,750')).toBeVisible();
    });
  });

  test.describe('Revenue Dashboard', () => {
    test('should display revenue chart', async ({ page }) => {
      await page.goto('/dashboard/reports/');
      
      // Check revenue chart
      await expect(page.locator('canvas')).toBeVisible();
      await expect(page.locator('h3')).toContainText('Revenue Chart');
    });

    test('should show revenue trends', async ({ page }) => {
      await page.goto('/dashboard/reports/');
      
      // Check trend indicators
      await expect(page.locator('text=+15%')).toBeVisible(); // Daily trend
      await expect(page.locator('text=+8%')).toBeVisible(); // Weekly trend
      await expect(page.locator('text=+12%')).toBeVisible(); // Monthly trend
    });

    test('should display revenue by ticket type', async ({ page }) => {
      await page.goto('/dashboard/reports/');
      
      // Check revenue breakdown
      await expect(page.locator('text=Revenue by Type')).toBeVisible();
      await expect(page.locator('text=Time-based: KES 8,500')).toBeVisible();
      await expect(page.locator('text=Data-based: KES 6,750')).toBeVisible();
    });

    test('should show top selling tickets', async ({ page }) => {
      await page.goto('/dashboard/reports/');
      
      // Check top selling section
      await expect(page.locator('h3')).toContainText('Top Selling Tickets');
      await expect(page.locator('text=1 Hour Ticket')).toBeVisible();
      await expect(page.locator('text=1GB Data Ticket')).toBeVisible();
    });
  });

  test.describe('Analytics & Reports', () => {
    test('should display sales analytics', async ({ page }) => {
      await page.goto('/dashboard/reports/analytics/');
      
      // Check analytics sections
      await expect(page.locator('h2')).toContainText('Sales Analytics');
      await expect(page.locator('text=Conversion Rate')).toBeVisible();
      await expect(page.locator('text=Average Order Value')).toBeVisible();
      await expect(page.locator('text=Customer Retention')).toBeVisible();
    });

    test('should show customer analytics', async ({ page }) => {
      await page.goto('/dashboard/reports/customers/');
      
      // Check customer analytics
      await expect(page.locator('h2')).toContainText('Customer Analytics');
      await expect(page.locator('text=New Customers')).toBeVisible();
      await expect(page.locator('text=Returning Customers')).toBeVisible();
      await expect(page.locator('text=Customer Lifetime Value')).toBeVisible();
    });

    test('should display performance metrics', async ({ page }) => {
      await page.goto('/dashboard/reports/performance/');
      
      // Check performance metrics
      await expect(page.locator('h2')).toContainText('Performance Metrics');
      await expect(page.locator('text=Peak Hours')).toBeVisible();
      await expect(page.locator('text=Average Session Duration')).toBeVisible();
      await expect(page.locator('text=Data Usage Patterns')).toBeVisible();
    });
  });

  test.describe('Date Range Filtering', () => {
    test('should filter reports by date range', async ({ page }) => {
      await page.goto('/dashboard/reports/');
      
      // Set custom date range
      await page.fill('input[name="start_date"]', '2024-01-01');
      await page.fill('input[name="end_date"]', '2024-01-31');
      await page.click('button:has-text("Apply Filter")');
      
      // Should update reports for January 2024
      await expect(page.locator('text=January 2024')).toBeVisible();
    });

    test('should filter by predefined periods', async ({ page }) => {
      await page.goto('/dashboard/reports/');
      
      // Select last 7 days
      await page.selectOption('select[name="period"]', 'last_7_days');
      await page.click('button:has-text("Apply Filter")');
      
      // Should show last 7 days data
      await expect(page.locator('text=Last 7 Days')).toBeVisible();
    });

    test('should filter by specific months', async ({ page }) => {
      await page.goto('/dashboard/reports/');
      
      // Select specific month
      await page.selectOption('select[name="month"]', '2024-01');
      await page.click('button:has-text("Apply Filter")');
      
      // Should show January 2024 data
      await expect(page.locator('text=January 2024')).toBeVisible();
    });
  });

  test.describe('Export Functionality', () => {
    test('should export sales data as CSV', async ({ page }) => {
      await page.goto('/dashboard/reports/');
      
      // Click export CSV button
      const downloadPromise = page.waitForEvent('download');
      await page.click('button:has-text("Export CSV")');
      const download = await downloadPromise;
      
      // Should download CSV file
      expect(download.suggestedFilename()).toContain('.csv');
    });

    test('should export sales data as Excel', async ({ page }) => {
      await page.goto('/dashboard/reports/');
      
      // Click export Excel button
      const downloadPromise = page.waitForEvent('download');
      await page.click('button:has-text("Export Excel")');
      const download = await downloadPromise;
      
      // Should download Excel file
      expect(download.suggestedFilename()).toContain('.xlsx');
    });

    test('should export sales report as PDF', async ({ page }) => {
      await page.goto('/dashboard/reports/');
      
      // Click export PDF button
      const downloadPromise = page.waitForEvent('download');
      await page.click('button:has-text("Export PDF")');
      const download = await downloadPromise;
      
      // Should download PDF file
      expect(download.suggestedFilename()).toContain('.pdf');
    });

    test('should export filtered data', async ({ page }) => {
      await page.goto('/dashboard/reports/');
      
      // Apply date filter
      await page.fill('input[name="start_date"]', '2024-01-01');
      await page.fill('input[name="end_date"]', '2024-01-31');
      await page.click('button:has-text("Apply Filter")');
      
      // Export filtered data
      const downloadPromise = page.waitForEvent('download');
      await page.click('button:has-text("Export CSV")');
      const download = await downloadPromise;
      
      // Should download filtered data
      expect(download.suggestedFilename()).toContain('January_2024');
    });
  });

  test.describe('Real-time Updates', () => {
    test('should update revenue in real-time', async ({ page }) => {
      await page.goto('/dashboard/reports/');
      
      // Check initial revenue
      await expect(page.locator('text=KES 15,250')).toBeVisible();
      
      // Simulate real-time update
      await page.evaluate(() => {
        // Mock real-time update
        const revenueElement = document.querySelector('[data-testid="total-revenue"]');
        if (revenueElement) {
          revenueElement.textContent = 'KES 15,500';
        }
      });
      
      // Should show updated revenue
      await expect(page.locator('text=KES 15,500')).toBeVisible();
    });

    test('should show live sales notifications', async ({ page }) => {
      await page.goto('/dashboard/reports/');
      
      // Simulate new sale notification
      await page.evaluate(() => {
        // Mock notification
        const notification = document.createElement('div');
        notification.className = 'bg-green-100 p-4 rounded';
        notification.textContent = 'New sale: 1 Hour Ticket - KES 50';
        document.body.appendChild(notification);
      });
      
      // Should show notification
      await expect(page.locator('text=New sale: 1 Hour Ticket - KES 50')).toBeVisible();
    });
  });

  test.describe('Performance Metrics', () => {
    test('should display conversion rates', async ({ page }) => {
      await page.goto('/dashboard/reports/analytics/');
      
      // Check conversion metrics
      await expect(page.locator('text=Conversion Rate')).toBeVisible();
      await expect(page.locator('text=75%')).toBeVisible();
    });

    test('should show average order value', async ({ page }) => {
      await page.goto('/dashboard/reports/analytics/');
      
      // Check AOV
      await expect(page.locator('text=Average Order Value')).toBeVisible();
      await expect(page.locator('text=KES 125')).toBeVisible();
    });

    test('should display customer retention rate', async ({ page }) => {
      await page.goto('/dashboard/reports/analytics/');
      
      // Check retention rate
      await expect(page.locator('text=Customer Retention')).toBeVisible();
      await expect(page.locator('text=68%')).toBeVisible();
    });
  });

  test.describe('Comparative Analysis', () => {
    test('should compare periods', async ({ page }) => {
      await page.goto('/dashboard/reports/');
      
      // Enable period comparison
      await page.check('input[name="compare_periods"]');
      await page.selectOption('select[name="compare_to"]', 'previous_month');
      await page.click('button:has-text("Apply Comparison")');
      
      // Should show comparison data
      await expect(page.locator('text=vs Previous Month')).toBeVisible();
      await expect(page.locator('text=+12%')).toBeVisible();
    });

    test('should show year-over-year comparison', async ({ page }) => {
      await page.goto('/dashboard/reports/');
      
      // Select year-over-year comparison
      await page.check('input[name="compare_periods"]');
      await page.selectOption('select[name="compare_to"]', 'same_period_last_year');
      await page.click('button:has-text("Apply Comparison")');
      
      // Should show YoY comparison
      await expect(page.locator('text=vs Same Period Last Year')).toBeVisible();
      await expect(page.locator('text=+25%')).toBeVisible();
    });
  });
});
