/**
 * Ticket Management Tests
 * Tests ticket generation, management, and expiry functionality
 */

import { test, expect } from '@playwright/test';
import { testUsers, testTickets } from './fixtures/test-data';

test.describe('Ticket Management', () => {
  test.beforeEach(async ({ page }) => {
    // Login as customer
    await page.goto('/login/');
    await page.fill('input[name="username"]', testUsers.customer.username);
    await page.fill('input[name="password"]', testUsers.customer.password);
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL(/.*dashboard/);
  });

  test.describe('Time-Based Tickets', () => {
    test('should generate 1-hour tickets successfully', async ({ page }) => {
      await page.goto('/dashboard/tickets/generate/');
      
      // Fill form for 1-hour ticket
      await page.fill('input[name="ticket_name"]', '1 Hour Internet');
      await page.selectOption('select[name="ticket_type"]', 'time');
      await page.fill('input[name="duration"]', '3600'); // 1 hour in seconds
      await page.fill('input[name="price"]', '50');
      await page.fill('input[name="quantity"]', '10');
      await page.fill('textarea[name="description"]', '1 hour internet access');
      
      // Submit form
      await page.click('button[type="submit"]');
      
      // Should show success message
      await expect(page.locator('.bg-green-100')).toContainText('Tickets generated successfully');
      
      // Should redirect to tickets list
      await expect(page).toHaveURL(/.*tickets/);
      
      // Check tickets were created
      const ticketRows = page.locator('tbody tr');
      await expect(ticketRows).toHaveCount(10);
    });

    test('should generate 1-day tickets successfully', async ({ page }) => {
      await page.goto('/dashboard/tickets/generate/');
      
      // Fill form for 1-day ticket
      await page.fill('input[name="ticket_name"]', '1 Day Internet');
      await page.selectOption('select[name="ticket_type"]', 'time');
      await page.fill('input[name="duration"]', '86400'); // 1 day in seconds
      await page.fill('input[name="price"]', '200');
      await page.fill('input[name="quantity"]', '5');
      await page.fill('textarea[name="description"]', '1 day internet access');
      
      // Submit form
      await page.click('button[type="submit"]');
      
      // Should show success message
      await expect(page.locator('.bg-green-100')).toContainText('Tickets generated successfully');
    });

    test('should validate time duration input', async ({ page }) => {
      await page.goto('/dashboard/tickets/generate/');
      
      // Try to submit with invalid duration
      await page.fill('input[name="ticket_name"]', 'Test Ticket');
      await page.selectOption('select[name="ticket_type"]', 'time');
      await page.fill('input[name="duration"]', '0'); // Invalid duration
      await page.fill('input[name="price"]', '50');
      await page.fill('input[name="quantity"]', '1');
      
      // Submit form
      await page.click('button[type="submit"]');
      
      // Should show validation error
      await expect(page.locator('.bg-red-100')).toContainText('Duration must be greater than 0');
    });
  });

  test.describe('Data-Based Tickets', () => {
    test('should generate 1GB data tickets successfully', async ({ page }) => {
      await page.goto('/dashboard/tickets/generate/');
      
      // Fill form for 1GB data ticket
      await page.fill('input[name="ticket_name"]', '1GB Data');
      await page.selectOption('select[name="ticket_type"]', 'data');
      await page.fill('input[name="data_limit"]', '1024'); // 1GB in MB
      await page.fill('input[name="price"]', '100');
      await page.fill('input[name="quantity"]', '8');
      await page.fill('textarea[name="description"]', '1GB data allowance');
      
      // Submit form
      await page.click('button[type="submit"]');
      
      // Should show success message
      await expect(page.locator('.bg-green-100')).toContainText('Tickets generated successfully');
    });

    test('should generate 5GB data tickets successfully', async ({ page }) => {
      await page.goto('/dashboard/tickets/generate/');
      
      // Fill form for 5GB data ticket
      await page.fill('input[name="ticket_name"]', '5GB Data');
      await page.selectOption('select[name="ticket_type"]', 'data');
      await page.fill('input[name="data_limit"]', '5120'); // 5GB in MB
      await page.fill('input[name="price"]', '400');
      await page.fill('input[name="quantity"]', '3');
      await page.fill('textarea[name="description"]', '5GB data allowance');
      
      // Submit form
      await page.click('button[type="submit"]');
      
      // Should show success message
      await expect(page.locator('.bg-green-100')).toContainText('Tickets generated successfully');
    });

    test('should validate data limit input', async ({ page }) => {
      await page.goto('/dashboard/tickets/generate/');
      
      // Try to submit with invalid data limit
      await page.fill('input[name="ticket_name"]', 'Test Data Ticket');
      await page.selectOption('select[name="ticket_type"]', 'data');
      await page.fill('input[name="data_limit"]', '0'); // Invalid data limit
      await page.fill('input[name="price"]', '100');
      await page.fill('input[name="quantity"]', '1');
      
      // Submit form
      await page.click('button[type="submit"]');
      
      // Should show validation error
      await expect(page.locator('.bg-red-100')).toContainText('Data limit must be greater than 0');
    });
  });

  test.describe('Ticket Display & Management', () => {
    test('should display generated tickets in table', async ({ page }) => {
      await page.goto('/dashboard/tickets/');
      
      // Check table headers
      await expect(page.locator('th')).toContainText('Ticket ID');
      await expect(page.locator('th')).toContainText('Username');
      await expect(page.locator('th')).toContainText('Password');
      await expect(page.locator('th')).toContainText('Type');
      await expect(page.locator('th')).toContainText('Status');
      await expect(page.locator('th')).toContainText('Created');
      await expect(page.locator('th')).toContainText('Actions');
    });

    test('should show ticket details correctly', async ({ page }) => {
      await page.goto('/dashboard/tickets/');
      
      // Check ticket details
      await expect(page.locator('text=TICKET_001')).toBeVisible();
      await expect(page.locator('text=user001')).toBeVisible();
      await expect(page.locator('text=pass001')).toBeVisible();
      await expect(page.locator('text=Time')).toBeVisible();
      await expect(page.locator('text=Active')).toBeVisible();
    });

    test('should allow ticket status filtering', async ({ page }) => {
      await page.goto('/dashboard/tickets/');
      
      // Filter by active tickets
      await page.selectOption('select[name="status_filter"]', 'active');
      await page.click('button:has-text("Filter")');
      
      // Should show only active tickets
      await expect(page.locator('text=Active')).toBeVisible();
      await expect(page.locator('text=Expired')).not.toBeVisible();
    });

    test('should allow ticket type filtering', async ({ page }) => {
      await page.goto('/dashboard/tickets/');
      
      // Filter by time-based tickets
      await page.selectOption('select[name="type_filter"]', 'time');
      await page.click('button:has-text("Filter")');
      
      // Should show only time-based tickets
      await expect(page.locator('text=Time')).toBeVisible();
      await expect(page.locator('text=Data')).not.toBeVisible();
    });
  });

  test.describe('Ticket Expiry Logic', () => {
    test('should show expired tickets as inactive', async ({ page }) => {
      // Mock expired tickets
      await page.route('**/api/tickets/**', route => {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify([
            {
              id: 'TICKET_001',
              username: 'user001',
              password: 'pass001',
              type: 'time',
              status: 'expired',
              created_at: '2024-01-01T00:00:00Z',
              expires_at: '2024-01-01T01:00:00Z'
            }
          ])
        });
      });
      
      await page.goto('/dashboard/tickets/');
      
      // Check expired ticket shows as inactive
      await expect(page.locator('text=Expired')).toBeVisible();
    });

    test('should auto-disable expired tickets', async ({ page }) => {
      await page.goto('/dashboard/tickets/');
      
      // Check that expired tickets are automatically disabled
      const expiredTickets = page.locator('tr:has-text("Expired")');
      await expect(expiredTickets).toBeVisible();
      
      // Expired tickets should not be usable
      await expect(page.locator('button:has-text("Use Ticket")')).not.toBeVisible();
    });

    test('should show expiry countdown for active tickets', async ({ page }) => {
      // Mock ticket expiring in 30 minutes
      await page.route('**/api/tickets/**', route => {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify([
            {
              id: 'TICKET_001',
              username: 'user001',
              password: 'pass001',
              type: 'time',
              status: 'active',
              created_at: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
              expires_at: new Date(Date.now() + 30 * 60 * 1000).toISOString()
            }
          ])
        });
      });
      
      await page.goto('/dashboard/tickets/');
      
      // Check countdown is displayed
      await expect(page.locator('text=30 minutes')).toBeVisible();
    });
  });

  test.describe('Ticket Actions', () => {
    test('should allow ticket deletion', async ({ page }) => {
      await page.goto('/dashboard/tickets/');
      
      // Click delete button for first ticket
      const deleteButton = page.locator('button:has-text("Delete")').first();
      await deleteButton.click();
      
      // Confirm deletion in modal
      await expect(page.locator('text=Confirm Delete')).toBeVisible();
      await page.click('button:has-text("Confirm Delete")');
      
      // Should show success message
      await expect(page.locator('.bg-green-100')).toContainText('Ticket deleted successfully');
    });

    test('should allow bulk ticket deletion', async ({ page }) => {
      await page.goto('/dashboard/tickets/');
      
      // Select multiple tickets
      await page.check('input[type="checkbox"]:nth-of-type(1)');
      await page.check('input[type="checkbox"]:nth-of-type(2)');
      
      // Click bulk delete
      await page.click('button:has-text("Bulk Delete")');
      
      // Confirm bulk deletion
      await page.click('button:has-text("Confirm Delete")');
      
      // Should show success message
      await expect(page.locator('.bg-green-100')).toContainText('Tickets deleted successfully');
    });

    test('should allow ticket status toggle', async ({ page }) => {
      await page.goto('/dashboard/tickets/');
      
      // Toggle ticket status
      await page.click('button:has-text("Toggle Status")').first();
      
      // Should show success message
      await expect(page.locator('.bg-green-100')).toContainText('Ticket status updated');
    });
  });

  test.describe('Ticket Export', () => {
    test('should export tickets as CSV', async ({ page }) => {
      await page.goto('/dashboard/tickets/');
      
      // Click export CSV button
      const downloadPromise = page.waitForEvent('download');
      await page.click('button:has-text("Export CSV")');
      const download = await downloadPromise;
      
      // Should download CSV file
      expect(download.suggestedFilename()).toContain('.csv');
    });

    test('should export tickets as Excel', async ({ page }) => {
      await page.goto('/dashboard/tickets/');
      
      // Click export Excel button
      const downloadPromise = page.waitForEvent('download');
      await page.click('button:has-text("Export Excel")');
      const download = await downloadPromise;
      
      // Should download Excel file
      expect(download.suggestedFilename()).toContain('.xlsx');
    });

    test('should export tickets as PDF', async ({ page }) => {
      await page.goto('/dashboard/tickets/');
      
      // Click export PDF button
      const downloadPromise = page.waitForEvent('download');
      await page.click('button:has-text("Export PDF")');
      const download = await downloadPromise;
      
      // Should download PDF file
      expect(download.suggestedFilename()).toContain('.pdf');
    });
  });

  test.describe('Ticket Printing', () => {
    test('should print individual ticket', async ({ page }) => {
      await page.goto('/dashboard/tickets/');
      
      // Click print button for first ticket
      await page.click('button:has-text("Print")').first();
      
      // Should open print dialog
      await expect(page.locator('text=Print Ticket')).toBeVisible();
    });

    test('should print multiple tickets', async ({ page }) => {
      await page.goto('/dashboard/tickets/');
      
      // Select multiple tickets
      await page.check('input[type="checkbox"]:nth-of-type(1)');
      await page.check('input[type="checkbox"]:nth-of-type(2)');
      
      // Click bulk print
      await page.click('button:has-text("Bulk Print")');
      
      // Should open print dialog for multiple tickets
      await expect(page.locator('text=Print Tickets')).toBeVisible();
    });

    test('should support thermal printer format', async ({ page }) => {
      await page.goto('/dashboard/tickets/');
      
      // Click print with thermal format
      await page.click('button:has-text("Print")').first();
      await page.selectOption('select[name="printer_format"]', 'thermal');
      await page.click('button:has-text("Print")');
      
      // Should format for thermal printer
      await expect(page.locator('text=Thermal Format')).toBeVisible();
    });
  });

  test.describe('Ticket Analytics', () => {
    test('should display ticket usage statistics', async ({ page }) => {
      await page.goto('/dashboard/tickets/analytics/');
      
      // Check analytics sections
      await expect(page.locator('h3')).toContainText('Ticket Usage Statistics');
      await expect(page.locator('text=Total Generated')).toBeVisible();
      await expect(page.locator('text=Active Tickets')).toBeVisible();
      await expect(page.locator('text=Expired Tickets')).toBeVisible();
    });

    test('should show revenue by ticket type', async ({ page }) => {
      await page.goto('/dashboard/tickets/analytics/');
      
      // Check revenue breakdown
      await expect(page.locator('text=Revenue by Type')).toBeVisible();
      await expect(page.locator('text=Time-based')).toBeVisible();
      await expect(page.locator('text=Data-based')).toBeVisible();
    });

    test('should display usage trends chart', async ({ page }) => {
      await page.goto('/dashboard/tickets/analytics/');
      
      // Check chart is displayed
      await expect(page.locator('canvas')).toBeVisible();
      await expect(page.locator('h3')).toContainText('Usage Trends');
    });
  });
});
