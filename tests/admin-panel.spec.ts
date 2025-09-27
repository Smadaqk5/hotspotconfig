/**
 * Admin Panel Tests
 * Tests admin functionality and user management
 */

import { test, expect } from '@playwright/test';
import { testUsers } from './fixtures/test-data';

test.describe('Admin Panel', () => {
  test.beforeEach(async ({ page }) => {
    // Login as admin
    await page.goto('/login/');
    await page.fill('input[name="username"]', testUsers.admin.username);
    await page.fill('input[name="password"]', testUsers.admin.password);
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL(/.*dashboard/);
  });

  test.describe('Admin Dashboard', () => {
    test('should load admin dashboard successfully', async ({ page }) => {
      await page.goto('/admin/');
      
      // Check admin dashboard title
      await expect(page.locator('h1')).toContainText('Admin Dashboard');
      await expect(page.locator('p')).toContainText('System administration');
    });

    test('should display admin statistics', async ({ page }) => {
      await page.goto('/admin/');
      
      // Check admin stats cards
      await expect(page.locator('text=Total Users')).toBeVisible();
      await expect(page.locator('text=Active Subscriptions')).toBeVisible();
      await expect(page.locator('text=Total Revenue')).toBeVisible();
      await expect(page.locator('text=System Health')).toBeVisible();
    });

    test('should display recent activity', async ({ page }) => {
      await page.goto('/admin/');
      
      // Check recent activity section
      await expect(page.locator('h3')).toContainText('Recent Activity');
      await expect(page.locator('text=User registrations')).toBeVisible();
      await expect(page.locator('text=Payment transactions')).toBeVisible();
    });
  });

  test.describe('User Management', () => {
    test('should display users list', async ({ page }) => {
      await page.goto('/admin/users/');
      
      // Check users table
      await expect(page.locator('table')).toBeVisible();
      await expect(page.locator('th')).toContainText('Username');
      await expect(page.locator('th')).toContainText('Email');
      await expect(page.locator('th')).toContainText('Status');
      await expect(page.locator('th')).toContainText('Actions');
    });

    test('should allow user activation', async ({ page }) => {
      await page.goto('/admin/users/');
      
      // Find inactive user and activate
      const activateButton = page.locator('button:has-text("Activate")').first();
      await activateButton.click();
      
      // Should show success message
      await expect(page.locator('.bg-green-100')).toContainText('User activated successfully');
    });

    test('should allow user suspension', async ({ page }) => {
      await page.goto('/admin/users/');
      
      // Find active user and suspend
      const suspendButton = page.locator('button:has-text("Suspend")').first();
      await suspendButton.click();
      
      // Confirm suspension
      await page.click('button:has-text("Confirm Suspend")');
      
      // Should show success message
      await expect(page.locator('.bg-green-100')).toContainText('User suspended successfully');
    });

    test('should allow user deletion', async ({ page }) => {
      await page.goto('/admin/users/');
      
      // Find user to delete
      const deleteButton = page.locator('button:has-text("Delete")').first();
      await deleteButton.click();
      
      // Confirm deletion
      await page.click('button:has-text("Confirm Delete")');
      
      // Should show success message
      await expect(page.locator('.bg-green-100')).toContainText('User deleted successfully');
    });

    test('should allow user role changes', async ({ page }) => {
      await page.goto('/admin/users/');
      
      // Change user role
      const roleSelect = page.locator('select[name="role"]').first();
      await roleSelect.selectOption('operator');
      await page.click('button:has-text("Update Role")');
      
      // Should show success message
      await expect(page.locator('.bg-green-100')).toContainText('User role updated successfully');
    });
  });

  test.describe('Billing Template Management', () => {
    test('should display billing templates', async ({ page }) => {
      await page.goto('/admin/billing-templates/');
      
      // Check templates table
      await expect(page.locator('table')).toBeVisible();
      await expect(page.locator('th')).toContainText('Name');
      await expect(page.locator('th')).toContainText('Mbps');
      await expect(page.locator('th')).toContainText('Duration');
      await expect(page.locator('th')).toContainText('Price');
      await expect(page.locator('th')).toContainText('Actions');
    });

    test('should allow adding new billing template', async ({ page }) => {
      await page.goto('/admin/billing-templates/');
      
      // Click add template button
      await page.click('button:has-text("Add Template")');
      
      // Fill template form
      await page.fill('input[name="name"]', 'Test Template');
      await page.fill('input[name="mbps"]', '10');
      await page.fill('input[name="duration"]', '3600');
      await page.fill('input[name="price"]', '100');
      await page.fill('textarea[name="description"]', 'Test billing template');
      
      // Submit form
      await page.click('button[type="submit"]');
      
      // Should show success message
      await expect(page.locator('.bg-green-100')).toContainText('Billing template created successfully');
    });

    test('should allow editing billing template', async ({ page }) => {
      await page.goto('/admin/billing-templates/');
      
      // Click edit button for first template
      await page.click('button:has-text("Edit")').first();
      
      // Update template
      await page.fill('input[name="name"]', 'Updated Template');
      await page.fill('input[name="price"]', '150');
      await page.click('button[type="submit"]');
      
      // Should show success message
      await expect(page.locator('.bg-green-100')).toContainText('Billing template updated successfully');
    });

    test('should allow deleting billing template', async ({ page }) => {
      await page.goto('/admin/billing-templates/');
      
      // Click delete button for first template
      await page.click('button:has-text("Delete")').first();
      
      // Confirm deletion
      await page.click('button:has-text("Confirm Delete")');
      
      // Should show success message
      await expect(page.locator('.bg-green-100')).toContainText('Billing template deleted successfully');
    });
  });

  test.describe('Config Template Management', () => {
    test('should display config templates', async ({ page }) => {
      await page.goto('/admin/config-templates/');
      
      // Check templates table
      await expect(page.locator('table')).toBeVisible();
      await expect(page.locator('th')).toContainText('Name');
      await expect(page.locator('th')).toContainText('Model');
      await expect(page.locator('th')).toContainText('Type');
      await expect(page.locator('th')).toContainText('Actions');
    });

    test('should allow adding new config template', async ({ page }) => {
      await page.goto('/admin/config-templates/');
      
      // Click add template button
      await page.click('button:has-text("Add Template")');
      
      // Fill template form
      await page.fill('input[name="name"]', 'Test Config Template');
      await page.selectOption('select[name="mikrotik_model"]', 'RB750');
      await page.selectOption('select[name="template_type"]', 'basic');
      await page.fill('textarea[name="template_content"]', '/ip hotspot setup');
      
      // Submit form
      await page.click('button[type="submit"]');
      
      // Should show success message
      await expect(page.locator('.bg-green-100')).toContainText('Config template created successfully');
    });

    test('should allow editing config template', async ({ page }) => {
      await page.goto('/admin/config-templates/');
      
      // Click edit button for first template
      await page.click('button:has-text("Edit")').first();
      
      // Update template
      await page.fill('input[name="name"]', 'Updated Config Template');
      await page.fill('textarea[name="template_content"]', '/ip hotspot setup\n/ip hotspot user');
      await page.click('button[type="submit"]');
      
      // Should show success message
      await expect(page.locator('.bg-green-100')).toContainText('Config template updated successfully');
    });

    test('should allow previewing config template', async ({ page }) => {
      await page.goto('/admin/config-templates/');
      
      // Click preview button for first template
      await page.click('button:has-text("Preview")').first();
      
      // Should show preview modal
      await expect(page.locator('text=Template Preview')).toBeVisible();
      await expect(page.locator('pre')).toBeVisible();
    });
  });

  test.describe('Payment Logs', () => {
    test('should display payment transactions', async ({ page }) => {
      await page.goto('/admin/payments/');
      
      // Check payments table
      await expect(page.locator('table')).toBeVisible();
      await expect(page.locator('th')).toContainText('Transaction ID');
      await expect(page.locator('th')).toContainText('User');
      await expect(page.locator('th')).toContainText('Amount');
      await expect(page.locator('th')).toContainText('Status');
      await expect(page.locator('th')).toContainText('Date');
    });

    test('should filter payments by status', async ({ page }) => {
      await page.goto('/admin/payments/');
      
      // Filter by completed payments
      await page.selectOption('select[name="status_filter"]', 'completed');
      await page.click('button:has-text("Filter")');
      
      // Should show only completed payments
      await expect(page.locator('text=Completed')).toBeVisible();
      await expect(page.locator('text=Failed')).not.toBeVisible();
    });

    test('should filter payments by date range', async ({ page }) => {
      await page.goto('/admin/payments/');
      
      // Set date range
      await page.fill('input[name="start_date"]', '2024-01-01');
      await page.fill('input[name="end_date"]', '2024-01-31');
      await page.click('button:has-text("Filter")');
      
      // Should show payments in date range
      await expect(page.locator('text=January 2024')).toBeVisible();
    });

    test('should export payment logs', async ({ page }) => {
      await page.goto('/admin/payments/');
      
      // Click export button
      const downloadPromise = page.waitForEvent('download');
      await page.click('button:has-text("Export")');
      const download = await downloadPromise;
      
      // Should download payment logs
      expect(download.suggestedFilename()).toContain('.csv');
    });
  });

  test.describe('System Settings', () => {
    test('should display system settings', async ({ page }) => {
      await page.goto('/admin/settings/');
      
      // Check settings sections
      await expect(page.locator('h3')).toContainText('General Settings');
      await expect(page.locator('h3')).toContainText('Email Settings');
      await expect(page.locator('h3')).toContainText('Payment Settings');
    });

    test('should allow updating general settings', async ({ page }) => {
      await page.goto('/admin/settings/');
      
      // Update site name
      await page.fill('input[name="site_name"]', 'Updated Hotspot Config');
      await page.fill('input[name="site_email"]', 'admin@updated.com');
      await page.click('button:has-text("Save Settings")');
      
      // Should show success message
      await expect(page.locator('.bg-green-100')).toContainText('Settings updated successfully');
    });

    test('should allow updating email settings', async ({ page }) => {
      await page.goto('/admin/settings/');
      
      // Update email settings
      await page.fill('input[name="smtp_host"]', 'smtp.gmail.com');
      await page.fill('input[name="smtp_port"]', '587');
      await page.fill('input[name="smtp_username"]', 'admin@example.com');
      await page.fill('input[name="smtp_password"]', 'password123');
      await page.click('button:has-text("Save Email Settings")');
      
      // Should show success message
      await expect(page.locator('.bg-green-100')).toContainText('Email settings updated successfully');
    });

    test('should allow updating payment settings', async ({ page }) => {
      await page.goto('/admin/settings/');
      
      // Update payment settings
      await page.fill('input[name="pesapal_consumer_key"]', 'new_consumer_key');
      await page.fill('input[name="pesapal_consumer_secret"]', 'new_consumer_secret');
      await page.click('button:has-text("Save Payment Settings")');
      
      // Should show success message
      await expect(page.locator('.bg-green-100')).toContainText('Payment settings updated successfully');
    });
  });

  test.describe('Permission Levels', () => {
    test('should restrict admin access to non-admin users', async ({ page }) => {
      // Login as regular user
      await page.goto('/login/');
      await page.fill('input[name="username"]', testUsers.customer.username);
      await page.fill('input[name="password"]', testUsers.customer.password);
      await page.click('button[type="submit"]');
      
      // Try to access admin panel
      await page.goto('/admin/');
      
      // Should redirect to dashboard with error
      await expect(page).toHaveURL(/.*dashboard/);
      await expect(page.locator('.bg-red-100')).toContainText('Access denied');
    });

    test('should allow operator access to limited admin features', async ({ page }) => {
      // Login as operator
      await page.goto('/login/');
      await page.fill('input[name="username"]', testUsers.operator.username);
      await page.fill('input[name="password"]', testUsers.operator.password);
      await page.click('button[type="submit"]');
      
      // Should access operator dashboard
      await page.goto('/admin/');
      await expect(page.locator('h1')).toContainText('Operator Dashboard');
      
      // Should have limited access
      await expect(page.locator('a:has-text("Users")')).toBeVisible();
      await expect(page.locator('a:has-text("System Settings")')).not.toBeVisible();
    });

    test('should show different menus based on user role', async ({ page }) => {
      await page.goto('/admin/');
      
      // Check admin menu items
      await expect(page.locator('a:has-text("Users")')).toBeVisible();
      await expect(page.locator('a:has-text("Billing Templates")')).toBeVisible();
      await expect(page.locator('a:has-text("Config Templates")')).toBeVisible();
      await expect(page.locator('a:has-text("Payments")')).toBeVisible();
      await expect(page.locator('a:has-text("Settings")')).toBeVisible();
    });
  });

  test.describe('System Health', () => {
    test('should display system health status', async ({ page }) => {
      await page.goto('/admin/');
      
      // Check system health card
      await expect(page.locator('text=System Health')).toBeVisible();
      await expect(page.locator('text=Database')).toBeVisible();
      await expect(page.locator('text=Email Service')).toBeVisible();
      await expect(page.locator('text=Payment Gateway')).toBeVisible();
    });

    test('should show system metrics', async ({ page }) => {
      await page.goto('/admin/metrics/');
      
      // Check metrics sections
      await expect(page.locator('h3')).toContainText('Server Metrics');
      await expect(page.locator('h3')).toContainText('Database Metrics');
      await expect(page.locator('h3')).toContainText('Application Metrics');
    });

    test('should allow system maintenance', async ({ page }) => {
      await page.goto('/admin/maintenance/');
      
      // Check maintenance options
      await expect(page.locator('button:has-text("Clear Cache")')).toBeVisible();
      await expect(page.locator('button:has-text("Optimize Database")')).toBeVisible();
      await expect(page.locator('button:has-text("Backup Database")')).toBeVisible();
    });
  });
});
