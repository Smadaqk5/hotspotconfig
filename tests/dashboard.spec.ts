/**
 * Dashboard Tests
 * Tests user dashboard functionality and features
 */

import { test, expect } from '@playwright/test';
import { testUsers, testTickets } from './fixtures/test-data';

test.describe('User Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    // Login as customer
    await page.goto('/login/');
    await page.fill('input[name="username"]', testUsers.customer.username);
    await page.fill('input[name="password"]', testUsers.customer.password);
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL(/.*dashboard/);
  });

  test.describe('Dashboard Overview', () => {
    test('should load dashboard successfully', async ({ page }) => {
      await page.goto('/dashboard/');
      
      // Check dashboard title
      await expect(page.locator('h1')).toContainText('Dashboard');
      await expect(page.locator('p')).toContainText('Manage your hotspot business');
    });

    test('should display stats cards correctly', async ({ page }) => {
      await page.goto('/dashboard/');
      
      // Check all stats cards are visible
      await expect(page.locator('text=Total Tickets')).toBeVisible();
      await expect(page.locator('text=Revenue')).toBeVisible();
      await expect(page.locator('text=Active Users')).toBeVisible();
      await expect(page.locator('text=Hotspots')).toBeVisible();
      
      // Check stats values
      const statsCards = page.locator('.bg-white.overflow-hidden.shadow.rounded-lg');
      await expect(statsCards).toHaveCount(4);
    });

    test('should display quick actions section', async ({ page }) => {
      await page.goto('/dashboard/');
      
      // Check quick actions
      await expect(page.locator('h3')).toContainText('Quick Actions');
      await expect(page.locator('button:has-text("Create New Ticket Type")')).toBeVisible();
      await expect(page.locator('button:has-text("Generate Tickets")')).toBeVisible();
      await expect(page.locator('button:has-text("View Reports")')).toBeVisible();
    });

    test('should display recent activity section', async ({ page }) => {
      await page.goto('/dashboard/');
      
      // Check recent activity
      await expect(page.locator('h3')).toContainText('Recent Activity');
      await expect(page.locator('text=Welcome to your dashboard')).toBeVisible();
    });
  });

  test.describe('Subscription Status', () => {
    test('should display subscription status card', async ({ page }) => {
      await page.goto('/dashboard/');
      
      // Check subscription status card
      await expect(page.locator('text=Subscription Status')).toBeVisible();
      
      // Should show current status
      const statusCard = page.locator('.bg-white.shadow.rounded-lg');
      await expect(statusCard).toBeVisible();
    });

    test('should show active subscription details', async ({ page }) => {
      // Mock active subscription
      await page.route('**/api/subscription/**', route => {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            status: 'active',
            plan: 'Professional',
            expires_at: '2024-02-15T00:00:00Z',
            features: ['Unlimited tickets', 'Advanced analytics', 'Priority support']
          })
        });
      });
      
      await page.goto('/dashboard/');
      
      // Check subscription details
      await expect(page.locator('text=Professional')).toBeVisible();
      await expect(page.locator('text=Active')).toBeVisible();
      await expect(page.locator('text=Unlimited tickets')).toBeVisible();
    });

    test('should show inactive subscription with upgrade prompt', async ({ page }) => {
      // Mock inactive subscription
      await page.route('**/api/subscription/**', route => {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            status: 'inactive',
            plan: null,
            features: []
          })
        });
      });
      
      await page.goto('/dashboard/');
      
      // Check inactive status
      await expect(page.locator('text=Inactive')).toBeVisible();
      await expect(page.locator('button:has-text("Subscribe Now")')).toBeVisible();
    });
  });

  test.describe('Ticket Generation', () => {
    test('should open ticket generation form', async ({ page }) => {
      await page.goto('/dashboard/');
      
      // Click generate tickets button
      await page.click('button:has-text("Generate Tickets")');
      
      // Should open ticket generation form
      await expect(page.locator('h2')).toContainText('Generate Tickets');
      await expect(page.locator('form')).toBeVisible();
    });

    test('should validate ticket form inputs', async ({ page }) => {
      await page.goto('/dashboard/tickets/generate/');
      
      // Try to submit empty form
      await page.click('button[type="submit"]');
      
      // Should show validation errors
      await expect(page.locator('input[name="ticket_name"]:invalid')).toBeVisible();
      await expect(page.locator('input[name="quantity"]:invalid')).toBeVisible();
    });

    test('should generate time-based tickets successfully', async ({ page }) => {
      await page.goto('/dashboard/tickets/generate/');
      
      // Fill ticket form
      await page.fill('input[name="ticket_name"]', testTickets.timeBased.name);
      await page.selectOption('select[name="ticket_type"]', 'time');
      await page.fill('input[name="duration"]', testTickets.timeBased.duration.toString());
      await page.fill('input[name="price"]', testTickets.timeBased.price.toString());
      await page.fill('input[name="quantity"]', '5');
      
      // Submit form
      await page.click('button[type="submit"]');
      
      // Should show success message
      await expect(page.locator('.bg-green-100')).toContainText('Tickets generated successfully');
      
      // Should redirect to tickets list
      await expect(page).toHaveURL(/.*tickets/);
    });

    test('should generate data-based tickets successfully', async ({ page }) => {
      await page.goto('/dashboard/tickets/generate/');
      
      // Fill ticket form for data-based
      await page.fill('input[name="ticket_name"]', testTickets.dataBased.name);
      await page.selectOption('select[name="ticket_type"]', 'data');
      await page.fill('input[name="data_limit"]', testTickets.dataBased.data_limit.toString());
      await page.fill('input[name="price"]', testTickets.dataBased.price.toString());
      await page.fill('input[name="quantity"]', '3');
      
      // Submit form
      await page.click('button[type="submit"]');
      
      // Should show success message
      await expect(page.locator('.bg-green-100')).toContainText('Tickets generated successfully');
    });
  });

  test.describe('Ticket Management', () => {
    test('should display tickets list', async ({ page }) => {
      await page.goto('/dashboard/tickets/');
      
      // Check tickets table
      await expect(page.locator('table')).toBeVisible();
      await expect(page.locator('th')).toContainText('Ticket ID');
      await expect(page.locator('th')).toContainText('Username');
      await expect(page.locator('th')).toContainText('Password');
      await expect(page.locator('th')).toContainText('Status');
      await expect(page.locator('th')).toContainText('Actions');
    });

    test('should show ticket details', async ({ page }) => {
      await page.goto('/dashboard/tickets/');
      
      // Check ticket entries
      const ticketRows = page.locator('tbody tr');
      await expect(ticketRows).toHaveCount(5); // Mock data
      
      // Check ticket details
      await expect(page.locator('text=TICKET_001')).toBeVisible();
      await expect(page.locator('text=Active')).toBeVisible();
    });

    test('should allow ticket deletion', async ({ page }) => {
      await page.goto('/dashboard/tickets/');
      
      // Click delete button for first ticket
      const deleteButton = page.locator('button:has-text("Delete")').first();
      await deleteButton.click();
      
      // Confirm deletion
      await page.click('button:has-text("Confirm Delete")');
      
      // Should show success message
      await expect(page.locator('.bg-green-100')).toContainText('Ticket deleted successfully');
    });

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
  });

  test.describe('Reports & Analytics', () => {
    test('should display revenue chart', async ({ page }) => {
      await page.goto('/dashboard/reports/');
      
      // Check revenue chart
      await expect(page.locator('canvas')).toBeVisible();
      await expect(page.locator('h3')).toContainText('Revenue Chart');
    });

    test('should show daily sales summary', async ({ page }) => {
      await page.goto('/dashboard/reports/');
      
      // Check daily sales
      await expect(page.locator('text=Today\'s Sales')).toBeVisible();
      await expect(page.locator('text=KES 1,250')).toBeVisible();
    });

    test('should show weekly sales summary', async ({ page }) => {
      await page.goto('/dashboard/reports/');
      
      // Check weekly sales
      await expect(page.locator('text=This Week')).toBeVisible();
      await expect(page.locator('text=KES 8,750')).toBeVisible();
    });

    test('should show monthly sales summary', async ({ page }) => {
      await page.goto('/dashboard/reports/');
      
      // Check monthly sales
      await expect(page.locator('text=This Month')).toBeVisible();
      await expect(page.locator('text=KES 35,000')).toBeVisible();
    });

    test('should allow date range filtering', async ({ page }) => {
      await page.goto('/dashboard/reports/');
      
      // Set date range
      await page.fill('input[name="start_date"]', '2024-01-01');
      await page.fill('input[name="end_date"]', '2024-01-31');
      await page.click('button:has-text("Filter")');
      
      // Should update reports
      await expect(page.locator('text=January 2024')).toBeVisible();
    });
  });

  test.describe('Export Functionality', () => {
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

    test('should export reports as PDF', async ({ page }) => {
      await page.goto('/dashboard/reports/');
      
      // Click export PDF button
      const downloadPromise = page.waitForEvent('download');
      await page.click('button:has-text("Export PDF")');
      const download = await downloadPromise;
      
      // Should download PDF file
      expect(download.suggestedFilename()).toContain('.pdf');
    });
  });

  test.describe('User Profile', () => {
    test('should display user profile information', async ({ page }) => {
      await page.goto('/dashboard/profile/');
      
      // Check profile form
      await expect(page.locator('input[name="first_name"]')).toHaveValue(testUsers.customer.first_name);
      await expect(page.locator('input[name="last_name"]')).toHaveValue(testUsers.customer.last_name);
      await expect(page.locator('input[name="email"]')).toHaveValue(testUsers.customer.email);
      await expect(page.locator('input[name="phone_number"]')).toHaveValue(testUsers.customer.phone_number);
    });

    test('should allow profile updates', async ({ page }) => {
      await page.goto('/dashboard/profile/');
      
      // Update profile
      await page.fill('input[name="first_name"]', 'Updated Name');
      await page.fill('input[name="company_name"]', 'Updated Company');
      await page.click('button:has-text("Update Profile")');
      
      // Should show success message
      await expect(page.locator('.bg-green-100')).toContainText('Profile updated successfully');
    });

    test('should allow password change', async ({ page }) => {
      await page.goto('/dashboard/profile/');
      
      // Click change password
      await page.click('button:has-text("Change Password")');
      
      // Fill password form
      await page.fill('input[name="current_password"]', testUsers.customer.password);
      await page.fill('input[name="new_password"]', 'newpassword123');
      await page.fill('input[name="confirm_password"]', 'newpassword123');
      await page.click('button:has-text("Update Password")');
      
      // Should show success message
      await expect(page.locator('.bg-green-100')).toContainText('Password updated successfully');
    });
  });

  test.describe('Navigation', () => {
    test('should have working navigation menu', async ({ page }) => {
      await page.goto('/dashboard/');
      
      // Check navigation links
      await expect(page.locator('a:has-text("Dashboard")')).toBeVisible();
      await expect(page.locator('a:has-text("Tickets")')).toBeVisible();
      await expect(page.locator('a:has-text("Reports")')).toBeVisible();
      await expect(page.locator('a:has-text("Profile")')).toBeVisible();
    });

    test('should navigate between dashboard sections', async ({ page }) => {
      await page.goto('/dashboard/');
      
      // Navigate to tickets
      await page.click('a:has-text("Tickets")');
      await expect(page).toHaveURL(/.*tickets/);
      
      // Navigate to reports
      await page.click('a:has-text("Reports")');
      await expect(page).toHaveURL(/.*reports/);
      
      // Navigate to profile
      await page.click('a:has-text("Profile")');
      await expect(page).toHaveURL(/.*profile/);
    });
  });
});
